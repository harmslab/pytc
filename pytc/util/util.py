import scipy
from scipy import stats

def choose_model(model1,model2,alpha=0.05):
    """
    Use an F-test to select between model1 and model2 with a cutoff of alpha.
    
    Returns acceptance (True or False) and p-value
    """

    if model1.fit_sum_of_squares == None:
        print("Fitting model 1.")
        model1.fit()
    else:
        print("Using fit already done for model 1.")

    model1.plot()
    print("")
    print("Model 1 fit")
    print(model1.fit_as_csv)
    print("")

    if model2.fit_sum_of_squares == None:
        print("Fitting model 2.")
        model2.fit()
    else:
        print("Using fit already done for model 2.")

    model2.plot()
    print("")
    print("Model 2 fit")
    print(model2.fit_as_csv)
    print("")
        
    # Calculate the F-statistic 
    if model1.fit_degrees_freedom == model2.fit_degrees_freedom:
        F = model1.fit_sum_of_squares/model2.fit_sum_of_squares
    else:
        num = (model1.fit_sum_of_squares - model2.fit_sum_of_squares)/(model1.fit_degrees_freedom - model2.fit_degrees_freedom)
        den = model2.fit_degrees_freedom/model2.fit_sum_of_squares
        F = num/den
   
    # Determine the p-value 
    p_value = 1 - stats.f.cdf(F,model2.fit_degrees_freedom,model1.fit_degrees_freedom)
   
    # Print status 
    if p_value < alpha:
        print("Model 1 (p: {:.5e})".format(p_value))
        status = True
    else:
        print("Model 2 (p: {:.5e})".format(p_value))
        status = False

    return status, p_value
    

