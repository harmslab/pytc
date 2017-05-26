__description__ = \
"""
models.py

Models subclassed from ITCModel used to model (and fit) ITC data.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import inspect
import numpy as np
import scipy.optimize
from .base import ITCModel

from . import bp_ext

class BindingPolynomial(ITCModel):
    """
    Base class for a binding polynomial fit.
    """

    def param_definition(fx_competent=1.0): 
        """
        Define fraction competent.  The binding polynomial parameters are built
        on the fly using the ._initialize_parameters below.
        """
        
        pass
    
    def __init__(self,
                 num_sites=1,
                 S_cell=100e-6,S_syringe=0.0,
                 T_cell=0.0,   T_syringe=1000e-6,
                 cell_volume=300.0,
                 shot_volumes=[2.5 for i in range(30)]):

        """
        num_sites: number of sites in the binding polynomial
        S_cell: stationary concentration in cell in M
        S_syringe: stationary concentration in syringe in M
        T_cell: titrant concentration cell in M
        T_syringe: titrant concentration syringe in M
        cell_volume: cell volume, in uL
        shot_volumes: list of shot volumes, in uL.
        """

        self._num_sites = num_sites
        super().__init__(S_cell,S_syringe,T_cell,T_syringe,cell_volume,shot_volumes)

    def _initialize_param(self):
        """
        Populate the names of the arguments for this number of sites and guesses
        for each parameter in the model.
        """

        # Build polynomial parameters, depending on the number of sites in the model
        param_names = ["beta{}".format(i) for i in range(1,self._num_sites + 1)]
        param_guesses = [1e6 for i in range(self._num_sites)]
        param_names.extend(["dH{}".format(i) for i in range(1,self._num_sites + 1)])
        param_guesses.extend([-4000.0 for i in range(self._num_sites)])

        # Initialize parameters
        super()._initialize_param(param_names,param_guesses)

        # Populate fitting parameter arrays
        self._fit_beta_array = np.zeros(self._num_sites,dtype=float)
        self._fit_dH_array   = np.zeros(self._num_sites,dtype=float)
        self._fit_beta_list  = ["beta{}".format(i+1) for i in range(self._num_sites)]
        self._fit_dH_list    = ["dH{}".format(i+1) for i in range(self._num_sites)]

        self._T_conc_free = np.zeros(len(self._S_conc),dtype=float)

    @property
    def dQ(self):
        """
        Calculate the heats that would be observed across shots for a given set
        of enthalpies and binding constants for each reaction.  This will work
        for an arbitrary-order binding polynomial.
        """

        # Populate fitting parameter arrays
        for i in range(self._num_sites):
            self._fit_beta_array[i] = self.param_values[self._fit_beta_list[i]]
            self._fit_dH_array[i] = self.param_values[self._fit_dH_list[i]]

        S_conc_corr = self._S_conc*self.param_values["fx_competent"]
        num_shots = len(S_conc_corr)
        size_T = self._T_conc.size

        final_array = np.zeros((num_shots-1),dtype=float)

        bp_ext.dQ(self._cell_volume, num_shots, size_T, self._num_sites, self.dilution_heats, 
            self._fit_beta_array, self._fit_dH_array, S_conc_corr, self._T_conc, self._T_conc_free, 
            final_array)

        return final_array
