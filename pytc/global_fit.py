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
from matplotlib import gridspec

from . global_connectors import GlobalConnector

class GlobalFit:
    """
    Class for regressing models against an arbitrary number of ITC experiments.
    """

    def __init__(self):
        """
        Set up the main binding model to fit.
        """

        # Objects for holding global parameters
        self._global_param_keys = []
        self._global_params = {}
        self._global_param_mapping = {}

        # List of experiments and the weight to apply for each experiment
        self._expt_dict = {}
        self._expt_weights = {}
        self._expt_list_stable_order = []

    def add_experiment(self,experiment,weight=1.0):
        """
        experiment: an initialized ITCExperiment instance
        weight: how much to weight this experiment in the regression relative to other
                experiments.  Values <1.0 weight this experiment less than others;
                values >1.0 weight this more than others.
        """

        name = experiment.experiment_id

        # Record the experiment
        self._expt_dict[name] = experiment
        self._expt_list_stable_order.append(name)
        self._expt_weights[name] = weight

    def remove_experiment(self,experiment):
        """
        Remove an experiment from the analysis.
        """

        expt_name = experiment.experiment_id

        # Go through all global parameters
        for k in self._global_param_mapping.keys():

            # If the experiment links to that
            for expt in self._global_param_mapping[k]:
                if expt_name == expt[0]:
                    self._global_param_mapping[k].remove(expt)

                    if len(self._global_param_mapping[k]) == 0:
                        self.remove_global(k)

        self._expt_dict.pop(expt_name)
        self._expt_list_stable_order.remove(expt_name)

    def link_to_global(self,expt,expt_param,global_param_name):
        """
        Link a local experimental fitting parameter to a global fitting
        parameter.
        """

        expt_name = expt.experiment_id

        # If the experiment hasn't already been added to the global fitter, add it
        try:
            self._expt_dict[expt_name]
        except KeyError:
            self.add_experiment(expt)

        # Make sure the experimental paramter is actually in the experiment
        if expt_param not in self._expt_dict[expt_name].model.param_names:
            err = "Parameter {} not in experiment {}\n".format(expt_param,expt_name)
            raise ValueError(err)

        # Update the alias from the experiment side
        self._expt_dict[expt_name].model.update_aliases({expt_param:
                                                         global_param_name})

        # Update the alias from the global side
        e = self._expt_dict[expt_name]
        if global_param_name not in self._global_param_keys:

            # Make new global parameter and create link
            self._global_param_keys.append(global_param_name)
            self._global_param_mapping[global_param_name] = [(expt_name,expt_param)]

            # If this is a "dumb" global parameter, store a FitParameter
            # instance with the data in it.
            if type(global_param_name) == str:
                self._global_params[global_param_name] = copy.copy(e.model.parameters[expt_param])

            # If this is a GlobalConnector method, store the GlobalConnector
            # instance as the paramter
            elif issubclass(global_param_name.__self__.__class__,GlobalConnector):
                self._global_params[global_param_name] = global_param_name.__self__

            else:
                err = "global variable class not recongized.\n"
                raise ValueError(err)

        else:
            # Only add link, but do not make a new global parameter
            if expt_name not in [m[0] for m in self._global_param_mapping[global_param_name]]:
                self._global_param_mapping[global_param_name].append((expt_name,expt_param))

    def unlink_from_global(self,expt,expt_param):
        """
        Remove the link between a local fitting parameter and a global
        fitting parameter.
        """

        expt_name = expt.experiment_id

        # Make sure the experimental parameter is actually in the experiment
        if expt_param not in self._expt_dict[expt_name].model.param_names:
            err = "Parameter {} not in experiment {}\n".format(expt_param,expt_name)
            raise ValueError(err)

        global_name = self._expt_dict[expt_name].model.parameters[expt_param].alias

        # remove global --> expt link
        self._global_param_mapping[global_name].remove((expt_name,expt_param))
        if len(self._global_param_mapping[global_name]) == 0:
            self.remove_global(global_name)

        # remove expt --> global link
        self._expt_dict[expt_name].model.update_aliases({expt_param:None})


    def remove_global(self,global_param_name):
        """
        Remove a global parameter, unlinking all local parameters.
        """

        if global_param_name not in self._global_param_keys:
            err = "Global parameter {} not defined.\n".format(global_param_name)
            raise ValueError(err)

        # Remove expt->global mapping from each experiment
        for k in self._global_param_mapping.keys():

            for expt in self._global_param_mapping[k]:

                expt_name = expt[0]
                expt_params = self._expt_dict[expt_name].model.param_aliases.keys()
                for p in expt_params:
                    if self._expt_dict[expt_name].model.param_aliases[p] == global_param_name:
                        self._expt_dict[expt_name].model.update_aliases({p:None})
                        break

        # Remove global data
        self._global_param_keys.remove(global_param_name)
        self._global_param_mapping.pop(global_param_name)
        self._global_params.pop(global_param_name)

    def _residuals(self,param=None):
        """
        Calculate the residuals between the experiment and calculated model
        heats.
        """

        all_residuals = []

        for i in range(len(param)):

            # local variable
            if self._float_param_type[i] == 0:
                experiment = self._float_param_mapping[i][0]
                parameter_name = self._float_param_mapping[i][1]
                self._expt_dict[experiment].model.update_values({parameter_name:param[i]})

            # Vanilla global variable
            elif self._float_param_type[i] == 1:
                param_key = self._float_param_mapping[i][0]
                for experiment, parameter_name in self._global_param_mapping[param_key]:
                    self._expt_dict[experiment].model.update_values({parameter_name:param[i]})

            # Global connector global variable
            elif self._float_param_type[i] == 2:
                connector = self._float_param_mapping[i][0].__self__
                param_name = self._float_param_mapping[i][1]
                connector.update_values({param_name:param[i]})

            else:
                err = "Paramter type {} not recongized.\n".format(self._float_param_type[i])
                raise ValueError(err) 

        # Look for connector functions
        for connector_function in self._global_param_keys:

            if type(connector_function) == str:
                continue

            # If this is a method of GlobalConnector...
            if issubclass(connector_function.__self__.__class__,
                          GlobalConnector):

                # Update experiments with the value spit out by the connector function
                for expt, param in self._global_param_mapping[connector_function]:
                    e = self._expt_dict[expt]
                    value = connector_function(e)
                    self._expt_dict[expt].model.update_values({param:value})
                 
        # Calculate residuals
        for k in self._expt_dict.keys():
            all_residuals.extend(self._expt_weights[k]*(self._expt_dict[k].heats - self._expt_dict[k].dQ))

        return np.array(all_residuals)


    def fit(self):
        """
        Perform a global fit using nonlinear regression.
        """

        self._float_param = []
        self._float_bounds = [[],[]]
        self._float_param_mapping = []
        self._float_param_type = []

        self._float_global_connectors_seen = []

        float_param_counter = 0

        # Go through global variables
        for k in self._global_param_mapping.keys():
      
            # Otherwise, there is just one parameter to enumerate over.
            if type(k) == str:
                enumerate_over = {k:self._global_params[k]} 
                param_type = 1
 
            # If this is a global connector, enumerate over all parameters in
            # that connector 
            elif issubclass(k.__self__.__class__,GlobalConnector):

                # Only load each global connector in once
                if k in self._float_global_connectors_seen:
                    continue

                enumerate_over = self._global_params[k].params
                self._float_global_connectors_seen.append(k)
                param_type = 2

            else:
                err = "global variable class not recongized.\n"
                raise ValueError(err)
            
            # Now update parameter values, bounds, and mapping 
            for e in enumerate_over.keys(): 

                # skip fixed paramters
                if enumerate_over[e].fixed:
                    continue

                self._float_param.append(enumerate_over[e].guess)
                self._float_bounds[0].append(enumerate_over[e].bounds[0])
                self._float_bounds[1].append(enumerate_over[e].bounds[1])
                self._float_param_mapping.append((k,e))
                self._float_param_type.append(param_type)

                float_param_counter += 1

        # Go through every experiment
        for k in self._expt_dict.keys():

            # Go through fit parameters within each experiment
            e = self._expt_dict[k]
            for p in e.model.param_names:

                # If the parameter is fixed, ignore it.
                if e.model.fixed_param[p]:
                    continue

                # If the paramter is global, ignore it.
                try:
                    e.model.param_aliases[p]
                    continue
                except KeyError:
                    pass

                # If not fixed or global, append the parameter to the list of
                # floating parameters
                self._float_param.append(e.model.param_guesses[p])
                self._float_bounds[0].append(e.model.bounds[p][0])
                self._float_bounds[1].append(e.model.bounds[p][1])
                self._float_param_mapping.append((k,p))
                self._float_param_type.append(0)

                float_param_counter += 1

        self._float_param = np.array(self._float_param,dtype=float)

        # Do the actual fit
        self._fit_result = optimize.least_squares(self._residuals, 
                                                  x0=self._float_param,
                                                  bounds=self._float_bounds)
        fit_parameters = self._fit_result.x

        # Determine the covariance matrix (Jacobian * residual variance)
        pcov = self._fit_result.jac*(np.sum(self._fit_result.fun**2)/(len(self._fit_result.fun)-len(self._fit_result.x)))

        # Estimates of parameter uncertainty
        error = np.absolute(np.diagonal(pcov))**0.5

        # Store the result
        for i in range(len(fit_parameters)):

            # local variable
            if self._float_param_type[i] == 0:

                experiment = self._float_param_mapping[i][0]
                parameter_name = self._float_param_mapping[i][1]

                self._expt_dict[experiment].model.update_values({parameter_name:fit_parameters[i]})
                self._expt_dict[experiment].model.update_errors({parameter_name:error[i]})

            # Vanilla global variable
            elif self._float_param_type[i] == 1:

                param_key = self._float_param_mapping[i][0]
                for k, p in self._global_param_mapping[param_key]:
                    self._expt_dict[k].model.update_values({p:fit_parameters[i]})
                    self._global_params[param_key].value = fit_parameters[i]
                    self._global_params[param_key].error = error[i]

            # Global connector global variable
            elif self._float_param_type[i] == 2:
                connector = self._float_param_mapping[i][0].__self__
                param_name = self._float_param_mapping[i][1]

                # HACK: if you use the params[param_name].value setter function,
                # it will break the connector.  This is because I expose the 
                # thermodynamic-y stuff of interest via .__dict__ rather than 
                # directly via params.  So, this has to use the .update_values
                # method. 
                connector.update_values({param_name:fit_parameters[i]})
                connector.params[param_name].error = error[i]

            else:
                err = "Paramter type {} not recongized.\n".format(self._float_param_type[i])
                raise ValueError(err) 


    def plot(self,correct_molar_ratio=False,subtract_dilution=False,
             color_list=None,data_symbol="o",linewidth=1.5):
        """
        Plot the experimental data and fit results.
    
        Returns matplotlib Figure and AxesSubplot instances that can be further
        manipulated by the user of the API.
        """

        fig = plt.figure(figsize=(5.5,6)) 

        gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1]) 
        ax = []
        ax.append(fig.add_subplot(gs[0]))
        ax.append(fig.add_subplot(gs[1],sharex=ax[0]))

        for i in range(2):
            ax[i].spines['top'].set_visible(False)
            ax[i].spines['right'].set_visible(False)

            ax[i].yaxis.set_ticks_position('left')
            ax[i].xaxis.set_ticks_position('bottom')


        if color_list == None:
            N = len(self._expt_list_stable_order)
            color_list = [plt.cm.brg(i/N) for i in range(N)]

        if len(color_list) < len(self._expt_list_stable_order):
            err = "Number of specified colors is less than number of experiments.\n"
            raise ValueError(err)

        for i, expt_name in enumerate(self._expt_list_stable_order):

            e = self._expt_dict[expt_name]

            mr = e.mole_ratio
            heats = e.heats
            calc = self._expt_dict[expt_name].dQ

            if len(calc) > 0:

                # Try to correct molar ratio for competent fraction
                if correct_molar_ratio:
                    try:
                        mr = mr/e.param_values["fx_competent"]
                    except KeyError:
                        pass

                if subtract_dilution:
                    heats = heats - e.dilution_heats
                    calc = calc - e.dilution_heats

            ax[0].plot(mr,heats,data_symbol,color=color_list[i])

            if len(e.dQ) > 0:

                ax[0].plot(mr,calc,color=color_list[i],linewidth=linewidth)
                ax[0].set_ylabel("heat per shot (kcal/mol)")

                ax[1].plot([np.min(mr),np.max(mr)],[0,0],"--",linewidth=1.0,color="gray")
                ax[1].plot(mr,(calc-heats),data_symbol,color=color_list[i])     
                ax[1].set_xlabel("molar ratio (titrant/stationary)")
                ax[1].set_ylabel("residual")

                plt.setp(ax[0].get_xticklabels(), visible=False)
        
        fig.set_tight_layout(True)
        #plt.tight_layout()

        return fig, ax

    # -------------------------------------------------------------------------
    # Properties describing fit results

    @property
    def fit_as_csv(self):
        """
        Return a csv-style string of the fit.
        """

        out = ["# Fit successful? {}\n".format(self.fit_success)]
        out.append("# Fit sum of square residuals: {}\n".format(self.fit_sum_of_squares))
        out.append("# Fit num param: {}\n".format(self.fit_num_param))
        out.append("# Fit num observations: {}\n".format(self.fit_num_obs))
        out.append("# Fit num degrees freedom: {}\n".format(self.fit_degrees_freedom))
        out.append("type,name,dh_file,value,uncertainty,fixed,guess,lower_bound,upper_bound\n") 
        for k in self.fit_param[0].keys():

            param_type = "global"
            dh_file = "NA"

            if self.global_param[k].fixed:
                fixed = "fixed"
            else:
                fixed = "float"

            param_name = k
            value = self.fit_param[0][k]
            uncertainty = self.fit_error[0][k]
            guess = self.global_param[k].guess
            lower_bound = self.global_param[k].bounds[0]
            upper_bound = self.global_param[k].bounds[1]

            out.append("{:},{:},{:},{:.5e},{:.5e},{:},{:.5e},{:.5e},{:.5e}\n".format(param_type,
                                                                                     param_name,
                                                                                     dh_file,
                                                                                     value,
                                                                                     uncertainty,
                                                                                     fixed,
                                                                                     guess,
                                                                                     lower_bound,
                                                                                     upper_bound))

        for i in range(len(self.fit_param[1])):

            expt_name = self._expt_list_stable_order[i]

            param_type = "local"
            dh_file = self._expt_dict[expt_name].dh_file

            for k in self.fit_param[1][i].keys():

                try:
                    alias = self._expt_dict[expt_name].model.parameters[k].alias
                    if alias != None:
                        continue
                except AttributeError:
                    pass

                if self._expt_dict[expt_name].model.parameters[k].fixed:
                    fixed = "fixed"
                else:
                    fixed = "float"

                param_name = k 
                value = self.fit_param[1][i][k]
                uncertainty = self.fit_error[1][i][k]
                guess = self._expt_dict[expt_name].model.parameters[k].guess
                lower_bound = self._expt_dict[expt_name].model.parameters[k].bounds[0]
                upper_bound = self._expt_dict[expt_name].model.parameters[k].bounds[1]

                out.append("{:},{:},{:},{:.5e},{:.5e},{:},{:.5e},{:.5e},{:.5e}\n".format(param_type,
                                                                                         param_name,
                                                                                         dh_file,
                                                                                         value,
                                                                                         uncertainty,
                                                                                         fixed,
                                                                                         guess,
                                                                                         lower_bound,
                                                                                         upper_bound))


        return "".join(out)
 

    @property
    def global_param(self):
        """
        Return all of the unique global parameters as FitParameter instances.
        """

        connectors_seen = []

        # Global parameters
        global_param = {}
        for g in self._global_param_keys:
            if type(g) == str:
                global_param[g] = self._global_params[g]
            else:
                if g.__self__ not in connectors_seen:
                    connectors_seen.append(g.__self__)
                    for p in g.__self__.params.keys():
                        global_param[p] = g.__self__.params[p]

        return global_param
                

    @property
    def fit_param(self):
        """
        Return the fit results as a dictionary that keys parameter name to fit
        value.  This is a tuple with global parameters first, then a list of
        dictionaries for each local fit.
        """

        # Global parameters
        global_out_param = {}
        for g in self.global_param.keys():
            global_out_param[g] = self.global_param[g].value

        # Local parameters
        local_out_param = []
        for expt_name in self._expt_list_stable_order:
            local_out_param.append(self._expt_dict[expt_name].model.param_values)

        return global_out_param, local_out_param

    @property
    def fit_error(self):
        """
        Return the param error as a dictionary that keys parameter name to fit
        value.  This is a tuple with global parameters first, then a list of
        dictionaries for each local fit.
        """

        # Global parameters
        global_out_error = {}
        for g in self.global_param.keys():
            global_out_error[g] = self.global_param[g].error

        # Local parameters
        local_out_error = []
        for expt_name in self._expt_list_stable_order:
            local_out_error.append(self._expt_dict[expt_name].model.param_errors)

        return global_out_error, local_out_error

    @property
    def fit_sum_of_squares(self):
        """
        Return fit sum_of_squares.
        """
        try:
            return self._fit_result.cost
        except AttributeError:
            return None

    @property
    def fit_success(self):
        """
        Return fit success.
        """
        try:
            return self._fit_result.success
        except AttributeError:
            return None

    @property
    def fit_status(self):
        """
        Return fit status.
        """
        try:
            return self._fit_result.status
        except AttributeError:
            return None


    @property
    def fit_num_obs(self):
        """
        Return the number of observations used for the fit.
        """

        try:
            # fun is fit residuals
            return len(self._fit_result.fun)
        except AttributeError:
            return None

    @property
    def fit_num_param(self):
        """
        Return the number of parameters fit.
        """

        # Global parameters
        num_param = 0
        for k in self.fit_param[0].keys():

            # Only count floating parameters
            if not self.global_param[k].fixed:
                num_param += 1

        # Local parameters
        for i in range(len(self.fit_param[1])):

            expt_name = self._expt_list_stable_order[i]
            for k in self.fit_param[1][i].keys():

                # Skip variables linked to global variables
                try:
                    alias = self._expt_dict[expt_name].model.parameters[k].alias
                    if alias != None:
                        continue
                except AttributeError:
                    pass
            
                # Only count floating parameters
                if not self._expt_dict[expt_name].model.parameters[k].fixed:
                    num_param += 1

        return num_param

    @property
    def fit_degrees_freedom(self):
        """
        Return the number of degrees of freedom from the fit. 
        """

        try:
            return self.fit_num_obs - self.fit_num_param 
        except AttributeError:
            return None

    # -------------------------------------------------------------------------
    # Properties describing currently loaded parameters and experiments

    @property
    def experiments(self):
        """
        Return a list of associated experiments.
        """

        out = []
        for expt_name in self._expt_list_stable_order:
            out.append(self._expt_dict[expt_name])

        return out

    #--------------------------------------------------------------------------
    # parameter names

    @property
    def param_names(self):
        """
        Return parameter names. This is a tuple of global names and then a list
        of parameter names for each experiment.
        """

        global_param_names = list(self.global_param.keys())

        final_param_names = []
        for expt_name in self._expt_list_stable_order:
            e = self._expt_dict[expt_name]

            param_names = copy.deepcopy(e.model.param_names)

            # Part of the global command names.
            for k in e.model.param_aliases.keys():
                param_names.remove(k)

            final_param_names.append(param_names)

        return global_param_names, final_param_names

    #--------------------------------------------------------------------------
    # parameter aliases

    @property
    def param_aliases(self):
        """
        Return the parameter aliases.  This is a tuple.  The first entry is a
        dictionary of gloal parameters mapping to experiment number; the second
        is a map between experiment number and global parameter names.
        """

        expt_to_global = []
        for expt_name in self._expt_list_stable_order:
            e = self._expt_dict[expt_name]
            expt_to_global.append(copy.deepcopy(e.model.param_aliases))

        return self._global_param_mapping, expt_to_global



    #--------------------------------------------------------------------------
    # parameter guesses

    @property
    def param_guesses(self):
        """
        Return parameter guesses. This is a tuple of global names and then a list
        of parameter guesses for each experiment.
        """

        global_param_guesses = {}
        for p in self.global_param.keys():
            global_param_guesses[p] = self.global_param[p].guess

        final_param_guesses = []
        for expt_name in self._expt_list_stable_order:
            e = self._expt_dict[expt_name]
            param_guesses = copy.deepcopy(e.model.param_guesses)

            for k in e.model.param_aliases.keys():
                param_guesses.pop(k)

            final_param_guesses.append(param_guesses)

        return global_param_guesses, final_param_guesses

    def update_guess(self,param_name,param_guess,expt=None):
        """
        Update the one of the guesses for this fit.  If the experiment is None,
        set a global parameter.  Otherwise, set the specified experiment.

            param_name: name of parameter to set
            param_guess: value to set parameter to
            expt_name: name of experiment
        """

        if expt == None:
            try:
                self.global_param[param_name].guess = param_guess
            except KeyError:
                err = "param \"{}\" is not global.  You must specify an experiment.\n".format(param_name)
                raise KeyError(err)
        else:
            self._expt_dict[expt.experiment_id].model.update_guesses({param_name:param_guess})

    #--------------------------------------------------------------------------
    # parameter ranges

    @property
    def param_ranges(self):
        """
        Return the parameter ranges for each fit parameter. This is a tuple.
        Global parameters are first, a list of local parameter ranges are next.
        """

        global_param_ranges = {}
        for p in self.global_param.keys():
            global_param_ranges[p] = self.global_param[p].guess_range

        final_param_ranges = []
        for expt_name in self._expt_list_stable_order:
            e = self._expt_dict[expt_name]
            param_ranges = copy.deepcopy(e.model.param_guess_ranges)

            for k in e.model.param_aliases.keys():
                param_ranges.pop(k)

            final_param_ranges.append(param_ranges)


        return global_param_ranges, final_param_ranges

    def update_range(self,param_name,param_range,expt=None):
        """
        Update the range of a parameter for this fit.  If the experiment is None,
        set a global parameter.  Otherwise, set the specified experiment.

            param_name: name of parameter to set
            param_guess: value to set parameter to
            expt_name: name of experiment
        """

        try:
            if len(param_range) != 2:
                raise TypeError
        except TypeError:
            err = "Parameter range must be a list or tuple of length 2"
            raise TypeError(err)

        if expt == None:
            try:
                self.global_param[param_name].guess_range = param_range
            except KeyError:
                err = "param \"{}\" is not global.  You must specify an experiment.\n".format(param_name)
                raise KeyError(err)
        else:
            self._expt_dict[expt.experiment_id].model.update_ranges({param_name:param_range})

    #--------------------------------------------------------------------------
    # fixed parameters

    @property
    def fixed_param(self):
        """
        Return the fixed parameters of the fit.  This is a tuple,  Global fixed
        parameters are first, a list of local fixed parameters is next.
        """

        global_fixed_param = {}
        for p in self.global_param.keys():
            global_fixed_param[p] = self._global_params[p].fixed

        final_fixed_param = []
        for expt_name in self._expt_list_stable_order:

            e = self._expt_dict[expt_name]

            fixed_param = copy.deepcopy(e.model.fixed_param)

            for k in e.model.param_aliases.keys():
                try:
                    fixed_param.pop(k)
                except KeyError:
                    pass

            final_fixed_param.append(fixed_param)

        return global_fixed_param, final_fixed_param

    def update_fixed(self,param_name,param_value,expt=None):
        """
        Fix fit parameters.  If expt is None, set a global parameter. Otherwise,
        fix individual experiment parameters.  
            param_name: name of parameter to set
            param_guess: value to set parameter to
            expt_name: name of experiment

            if param_value is set to None, fixed value is removed.

        """

        if expt == None:
            try:
                if param_value == None:
                    self.global_param[param_name].fixed = False
                else:
                    self.global_param[param_name].fixed = True
                    self.global_param[param_name].value = param_value
            except KeyError:
                err = "param \"{}\" is not global.  You must specify an experiment.\n".format(param_name)
                raise KeyError(err)

        else:
            self._expt_dict[expt.experiment_id].model.update_fixed({param_name:param_value})


    #--------------------------------------------------------------------------
    # parameter bounds

    @property
    def param_bounds(self):
        """
        Return the parameter bounds for each fit parameter. This is a tuple.
        Global parameters are first, a list of local parameter ranges are next.
        """

        global_param_bounds = {}
        for p in self.global_param.keys():
            global_param_bounds[p] = copy.deepcopy(self.global_param[p].bounds)

        final_param_bounds = []
        for expt_name in self._expt_list_stable_order:
            e = self._expt_dict[expt_name]
            param_bounds = copy.deepcopy(e.model.bounds)

            for k in e.model.param_aliases.keys():
                param_bounds.pop(k)

            final_param_bounds.append(param_bounds)


        return global_param_bounds, final_param_bounds

    def update_bounds(self,param_name,param_bounds,expt=None):
        """
        Update the bounds of a parameter for this fit.  If the experiment is None,
        set a global parameter.  Otherwise, set the specified experiment.

            param_name: name of parameter to set
            param_bounds value to set parameter to
            expt_name: name of experiment
        """

        try:
            if len(param_bounds) != 2:
                raise TypeError
        except TypeError:
            err = "Parameter bounds must be a list or tuple of length 2"
            raise TypeError(err)

        if expt == None:
            try:
                self.global_param[param_name].bounds = param_bounds
            except KeyError:
                err = "param \"{}\" is not global.  You must specify an experiment.\n".format(param_name)
                raise KeyError(err)
        else:
            self._expt_dict[expt.experiment_id].model.update_bounds({param_name:param_bounds})


    #--------------------------------------------------------------------------
    # Functions for updating values directly (used in gui)

    def guess_to_value(self):
        """
        Set all parameter values back to their guesses.
        """       
 
        for p in self.global_param.keys():
            self.global_param[p].value = self.global_param[p].guess

        for expt_name in self._expt_list_stable_order:
            for n, p in self._expt_dict[expt_name].model.parameters.items():
                p.value = p.guess

    def update_value(self,param_name,param_value,expt=None):
        """
        Update the one of the values for this fit.  If the experiment is None,
        set a global parameter.  Otherwise, set the specified experiment.

            param_name: name of parameter to set
            param_value: value to set parameter to
            expt_name: name of experiment
        """

        if expt == None:
            try:
                self.global_param[param_name].value = param_value
            except KeyError:
                err = "param \"{}\" is not global.  You must specify an experiment.\n".format(param_name)
                raise KeyError(err)
        else:
            self._expt_dict[expt.experiment_id].model.update_values({param_name:param_value})

