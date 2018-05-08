:orphan:

Competitive ligand binding
--------------------------
+ Model binding where two molecules compete for binding to a single other molecule.
+ Sigurskjold BW (2000) *Analytical Biochemistry* 277(2):260-266 `(link) <http://dx.doi.org/10.1006/abio.1999.4402>`_.
+ `indiv_models\.SingleSiteCompetitor <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/single_site_competitor.py>`_

Scheme
~~~~~~
Scheme is for competitive binding of :math:`A` and :math:`B` to protein :math:`P`:

.. math::
    A + P \rightleftharpoons PA
.. math::
    B + P \rightleftharpoons PB

To describe this, we use the following equilibrium constants:

.. math::
    K_{A} = \frac{[PA]}{[P]_{free}[A]_{free}}

.. math::
    K_{B} = \frac{[PB]}{[P]_{free}[B]_{free}}

Parameters
~~~~~~~~~~
+--------------------------------+----------------------+----------------------------+---------------+
|parameter                       | variable             | parameter name             | class         |
+================================+======================+============================+===============+
|association constant for A      | :math:`K_{A}`        | :code:`K`                  | thermodynamic |
+--------------------------------+----------------------+----------------------------+---------------+
|association constant for B      | :math:`K_{B}`        | :code:`Kcompetitor`        | thermodynamic |
+--------------------------------+----------------------+----------------------------+---------------+
|binding enthalpy for A          | :math:`\Delta H_{A}` | :code:`dH`                 | thermodynamic |
+--------------------------------+----------------------+----------------------------+---------------+
|binding enthalpy for B          | :math:`\Delta H_{B}` | :code:`dHcompetitor`       | thermodynamic |
+--------------------------------+----------------------+----------------------------+---------------+
|fraction competent              | `---`                | :code:`fx_competent`       | nuisance      |
+--------------------------------+----------------------+----------------------------+---------------+
|slope of heat of dilution       | `---`                | :code:`dilution_heat`      | nuisance      |
+--------------------------------+----------------------+----------------------------+---------------+
|intercept of heat of dilution   | `---`                | :code:`dilution_intercept` | nuisance      |
+--------------------------------+----------------------+----------------------------+---------------+

Species
~~~~~~~

We can only manipulate :math:`[P]_{total}`, :math:`[A]_{total}` and :math:`[B]_{total}` experimentally, so our first goal is to determine the concentrations of species such as :math:`[PA]`, which we cannot manipulate or directly observe.  Start by writing concentrations as mole fractions:

.. math::
    x_{P} = \frac{[P]_{free}}{[P]_{total}}

.. math::
    x_{PA} = \frac{[PA]}{[P]_{total}}

.. math::
    x_{PB} = \frac{[PB]}{[P]_{total}}

.. math::
    x_{P} + x_{PA} + x_{PB} = 1

A root of the binding polynomial has been found that describes :math:`x_{P}` only in terms of :math:`K_{A}`, :math:`K_{B}`, :math:`[A]_{total}`, :math:`[B]_{total}` and :math:`[P]_{total}`.  Start with some convenient definitions:

.. math::
    c_{A} = K_{A}[P]_{total}

.. math::
    c_{B} = K_{B}[P]_{total}

.. math::
    r_{A} = \frac{[A]_{total}}{P_{total}}

.. math::
    r_{B} = \frac{[B]_{total}}{P_{total}}

The value of :math:`x_{P}` is given by:

.. math::
    \alpha = \frac{1}{c_{A}} + \frac{1}{c_{B}} + r_{A} + r_{B} - 1

.. math::
    \beta = \frac{r_{A}-1}{c_{B}} + \frac{r_{B} - 1}{c_{A}} + \frac{1}{c_{A}c_{B}}

.. math::
    \gamma = -\frac{1}{c_{A}c_{B}}

.. math::
    \theta = arccos \Big ( \frac{-2\alpha^{3} + 9\alpha \beta -27\gamma}{2\sqrt{(\alpha^2 - 3 \beta)^3}} \Big)

.. math::
    x_{P} = \frac{2\sqrt{\alpha^2 - 3 \beta}\ cos(\theta/3) - \alpha}{3}

Once this is known :math:`x_{PA}` and :math:`x_{PB}` are uniquely determined by:

.. math::
    x_{PA} = \frac{r_{A} x_{P}}{1/C_{A} + x_{P}}

.. math::
    x_{PB} = \frac{r_{B} x_{P}}{1/C_{B} + x_{P}}

Heat
~~~~
The heat for each shot :math:`i` (:math:`q_{i}`) is:

.. math::
    q_{i} = V_{0}P_{total}(\Delta H_{A}(x_{PA,i} - f_{i}x_{PA,i-1}) + \Delta H_{B}(x_{PB,i} - f_{i}x_{PB,i-1})) + q_{dilution},

where :math:`V_{0}` is the volume of the cell, :math:`\Delta H_{A}` is the enthalpy for binding ligand :math:`A`, :math:`\Delta H_{B}` is the enthalpy for binding ligand :math:`B`. :math:`f_{i}` is the dilution factor for each injection:

.. math::
    f_{i} = exp(-V_{i}/V_{0}),

where :math:`V_{0}` is the volume of the cell and :math:`V_{i}` is the volume of the :math:`i`-th injection.

**pytc** calculates :math:`x_{PA,i}` and friends for the entire titration, correcting for dilution.  This means the :math:`f_{i}` term is superfluous.  Thus, heats are related by:

.. math::
    q_{i} = V_{0}P_{total,i}(\Delta H_{A}(x_{PA,i} - x_{PA,i-1}) + \Delta H_{B}(x_{PB,i} - x_{PB,i-1})) + q_{dilution}.

Note that :math:`V_{0}` is held constant (it is the cell volume) as only that volume is detected, not the neck of the cell.
