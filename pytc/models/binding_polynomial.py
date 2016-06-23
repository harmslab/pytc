__description__ = \
"""
models.py

Models subclassed from ITCModel used to model (and fit) ITC data.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import numpy as np
from .base import ITCModel

class BindingPolynomial(ITCModel):
    """
    Base class for a binding polynomial fit.
    """
    
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
 
        self._S_cell = S_cell
        self._S_syringe = S_syringe
        
        self._T_cell = T_cell
        self._T_syringe = T_syringe
           
        self._cell_volume = cell_volume
        self._shot_volumes = np.array(shot_volumes)
        
        self._determine_titration_conc()

        # Populate the set of arguments for this number of sites.
        self.dQ_arguments = ["beta{}".format(i) for i in range(1,self._num_sites + 1)]
        self.dQ_arguments.extend(["dH{}".format(i) for i in range(1,self._num_sites + 1)])
        self.dQ_arguments.append("fx_competent")
        self.dQ_arguments.append("dilution_heat")

    def _determine_titration_conc(self):
        """
        Determine the concentrations of stationary and titrant species in the
        cell given a set of titration shots and initial concentrations of both 
        the stationary and titrant species. 
        """
        
        self._volume = np.zeros(len(self._shot_volumes)+1)
        self._S_conc = np.zeros(len(self._shot_volumes)+1)
        self._T_conc = np.zeros(len(self._shot_volumes)+1)
        
        self._volume[0] = self._cell_volume
        self._S_conc[0] = self._S_cell
        self._T_conc[0] = self._T_cell
        
        for i in range(len(self._shot_volumes)):
            
            self._volume[i+1] = self._volume[i] + self._shot_volumes[i]
            
            dilution = self._volume[i]/self._volume[i+1]
            added = self._shot_volumes[i]/self._volume[i+1]
            
            self._S_conc[i+1] = self._S_conc[i]*dilution + self._S_syringe*added
            self._T_conc[i+1] = self._T_conc[i]*dilution + self._T_syringe*added
   
    def _dQdT(self,T_free,beta_list,S_total,T_total):
        """
        T_total = T_free + S_total*(dln(P)/dln(T_free)), so:
        0 = T_free + S_total*(dln(P)/dln(T_free)) - T_total

        Solve this for T_free to find free titrant.

        dln(P)/dln(T_free)

        P = (beta1*T_free**1) *  b2*T**2
        """
    
        i_array = np.arange(len(beta_list),dtype=float)
        numerator =       np.sum(i_array*beta_list[i]*(T_free**i_array))
        denominator = 1 + np.sum(        beta_list[i]*(T_free**i_array))

        return T_free + S_total*(numerator/denominator) - T_total

    def _get_dQ(self,beta_array,dH_array,fx_competent,dilution_heat):
        """
        Method for calculating dQ for an arbitrary-order binding polynomial. 
        """

        S_conc_corr = self._S_conc*fx_competent
       
        # Find the root of the derivative of the binding polynomial, giving the
        # free titrant concentration
        T_conc_free = np.zeros(len(S_conc_corr),dtype=float) 
        for i in range(len(S_conc_corr)):
            T = scipy.optimize.findminbound(self.dQdT,0,T_total[i],
                                            args=(beta_array,
                                                  S_conc_corr[i],
                                                  T_total[i]))
            T_conc_free[i] = T[0]

        numerator = np.zeros(len(T_conc_free),dtype=float)
        denominator = np.ones(len(T_conc_free),dtype=float)
        for i in range(len(beta_list)):
            numerator   += dH_array[i]*beta_list[i]*(T_conc_free**(i))
            denominator +=             beta_list[i]*(T_conc_free**(i))
      
        Q = numerator/denominator
        X = Q[1:] - Q[:-1]

        to_return = self._cell_volume*S_conc_corr[1:]*X + self._T_conc[1:]*dilution_heat

        return to_return

    def dQ(self,fx_competent=1.0,dilution_heat=0.0,**kwargs):
        """
        Calculate the heats that would be observed across shots for a given set
        of enthalpies and binding constants for each reaction.
        """
        
        beta_array = np.zeros(self._num_sites,dtype=float)
        dH_array = np.zeros(self._num_sites,dtype=float)

        for i in range(self._num_sites):
            beta_array[i] = kwargs["beta{}".format(i+1)]
            dH_array[i] =   kwargs["dH{}".format(i+1)]
        
        return self._get_dQ(beta_array,dH_array,fx_competent,dilution_heat)

