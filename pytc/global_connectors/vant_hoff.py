__description__ = \
"""
Fit a collection of ITC experiments at different temperatures to extract the 
van't Hoff enthalpy.  Assumes constant enthalpy over the temperature range.
"""
__author__ = "Michael J. Harms"
__date__ = "2017-01-15"

import numpy as np
from . import GlobalConnector

class VantHoff(GlobalConnector):
    """
    Fit a collection of ITC experiments at different temperatures to extract the 
    van't Hoff enthalpy.  Assumes constant enthalpy over the temperature range.
    """
    
    param_guesses = {"dH_vanthoff":0.0,"K_ref":10000}
    required_data = ["temperature"]

    def __init__(self,name,reference_temp=298.15):
        """
        Initialize the VantHoff class, defining the fitting parameters.
        """
    
        self.reference_temp = reference_temp

        super().__init__(name)


    def K(self,experiment):
        """
        Return the temperature-dependent binding constant, calculated using the
        a fixed enthalpy and shifting K. 
        """

        T = experiment.temperature + 273.15
        T_ref = self.reference_temp

        a = -(self.dH_vanthoff/experiment.R)*(1/T - 1/T_ref)

        return self.K_ref*np.exp(a)
       
    def dH(self,experiment):
        """
        Return the van't Hoff enthalpy.
        """

        return self.dH_vanthoff 

