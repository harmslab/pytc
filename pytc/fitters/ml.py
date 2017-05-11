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

    def fit(self,model,parameters,bounds,y_obs,y_err):
        """
        Perform the fit using nonlinear least-squares regression.
        
        Parameters
        ----------

        parameters : np.array of floats
            fit parameters
        parameter_bounds : 2-tuple of array-like
            Lower and upper bounds on independent variables
       
        """

        self._model = model
        self._bounds = list(zip(bounds[0],bounds[1]))
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
                                                  bounds=bounds)
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

    @property
    def success(self):

        return self._fit_result.success
