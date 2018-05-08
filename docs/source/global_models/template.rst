The Name of the Model
---------------------
DIRECTIONS: Update the name of the model and change the following

+ A one sentence description of the model.
+ Contributed by: Jane Doe, [email, url, other info you wish to provide]
+ `plain text, human-readable citation. <url_to_citation>`_
+ `global_connectors\.NAME_OF_MODEL_CLASS <https://github.com/harmslab/pytc/blob/master/pytc/global_connectors/NAME_OF_MODEL_FILE>`_

A longer description of the model, if desired/needed.

Scheme
~~~~~~
DIRECTIONS: Put a png image describing the scheme in the "docs/source/global_models" folder and link to it here.
.. image:: assembly-auto-inhibition_scheme.png
    :scale: 25%
    :alt: model scheme
    :align: center

DIRECTIONS: Alternatively, write up your scheme in text/LaTex.

.. math::
    \Delta H(T) = \Delta H_{ref} + \Delta C_{p}(T - T_{ref})

.. math::
    K = K(T_{ref})exp \Big ( \frac{-\Delta H_{ref}}{R} \Big (\frac{1}{T} - \frac{1}{T_{ref}} \Big ) + \frac{\Delta C_{p}}{R} \Big ( ln(T/T_{re}) + T/T_{ref} - 1 \Big ) \Big )

By performing experiments at a minimum of two temperatures, one can extract the
heat capacity :math:`\Delta C_{p}`, the enthalpy at a reference temperture
:math:`\Delta H_{ref}` and the binding constant at a reference temperature
:math:`K_{ref}`.


Parameters
~~~~~~~~~~

DIRECTIONS: Update the table, using the description in the first data row.
+---------------------------------+------------------------------+----------------------------+---------------+
|parameter                        | variable                     | parameter name             | class         |
+=================================+==============================+============================+===============+
|description of the parameter in  | name of variable in the      | name of the variable in the| whether the   |
|enough detail that we know what  | scheme (see below for        | python code (see below for | variable is   |
|it means                         | example)                     | example)                   | nuisance or   |
|                                 |                              |                            | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+
|association constant             | :math:`K_{ref}`              | :code:`K`                  | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+
|binding enthalpy                 | :math:`\Delta H_{ref}`       | :code:`dH`                 | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+
|heat capacity                    | :math:`\Delta C_{p}`         | :code:`dCp`                | thermodynamic |
+---------------------------------+------------------------------+----------------------------+---------------+

Required data for each experiment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DIRECTIONS: Update the table, using the description in the first data row.
+---------------------------------+--------------------------------------+----------------------------+
|data                             | variable                             | parameter name             |
+=================================+======================================+============================+
|type of data required for each   | name of variable in the scheme (see  | name of parameter in       |
|experiment in enough detail that | below for an example)                | python code                |
|we know what it means.           |                                      |                            |
+---------------------------------+--------------------------------------+----------------------------+
|temperature (K)                  | :math:`T`                            | :code:`temperature`        |
+---------------------------------+--------------------------------------+----------------------------+
