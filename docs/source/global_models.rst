:orphan:

==============
Global Fitting
==============

Simple global parameters
------------------------

The first (and simplest) sort of global fit is to declare that parameters
from separate experiments should use the same, shared, fitting parameter.  The
following code takes two experimental replicates and fits them to a single
:math:`K` and :math:`\Delta H`.  The code that actually does the linking is
highlighted with :code:`***`

.. code:: python

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
rest. The output of this fit will look something like the following.  The
global parameters appear as :code:`global_K` and :code:`global_dH`.

|   type,name,dh_file,value,uncertainty,fixed,guess,lower_bound,upper_bound
|   global,global_K,NA,3.84168e+07,1.40582e-06,float,1.00000e+06,-inf,inf
|   global,global_dH,NA,-4.64104e+03,7.96280e-03,float,-4.00000e+03,-inf,inf
|   ...

Global connectors
-----------------

**pytc** also defines global connectors that link titrations to one
another.  For example, one might perform the same binding experiment at different
temperatures and use that information to perform a Van 't Hoff analysis.

Implemented connectors
~~~~~~~~~~~~~~~~~~~~~~

+ `Proton-linked <global_models/proton-linked.html>`_
+ `Van 't Hoff <global_models/vant-hoff.html>`_
+ `Extended Van 't Hoff <global_models/vant-hoff-extended.html>`_

Example 1: van 't Hoff fit
~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code takes two experiments, done at :math:`5\ ^{\circ}C` and
:math:`10\ ^{\circ}C` and then uses them to extract the van't Hoff enthalpy.
(In practice, this would require more than two temperatures, but it illustrates
the approach).  The code that actually does the linking is highlighted with
:code:`***`

.. code:: python

    import pytc
    from pytc import global_connectors

    # Create fitter
    g = pytc.GlobalFit()

    # Load experiments
    t5 = pytc.ITCExperiment("temp-dependence/5C.DH",
                            pytc.indiv_models.SingleSite,
                            shot_start=1)
    g.add_experiment(t5)

    t10 = pytc.ITCExperiment("temp-dependence/10C.DH",
                             pytc.indiv_models.SingleSite,
                             shot_start=1)
    g.add_experiment(t10)

    # **********************************
    # Create a van't hoff GlobalConnector, assigning the prefix "vh" to each parameter
    vh_conn = pytc.global_connectors.VantHoff("vh")

    # Link 5 C experiment into connector
    g.link_to_global(t5,"dH",vh_conn.dH)
    g.link_to_global(t5,"K",vh_conn.K)

    # Link 10 C experiment into connector
    g.link_to_global(t10,"dH",vh_conn.dH)
    g.link_to_global(t10,"K",vh_conn.K)
    # **********************************

    # Fit and show results
    g.fit()
    print(g.fit_as_csv)

The new global parameters are assigned the name "vh_K_ref" and
"vh_dH_vanthoff".  The output of this fit will look something like the following.

|    type,name,exp_file,value,stdev,bot95,top95,fixed,guess,lower_bound,upper_bound
|    global,vh_K_ref,NA,9.06284e+03,2.66839e+02,8.53780e+03,9.64146e+03,False,1.00000e+00,-inf,inf
|    global,vh_dH_vanthoff,NA,-6.23127e+03,1.15980e+02,-6.46163e+03,-5.96134e+03,False,0.00000e+00,-inf,inf
|    ...

Note the similarity to the simple global fit.  The main difference is that we have
defined a connector (:code:`vh_conn`) that we link variables to as opposed to a
name: for example, :code:`vh_conn.K` rather than :code:`"K_global"`.

Example 2:
~~~~~~~~~~

The following code takes two experiments, one in Tris and another in Imidazole,
and uses them to extract the buffer-independent binding enthalpy and number of
protons released (or taken up) upon binding.  The code that actually does the
linking is highlighted with :code:`***`

.. code:: python

    import pytc
    from pytc import global_connectors

    # define buffer ionization enthalpies.
    # goldberg et al (2002) Journal of Physical and Chemical Reference Data 31 231,  doi: 10.1063/1.1416902
    TRIS_IONIZATION_DH = 47.45/4.184*1000
    IMID_IONIZATION_DH = 36.64/4.184*1000

    # Create fitter
    g = pytc.GlobalFit()

    # Load in an experiment done in tris buffer
    tris = pytc.ITCExperiment("demos/ca-edta/tris-01.DH",
                              pytc.indiv_models.SingleSite,
                              shot_start=2)
    tris.ionization_enthalpy = TRIS_IONIZATION_DH
    g.add_experiment(tris)

    # Imidazole buffer experiment
    imid = pytc.ITCExperiment("demos/ca-edta/imid-01.DH",
                              pytc.indiv_models.SingleSite,
                              shot_start=2)
    imid.ionization_enthalpy = IMID_IONIZATION_DH
    g.add_experiment(imid)

    # **********************************
    # Create a NumProtons GlobalConnector, assigning the prefix "np" to each parameter
    num_protons = global_connectors.NumProtons("np")
    g.link_to_global(tris,"dH",num_protons.dH)
    g.link_to_global(imid,"dH",num_protons.dH)
    # **********************************

    # Fit and show results
    g.fit()
    print(g.fit_as_csv)

This will spit out:

|   type,name,dh_file,value,uncertainty,fixed,guess,lower_bound,upper_bound
|   global,np_num_H,NA,-9.79065e-01,1.15256e+00,float,1.00000e-01,-inf,inf
|   global,np_dH_intrinsic,NA,-4.63537e+02,1.08227e-02,float,0.00000e+00,-inf,inf
|   ...

The major difference between this code and the van't Hoff analysis is the
line in which we assign the ionization enthalpy for each experiment (for example,
:code:`tris.ionization_enthalpy = TRIS_IONIZATION_DH`). This provides the
information required by the :code:`NumProtons` class do perform the fit.  If you
are using a different global connector, you could set different properties in
this way (pH, competitor concentration, etc.). Note: :code:`experiment.temperature`
is always defined in ITC output, so it should never have to be set manually.
