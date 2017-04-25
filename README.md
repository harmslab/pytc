# pytc
A python software package for analyzing Isothermal Titration Calorimetry
experiments.

 + [Documentation](https://pytc.readthedocs.io/en/latest/)
 + [Graphical User Interface](https://github.com/harmslab/pytc-gui)
 + Try it out: [![Binder](http://mybinder.org/badge.svg)](http://mybinder.org:/repo/harmslab/pytc-binder)

## Quick Start
 + Install via pip `sudo python3 install pytc-fitter` (Mac/Linux), `python3 -m pip install pytc-fitter` (Windows)
 + Alternatively, clone from github and install 
    ```
    git clone https://github.com/harmslab/pytc.git
    cd pytc
    python3 setup.py install
    ```
 + If jupyter is installed, you can open the `demos/Demo.ipynb` jupyter notebook to see a collection of example fits. 

## Example script
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
