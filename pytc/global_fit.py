__description__ = \
"""
global_fit.py

Main class that user interacts with when fitting with pytc.
"""
__author__ = "Michael J. Harms"
__date__ = "2016-06-22"

from . global_connectors import GlobalConnector
from . import fitters, mapper

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec

import inspect

class GlobalFit:

    def __init__(self):
        """
        Set up the main binding model to fit.
        """

        self._mapper = mapper.Mapper()


    def fit(self,fitter=fitters.MLFitter):
        """
        Public fitting function that fits the data.
        """

        self._prep_fit()
       
        # If the fitter is not intialized, initialize it 
        if inspect.isclass(fitter):
            self._fitter = fitter()
        else:
            self._fitter = fitter

        self._fitter = fitter()
        self._fitter.fit(self._mapper,
                         self._residuals,
                         self._float_param,
                         self._float_bounds)
        print(self._fitter.stats)
        self._parse_fit()

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
            N = len(self._mapper.expt_names)
            color_list = [plt.cm.brg(i/N) for i in range(N)]

        if len(color_list) < len(self._mapper.expt_names):
            err = "Number of specified colors is less than number of experiments.\n"
            raise ValueError(err)

        for i, expt_name in enumerate(self._mapper.expt_names):

            e = self._mapper.expt_dict[expt_name]

            mr = e.mole_ratio
            heats = e.heats
            calc = self._mapper.expt_dict[expt_name].dQ

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

        return fig, ax

    # -------------------------------------------------------------------------
    # Properties describing fit results

    @property
    def fit_as_csv(self):
        """
        Return a csv-style string of the fit.
        """

        out = ["# Fit successful? {}\n".format(self._fitter.success)]
        
        self._fitter.stats_keys = list(self._fitter.stats.keys())
        self._fitter.stats_keys.sort()
    
        for k in self._fitter.stats_keys:
            out.append("# {}: {}\n".format(k,self._fitter.stats[k]))

        out.append("type,name,dh_file,value,uncertainty,fixed,guess,lower_bound,upper_bound\n") 
        for k in self.fit_param[0].keys():

            param_type = "global"
            dh_file = "NA"

            if self.global_params[k].fixed:
                fixed = "fixed"
            else:
                fixed = "float"

            param_name = k
            value = self.fit_param[0][k]
            uncertainty = self.fit_stdev[0][k]
            guess = self.global_params[k].guess
            lower_bound = self.global_params[k].bounds[0]
            upper_bound = self.global_params[k].bounds[1]

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

            expt_name = self._mapper.expt_names[i]

            param_type = "local"
            dh_file = self._mapper.expt_dict[expt_name].dh_file

            for k in self.fit_param[1][i].keys():

                try:
                    alias = self._mapper.expt_dict[expt_name].model.parameters[k].alias
                    if alias != None:
                        continue
                except AttributeError:
                    pass

                if self._mapper.expt_dict[expt_name].model.parameters[k].fixed:
                    fixed = "fixed"
                else:
                    fixed = "float"

                param_name = k 
                value = self.fit_param[1][i][k]
                uncertainty = self.fit_stdev[1][i][k]
                guess = self._mapper.expt_dict[expt_name].model.parameters[k].guess
                lower_bound = self._mapper.expt_dict[expt_name].model.parameters[k].bounds[0]
                upper_bound = self._mapper.expt_dict[expt_name].model.parameters[k].bounds[1]

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
    def fit_param(self):
        """
        Return the fit results as a dictionary that keys parameter name to fit
        value.  This is a tuple with global parameters first, then a list of
        dictionaries for each local fit.
        """

        # Global parameters
        global_out_param = {}
        for g in self.global_params.keys():
            global_out_param[g] = self.global_params[g].value

        # Local parameters
        local_out_param = []
        for expt_name in self._mapper.expt_names:
            local_out_param.append(self._mapper.expt_dict[expt_name].model.param_values)

        return global_out_param, local_out_param

    @property
    def fit_stdev(self):
        """
        Return the param error as a dictionary that keys parameter name to fit
        value.  This is a tuple with global parameters first, then a list of
        dictionaries for each local fit.
        """

        # Global parameters
        global_out_error = {}
        for g in self.global_params.keys():
            global_out_error[g] = self.global_params[g].error

        # Local parameters
        local_out_error = []
        for expt_name in self._mapper.expt_names:
            local_out_error.append(self._mapper.expt_dict[expt_name].model.param_errors)

        return global_out_error, local_out_error

    
    def _prep_fit(self):
        """
        Prep the fit, creating all appropriate parameter mappings etc.
        """

        self._float_param = []
        self._float_bounds = [[],[]]
        self._float_param_mapping = []
        self._float_param_type = []

        self._float_global_connectors_seen = []

        float_param_counter = 0

        # Go through global variables
        for k in self._mapper.global_param_mapping.keys():
      
            # Otherwise, there is just one parameter to enumerate over.
            if type(k) == str:
                enumerate_over = {k:self._mapper.global_params[k]}
                param_type = 1
 
            # If this is a global connector, enumerate over all parameters in
            # that connector 
            elif issubclass(k.__self__.__class__,GlobalConnector):

                # Only load each global connector in once
                if k in self._float_global_connectors_seen:
                    continue

                enumerate_over = self._mapper.global_params_internal[k].params
                self._float_global_connectors_seen.append(k)
                param_type = 2

            else:
                err = "global variable class not recongized.\n"
                raise ValueError(err)
            
            # Now update parameter values, bounds, and mapping 
            for e in enumerate_over.keys(): 

                # write fixed parameter values to the appropriate experiment,
                # then skip
                if enumerate_over[e].fixed:
                    fixed_value = enumerate_over[e].value
                    for expt, expt_param in self._mapper.global_param_mapping[k]:
                        self._mapper.expt_dict[expt].model.update_fixed({expt_param:fixed_value}) 
                    continue

                self._float_param.append(enumerate_over[e].guess)
                self._float_bounds[0].append(enumerate_over[e].bounds[0])
                self._float_bounds[1].append(enumerate_over[e].bounds[1])
                self._float_param_mapping.append((k,e))
                self._float_param_type.append(param_type)

                float_param_counter += 1

        # Go through every experiment
        for k in self._mapper.expt_dict.keys():                                       

            # Go through fit parameters within each experiment
            e = self._mapper.expt_dict[k]                                             
            for p in e.model.param_names:

                # If the parameter is fixed, ignore it.
                if e.model.fixed_param[p]:
                    continue

                # If the parameter is global, ignore it.
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
                self._mapper.expt_dict[experiment].model.update_values({parameter_name:param[i]})    

            # Vanilla global variable
            elif self._float_param_type[i] == 1:
                param_key = self._float_param_mapping[i][0]
                for experiment, parameter_name in self._mapper.global_param_mapping[param_key]:
                    self._mapper.expt_dict[experiment].model.update_values({parameter_name:param[i]}) 

            # Global connector global variable
            elif self._float_param_type[i] == 2:
                connector = self._float_param_mapping[i][0].__self__
                param_name = self._float_param_mapping[i][1]
                connector.update_values({param_name:param[i]})

            else:
                err = "Paramter type {} not recongized.\n".format(self._float_param_type[i])
                raise ValueError(err) 

        # Look for connector functions
        for connector_function in self._mapper.global_param_keys:            

            if type(connector_function) == str:
                continue

            # If this is a method of GlobalConnector...
            if issubclass(connector_function.__self__.__class__,GlobalConnector):

                # Update experiments with the value spit out by the connector function
                for expt, param in self._mapper.global_param_mapping[connector_function]: 
                    e = self._mapper.expt_dict[expt]                                                 
                    value = connector_function(e)
                    self._mapper.expt_dict[expt].model.update_values({param:value})                  
                 
        # Calculate residuals
        for k in self._mapper.expt_dict.keys():                                                       
            all_residuals.extend(self._mapper.expt_weights[k]*(self._mapper.expt_dict[k].heats - self._mapper.expt_dict[k].dQ))

        return np.array(all_residuals)

        
    def _parse_fit(self):
        """
        Parse the fit results.
        """

        # Store the result
        for i in range(len(self._fitter.estimate)):
                
            # local variable
            if self._float_param_type[i] == 0:

                experiment = self._float_param_mapping[i][0]
                parameter_name = self._float_param_mapping[i][1]

                self._mapper.expt_dict[experiment].model.update_values({parameter_name:self._fitter.estimate[i]})
                self._mapper.expt_dict[experiment].model.update_errors({parameter_name:self._fitter.stdev[i]})

            # Vanilla global variable
            elif self._float_param_type[i] == 1:

                param_key = self._float_param_mapping[i][0]
                for k, p in self._mapper.global_param_mapping[param_key]:
                    self._mapper.expt_dict[k].model.update_values({p:self._fitter.estimate[i]})
                    self._mapper.global_params[param_key].value = self._fitter.estimate[i]
                    self._mapper.global_params[param_key].error = self._fitter.stdev[i]

            # Global connector global variable
            elif self._float_param_type[i] == 2:
                connector = self._float_param_mapping[i][0].__self__
                param_name = self._float_param_mapping[i][1]

                # HACK: if you use the params[param_name].value setter function,
                # it will break the connector.  This is because I expose the 
                # thermodynamic-y stuff of interest via .__dict__ rather than 
                # directly via params.  So, this has to use the .update_values
                # method. 
                connector.update_values({param_name:self._fitter.stdev[i]})
                connector.params[param_name].error = self._fitter.stdev[i]

            else:
                err = "Paramter type {} not recognized.\n".format(self._float_param_type[i])
                raise ValueError(err) 
    
    # ----------------------------------------------------------------------- #
    # To keep the global_fit api clean, wrap the key self._mapper methods and #
    # properties ane expose them here.                                        #
    # ----------------------------------------------------------------------- #
    
    def add_experiment(self,experiment,weight=1.0):
        """
        experiment: an initialized ITCExperiment instance
        weight: how much to weight this experiment in the regression relative to other
                experiments.  Values <1.0 weight this experiment less than others;
                values >1.0 weight this more than others.
        """
        
        self._mapper.add_experiment(experiment,weight)

    def remove_experiment(self,experiment):
        """
        Remove an experiment from the analysis.
        """

        self._mapper.remove_experiment(experiment)

    def link_to_global(self,expt,expt_param,global_param_name):
        """
        Link a local experimental fitting parameter to a global fitting
        parameter.
        """

        self._mapper.link_to_global(expt,expt_param,global_param_name)

    def unlink_from_global(self,expt,expt_param):
        """
        Remove the link between a local fitting parameter and a global
        fitting parameter.
        """

        self._mapper.unlink_from_global(expt,expt_param)

    def remove_global(self,global_param_name):
        """
        Remove a global parameter, unlinking all local parameters.
        """

        self._mapper.remove_global(global_param_name)

    @property
    def experiments(self):
        return self._mapper.experiments

    @property
    def param_names(self):
        return self._mapper.param_names

    @property
    def param_aliases(self):
        return self._mapper.param_aliases

    @property
    def param_guesses(self):
        return self._mapper.param_guesses

    def update_guess(self,*args,**kwargs):
        self._mapper.update_guess(*args,**kwargs)

    @property
    def param_ranges(self):
        return self._mapper.param_ranges

    def update_range(self,*args,**kwargs):
        self._mapper.update_range(*args,**kwargs)

    @property
    def fixed_param(self):
        return self._mapper.fixed_param

    def update_fixed(self,*args,**kwargs):
        self._mapper.update_fixed(*args,**kwargs)

    @property
    def param_bounds(self):
        return self._mapper.param_bounds

    def update_bounds(self,*args,**kwargs):
        self._mapper.update_bounds(*args,**kwargs)

    def guess_to_value(self):
        self._mapper.guess_to_value()
 
    def update_value(self,*args,**kwargs):
        self._mapper.update_value(*args,**kwargs)

    @property
    def global_params(self):
        return self._mapper.global_params
