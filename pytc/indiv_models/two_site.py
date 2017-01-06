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

    def _dQdT(self,T_free,p,q,r):
        """
        """

        return T_free**3 + p*(T_free**2) + q*T_free + r


    @property
    def dQ(self):
        """
        Calculate the heats that would be observed across shots for a given set
        of enthalpies and binding constants for each reaction.
        """

        S_conc_corr = self._S_conc*self.param_values["fx_competent"]

        for i in range(len(S_conc_corr)):

            # If there's no titrant, nothing is free.  (avoid numerical problems)
            if self._T_conc[i] == 0:
                self._T_conc_free[i] = 0.0
                continue

            # Manually check that bounds for root calculation have opposite signs
            min_value = self._dQdT(            0.0,S_conc_corr[i],self._T_conc[i])
            max_value = self._dQdT(self._T_conc[i],S_conc_corr[i],self._T_conc[i])

            # Uh oh, they have same sign (root optimizer will choke)
            if min_value*max_value > 0:

                if max_value < 0:
                    # root is closest to min --> set to that
                    if (max_value < min_value):
                        self._T_conc_free[i] = 0.0

                    # root is closest to max --> set to that
                    else:
                        self._T_conc_free[i] = self._T_conc[i]
                else:
                    # root is closest to max --> set to that
                    if (max_value < min_value):
                        self._T_conc_free[i] = self._T_conc[i]

                    # root is closest to min --> set to that
                    else:
                        self._T_conc_free[i] = 0.0

                continue

            T = scipy.optimize.brentq(self._dQdT,
                                      0,self._T_conc[-1],
                                      args=(S_conc_corr[i],
                                           self._T_conc[i]))

            # numerical problems sometimes make T slightly bigger than the total
            # concentration, so bring down to the correct value
            if (T > self._T_conc[i]):
                T = self._T_conc[i]

            self._T_conc_free[i] = T

        p = 1/self.param_values["K1"] + 1/self.param_values["K2"] + 2*S_conc_corr - self._T_conc

        q1 = (1/self.param_values["K1"] + 1/self.param_values["K2"])*S_conc_corr
        q2 = (1/self.param_values["K1"] + 1/self.param_values["K2"])*self._T_conc
        q3 = 1/(self.param_values["K1"]*self.param_values["K2"])
        q = q1 - q2 + q3

        r = -self._T_conc/(self.param_values["K1"]*self.param_values["K2"])

        T = scipy.optimize.brentq(self._dQdT,
                                  0,self._T_conc[-1],
                                  args=(S_conc_corr[i],
                                        self._T_conc[i]))
        

        # ----- Determine mole fractions -----
        S_conc_corr = self._S_conc*self.param_values["fx_competent"]
        b = S_conc_corr + self._T_conc + 1/self.param_values["K"]
        ST = (b - np.sqrt((b)**2 - 4*S_conc_corr*self._T_conc))/2

        self._mol_fx_st = ST/S_conc_corr

        # ---- Relate mole fractions to heat -----
        X = self.param_values["dH"]*(self._mol_fx_st[1:] - self._mol_fx_st[:-1])
   
        to_return = self._cell_volume*S_conc_corr[1:]*X + self.dilution_heats

        return to_return
