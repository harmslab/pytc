__description__ = \
"""
Class that holds an ITC experiment integrated using Origin.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

from .base import BaseITCExperiment
import numpy as np

class OriginExperiment(BaseITCExperiment):
    """
    Class that holds an ITC experiment integrated using Origin.
    """

    def _read_heats_file(self):
        """
        Read the heats file written out by the MicroCal/Origin ITC analysis
        package.
        """

        f = open(self.dh_file,'r')
        lines = f.readlines()
        f.close()

        meta = lines[2].split(",")

        self.temperature = float(meta[0])
        self.stationary_cell_conc = float(meta[1])*1e-3
        self.titrant_syringe_conc = float(meta[2])*1e-3
        self.cell_volume = float(meta[3])*1e3

        shots = []
        heats = []
        for l in lines[5:]:
            col = l.split(",")
            shots.append(float(col[0]))
            heats.append(float(col[1]))

        self._shots = np.array(shots)
        self._heats = np.array(heats)
      
        # Because there is no heat error in this file, assign the heat error
        # specified by the user. 
        self._heats_stdev = np.array([self._uncertainty
                                      for i in range(len(self._heats))]) 

