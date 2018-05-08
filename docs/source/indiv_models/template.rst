The Name of the Model
---------------------

DIRECTIONS: Update the name of the model and change the following.

+ A one sentence description of the model.
+ Contributed by: Jane Doe, [email, url, other info you wish to provide]
+ `plain text, human-readable citation. <url_to_citation>`_
+ `indiv_models\.NAME_OF_MODEL_CLASS <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/NAME_OF_MODEL_FILE>`_

A longer description of the model, if desired/needed.

Scheme
~~~~~~

DIRECTIONS: Put a png image describing the scheme in the "docs/source/indiv_models" folder and link to it here.

.. image:: assembly-auto-inhibition_scheme.png
    :scale: 25%
    :alt: model scheme
    :align: center

DIRECTIONS: Alternatively, write up your scheme in text/LaTeX.

Scheme is for binding of titrant :math:`T` to a stationary species :math:`S`:

.. math::
    S + T \rightleftharpoons TS

To describe this, we use the following equilibrium constant:

.. math::
    K = \frac{[ST]}{[S]_{free}[T]_{free}}


Parameters
~~~~~~~~~~

DIRECTIONS: Update the table, using the description in the first data row.

+--------------------------------+------------------------+----------------------------+---------------+
|parameter                       | variable               | parameter name             | class         |
+================================+========================+============================+===============+
|description of the parameter in | name of variable in the| name of the variable in the| whether the   |
|enough detail that we know what | scheme (see below for  | python code (see below for | variable is   |
|it means                        | example)               | example)                   | nuisance or   |
|                                |                        |                            | thermodynamic |
+--------------------------------+------------------------+----------------------------+---------------+
|example: association constant   |                        |                            |               |
|for binding of the second       |                        |                            |               |
|ligand to the protein (M)       | :math:`K_{2}`          | :code:`Klig2`              | thermodynamic |
+--------------------------------+------------------------+----------------------------+---------------+
|fraction competent              | ---                    | :code:`fx_competent`       | nuisance      |
+--------------------------------+------------------------+----------------------------+---------------+
|slope of heat of dilution       | ---                    | :code:`dilution_heat`      | nuisance      |
+--------------------------------+------------------------+----------------------------+---------------+
|intercept of heat of dilution   | ---                    | :code:`dilution_intercept` | nuisance      |
+--------------------------------+------------------------+----------------------------+---------------+

Species
~~~~~~~

DIRECTIONS: Write mathematical description of the species in solution at shot "i".  Use standard LaTeX for formatting.

.. math::
    [P_{T}]_{i} =   [P]_{i} + [PL]_{i} + [PL_{2}]_{i} + 4[P_{olig}]_{i}

.. math::
    [L_{T}]_{i} = [L]_{i} + [PL]_{i} + 2[PL_{2}]_{i} + n_{L}[P_{olig}]_{i}

.. math::
    [PL]_{i} = K_{1}[P]_{i}[L]_{i}

.. math::
    [PL_{2}]_{i} = K_{1}K_{2}[P]_{i}[L]_{i}^{2}

.. math::
    [P_{olig}]_{i} = K_{3}[P]_{i}^{4}[L]_{i}^{n_{L}}


Heat
~~~~
DIRECTIONS: Write mathematical description the heat at shot "i".  Use standard LaTeX for formatting.

.. math::
    q_{i} = V_{cell}\Big ( \Delta H_{1}^{\circ}([PL]_{i} - [PL]_{i-1}(1-v_{i}/V_{cell})) \\
                          + (\Delta H_{1}^{\circ} + \Delta H_{2}^{\circ})([PL_{2}]_{i} - [PL_{2}]_{i-1}(1 - v_{i}/V_{cell})) \\
                          +  \Delta H_{3}^{\circ}([P_{olig}]_{i} - [P_{olig}]_{i-1}(1 - v_{i}/V_{cell})) \Big ) + q_{dil}
