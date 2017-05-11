__description__ = \
"""
Fitter base class allowing different classes of fits.
"""
__author__ = "Michael J. Harms"
__date__ = "2017-05-10"

import numpy as np
import scipy.stats
import scipy.optimize as optimize
import corner

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

        self.fit_type = ""

    def unweighted_residuals(self,param):
        """
        Calculate residuals.
        """

        y_calc = self._model(param)

        return self._y_obs - y_calc

    def weighted_residuals(self,param):
        """
        Calculate weighted residuals.
        """

        y_calc = self._model(param)

        return (self._y_obs - y_calc)/self._y_err

    def ln_like(self,param):
        """
        Log likelihood as a function of fit parameters.
        """

        y_calc = self._model(param)
        sigma2 = self._y_err**2

        return -0.5*(np.sum((self._y_obs - y_calc)**2/sigma2 + np.log(sigma2)))

    def fit(self,model,parameters,bounds,y_obs,y_err=None):
        """
        Fit the parameters.       
        Should be redefined in subclasses.
 
        Parameters
        ----------

        model : callable
            model to fit.  model should take "parameters" as its only argument.
            this should (usually) be GlobalFit._y_calc
        parameters : array of floats
            parameters to be optimized.  usually constructed by GlobalFit._prep_fit
        bounds : list
            list of two lists containing lower and upper bounds
        y_obs : array of floats
            observations in an concatenated array
        y_err : array of floats or None
            standard deviation of each observation.  if None, each observation
            is assigned an error of 1/num_obs 
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
        Full fit results (will depend on exact fit type what is placed here).
        """
    
        return self._fit_result

    @property
    def success(self):
        """
        Whether the fit was successful.
        """
        
        return self._success

    @property
    def fit_info(self):
        """
        Information about fit run.  Should be redfined in subclass.
        """
       
        return {} 

    def corner_plot(self,param_names=()):
        """
        Create a "corner plot" that shows distributions of values for each
        parameter, as well as cross-correlations between parameters.

        Parameters
        ----------
        param_names : list
            list of parameter names to include.  if (), show all with names 
            p0,p1,... pN.
        """
    
        s = self._samples

        if len(param_names) == 0:
            param_names = ["p{}".format(i) for i in range(len(s.shape[1]))]

        corner_range = []
        for i in range(s.shape[1]):
            corner_range.append(tuple([np.min(s[:,i])-0.5,np.max(s[:,i])+0.5]))

        fig = corner.corner(s,labels=param_names,range=corner_range)

    @property
    def samples(self):
        """
        Samples from stochastic fits.
        """
   
        try: 
            return self._samples
        except AttributeError:
            return []

