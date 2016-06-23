#pytc
A python software package for analyzing Isothermal Titration Calorimetry data
(python + ITC --> pytc).  

See the Documentation.ipynb jupyter notebook for full descriptions of models.


##Quick Start
```Python
import pytc

# Set up the global fit with parameter guesses
fitter = pytc.GlobalFit({"K":1e6,"dH":-2000,"fx_competent":1.0,"dilution_heat":0.0})

# Load experimental data, defining input data and fitting model
e1 = pytc.ITCExperiment("test-data/hA5A5conTESCaTCEP.DH",pytc.models.SingleSite)

# Associate the model with the fit
fitter.add_experiment(e1)

# Do the global fit
fitter.fit()

# Plot the fit
fitter.plot()

# Print out the final fit parameters
print(fitter.fit_param)
```

###Notes

####Fixing fit parameters

Only parameters passed as `param_guesses` to `GlobalFit` will be fit to the data.

Some fit parameters have natural default values that are specified in the dQ method
for each model.  For example, the `fx_competent` parameter is a nuisance parameter
that accounts for a mismatch between the intended and actual concentrations of
species in the titrant cell.  The default is to fix this value at 1.0
