__description__ = \
"""
blank.py

Model describing a blank titration (e.g. titration into cell with without a
stationary species).
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import numpy as np
from .base import ITCModel

class Blank(ITCModel):
    """
    Blank titration in which no stationary species is present.  You can still
    specify a stationary species (for plotting purposes), but this is not
    required or actually used in the fitting.
    """

    def __init__(self,
                 S_cell=100e-6,S_syringe=0.0,
                 T_cell=0.0,   T_syringe=1000e-6,
                 cell_volume=300.0,
                 shot_volumes=[2.5 for i in range(30)]):

        """
        S_cell: stationary concentration in cell in M (this number does not
                actually go into the fit, but is useful for creating a
                mole_ratio to plot on same graph as a real titration).
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

    def initialize_param(self,dilution_heat=0.0,dilution_intercept=0.0):
        """
        Initialize the fitting parameters.
        """

        self._initialize_param()

    @property
    def dQ(self):
        """
        Calculate heat of dilution as a function of titrant concentration in
        the cell.
        """

        to_return = self.dilution_heats

        return to_return
