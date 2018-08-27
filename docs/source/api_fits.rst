:orphan:

====================
Fitting with the API
====================

Workflow
========

+ Integrate raw power curves using Origin or `NITPIC  <http://biophysics.swmed.edu/MBR/software.html>`_,
  creating files containing heats per shot.  A collection of demo heat files
  are available `on github <https://github.com/harmslab/pytc-demos>`_.
+ Load heat files.
+ `Choose model describing experiment <indiv_models.html>`_.
+ Choose the `fitter <https://pytc.readthedocs.io/en/latest/fitters.html>`_.
+ Link individual fit parameters to `global parameters <https://pytc.readthedocs.io/en/latest/global_models.html>`_.
+ Fit the model to the data.
+ Evaluate the `fit statistics <https://pytc.readthedocs.io/en/latest/statistics.html>`_.
+ Export the results, which will save a csv file and pdf files showing the fit and corner plot.

API demos
=========

We have posted a collection of Jupyter notebooks that demonstrate working with
the API: `<https://github.com/harmslab/pytc-demos>`_.  The topics covered are
listed below.

Fitter choice
-------------
+ Using maximum likelihood to fit a model. `00_fit-single-site.ipynb <https://github.com/harmslab/pytc-demos/blob/master/00_fit-single-site.ipynb>`_.
+ Using a Bayesian sampler. `01_single-site-Bayesian.ipynb <https://github.com/harmslab/pytc-demos/blob/master/01_single-site-Bayesian.ipynb>`_.
+ Comparision of maximum likelihood, bootstrap, or Bayesian methods. `04_ml-v-bootstrap-v-bayesian.ipynb <https://github.com/harmslab/pytc-demos/blob/master/03_fit-competitor-model.ipynb>`_.

Model choice
------------
+ Fit a single-site model. `00_fit-single-site.ipynb <https://github.com/harmslab/pytc-demos/blob/master/00_fit-single-site.ipynb>`_.
+ Fit a binding polynomial. `02_fit-binding-polynomial.ipynb <https://github.com/harmslab/pytc-demos/blob/master/02_fit-binding-polynomial.ipynb>`_.
+ Fit a competitor binding model. `03_fit-competitor-model.ipynb <https://github.com/harmslab/pytc-demos/blob/master/03_fit-competitor-model.ipynb>`_.

Fitting options
---------------
+ Change fit guesses or fix parameters. `05_change-param-guess-fix.ipynb <https://github.com/harmslab/pytc-demos/blob/master/05_change-param-guess-fix.ipynb>`_.
+ Choose the best model using AIC. `11_use-aic-choose-model.ipynb <https://github.com/harmslab/pytc-demos/blob/master/11_use-aic-choose-model.ipynb>`_.

Global fits
-----------
+ Global fit of a single site model to a blank and experimental titration. `07_simultaneous-fit-blank-experiment.ipynb <https://github.com/harmslab/pytc-demos/blob/master/07_simultaneous-fit-blank-experiment.ipynb>`_.
+ Global fit of a single site model to a blank and three replicate experimental titrations `06_global-fit-three-replicates-and-blank.ipynb <https://github.com/harmslab/pytc-demos/blob/master/06_global-fit-three-replicates-and-blank.ipynb>`_.
+ Global connector: fit the same binding reaction measured in different buffers to extract ionization enthalpy and num protons `08_global-fit-with-NumProtons-connector.ipynb <https://github.com/harmslab/pytc-demos/blob/master/08_global-fit-with-NumProtons-connector.ipynb>`_.
+ Global connector: fit the same binding reaction measured at different temperatures to extract van't Hoff enthalpy `09_global-fit-for-vant-hoff-enthalpy.ipynb <https://github.com/harmslab/pytc-demos/blob/master/09_global-fit-for-vant-hoff-enthalpy.ipynb>`_.
+ Global connector: implement a custom global connector `10_implement-custom-global-connector.ipynb <https://github.com/harmslab/pytc-demos/blob/master/10_implement-custom-global-connector.ipynb>`_.
