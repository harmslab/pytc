__description__ = \
"""
fitting.py

Classes for doing nonlinear regression of global models against multiple ITC
experiments.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import copy
import numpy as np
import scipy.optimize as optimize
from matplotlib import pyplot as plt

class GlobalFit:
    """
    Class for regressing some binding model against an arbitrary number of 
    ITC experiments.
    """

    def __init__(self,param_guesses):
        """
        Set up the main binding model to fit.
        param_guesses: a dictionary of all parameters to be fit.  keys are parameter
                       names.  values are parameter guesses. 
        """

        # Dictionary with all parameters to be fit as keys and initial guesses
        # for their values.
        self._param_guesses = copy.copy(param_guesses)

        # maps for converting between parameter name and index of parameter in 
        # the np.array used for the fitting.
        self._index_to_name = list(self._param_guesses.keys())
        self._index_to_name.sort()
        self._name_to_index = dict([(a,i)
                                    for i,a in enumerate(self._index_to_name)])

        # _fit_param_array holds the parameter values that will be fit by 
        # nonlinear regression
        self._fit_param_array = np.zeros(len(self._param_guesses),dtype=float)
        for a in self._name_to_index.keys():
            self._fit_param_array[self._name_to_index[a]] = self._param_guesses[a]

        # List of experiments and parameter mapping
        self._experiment_list = []
        self._arg_map_list = []
        self._exp_weights = []

    def add_experiment(self,experiment,arg_map,weight=1.0):
        """
        experiment: an initialized ITCExperiment instance
        arg_map: dictionary mapping global parameter names to parameters for individual
                 experiment model parameters.  
        weight: how much to weight this experiment in the regression relative to other
                experiments.  Values <1.0 weight this experiment less than others; 
                values >1.0 weight this more than others.
        """

        self._experiment_list.append(experiment)
        self._arg_map_list.append(copy.copy(arg_map))
        self._exp_weights.append(weight)

        # Make sure that the global parameter values in arg_map are actually found in
        # the set of global parameters
        for a in self._arg_map_list[-1].keys():
            try:
                self._name_to_index[a]
            except KeyError:
                err = "parameter {} not part of fit\n".format(a)
                raise ValueError(err)

    def _residuals(self,param):
        """
        Determine the residuals between the global model and all experiments.
        """
        
        all_residuals = []
        
        # Calculate residuals for each experiment
        for i, e in enumerate(self._experiment_list):

            # This uses the names of the total model parameters as keys to 
            # map to the appropriate parameter values being fit to the 
            # names of those parameters in the local experiment model.
            model_param_kwarg = {}
            for a in self._arg_map_list[i].keys():
                dq_model_param_name = self._arg_map_list[i][a]
                param_value = param[self._name_to_index[a]]
                model_param_kwarg[dq_model_param_name] = param_value

            # calculate the current value of the model
            calc = e.model_dq(**model_param_kwarg)
            
            # add to the total set of residuals
            all_residuals.extend(self._exp_weights[i]*(e.heats - calc))

        return np.array(all_residuals)

    
    def fit(self):
        """
        Perform a global fit using nonlinear regression.
        """
        
        # Do the actual fit
        fit_param, covariance, info_dict, message, error = optimize.leastsq(self._residuals,
                                                                            x0=self._fit_param_array,
                                                                            full_output=True)
        # Store the result
        self._fit_param = fit_param
    
    
    def plot(self,color_list=None):
        """
        Plot the experimental data and fit results.
        """
        
        if color_list == None:
            N = len(self._experiment_list)
            color_list = [plt.cm.brg(i/N) for i in range(N)]
        
        if len(color_list) < len(self._experiment_list):
            err = "Number of specified colors is less than number of experiments.\n"
            raise ValueError(err)
        
        for i, e in enumerate(self._experiment_list):
            
            model_param_kwarg = {}
            for a in self._arg_map_list[i].keys():
                dq_param_name = self._arg_map_list[i][a]
                param_value = self.fit_param[a]
                model_param_kwarg[dq_param_name] = param_value
            
            plt.plot(e.mole_ratio,e.heats,"o",color=color_list[i])
            plt.plot(e.mole_ratio,e.model_dq(**model_param_kwarg),color=color_list[i],linewidth=1.5)
        
    
    @property
    def fit_param(self):
        """
        Return the fit results as a dictionary that keys parameter name to fit value.
        """
        
        out_dict = {}
        for i, a in enumerate(self._index_to_name):
            out_dict[a] = self._fit_param[i]
        
        return out_dict
        
