__description__ = \
"""
experiments.py

Classes for loading experimental ITC data and associating those data with a model.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import random, string
import numpy as np

class ITCExperiment:
    """
    Class that holds an experimental ITC measurement and a model that describes it.
    """

    def __init__(self,dh_file,model,shot_start=1,**model_kwargs):
        """
        dh_file: integrated heats file written out by origin software.
        model: name of ITCModel subclass to use for modeling
        shot_start: what shot to use as the first real point.  Shots
                    start at 0, so default=1 discards first point.
        **model_kwargs: any keyword arguments to pass to the model.  Any
                        keywords passed here will override whatever is
                        stored in the dh_file.
        """

        self.dh_file = dh_file
        self._shot_start = shot_start

        # Load in heats
        self._read_heats_file()

        # Initialize model using information read from heats file
        self._model = model(S_cell=self.stationary_cell_conc,
                            T_syringe=self.titrant_syringe_conc,
                            cell_volume=self.cell_volume,
                            shot_volumes=self._shots,**model_kwargs)

        self._experiment_id = "".join([random.choice(string.ascii_letters)
                                       for i in range(20)])


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


    @property
    def dQ(self):
        """
        Return heats calculated by the model with parameters defined in params
        dictionary.
        """

        if len(self._model.dQ) == 0:
            return np.array(())

        return self._model.dQ[self._shot_start:]

    @property
    def dilution_heats(self):
        """
        Return dilution heats calculated by the model with parameters defined
        in params dictionary.
        """

        if len(self._model.dilution_heats) == 0:
            return np.array(())

        return self._model.dilution_heats[self._shot_start:]

    @property
    def param_values(self):

        return self._model.param_values

    @property
    def param_errors(self):

        return self._model.param_errors

    @property
    def model(self):
        """
        Fitting model.
        """

        return self._model

    @property
    def heats(self):
        """
        Return experimental heats.
        """
        return self._heats[self._shot_start:]

    @property
    def mole_ratio(self):
        """
        Return the mole ratio of titrant to stationary.
        """
        return self._model.mole_ratio[self._shot_start:]

    @property
    def experiment_id(self):
        """
        Return a unique experimental id.
        """

        return self._experiment_id
