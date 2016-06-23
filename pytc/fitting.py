__description__ = \
"""
fitting.py

Classes for doing nonlinear regression of global models against multiple ITC
experiments.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

import copy, inspect, warnings
import numpy as np
import scipy.optimize as optimize
from matplotlib import pyplot as plt

class GlobalFit:
    """
    Class for regressing some binding model against an arbitrary number of 
    ITC experiments.
    """

    def __init__(self,param_guesses,fixed_param=None):
        """
        Set up the main binding model to fit.
        param_guesses: a dictionary of all parameters to be fit.  keys are parameter
                       names.  values are parameter guesses. 
        """

        # Dictionary with all parameters to be fit as keys and initial guesses
        # for their values.
        self._param_guesses = copy.copy(param_guesses)

        # Fixed parameters
        self._fixed_global_param = {}
        if fixed_param != None:
            self._fixed_global_param = copy.copy(fixed_param)

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
        self._fixed_local_param = []

    def add_experiment(self,experiment,arg_map=None,weight=1.0,**fixed_param_kwargs):
        """
        experiment: an initialized ITCExperiment instance
        arg_map: dictionary mapping names of global parameter to names of 
                 parameters passed to a model dQ function.  If None, the
                 global names will be passed directly to dQ.
        weight: how much to weight this experiment in the regression relative to other
                experiments.  Values <1.0 weight this experiment less than others; 
                values >1.0 weight this more than others.
        """

        self._experiment_list.append(experiment)
        self._exp_weights.append(weight)

        # Get a list of the possible arguments that could be passed to the model
        # dQ method       
        possible_model_args = inspect.getargspec(experiment.model.dQ).args
        possible_model_args.remove("self")

        # If no argument mapping is specified, associate global parameter names
        # with local function names. 
        if arg_map == None:
            arg_map = {}
            for a in self._index_to_name:
                if a in possible_model_args:
                    arg_map[a] = a

        self._arg_map_list.append(copy.copy(arg_map))

        # Fixed parameter values can be passed as keywords to add_experiment.  If
        # any are present, record them.
        self._fixed_local_param.append({}) 
        if len(fixed_param_kwargs) != 0:
            for k in fixed_param_kwargs.keys():
                self._fixed_local_param[-1][k] = fixed_param_kwargs[k]
                
        # Make sure that the global parameter values in arg_map are actually found in
        # the set of global parameters, and that the local parameter names are
        # correct.
        for a in self._arg_map_list[-1].keys():

            try:
                self._name_to_index[a]
            except KeyError:
                err = "parameter {} not defined in global fit\n".format(a)
                raise ValueError(err)

            if self._arg_map_list[-1][a] not in possible_model_args:
                err = "the fitting model does not have an argument named {}\n".format(self._arg_map_list[-1][a])
                raise ValueError(err)

    def _call_dq(self,i,param):
        """
        Call the dQ method for experiment i, mapping global parameters to local
        parameters and fixing specified parameters.
        """

        # This uses the names of the total model parameters as keys to 
        # map to the appropriate parameter values being fit to the 
        # names of those parameters in the local experiment model.
        model_param_kwarg = {}
        for a in self._arg_map_list[i].keys():
            dq_model_param_name = self._arg_map_list[i][a]

            # See if the parameter is globally fixed.  If so, use the fixed
            # value.  If not, use the param value from the method call
            try:
                param_value = self._fixed_global_param[dq_model_param_name]
            except KeyError:
                param_value = param[self._name_to_index[a]]

            model_param_kwarg[dq_model_param_name] = param_value

        # A parameter fixed for this local experiment overrides either the 
        # floating parameter or the globally fixed parameters
        for a in self._fixed_local_param[i].keys():
            model_param_kwarg[a] = self._fixed_local_param[i][a]

        # calculate the current value of the model
        return self._experiment_list[i].model_dq(**model_param_kwarg)


    def _residuals(self,param):
        """
        Determine the residuals between the global model and all experiments.
        """
        
        all_residuals = []
        
        # Calculate residuals for each experiment
        for i, e in enumerate(self._experiment_list):

            calc = self._call_dq(i,param)
 
            # add to the total set of residuals
            all_residuals.extend(self._exp_weights[i]*(e.heats - calc))

        return np.array(all_residuals)

    
    def fit(self):
        """
        Perform a global fit using nonlinear regression.
        """

        # Some sanity checking
        if len(self._experiment_list) == 0:
            warn = "No experiments loaded.  Fit is trivial.\n"
            warnings.warn(warn)
        
        if len(self._experiment_list) > 1:
            for i in range(len(self._experiment_list)):
                if len(self._fixed_local_param[i]) != 0:
                    warn = "Individual experiment(s) have fixed parameters.  These will be ignored by the global fit for this experiment, but could float for other experiments in the data set.  To fix a parameter globally, pass it to GlobalFit in the fixed_param dictionary.  See documentation for details."
                    warnings.warn(warn)

                    # Get out of loop so the warning only appears once.
                    break

        # Set starting value for fit
        self._fit_param = self._fit_param_array
        
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
       
        # Only make a plot if the fit has already been run 
        try:
            self._fit_param
        except AttributeError:
            warn = "Fit has not yet been run.  No plot generated."
            warnings.warn(warn)
            return      
 
 
        if color_list == None:
            N = len(self._experiment_list)
            color_list = [plt.cm.brg(i/N) for i in range(N)]
        
        if len(color_list) < len(self._experiment_list):
            err = "Number of specified colors is less than number of experiments.\n"
            raise ValueError(err)
        
        for i, e in enumerate(self._experiment_list):
            
            calc = self._call_dq(i,self._fit_param)
 
            plt.plot(e.mole_ratio,e.heats,"o",color=color_list[i])
            plt.plot(e.mole_ratio,calc,color=color_list[i],linewidth=1.5)
        
    
    @property
    def fit_param(self):
        """
        Return the fit results as a dictionary that keys parameter name to fit value.
        """
       
        try:
 
            out_dict = {}
            for i, a in enumerate(self._index_to_name):
                out_dict[a] = self._fit_param[i]
       
            for a in self._fixed_global_param.keys():
                out_dict[a] = self._fixed_global_param[a]
        
        # If the fit has not been run, return an empty dictionary    
        except AttributeError:
            out_dict = {}

        return out_dict
        
