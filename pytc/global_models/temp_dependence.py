__description__ = \
"""
proton_linked.py

"""
__author__ = "Michael J. Harms"
__date__ = "2016-10-12"

import numpy as np
import scipy.optimize as optimize
from matplotlib import pyplot as plt
import copy

from .. import fit_param
from .base import GlobalFit

class TempDependence(GlobalFit):
    """
    """

    def __init__(self):
        """
        Set up the main binding model to fit.
        """

        super(TempDependence, self).__init__()

        # dCp will be the first parameter (param[0])
        self._global_param_names.append("dCp")
        self._global_params["dCp"] = fit_param.FitParameter("dCp",guess=0.0)

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

                # param[0] is heat capacity (slope vs. temperature)
                if p.startswith("dH"):
                    value_to_pass = param[i] + param[0]*self._expt_dict[k].temperature
                else:
                    value_to_pass = param[i]

                self._expt_dict[k].model.update_values({p:value_to_pass})

            else:
                for k, p in self._global_param_mapping[param_key]:
            
                    # param[0] is heat capacity (slope vs. temperature)
                    if p.startswith("dH"):
                        value_to_pass = param[i] + param[0]*self._expt_dict[k].temperature
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

        self._float_param = [self._global_params["dCp"].value]
        self._float_bounds = [[self._global_params["dCp"].bounds[0]],
                              [self._global_params["dCp"].bounds[1]]]
        self._float_param_mapping = ["dCp"]
        float_param_counter = 1

        # Go through global variables
        for k in self._global_param_mapping.keys():
            
            if k == "dCp":
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
        self._fit_result = optimize.least_squares(self._residuals, x0=self._float_param,bounds=self._float_bounds)
        fit = self._fit_result
        fit_parameters = fit.x

        # Determine the covariance matrix (Jacobian * residual variance)
        pcov = fit.jac*(np.sum(fit.fun**2)/(len(fit.fun)-len(fit.x)))

        # Estimates of parameter uncertainty
        error = np.absolute(np.diagonal(pcov))**0.5

        # Store the result
        self._global_params["dCp"].value = fit_parameters[0]
        self._global_params["dCp"].error = error[0]
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

    def _get_calc_heats(self,expt_name):
        """
        Spit calculated heats, accounting for proton titration bit.
        """

        e = copy.copy(self._expt_dict[expt_name])
        for p in e.model.parameters:
            if p.startswith("dH"):
                v = e.model.param_values[p]
                new_dH = v + self._global_params["dCp"].value*e.temperature
                e.model.update_values({p:new_dH})

        return e.dQ

