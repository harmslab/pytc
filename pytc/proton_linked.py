__description__ = \
"""
proton_linked.py

"""
__author__ = "Michael J. Harms"
__date__ = "2016-10-12"

import numpy as np
import scipy.optimize as optimize
from . import fitting, fit_param
from matplotlib import pyplot as plt
import copy

class ProtonLinked(fitting.GlobalFit):
    """
    """

    def __init__(self):
        """
        Set up the main binding model to fit.
        """

        super(ProtonLinked, self).__init__()

        self._expt_ionization_enthalpy = {}
        self._global_param_names.append("num_protons")
        self._global_params["num_protons"] = fit_param.FitParameter("num_protons",guess=0.0)

    def add_experiment(self,experiment,ionization_enthalpy,param_guesses=None,
                       fixed_param=None,param_aliases=None,weight=1.0):
        """
        experiment: an initialized ITCExperiment instance
        ionization_enthalpy: ionization enthalpy for this buffer
        param_guesses: a dictionary of parameter guesses (need not be complete)
        fixed_param: a dictionary of parameters to be fixed, with value being
                     fixed_value.
        param_aliases: dictionary keying local experiment parameters to global
                       parameters.
        weight: how much to weight this experiment in the regression relative to other
                experiments.  Values <1.0 weight this experiment less than others;
                values >1.0 weight this more than others.
        """

        super(ProtonLinked, self).add_experiment(experiment,
                                                 param_guesses,fixed_param,
                                                 param_aliases,weight)
        self._expt_ionization_enthalpy[experiment.experiment_id] = ionization_enthalpy

    def remove_experiment(self,experiment):
        """
        Remove an experiment from the analysis.
        """

        super(ProtonLinked,self).remove_experiment(experiment)
        self._expt_ionization_enthalpy.pop(expt_name)

    def _residuals(self,param=None):
        """
        Calculate the residuals between the experiment and calculated model
        heats.
        """

        all_residuals = []

        for i in range(1,len(param)):
            param_key = self._float_param_mapping[i]

            if type(param_key) == tuple and len(param_key) == 2:
                k = param_key[0]
                p = param_key[1]

                # add offset to enthalpy
                if p.startswith("dH"):
                    value_to_pass = param[i] + param[0]*self._expt_ionization_enthalpy[k]
                else:
                    value_to_pass = param[i]

                self._expt_dict[k].model.update_values({p:value_to_pass})
            else:
                for k, p in self._global_param_mapping[param_key]:
            
                    # add offset to enthalpy
                    if p.startswith("dH"):
                        value_to_pass = param[i] + param[0]*self._expt_ionization_enthalpy[k]
                    else:
                        value_to_pass = param[i]

                    self._expt_dict[k].model.update_values({p:value_to_pass})


        for k in self._expt_dict.keys():
            all_residuals.extend(self._expt_weights[k]*(self._expt_dict[k].heats - self._expt_dict[k].dQ))

        return np.array(all_residuals)


    def fit(self):
        """
        Perform a global fit using nonlinear regression.
        """

        self._float_param = [self._global_params["num_protons"].value]
        self._float_bounds = [[self._global_params["num_protons"].bounds[0]],
                              [self._global_params["num_protons"].bounds[1]]]
        self._float_param_mapping = ["num_protons"]
        float_param_counter = 1

        # Go through global variables
        for k in self._global_param_mapping.keys():
            
            if k == "num_protons":
                continue

            self._float_param.append(self._global_params[k].guess)
            self._float_bounds[0].append(self._global_params[k].bounds[0])
            self._float_bounds[1].append(self._global_params[k].bounds[1])
            self._float_param_mapping.append(k)
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

                float_param_counter += 1

        self._float_param = np.array(self._float_param,dtype=float)

        # Do the actual fit
        fit = optimize.least_squares(self._residuals, x0=self._float_param,bounds=self._float_bounds)
        fit_parameters = fit.x

        # Determine the covariance matrix (Jacobian * residual variance)
        pcov = fit.jac*(np.sum(fit.fun**2)/(len(fit.fun)-len(fit.x)))

        # Estimates of parameter uncertainty
        error = np.absolute(np.diagonal(pcov))**0.5

        # Store the result
        self._global_params["num_protons"].value = fit_parameters[0]
        self._global_params["num_protons"].error = error[0]
        for i in range(1,len(fit_parameters)):
            param_key = self._float_param_mapping[i]
            if len(param_key) == 2:
                k = param_key[0]
                p = param_key[1]
                self._expt_dict[k].model.update_values({p:fit_parameters[i]})
                self._expt_dict[k].model.update_errors({p:error[i]})
            else:
                for k, p in self._global_param_mapping[param_key]:
                    self._expt_dict[k].model.update_values({p:fit_parameters[i]})
                    self._global_params[param_key].value = fit_parameters[i]
                    self._global_params[param_key].error = error[i]

    def plot(self,color_list=None,correct_molar_ratio=False,subtract_dilution=False):
        """
        Plot the experimental data and fit results.
        """

        if color_list == None:
            N = len(self._expt_list_stable_order)
            color_list = [plt.cm.brg(i/N) for i in range(N)]

        if len(color_list) < len(self._expt_list_stable_order):
            err = "Number of specified colors is less than number of experiments.\n"
            raise ValueError(err)

        for i, expt_name in enumerate(self._expt_list_stable_order):

            e = copy.copy(self._expt_dict[expt_name])
            for p in e.model.parameters:
                if p.startswith("dH"):
                    v = e.model.param_values[p]
                    e.model.update_values({p:v + self._global_params["num_protons"].value*self._expt_ionization_enthalpy[expt_name]})
            mr = e.mole_ratio
            heats = e.heats
            calc = e.dQ

            if e.dQ != None:

                # Try to correct molar ratio for competent fraction
                if correct_molar_ratio:
                    try:
                        mr = mr/e.param_values["fx_competent"]
                    except KeyError:
                        pass

                    if subtract_dilution:
                        heats = heats - e.dilution_heats
                        calc = calc - e.dilution_heats

            plt.plot(mr,heats,"o",color=color_list[i])

            if e.dQ != None:
                plt.plot(mr,calc,color=color_list[i],linewidth=1.5)
