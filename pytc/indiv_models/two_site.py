__description__ = \
"""
single_site.py

Model describing binding of a ligand to a single site.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import numpy as np

from .base import ITCModel

class SingleSite(ITCModel):
    """
    Binding at a single site.
    """

    def initialize_param(self,K1=1e6,K2=1e6,dH1=-4000,dH2=-4000,fx_competent=1.0,dilution_heat=0.0,dilution_intercept=0.0):
        """
        Initialize the fitting parameters.
        """

        self._initialize_param()

    @property
    def dQ(self):
        """
        Calculate the heats that would be observed across shots for a given set
        of enthalpies and binding constants for each reaction.
        """

        # ----- Determine mole fractions -----
        S_conc_corr = self._S_conc*self.param_values["fx_competent"]
        b = S_conc_corr + self._T_conc + 1/self.param_values["K1"]
        ST = (b - np.sqrt((b)**2 - 4*S_conc_corr*self._T_conc))/2
        self._mol_fx_st = ST/S_conc_corr

        # ---- Relate mole fractions to heat -----
        X1 = self.param_values["dH1"]*(self._mol_fx_st[1:] - self._mol_fx_st[:-1])

        # ----- Determine mole fractions -----
        S_conc_corr = self._S_conc*self.param_values["fx_competent"]
        b = S_conc_corr + self._T_conc + 1/self.param_values["K2"]
        ST = (b - np.sqrt((b)**2 - 4*S_conc_corr*self._T_conc))/2
        self._mol_fx_st = ST/S_conc_corr

        # ---- Relate mole fractions to heat -----
        X2 = self.param_values["dH2"]*(self._mol_fx_st[1:] - self._mol_fx_st[:-1])

        to_return = self._cell_volume*S_conc_corr[1:]*(X1 + X2) + self.dilution_heats

        return to_return
