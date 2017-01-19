================================
pytc documentation
================================
A python software package for analyzing Isothermal Titration Calorimetry data.

Introduction
================================
(The name is portmanteau of Python and ITC).  

Quick Start
--------------------------------

 + Clone the repository with :code:`git clone https://github.com/harmslab/pytc.git`
 + Open the :code:`Demo.ipynb` jupyter notebook to see a collection of example fits. 

Example code
--------------------------------

Fit a :math:`Ca^{2+}/EDTA` binding experiment.

.. sourcecode:: python

    import pytc

    # Load in integrated heats from an ITC experiment
    e = pytc.ITCExperiment("demos/ca-edta/tris-01.DH",
                           pytc.indiv_models.SingleSite)

    # Create the global fitter, add the experiment, and fit
    g = pytc.GlobalFit()
    g.add_experiment(e)
    g.fit()

    # Print the results out
    g.plot()
    print(g.fit_as_csv)

Fitting models
-----------------
 + `Individual experiment models included in package <indiv_models.html>`_.
 + `Global fit models included in package <global_models.html>`_.
 + `Defining new models <writing_new_models.html>`_.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   _api/pytc.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
