__description__ = \
"""
Fitter subclass for performing bayesian (MCMC) fits.
"""
__author__ = "Michael J. Harms"
__date__ = "2017-05-10"

from .base import Fitter

import emcee, corner

import numpy as np
import scipy.optimize as optimize

import multiprocessing

class BayesianFitter(Fitter):
    """
    """
    def __init__(self,num_walkers=100,initial_walker_spread=1e-4,ml_guess=True,
                 num_steps=100,burn_in=0.1,num_threads=1):
        """
        Initialize the bayesian fitter

        Parameters
        ----------       
 
        num_walkers : int > 0
            how many markov chains to have in the analysis
        initial_walker_spread : float
            each walker is initialized with parameters sampled from normal 
            distributions with mean equal to the initial guess and a standard
            deviation of guess*initial_walker_spread 
        ml_guess : bool
            if true, do an ML optimization to get the initial guess
        num_steps:
            number of steps to run the markov chains
        burn_in : float between 0 and 1
            fraction of samples to discard from the start of the run
        num_threads : int or `"max"`
            number of threads to use.  if `"max"`, use the total number of 
            cpus. [NOT YET IMPLEMENTED] 
        """

        Fitter.__init__(self)

        self._num_walkers = num_walkers
        self._initial_walker_spread = initial_walker_spread
        self._ml_guess = ml_guess
        self._num_steps = num_steps
        self._burn_in = burn_in

        self._num_threads = num_threads
        if self._num_threads == "max":
            self._num_threads = multiprocessing.cpu_count()

        if not type(self._num_threads) == int and self._num_threads > 0:
            err = "num_threads must be 'max' or a positive integer\n"
            raise ValueError(err)

        if self._num_threads != 1:
            err = "multithreading has not yet been (fully) implemented.\n"
            raise NotImplementedError(err)

        self._success = None

        self.fit_type = "bayesian"

    def ln_prior(self,param):
        """
        Log prior of fit parameters.  Priors are uniform between bounds and 
        set to -np.inf outside of bounds.

        Parameters
        ----------

        param : array of floats
            parameters to fit

        Returns
        -------

        float value for log of priors. 
        """

        # If a paramter falls outside of the bounds, make the prior -infinity
        if np.sum(param < self._bounds[0,:]) > 0 or np.sum(param > self._bounds[1,:]) > 0:
            return -np.inf

        # otherwise, uniform
        return 0.0

    def ln_prob(self,param):
        """
        Posterior probability of model parameters.

        Parameters
        ----------

        param : array of floats
            parameters to fit

        Returns
        -------

        float value for log posterior proability
        """

        # Calcualte prior.  If not finite, this solution has an -infinity log 
        # likelihood
        ln_prior = self.ln_prior(param)
        if not np.isfinite(ln_prior):
            return -np.inf
 
        # Calcualte likelihood.  If not finite, this solution has an -infinity
        # log likelihood
        ln_like = self.ln_like(param)
        if not np.isfinite(ln_like):
            return -np.inf

        # log posterior is log prior plus log likelihood 
        return ln_prior + ln_like

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
        self._y_obs = y_obs

        # Convert the bounds (list of lower and upper lists) into a 2d numpy array
        self._bounds = np.array(bounds)

        # If no error is specified, assign the error as 1/N, identical for all
        # points 
        self._y_err = y_err
        if y_err is None:
            self._y_err = np.array([1/len(self._y_obs) for i in range(len(self._y_obs))])

        if param_names is None:
            self._param_names = ["p{}".format(i) for i in range(len(parameters))]
        else:
            self._param_names = param_names[:] 

        # Make initial guess (ML or just whatever the paramters sent in were)
        if self._ml_guess:
            fn = lambda *args: -self.weighted_residuals(*args)
            ml_fit = optimize.least_squares(fn,x0=parameters,bounds=self._bounds)
            self._initial_guess = np.copy(ml_fit.x)
        else:
            self._initial_guess = np.copy(parameters)
        
        # Create walker positions 

        # Size of perturbation in parameter depends on the scale of the parameter 
        perturb_size = self._initial_guess*self._initial_walker_spread
 
        ndim = len(parameters)
        pos = [self._initial_guess + np.random.randn(ndim)*perturb_size
               for i in range(self._num_walkers)]

        # Sample using walkers
        self._fit_result = emcee.EnsembleSampler(self._num_walkers, ndim, self.ln_prob,
                                                 threads=self._num_threads)
        self._fit_result.run_mcmc(pos, self._num_steps)

        # Create list of samples
        to_discard = int(round(self._burn_in*self._num_steps,0))
        self._samples = self._fit_result.chain[:,to_discard:,:].reshape((-1,ndim))
        self._lnprob = self._fit_result.lnprobability[:,:].reshape(-1)

        # Get mean and standard deviation 
        self._estimate = np.mean(self._samples,axis=0)
        self._stdev = np.std(self._samples,axis=0)

        # Calculate 95% confidence intervals
        self._ninetyfive = []
        lower = int(round(0.025*self._samples.shape[0],0))
        upper = int(round(0.975*self._samples.shape[0],0))
        for i in range(self._samples.shape[1]):
            nf = np.sort(self._samples[:,i])
            self._ninetyfive.append([nf[lower],nf[upper]])

        self._ninetyfive = np.array(self._ninetyfive)

        self._success = True

    @property
    def fit_info(self):
        """
        Information about the Bayesian run.
        """

        output = {}
        output["Num walkers"] = self._num_walkers
        output["Initial walker spread"] = self._initial_walker_spread
        output["Use ML guess"] = self._ml_guess
        output["Num steps"] = self._num_steps
        output["Burn in"] = self._burn_in
        output["Final sample number"] = len(self._samples[:,0])
        output["Num threads"] = self._num_threads
        
        return output

    @property
    def samples(self):
        """
        Bayesian samples.
        """
        
        return self._samples

