:orphan:

========================================
Fitting Models to Individual Experiments
========================================

Basic model pipeline
====================
Under the hood, models of individual experiments do the following:

1. Guess model parameters.
2. Calculate the concentrations of all molecular species using guessed binding
   constants (as well as the titration shot sizes and initial concentrations
   in the cell and syringe).
3. Calculate the heat change per shot using the guess reaction enthalpies and
   species concentrations from (2).
4. Compare the calculated and measured heat changes at each shot.
5. Iterate through steps 2-4 using nonlinear regression to find parameter estimates.

Implemented Models
==================

+ `Blank <indiv_models/blank.html>`_
+ `Single site <indiv_models/single-site.html>`_
+ `Competitive ligand binding <indiv_models/competitive.html>`_
+ `Binding polynomial <indiv_models/binding-polynomial.html>`_
+ `Assembly autoinhibition <indiv_models/assembly-auto-inhibition.html>`_

Example Fit
===========

.. code:: python

    import pytc

    # Create fitter
    g = pytc.GlobalFit()

    # Load experiments
    a = pytc.ITCExperiment("demos/ca-edta/hepes-01.DH",pytc.indiv_models.SingleSite,shot_start=2)
    g.add_experiment(a)

    # Fit and show results
    g.fit()
    print(g.fit_as_csv)

Differences from other modeling approaches
==========================================

**pytc** is implemented with the philosophy that one should model all processes
in the ITC experiment and include them in the fit.  These processes include not only
the binding reaction of interest, but also systematic errors in sample preparation
and heat arising from dilution.  The latter effects are captured with nuisance
parameters added to standard thermodynamic models of binding:

.. math::
    Q_{i,obs} = Q_{i}\alpha + D_{slope}[T]_{total} + D_{interecept} + \varepsilon

where :math:`Q_{i,obs}` is the heat at injection :math:`i` and :math:`Q_{i}` is the
heat at injection :math:`i` arising from the reaction of interest.  :math:`Q_{i,obs}`
differs from :math:`Q_{i}` because of systematic concentration errors (:math:`\alpha`)
and the heat arising from dilution (:math:`D_{slope}` and :math:`D_{intercept}`).
:math:`\varepsilon` is the fit residual.

:math:`\alpha` scales all heats, accounting for systematic errors in the relative
protein or ligand concentration. This could also be viewed as an apparent
stoichiometry but, following `Freire et al. <https://www.sciencedirect.com/science/article/pii/S0076687908042055>`_,
we interpret this as "the effective amount of active protein relative to the nominal
value entered as protein concentration."  This term is referred to as the
:code:`fx_competent` (fraction competent) in **pytc** output. Practically, this
value should be near 1.0. Large deviations from 1.0 may indicate that the model
used does not describe the stoichiometry of the protein or that there is a
problem with the experiment.

The other nuisance parameters, :math:`D_{slope}` and :math:`D_{intercept}`, model
the heat of dilution as a linear function of titrant concentration.  This is
equivalent to fitting a straight line through a blank titration and then subtracting
that line from an experimental titration.  Rather than subtracting a blank, **pytc**
allows a user to incorporate a blank titration into the global fit: the user
fits the same :math:`D_{slope}`` and :math:`D_{intercept}` across both an
experimental and blank titration, thus explicitly modeling the heat of dilution.

If a one sets the values of :math:`\alpha` to 1.0, :math:`D_{slope}` to 0.0, and
:math:`D_{intercept}` to 0.0, and then does not allow them to vary during the
fit, one recovers only the thermodynamic model---as is done in software such as
Origin.
