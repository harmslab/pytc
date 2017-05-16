__description__ = \
"""
Class for analyzing experimental enthalpy vs. ionization enthalpy of buffer.
"""
__author__ = "Michael J. Harms"
__date__ = "2017-01-15"

from . import GlobalConnector

class NumProtons(GlobalConnector):
    """
    Returns the observed enthalpy of an experiment given an intrinsic binding
    enthalpy and number of protons released/taken up.  Requires experiment 
    instances have .ionization_enthalpy attribute.
    """

    param_guesses = {"num_H":0.0, "dH_intrinsic":0.0}
    required_data = ["ionization_enthalpy"]

    def dH(self,experiment):
        """
        Return the change in enthalpy upon binding of buffers with different
        ionization enthalpies. 
        """

        dHion = experiment.ionization_enthalpy

        return self.dH_intrinsic + self.num_H*dHion

