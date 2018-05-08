:orphan:

======================
Writing New ITC Models
======================

There are two types of models in **pytc**: individual models and global connectors.
Individual models describe a single ITC experiment under a single set of
conditions.  Global connectors describe relationships between individual ITC
experiments. Individual models and global connectors are both appended to
instances of :code:`pytc.GlobalFit`, which then simultaneously fits parameters
from all models.  See the `individual models <indiv_models.html>`_ and
`global connectors <global_models.html>`_ pages for more details.

The following sections describe how to write new individual models and global
connectors.

Individual models
=================

These models describe a single ITC experiment.  They are passed to
:code:`pytc.ITCExperiment` along with an appropriate ITC heats file to analyze that
individual experiment.

To define a new fitting model, create a new subcass of
:code:`pytc.indiv_models.ITCModel`.  Here is an implementation of a
`single-site binding model <indiv_models/single-site.html>`_

.. code:: python

    import pytc

    class SingleSite(pytc.indiv_models.ITCModel):

        def param_definition(K=1e6,dH=-4000.0,fx_competent=1.0):
            pass

        @property
        def dQ(self):
            """
            Calculate the heats that would be observed across shots for a given set
            of enthalpies and binding constants for each reaction.
            """

            # ----- Determine mole fractions -----
            S_conc_corr = self._S_conc*self.param_values["fx_competent"]
            b = S_conc_corr + self._T_conc + 1/self.param_values["K"]
            ST = (b - np.sqrt((b)**2 - 4*S_conc_corr*self._T_conc))/2

            mol_fraction = ST/S_conc_corr

            # ---- Relate mole fractions to heat -----
            X = self.param_values["dH"]*(mol_fraction[1:] - mol_fraction[:-1])

            return self._cell_volume*S_conc_corr[1:]*X + self.dilution_heats

The new class does two things:
 + It defines a method called :code:`param_defintion` that defines the
   fittable parameters and reasonable guesses for those parameters as arguments
   to the method.
 + It defines a property called :code:`dQ` which spits out the heat change for
   for each shot. It access the parameters defined in :code:`param_definition`
   using :code:`self.param_values[PARAMETER_NAME]`.

The requirements for an individual model are:
 + It is a subclass of :code:`pytc.indiv_models.ITCModel`
 + It defines a :code:`param_definition` method with all fittable parameters as
   arguments.  Each paramter should have a default value that is a reasonable
   guess for that parameter.
 + Expose a :code:`dQ` property that gives the heat change per shot.

More complex models might require a few additional pieces of code:
 + To pass information to the model that is not present in a .DH file,
   define a new :code:`__init__` function that has new arguments.  For example,
   one might define an :code:`__init__` function that takes the pH of the
   solution.  After this information is recorded by the new :code:`__init__`
   function, it should then call :code:`super().__init__(...)`, where
   :code:`...` contains the normal arguments to :code:`ITCModel.__init__`.
   See `pytc\/indiv_models\/single_site_competitor.py <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/single_site_competitor.py>`_ as an example.
 + To keep track of the concentration of something else in the cell besides the
   titrant and stationary species, define a new :code:`__init__` function that
   titrates this species.  See the :code:`__init__` function defined for
   `pytc\/indiv_models\/single_site_competitor.py <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/single_site_competitor.py>`_ as an example.
 + To construct a model with a variable number of parameters--say, a binding
   polynomial with :math:`N` sites--redefine :code:`_initialize_params`.  See
   the :code:`_initialize_params` method defined for
   `pytc\/indiv_models\/binding_polynomial.py <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/binding_polynomial.py>`_ as an example.


Global connectors
=================

Global connectors describe how binding thermodynamics should change between
experiments.

A good example of this is a binding reaction that involves the gain or loss of
a proton.  The measured enthalpy will have a binding component and an ionization
component.  These can be separated by performing ITC experiments using buffers
with different ionization enthalpies. Mathematically, the observed enthalpy in
a buffer is:

.. math::
    \Delta H_{obs,buffer} = \Delta H_{intrinsic} + \Delta H_{ionization,buffer} \times n_{proton},

where :math:`\Delta H_{intrinsic}` is the buffer-independent binding enthalpy,
:math:`\Delta H_{ionization,buffer}` is the buffer ionization enthalpy, and
:math:`n_{proton}` is the number of protons gained or lost.

One can encode this relationship using a subclass of
:code:`pytc.global_models.GlobalConnector`.  We will illustrate this by
implementing the relationship between buffer ionization enthalpy and observed enthalpy.

.. code:: python

    import pytc

    class NumProtons(pytc.global_models.GlobalConnector):

        param_guesses = {"dH_intrinsic":0.1,"num_H",0.1}
        required_data = ["ionization_enthalpy"]

        def dH(self,experiment):

            return self.dH_intrinsic + self.num_H*experiment.ionization_enthalpy

The new class does three things.
 + It defines an attribute called :code:`param_guesses` that defines the fittable
   parameters and reasonable guesses for those parameters.
 + It defines an attribute called :code:`required_data` that defines attributes
   of :code:`experiment` that must be set for the connector to work.
 + It defines a method called :code:`dH` which spits out the enthalpy for a given
   :code:`experiment`.  Notice that :code:`dH` uses both parameters defined in
   :code:`param_guesses`: :code:`self.dH_intrinsic` and :code:`self.num_H`.  It
   gets the ionization enthalpy for a given experiment from the :code:`experiment`
   object it takes as an argument.

The general requirements for these :code:`GlobalConnector` requirements are:
 + It must be a subclass of :code:`pytc.global_models.GlobalConnector`.
 + It must define :code:`param_guesses` in the class namespace (i.e. at the
   top of the class definition.)  This should have reasonable guesses for the
   parameters.
 + It must define :code:`required_data` in the class namespace (i.e. at the
   top of the class definition.)  These are strings that name the attributes of
   :code:`experiment` that are required to do the calculation.
 + It must define output methods (like :code:`dH`) that:
     + take only :code:`self` and :code:`experiment` as arguments.
     + use the parameters specified in :code:`param_guesses` as attributes of
       :code:`self` (e.g. :code:`self.dH_intrinsic` above).
     + access any required information about the experiment from the
       :code:`experiment` object.
 + There is no limit to the number of parameters, required data, or output
   methods.

More complex models might require a few additional pieces of code:
 + To pass information to the model that does not vary across experiments,
   define a new :code:`__init__` function that has new arguments.  For example,
   one might define an :code:`__init__` function that takes the reference
   temperature for an analysis. After this information is recorded by the new
   :code:`__init__` function, it should then call :code:`super().__init__(name)`.
   See `pytc.global_connectors.VantHoff <https://github.com/harmslab/pytc/blob/master/pytc/global_connectors/vant_hoff.py>`_ as an example.
 + Models can implement multiple output functions.  For example
   `pytc.global_connectors.VantHoff <https://github.com/harmslab/pytc/blob/master/pytc/global_connectors/vant_hoff.py>`_
   has both a :code:`dH` and :code:`K` output function.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   _api/pytc.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
