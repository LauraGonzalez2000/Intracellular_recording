import os
from PdfPage_washout import PdfPage
from washout_trace_analysis import DataFile_washout
import matplotlib.pylab as plt
import pandas as pd
import numpy as np

#folders
files_directory = 'C:/Users/LauraGonzalez/DATA/Washout_experiment/RAW-DATA-WASHOUT-q'
meta_info_directory = 'C:/Users/LauraGonzalez/Programming/Intracellular_recording/src/Files-q.csv' #in laptop

#for PC
#files_directory = 'D:\Internship_Rebola_ICM\EXP-recordings\RAW-DATA-WASHOUT-q'
#meta_info_directory = 'C:/Users/laura.gonzalez/Programming/Intracellular_recording/src/Files.csv' #in PC

#methods
def find_nm_files(root_folder):
    nm_paths = []
    
    # Walk through all directories and files in the root_folder
    for folder, _, files in os.walk(root_folder):
        # Check each file in the current directory
        for file in files:

            # Skip files with specific extensions
            if any(ext in file for ext in ['HDF5', 'txt', 'pdf', 'log', 'xlsx']):
                break
            # Construct the full path of the file
            file_path = os.path.join(folder, file)
            normalized_path = os.path.normpath(file_path)
            forward_slash_path = normalized_path.replace("\\", "/")
            nm_paths.append(forward_slash_path)
            #print('-', file)

    return nm_paths

def add_metadata(datafile):
    file_meta_info = open(meta_info_directory, 'r')  
    info_df = pd.read_csv(file_meta_info, header=0, sep=';')
    info_df_datafile = info_df.loc[info_df['Files'] == datafile.filename]
   
    datafile.infos['File'] = info_df_datafile["Files"].item()
    datafile.infos['Euthanize method'] = info_df_datafile["euthanize method"].item()
    datafile.infos['Holding (mV)'] = info_df_datafile["Holding (mV)"].item()
    datafile.infos['Infusion substance'] = info_df_datafile["infusion"].item()
    datafile.infos['Infusion concentration'] = info_df_datafile["infusion concentration"].item()
    datafile.infos['Infusion start'] = info_df_datafile["infusion start"].item()
    datafile.infos['Infusion end'] = info_df_datafile["infusion end"].item()
    datafile.infos['Group'] = info_df_datafile["Group"].item()

def merge_Ids(datafile, list_of_Ids): 
    Ids_datafile_ = datafile.get_Ids()
    Ids_datafile_m, _ = datafile.get_batches(Ids_datafile_, batch_size=6)
    list_of_Ids.append(Ids_datafile_m) 
    return 0

def merge_leaks(datafile, list_of_leaks): 
    leaks_datafile = datafile.get_baselines()
    leaks_datafile_m, _ = datafile.get_batches(leaks_datafile, batch_size=6)
    list_of_leaks.append(leaks_datafile_m) 
    return 0

def merge_diffs(datafile, list_of_diffs):
    diffs_datafile = datafile.batches_corr_diffs
    list_of_diffs.append(diffs_datafile)
    return 0

def merge_stats(datafile, list_of_bsl_m, list_of_inf_m, list_of_wash_m): 
    batches_c_diffs_mean,  batches_c_diffs_std  = datafile.get_batches(datafile.corr_diffs) #noise was removed
    norm_batches_corr_diffs, _ = datafile.normalize(batches_c_diffs_mean,  batches_c_diffs_std)

    subset1 = norm_batches_corr_diffs[5:10]
    subset2 = norm_batches_corr_diffs[12:17]
    subset3 = norm_batches_corr_diffs[45:50]
    
    bsl_m = np.mean(subset1)
    bsl_std = np.std(subset1)
    inf_m = np.mean(subset2)
    inf_std = np.std(subset2)
    wash_m = np.mean(subset3)
    wash_std = np.std(subset3)

    bsl_m_datafile, _, inf_m_datafile, _, wash_m_datafile, _ = bsl_m, bsl_std, inf_m, inf_std, wash_m, wash_std 
    list_of_bsl_m.append(bsl_m_datafile)
    list_of_inf_m.append(inf_m_datafile)
    list_of_wash_m.append(wash_m_datafile)
    return 0

def merge_info(datafile, list_of_Ids, list_of_leaks, list_of_diffs, list_of_bsl_m, list_of_inf_m, list_of_wash_m):
    merge_Ids(datafile, list_of_Ids)
    merge_leaks(datafile, list_of_leaks)
    merge_diffs(datafile, list_of_diffs)
    merge_stats(datafile, list_of_bsl_m, list_of_inf_m, list_of_wash_m)
    return 0

def get_avg_std(my_list):
    mean_list = np.mean(my_list, axis=0)
    std_list = np.std(my_list, axis=0)
    return mean_list, std_list

def create_individual_pdf(files, datafiles_keta, datafiles_APV, datafiles_control):
    for file in files:
        try:
            print(file)     
            datafile = DataFile_washout(file)
            add_metadata(datafile)   

            #save the datafile in the corresponding group
            if datafile.infos['Group'] == 'control': datafiles_control.append(datafile)
            elif datafile.infos['Group'] == 'KETA': datafiles_keta.append(datafile)
            elif datafile.infos['Group'] == 'APV': datafiles_APV.append(datafile)


            pdf = PdfPage(debug=False)
            pdf.fill_PDF(datafile, debug=False)
            #plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/washout/{datafile.filename}.pdf') #in PC
            plt.savefig(f'C:/Users/LauraGonzalez/DATA/PDFs/washout/{datafile.filename}.pdf') #in laptop
            print("File saved successfully :", file, '\n')
        except Exception as e:
            print(f"Error analysing this file : {e}")
            
    return 0

def create_group_pdf(datafiles_group, label, filename, final_dict, temp_barplot):
    try:
        num_files = len(datafiles_group)
        list_of_Ids, list_of_leaks, list_of_diffs, list_of_bsl_m, list_of_inf_m, list_of_wash_m = [], [], [], [], [], []

        for datafile in datafiles_group:
            merge_info(datafile, list_of_Ids, list_of_leaks, list_of_diffs, list_of_bsl_m, list_of_inf_m, list_of_wash_m)
        
        mean_Ids, std_Ids = get_avg_std(list_of_Ids)
        mean_leaks, std_leaks = get_avg_std(list_of_leaks)
        mean_diffs, std_diffs = get_avg_std(list_of_diffs)
        final_dict[label] = mean_diffs
        final_dict_std[label] = std_diffs

        mean_bsl, std_bsl = get_avg_std(list_of_bsl_m)
        mean_inf, std_inf = get_avg_std(list_of_inf_m)
        mean_wash, std_wash = get_avg_std(list_of_wash_m)
        barplot = {'Baseline (5 last)': mean_bsl, 'Infusion (5 last)': mean_inf, 'Washout (5 last)': mean_wash}
        temp_barplot.append(mean_bsl)
        temp_barplot.append(mean_inf)
        temp_barplot.append(mean_wash)

    
        pdf = PdfPage(debug=False)
        pdf.fill_PDF_merge(mean_diffs, std_diffs, num_files, label, mean_Ids, std_Ids, mean_leaks, std_leaks, barplot)
        #plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/washout/{filename}.pdf') #in PC
        plt.savefig(f'C:/Users/LauraGonzalez/DATA/PDFs/washout/{filename}.pdf') #in laptop
        print(f"{label} PDF saved")
    except Exception as e:
        print(f"Error doing group analysis for {label}: {e}")
    return 0

def final_results_pdf(final_dict, final_dict_std, final_barplot):
    pdf = PdfPage(debug=False, final=True)
    pdf.fill_final_results(final_dict, final_dict_std, final_barplot)
    plt.savefig(f'C:/Users/LauraGonzalez/DATA/PDFs/washout/final_results.pdf') #in laptop
    print('final results figure saved')
    return 0

if __name__=='__main__':
    files = find_nm_files(files_directory)
    datafiles_keta, datafiles_APV, datafiles_control  = [], [], []

    final_dict = {"ketamine": None, "D-AP5": None, "control": None}
    final_dict_std = {"ketamine": None, "D-AP5": None, "control": None}
    temp_barplot = []
    
    #PDF creation individual files
    create_individual_pdf(files, datafiles_keta, datafiles_APV, datafiles_control)
    #PDF creation per group
    create_group_pdf(datafiles_keta, "ketamine", "ketamine_merge", final_dict, temp_barplot)
    create_group_pdf(datafiles_APV, "D-AP5", "D-AP5_merge", final_dict, temp_barplot)
    create_group_pdf(datafiles_control, "control", "control_merge", final_dict, temp_barplot)
    #PDF creation to compare groups
    print(final_dict_std)
    final_barplot = {'Baseline keta (5 last)': temp_barplot[0], 
                     'Infusion keta (5 last)': temp_barplot[1], 
                     'Washout keta (5 last)': temp_barplot[2],
                     'Baseline D-AP5 (5 last)': temp_barplot[3], 
                     'Infusion D-AP5 (5 last)': temp_barplot[4], 
                     'Washout D-AP5 (5 last)': temp_barplot[5],
                     'Baseline control (5 last)': temp_barplot[6], 
                     'Infusion control (5 last)': temp_barplot[7], 
                     'Washout control (5 last)': temp_barplot[8]}

    print(final_barplot)
    final_results_pdf(final_dict, final_dict_std, final_barplot)
