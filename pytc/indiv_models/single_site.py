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
        shot_start: first shot to use in fit
        """

        self._S_cell = S_cell
        self._S_syringe = S_syringe

        self._T_cell = T_cell
        self._T_syringe = T_syringe

        self._cell_volume = cell_volume
        self._shot_volumes = np.array(shot_volumes)

        # Determinte the concentration of all of the species across the titration
        self._S_conc = self._titrate_species(self._S_cell,self._S_syringe)
        self._T_conc = self._titrate_species(self._T_cell,self._T_syringe)

    def initialize_param(self,K=1e6,dH=-4000,fx_competent=1.0,dilution_heat=0.0,dilution_intercept=0.0):
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
        b = S_conc_corr + self._T_conc + 1/self.param_values["K"]
        ST = (b - np.sqrt((b)**2 - 4*S_conc_corr*self._T_conc))/2

        self._mol_fx_st = ST/S_conc_corr

        # ---- Relate mole fractions to heat -----
        X = self.param_values["dH"]*(self._mol_fx_st[1:] - self._mol_fx_st[:-1])

        to_return = self._cell_volume*S_conc_corr[1:]*X + self.dilution_heats

        return to_return
