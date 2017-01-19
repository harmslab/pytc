=============================================
Models for fitting individual ITC experiments
=============================================

Basic model pipeline
====================
The basic procedure for fitting a model to an individual ITC experiments is:

1. Guess model parameters.
2. Use the parameter guesses to calculate the concentrations of all molecular species over the course of the experiment.
3. Combine the estimated species concentrations with the guessed enthalpy(s) to calculate the heat change for each shot. 
4. Compare the calculated and measured heat changes at each shot.  
5. Iterate through steps 2-4 using nonlinear regression to find maximum likelihood parameter estimates. 

Differences from other modeling approaches
==========================================
The models used by *pytc* differ from models in Origin in two ways:

1. The dilution correction is a fittable parameter within each model, treated as a linear function of titrant concentration.  To incorporate a blank titration, you globally fit the dilution for the blank and production experiments (see `Demo.ipynb <https://github.com/harmslab/pytc/https://github.com/harmslab/pytc/blob/master/Demo.ipynb>`_ for an example). 
2. The stoichiometry of each model is fixed (rather than fittable). Instead, there is a fraction competent (:code:`fx_competent`) parameter that floats to account for inaccurate measurements of the concentrations of either the titrant or stationary phase.  This follows the approach used by `sedphat <http://www.analyticalultracentrifugation.com/sedphat/sedphat.htm>`_.  If this value is very different than one, it indicates a problem with the experiment.  

Specific Models
===============

Blank
-----

Titration of titrant into a cell without a stationary component. 
 
`indiv_models\.Blank <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/blank.py>`_


Model parameters
~~~~~~~~~~~~~~~~
+---------------------------------+-----------------------+---------------------------+---------------+
|parameter                        |  variable             | parameter name            | class         |
+=================================+=======================+===========================+===============+
|slope of heat of dilution        | :math:`q_{slope}`     |:code:`dilution_heat`      | nuisance      |
+---------------------------------+-----------------------+---------------------------+---------------+
|intercept of heat of dilution    | :math:`q_{intercept}` |:code:`dilution_intercept` | nuisance      |
+---------------------------------+-----------------------+---------------------------+---------------+

Calculate heat changes
~~~~~~~~~~~~~~~~~~~~~~
The change in heat for each shot :math:`i` (:math:`\Delta Q_{i}`) is:

.. math::
    q_{dilution,i} = [T]_{i} \times q_{slope} + q_{intercept},

    \Delta Q_{i} = q_{dilution,i},

where :math:`[T]_{i}` is the concentration of titrant at shot :math:`i`, :math:`q_{slope}` is the slope of the heat of dilution (:code:`dilution_heat`) and :math:`q_{intercept}` is the intercept of the heat of dilution (:code:`dilution_intercept`).  

Single-Site Binding
-------------------
This is a basic, single-site binding model.

`indiv_models\.SingleSite <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/single_site.py>`_

Model parameters
~~~~~~~~~~~~~~~~
+---------------------------------+------------------+----------------------------+---------------+
|parameter                        | variable         | parameter name             | class         |
+=================================+==================+============================+===============+
|association constant             | :math:`K`        | :code:`K`                  | thermodynamic |
+---------------------------------+------------------+----------------------------+---------------+
|binding enthalpy                 | :math:`\Delta H` | :code:`dH`                 | thermodynamic |
+---------------------------------+------------------+----------------------------+---------------+
|fraction competent               | `---`            | :code:`fx_competent`       | nuisance      |
+---------------------------------+------------------+----------------------------+---------------+
|slope of heat of dilution        | `---`            | :code:`dilution_heat`      | nuisance      |
+---------------------------------+------------------+----------------------------+---------------+
|intercept of heat of dilution    | `---`            | :code:`dilution_intercept` | nuisance      |
+---------------------------------+------------------+----------------------------+---------------+

Model Scheme
~~~~~~~~~~~~
Scheme is for binding of titrant :math:`T` to a stationary species :math:`S`:

.. math::
    S + T \rightleftharpoons TS

To describe this, we use the following equilibrium constant:

.. math::
    K = \frac{[ST]}{[S]_{free}[T]_{free}}


Determine the relative populations of species in solution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We can only manipulate :math:`[T]_{total}` and :math:`[S]_{total}` experimentally, so our first goal is to determine the concentration of :math:`[ST]`, which we cannot manipulate or directly observe.  

.. math::
    K = \frac{[ST]}{([S]_{total} - [ST])([T]_{total}-[ST])},
.. math::
    K \Big ([S]_{total}[T]_{total} - [ST]([S]_{total} + [T]_{total}) + [ST]^2 \Big ) = [ST],
.. math::    
    [S]_{total}[T]_{total} - [ST](S_{total} + T_{total}) + [ST]^{2} - [ST]/K = 0,
.. math::
    [S]_{total}[T]_{total} - [ST]([S]_{total} + [T]_{total} + 1/K) + [ST]^2 = 0.

The real root of this equation describes :math:`[ST]` in terms of :math:`K` and the total concentrations of :math:`[S]` and :math:`[T]`:

.. math::
    [ST] = \frac{[S]_{total}  + [T]_{total} + 1/K - \sqrt{([S]_{total} + [T]_{total} + 1/K)^2 -4[S]_{total}[T]_{total}}}{2}

The mole fraction :math:`ST` is:

.. math::
    x_{ST} = \frac{[ST]}{[S]_{total}}

Calculate heat changes
~~~~~~~~~~~~~~~~~~~~~~

The change in heat for each shot :math:`i` (:math:`\Delta Q_{i}`) is:

.. math::
    \Delta Q_{i} = V_{0}[S]_{total,i}(\Delta H(x_{ST,i} - x_{ST,i-1})) + q_{dilution,i},

where :math:`V_{0}` is the volume of the cell (fixed) and :math:`\Delta H` is the enthalpy of binding. Note that we do not deal with dilution here, as *pytc* calculates :math:`x_{ST,i}` for the entire titration, accouting for dilution at each step.  :math:`V_{0}` is held constant as the total cell volume (not the volume of solution including the neck) as only the cell, not the neck, is detected in the signal.  


Competitive ligand binding
--------------------------
Model binding where two molecules compete for binding to a single other molecule.  This model was described by Sigurskjold BW (2000) *Analytical Biochemistry* 277(2):260-266 `(link) <http://dx.doi.org/10.1006/abio.1999.4402>`_.

`indiv_models\.SingleSiteCompetitor <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/single_site_competitor.py>`_


Model parameters
~~~~~~~~~~~~~~~~
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

Model Scheme
~~~~~~~~~~~~
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


Determine the relative populations of species in solution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Calculate heat changes
~~~~~~~~~~~~~~~~~~~~~~
The change in heat for each shot :math:`i` (:math:`\Delta Q_{i}`) is:

.. math::
    \Delta Q_{i} = V_{0}P_{total}(\Delta H_{A}(x_{PA,i} - f_{i}x_{PA,i-1}) + \Delta H_{B}(x_{PB,i} - f_{i}x_{PB,i-1})) + q_{dilution},

where :math:`V_{0}` is the volume of the cell, :math:`\Delta H_{A}` is the enthalpy for binding ligand :math:`A`, :math:`\Delta H_{B}` is the enthalpy for binding ligand :math:`B`. :math:`f_{i}` is the dilution factor for each injection: 
 
.. math::
    f_{i} = exp(-V_{i}/V_{0}),

where :math:`V_{0}` is the volume of the cell and :math:`V_{i}` is the volume of the :math:`i`-th injection.

*pytc* calculates :math:`x_{PA,i}` and friends for the entire titration, correcting for dilution.  This means the :math:`f_{i}` term is superfluous.  Thus, heats are related by:

.. math::
    \Delta Q_{i} = V_{0}P_{total,i}(\Delta H_{A}(x_{PA,i} - x_{PA,i-1}) + \Delta H_{B}(x_{PB,i} - x_{PB,i-1})) + q_{dilution}.

Note that :math:`V_{0}` is held constant (it is the cell volume) as only that volume is detected, not the neck of the cell.


Binding Polynomial
------------------
This model was described by Freire et al. (2009). *Methods in Enzymology* 455:127-155 `(link) <http://www.sciencedirect.com/science/article/pii/S0076687908042055>`_.

`indiv_models\.BindingPolynomial <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/binding_polynomial.py>`_


Model parameters
~~~~~~~~~~~~~~~~
+--------------------------------+------------------------+----------------------+---------------+
|parameter                       | variable               | parameter name       | class         |
+================================+========================+======================+===============+
|adair constant for site 1       | :math:`\beta_{1}`      | `beta1`              | thermodynamic |
+--------------------------------+------------------------+----------------------+---------------+
|binding enthalpy for site 1     | :math:`\Delta H_{1}`   | `dH1`                | thermodynamic |
+--------------------------------+------------------------+----------------------+---------------+
| This will have as many :math:`\beta` and :math:`\Delta H` terms as sites defined in the model. |
+--------------------------------+------------------------+----------------------+---------------+
|fraction competent              | ---                    | `fx_competent`       | nuisance      |
+--------------------------------+------------------------+----------------------+---------------+
|slope of heat of dilution       | ---                    | `dilution_heat`      | nuisance      |
+--------------------------------+------------------------+----------------------+---------------+
|intercept of heat of dilution   | ---                    | `dilution_intercept` | nuisance      |
+--------------------------------+------------------------+----------------------+---------------+

Model Scheme
~~~~~~~~~~~~
The scheme is:

.. math::
    S + iT \rightleftharpoons ST_{i}

where :math:`S` is the stationary species and :math:`T` is the titrant.  This is an overall binding polynomial, meaning that we account for the total loading of :math:`i` molecules of :math:`T` onto :math:`S`. The equilibrium constants (Adair constants) are:

.. math::
    \beta_{i} = \frac{[ST_{i}]}{[S][T]^{i}}

This model is entirely general (and therefore phenomenological), but is an appropriate starting point for analyzing a complex binding reaction.  The Adair constants can be related to a sequential binding model by:

.. math::
    S + T \rightleftharpoons ST
.. math::
    ST + T \rightleftharpoons ST_{2}
.. math::
    ...
.. math::
    ST_{i-1} + T \rightleftharpoons ST_{i}
.. math::
    K_{i} = \frac{[ML_{i}]}{[ML_{i-1}][L]} = \frac{\beta_{i}}{\beta_{i-1}}

Determine the relative populations of species in solution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first thing to note is that the binding polynomial :math:`P` is a partition function:

.. math::
    P = \sum_{i=0}^{n}\frac{[ST_{i}]}{[S]} = \sum_{i=0}^{n} \beta_{i}[T]^{i}

This allows us to write equations for the average enthalphy and number of ligand molecules bound:

.. math::
    \langle \Delta H \rangle = \frac{\sum_{i=0}^{n} \Delta H_{i} \beta_{i}[T]^{i}} {\sum_{i=0}^{n} \beta_{i}[T]^{i}}

and 

.. math::
    \langle n \rangle = \frac{\sum_{i=0}^{n} i \beta_{i}[T]^{i}} {\sum_{i=0}^{n} \beta_{i}[T]^{i}}

This means that obtaining the relative populations of species in solution is (relatively) simple:

.. math::
    [T]_{total} = [T]_{bound} + [T]_{free}

.. math::
    [T]_{total} = \langle n \rangle[S]_{total} + [T]_{free}

.. math::
    0 = \langle n \rangle[S]_{total} + [T]_{free} - [T]_{total}

.. math::
    0 = \frac{\sum_{i=0}^{n} i \beta_{i}[T]_{free}^{i}} {\sum_{i=0}^{n} \beta_{i}[T]_{free}^{i}}[S]_{total} + [T]_{free} - [T]_{total}

This can then be solved numerically for a value of :math:`[T]_{free}`.  

Calculate heat changes
~~~~~~~~~~~~~~~~~~~~~~

We can relate the heat at shot to the average enthalpies calculated using the value of :math:`T_{free}` over the titration.  Recalling:

.. math::
    \langle \Delta H \rangle = \frac{\sum_{i=0}^{n} \Delta H_{i} \beta_{i}[T]_{free}^{i}} {\sum_{i=0}^{n} \beta_{i}[T]_{free}^{i}}

we can calculate the change in heat for shot :math:`j` as:

.. math::
    \Delta Q_{j} = V_{0} S_{total,j} (\langle \Delta H \rangle_{j} - \langle \Delta H \rangle_{j-1}) + q_{dilution,i}.

