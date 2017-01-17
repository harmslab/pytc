=================
Global ITC Models
=================

xxx trickier

Global Model
------------

Fits individual models to a collection of individual ITC experiments.  The parameters of
the individual models can be arbitrarily linked to one another.  For example, the code
below extracts a single :math:`K` and :math:`\Delta H` from three, replicate ITC
experiments, while allowing the fraction competent and the dilution baselines to
float for the individual experiments.

`global_models\.GlobalFit <https://github.com/harmslab/pytc/blob/master/pytc/global_models/base.py>`_

.. sourcecode:: python
    
    import pytc

    # --------------------------------------------------------------------
    # Create a global fitting instance
    g = pytc.global_models.GlobalFit()

    # --------------------------------------------------------------------
    # Load in an experimental data set with a single-site binding model
    a = pytc.ITCExperiment("demos/ca-edta/tris-01.DH",pytc.indiv_models.SingleSite,shot_start=2)

    # Add the experiment to the fitter.  Then link the dilution heat and
    # intercept to global parameters
    g.add_experiment(a)
    g.link_to_global(a,"K","global_K")
    g.link_to_global(a,"dH","global_dH")

    # --------------------------------------------------------------------
    # Load in a second experimental data set with a single-site binding model
    b = pytc.ITCExperiment("demos/ca-edta/tris-02.DH",pytc.indiv_models.SingleSite,shot_start=2)

    # Add a blank titration to the fitter. Then link the dilution heat and
    # intercept to global parameters
    g.add_experiment(b)
    g.link_to_global(b,"K","global_K")
    g.link_to_global(b,"dH","global_dH")

    # --------------------------------------------------------------------
    # Load in a third experimental data set with a single-site binding model
    c = pytc.ITCExperiment("demos/ca-edta/tris-03.DH",pytc.indiv_models.SingleSite,shot_start=2)

    # Add a blank titration to the fitter. Then link the dilution heat and
    # intercept to global parameters
    g.add_experiment(c)
    g.link_to_global(c,"K","global_K")
    g.link_to_global(c,"dH","global_dH")

    # --------------------------------------------------------------------
    # Do a global fit to the single-site and blank titrations
    g.fit()

    # --------------------------------------------------------------------
    # Show the results
    fig, ax = g.plot()
    print(g.fit_as_csv)


Proton Linked
-------------

`global_models\.ProtonLinked <https://github.com/harmslab/pytc/blob/master/pytc/global_models/proton_linked.py>`_

Fits a global model to a collection of ITC experiments collected in buffers of the same
pH, but different ionization enthalpies. The :code:`\.add_experiment` method is
subclassed to require an :code:`ionization_enthalpy` parameter for each experiment.
The model also adds the new global parameter :code:`n_protons` (which describes the
number of protons released or taken up during binding).  For experiment :math:`x`,
the enthalpy is given by: 

.. math::
    \Delta H_{x} = \Delta H_{bind} + \Delta H_{ionization,x} \times n_{proton}

By performing experiments in at least two buffers with different ionization enthalpies,
one can extract the buffer-independent :math:`\Delta H_{bind}` and the number of
protons taken up or released with the ligand binds.

The example code below fits the binding of :math:`Ca^{2+}` to :math:`EDTA` in Tris
and imidazole at :math:`pH = 7`. 

.. sourcecode:: python

    # --------------------------------------------------------------------
    # define buffer ionization enthalpies.
    # goldberg et al (2002) Journal of Physical and Chemical Reference Data 31 231,
    # doi: 10.1063/1.1416902
    IMID_IONIZATION_DH = 36.64/4.184*1000
    TRIS_IONIZATION_DH = 47.45/4.184*1000 

    import pytc

    # --------------------------------------------------------------------
    # Create a global fitting instance
    g = pytc.global_models.ProtonLinked()

    # ------------------------------------------------------------------------------------
    # IMIDAZOLE buffer experiment

    imid = pytc.ITCExperiment("demos/ca-edta/imid-01.DH",pytc.indiv_models.SingleSite,shot_start=2)

    g.add_experiment(imid,ionization_enthalpy=IMID_IONIZATION_DH)
    g.link_to_global(imid,"K","global_K")
    g.link_to_global(imid,"dH","dH_global")

    # ------------------------------------------------------------------------------------
    # Tris buffer experiment

    tris = pytc.ITCExperiment("demos/ca-edta/tris-01.DH",pytc.indiv_models.SingleSite,shot_start=2)

    g.add_experiment(tris,ionization_enthalpy=TRIS_IONIZATION_DH)
    g.link_to_global(tris,"K","global_K")
    g.link_to_global(tris,"dH","dH_global")

    # Do a global fit
    g.fit()

    # Show the results
    fig, ax = g.plot()
    print(g.fit_as_csv)


Temperature dependence of enthalpy
----------------------------------

`global_models\.TempDependence <https://github.com/harmslab/pytc/blob/master/pytc/global_models/temp_dependence.py>`_

Fits a collection of ITC experiments collected in identical buffer conditions, but
at different temperatures.  The temperature of each experiment is taken from the
heats file. The model adds the new global parameter :code:`dCp` (the heat capacity
change on binding). For experiment :math:`x`, the enthalpy is given by: 

.. math::
    \Delta H_{x} = \Delta H_{bind,0K + \Delta C_{p} \times T_{x}

By performing experiments at a minimum of two temperatures, one can extract the
enthalpy (extrapolated) to :math:`0 \ K` and the :math:`\Delta C_{p}` for binding.


