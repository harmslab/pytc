__description__ = 
"""
Basic functions for manipulating fits.
"""
__author__ = "Michael J. Harms"
__date__ = "2017-01-28"

import numpy as np

def weight_stat(test_stats):
    """
    Return weights for test statistics. 
    """  

    test_stats = np.arrary(test_stats)
    w = np.exp(-test_stats/2)
    weights = w/np.sum(w)

    best_value = np.amax(weights)
    best_index = np.argmax(weights)

    return best_index, weights

def compare_models(*models):
    """
    Weight GlobalFits relative to each other using their AIC, AICc, and BIC
    values.

    Parameters:
        *models : one more more GlobalFit instances

    **NOTE**: This comparison is only valid if the models all fit the  same
    set of observations.  The models do not need to be nested.
    """

    aic = []
    aic_c = []
    bic = []

    for i, m in enumerate(models):
        if not m.success:
            print("Fitting model {}".format(i))
            m.fit()
        
        aic.append(m.fit_stats["AIC"])       
        aic_c.append(m.fit_stats["AICc"])       
        bic.append(m.fit_stats["BIC"])       

    out = {}
    
    out["AIC"]  = weight_stat(aic)
    out["AICc"] = weight_stat(aic_c)
    out["BIC"]  = weight_stat(bic)
   
    return out 


