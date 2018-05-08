:orphan:

Blank
-----

+ Titration of titrant into a cell without a stationary component.
+ `indiv_models\.Blank <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/blank.py>`_

Parameters
~~~~~~~~~~
+---------------------------------+-----------------------+---------------------------+---------------+
|parameter                        |  variable             | parameter name            | class         |
+=================================+=======================+===========================+===============+
|slope of heat of dilution        | :math:`q_{slope}`     |:code:`dilution_heat`      | nuisance      |
+---------------------------------+-----------------------+---------------------------+---------------+
|intercept of heat of dilution    | :math:`q_{intercept}` |:code:`dilution_intercept` | nuisance      |
+---------------------------------+-----------------------+---------------------------+---------------+

Heat
~~~~
The heat for each shot :math:`i` (:math:`q_{i}`) is:

.. math::
    q_{dilution,i} = [T]_{i} \times q_{slope} + q_{intercept},

    q_{i} = q_{dilution,i},

where :math:`[T]_{i}` is the concentration of titrant at shot :math:`i`, :math:`q_{slope}` is the slope of the heat of dilution (:code:`dilution_heat`) and :math:`q_{intercept}` is the intercept of the heat of dilution (:code:`dilution_intercept`).
