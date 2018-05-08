:orphan:

Single-Site Binding
-------------------
+ A basic, single-site binding model.
+ `indiv_models\.SingleSite <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/single_site.py>`_

Scheme
~~~~~~
Scheme is for binding of titrant :math:`T` to a stationary species :math:`S`:

.. math::
    S + T \rightleftharpoons TS

To describe this, we use the following equilibrium constant:

.. math::
    K = \frac{[ST]}{[S]_{free}[T]_{free}}

Parameters
~~~~~~~~~~
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

Species
~~~~~~~
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

Heat
~~~~

The heat for each shot :math:`i` (:math:`q_{i}`) is:

.. math::
    q_{i} = V_{0}[S]_{total,i}(\Delta H(x_{ST,i} - x_{ST,i-1})) + q_{dilution,i},

where :math:`V_{0}` is the volume of the cell (fixed) and :math:`\Delta H` is the enthalpy of binding. Note that we do not deal with dilution here, as **pytc** calculates :math:`x_{ST,i}` for the entire titration, accouting for dilution at each step.  :math:`V_{0}` is held constant as the total cell volume (not the volume of solution including the neck) as only the cell, not the neck, is detected in the signal.

