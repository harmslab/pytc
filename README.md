#pytc
A python software package for analyzing Isothermal Titration Calorimetry data
(python + ITC --> pytc).  

See the Documentation.ipynb jupyter notebook for full descriptions of models.

##Quick Start
```Python
import pytc

# Set up the global fit with parameter guesses
fitter = pytc.GlobalFit({"K1":1e6,"dH1":-2000,"fx1":1.0,"dil1":0.0})

# Load in an experiment, defining input data and fitting model
e1 = pytc.ITCExperiment("test-data/hA5A5conTESCaTCEP.DH",pytc.models.SingleSite)

# Associate the global K1 parameter with the local K parameter, etc.
fitter.add_experiment(e1,{"K1":"K",
                          "dH1":"dH",
                          "fx1":"fx_competent",
                          "dil1":"dilution_heat"})

# Do the global fit
fitter.fit()

# Plot the fit
fitter.plot()

# Print out the final fit parameters
print(fitter.fit_param)
```
