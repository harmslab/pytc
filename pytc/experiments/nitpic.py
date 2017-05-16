__description__ = \
"""
nitpic.py

Read data files from NITPIC ITC package. Takes the X.sedphat folder output.
"""
__author__ = "Michael J. Harms"
__date__ = "2017-05-15"

from .base import BaseITCExperiment
import numpy as np
import os

class NitpicExperiment(BaseITCExperiment):
    """
    Read data files from NITPIC ITC package. Takes the X.sedphat folder output
    by ITC as the dh_file.
    """

    def _read_heats_file(self):
        """
        Read data files from NITPIC ITC package. Takes the X.sedphat folder output.
        """

        # Figure out what files to load in
        read_files = []
        for path, subdirs, files in os.walk(self.dh_file):
            for name in files:
                if name.endswith((".xp", ".nitpic",".error-dat")):
                    read_files.append(os.path.join(path, name))

        # Read in meta data
        exp_data = next(f for f in read_files if ".xp" in f)
        f = open(exp_data, 'r')
        meta = f.readlines()
        f.close()

        self.temperature = float(next(t for t in meta if "Temperature" in t).split()[0])
        self.stationary_cell_conc = float(next(t for t in meta if "cellconc" in t).split()[0])/1e6
        self.titrant_syringe_conc = float(next(t for t in meta if "syringconc" in t).split()[0])*1e-6
        self.cell_volume = float(next(t for t in meta if "cellvolume" in t).split()[0])

        # Read in heat data
        heat_data = next(f for f in read_files if ".nitpic" in f)
        f = open(heat_data, 'r')
        lines = f.readlines()
        f.close()

        shots = []
        heats = []
        ndh = []
        for l in lines[1:]:
            if "--" in l:
                break
            col = l.split()
            heats.append(float(col[0]))
            shots.append(float(col[1]))
            ndh.append(float(col[5]))

        self._shots = np.array(shots)
        self._heats = np.array(heats)

        # Read standard deviation on heat from the nitpic .error-dat file
        err_data = next(f for f in read_files if ".error-dat" in f)
        f = open(err_data,'r')
        lines = f.readlines()
        f.close()

        heats_stdev = []
        for i, l in enumerate(lines):
            sd = ndh[i] - float(l.split()[0])
            heats_stdev.append(sd*shots[i]/1000.0)

        self._heats_stdev = np.array(heats_stdev)
