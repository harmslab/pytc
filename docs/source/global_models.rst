:orphan:

=================
Global ITC Models
=================

Simple global parameters
------------------------

The first (and simplest) sort of global fit is to declare that parameters
from separate experiments should use the same, shared, fitting parameter.  The
following code takes two experimental replicates and fits them to a single
:math:`K` and :math:`\Delta H`.  The code that actually does the linking is
highlighted with :code:`***`

.. sourcecode:: python

    import pytc

    # Create fitter
    g = pytc.GlobalFit()

    # Load experiments
    a = pytc.ITCExperiment("demos/ca-edta/hepes-01.DH",pytc.indiv_models.SingleSite,shot_start=2)
    g.add_experiment(a)

    b = pytc.ITCExperiment("demos/ca-edta/hepes-02.DH",pytc.indiv_models.SingleSite,shot_start=2)
    g.add_experiment(b)

    # **********************************
    # Link global fitting parameters
    g.link_to_global(a,"K","global_K")
    g.link_to_global(b,"K","global_K")

    g.link_to_global(a,"dH","global_dH")
    g.link_to_global(b,"dH","global_dH")
    # **********************************

    # Fit and show results
    g.fit()
    print(g.fit_as_csv)

The new global parameters are simply assigned a name (:code:`global_K` and
:code:`global_dH`) that are individually fit.  The fitter takes care of the
rest. The output of this fit will look like the following.  The
global parameters appear as :code:`global_K` and :code:`global_dH`.

.. code::

    # Fit successful? True
    # Fit sum of square residuals: 0.634237669456395
    # Fit num param: 8
    # Fit num observations: 108
    # Fit num degrees freedom: 100
    type,name,dh_file,value,uncertainty,fixed,guess,lower_bound,upper_bound
    global,global_K,NA,3.84168e+07,1.40582e-06,float,1.00000e+06,-inf,inf
    global,global_dH,NA,-4.64104e+03,7.96280e-03,float,-4.00000e+03,-inf,inf
    ...

Specific Global Models
----------------------

**pytc** also defines specific global models that link titrations to one
another.  The models currently implemented are:

+ `Proton-linked <global_models/proton-linked.html>`_
+ `Van 't Hoff <global_models/vant-hoff.html>`_
+ `Extended Van 't Hoff <global_models/vant-hoff-extended.html>`_
