__description__ = \
"""
Fitter subclass for performing bootstrap fits.
"""
__author__ = "Michael J. Harms"
__date__ = "2017-05-11"

from .base import Fitter

import numpy as np
import scipy.optimize

import sys

class BootstrapFitter(Fitter):
    """
    Perform the fit many times, sampling from uncertainty in each measured heat. 
    """

    def __init__(self,num_bootstrap=100,perturb_size=1.0,exp_err=False,verbose=False):
        """
        Perform the fit many times, sampling from uncertainty in each measured
        heat. 
        
        Parameters
        ----------

        num_bootstrap : int
            Number of bootstrap samples to do
        perturb_size : float
            Standard deviation of random samples for heats.  Ignored if exp_err
            is specified. 
        exp_err : bool
            Use experimental estimates of heat uncertainty.  If specified, overrides
            perturb_size.
        verbose : bool
            Give verbose output.
        """
        
        Fitter.__init__(self)

        self._num_bootstrap = num_bootstrap
        self._perturb_size = perturb_size
        self._exp_err = exp_err
        self._verbose = verbose

        self.fit_type = "bootstrap"

    def fit(self,model,parameters,bounds,y_obs,y_err=None,param_names=None):
        """
        Fit the parameters.       
 
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
   
        self._model = model
        self._bounds= bounds
        self._y_obs = y_obs
        self._y_err = y_err

        self._success = None 
    
        if y_err is None or self._exp_err == False:
            self._y_err = np.array([self._perturb_size
                                    for i in range(len(self._y_obs))])

        if param_names is None:
            self._param_names = ["p{}".format(i) for i in range(len(parameters))]
        else:
            self._param_names = param_names[:] 
 
        # Create array to store bootstrap replicates 
        self._samples = np.zeros((self._num_bootstrap,len(parameters)),
                                 dtype=float)

        original_y_obs = np.copy(self._y_obs)

        # Go through bootstrap reps
        for i in range(self._num_bootstrap):

            if self._verbose and i != 0 and i % 100 == 0:
                print("Bootstrap {} of {}".format(i,self._num_bootstrap))
                sys.stdout.flush()

            # Add random error to each sample
            self._y_obs = original_y_obs + np.random.normal(0.0,y_err)
            
            # Do the fit
            fit = scipy.optimize.least_squares(self.unweighted_residuals,
                                               x0=parameters,
                                               bounds=bounds)
    
            # record the fit results
            self._samples[i,:] = fit.x

        self._y_obs = np.copy(original_y_obs)

        self._fit_result = self._samples

        # mean of bootstrap samples
        self._estimate = np.mean(self._samples,axis=0)

        # standard deviation from bootstrap samples
        self._stdev = np.std(self._samples,axis=0)

        # 95% from bootstrap samples 
        self._ninetyfive = []
        for i in range(self._samples.shape[1]):
            lower = np.percentile(self._samples[:,i], 2.5)
            upper = np.percentile(self._samples[:,i],97.5)
            self._ninetyfive.append([lower,upper])
        self._ninetyfive = np.array(self._ninetyfive)
         
        self._success = True 

    @property
    def fit_info(self):
        """
        Return information about the fit.
        """

        output = {}
        
        output["Num bootstrap"] = self._num_bootstrap
        output["Perturb size"] = self._perturb_size
        output["Use experimental error"] = self._exp_err

        return output

    @property
    def samples(self):
        """
        Bootstrap samples.
        """

        return self._samples
