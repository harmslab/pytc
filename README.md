#pytc
A python software package for analyzing Isothermal Titration Calorimetry data
(Python + ITC --> pytc).  

See the `model-documention.ipynb` jupyter notebook for full descriptions of models.

##Quick Start
Open the `template.ipynb` jupyter notebook for an example fit.

```Python
import pytc

# Load in integrated heats from an ITC experiment
e = pytc.ITCExperiment("demos/ca-edta/hepes-01.DH",pytc.indiv_models.SingleSite)

# Create the global fitter, add the experiment, and fit
g = pytc.GlobalFit()
g.add_experiment(e)
g.fit()

# Print the results out
print(g.fit_as_csv)
```

```
e = pytc.ITCExperiment("demos/ca-edta/hepes-01.DH",pytc.indiv_models.SingleSite)

g.add_experiment(e)

g.update_bounds("K",(-np.inf,np.inf),e)
g.update_guess("K",1,e)
g.update_fixed("K",1,e)
```


##Fitting

####Fit parameters

* Parameters passed as `param_guesses` to `GlobalFit` will be fit to the data.

* Parameters can have any names and can be passed to any itc model.  To specify
  how the global parameters map to a given itc experiment, specify an `arg_map`
  when adding an experiment to the fitter. If no `arg_map` is specified, the 
  fitter will pass the global parameter names straight to the local fitting
  model.  This works fine if the global parameters have the same name as the
  local model parameters (e.g. the global parameter is `K` and the local model
  expects an argument called `K`).

* Parameters can be fixed in three ways:
  + passing a `fixed_param` dictionary to `GlobalFit` when initalized.  This will 
    fix the parameter for all experiments and will supercede the `param_guesses`
    values.
  + passing a `fixed_param` dictionary to the `GlobalFit.add_experiment` method. 
    This will fix the parameter, but only for that experiment.
  + "nuisance" parameters (e.g. competent fraction) have natural default
    values (e.g. 1.0 for competent fraction) that are specified in the models
    `dQ` method.  These defaults will be used and fixed unless these parameters 
    are specifically floated.

##Model API specifications

Models should:
* ... be subclasses of ITCModel
* ... expose a `mole_ratio` property (taken care of by ITCModel)
* ... expose a `dQ` method that takes a set of model parameters as arguments
  and returns change-in-heat for each shot.  
* ... specify no default values for thermodynamic parameters and sane default
  values for nuisance parameters.  For example, the binding constant `K` should
  have no default, while the dilution correction `dilution_heat` should default
  to 0.0 (no correction).  This design forces a user to pass guesses or fixed
  values for the thermodynamic parameters, while allowing them to ignore
  nuisance parameters unless they specifically want to fit them.
