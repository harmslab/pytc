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
