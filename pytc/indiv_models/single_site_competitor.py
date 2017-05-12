__description__ = \
"""
single_site.py

Model describing competition between two ligands for a single site.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import numpy as np
from .base import ITCModel

class SingleSiteCompetitor(ITCModel):
    """
    Competition between two ligands for the same site.  Model taken from:

    Sigurskjold BW (2000) Analytical Biochemistry 277(2):260-266
    doi:10.1006/abio.1999.4402
    http://www.sciencedirect.com/science/article/pii/S0003269799944020
    """
 
    def param_definition(K=1e6,Kcompetitor=1e6,
                         dH=-4000,dHcompetitor=-4000,
                         fx_competent=1.0):
        pass

    def __init__(self,
                 S_cell=100e-6,S_syringe=0.0,
                 T_cell=0.0,   T_syringe=1000e-6,
                 C_cell=200e-6,C_syringe=0.0,
                 cell_volume=300.0,
                 shot_volumes=[2.5 for i in range(30)]):

        """
        S_cell: stationary concentration in cell in M
        S_syringe: stationary concentration in syringe in M
        T_cell: titrant concentration cell in M
        T_syringe: titrant concentration syringe in M
        C_cell: competitor concentration cell in M
        C_syringe: competitor concentration syringe in M
        cell_volume: cell volume, in uL
        shot_volumes: list of shot volumes, in uL.
        """

        # Run standard __init__ function to create titrations, initialize params
        # etc.
        super().__init__(S_cell,S_syringe,T_cell,T_syringe,cell_volume,shot_volumes)

        # Titrate the competitor
        self._C_cell = C_cell
        self._C_syringe = C_syringe
        self._C_conc = self._titrate_species(self._C_cell,self._C_syringe)


    @property
    def dQ(self):
        """
        Calculate the heats that would be observed across shots for a given set
        of enthalpies and binding constants for each reaction.
        """

        # ----- Determine mole fractions -----
        S_conc_corr = self._S_conc*self.param_values["fx_competent"]

        c_a = self.param_values["K"]*S_conc_corr
        c_b = self.param_values["Kcompetitor"]*S_conc_corr
        r_a = self._T_conc/S_conc_corr
        r_b = self._C_conc/S_conc_corr

        alpha = 1/c_a + 1/c_b + r_a + r_b - 1
        beta = (r_a - 1)/c_b + (r_b - 1)/c_a + 1/(c_a*c_b)
        gamma = -1/(c_a*c_b)
        theta = np.arccos((-2*alpha**3 + 9*alpha*beta - 27*gamma)/(2*np.sqrt((alpha**2 - 3*beta)**3)))

        mol_fx_s = (2*np.sqrt(alpha**2 - 3*beta) * np.cos(theta/3) - alpha)/3
        mol_fx_st = r_a*mol_fx_s/(1/c_a + mol_fx_s)
        mol_fx_sc = r_b*mol_fx_s/(1/c_b + mol_fx_s)

        # ---- Relate mole fractions to heat -----
        X = self.param_values["dH"]*(mol_fx_st[1:] - mol_fx_st[:-1])
        Y = self.param_values["dHcompetitor"]*(mol_fx_sc[1:] - mol_fx_sc[:-1])

        to_return = self._cell_volume*S_conc_corr[1:]*(X + Y) + self.dilution_heats

        return to_return
