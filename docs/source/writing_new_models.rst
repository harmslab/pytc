======================
Writing New ITC Models
======================

Individual models
=================

These models describe a single ITC experiment.  They are passed to 
:code:`pytc.ITCExperiment` along with an appropriate ITC heats file to analyze that
individual experiment.

To define a new fitting model, you create a new subcass of 
:code:`pytc.indiv_models.ITCModel`.  Here is an implementation of a single-site
binding model. 

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
   using :code:`self.param_values[PARAMETER_NAME]`.  The actual model
   implemented is `Single Site <indiv_models.html#single_site>`_. 

The requirements for one of these models are straightforward:
 + Be subclasses of :code:`pytc.indiv_models.ITCModel`
 + Define a :code:`param_definition` method with all fittable parameters as
   arguments.  Each paramter should have a default value that is a reasonable
   guess for that parameters. 
 + Expose a :code:`dQ` property that gives the heat change per shot.

Other useful xx:
 + To pass other information to the model that is not present in a .DH file,
   define a new :code:`__init__` function that has new arguments.  These can
   then be dealt with, followed by calling :code:`super().__init__(...)`
   where :code:`...` are the normal arguments to :code:`ITCModel.__init__`.
   See `pytc\/indiv_models\/single_site_competitor.py <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/single_site_competitor.py>`_ as an example.
 + To keep track of the concentration of something else in the cell besides a single
   titrant and stationary species, define a new :code:`__init__` function that 
   titrates this species.  See the :code:`__init__` function defined for 
   `pytc\/indiv_models\/single_site_competitor.py <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/single_site_competitor.py>`_ as an example.
 + To construct a model with a variable number of parameters--say, a binding
   polynomial with :math:`N` sites--redefine :code:`_initialize_params`.  See
   the :code:`_initialize_params` method defined for
   `pytc\/indiv_models\/binding_polynomial.py <https://github.com/harmslab/pytc/blob/master/pytc/indiv_models/binding_polynomial.py>`_ as an example.  

See the `here <indiv_models.html>`_ for descriptions of the currently-implemented models.

Global models
=============

Simple global parameters
------------------------

The first (and simplest) sort of global fit is to declare that parameters
from separate experiments should use the same, shared, fitting parameter.  The
following code takes two experimental replicates and fits them to a single
:math:`K` and :math:`\Delta H`.  The code that actually does the linking is
highlighted with :code:`***`

.. sourcecode:: python

    import pytc

    # Create fitter
    g = pytc.GlobalFit()

    # Load experiments
    a = pytc.ITCExperiment("demos/ca-edta/hepes-01.DH",pytc.indiv_models.SingleSite,shot_start=2)
    g.add_experiment(a)

    b = pytc.ITCExperiment("demos/ca-edta/hepes-02.DH",pytc.indiv_models.SingleSite,shot_start=2)
    g.add_experiment(b)

    # **********************************
    # Link global fitting parameters
    g.link_to_global(a,"K","global_K")
    g.link_to_global(b,"K","global_K")

    g.link_to_global(a,"dH","global_dH")
    g.link_to_global(b,"dH","global_dH")
    # **********************************
     
    # Fit and show results
    g.fit()
    print(g.fit_as_csv)

The new global parameters are simply assigned a name (:code:`global_K` and 
:code:`global_dH`) that are individually fit.  The fitter takes care of the
rest. The output of this fit will look like the following.  The 
global parameters appear as :code:`global_K` and :code:`global_dH`.

| # Fit successful? True
| # Fit sum of square residuals: 0.634237669456395
| # Fit num param: 8
| # Fit num observations: 108
| # Fit num degrees freedom: 100
| type,name,dh_file,value,uncertainty,fixed,guess,lower_bound,upper_bound
| global,global_K,NA,3.84168e+07,1.40582e-06,float,1.00000e+06,-inf,inf
| global,global_dH,NA,-4.64104e+03,7.96280e-03,float,-4.00000e+03,-inf,inf
| ...


Global parameter functions
--------------------------

What about more complex relationships between experiments?  What if the parameter
will not be the same across experiments, but will instead depend on some property
of the experiment?

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

pytc encodes such a relationship using subclasses of :code:`GlobalConnector`.
We will illustrate this by implementing the relationship between buffer 
ionization enthalpy and observed enthalpy from above.  

Define the :code:`GlobalConnector` object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, we'll define :code:`NumProtons`, the subclass of :code:`GlobalConnector`
that encodes the relationship.

.. sourcecode:: python

    import pytc
    from pytc import global_models

    class NumProtons(global_models.GlobalConnector):
   
        param_guesses = {"dH_intrinsic":0.1,"num_H",0.1}
 
        def dH(self,experiment):

            return self.dH_intrinsic + self.num_H*experiment.ionization_enthalpy

The new class does two things. 
 + It defines an attribute called :code:`param_guesses` that defines the fittable
   parameters and reasonable guesses for those parameters.
 + It defines a method called :code:`dH` which spits out the enthalpy for a given
   :code:`experiment`.  Notice that :code:`dH` uses both parameters defined in 
   :code:`param_guesses`: :code:`self.dH_intrinsic` and :code:`self.num_H`.  It 
   gets the ionization enthalpy for a given experiment from the :code:`experiment`
   object it takes as an argument.

The general requirements for these `GlobalConnector` requirements are
straightforward:

 + It must be a subclass of :code:`GlobalConnector`.
 + It must define :code:`param_guesses` in the class namespace (i.e. at the 
   top of the class definition.)  This should have reasonable guesses for the
   parameters.
 + It must define output methods (like :code:`dH`) that: 
     + take only :code:`self` and :code:`experiment` as arguments.
     + use the parameters specified in :code:`param_guesses` as attributes of
       :code:`self` (e.g. :code:`self.dH_intrinsic` above).
     + access any required information about the experiment from the 
       :code:`experiment` object.
 + There is no limit to the number of parameters or output methods.  


Link fit parameters to the object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:code:`GlobalConnector` objects can then be linked to invididual experiment
model parameters in a way directly analagous to the simple global fit
parameters from above.  As before, we'll show an example and then describe it.  

.. sourcecode:: python
   
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

The lines containing `np_num_H` and `np_dH_intrinsic` are the outputs from the 
new global fit. 

There are three key things in this code:

 + **It creates an instance of :code:`NumProtons`.**  This takes a required argument
   called :name:`name` that is used to identify which :code:`GlobalConnector`
   each parameter is associated with. In this case, :code:`name="np"`, so the 
   string :code:`"np_"` is appended to the parameters when they are output.  
 + **It assigns :code:`.ionization_enthalpy` to each experiment.**  This is how
   :code:`experiment.ionization_enthalpy` is accessed in the :code:`NumProtons.dH`
   function.  If you were implementing a different model, you could send different
   properties here (pH, competitor concentration, etc.).  NOTE: 
   :code:`experiment.temperature` is already defined and does not need to be set
   manually. 
 + **It links the :code:`"dH"` parameter from each experiment to 
   :code:`num_protons.dH`.**  The linking uses the *name* of the output function,
   but does not call it (e.g. it is :code:`num_protons.dH` **NOT** 
   :code:`num_protons.dH()`)

See the `here <global_mdels.html>`_ for descriptions of the currently-implemented models.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   _api/pytc.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
