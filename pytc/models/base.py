__description__ = \
"""
base.py

Base class for other itc model description.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import numpy as np

class ITCModel:
    """
    Base class from which all ITC models should be sub-classed.  Each model
    should have an __init__ method that populates the model and a dQ method
    that returns dQ as a function of a set of keyword parameters.
    """
    
    def __init__(self):

        pass
    
    def dQ(self):
        pass
    
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
        Molar ratio of titrant to stationary species.
        """   
     
        return self._T_conc[1:]/self._S_conc[1:]

