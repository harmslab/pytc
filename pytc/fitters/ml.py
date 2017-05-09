
class MLFitter(Fitter):
    """
    Fit the model to the data using nonlinear least squares. 

    Standard deviation and ninety-five percent confidence intervals on parameter
    estimates are determined using the covariance matrix (Jacobian * residual
    variance)  See:
    # http://stackoverflow.com/questions/14854339/in-scipy-how-and-why-does-curve-fit-calculate-the-covariance-of-the-parameter-es
    # http://stackoverflow.com/questions/14581358/getting-standard-errors-on-fitted-parameters-using-the-optimize-leastsq-method-i
    """

    def fit(self,residuals,parameters,bounds):
        """
        Perform the fit using nonlinear least-squares regression.
        
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

        # Do the actual fit
        self._fit_result = optimize.least_squares(residuals, 
                                                  x0=parameters,
                                                  bounds=bounds)
            
        self._estimate = self._fit_result.x

        # Extract standard error on the fit parameter from the covariance
        N = len(self._fit_result.fun)
        P = len(self._fit_result.x)

        s_sq = np.sum(self._fit_result.fun**2)/(N - P)
        pcov = self._fit_result.jac*s_sq
        variance = np.absolute(np.diagonal(pcov))
        
        self._stdev = np.sqrt(variance)

        # 95% confidence intervals from standard error
        z = scipy.stats.t(N-P-1).ppf(0.975)
        c1 = fit_parameters - z*std_error
        c2 = fit_parameters + z*std_error

        self._ninetyfive = (c1,c2)

    @property
    def success(self):

        return self._fit_result.success
