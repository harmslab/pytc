from .base import Fitter

import emcee
import scipy.optimize as optimize


class BayesianFitter(Fitter):
    """
    """
    def __init__(self,num_walkers=100,initial_walker_spread=0.5,ml_guess=False,
                 num_steps=100,burn_in=0.1):
        """
        """

        self._num_walkers = num_walkers
        self._initial_walker_spread = initial_walker_spread
        self._ml_guess = ml_guess
        self._num_steps = num_steps
        self._burn_in = burn_in


    def ln_prior(self,param):
        """
        Log prior of fit parameters.
        """

        # If a paramter falls outside of the bounds, make the prior -infinity
        if np.sum(param < self._bounds[0,:]) > 0 or np.sum(param > self._bounds[1,:]):
            return -np.inf

        # otherwise, uniform
        return 0.0

    def ln_prob(self,param):
        """
        Posterior probability of model parameters.
        """

        # Calcualte prior.  If not finite, this solution has an -infinity log 
        # likelihood
        ln_prior = self.ln_prior(param)
        if not np.isfinite(ln_prior):
            return -np.inf
  
        # log posterior is log prior plus log likelihood 
        return ln_prior + self.ln_like(param)

    def fit(self,model,parameters,bounds,y_obs,y_err=None):
        """
        """

        self._model = model
        self._y_obs = y_obs

        # Convert the bounds (list of lists) into a 2d numpy array
        self._bounds = np.array(bounds)

        # If no error is specified, assign the error as 1/N, identical for all
        # points 
        self._y_err = y_err
        if y_err is None:
            self._y_err = np.array([1/len(self._y_obs) for i in range(len(self._y_obs))])


        # Make initial guess (ML or just whatever the paramters sent in were)
        if self._ml_guess:
            fn = lambda *args: -self.ln_like(*args)
            ml_fit = optimize.least_squares(fn,x0=parameters,bounds=bounds)
            self._initial_guess = ml_fit.x
        else:
            self._initial_guess = np.copy(parameters)
         
        # Create walker positions 

        # Size of perturbation in parameter depends on the scale of the parameter 
        perturb_size = initial_guess.x*initial_walker_spread
 
        ndim = len(parameters)
        pos = [initial_guess.x + np.random.randn(ndim)*perturb_size
               for i in range(self._num_walkers)]

        # Sample using walkers
        fn = lambda *args: self.ln_like(args) 
        self._fit_result = emcee.EnsembleSampler(nwalkers, ndim, fn, args=parameters)
        self._fit_result.run_mcmc(pos, self._numsteps)

        samples = self._fit_result.chain[:,self._burn_in,:].reshape((-1,ndim))


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
