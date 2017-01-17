#pytc
A python software package for analyzing Isothermal Titration Calorimetry data
(Python + ITC --> pytc).  

## Quick Start
 + Clone the repository with `git clone https://github.com/harmslab/pytc.git`
 + Open the `Demo.ipynb` jupyter notebook to see a collection of example fits. 

### Example script

Fit a Ca2+/EDTA binding experiment.

```Python
import pytc

# Load in integrated heats from an ITC experiment
e = pytc.ITCExperiment("demos/ca-edta/tris-01.DH",pytc.indiv_models.SingleSite)

# Create the global fitter, add the experiment, and fit
g = pytc.GlobalFit()
g.add_experiment(e)
g.fit()

# Print the results out
g.plot()
print(g.fit_as_csv)
```

##Fitting


##Model API specifications

### Individual models

These models describe a single ITC experiment.  They are passed to 
`pytc.ITCExperiment` along with an appropriate ITC heats file to analyze that
individual experiment.

These models should:
* Be subclasses of `pytc.indiv_models.base.ITCModel`
* Define a new `__init__` function that uses the contents of the syringe and
  titrant and calculates how the total concentrations of various species change
  over the titration.
* Expose a `dQ` property that gives the heat change per shot.
* Define a `initialize_param` method with all fittable parameters as
  arguments.  Each paramter should have a default value that is a reasonable
  guess for that parameters.

See `pytc/indiv_models/single_site.py` for a simple example.

See the `model-documention.ipynb` jupyter notebook for full descriptions of
the currently-implemented models.

### Global models

These models describe relationships between multiple ITC experiments.  They
should be subclasses of `pytc.global_models.base.GlobalModel`. The exact 
implementation of these models depends on the relationships being probed.  
At a minimum this will probably require:
* Define `__init__` to add any global parameters unique to the global
  fit (e.g. heat-capacity for a temperature-dependent titration).
* Define `_residuals`, which calculates the (mis)match between the model and all
  loaded data.
* Define `fit`, which manages the global variables
* Define `_get_calc_heats`.  

See `pytc/global_models/temp_dependence.py` for a (relatively) simple example.
