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

Quick Start
--------------------------------

Fit a Ca2+/EDTA binding experiment.

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
 + Models to fit individual experiments are described `here <indiv_models.html>`_.
 + Models to fit multiple experiments globally are described `here <global_models.html>`_.

Model API specifications
--------------------------------

Individual models
~~~~~~~~~~~~~~~~~

These models describe a single ITC experiment.  They are passed to 
:code:`pytc.ITCExperiment` along with an appropriate ITC heats file to analyze that
individual experiment.

These models should:

* Be subclasses of :code:`pytc.indiv_models.ITCModel`
* Define a new :code:`__init__` function that uses the contents of the syringe and
  titrant and calculates how the total concentrations of various species change
  over the titration.
* Expose a :code:`dQ` property that gives the heat change per shot.
* Define a :code:`initialize_param` method with all fittable parameters as
  arguments.  Each paramter should have a default value that is a reasonable
  guess for that parameters.

See `pytc\/indiv_models\/single_site.py <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/single_site.py>`_ for a simple example.

See the :code:`model-documention.ipynb` jupyter notebook for full descriptions of
the currently-implemented models.

Global models
~~~~~~~~~~~~~

These models describe relationships between multiple ITC experiments.  They
should be subclasses of :code:`pytc.global_models.base.GlobalModel`. The exact 
implementation of these models depends on the relationships being probed. 
 
At a minimum this will probably require:

* Define :code:`__init__` to add any global parameters unique to the global
  fit (e.g. heat-capacity for a temperature-dependent titration).
* Define :code:`_residuals`, which calculates the (mis)match between the model and all
  loaded data.
* Define :code:`fit`, which manages the global variables
* Define :code:`_get_calc_heats`.  

See :code:`pytc/global_models/temp_dependence.py` for a (relatively) simple example.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   _api/pytc.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
