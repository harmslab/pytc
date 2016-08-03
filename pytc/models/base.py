__description__ = \
"""
base.py

Base class for other itc model description.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import inspect
import numpy as np

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


    # -------------------------------------------------------------------------
    # parameter names

    @property
    def param_names(self):
        """
        The parameters for the model.
        """

        try:
            return self._param_names
        except AttributeError:
            self._initialize_param_names()

        return self._param_names

    def _initialize_param_names(self):
        """
        Initialize the parameter names.
        """

        self._param_names = inspect.getargspec(self.initialize_param).args
        self._param_names.remove("self")
        self._param_names.sort()

    # -------------------------------------------------------------------------
    # parameter values

    @property
    def param_values(self):
        """
        Values for each parameter in the model.
        """

        try:
            return self._param_values
        except AttributeError:
            self._initialize_param_values()

        return self._param_values

    def _initialize_param_values(self):
        """
        Initialize parameter values.
        """

        self._param_values = {}
        for p in self.param_names:
            self._param_values[p] = self.param_guesses[p]

    def update_values(self,param_values):
        """
        Update parameter values for fit. param_values is a dictionary with
        with some number of parameter names.
        """

        try:
            tmp = self._param_values
        except AttributeError:
            self._initialize_param_values()

        for p in param_values.keys():
            self._param_values[p] = param_values[p]

    # -------------------------------------------------------------------------
    # parameter guesses

    @property
    def param_guesses(self):
        """
        Guesses for each parameter in the model.
        """

        try:
            return self._param_guesses
        except AttributeError:
            self._initialize_param_guesses()

        return self._param_guesses

    def _initialize_param_guesses(self):
        """
        Initialize parameter guesses.
        """

        a = inspect.getargspec(self.initialize_param)
        args = a.args
        args.remove("self")
        defaults = a.defaults
        self._param_guesses = dict(zip(args,defaults))

    def update_guesses(self,param_guesses):
        """
        Update parameter guesses for fit. param_guesses is a dictionary with
        with some number of parameter names.
        """

        try:
            tmp = self._param_guesses
        except AttributeError:
            self._initialize_param_guesses()

        for p in param_guesses.keys():
            self._param_guesses[p] = param_guesses[p]

    # -------------------------------------------------------------------------
    # fixed parameters

    @property
    def fixed_param(self):
        """
        Return the fixed parameters.
        """

        try:
            return self._fixed_param
        except AttributeError:
            self._initialize_fixed_param()

        return self._fixed_param

    def _initialize_fixed_param(self):
        """
        Initialize the fixed parameters.
        """

        self._fixed_param = {}


    def update_fixed(self,fixed_param):
        """
        Fix parameters.  fixed_param is a dictionary of parameters keyed to their
        fixed values.  If the value is None, the parameter is removed from the
        fixed parameters dictionary and will float.
        """

        try:
            self._fixed_param
        except AttributeError:
            self._initialize_fixed_param()

        for p in fixed_param.keys():
            if p == None:
                try:
                    self._fixed_param.pop(p)
                except KeyError:
                    pass
            else:
                self._fixed_param[p] = fixed_param[p]

    # -------------------------------------------------------------------------
    # parameter aliases

    @property
    def param_aliases(self):
        """
        Return parameter aliases.
        """

        try:
            return self._param_aliases
        except AttributeError:
            self._initialize_param_aliases()

        return self._param_aliases

    def _initialize_param_aliases(self):
        """
        Initialize the parameter aliases.
        """

        self._param_aliases = {}

    def update_aliases(self,param_alias):
        """
        Update parameter aliases.  param_alias is a dictionary of parameters keyed
        to their aliases (used by the global fit).  If the value is None, the parameter
        alias is removed.
        """

        try:
            tmp = self._param_aliases
        except AttributeError:
            self._initialize_param_aliases()

        for p in param_alias.keys():
            if param_alias[p] == None:
                try:
                    self._param_aliases.pop(p)
                except KeyError:
                    pass
            else:
                self._param_aliases[p] = param_alias[p]

    # -------------------------------------------------------------------------
    # parameter ranges

    @property
    def param_ranges(self):
        """
        Return parameter ranges.
        """

        try:
            return self._param_ranges
        except AttributeError:
            self._initialize_param_ranges()

        return self._param_ranges

    def _initialize_param_ranges(self):
        """
        Guess at parameter ranges.  Rather hacked at the moment.  Replace this
        function in a subclass if you want to have more sophisticated control
        of parameter ranges.
        """

        self._param_ranges = {}
        for p in self.param_names:
            if p.startswith("dH"):
                p_range = [-10000,10000]
            elif p.startswith("beta") or p.startswith("K"):
                p_range = [1,1e6]
            elif p == "fx_competent":
                p_range = [0.0,2.0]
            else:
                p_range = [-10000,10000]

            self._param_ranges[p] = p_range

    def update_ranges(self,param_ranges):
        """
        Update parameter ranges.  param_ranges is a dictionary of paramters
        keyed to two-entry lists/tuples or ranges.
        """

        try:
            tmp = self._param_ranges
        except AttributeError:
            self._initialize_param_ranges()

        for p in param_ranges.keys():
            if type(param_ranges[p]) in (list,tuple) and len(param_ranges[p]) == 2:
                self._param_ranges[p] = param_ranges[p]
                continue
            else:
                err = "parameter range {} is invalid for parameter {}. ".format(param_ranges[p],p)
                err += "Must be a tuple or list of length 2.\n"
                raise ValueError(err)
