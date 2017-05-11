import numpy as np
import scipy.stats
import scipy.optimize as optimize



class Fitter:
    """
    Base class for fits.
    """

    def __init__(self):
        """
        Init function for the class.
        """

        self._coeff = None
        self._stdev = None
        self._ninetyfive = None
        self._fit_result = None
        self._success = False

    def fit(self,model,parameters,bounds,y_obs,y_err=None):
        """
        """

        pass

    def ln_like(self,param):
        """
        Log likelihood as a function of fit parameters.
        """

        y_calc = self._model(param)
        sigma2 = self._y_err**2

        return -0.5*(np.sum((self._y_obs - y_calc)**2/sigma2 + np.log(sigma2)))

    def weighted_residuals(self,param):
        """
        Calculate weighted residuals.
        """

        y_calc = self._model(param)

        return (self._y_obs - y_calc)/self._y_err

    @property
    def estimate(self):
        """
        Estimates of fit parameters.
        """
        
        return self._estimate
  
    @property
    def stdev(self):
        """
        Standard deviations on estimates of fit parameters.
        """       
 
        return self._stdev

    @property
    def ninetyfive(self):
        """
        Ninety-five perecent confidence intervals on the estimates.
        """

        return self._ninetyfive

    @property
    def fit_result(self):
        """
        Full fit results. 
        """
    
        return self._fit_result

    @property
    def success(self):
        """
        Whether the fit was successful.
        """
        
        return self._success

    @property
    def stats(self):
        """
        Assumes that all data have the same error distribution -- e.g. similar
        noise levels etc.  Should be fine for data collected on same instrument.

        """

        if not self.success:

            return None

        output = {}
     
        output["num_obs"] = self.num_obs
        output["num_param"] = self.num_param
 
        # Create a vector of calcluated and observed values.  
        y_obs = [] 
        y_estimate = []
        for k in self._mapper.expt_dict:
            y_obs.extend(self._mapper.expt_dict[k].heats)
            y_estimate.extend(self._mapper.expt_dict[k].dQ)
        y_estimate= np.array(y_estimate)
        y_obs = np.array(y_obs)

        P = self.num_param
        N = self.num_obs
 
        sse = np.sum((y_obs -          y_estimate)**2)
        sst = np.sum((y_obs -      np.mean(y_obs))**2)
        ssm = np.sum((y_estimate - np.mean(y_obs))**2)

        # Calcluate R**2 and adjusted R**2
        if sst == 0.0:
            output["Rsq"] = np.inf
            output["Rsq_adjusted"] = np.inf
        else:
            Rsq = 1 - (sse/sst)
            Rsq_adjusted = Rsq - (1 - Rsq)*P/(N - P - 1)

            output["Rsq"] = Rsq
            output["Rsq_adjusted"] = Rsq_adjusted
        
        # calculate F-statistic
        msm = (1/P)*ssm
        mse = 1/(N - P - 1)*sse
        if mse == 0.0:
            output["F"] = np.inf
            output["F"] = np.inf
        else:
            output["F"] = msm/mse
            output["p"] = 1 - scipy.stats.f.cdf(output["F"],P,(N-P-1))  

        # Calcluate log-likelihood
        variance = sse/N
        L1 = (1.0/np.sqrt(2*np.pi*variance))**N
        L2 = np.exp(-sse/(2*variance))
        lnL = np.log(L1*L2)
        output["ln(L)"] = lnL

        # AIC and BIC
        P_all = P + 1 # add parameter to account for intercept
        output["AIC"] = 2*P_all  - 2*lnL
        output["BIC"] = P_all*np.log(N) - 2*lnL
        output["AICc"] = output["AIC"] + 2*(P_all + 1)*(P_all + 2)/(N - P_all - 2)

        return output
