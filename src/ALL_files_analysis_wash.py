import os
from PdfPage_wash import PdfPage
from trace_analysis_wash import DataFile_washout
import matplotlib.pylab as plt
import numpy as np

import pprint

#keep this aborescence if program used in other computers
base_path = os.path.join(os.path.expanduser('~'), 'DATA','In_Vitro_experiments', 'Washout_experiment') 
directory = "RAW-DATA-WASHOUT-PYR"
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
    if label=='memantine': 
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

            if len(np.unique(sizes))>1:  #we have to pad

                for key in my_list:
                    for mean in my_list[key]['values']:
                        max_size = np.max(sizes)
                        size = len(mean)
                        
                        if max_size==size: #don't pad the one defining the max size
                            continue
                        else: #pad
                            num_pad_after = max_size - size 
                            for i in range(num_pad_after):
                                mean.append(np.nan)
            else: #don't pad if all have the same size
                continue
    return 0

def get_barplot(my_list, label):
    if label=='memantine':
        list_end_bsl  = my_list['Diffs']['mean_norm'][0][2:7]  #generalize
    else: 
        list_end_bsl  = my_list['Diffs']['mean_norm'][0][6:11]

    list_end_inf  = my_list['Diffs']['mean_norm'][0][15:19]
    list_end_wash = my_list['Diffs']['mean_norm'][0][45:50]
    list_end_wash_ = my_list['Diffs']['mean_norm'][0][-5:-1]

    if label=='memantine':
        barplot = {'End baseline' : {'values': list_end_bsl,   'mean' : np.nanmean(list_end_bsl),  'sem': np.nanstd(list_end_bsl)/np.sqrt(len(list_end_bsl)),     'std': np.nanstd(list_end_bsl)},
                   'End infusion' : {'values': list_end_inf,   'mean' : np.nanmean(list_end_inf),  'sem': np.nanstd(list_end_inf)/np.sqrt(len(list_end_inf)),     'std': np.nanstd(list_end_inf)},
                   'End wash'     : {'values': list_end_wash,  'mean' : np.nanmean(list_end_wash), 'sem': np.nanstd(list_end_wash)/np.sqrt(len(list_end_wash)),   'std': np.nanstd(list_end_wash)},
                   'End wash_'    : {'values': list_end_wash_, 'mean' : np.nanmean(list_end_wash_),'sem': np.nanstd(list_end_wash)/np.sqrt(len(list_end_wash_)), 'std': np.nanstd(list_end_wash_)}}
    else:
        barplot = {'End baseline' : {'values': list_end_bsl,   'mean' : np.nanmean(list_end_bsl), 'sem': np.nanstd(list_end_bsl)/np.sqrt(len(list_end_bsl)),   'std': np.nanstd(list_end_bsl)},
                   'End infusion' : {'values': list_end_inf,   'mean' : np.nanmean(list_end_inf), 'sem': np.nanstd(list_end_inf)/np.sqrt(len(list_end_inf)),   'std': np.nanstd(list_end_inf)},
                   'End wash'     : {'values': list_end_wash,  'mean' : np.nanmean(list_end_wash),'sem': np.nanstd(list_end_wash)/np.sqrt(len(list_end_wash)), 'std': np.nanstd(list_end_wash)}}

    print("barplot1: \n", barplot)
    return barplot

def get_barplot2(my_list, label) : 

    list_values_norm = []

    for i in range(len(my_list['Diffs']['values'])):
        
        if label=='memantine':
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
        if label=='memantine':
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
    
    if label=='memantine':
        barplot2 = {'End baseline' : {'values': list_end_bsl,   'mean' : np.nanmean(list_end_bsl, axis=1),  'sem': np.nanstd(list_end_bsl)/np.sqrt(len(list_end_bsl)),     'std': np.nanstd(list_end_bsl)},
                   'End infusion' : {'values': list_end_inf,   'mean' : np.nanmean(list_end_inf, axis=1),  'sem': np.nanstd(list_end_inf)/np.sqrt(len(list_end_inf)),     'std': np.nanstd(list_end_inf)},
                   'End wash'     : {'values': list_end_wash,  'mean' : np.nanmean(list_end_wash, axis=1), 'sem': np.nanstd(list_end_wash)/np.sqrt(len(list_end_wash)),   'std': np.nanstd(list_end_wash)},
                   'End wash_'    : {'values': list_end_wash_, 'mean' : np.nanmean(list_end_wash_, axis=1),'sem': np.nanstd(list_end_wash)/np.sqrt(len(list_end_wash_)), 'std': np.nanstd(list_end_wash_)}}
    else:
        barplot2 = {'End baseline' : {'values': list_end_bsl,   'mean' : np.nanmean(list_end_bsl, axis=1), 'sem': np.nanstd(list_end_bsl)/np.sqrt(len(list_end_bsl)),   'std': np.nanstd(list_end_bsl)},
                   'End infusion' : {'values': list_end_inf,   'mean' : np.nanmean(list_end_inf, axis=1), 'sem': np.nanstd(list_end_inf)/np.sqrt(len(list_end_inf)),   'std': np.nanstd(list_end_inf)},
                   'End wash'     : {'values': list_end_wash,  'mean' : np.nanmean(list_end_wash, axis=1),'sem': np.nanstd(list_end_wash)/np.sqrt(len(list_end_wash)), 'std': np.nanstd(list_end_wash)}}

    print("barplot2 \n", barplot2)
    return barplot2

def get_final_info(datafiles_keta, datafiles_APV, datafiles_control, datafiles_memantine):
    final_dict = {"control"  : {'mean':None, 'sem': None, 'std': None}, 
                  "ketamine" : {'mean':None, 'sem': None, 'std': None}, 
                  "D-AP5"    : {'mean':None, 'sem': None, 'std': None}, 
                  "memantine": {'mean':None, 'sem': None, 'std': None}}

    final_barplot = {"End baseline" : {"control"  : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "ketamine" : {'values' : None, 'mean': None, 'sem': None, 'std': None},
                                       "D-AP5"    : {'values' : None, 'mean': None, 'sem': None, 'std': None},
                                       "memantine": {'values' : None, 'mean': None, 'sem': None, 'std': None} },
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

    final_num_files = {"control"  : None, 
                       "ketamine" : None, 
                       "D-AP5"    : None,
                       "memantine": None}
    for label in GROUPS: 
        
        if label == 'control': 
            datafiles_group = datafiles_control
        elif label == 'ketamine': 
            datafiles_group = datafiles_keta
        elif label == 'memantine': 
            datafiles_group = datafiles_memantine
        elif label == 'D-AP5': 
            datafiles_group = datafiles_APV

        my_list = get_dict(datafiles_group, label)
        barplot = get_barplot2(my_list, label)
        
        final_dict[label]['mean'] = np.array(my_list['Diffs']['mean'])
        final_dict[label]['std']  = np.array(my_list['Diffs']['std'])
        final_dict[label]['sem']  = np.array(my_list['Diffs']['sem'])

        final_barplot['End baseline'][label]['values'] = barplot["End baseline"]['values']
        final_barplot['End infusion'][label]['values'] = barplot['End infusion']['values']
        final_barplot['End wash'][label]['values']     = barplot['End wash']['values']

        final_barplot['End baseline'][label]['mean']   = np.mean(barplot["End baseline"]['values'], axis=1)
        final_barplot['End infusion'][label]['mean']   = np.mean(barplot['End infusion']['values'], axis=1)
        final_barplot['End wash'][label]['mean']       = np.mean(barplot['End wash']['values'], axis=1)

        
        final_barplot['End baseline'][label]['sem']    = np.std(barplot["End baseline"]['values'], axis=1)/np.sqrt(len(barplot["End baseline"]['values']))
        final_barplot['End infusion'][label]['sem']    = np.std(barplot['End infusion']['values'], axis=1)/np.sqrt(len(barplot['End infusion']['values']))
        final_barplot['End wash'][label]['sem']        = np.std(barplot['End wash']['values'], axis=1)/np.sqrt(len(barplot['End wash']['values']))

        final_barplot['End baseline'][label]['std']    = np.std(barplot["End baseline"]['values'], axis=1)
        final_barplot['End infusion'][label]['std']    = np.std(barplot['End infusion']['values'], axis=1)
        final_barplot['End wash'][label]['std']        = np.std(barplot['End wash']['values'], axis=1)
      
        if label=='memantine': 
            
            final_barplot2['End wash']['values']      = barplot['End wash']['values']
            final_barplot2['End wash long']['values'] = barplot['End wash_']['values']
            final_barplot2['End wash']['mean']        = np.mean(barplot['End wash']['values'], axis=0)
            final_barplot2['End wash long']['mean']   = np.mean(barplot['End wash_']['values'], axis=0)  
            final_barplot2['End wash']['sem']         = np.std(barplot['End wash']['values'], axis=0)/np.sqrt(len(barplot['End wash']['values']))
            final_barplot2['End wash long']['sem']    = np.std(barplot['End wash_']['values'], axis=0)/np.sqrt(len(barplot['End wash_']['values']))
            final_barplot2['End wash']['std']         = np.std(barplot['End wash']['values'], axis=0)
            final_barplot2['End wash long']['std']    = np.std(barplot['End wash_']['values'], axis=0)
     
        final_num_files[label] = len(datafiles_group)
 
    inf_start = {'ketamine' : 10, 
                 'memantine': 6, 
                 'control': 10,
                 'D-AP5': 10}
    num_pad_before = inf_start["ketamine"]-inf_start["memantine"]  #10 -6 = 4
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
    
    #print("final dict after padding for final : \n", final_dict)
   
    return final_dict, final_barplot, final_barplot2, final_num_files

def create_individual_pdf(datafiles, wash= 'all', debug=False):
    for datafile in datafiles:
        try:
            pdf = PdfPage(PDF_sheet = 'individual', debug=debug )
            pdf.fill_PDF(datafile, wash= wash, debug=debug)
            plt.savefig(f'C:/Users/sofia/Output_expe/washout/Washout_PDFs/{datafile.filename}.pdf')
            print("OK File saved successfully \n")
        except Exception as e:
            print(f"Error analysing this file : {e}")      
    return 0

def create_group_pdf(datafiles_group, label, filename, debug=False):
    try:
        dict = get_dict(datafiles_group, label, debug=False)
        barplot = get_barplot(dict, label)
        barplot2 = get_barplot2(dict, label)
        pdf = PdfPage(PDF_sheet = 'group analysis', debug=False )
        if debug:
            print("dict :\n" , dict)
            print("barplot :\n", barplot2)
        pdf.fill_PDF_merge(num_files = len(datafiles_group), group = label, my_list = dict, barplot = barplot2)
        plt.savefig(f'C:/Users/sofia/Output_expe/washout/Washout_PDFs/{filename}.pdf') #PC
        print(f"{label} PDF saved \n")

    except Exception as e:
        print(f"Error doing group analysis for {label}: {e}")
    return 0

def create_final_results_pdf(final_dict, final_barplot, final_num_files, concentration, colors, GROUPS, final_barplot2, debug=False):
    pdf = PdfPage(PDF_sheet = 'final', debug=debug )
    pdf.fill_final_results(final_dict, final_barplot, final_num_files, concentration, colors, GROUPS, final_barplot2)
    plt.savefig(f'C:/Users/sofia/Output_expe/washout/Washout_PDFs/final_results.pdf') #PC #plt.savefig(f'C:/Users/LauraGonzalez/Output_expe/Washout_PDFs/final_results.pdf') #in laptop
    print('final results figure saved')
    return 0


if __name__=='__main__':

    concentration = {'ketamine' : '100uM', 
                     'control'  : '-',  
                     'D-AP5'    : '50uM',
                     'memantine': '100uM'}
    colors = {'ketamine' : 'purple', 
              'control'  : 'grey', 
              'D-AP5'    : 'orange',
              'memantine': 'gold'}
    GROUPS = ['control', 'ketamine', 'D-AP5', 'memantine'] 

    #Load and sort datafiles: ###################################################################################################
    debug1 = False

    files = find_nm_files(files_directory)
    datafiles, datafiles_keta, datafiles_APV, datafiles_control, datafiles_memantine = [], [], [], [], [] #make only 1 dict?
    
    infusion_start = []

    for file in files:
            print("\n", file)     
            datafile = DataFile_washout(file, debug=debug1)
            datafiles.append(datafile)
            
            if datafile.infos['Group'] == 'control': 
                datafiles_control.append(datafile)
            elif datafile.infos['Group'] == 'KETA':
                datafiles_keta.append(datafile)
            elif datafile.infos['Group'] == 'APV': 
                datafiles_APV.append(datafile)
            elif datafile.infos['Group'] == 'MEMANTINE': 
                datafiles_memantine.append(datafile)

            infusion_start.append(datafile.infos['Infusion start'])

    #PDF creation for each datafile : #########################################################################################

    
    create_individual_pdf(datafiles, wash='all', debug=debug1)
    
    #PDF creation for the chosen groups: #########################################################################################
    debug2 = False

    create_group_pdf(datafiles_keta, "ketamine", "ketamine_merge", debug=debug2)
    create_group_pdf(datafiles_memantine, "memantine", "memantine_merge", debug=debug2)  
    create_group_pdf(datafiles_APV, "D-AP5", "D-AP5_merge", debug=debug2)
    create_group_pdf(datafiles_control, "control", "control_merge", debug=debug2)

    #PDF creation to compare groups: ##############################################################################################
    
    debug3 = True
   
    final_dict, final_barplot, final_barplot2, final_num_files = get_final_info(datafiles_keta, datafiles_APV, datafiles_control, datafiles_memantine)

    if debug3: 
        print("Debug for final PDF")
        print("final dict : ")
        pprint.pprint(final_dict)
        print("final barplot ")
        pprint.pprint(final_barplot)

    create_final_results_pdf(final_dict, final_barplot, final_num_files, concentration, colors, GROUPS, final_barplot2, debug=debug3)
    

    