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
during least-squares regression.  This is susceptible to numerical problems and
may not always be reliable.  

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
