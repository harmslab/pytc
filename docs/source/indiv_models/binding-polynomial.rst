:orphan:

Binding Polynomial
------------------
+ Binding polynomial for binding at :math:`N` sites.  Adair constants.
+ Freire et al. (2009). *Methods in Enzymology* 455:127-155 `(link) <http://www.sciencedirect.com/science/article/pii/S0076687908042055>`_.
+ `indiv_models\.BindingPolynomial <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/binding_polynomial.py>`_

Scheme
~~~~~~
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

Parameters
~~~~~~~~~~
+--------------------------------+------------------------+----------------------------+---------------+
|parameter                       | variable               | parameter name             | class         |
+================================+========================+============================+===============+
|Adair constant for site 1       | :math:`\beta_{1}`      | :code:`beta1`              | thermodynamic |
+--------------------------------+------------------------+----------------------------+---------------+
|binding enthalpy for site 1     | :math:`\Delta H_{1}`   | :code:`dH1`                | thermodynamic |
+--------------------------------+------------------------+----------------------------+---------------+
| This will have as many :math:`\beta` and :math:`\Delta H` terms as sites defined in the model.       |
+--------------------------------+------------------------+----------------------------+---------------+
|fraction competent              | ---                    | :code:`fx_competent`       | nuisance      |
+--------------------------------+------------------------+----------------------------+---------------+
|slope of heat of dilution       | ---                    | :code:`dilution_heat`      | nuisance      |
+--------------------------------+------------------------+----------------------------+---------------+
|intercept of heat of dilution   | ---                    | :code:`dilution_intercept` | nuisance      |
+--------------------------------+------------------------+----------------------------+---------------+

Species
~~~~~~~

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

Heat
~~~~

We can relate the heat at shot to the average enthalpies calculated using the value of :math:`T_{free}` over the titration.  Recalling:

.. math::
    \langle \Delta H \rangle = \frac{\sum_{i=0}^{n} \Delta H_{i} \beta_{i}[T]_{free}^{i}} {\sum_{i=0}^{n} \beta_{i}[T]_{free}^{i}}

we can calculate the change in heat for shot :math:`j` as:

.. math::
    \q_{j} = V_{0} S_{total,j} (\langle \Delta H \rangle_{j} - \langle \Delta H \rangle_{j-1}) + q_{dilution,i}.


