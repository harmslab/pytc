from .base import Fitter

def ln_prob(param,bf):

    # Calcualte prior.  If not finite, this solution has an -infinity log 
    # likelihood
    ln_prior = bf.ln_prior(param)
    if not np.isfinite(ln_prior):
        return -np.inf
  
    # log posterior is log prior plus log likelihood 
    return ln_prior + bf.ln_like(param)


class BayesianFitter(Fitter):
    """
    """
    def __init__(self):
        """
        """

        pass 


    def ln_like(self,param):
        """
        Log likelihood as a function of fit parameters.
        """

        self._residuals(param)

        inv_sigma2 = 1.0/(yerr**2 + model**2*np.exp(2*lnf))
        return -0.5*(np.sum((y-model)**2*inv_sigma2 - np.log(inv_sigma2)))

    def ln_prior(self,theta):
        """
        Log prior of fit parameters.
        """

        m, b, lnf = theta
        if -5.0 < m < 0.5 and 0.0 < b < 10.0 and -10.0 < lnf < 1.0:
            return 0.0
        return -np.inf

    def fit(self,residuals,parameters,bounds,num_walkers=100,initial_walker_spread=0.5):
        """

        initial_walker_spread : float
        """


        self._num_walkers = num_walkers
        self._initial_walker_spread = initial_walker_spread
        self._ndim = len(parameters)

        initial_guess = optimize.least_squares(residuals, 
                                               x0=parameters,
                                               bounds=bounds)
         
        # Size of perturbation in parameter depends on the scale of the parameter 
        perturb_size = initial_guess.x*initial_walker_spread
 
        # Create walker positions 
        pos = [initial_guess.x + np.random.randn(self._ndim)*perturb_size
               for i in range(self._num_walkers)]

        self._sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob, args=(x, y, yerr))
        self._sampler.run_mcmc(pos, 500)
