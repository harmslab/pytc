import scipy
from scipy import stats
import numpy as np

def _simple_compare(m1,m2,key):
    """
    Likelihood tests.
    """  
 
    m1_w = np.exp(-m1[key]/2)
    m2_w = np.exp(-m2[key]/2)

    weight = m1_w/(m1_w + m2_w)
 
    if m1[key] < m2[key]:
        status = True
        print("{}: model 1 one favored over model 2 (weight = {:.3e})".format(key,weight))
    else:
        status = False
        print("{}: model 2 one favored over model 1 (weight = {:.3e})".format(key,1-weight))

    return status, weight

def choose_model(model1,model2):
    """
    Compare two models and test which is better supported using an AIC, AICc,
    and BIC test.
    """

    if model1.fit_sum_of_squares == None:
        print("Fitting model 1.")
        model1.fit()
    else:
        print("Using fit already done for model 1.")

    #model1.plot()
    print("")
    print("Model 1 fit")
    print(model1.fit_as_csv)
    print("")

    if model2.fit_sum_of_squares == None:
        print("Fitting model 2.")
        model2.fit()
    else:
        print("Using fit already done for model 2.")

    #model2.plot()
    print("")
    print("Model 2 fit")
    print(model2.fit_as_csv)
    print("")

    m1_stats = model1.fit_stats
    m2_stats = model2.fit_stats

    out = {}
    
    out["AIC"]  = _simple_compare(m1_stats,m2_stats,"AIC")
    out["AICc"] = _simple_compare(m1_stats,m2_stats,"AICc")
    out["BIC"]  = _simple_compare(m1_stats,m2_stats,"BIC")
   
    return out, model1.plot(), model2.plot()


