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
    
    @property
    def mole_ratio(self):
        
        return self._T_conc[1:]/self._S_conc[1:]

