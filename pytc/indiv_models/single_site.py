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

        mol_fx_st = ST/S_conc_corr

        # ---- Relate mole fractions to heat -----
        X = self.param_values["dH"]*(mol_fx_st[1:] - mol_fx_st[:-1])
   
        to_return = self._cell_volume*S_conc_corr[1:]*X + self.dilution_heats

        return to_return
