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

def merge_info(datafile, my_list):
    for key in my_list:
        if key=='Ids':
            metric_datafile = datafile.get_Ids()
            metric_datafile_m, _ = datafile.get_batches(metric_datafile, batch_size=6)
        elif key=='Leaks':
            metric_datafile = datafile.get_baselines()
            metric_datafile_m, _ = datafile.get_batches(metric_datafile, batch_size=6)
        elif key=='Diffs':
            metric_datafile_m = datafile.batches_corr_diffs       
        my_list[key]['mean'].append(metric_datafile_m)
    return 0

def create_individual_pdf(datafiles, wash= 'all', debug=False):
    for datafile in datafiles:
        try:
            pdf = PdfPage(PDF_sheet = 'individual', debug=debug )
            pdf.fill_PDF(datafile, wash= wash, debug=debug)
            plt.savefig(f'C:/Users/sofia/Output_expe/washout/Washout_PDFs/{datafile.filename}.pdf')
            #plt.savefig(f'C:/Users/sofia/Output_expe/washout/Washout_PDFs/end_cut/PYR-Nelson/{datafile.filename}.pdf')
            print(datafile.filename)
            print("OK File saved successfully")
        except Exception as e:
            print(f"Error analysing this file : {e}")      
    return 0

def create_group_pdf(datafiles_group, label, filename, final_dict, final_barplot, final_num_files, final_barplot2, debug=False):
    try:
        my_list = {'Ids'  : {'mean': [], 'std': [], 'sem': []},
                   'Leaks': {'mean': [], 'std': [], 'sem': []}, 
                   'Diffs': {'mean': [], 'std': [], 'sem': [], 
                             'mean_norm': [], 'std_norm': [], 'sem_norm': []}}
        

        for datafile in datafiles_group:
            merge_info(datafile, my_list)
        
        for key in my_list:
            metric_datafile_std = np.std(my_list[key]['mean'], axis=0)   #std of the different files's mean for each one of the 50 positions  
            metric_datafile_sem = np.std(my_list[key]['mean'], axis=0)/np.sqrt(len(my_list[key]['mean'])) #sem of the different files's mean for each one of the 50 positions  
            my_list[key]['std'].append(metric_datafile_std)
            my_list[key]['sem'].append(metric_datafile_sem)
            my_list[key]['mean'] = np.mean(my_list[key]['mean'], axis=0)  #updates the mean!!! #mean of the different files's mean for each one of the 50 positions  
            print("my_list[", key, "]['mean'] after for group : ", label," ", my_list[key]['mean'])

        if debug : 
            #print(" datafiles_group  ", datafiles_group)
            #print("Ids, Leaks, Diffs that are given for the pdf ")
            pprint.pprint(my_list)
        
        ################################################################################

        if label=='memantine':
            baseline_diffs_m = np.mean(my_list['Diffs']['mean'][2:7])
            my_list['Diffs']['mean_norm'] = (my_list['Diffs']['mean']/ baseline_diffs_m) * 100  
            my_list['Diffs']['std_norm']  = (my_list['Diffs']['std'] / baseline_diffs_m) * 100  
            my_list['Diffs']['sem_norm']  = (my_list['Diffs']['sem'] / baseline_diffs_m) * 100  
            list_end_bsl  = my_list['Diffs']['mean_norm'][2:7]

        else:
            baseline_diffs_m = np.mean(my_list['Diffs']['mean'][6:11])
            my_list['Diffs']['mean_norm'] = (my_list['Diffs']['mean']/ baseline_diffs_m) * 100  
            my_list['Diffs']['std_norm']  = (my_list['Diffs']['std'] / baseline_diffs_m) * 100  
            my_list['Diffs']['sem_norm']  = (my_list['Diffs']['sem'] / baseline_diffs_m) * 100 
            list_end_bsl  = my_list['Diffs']['mean_norm'][6:11]

        list_end_inf  = my_list['Diffs']['mean_norm'][15:19]
        list_end_wash = my_list['Diffs']['mean_norm'][45:50]
        list_end_wash_ = my_list['Diffs']['mean_norm'][-5:-1]

        if label=='memantine':
            barplot = {'End baseline' : {'values': list_end_bsl,   'mean' : np.mean(list_end_bsl, axis=0),  'sem': np.std(list_end_bsl, axis=0)/np.sqrt(len(list_end_bsl)),     'std': np.std(list_end_bsl, axis=0)},
                       'End infusion' : {'values': list_end_inf,   'mean' : np.mean(list_end_inf, axis=0),  'sem': np.std(list_end_inf, axis=0)/np.sqrt(len(list_end_inf)),     'std': np.std(list_end_inf, axis=0)},
                       'End wash'     : {'values': list_end_wash,  'mean' : np.mean(list_end_wash, axis=0), 'sem': np.std(list_end_wash, axis=0)/np.sqrt(len(list_end_wash)),   'std': np.std(list_end_wash, axis=0)},
                       'End wash_'    : {'values': list_end_wash_, 'mean' : np.mean(list_end_wash_, axis=0),'sem': np.std(list_end_wash_, axis=0)/np.sqrt(len(list_end_wash_)), 'std': np.std(list_end_wash_, axis=0)}}
        else:
            barplot = {'End baseline' : {'values': list_end_bsl,  'mean' : np.mean(list_end_bsl, axis=0), 'sem': np.std(list_end_bsl, axis=0)/np.sqrt(len(list_end_bsl)),   'std': np.std(list_end_bsl, axis=0)},
                    'End infusion'    : {'values': list_end_inf,  'mean' : np.mean(list_end_inf, axis=0), 'sem': np.std(list_end_inf, axis=0)/np.sqrt(len(list_end_inf)),   'std': np.std(list_end_inf, axis=0)},
                    'End wash'        : {'values': list_end_wash, 'mean' : np.mean(list_end_wash, axis=0),'sem': np.std(list_end_wash, axis=0)/np.sqrt(len(list_end_wash)), 'std': np.std(list_end_wash, axis=0)}}

        #################################################################################
        
        pdf = PdfPage(PDF_sheet = 'group analysis', debug=False )

        #pprint.pprint("my_list" , my_list)
        pdf.fill_PDF_merge(num_files = len(datafiles_group), group = label, my_list = my_list, barplot = barplot)
        plt.savefig(f'C:/Users/sofia/Output_expe/washout/Washout_PDFs/{filename}.pdf') #PC
        #plt.savefig(f'C:/Users/sofia/Output_expe/washout/Washout_PDFs/end_cut/PYR-Nelson/{filename}.pdf') #PC
        print(f"{label} PDF saved")

    except Exception as e:
        print(f"Error doing group analysis for {label}: {e}")
 
    #useful for final PDF ##############################################################################

    final_dict[label]['mean'] = my_list['Diffs']['mean']
    final_dict[label]['std']  = my_list['Diffs']['std']
    final_dict[label]['sem']  = my_list['Diffs']['sem']

    final_barplot['End baseline'][label]['values'] = list_end_bsl
    final_barplot['End infusion'][label]['values'] = list_end_inf
    final_barplot['End wash'][label]['values']     = list_end_wash

    final_barplot['End baseline'][label]['mean']   = np.mean(list_end_bsl, axis=0)
    final_barplot['End infusion'][label]['mean']   = np.mean(list_end_inf, axis=0)
    final_barplot['End wash'][label]['mean']       = np.mean(list_end_wash, axis=0)
    
    final_barplot['End baseline'][label]['sem']    = np.std(list_end_bsl, axis=0)/np.sqrt(len(list_end_bsl))
    final_barplot['End infusion'][label]['sem']    = np.std(list_end_inf, axis=0)/np.sqrt(len(list_end_inf))
    final_barplot['End wash'][label]['sem']        = np.std(list_end_wash, axis=0)/np.sqrt(len(list_end_wash))

    final_barplot['End baseline'][label]['std']    = np.std(list_end_bsl, axis=0)
    final_barplot['End infusion'][label]['std']    = np.std(list_end_inf, axis=0)
    final_barplot['End wash'][label]['std']        = np.std(list_end_wash, axis=0)

    if label=='memantine': 
        
        final_barplot2['End wash']['values']      = list_end_wash
        final_barplot2['End wash long']['values'] = list_end_wash_
        final_barplot2['End wash']['mean']        = np.mean(list_end_wash, axis=0)
        final_barplot2['End wash long']['mean']   = np.mean(list_end_wash_, axis=0)  
        final_barplot2['End wash']['sem']         = np.std(list_end_wash, axis=0)/np.sqrt(len(list_end_wash))
        final_barplot2['End wash long']['sem']    = np.std(list_end_wash_, axis=0)/np.sqrt(len(list_end_wash_))
        final_barplot2['End wash']['std']         = np.std(list_end_wash, axis=0)
        final_barplot2['End wash long']['std']    = np.std(list_end_wash_, axis=0)

    final_num_files[label] = len(datafiles_group)
    
    return 0

def create_final_results_pdf(final_dict, final_barplot, final_num_files, concentration, colors, GROUPS, final_barplot2, debug=False):
    pdf = PdfPage(PDF_sheet = 'final', debug=debug )
    pdf.fill_final_results(final_dict, final_barplot, final_num_files, concentration, colors, GROUPS, final_barplot2)
    plt.savefig(f'C:/Users/sofia/Output_expe/washout/Washout_PDFs/final_results.pdf') #PC #plt.savefig(f'C:/Users/LauraGonzalez/Output_expe/Washout_PDFs/final_results.pdf') #in laptop
    #plt.savefig(f'C:/Users/sofia/Output_expe/washout/Washout_PDFs/end_cut/PYR-Nelson/final_results.pdf')
    print('final results figure saved')
    return 0

if __name__=='__main__':

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
                     "End wash"    : {"control"  : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "ketamine" : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "D-AP5"    : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "memantine": {'values' : None, 'mean': None, 'sem': None, 'std': None} }}
    
    final_barplot2 = {"End wash"      : {'values' : None, 'mean': None, 'sem': None, 'std': None},
                      "End wash long" : {'values' : None, 'mean': None, 'sem': None, 'std': None}}

    final_num_files = {"control"  : None, 
                       "ketamine" : None, 
                       "D-AP5"    : None, 
                       "memantine": None}
    
    concentration = {'ketamine' : '100uM', 
                     'D-AP5'    : '50uM', 
                     'control'  : '-', 
                     'memantine': '100uM'}
    
    colors = {'ketamine' : 'purple', 
              'D-AP5'    : 'orange', 
              'control'  : 'grey', 
              'memantine': 'gold'}
    
    GROUPS = ['control', 'ketamine','D-AP5','memantine']
    

    #Load and sort datafiles: ###################################################################################################
    
    files = find_nm_files(files_directory)
    #datafiles, datafiles_keta, datafiles_APV, datafiles_control = [], [], [], []
    datafiles, datafiles_keta, datafiles_APV, datafiles_control, datafiles_memantine = [], [], [], [], []   #make only 1 dict?
    
    # PDF creation for each individual file ######################################################################################
    debug1 = True
    infusion_start = []

    for file in files:
            print(file)     
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

    create_individual_pdf(datafiles, wash='all', debug=debug1)

    
    #PDF creation for the chosen groups: #########################################################################################
    debug2 = False

    if debug2: 
        print("Debug for group analysis")
        print("final dict : ")
        pprint.pprint(final_dict)
        print("datafiles keta : ")
        print(datafiles_keta)
        print("datafiles control : ")
        print(datafiles_control)
        print("datafiles AP5 : ")
        print(datafiles_APV)
        #print("datafiles memantine : ")
        #print(datafiles_memantine)


    create_group_pdf(datafiles_keta, "ketamine", "ketamine_merge", final_dict, final_barplot, final_num_files, final_barplot2, debug=debug2)
    create_group_pdf(datafiles_APV, "D-AP5", "D-AP5_merge", final_dict, final_barplot, final_num_files, final_barplot2, debug=debug2)
    create_group_pdf(datafiles_control, "control", "control_merge", final_dict, final_barplot, final_num_files, final_barplot2, debug=debug2)
    create_group_pdf(datafiles_memantine, "memantine", "memantine_merge", final_dict, final_barplot, final_num_files, final_barplot2, debug=debug2)  

        
    #PDF creation to compare groups: ##############################################################################################
    debug3 = False

    #pad arrays! find a more general solution
    inf_start = {'ketamine' : 10, 
                 'memantine': 6, 
                 'control': 10,
                 'D-AP5': 10}
    
    
    num_pad_before = inf_start["ketamine"]-inf_start["memantine"]  #10 -6 = 4
    num_pad_after = len(final_dict["memantine"]["mean"]) - len(final_dict["ketamine"]["mean"])  #63-50 = 13
    
    prepended_values = np.full((num_pad_before), np.nan, dtype=np.float16)
    posterior_values = np.full((num_pad_after), np.nan, dtype=np.float16)
    
    final_dict["memantine"]["mean"] = np.concatenate((prepended_values, final_dict["memantine"]["mean"].astype(np.float16)))
    final_dict["ketamine"]["mean"] = np.concatenate((final_dict["ketamine"]["mean"].astype(np.float16), posterior_values))
    final_dict["D-AP5"]["mean"] = np.concatenate((final_dict["D-AP5"]["mean"].astype(np.float16), posterior_values))
    final_dict["control"]["mean"] = np.concatenate((final_dict["control"]["mean"].astype(np.float16), posterior_values))

    final_dict["memantine"]["std"] = np.concatenate((prepended_values, final_dict["memantine"]["std"][0]))
    final_dict["ketamine"]["std"] = np.concatenate((final_dict["ketamine"]["std"][0].astype(np.float16), posterior_values))
    final_dict["D-AP5"]["std"] = np.concatenate((final_dict["D-AP5"]["std"][0].astype(np.float16), posterior_values))
    final_dict["control"]["std"] = np.concatenate((final_dict["control"]["std"][0].astype(np.float16), posterior_values))

    final_dict["memantine"]["sem"] = np.concatenate((prepended_values, final_dict["memantine"]["sem"][0].astype(np.float16)))
    final_dict["ketamine"]["sem"] = np.concatenate((final_dict["ketamine"]["sem"][0].astype(np.float16), posterior_values))
    final_dict["D-AP5"]["sem"] = np.concatenate((final_dict["D-AP5"]["sem"][0].astype(np.float16), posterior_values))
    final_dict["control"]["sem"] = np.concatenate((final_dict["control"]["sem"][0].astype(np.float16), posterior_values))
    
    if debug3: 
        print("Debug for final PDF")
        print("final dict : ")
        pprint.pprint(final_dict)
        print("final barplot ")
        pprint.pprint(final_barplot)

    create_final_results_pdf(final_dict, final_barplot, final_num_files, concentration, colors, GROUPS, final_barplot2, debug=debug3)
    

    