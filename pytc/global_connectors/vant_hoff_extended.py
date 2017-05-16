__description__ = \
"""
Fit a collection of ITC experiments at different temperatures to extract the 
heat capacity change upon binding, as well as the enthalpy and binding 
constant at at the defined reference temperature.
"""
__author__ = "Michael J. Harms"
__date__ = "2017-01-15"

import numpy as np
from . import GlobalConnector

class VantHoffExtended(GlobalConnector):
    """
    Fit a collection of ITC experiments at different temperatures to extract the 
    heat capacity change upon binding, as well as the enthalpy and binding 
    constant at at the defined reference temperature.
    """

    param_guesses = {"K_ref":1.0,"dH_ref":0.0,"dCp":0.0}
    required_data = ["temperature"]
    
    def __init__(self,name,reference_temp=298.15):
        """
        Initialize the VantHoffExtended class, defining the fitting parameters.
        """

        self.reference_temp = reference_temp

        super().__init__(name)

    def K(self,experiment):
        """
        Return the temperature-dependent binding constant, determined using the
        binding constant at a reference temperature, enthalpy at that reference
        temperature, and the heat capacity change on binding.
        """

        T = experiment.temperature + 273.15
        T_ref = self.reference_temp

        a = -(self.dH_ref/experiment.R)*(1/T - 1/T_ref)
        b = (self.dCp/experiment.R)*(np.log(T/T_ref) + T_ref/T - 1)

        return self.K_ref*np.exp(a + b)

    def dH(self,experiment):
        """
        Return the enthalpy change of binding at a given temperature, determined
        from the enthalpy change at the reference temperature and the heat 
        capacity change on binding.
        """

        T = experiment.temperature + 273.15
        return self.dH_ref + self.dCp*(T - self.reference_temp)

