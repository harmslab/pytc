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

    def param_definition():
        pass
    
    @property
    def dQ(self):
        """
        Calculate heat of dilution as a function of titrant concentration in
        the cell.
        """

        to_return = self.dilution_heats

        return to_return
