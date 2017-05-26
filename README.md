# pytc
A python software package for analyzing Isothermal Titration Calorimetry
experiments.  Does Bayesian and ML fitting.  Performs global fits to 
multiple experiments.  Has a clean Python API. Designed for easy extension
with new models.

 + [Full documentation](https://pytc.readthedocs.io/en/latest/)
 + [Graphical User Interface](https://github.com/harmslab/pytc-gui)

## Quick Start
 + Install via pip `sudo pip3 install pytc-fitter` (Mac/Linux), `python3 -m pip install pytc-fitter` (Windows)
 + Alternatively, clone from github and install 
    ```
    git clone https://github.com/harmslab/pytc.git
    cd pytc
    python3 setup.py install
    ```
 + If jupyter is installed, you can clone the [pytc-demos](https://github.com/harmslab/pytc-demos)
   repo to see a collection of example fits.

## Example script
Fit a Ca2+/EDTA binding experiment.

```Python
import pytc

# Load in integrated heats from an ITC experiment
e = pytc.ITCExperiment("pytc-demos/ca-edta/tris-01.DH",pytc.indiv_models.SingleSite)

# Create the global fitter, add the experiment, and fit
g = pytc.GlobalFit()
g.add_experiment(e)
g.fit()

# Print the results out
g.plot()
g.corner_plot()
print(g.fit_as_csv)
```

## Release Notes

### v1.0
Initial release of pytc.  Implemented individual and global fits.   
