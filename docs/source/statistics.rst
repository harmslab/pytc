:orphan:
======================
Fitting and Statistics
======================

Public Serivce Announcement:

.. warning::
    **pytc** will fit all sorts of complicated models to your data. It is up to
    you to make sure the fit is justified by the data.  You should always 
    follow best practices for selecting the your model (choosing the simplest
    model, inspecting residuals, knowing the assumptions made, etc.)

Fitting
-------

Assumptions
~~~~~~~~~~~

As implemented, **pytc** assumes that all data points from all experiments have
identical error distributions. Assuming all data are collected on the same 
instrument with the same gain and reference power, this should likely be true.  

Statistics
~~~~~~~~~~

Models with more parameters will generally fit the data better than models with
fewer parameters.  These extra parameters may or may not be meaningful.  (You
could, for example, fit :math:`N` data points with :math:`N` parameters.  This
would give a perfect fit -- and very little insight into the system).  A
standard approach in model fittng is to choose the simplest model consistent
with the data.  A variety of statistics can be used to balance fitting the data 
well against the addition of many parameters.  **pytc** returns four test
statistics that penalize models based on the number of free parameters: Akaike
Information, corrected Akaike Information, Bayesian Information, and the
F-statistic. 

These statistics are accessible via :code:`GlobalModel.fit_stats`, a dictionary
keyed to these values (:code:`AIC`, :code:`AICc`, :code:`BIC`, and :code:`F`). 
The implementation of these statistics is in the :code:`GlobalModel.fit_stats`
property in :code:`pytc/global_fit.py`.  

The :code:`pytc.util.compare_models` function will conveniently 
compare two models to one another.  This will automatically calculate the 
support for one model versus another using AIC, AICc, and BIC.   

The :code:`GlobalModel.fit_stats` property also returns the 

 + The :code:`Rsq` and :code:`Rsq_adjusted` return the :math:`R^{2}` and 
   :math:`R^{2}_{adjusted}` for the fit.  

Parameter uncertainty
~~~~~~~~~~~~~~~~~~~~~

Each fit parameter has an associated standard error and 95% confidence interval.
These are determined using the diagonal of the parameter Jacobian estimated
during least-squares regression.  

:code:`pytc` also implements a bootstrap sampler that samples from uncertainty
in each data point and then uses each pseudoreplicate to refit.  This analysis
assumes that each point has the same uncertainty (specificed by 
:code:`perturb_size` in the :code:`GlobalModel.fit` call).  The parameter 
estimates returned are the mean of the bootstrap replicates; the error is the
standard deviation of those replicates.  

Residuals
~~~~~~~~~

Plotting the fit will automatically plot fit residuals below the main fit.  
These residuals should be randomly distributed around zero.  Non-random 
residuals can indicate that the model does not adequately describe the data,
despite potentially having a small residual standard error.  


Least-squares regression
------------------------

POINTER_TO_THE_ML_METHOD

Weighted least-squares regression using `scipy.optimize.least_squares`.  The 
residuals function is:

.. math::

    \vec{r} = \frac{\vec{dQ}_{obs} - \vec{dQ}_{calc}(\theta)}{\vec{\sigma}_{obs}}

where :math:`\vec{dQ}_{obs}` is a vector of the observed heats, 
:math:`\vec{dQ}_{calc}(\vec{\theta})` is a vector of heats observed with fit
paramters :math:`\vec{\theta}`, and :math:`\vec{\sigma}_{obs}` are the uncertainties
on each fit. 

This uses the very robust `'XXX'` method for the regression.

Parameter estimates
~~~~~~~~~~~~~~~~~~~

The parameter estimates are the maximum-likelihood parameters returned by 
:code:`scipy.optimize.least_squares`.

Parameter uncertainty
~~~~~~~~~~~~~~~~~~~~~

We first approximate the covariance matrix :math:`\mathbf{\Sigma}` from the Jacobian
matrix :math:`\mathbf{J}` estimated by :code:`scipy.optimize.least_squares`:

.. math::
    \Sigma \approx [2(\mathbf{J}^{T} \dot \mathbf{J})]^{-1}

We can then determine the standard deviation on the parameter estimates 
:math:`\sigma` by taking the square-root of the diagonal of :math:`\Sigma`:

.. math::
    \sigma = \sqrt(diag(\Sigma)) 

Ninety-five percent confidence intervals are estimated using the Z-score assuming
a normal parameter distribution with the mean and standard deviations determined
above.

.. warning::

    Going from :math:`\mathbf{J}` to :math:`\mathbf{\Sigma}` is an approximation.
    This is susceptible to numerical problems and may not always be reliable. 
    Use common sense on your fit errors or, better yet, do Bayesian integration!


Bootstrap
---------

POINTER_TO_THE_BOOTSTRAP_METHOD

Samples from experimental uncertainty in each heat and then peforms unweighted
east-squares regression on each pseudoreplicate using `scipy.optimize.least_squares`.
The residuals function is:

.. math::

    \vec{r} = \vec{dQ}_{obs} - \vec{dQ}_{calc}(\theta)

where :math:`\vec{dQ}_{obs}` is a vector of the observed heats, 
:math:`\vec{dQ}_{calc}(\vec{\theta})` is a vector of heats observed with fit
paramters :math:`\vec{\theta}`, and :math:`\vec{\sigma}_{obs}` are the uncertainties
on each fit. 

This uses the very robust `'XXX'` method for the regression.

Parameter estimates
~~~~~~~~~~~~~~~~~~~

The parameter estimates are the mean of the bootstrap replicates.

Parameter uncertainty
~~~~~~~~~~~~~~~~~~~~~

The parameter uncertainties are the mean and numerically estimated 95% confidence
intervals of the bootstrap pseudoreplicates.

Bayesian
--------

POINTER_TO_THE_BAYESIAN_METHOD

Uses Markov-Chain Monte Carlo (MCMC) to sample from the posterior probability 
distributions of fit parameters.   `pytc` uses the package `emcee` to do the 
sampling.  The log likelihood function is:

.. math::

    ln(L) = -0.5 \sum_{i=0}^{i < N} \Big ( \frac{(dQ_{obs,i} - dQ_{calc,i}(\vec{\theta}))^{2}}{\sigma_{i}^{2}} + ln(\sigma_{i}^{2}) \Big )

The prior distribution is uniform within the specified parameter bounds.  If
any parameter is outside of its bounds, the prior is :math:`\-infty`.  
Otherwise, the prior is 0.0 (uniform). 

The posterior probability is given by the sum of the log prior and log 
likelihood functions.  

.. math::
    ln(P) = ln(L) + ln(prior)


Parameter estimates
~~~~~~~~~~~~~~~~~~~

Parameter estimates are the mean of posterior probability distribution after 
sampling.

Parameter uncertainty
~~~~~~~~~~~~~~~~~~~~~

The parameter uncertainties are the mean and numerically estimated 95% confidence
intervals of the bootstrap pseudoreplicates.
