import os
from PdfPage_wash import PdfPage
from trace_analysis_wash import DataFile_washout
import matplotlib.pylab as plt
import numpy as np

import pprint

#keep this aborescence if program used in other computers
base_path = os.path.join(os.path.expanduser('~'), 'DATA','In_Vitro_experiments', 'Washout_experiment') 
base_path_output = os.path.join(os.path.expanduser('~'), 'Output_expe', 'washout', 'Washout_PDFs') 
#directory = "RAW-DATA-WASHOUT-PYR"
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

def merge_info(datafile, my_list, list_of_bsl_m, list_of_inf_m, list_of_wash_m):
    for key in my_list:

        if key=='Ids':

            metric_datafile = datafile.get_Ids()
            metric_datafile_m, _ = datafile.get_batches(metric_datafile, batch_size=6)
        elif key=='Leaks':
            
            metric_datafile = datafile.get_baselines()
            metric_datafile_m, _ = datafile.get_batches(metric_datafile, batch_size=6)
        elif key=='Diffs':
        
            metric_datafile_m = datafile.batches_corr_diffs       

        print("metric_datafile_m  ", metric_datafile_m)
        my_list[key]['mean'].append(metric_datafile_m)


    ############################################################################################
    
    batches_c_diffs_mean,  batches_c_diffs_std  = datafile.get_batches(datafile.corr_diffs) #noise was removed
    norm_batches_corr_diffs, _ = datafile.normalize(batches_c_diffs_mean,  batches_c_diffs_std)
    
    try: 
        if datafile.infos['Infusion start']=='-':   #control
            list_of_bsl_m.append(np.mean(norm_batches_corr_diffs[5:10]))
            list_of_inf_m.append(np.mean(norm_batches_corr_diffs[12:17]))
            list_of_wash_m.append(np.mean(norm_batches_corr_diffs[45:50]))
            #print("new values for barplot")

        else: 
            start = int(datafile.infos['Infusion start'])
            stop = int(datafile.infos['Infusion end'])
            list_of_bsl_m.append(np.mean(norm_batches_corr_diffs[start-4:start+1]))
            list_of_inf_m.append(np.mean(norm_batches_corr_diffs[stop-2:stop+2]))
            list_of_wash_m.append(np.mean(norm_batches_corr_diffs[-5:-1]))
            #print("new values for barplot")
    
    except Exception as e: 

        list_of_bsl_m.append(np.mean(norm_batches_corr_diffs[5:10]))
        list_of_inf_m.append(np.mean(norm_batches_corr_diffs[12:17]))
        list_of_wash_m.append(np.mean(norm_batches_corr_diffs[45:50]))
        print(f"old values for barplot because : {e}")  

    return 0

def create_individual_pdf(datafiles, debug=False):
    for datafile in datafiles:
        try:
            pdf = PdfPage(PDF_sheet = 'individual', debug=debug )
            pdf.fill_PDF(datafile, debug=debug)
            plt.savefig(f'C:/Users/laura.gonzalez/Output_expe/washout/Washout_PDFs/{datafile.filename}.pdf')
            print("OK File saved successfully")
        except Exception as e:
            print(f"Error analysing this file : {e}")      
    return 0

def create_group_pdf(datafiles_group, label, filename, final_dict, final_barplot, final_num_files, debug=False):
    try:
        my_list = {'Ids'  : {'mean': [], 'std': [], 'sem': []},
                   'Leaks': {'mean': [], 'std': [], 'sem': []}, 
                   'Diffs': {'mean': [], 'std': [], 'sem': []}}
        

        list_of_bsl_m, list_of_inf_m, list_of_wash_m = [], [], []

        for datafile in datafiles_group:
            merge_info(datafile, my_list, list_of_bsl_m, list_of_inf_m, list_of_wash_m)
        
        for key in my_list:
            #print("my_list[key]['mean'] ", my_list[key]['mean'])
            metric_datafile_std = np.std(my_list[key]['mean'], axis=0)   #std of the different files's mean for each one of the 50 positions  
            metric_datafile_sem = np.std(my_list[key]['mean'], axis=0)/np.sqrt(len(my_list[key]['mean'])) #sem of the different files's mean for each one of the 50 positions  
            my_list[key]['std'].append(metric_datafile_std)
            my_list[key]['sem'].append(metric_datafile_sem)
            my_list[key]['mean'] = np.mean(my_list[key]['mean'], axis=0)  #updates the mean!!! #mean of the different files's mean for each one of the 50 positions  
            
        if debug : 
            #print(" datafiles_group  ", datafiles_group)
            #print("Ids, Leaks, Diffs that are given for the pdf ")
            pprint.pprint(my_list)
        
        ################################################################################

        mean_bsl,  std_bsl,  sem_bsl  = np.mean(list_of_bsl_m, axis=0),  np.std(list_of_bsl_m, axis=0),  np.std(list_of_bsl_m, axis=0)/np.sqrt(len(list_of_bsl_m))
        mean_inf,  std_inf,  sem_inf  = np.mean(list_of_inf_m, axis=0),  np.std(list_of_inf_m, axis=0),  np.std(list_of_inf_m, axis=0)/np.sqrt(len(list_of_inf_m))
        mean_wash, std_wash, sem_wash = np.mean(list_of_wash_m, axis=0), np.std(list_of_wash_m, axis=0), np.std(list_of_wash_m, axis=0)/np.sqrt(len(list_of_wash_m))
        
        barplot = {'End baseline' : {'values': list_of_bsl_m,  'mean' : mean_bsl, 'sem': sem_bsl,  'std': std_bsl},
                   'End infusion': {'values': list_of_inf_m,  'mean' : mean_inf, 'sem': sem_inf,  'std': std_inf},
                   'End wash': {'values': list_of_wash_m, 'mean' : mean_wash,'sem': sem_wash, 'std': std_wash}}
        
        #################################################################################
        
        pdf = PdfPage(PDF_sheet = 'group analysis', debug=False )

        #pprint.pprint("my_list" , my_list)
        pdf.fill_PDF_merge(num_files = len(datafiles_group), group = label, my_list = my_list, barplot = barplot)
        plt.savefig(f'C:/Users/laura.gonzalez/Output_expe/washout/Washout_PDFs/{filename}.pdf') #PC
        print(f"{label} PDF saved")

    except Exception as e:
        print(f"Error doing group analysis for {label}: {e}")
 
    #useful for final PDF ##############################################################################

    final_dict[label]['mean'] = my_list['Diffs']['mean']
    final_dict[label]['std'] = np.std(my_list['Diffs']['mean'], axis=0)
    final_dict[label]['sem'] = np.std(my_list['Diffs']['mean'], axis=0)/np.sqrt(len(my_list['Diffs']['mean']))


    final_barplot['End baseline'][label]['values'] = list_of_bsl_m
    final_barplot['End infusion'][label]['values'] = list_of_inf_m
    final_barplot['End wash'][label]['values']     = list_of_wash_m

    final_barplot['End baseline'][label]['mean']   = mean_bsl
    final_barplot['End infusion'][label]['mean']   = mean_inf
    final_barplot['End wash'][label]['mean']       = mean_wash

    final_barplot['End baseline'][label]['sem']    = sem_bsl
    final_barplot['End infusion'][label]['sem']    = sem_inf
    final_barplot['End wash'][label]['sem']        = sem_wash

    final_barplot['End baseline'][label]['std']    = std_bsl
    final_barplot['End infusion'][label]['std']    = std_inf
    final_barplot['End wash'][label]['std']        = std_wash

    final_num_files[label] = len(datafiles_group)
    
    return 0

def create_final_results_pdf(final_dict, final_barplot, final_num_files, concentration, colors, GROUPS, debug=False):
    pdf = PdfPage(PDF_sheet = 'final', debug=debug )
    pdf.fill_final_results(final_dict, final_barplot, final_num_files, concentration, colors, GROUPS)
    plt.savefig(f'C:/Users/laura.gonzalez/Output_expe/washout/Washout_PDFs/final_results.pdf') #PC #plt.savefig(f'C:/Users/LauraGonzalez/Output_expe/Washout_PDFs/final_results.pdf') #in laptop
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
                     "End wash" : {    "control"  : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "ketamine" : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "D-AP5"    : {'values' : None, 'mean': None, 'sem': None, 'std': None}, 
                                       "memantine": {'values' : None, 'mean': None, 'sem': None, 'std': None} }}

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
    datafiles, datafiles_keta, datafiles_APV, datafiles_control, datafiles_memantine = [], [], [], [], []   #make only 1 dict?
    
    # PDF creation for each individual file ######################################################################################
    debug1 = True

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
            

    create_individual_pdf(datafiles, debug=debug1)

    
    #PDF creation for the chosen groups: #########################################################################################
    debug2 = True

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
        print("datafiles memantine : ")
        print(datafiles_memantine)


    create_group_pdf(datafiles_keta, "ketamine", "ketamine_merge", final_dict, final_barplot, final_num_files, debug=debug2)
    create_group_pdf(datafiles_APV, "D-AP5", "D-AP5_merge", final_dict, final_barplot, final_num_files, debug=debug2)
    create_group_pdf(datafiles_control, "control", "control_merge", final_dict, final_barplot, final_num_files, debug=debug2)
    create_group_pdf(datafiles_memantine, "memantine", "memantine_merge", final_dict, final_barplot, final_num_files, debug=debug2)  

        
    #PDF creation to compare groups: ##############################################################################################
    debug3 = False

    if debug3: 
        print("Debug for final PDF")
        print("final barplot")
        print(final_barplot)
    
    create_final_results_pdf(final_dict, final_barplot, final_num_files, concentration, colors, GROUPS, debug=debug3)
    
    