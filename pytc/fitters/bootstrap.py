
class BootstrapFitter(Sampler):
    """
    Perform the fit many times, sampling from uncertainty in each measured heat. 
    """

    def __init__(self):
        
        self._success = False
        Sampler.__init__(self)

    def fit(self,residuals,parameters,bounds,num_bootstrap=100,perturb_size=1.00,
            exp_err=False):
        """
        Perform the fit many times, sampling from uncertainty in each measured
        heat. 
        
        Parameters
        ----------

        residuals : function
            residuals function. This should take parameters and parameter_bounds
            as arguments.
        parameters : np.array of floats
            fit parameters
        parameter_bounds : 2-tuple of array-like
            Lower and upper bounds on independent variables
        num_bootstrap : int
            Number of bootstrap samples to do
        perturb_size : float
            Standard deviation of random samples for heats.  Ignored if exp_err
            is specified. 
        exp_err : bool
            Use experimental estimates of heat uncertainty.  If specified, overrides
            perturb_size.
        """
    
        # Record actual heats before sampling
        tmp_dict = {}
        for k in self._expt_dict.keys():
            tmp_dict[k] = copy.copy(self._expt_dict[k].heats)
         
        # Create array to store bootstrap replicates 
        self._fit_result = np.zeros((num_bootstrap + 1,
                                     len(self._float_param)),dtype=float)

        # Go through bootstrap reps
        for i in range(num_bootstrap + 1):

            if i != 0 and i % 10 == 0:
                print("Bootstrap {} of {}".format(i,num_bootstrap + 1))
                sys.stdout.flush()

            # Perturb rep heats
            for k in self._expt_dict.keys():
                if exp_err:
                    self._expt_dict[k].heats = tmp_dict[k] + np.random.normal(0.0,self._expt_dict[k].heat_err)
                else:
                    self._expt_dict[k].heats = tmp_dict[k] + np.random.normal(0.0,perturb_size,len(tmp_dict[k]))
            
            # Last fit should be ML to the experiments all have ML parameter
            # by end. 
            if i == num_bootstrap:

                # Restore heats
                for k in self._expt_dict.keys():
                    self._expt_dict[k].heats = tmp_dict[k]

            # Do the actual fit
            fit = optimize.least_squares(self._residuals, 
                                         x0=self._float_param,
                                         bounds=self._float_bounds)
            self._fit_result[i,:] = fit.x


        # Estimate is ML (last fit)
        self._estimate = fit.x

        # standard deviation from bootstrap samples
        self._stdev = np.std(self._bootstrap_params,0)

        # 95% from bootstrap samples 
        self._ninetyfive = np.zeros((len(self._estimate),2),dtype=np.float)
        bottom = int(round(0.025*num_bootstrap,0))
        top    = int(round(0.975*num_bootstrap,0))
        for i in range(len(self._estimate)):
            p1 = np.copy(self._bootstrap_params[:,i])
            p1.sort()

            self._ninetyfive[i,0] = p1[bottom]
            self._ninetyfive[i,1] = p1[top]
         
        self._success = True 

    @property
    def success(self):

        return self._success  
