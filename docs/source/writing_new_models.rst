======================
Writing New ITC Models
======================

There are two types of models in *pytc*: individual models and global models. 
Individual models describe a single ITC experiment under a single set of 
conditions.  Global models describe relationships between individual ITC 
experiments. Individual models and global models are both appended to 
instances of :code:`pytc.GlobalFit`, which then simultaneously fits parameters
from all models. 

See the `here <indiv_models.html>`_ for descriptions of the individual models
already implemented. See `here <global_models.html`>_ for the global models
already implemented.

The following sections describe how to write new individual and global models.

Individual models
=================

These models describe a single ITC experiment.  They are passed to 
:code:`pytc.ITCExperiment` along with an appropriate ITC heats file to analyze that
individual experiment.

To define a new fitting model, create a new subcass of
:code:`pytc.indiv_models.ITCModel`.  Here is an implementation of a single-site
binding model. A full description of the model is
`here <indiv_models.html#single_site>`_. 

.. sourcecode:: python

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

The new class does two things. 
 + It defines a method called :code:`param_defintion` that defines the
   fittable parameters and reasonable guesses for those parameters as arguments
   to the method.
 + It defines a property called :code:`dQ` which spits out the heat change for 
   for each shot. It access the parameters defined in :code:`param_definition`
   using :code:`self.param_values[PARAMETER_NAME]`.  

The requirements for an individul model are:
 + It is a subclass of :code:`pytc.indiv_models.ITCModel`
 + It defines a :code:`param_definition` method with all fittable parameters as
   arguments.  Each paramter should have a default value that is a reasonable
   guess for that parameter. 
 + Expose a :code:`dQ` property that gives the heat change per shot.

More complex models might require a few additional pieces.  
 + To pass information to the model that is not present in a .DH file,
   define a new :code:`__init__` function that has new arguments.  For example,
   one might define an :code:`__init__` function that takes the pH of the 
   solution.  After this information is recorded by the new :code:`__init__`
   function, it should then call :code:`super().__init__(...)`, where
   :code:`...` contains the normal arguments to :code:`ITCModel.__init__`.
   See `pytc\/indiv_models\/single_site_competitor.py <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/single_site_competitor.py>`_ as an example.
 + To keep track of the concentration of something else in the cell besides theax
   titrant and stationary species, define a new :code:`__init__` function that 
   titrates this species.  See the :code:`__init__` function defined for 
   `pytc\/indiv_models\/single_site_competitor.py <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/single_site_competitor.py>`_ as an example.
 + To construct a model with a variable number of parameters--say, a binding
   polynomial with :math:`N` sites--redefine :code:`_initialize_params`.  See
   the :code:`_initialize_params` method defined for
   `pytc\/indiv_models\/binding_polynomial.py <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/binding_polynomial.py>`_ as an example.  


Global models
=============

Global models describe how binding thermodynamics should change between
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

One can encode thisrelationship using a subclasse of
:code:`pytc.global_models.GlobalConnector`.  We will illustrate this by
implementing the relationship between buffer ionization enthalpy and observed
enthalpy from above.  

Define the :code:`GlobalConnector` object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, we'll define :code:`NumProtons`, the subclass of :code:`GlobalConnector`
that encodes the relationship.

.. sourcecode:: python

    import pytc
    from pytc import global_models

    class NumProtons(global_models.GlobalConnector):
   
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


Link fit parameters to the object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Once the :code:`GlobalConnector` object is defined, it can then be linked to 
individual experimental model parameters in a way directly analagous to simple
global fit parameters.  As before, we'll show an example and then describe it.  

.. sourcecode:: python

    # --------------------------------------------------------------------
    # define buffer ionization enthalpies.
    # goldberg et al (2002) Journal of Physical and Chemical Reference Data 31 231,  doi: 10.1063/1.1416902
    TRIS_IONIZATION_DH = 47.45/4.184*1000
    IMID_IONIZATION_DH = 36.64/4.184*1000 
   
    # --------------------------------------------------------------------
    # Create a global fitting instance
    g = pytc.GlobalFit()

    # ----------------------------------------------------
    # Create an instance of the connector we defined above
    num_protons = NumProtons("np")

    # ------------------------------------------------------------------------------------
    # Load in an experiment done in tris buffer experiment
    tris = pytc.ITCExperiment("demos/ca-edta/tris-01.DH",pytc.indiv_models.SingleSite,shot_start=2)

    # Assign ionization enthalpy of experiment
    tris.ionization_enthalpy = TRIS_IONIZATION_DH

    # Add the experiment to the fitter
    g.add_experiment(tris)

    # Assign the local variable "dH" to the global connector method
    g.link_to_global(tris,"dH",num_protons.dH) 

    # ------------------------------------------------------------------------------------
    # Imidazole buffer experiment
    imid = pytc.ITCExperiment("demos/ca-edta/imid-01.DH",pytc.indiv_models.SingleSite,shot_start=2)

    # Assign ionization enthalpy of experiment
    imid.ionization_enthalpy = IMID_IONIZATION_DH

    # Add the experiment to the fitter
    g.add_experiment(imid)

    # Assign the local variable "dH" to the global connector method
    g.link_to_global(imid,"dH",num_protons.dH)

    # --------------------------------------------------------------------
    # Do a global fit and show results
    g.fit()
    print(g.fit_as_csv)

This will spit out:

|   # Fit successful? True
|   # Fit sum of square residuals: 1.1482376047181797
|   # Fit num param: 10
|   # Fit num observations: 108
|   # Fit num degrees freedom: 98
|   type,name,dh_file,value,uncertainty,fixed,guess,lower_bound,upper_bound
|   global,np_num_H,NA,-9.79065e-01,1.15256e+00,float,1.00000e-01,-inf,inf
|   global,np_dH_intrinsic,NA,-4.63537e+02,1.08227e-02,float,0.00000e+00,-inf,inf
|   ...

The lines containing :code:`np_num_H` and :code:`np_dH_intrinsic` are the
outputs from the new global fit. 

There are three key things in this code:
 + It creates an instance of :code:`NumProtons`.  This takes a required argument
   called :code:`name` that is used to identify which :code:`GlobalConnector`
   each parameter is associated with. In this case, :code:`name="np"`, so the 
   string :code:`"np_"` is appended to the parameters when they are output.  
 + It assigns :code:`.ionization_enthalpy` to each experiment.  This is how
   :code:`experiment.ionization_enthalpy` is accessed in the :code:`NumProtons.dH`
   function.  If you were implementing a different model, you could send different
   properties here (pH, competitor concentration, etc.).  NOTE: 
   :code:`experiment.temperature` is already defined and does not need to be set
   manually. 
 + It links the :code:`"dH"` parameter from each experiment to 
   :code:`num_protons.dH`.  The linking uses the *name* of the output function,
   but does not call it (e.g. it is :code:`num_protons.dH` **NOT** 
   :code:`num_protons.dH()`)

More complex models might require a few additional pieces.  
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
