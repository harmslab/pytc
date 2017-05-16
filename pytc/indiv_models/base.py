__description__ = \
"""
base.py

Base class for other itc model description.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import inspect
import numpy as np
from .. import fit_param

class ITCModel:
    """
    Base class from which all ITC models should be sub-classed.
    """

    def __init__(self,
                 S_cell=100e-6,S_syringe=0.0,
                 T_cell=0.0,   T_syringe=1000e-6,
                 cell_volume=300.0,
                 shot_volumes=[2.5 for i in range(30)]):

        """
        S_cell: stationary concentration in cell in M
        S_syringe: stationary concentration in syringe in M
        T_cell: titrant concentration cell in M
        T_syringe: titrant concentration syringe in M
        cell_volume: cell volume, in uL
        shot_volumes: list of shot volumes, in uL.
        """

        self._S_cell = S_cell
        self._S_syringe = S_syringe

        self._T_cell = T_cell
        self._T_syringe = T_syringe

        self._cell_volume = cell_volume
        self._shot_volumes = np.array(shot_volumes)

        # Determine the concentration of all of the species across the titration
        self._S_conc = self._titrate_species(self._S_cell,self._S_syringe)
        self._T_conc = self._titrate_species(self._T_cell,self._T_syringe)

        self._initialize_param()

    def param_definition(self):
        pass

    @property
    def dQ(self):
        return np.array(())

    # --------------------------------------------------------------------------

    def _titrate_species(self,cell_conc,syringe_conc):
        """
        Determine the concentrations of stationary and titrant species in the
        cell given a set of titration shots and initial concentrations of both
        the stationary and titrant species.

        Does two independent calculations and adds them.  First, it calculates
        the concentration change due to injection (injected).  It then treats
        the dilution of the stuff initially in hte cell (diluted).  The sum of
        these two groups is the total concentration of whatever was titrated.
        The shot_ratio_product method is described on p. 134 of Freire et al.
        (2009) Meth Enzymology 455:127-155
        """

        volume = np.zeros(len(self._shot_volumes)+1)
        out_conc = np.zeros(len(self._shot_volumes)+1)

        volume[0] = self._cell_volume
        out_conc[0] = cell_conc

        shot_ratio = (1 - self._shot_volumes/self._cell_volume)
        for i in range(len(self._shot_volumes)):

            shot_ratio_prod = np.prod(shot_ratio[:(i+1)])
            injected = syringe_conc*(1 - shot_ratio_prod)
            diluted = cell_conc*shot_ratio_prod

            out_conc[i+1] = injected + diluted

        return out_conc

    @property
    def mole_ratio(self):
        """
        Molar ratio of titrant to stationary species.  If not yet initialized,
        send return empty array.
        """

        try:
            return self._T_conc[1:]/self._S_conc[1:]
        except AttributeError:
            return np.array([],dtype=float)

    @property
    def dilution_heats(self):
        """
        Return the heat of dilution.
        """

        return self._T_conc[1:]*self.param_values["dilution_heat"] + self.param_values["dilution_intercept"]

    def _initialize_param(self,param_names=None,param_guesses=None):
        """
        Initialize the parameters.  
        """

        self._params = {}

        if param_names == None:
            param_names = []
        if param_guesses == None:
            param_guesses = []

        # Grab parameter names and guesses from the self.param_definition function
        a = inspect.getargspec(self.param_definition)

        if type(a.args) != None:

            args = list(a.args)
            try:
                args.remove("self")
            except ValueError:
                pass

        if len(args) != 0:
                
            if len(args) != len(a.defaults):
                err = "all parameters in self.param_definition must have a default value.\n"
                raise ValueError(err)

            param_names.extend(args)
            param_guesses.extend(list(a.defaults))

        # Add dilution parameters
        param_names.extend(["dilution_heat","dilution_intercept"])
        param_guesses.extend([0.0,0.0])

        for i, p in enumerate(param_names):
            self._params[p] = fit_param.FitParameter(p,guess=param_guesses[i])

        self._param_names = param_names[:]
        self._param_names.sort()


    # -------------------------------------------------------------------------
    # parameter names

    @property
    def param_names(self):
        """
        The parameters for the model.
        """

        return self._param_names

    # -------------------------------------------------------------------------
    # parameter objects

    @property
    def parameters(self):
        """
        Return FitParam objects associated with the model.
        """

        return self._params

    # -------------------------------------------------------------------------
    # parameter values

    @property
    def param_values(self):
        """
        Values for each parameter in the model.
        """

        return dict([(p,self._params[p].value) for p in self._param_names])  
 

    def update_values(self,param_values):
        """
        Update parameter values for fit. param_values is a dictionary with
        with some number of parameter names.
        """

        for p in param_values.keys():
            self._params[p].value = param_values[p]

    # -------------------------------------------------------------------------
    # parameter stdev

    @property
    def param_stdevs(self):
        """
        Standard deviation for each parameter in the model.
        """

        return dict([(p,self._params[p].stdev) for p in self._param_names])  
 

    def update_stdevs(self,param_stdevs):
        """
        Update parameter stdev for fit. param_stdevs is a dictionary with
        with some number of parameter names.
        """

        for p in param_stdevs.keys():
            self._params[p].stdev = param_stdevs[p]

    # -------------------------------------------------------------------------
    # parameter ninetyfive

    @property
    def param_ninetyfives(self):
        """
        95% confidence intervals for each parameter in the model.
        """

        return dict([(p,self._params[p].ninetyfive) for p in self._param_names])  
 

    def update_ninetyfives(self,param_ninetyfives):
        """
        Update parameter 95% for fit. param_ninetyfives is a dictionary with
        with some number of parameter names.
        """

        for p in param_ninetyfives.keys():
            self._params[p].ninetyfive = param_ninetyfives[p]

    # -------------------------------------------------------------------------
    # parameter guesses

    @property
    def param_guesses(self):
        """
        Guesses for each parameter in the model.
        """

        return dict([(p,self._params[p].guess) for p in self._param_names])  

    def update_guesses(self,param_guesses):
        """
        Update parameter guesses for fit. param_guesses is a dictionary with
        with some number of parameter names.
        """

        for p in param_guesses.keys():
            self._params[p].guess = param_guesses[p]

    # -------------------------------------------------------------------------
    # parameter ranges

    @property
    def param_guess_ranges(self):
        """
        Return parameter ranges.
        """

        return dict([(p,self._params[p].guess_range) for p in self._param_names])  

    def update_guess_ranges(self,param_ranges):
        """
        Update parameter ranges.  param_ranges is a dictionary of paramters
        keyed to two-entry lists/tuples or ranges.
        """

        for p in param_ranges.keys():
            self._params[p].guess_range = param_ranges[p]


    # -------------------------------------------------------------------------
    # fixed parameters

    @property
    def fixed_param(self):
        """
        Return the fixed parameters.
        """

        return dict([(p,self._params[p].fixed) for p in self._param_names])  

    def update_fixed(self,fixed_param):
        """
        Fix parameters.  fixed_param is a dictionary of parameters keyed to their
        fixed values.  If the value is None, the parameter is removed from the
        fixed parameters dictionary and will float.
        """

        for p in fixed_param.keys():
        
            if fixed_param[p] == None:
                self._params[p].fixed = False
            else:
                self._params[p].fixed = True
                self._params[p].value = fixed_param[p]


    # -------------------------------------------------------------------------
    # parameter bounds

    @property
    def bounds(self):
        """
        Return parameter bounds.
        """

        return dict([(p,self._params[p].bounds) for p in self._param_names])  

    def update_bounds(self,bounds):
        """
        Update parameter bounds.  bounds is a dictionary of paramters
        keyed to two-entry lists/tuples or ranges.
        """

        for p in bounds.keys():
            self._params[p].bounds = bounds[p]

    # -------------------------------------------------------------------------
    # parameter aliases

    @property
    def param_aliases(self):
        """
        Return parameter aliases.
        """

        return dict([(p,self._params[p].alias) for p in self._param_names
                     if self._params[p].alias != None])  

    def update_aliases(self,param_alias):
        """
        Update parameter aliases.  param_alias is a dictionary of parameters keyed
        to their aliases (used by the global fit).  If the value is None, the parameter
        alias is removed.
        """

        for p in param_alias.keys():
            self._params[p].alias = param_alias[p]
