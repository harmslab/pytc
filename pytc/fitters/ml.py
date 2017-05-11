__description__ = \
"""
Fitter subclass for performing bootstrap fits.
"""
__author__ = "Michael J. Harms"
__date__ = "2017-05-10"

from .base import Fitter

import numpy as np
import scipy.stats
import scipy.optimize as optimize

class MLFitter(Fitter):
    """
    Fit the model to the data using nonlinear least squares. 

    Standard deviation and ninety-five percent confidence intervals on parameter
    estimates are determined using the covariance matrix (Jacobian * residual
    variance)  See:
    # http://stackoverflow.com/questions/14854339/in-scipy-how-and-why-does-curve-fit-calculate-the-covariance-of-the-parameter-es
    # http://stackoverflow.com/questions/14581358/getting-standard-errors-on-fitted-parameters-using-the-optimize-leastsq-method-i
    """
    def __init__(self):
        """
        Initialize the fitter.
        """

        Fitter.__init__(self)
       
        self.fit_type = "maximum likelihood"    

    def fit(self,model,parameters,bounds,y_obs,y_err):
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
        """

        self._model = model
        self._bounds = bounds
        self._y_obs = y_obs
        self._y_err = y_err

        # If no error is specified, assign the error as 1/N, identical for all
        # points 
        self._y_err = y_err
        if y_err is None:
            self._y_err = np.array([1/len(self._y_obs) for i in range(len(self._y_obs))])

        # Do the actual fit 
        fn = lambda *args: -self.weighted_residuals(*args)
        self._fit_result = optimize.least_squares(fn,
                                                  x0=parameters,
                                                  bounds=self._bounds)
        self._estimate = self._fit_result.x

        # Extract standard error on the fit parameter from the covariance
        N = len(self._y_obs)
        P = len(self._fit_result.x)

        s_sq = np.sum(self._fit_result.fun**2)/(N - P)
        pcov = self._fit_result.jac*s_sq 
        variance = np.absolute(np.diagonal(pcov))
        self._stdev = np.sqrt(variance)

        # 95% confidence intervals from standard error
        z = scipy.stats.t(N-P-1).ppf(0.975)
        c1 = self._estimate - z*self._stdev
        c2 = self._estimate + z*self._stdev

        self._ninetyfive = (c1,c2)

        self._sucess = self._fit_result.success

    @property
    def fit_info(self):
        """
        Return information about the fit.
        """

        return {}
        
