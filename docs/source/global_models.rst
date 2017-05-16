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

Proton linked
--------------

This fits a global model to a collection of ITC experiments collected in buffers
of the same pH, but different ionization enthalpies. 

`global_connectors\.NumProtons <https://github.com/harmslab/pytc/blob/master/pytc/global_connectors/num_protons.py>`_

This is useful for analyzing a binding reaction that involves the gain or loss of
a proton.  The measured enthalpy will have a binding component and an ionization
component.  These can be separated by performing ITC experiments using buffers
with different ionization enthalpies. 

Model parameters
~~~~~~~~~~~~~~~~
+---------------------------------+------------------------------+----------------------------+---------------+
|parameter                        | variable                     | parameter name             | class         |
+=================================+==============================+============================+===============+
|association constant             | :math:`\Delta H_{intrinsic}` | :code:`dH_intrinsic`       | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+
|binding enthalpy                 | :math:`n_{proton}`           | :code:`num_protons`        | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+

Required data for each experiment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
+---------------------------------+--------------------------------------+----------------------------+
|data                             | variable                             | data                       |
+=================================+======================================+============================+
|ioinzation enthalpy              | :math:`\Delta H_{ionization,buffer}` | :code:`ionization_enthalpy`|      
+---------------------------------+--------------------------------------+----------------------------+

Model Scheme
~~~~~~~~~~~~

.. math::
    \Delta H_{obs,buffer} = \Delta H_{intrinsic} + \Delta H_{ionization,buffer} \times n_{proton},

where :math:`\Delta H_{intrinsic}` is the buffer-independent binding enthalpy, 
:math:`\Delta H_{ionization,buffer}` is the buffer ionization enthalpy, and 
:math:`n_{proton}` is the number of protons gained or lost.  


Van't Hoff
----------

A standard Van't Hoff analysis assuming a constant enthalpy.

`global_connectors\.VantHoff <https://github.com/harmslab/pytc/blob/master/pytc/global_connectors/vant_hoff.py>`_

Fits a collection of ITC experiments collected in identical buffer conditions, but
at different temperatures.  The temperature of each experiment is taken from the
heats file.  Allows extraction of the Van't Hoff enthalpy and binding constant 
for the reaction at a defined reference temperature.

Model parameters
~~~~~~~~~~~~~~~~
+---------------------------------+------------------------------+----------------------------+---------------+
|parameter                        | variable                     | parameter name             | class         |
+=================================+==============================+============================+===============+
|association constant             | :math:`K_{ref}`              | :code:`K`                  | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+
|binding enthalpy                 | :math:`\Delta H_{vh}`        | :code:`dH`                 | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+

Required data for each experiment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
+---------------------------------+--------------------------------------+----------------------------+
|data                             | variable                             | data                       |
+=================================+======================================+============================+
|temperature (K)                  | :math:`T`                            | :code:`temperature`        |      
+---------------------------------+--------------------------------------+----------------------------+

Model Scheme
~~~~~~~~~~~~

.. math::
    \Delta H = \Delta H_{vh}
.. math::
    K = K(T_{ref})exp \Big ( \frac{-\Delta H_{vh}}{R} \Big (\frac{1}{T} - \frac{1}{T_{ref}} \Big ) \Big )

By performing experiments at a minimum of two temperatures, one can extract the
Van't Hoff enthalpy :math:`\Delta H_{vh}` and binding constant at the reference 
temperature :math:`K(T_{ref})`.


Extended Van't Hoff
-------------------

An extended Van't Hoff analysis that assumes constant heat capacity.

`global_connectors\.VantHoff <https://github.com/harmslab/pytc/blob/master/pytc/global_connectors/vant_hoff_extended.py>`_

Fits a collection of ITC experiments collected in identical buffer conditions, but
at different temperatures.  The temperature of each experiment is taken from the
heats file.  Allows extraction of the heat capacity, as well as the enthalpy and 
binding constant at a reference temperature. 

Model parameters
~~~~~~~~~~~~~~~~
+---------------------------------+------------------------------+----------------------------+---------------+
|parameter                        | variable                     | parameter name             | class         |
+=================================+==============================+============================+===============+
|association constant             | :math:`K_{ref}`              | :code:`K`                  | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+
|binding enthalpy                 | :math:`\Delta H_{ref}`       | :code:`dH`                 | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+
|heat capacity                    | :math:`\Delta C_{p}`         | :code:`dCp`                | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+

Required data for each experiment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
+---------------------------------+--------------------------------------+----------------------------+
|data                             | variable                             | data                       |
+=================================+======================================+============================+
|temperature (K)                  | :math:`T`                            | :code:`temperature`        |      
+---------------------------------+--------------------------------------+----------------------------+

Model Scheme
~~~~~~~~~~~~

.. math::
    \Delta H(T) = \Delta H_{ref} + \Delta C_{p}(T - T_{ref})

.. math::
    K = K(T_{ref})exp \Big ( \frac{-\Delta H_{ref}}{R} \Big (\frac{1}{T} - \frac{1}{T_{ref}} \Big ) + \frac{\Delta C_{p}}{R} \Big ( ln(T/T_{re}) + T/T_{ref} - 1 \Big ) \Big )

By performing experiments at a minimum of two temperatures, one can extract the
heat capacity :math:`\Delta C_{p}`, the enthalpy at a reference temperture 
:math:`\Delta H_{ref}` and the binding constant at a reference temperature 
:math:`K_{ref}`.
