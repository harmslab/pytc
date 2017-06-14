:orphan:

=======
Fitters
=======

Fitting Strategies
==================

**pytc** implements a variety of fitting strategies:

- BayesianFitter_ uses Markov-Chain Monte Carlo to estimate posterior
  probability distributions for all fit parameters. (Recommended)
- BootstrapFitter_ samples from uncertainty in each heat and then fits the model
  to pseudoreplicates using unweighted least-squares regression. 
- MLFitter_ fits the model to the data using least-squares regression
  weighted by the uncertainty in each heat. (Default)

These are implemented as subclasses of the
`pytc.fitters.Fitter <https://github.com/harmslab/pytc/blob/master/pytc/fitters/base.py>`_.  
base class. 

.. _BayesianFitter:

Bayesian
--------

`pytc.fitters.BayesianFitter <https://github.com/harmslab/pytc/blob/master/pytc/fitters/bayesian.py>`_. 

Uses Markov-Chain Monte Carlo (MCMC) to sample from the posterior probability 
distributions of fit parameters. **pytc** uses the package `emcee <http://dan.iel.fm/emcee/current/>`_ to do the 
sampling.  The log likelihood function is:

.. math::

    ln(L) = -0.5 \sum_{i=0}^{i < N} \Big [ \frac{(dQ_{obs,i} - dQ_{calc,i}(\vec{\theta}))^{2}}{\sigma_{i}^{2}} + ln(\sigma_{i}^{2}) \Big ]

where :math:`dQ_{obs,i}` is an observed heat for a shot, :math:`dQ_{calc,i}` is
the heat calculated for that shot by the model, and :math:`\sigma_{i}` is the
experimental uncertainty on that heat.

The prior distribution is uniform within the specified parameter bounds.  If
any parameter is outside of its bounds, the prior is :math:`-\infty`.  
Otherwise, the prior is 0.0 (uniform). 

The posterior probability is given by the sum of the log prior and log 
likelihood functions.  

.. math::
    ln(P) = ln(L) + ln(prior)


Parameter estimates
~~~~~~~~~~~~~~~~~~~

Parameter estimates are the means of posterior probability distributions.

Parameter uncertainty
~~~~~~~~~~~~~~~~~~~~~

Parameter uncertainties are estimated by numerically integrating the posterior
probability distributions.

Options
~~~~~~~

+ :code:`num_walkers`: number of MCMC walkers
+ :code:`initial_walker_spread`: how much to spread out the inital walkers
+ :code:`ml_guess`: whether or not to start the sampler from the ML guess
+ :code:`num_steps`: number of steps each walker should take
+ :code:`burn_in`: fraction of initial samples to discard from the sampler
+ :code:`num_threads`: number of threads to use (not yet implemented)

.. _BootstrapFitter:

Bootstrap
---------

`pytc.fitters.BootstrapFitter <https://github.com/harmslab/pytc/blob/master/pytc/fitters/bootstrap.py>`_. 

Samples from experimental uncertainty in each heat and then peforms unweighted
least-squares regression on each pseudoreplicate using `scipy.optimize.least_squares <https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.optimize.least_squares.html>`_.
The residuals function is:

.. math::
    \vec{r} = \vec{dQ}_{obs} - \vec{dQ}_{calc}(\vec{\theta})

where :math:`\vec{dQ}_{obs}` is a vector of the observed heats and 
:math:`\vec{dQ}_{calc}(\vec{\theta})` is a vector of heats observed with fit
paramters :math:`\vec{\theta}`.

This uses the robust `Trust Region Reflective <https://nmayorov.wordpress.com/2015/06/19/trust-region-reflective-algorithm/>`_
method for the nonlinear regression.

Parameter estimates
~~~~~~~~~~~~~~~~~~~

Parameter estimates are the means of bootstrap pseudoreplicate distributions.

Parameter uncertainty
~~~~~~~~~~~~~~~~~~~~~

Parameter uncertainties are estimated by numerically integrating the bootstrap
pseudoreplicate distributions.

Options
~~~~~~~

+ :code:`num_bootstrap`: number of bootstrap replicates
+ :code:`perturb_size`: how much to perturb each heat for random sampling
+ :code:`exp_err`: use experimental estimates of heat uncertainty.  (overrides 
  :code:`perturb_size`.
+ :code:`verbose`: how verbose to be during the fit

.. _MLFitter: 

Least-squares regression
------------------------

`pytc.fitters.MLFitter <https://github.com/harmslab/pytc/blob/master/pytc/fitters/ml.py>`_. 

Weighted least-squares regression using `scipy.optimize.least_squares <https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.optimize.least_squares.html>`_.  The 
residuals function is:

.. math::

    \vec{r} = \frac{\vec{dQ}_{obs} - \vec{dQ}_{calc}(\vec{\theta})}{\vec{\sigma}_{obs}}

where :math:`\vec{dQ}_{obs}` is a vector of the observed heats, 
:math:`\vec{dQ}_{calc}(\vec{\theta})` is a vector of heats observed with fit
paramters :math:`\vec{\theta}`, and :math:`\vec{\sigma}_{obs}` are the uncertainties
on each fit. 

This uses the robust `Trust Region Reflective <https://nmayorov.wordpress.com/2015/06/19/trust-region-reflective-algorithm/>`_
method for the nonlinear regression.

Parameter estimates
~~~~~~~~~~~~~~~~~~~

The parameter estimates are the maximum-likelihood parameters returned by 
`scipy.optimize.least_squares <https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.optimize.least_squares.html>`_.

Parameter uncertainty
~~~~~~~~~~~~~~~~~~~~~

We first approximate the covariance matrix :math:`\Sigma` from the Jacobian
matrix :math:`J` estimated by `scipy.optimize.least_squares <https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.optimize.least_squares.html>`_:

.. math::
    \Sigma \approx [2(J^{T} \cdot J)]^{-1}

We can then determine the standard deviation on the parameter estimates 
:math:`\sigma` by taking the square-root of the diagonal of :math:`\Sigma`:

.. math::
    \sigma = \sqrt(diag(\Sigma)) 

Ninety-five percent confidence intervals are estimated using the Z-score assuming
a normal parameter distribution with the mean and standard deviations determined
above.

.. warning::

    Going from :math:`J` to :math:`\Sigma` is an approximation.
    This is susceptible to numerical problems and may not always be reliable. 
    Use common sense on your fit errors or, better yet, do Bayesian integration!
