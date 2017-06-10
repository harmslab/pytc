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

import re

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

    def fit(self,model,parameters,bounds,y_obs,y_err=None,param_names=None):
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
        param_names : array of str
            names of parameters.  If None, parameters assigned names p0,p1,..pN
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

    def corner_plot(self,filter_params=(),*args,**kwargs):
        """
        Create a "corner plot" that shows distributions of values for each
        parameter, as well as cross-correlations between parameters.

        Parameters
        ----------
        filter_params : list-like
            strings used to search parameter names.  if the string matches, 
            the parameter is *excluded* from the plot.
        """
   
        skip_pattern = re.compile("|".join(filter_params))
 
        s = self._samples

        to_plot = []
        corner_range = []
        param_names = []
        est_values = []
        for i in range(s.shape[1]):
         
            # look for patterns to skip 
            if skip_pattern.search(self._param_names[i]):
                continue

            param_names.append(self._param_names[i])
            to_plot.append(s[:,i])
            corner_range.append(tuple([np.min(s[:,i])-0.5,np.max(s[:,i])+0.5]))

            est_values.append(self.estimate[i])

        to_plot = np.array(to_plot)
        to_plot = np.swapaxes(to_plot,0,1)

        fig = corner.corner(to_plot,labels=param_names,range=corner_range,
                            truths=est_values,*args,**kwargs)

        return fig

    @property
    def samples(self):
        """
        Samples from stochastic fits.
        """
   
        try: 
            return self._samples
        except AttributeError:
            return []
