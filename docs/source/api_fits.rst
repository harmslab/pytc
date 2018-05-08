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
the API: `<https://github.com/harmslab/pytc-demos>`_. 
