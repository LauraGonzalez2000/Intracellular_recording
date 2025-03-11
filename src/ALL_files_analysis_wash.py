
import os
from PdfPage_wash import PdfPage
from trace_analysis_wash import DataFile_washout
import matplotlib.pylab as plt
import numpy as np
from scipy.stats import f_oneway, tukey_hsd, normaltest, kruskal, levene
import scikit_posthocs as sp
import pandas as pd
import openpyxl
#from scipy import stats

import pprint

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.my_math import calc_stats

#keep this aborescence if program used in other computers
base_path = os.path.join(os.path.expanduser('~'), 'DATA','In_Vitro_experiments', 'Washout_experiment') 
directory = "RAW-DATA-WASHOUT-PYR-bis"
files_directory = os.path.join(base_path, directory)

#methods
def find_nm_files(root_folder):
    nm_paths = []
    
    # Walk through all directories and files in the root_folder
    for folder, _, files in os.walk(root_folder):
        # Check each file in the current directory
        for file in files:

            # Skip files with specific extensions
            if any(ext in file for ext in ['HDF5', 'txt', 'pdf', 'log', 'xlsx', 'Experiment', 'pptx']):
                break
            # Construct the full path of the file
            file_path = os.path.join(folder, file)
            normalized_path = os.path.normpath(file_path)
            forward_slash_path = normalized_path.replace("\\", "/")
            nm_paths.append(forward_slash_path)
            #print('-', file)

    return nm_paths

def get_dict(datafiles_group, label, debug=False):

    my_dict = {'Ids'  : {'values': [], 'mean': [], 'std': [], 'sem': []},
               'Leaks': {'values': [], 'mean': [], 'std': [], 'sem': []}, 
               'Diffs': {'values': [], 'mean': [], 'std': [], 'sem': [], 'mean_norm': [], 'std_norm': [], 'sem_norm': []}}
        
    for key in my_dict:
        for datafile in datafiles_group:
            if key=='Ids':
                metric_datafile = datafile.get_Ids()
                metric_datafile_m, _ = datafile.get_batches(metric_datafile, batch_size=6)
            elif key=='Leaks':
                metric_datafile = datafile.get_baselines()
                metric_datafile_m, _ = datafile.get_batches(metric_datafile, batch_size=6)
            elif key=='Diffs':
                metric_datafile_m = datafile.batches_corr_diffs
            my_dict[key]['values'].append(metric_datafile_m)

    #ensure same length of values arrays
    pad(my_dict)
    
    #add statistical info
    for key in my_dict:
        my_dict[key]['mean'].append(np.nanmean(my_dict[key]['values'], axis=0)) #mean of the different files's mean for each one of the 50 positions
        my_dict[key]['std'].append(np.nanstd(my_dict[key]['values'], axis=0)) #std of the different files's mean for each one of the 50 positions
        my_dict[key]['sem'].append(np.nanstd(my_dict[key]['values'], axis=0)/np.sqrt(len(my_dict[key]['values'])))  #sem of the different files's mean for each one of the 50 positions
    #add nonrmalized values
    if (label=='memantine'): 
        baseline_diffs_m = np.nanmean(my_dict['Diffs']['mean'][0][2:7])
        my_dict['Diffs']['mean_norm'] = (my_dict['Diffs']['mean']/ baseline_diffs_m) * 100  
        my_dict['Diffs']['std_norm']  = (my_dict['Diffs']['std'] / baseline_diffs_m) * 100  
        my_dict['Diffs']['sem_norm']  = (my_dict['Diffs']['sem'] / baseline_diffs_m) * 100  

    else:
        baseline_diffs_m = np.nanmean(my_dict['Diffs']['mean'][0][6:11])
        my_dict['Diffs']['mean_norm'] = (my_dict['Diffs']['mean']/ baseline_diffs_m) * 100  
        my_dict['Diffs']['std_norm']  = (my_dict['Diffs']['std'] / baseline_diffs_m) * 100  
        my_dict['Diffs']['sem_norm']  = (my_dict['Diffs']['sem'] / baseline_diffs_m) * 100 
    if debug : 
            print("Ids, Leaks, Diffs that are given for the grouped pdf ")
            pprint.pprint(my_dict)
    return my_dict

def pad(my_list):
    sizes = []

    for key in ['Ids','Leaks','Diffs']:
    
        for mean in my_list[key]['values']:
            sizes.append(len(mean))

            if (len(np.unique(sizes))>1):  #we have to pad

                for key in my_list:
                    for mean in my_list[key]['values']:
                        max_size = np.max(sizes)
                        size = len(mean)
                        
                        if (max_size==size): #don't pad the one defining the max size
                            continue
                        else: #pad
                            num_pad_after = max_size - size 
                            for i in range(num_pad_after):
                                mean.append(np.nan)
            else: #don't pad if all have the same size
                continue
    return 0

def get_barplot_merged(my_list, label):
    
    #to normalize:
    if (label=='memantine'):
        sliced_array = [arr[2:7] for arr in my_list['Diffs']['values']]
    else : 
        sliced_array = [arr[6:11] for arr in my_list['Diffs']['values']]
    baseline_diffs_m = np.mean(sliced_array, axis=1)
    
    #end baseline
    if (label=='memantine'):
        sliced_array_bsl = [arr[2:7] for arr in my_list['Diffs']['values']]
    else : 
        sliced_array_bsl = [arr[6:11] for arr in my_list['Diffs']['values']]
    mean_sliced_array = np.mean(sliced_array_bsl, axis=1)
    sliced_array_norm_bsl = [(mean_sliced_array[i]/ baseline_diffs_m[i]) * 100 for i in range(len(sliced_array))]
    
    #end infusion:
    sliced_array_inf = [arr[15:19] for arr in my_list['Diffs']['values']]
    mean_sliced_array = np.mean(sliced_array_inf, axis=1)
    sliced_array_norm_inf = [(mean_sliced_array[i]/ baseline_diffs_m[i]) * 100 for i in range(len(sliced_array))] 
    
    #end wash
    sliced_array_wash = [arr[45:50] for arr in my_list['Diffs']['values']]
    mean_sliced_array = np.mean(sliced_array_wash, axis=1)
    sliced_array_norm_wash = [(mean_sliced_array[i]/ baseline_diffs_m[i]) * 100 for i in range(len(sliced_array))] 
    
    #end wash _
    sliced_array_wash_ = [arr[-5:-1] for arr in my_list['Diffs']['values']]
    mean_sliced_array = np.mean(sliced_array_wash_, axis=1)
    sliced_array_norm_wash_ = [(mean_sliced_array[i]/ baseline_diffs_m[i]) * 100 for i in range(len(sliced_array))] 

    #set barplot
    if (label=='memantine'):
        barplot = {'End baseline' : {'values': sliced_array_bsl,   'mean' : sliced_array_norm_bsl,  'sem': np.nanstd(sliced_array_norm_bsl)/np.sqrt(len(sliced_array_norm_bsl)),     'std': np.nanstd(sliced_array_norm_bsl)},
                   'End infusion' : {'values': sliced_array_inf,   'mean' : sliced_array_norm_inf,  'sem': np.nanstd(sliced_array_norm_inf)/np.sqrt(len(sliced_array_norm_inf)),     'std': np.nanstd(sliced_array_norm_inf)},
                   'End wash'     : {'values': sliced_array_wash,  'mean' : sliced_array_norm_wash, 'sem': np.nanstd(sliced_array_norm_wash)/np.sqrt(len(sliced_array_norm_wash)),   'std': np.nanstd(sliced_array_norm_wash)},
                   'End wash_'    : {'values': sliced_array_wash_, 'mean' : sliced_array_norm_wash_,'sem': np.nanstd(sliced_array_norm_wash_)/np.sqrt(len(sliced_array_norm_wash_)), 'std': np.nanstd(sliced_array_norm_wash_)}}
    else:
        barplot = {'End baseline' : {'values': sliced_array_bsl,   'mean' : sliced_array_norm_bsl, 'sem': np.nanstd(sliced_array_norm_bsl)/np.sqrt(len(sliced_array_norm_bsl)),   'std': np.nanstd(sliced_array_norm_bsl)},
                   'End infusion' : {'values': sliced_array_inf,   'mean' : sliced_array_norm_inf, 'sem': np.nanstd(sliced_array_norm_inf)/np.sqrt(len(sliced_array_norm_inf)),   'std': np.nanstd(sliced_array_norm_inf)},
                   'End wash'     : {'values': sliced_array_wash,  'mean' : sliced_array_norm_wash,'sem': np.nanstd(sliced_array_norm_wash)/np.sqrt(len(sliced_array_norm_wash)), 'std': np.nanstd(sliced_array_norm_wash)}}

    return barplot

def get_barplot(my_list, label):

    if (label=='memantine'):
        list_end_bsl  = my_list['Diffs']['mean_norm'][0][2:7]  #generalize
    else: 
        list_end_bsl  = my_list['Diffs']['mean_norm'][0][6:11]

    list_end_inf  = my_list['Diffs']['mean_norm'][0][15:19]
    list_end_wash = my_list['Diffs']['mean_norm'][0][45:50]
    list_end_wash_ = my_list['Diffs']['mean_norm'][0][-5:-1]

    if (label=='memantine'):
        barplot = {'End baseline' : {'values': list_end_bsl,   'mean' : np.nanmean(list_end_bsl),  'sem': np.nanstd(list_end_bsl)/np.sqrt(len(list_end_bsl)),     'std': np.nanstd(list_end_bsl)},#   'sem_means': np.nanstd(np.nanmean(list_end_bsl))  /np.sqrt(len(np.nanmean(list_end_bsl))) },
                   'End infusion' : {'values': list_end_inf,   'mean' : np.nanmean(list_end_inf),  'sem': np.nanstd(list_end_inf)/np.sqrt(len(list_end_inf)),     'std': np.nanstd(list_end_inf)},#   'sem_means': np.nanstd(np.nanmean(list_end_inf))  /np.sqrt(len(np.nanmean(list_end_inf))) },
                   'End wash'     : {'values': list_end_wash,  'mean' : np.nanmean(list_end_wash), 'sem': np.nanstd(list_end_wash)/np.sqrt(len(list_end_wash)),   'std': np.nanstd(list_end_wash)},#  'sem_means': np.nanstd(np.nanmean(list_end_wash)) /np.sqrt(len(np.nanmean(list_end_wash)))},
                   'End wash_'    : {'values': list_end_wash_, 'mean' : np.nanmean(list_end_wash_),'sem': np.nanstd(list_end_wash_)/np.sqrt(len(list_end_wash_)), 'std': np.nanstd(list_end_wash_)}}#, 'sem_means': np.nanstd(np.nanmean(list_end_wash_))/np.sqrt(len(np.nanmean(list_end_wash_)))}}
    else:
        barplot = {'End baseline' : {'values': list_end_bsl,   'mean' : np.nanmean(list_end_bsl), 'sem': np.nanstd(list_end_bsl)/np.sqrt(len(list_end_bsl)),   'std': np.nanstd(list_end_bsl)},#  'sem_means': np.nanstd(np.nanmean(list_end_bsl))  /np.sqrt(len(np.nanmean(list_end_bsl))) },
                   'End infusion' : {'values': list_end_inf,   'mean' : np.nanmean(list_end_inf), 'sem': np.nanstd(list_end_inf)/np.sqrt(len(list_end_inf)),   'std': np.nanstd(list_end_inf)},#  'sem_means': np.nanstd(np.nanmean(list_end_inf))  /np.sqrt(len(np.nanmean(list_end_inf))) },
                   'End wash'     : {'values': list_end_wash,  'mean' : np.nanmean(list_end_wash),'sem': np.nanstd(list_end_wash)/np.sqrt(len(list_end_wash)), 'std': np.nanstd(list_end_wash)}}#, 'sem_means': np.nanstd(np.nanmean(list_end_wash)) /np.sqrt(len(np.nanmean(list_end_wash))) }}

    return barplot

def get_final_barplot(my_list, label) : 

    #print("get final barplot")

    list_values_norm = []

    for i in range(len(my_list['Diffs']['values'])): 
        if (label=='memantine'):
            baseline_diffs_m = np.nanmean(my_list['Diffs']['values'][i][2:7])
        else: 
            baseline_diffs_m = np.nanmean(my_list['Diffs']['values'][i][6:11])
        norm = (my_list['Diffs']['values'][i]/ baseline_diffs_m) * 100  
        list_values_norm.append(norm)
    
    list_end_bsl = []
    list_end_inf  = []
    list_end_wash = []
    list_end_wash_ = []

    temp = []

    for i in range(len(list_values_norm)):
        #print("i ", i)
        #print("list values norm i ", list_values_norm[i])
        #print("baseline",list_values_norm[i][2:7])
        #print("baseline",list_values_norm[i][15:19])
        #print("baseline",list_values_norm[i][45:50])
        #print("baseline",list_values_norm[i][-5:-1])
        if (label=='memantine'):
            temp = list_values_norm[i][2:7]
            list_end_bsl.append(temp)
        else: 
            temp = list_values_norm[i][6:11]
            list_end_bsl.append(temp)
        
        temp = list_values_norm[i][15:19]
        list_end_inf.append(temp)
        
        temp = list_values_norm[i][45:50]
        list_end_wash.append(temp)

        temp = list_values_norm[i][-5:-1]
        list_end_wash_.append(temp)

    #print("fff")
    #print("list_end_wash_ ", list_end_wash_)
    
    if (label=='memantine'):
        barplot2 = {'End baseline' : {'values': list_end_bsl,   'mean' : np.nanmean(list_end_bsl, axis=1),  'sem': np.nanstd(list_end_bsl)/np.sqrt(len(list_end_bsl)),     'std': np.nanstd(list_end_bsl)},
                   'End infusion' : {'values': list_end_inf,   'mean' : np.nanmean(list_end_inf, axis=1),  'sem': np.nanstd(list_end_inf)/np.sqrt(len(list_end_inf)),     'std': np.nanstd(list_end_inf)},
                   'End wash'     : {'values': list_end_wash,  'mean' : np.nanmean(list_end_wash, axis=1), 'sem': np.nanstd(list_end_wash)/np.sqrt(len(list_end_wash)),   'std': np.nanstd(list_end_wash)},
                   'End wash_'    : {'values': list_end_wash_, 'mean' : np.nanmean(list_end_wash_, axis=1),'sem': np.nanstd(list_end_wash)/np.sqrt(len(list_end_wash_)), 'std': np.nanstd(list_end_wash_)}}
    else:
        barplot2 = {'End baseline' : {'values': list_end_bsl,   'mean' : np.nanmean(list_end_bsl, axis=1), 'sem': np.nanstd(list_end_bsl)/np.sqrt(len(list_end_bsl)),   'std': np.nanstd(list_end_bsl)},
                   'End infusion' : {'values': list_end_inf,   'mean' : np.nanmean(list_end_inf, axis=1), 'sem': np.nanstd(list_end_inf)/np.sqrt(len(list_end_inf)),   'std': np.nanstd(list_end_inf)},
                   'End wash'     : {'values': list_end_wash,  'mean' : np.nanmean(list_end_wash, axis=1),'sem': np.nanstd(list_end_wash)/np.sqrt(len(list_end_wash)), 'std': np.nanstd(list_end_wash)}}


    return barplot2

def get_final_info(datafiles):
    
    #initialize objects

    final_dict = {"control"  : {'mean':None, 'sem': None, 'std': None}, 
                  "ketamine" : {'mean':None, 'sem': None, 'std': None}, 
                  "D-AP5"    : {'mean':None, 'sem': None, 'std': None}, 
                  "memantine": {'mean':None, 'sem': None, 'std': None}}

    final_barplot = {"End baseline" : {"control"  : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "ketamine" : {'values' : None, 'mean': None, 'sem': None, 'std': None},
                                       "D-AP5"    : {'values' : None, 'mean': None, 'sem': None, 'std': None},
                                       "memantine": {'values' : None, 'mean': None, 'sem': None, 'std': None}},
                     "End infusion" : {"control"  : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "ketamine" : {'values' : None, 'mean': None, 'sem': None, 'std': None},
                                       "D-AP5"    : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "memantine": {'values' : None, 'mean': None, 'sem': None, 'std': None}},
                     "End wash"     : {"control"  : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "ketamine" : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "D-AP5"    : {'values' : None, 'mean': None, 'sem': None, 'std': None},           
                                       "memantine": {'values' : None, 'mean': None, 'sem': None, 'std': None} }}
    
    final_barplot2 = {"End wash"      : {'values' : None, 'mean': None, 'sem': None, 'std': None},
                      "End wash long" : {'values' : None, 'mean': None, 'sem': None, 'std': None}}


    for label in GROUPS: 
        datafiles_group = datafiles[label]
        my_list = get_dict(datafiles_group, label)
        barplot = get_final_barplot(my_list, label)
        
        final_dict[label]['mean'] = np.array(my_list['Diffs']['mean'])
        final_dict[label]['std']  = np.array(my_list['Diffs']['std'])
        final_dict[label]['sem']  = np.array(my_list['Diffs']['sem'])

        final_barplot['End baseline'][label]['values'] = barplot["End baseline"]['values']
        final_barplot['End infusion'][label]['values'] = barplot['End infusion']['values']
        final_barplot['End wash'][label]['values']     = barplot['End wash']['values']

        final_barplot['End baseline'][label]['mean']   = np.nanmean(barplot["End baseline"]['values'], axis=1)
        final_barplot['End infusion'][label]['mean']   = np.nanmean(barplot['End infusion']['values'], axis=1)
        final_barplot['End wash'][label]['mean']       = np.nanmean(barplot['End wash']['values'], axis=1)

        final_barplot['End baseline'][label]['sem']    = np.nanstd(barplot["End baseline"]['values'], axis=1)/np.sqrt(len(barplot["End baseline"]['values']))
        final_barplot['End infusion'][label]['sem']    = np.nanstd(barplot['End infusion']['values'], axis=1)/np.sqrt(len(barplot['End infusion']['values']))
        final_barplot['End wash'][label]['sem']        = np.nanstd(barplot['End wash']['values'], axis=1)/np.sqrt(len(barplot['End wash']['values']))

        final_barplot['End baseline'][label]['std']    = np.nanstd(barplot["End baseline"]['values'], axis=1)
        final_barplot['End infusion'][label]['std']    = np.nanstd(barplot['End infusion']['values'], axis=1)
        final_barplot['End wash'][label]['std']        = np.nanstd(barplot['End wash']['values'], axis=1)
      
        if (label=='memantine'): 
            final_barplot2['End wash']['values']      = barplot['End wash']['values']
            final_barplot2['End wash long']['values'] = barplot['End wash_']['values']
            final_barplot2['End wash']['mean']        = np.nanmean(barplot['End wash']['values'], axis=0)
            final_barplot2['End wash long']['mean']   = np.nanmean(barplot['End wash_']['values'], axis=0)  
            final_barplot2['End wash']['sem']         = np.nanstd(barplot['End wash']['values'], axis=0)/np.sqrt(np.sum(~np.isnan(barplot['End wash']['values'])))
            final_barplot2['End wash long']['sem']    = np.nanstd(barplot['End wash_']['values'], axis=0)/np.sqrt(np.sum(~np.isnan(barplot['End wash_']['values'])))
            final_barplot2['End wash']['std']         = np.nanstd(barplot['End wash']['values'], axis=0)
            final_barplot2['End wash long']['std']    = np.nanstd(barplot['End wash_']['values'], axis=0)
     
        GROUPS[label]['num_files'] = len(datafiles_group)
 
    
    num_pad_before = GROUPS['ketamine']['inf_start']-GROUPS['memantine']['inf_start']  #10 -6 = 4
    num_pad_after = len(final_dict["memantine"]["mean"]) - len(final_dict["ketamine"]["mean"])  #63-50 = 13
    prepended_values = np.full((num_pad_before), np.nan, dtype=np.float16)
    posterior_values = np.full((num_pad_after), np.nan, dtype=np.float16)
    final_dict["memantine"]["mean"] = np.concatenate((prepended_values, final_dict["memantine"]["mean"][0].astype(np.float16)))
    final_dict["ketamine"]["mean"] = np.concatenate((final_dict["ketamine"]["mean"][0].astype(np.float16), posterior_values))
    final_dict["D-AP5"]["mean"] = np.concatenate((final_dict["D-AP5"]["mean"][0].astype(np.float16), posterior_values))
    final_dict["control"]["mean"] = np.concatenate((final_dict["control"]["mean"][0].astype(np.float16), posterior_values))
    final_dict["memantine"]["std"] = np.concatenate((prepended_values, final_dict["memantine"]["std"][0]))
    final_dict["ketamine"]["std"] = np.concatenate((final_dict["ketamine"]["std"][0].astype(np.float16), posterior_values))
    final_dict["D-AP5"]["std"] = np.concatenate((final_dict["D-AP5"]["std"][0].astype(np.float16), posterior_values))
    final_dict["control"]["std"] = np.concatenate((final_dict["control"]["std"][0].astype(np.float16), posterior_values))
    final_dict["memantine"]["sem"] = np.concatenate((prepended_values, final_dict["memantine"]["sem"][0].astype(np.float16)))
    final_dict["ketamine"]["sem"] = np.concatenate((final_dict["ketamine"]["sem"][0].astype(np.float16), posterior_values))
    final_dict["D-AP5"]["sem"] = np.concatenate((final_dict["D-AP5"]["sem"][0].astype(np.float16), posterior_values))
    final_dict["control"]["sem"] = np.concatenate((final_dict["control"]["sem"][0].astype(np.float16), posterior_values))
    
    return final_dict, final_barplot, final_barplot2

def my_calc_stats(final_barplot, final_barplot2, GROUPS):

    #flipping structure seems easier ##########################################
    values_barplot = {"control"  : {"End baseline" : None, 
                                    "End infusion" : None,
                                    "End wash"     : None},
                     "ketamine"  : {"End baseline" : None, 
                                    "End infusion" : None,
                                    "End wash"     : None},
                     "D-AP5"     : {"End baseline" : None, 
                                    "End infusion" : None,
                                    "End wash"     : None},
                     "memantine" : {"End baseline" : None, 
                                    "End infusion" : None,
                                    "End wash"     : None}}
    for group in GROUPS:
        for time in final_barplot.keys():
            values_barplot[group][time] = final_barplot[time][group]['mean']
        if (group=='memantine'):
            values_barplot['memantine']['End wash_'] = final_barplot2['End wash long']['mean']

    #####################################################################
    stats = {'control':{'Normality': True,
                        'Homescedasticity': True,
                        'Parametric': True,
                        'Test': "",
                        'F_stat': None,
                        'p_val': None, 
                        'Post hoc test':"",
                        'final_stats': np.array([[np.nan, np.nan, np.nan],
                                                 [np.nan, np.nan, np.nan],
                                                 [np.nan, np.nan, np.nan]])}, 
            'ketamine':{'Normality': True,
                        'Homescedasticity': True,
                        'Parametric': True,
                        'Test': "",
                        'F_stat': None,
                        'p_val': None, 
                        'Post hoc test':"",
                        'final_stats': np.array([[np.nan, np.nan, np.nan],
                                                 [np.nan, np.nan, np.nan],
                                                 [np.nan, np.nan, np.nan]])}, 
            'D-AP5':{'Normality': True,
                        'Homescedasticity': True,
                        'Parametric': True,
                        'Test': "",
                        'F_stat': None,
                        'p_val': None, 
                        'Post hoc test':"",
                        'final_stats': np.array([[np.nan, np.nan, np.nan],
                                                 [np.nan, np.nan, np.nan],
                                                 [np.nan, np.nan, np.nan]])}, 
            'memantine':{'Normality': True,
                        'Homescedasticity': True,
                        'Parametric': True,
                        'Test': "",
                        'F_stat': None,
                        'p_val': None, 
                        'Post hoc test':"",
                        'final_stats': np.array([[np.nan, np.nan, np.nan, np.nan],
                                                 [np.nan, np.nan, np.nan, np.nan],
                                                 [np.nan, np.nan, np.nan, np.nan],
                                                 [np.nan, np.nan, np.nan, np.nan]])}}


    #statistic performed within each group:
    for group in GROUPS:
        test_stats = calc_stats(group,
                                values_barplot[group]["End baseline"],
                                values_barplot[group]["End infusion"], 
                                values_barplot[group]["End wash"])
        stats[group]['Normality'] = test_stats['Normality']
        stats[group]['Homescedasticity'] = test_stats['Homescedasticity']
        stats[group]['Parametric'] = test_stats['Parametric']
        stats[group]['F_stat'] = test_stats['F_stat']
        stats[group]['p_val'] = test_stats['p_val']
        stats[group]['Post hoc test'] = test_stats['Supplementary test']
        stats[group]['final_stats'] = test_stats['final_stats']
    return stats

def save_stats(data_list):
    try:
        data_for_excel = pd.DataFrame(data_list)
        path = 'C:/Users/sofia/Output_expe/In_Vitro/washout/statistics_wash.xlsx'
        with pd.ExcelWriter(path, engine='openpyxl') as writer: 
            data_for_excel.to_excel(writer, sheet_name='Statistics', index=False)
            worksheet = writer.sheets['Statistics']
            # Adjust column widths for data_for_excel
            for column in data_for_excel:
                column_length = max(data_for_excel[column].astype(str).map(len).max(), len(column))
                col_idx = data_for_excel.columns.get_loc(column)
                worksheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx + 1)].width = column_length
        print("stats file saved successfully.")
    except Exception as e:
        print(f"ERROR when saving the stats file : {e}")
    return 0
    
#OK
def create_individual_pdf(datafile, GROUPS, wash='all',  debug=False):
    try:
        pdf = PdfPage(PDF_sheet = 'individual', debug=debug )
        pdf.fill_PDF(datafile, GROUPS, wash= wash,  debug=debug)
        plt.savefig(f'C:/Users/sofia/Output_expe/In_Vitro/washout/Washout_PDFs/{datafile.filename}.pdf')
        print("OK PDF file saved successfully. \n")
    except Exception as e:
        print(f"Error saving individual PDF file : {e}")      
    return 0

#OK
def create_group_pdf(label, dict, barplot, len_group, GROUPS, stats, debug=False):
    if debug:
        print("label :\n" , label)
        print("dict :\n" , dict)
        print("barplot :\n", barplot)
        print("len group :\n", len_group)

    try:
        pdf = PdfPage(PDF_sheet = 'group analysis', debug=debug)
        pdf.fill_PDF_merge(num_files = len_group, group = label, my_list = dict, barplot = barplot, GROUPS=GROUPS, stats=stats, debug=debug)
        plt.savefig(f'C:/Users/sofia/Output_expe/In_Vitro/washout/Washout_PDFs/{label}_merged.pdf') 
        print(f"OK PDF file saved successfully for group {label}. \n")
    except Exception as e:
        print(f"Error saving group PDF file for group {label} : {e}")
    return 0

#OK
def create_final_results_pdf(final_dict, final_barplot, GROUPS, final_barplot2, stats, debug):
    if debug: 
        print("Debug for final PDF")
        print("final dict : ")
        pprint.pprint(final_dict)
        print("final barplots :")
        pprint.pprint(final_barplot)
        pprint.pprint(final_barplot2)
        pprint.pprint(GROUPS)
        
    
    try: 
        pdf = PdfPage(PDF_sheet = 'final', debug=debug )
        pdf.fill_final_results(final_dict, final_barplot, GROUPS, final_barplot2, stats, debug=debug3)
        plt.savefig(f'C:/Users/sofia/Output_expe/In_Vitro/washout/Washout_PDFs/final_results.pdf') 
        print('OK final results PDF file saved successfully')
    except Exception as e:
        print(f"Error saving final PDF file : {e}")
    return 0

###################################################################################################
###################################################################################################
#OK
if __name__=='__main__':

    GROUPS = {'control':   {'concentration': '-', 
                            'color':'grey',
                            'inf_start': 10, 
                            'num_files': None}, 
              'ketamine':  {'concentration': '100uM', 
                            'color':'purple',
                            'inf_start':10,
                            'num_files': None},
              'D-AP5':     {'concentration': '50uM', 
                            'color':'orange',
                            'inf_start': 10,
                            'num_files': None},
              'memantine': {'concentration': '100uM', 
                            'color':'gold',
                            'inf_start': 6,
                            'num_files': None}} 

    datafiles = {'all':[],
                 'ketamine':[], 
                 'D-AP5':[], 
                 'control':[], 
                 'memantine':[]}
    
    #############################################################################################################################
    #Load and sort datafiles: ###################################################################################################
    debug0 = False

    files = find_nm_files(files_directory)

    for file in files:
        print("\n", file)     
        datafile = DataFile_washout(file, debug=debug0)
        datafiles['all'].append(datafile)
        datafiles[datafile.infos['Group']].append(datafile)

    #############################################################################################################################
    #PDF creation for each datafile : ###########################################################################################
    '''
    debug1=False
    for datafile in datafiles['all']: 
        create_individual_pdf(datafile, GROUPS, wash='all',  debug=debug1)
    
    '''
    ##############################################################################################################################
    final_dict, final_barplot, final_barplot2 = get_final_info(datafiles)
    stats = my_calc_stats(final_barplot, final_barplot2, GROUPS)
    '''
    ##############################################################################################################################
    #PDF creation for the chosen groups: #########################################################################################
    debug2 = False
    create_group_pdf(label="ketamine",  
                     dict = get_dict(datafiles['ketamine'], "ketamine", debug=debug2),
                     barplot= get_barplot_merged(get_dict(datafiles['ketamine'], "ketamine", debug=debug2), "ketamine"), 
                     len_group = len(datafiles['ketamine']), 
                     GROUPS=GROUPS['ketamine'],
                     stats = stats['ketamine'], 
                     debug=debug2)

    create_group_pdf(label="memantine", 
                     dict= get_dict(datafiles['memantine'], "memantine", debug=debug2),
                     barplot= get_barplot_merged(get_dict(datafiles['memantine'], "memantine", debug=debug2), "memantine"), 
                     len_group= len(datafiles['memantine']), 
                     GROUPS=GROUPS['memantine'], 
                     stats=stats["memantine"],
                     debug=debug2)  
    
    create_group_pdf(label="D-AP5", 
                     dict= get_dict(datafiles['D-AP5'], "D-AP5", debug=debug2),
                     barplot= get_barplot_merged(get_dict(datafiles['D-AP5'], "D-AP5", debug=debug2), "D-AP5"), 
                     len_group=len(datafiles['D-AP5']), 
                     GROUPS=GROUPS['D-AP5'], 
                     stats=stats["D-AP5"],
                     debug=debug2)  
    
    create_group_pdf(label="control", 
                     dict= get_dict(datafiles['control'], "control", debug=debug2), 
                     barplot= get_barplot_merged(get_dict(datafiles['control'], "control", debug=debug2), "control"), 
                     len_group = len(datafiles['control']), 
                     GROUPS= GROUPS['control'],
                     stats = stats["control"],
                     debug=debug2) 
    '''
    ###############################################################################################################################

    #PDF creation to compare groups: ##############################################################################################
    debug3 = False
    create_final_results_pdf(final_dict, final_barplot, GROUPS, final_barplot2, stats, debug=debug3)
    save_stats(stats)