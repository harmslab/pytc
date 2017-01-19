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
        shot_start: first shot to use in fit
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
        self._numerator = np.zeros(len(self._S_conc),dtype=float)
        self._denominator = np.ones(len(self._S_conc),dtype=float)
        self._i_array = np.arange(len(self._fit_beta_list),dtype=float) + 1

    def _dQdT(self,T_free,S_total,T_total):
        """
        T_total = T_free + S_total*(dln(P)/dln(T_free)), so:
        0 = T_free + S_total*(dln(P)/dln(T_free)) - T_total

        Solve this for T_free to find free titrant.

        dln(P)/dln(T_free)

        P = (beta1*T_free**1) *  b2*T**2
        """

        numerator =       np.sum(self._i_array*self._fit_beta_array*(T_free**self._i_array))
        denominator = 1 + np.sum(              self._fit_beta_array*(T_free**self._i_array))

        return T_free + S_total*(numerator/denominator) - T_total

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

        # Find the root of the derivative of the binding polynomial, giving the
        # free titrant concentration
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


        # calculate the average enthalpy change
        self._numerator   = 0.0
        self._denominator = 1.0
        for i in range(len(self._fit_beta_array)):
            self._numerator   += self._fit_dH_array[i]*self._fit_beta_array[i]*(self._T_conc_free**(i+1))
            self._denominator +=                       self._fit_beta_array[i]*(self._T_conc_free**(i+1))

        avg_dH = self._numerator/self._denominator

        X = avg_dH[1:] - avg_dH[:-1]

        to_return = self._cell_volume*S_conc_corr[1:]*X + self.dilution_heats

        return to_return
