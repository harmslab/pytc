__description__ = \
"""
base.py

Base class for other itc model description.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import inspect
import numpy as np
from . import fit_param

class ITCModel:
    """
    Base class from which all ITC models should be sub-classed.
    """

    # --------------------------------------------------------------------------
    # These three methods need to be defined for each subclass.

    def __init__(self):
        pass

    def initialize_param(self):
        pass

    @property
    def dQ(self):
        return None

    # --------------------------------------------------------------------------

    def _titrate_species(self,cell_conc,syringe_conc):
        """
        Determine the concentrations of stationary and titrant species in the
        cell given a set of titration shots and initial concentrations of both
        the stationary and titrant species.
        """

        volume = np.zeros(len(self._shot_volumes)+1)
        out_conc = np.zeros(len(self._shot_volumes)+1)

        volume[0] = self._cell_volume
        out_conc[0] = cell_conc

        for i in range(len(self._shot_volumes)):

            volume[i+1] = volume[i] + self._shot_volumes[i]
            dilution = volume[i]/volume[i+1]
            added = self._shot_volumes[i]/volume[i+1]

            out_conc[i+1] = out_conc[i]*dilution + syringe_conc*added

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
        Initialize the parameters.  If param_names is None, the parameter
        names and guesses are determined by inspection of self.initialize_param.
        """

        self._params = {}
        if param_names == None:

            # If parameter names are not specified, grab them from
            # self.initialize_param defaults
            a = inspect.getargspec(self.initialize_param)
            param_names = a.args
            param_names.remove("self")
            param_guesses = a.defaults

        for i, p in enumerate(param_names):
            if param_guesses != None:
                self._params[p] = fit_param.FitParameter(p,guess=param_guesses[i])
            else:
                self._params[p] = fit_param.FitParameter(p)

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
