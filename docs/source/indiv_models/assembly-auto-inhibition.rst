:orphan:

Assembly Auto Inhibition
------------------------
+ Ligand binding at two sites that promotes oligomerization and inhibition of binding.
+ Model contributed by: Martin Rennie, PhD
+ This model is not yet published.
+ `indiv_models\.AssemblyAutoInhibition <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/assembly_auto_inhibition.py>`_

Scheme
~~~~~~

.. image:: images/assembly-auto-inhibition_scheme.png
    :scale: 25%
    :alt: model scheme
    :align: center

Parameters
~~~~~~~~~~
+--------------------------------+------------------------+----------------------------+---------------+
|parameter                       | variable               | parameter name             | class         |
+================================+========================+============================+===============+
|association constant for        |                        |                            |               |
|binding of the first ligand to  |                        |                            |               |
|the protein (M)                 | :math:`K_{1}`          | :code:`Klig1`              | thermodynamic |
+--------------------------------+------------------------+----------------------------+---------------+
|association constant for        |                        |                            |               |
|binding of the second ligand to |                        |                            |               |
|the protein (M)                 | :math:`K_{2}`          | :code:`Klig2`              | thermodynamic |
+--------------------------------+------------------------+----------------------------+---------------+
|"united normalized" association |                        |                            |               |
|constant for formation of the   |                        |                            |               |
|protein oligomer (M)            | :math:`K_{3}`          | :code:`Kolig`              | thermodynamic |
+--------------------------------+------------------------+----------------------------+---------------+
|enthalpy change for             |                        |                            |               |
|binding of the first ligand to  |                        |                            |               |
|the protein                     | :math:`\Delta H_{1}`   | :code:`dHlig1`             | thermodynamic |
+--------------------------------+------------------------+----------------------------+---------------+
|enthalpy change for             |                        |                            |               |
|binding of the second ligand to |                        |                            |               |
|the protein                     | :math:`\Delta H_{2}`   | :code:`dHlig2`             | thermodynamic |
+--------------------------------+------------------------+----------------------------+---------------+
|enthalpy change for formation   |                        |                            |               |
|of the protein oligomer         |                        |                            |               |
|                                | :math:`\Delta H_{3}`   | :code:`dHolig`             | thermodynamic |
+--------------------------------+------------------------+----------------------------+---------------+
| stoichiometry of ligands in    | :math:`n_{L}`          | :code:`n_lig`              | thermodynamic |
| the protein oligomer           |                        |                            |               |
+--------------------------------+------------------------+----------------------------+---------------+
| stoichiometry of proteins in   | :math:`n_{P}`          | :code:`n_prot`             | thermodynamic |
| the protein oligomer           |                        |                            |               |
+--------------------------------+------------------------+----------------------------+---------------+
|fraction competent              | ---                    | :code:`fx_competent`       | nuisance      |
+--------------------------------+------------------------+----------------------------+---------------+
|slope of heat of dilution       | ---                    | :code:`dilution_heat`      | nuisance      |
+--------------------------------+------------------------+----------------------------+---------------+
|intercept of heat of dilution   | ---                    | :code:`dilution_intercept` | nuisance      |
+--------------------------------+------------------------+----------------------------+---------------+

Species
~~~~~~~

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

.. math::
    q_{i} = V_{cell}\Big ( \Delta H_{1}^{\circ}([PL]_{i} - [PL]_{i-1}(1-v_{i}/V_{cell})) \\
                          + (\Delta H_{1}^{\circ} + \Delta H_{2}^{\circ})([PL_{2}]_{i} - [PL_{2}]_{i-1}(1 - v_{i}/V_{cell})) \\
                          +  \Delta H_{3}^{\circ}([P_{olig}]_{i} - [P_{olig}]_{i-1}(1 - v_{i}/V_{cell})) \Big ) + q_{dil}
