import numpy as np
from scipy.optimize import curve_fit

##################   MATEMATICAL TOOLS ###############################

def model_function_constant(t, Iprev): #constant
    return 0*t + Iprev

def model_exponential(t, A, B, C, D): 
    return A * (B*np.exp(-(t-100)/C)) + D

def model_biexponential1(t, A, B, C, D, E): #biexponential model 1
    return A * (B*np.exp(-(t-100)/C) + (1-B)*np.exp(-(t-100)/D)) + E

def get_fit(subset_range, model_function, time, average_data_aligned):
    try :
        params = []
        start, end = subset_range
        x_subset = time[start:end]
        y_subset = average_data_aligned[start:end]
        params, _ = curve_fit(model_function, x_subset, y_subset)  
        return x_subset, model_function(x_subset, *params)
    except: 
        print("error : optimal parameter not found")
        return -1
        
def get_params_function(model_function, start, end, recording, time):
    x_subset = time[start:end]
    y_subset = recording[start:end]
    params, _ = curve_fit(model_function, x_subset, y_subset)
    return params
