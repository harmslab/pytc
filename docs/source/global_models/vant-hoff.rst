:orphan:

Van't Hoff
----------

A standard Van't Hoff analysis assuming a constant enthalpy.

`global_connectors\.VantHoff <https://github.com/harmslab/pytc/blob/master/pytc/global_connectors/vant_hoff.py>`_

Fits a collection of ITC experiments collected in identical buffer conditions, but
at different temperatures.  The temperature of each experiment is taken from the
heats file.  Allows extraction of the Van't Hoff enthalpy and binding constant
for the reaction at a defined reference temperature.

Scheme
~~~~~~

.. math::
    \Delta H = \Delta H_{vh}
.. math::
    K = K(T_{ref})exp \Big ( \frac{-\Delta H_{vh}}{R} \Big (\frac{1}{T} - \frac{1}{T_{ref}} \Big ) \Big )

By performing experiments at a minimum of two temperatures, one can extract the
Van't Hoff enthalpy :math:`\Delta H_{vh}` and binding constant at the reference
temperature :math:`K(T_{ref})`.


Parameters
~~~~~~~~~~
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
|data                             | variable                             | parameter name             |
+=================================+======================================+============================+
|temperature (K)                  | :math:`T`                            | :code:`temperature`        |
+---------------------------------+--------------------------------------+----------------------------+
