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

    def fit(self,model,parameters,bounds,y_obs,y_err,param_names=None):
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
        self._bounds = bounds
        self._y_obs = y_obs
        self._y_err = y_err

        self._success = None

        # If no error is specified, assign the error as 1/N, identical for all
        # points 
        self._y_err = y_err
        if y_err is None:
            self._y_err = np.array([1/len(self._y_obs) for i in range(len(self._y_obs))])

        if param_names is None:
            self._param_names = ["p{}".format(i) for i in range(len(parameters))]
        else:
            self._param_names = param_names[:] 

        # Do the actual fit 
        fn = lambda *args: -self.weighted_residuals(*args)
        self._fit_result = optimize.least_squares(fn,
                                                  x0=parameters,
                                                  bounds=self._bounds)
        self._estimate = self._fit_result.x

        # Extract standard error on the fit parameter from the covariance
        N = len(self._y_obs)
        P = len(self._fit_result.x)

        J = self._fit_result.jac
        cov = np.linalg.inv(2*np.dot(J.T,J))

        self._stdev = np.sqrt(np.diagonal(cov)) #variance)

        # 95% confidence intervals from standard error
        z = scipy.stats.t(N-P-1).ppf(0.975)
        c1 = self._estimate - z*self._stdev
        c2 = self._estimate + z*self._stdev

        self._ninetyfive = []
        for i in range(P):
            self._ninetyfive.append([c1[i],c2[i]])
        self._ninetyfive = np.array(self._ninetyfive)

        self._success = self._fit_result.success

    @property
    def fit_info(self):
        """
        Return information about the fit.
        """

        return {}

    def corner_plot(self,filter_params=(),num_samples=100000,*args,**kwargs):
        """
        Create a "corner plot" that shows distributions of values for each
        parameter, as well as cross-correlations between parameters.

        Parameters
        ----------
        filter_params : list-like
            strings used to search parameter names.  if the string matches, 
            the parameter is *excluded* from the plot.
        num_samples : int
            how many samples to generate

        Wraps the Fitter.plot_corner method.  Least squares does not generate 
        samples but corner.corner samples.  Use the Jacobian spit out by 
        least_squares to generate a whole bunch of fake samples.  These are 
        then deleted. 

        Approximate the covariance matrix as $(2*J^{T} \dot J)^{-1}$, then perform
        cholesky factorization on the covariance matrix.  This can then be
        multiplied by random normal samples to create distributions that come
        from this covariance matrix. 
  
        See:       
        https://stackoverflow.com/questions/40187517/getting-covariance-matrix-of-fitted-parameters-from-scipy-optimize-least-squares
        https://stats.stackexchange.com/questions/120179/generating-data-with-a-given-sample-covariance-matrix
        """

        J = self._fit_result.jac
      
        cov = np.linalg.inv(2*np.dot(J.T,J))
        chol_cov = np.linalg.cholesky(cov).T

        self._samples = np.dot(np.random.normal(size=(num_samples,chol_cov.shape[0])),chol_cov)
        self._samples = self._samples + self.estimate       
 
        fig = Fitter.corner_plot(self,filter_params,*args,**kwargs)

        del self._samples

        return fig
 
        
