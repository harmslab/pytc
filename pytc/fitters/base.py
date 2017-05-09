
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

    def fit(self,residuals,parameters,parameter_bounds):
        """
        Dummy fit function.
        
        Parameters
        ----------

        residuals : function
            residuals function. This should take parameters and parameter_bounds
            as arguments.
        parameters : np.array of floats
            fit parameters
        parameter_bounds : 2-tuple of array-like
            Lower and upper bounds on independent variables
        """

        pass

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
    def num_obs(self):
        """
        Return the number of observations used for the fit.
        """

        try:
            # fun is fit residuals XXX FIX SO NOT ML SPECIFIC
            return len(self._fit_result.fun)
        except AttributeError:
            return None

    @property
    def fit_num_param(self):
        """
        Return the number of parameters fit.
        """

        # Global parameters
        num_param = 0
        for k in self.fit_param[0].keys():

            # Only count floating parameters
            if not self.global_param[k].fixed:
                num_param += 1

        # Local parameters
        for i in range(len(self.fit_param[1])):

            expt_name = self._expt_list_stable_order[i]
            for k in self.fit_param[1][i].keys():

                # Skip variables linked to global variables
                try:
                    alias = self._expt_dict[expt_name].model.parameters[k].alias
                    if alias != None:
                        continue
                except AttributeError:
                    pass
            
                # Only count floating parameters
                if not self._expt_dict[expt_name].model.parameters[k].fixed:
                    num_param += 1

        return num_param

    @property
    def stats(self):
        """
        Assumes that all data have the same error distribution -- e.g. similar
        noise levels etc.  Should be fine for data collected on same instrument.

        """

        try:
            self._sampler.fit_result
        except AttributeError:
            return None

        output = {}
     
        output["num_obs"] = self.fit_num_obs
        output["num_param"] = self.fit_num_param
 
        # Create a vector of calcluated and observed values.  
        y_obs = [] 
        y_estimate = []
        for k in self._expt_dict:
            y_obs.extend(self._expt_dict[k].heats)
            y_estimate.extend(self._expt_dict[k].dQ)
        y_estimate= np.array(y_estimate)
        y_obs = np.array(y_obs)

        P = self.fit_num_param
        N = self.fit_num_obs
 
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
        P_all = P + 1 # add parameter to account for implicit residual
        output["AIC"] = 2*P_all  - 2*lnL
        output["BIC"] = P_all*np.log(N) - 2*lnL
        output["AICc"] = output["AIC"] + 2*(P_all + 1)*(P_all + 2)/(N - P_all - 2)

        return output
