
import os

#from PdfPage import PdfPage
from PdfPage_washout import PdfPage
#from trace_analysis import DataFile
from washout_trace_analysis import DataFile_washout
from igor2.packed import load as loadpxp
import matplotlib.pylab as plt
import pandas as pd
from openpyxl.utils import get_column_letter

import numpy as np

files_directory = 'D:\Internship_Rebola_ICM\EXP-recordings\RAW-DATA-TO-ANALYSE-WASHOUT-q'
meta_info_directory = 'C:/Users/laura.gonzalez/Programming/Intracellular_recording/src/Files1q.csv'

#from openpyxl import load_workbook

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
    file_meta_info = open('C:/Users/laura.gonzalez/Programming/Intracellular_recording/src/Files1.csv', 'r')  
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

def avg_std_diffs(group_datafiles):
    #print("group ",group_datafiles," len group ",len(group_datafiles))
    list_of_diffs = []
    for datafile in group_datafiles:
        diffs_datafile = datafile.get_diffs()
        list_of_diffs.append(diffs_datafile)

        #print("num recordings in datafile", len(datafile.recordings))
        #print(diff)
        #print("len diff", len(diff))
        
    #print("diffs ",diffs)
    #print("len diffs ",len(diffs))

    #ensure same size
    max_length = max(len(sub_array) for sub_array in list_of_diffs)
    padded_diffs = np.array([sub_array + [np.nan]*(max_length - len(sub_array)) for sub_array in list_of_diffs])

    mean_list_of_diffs = np.mean(padded_diffs, axis=0)
    std_list_of_diffs = np.std(padded_diffs, axis=0)

    #print("mean diffs ", mean_list_of_diffs)
    #print("len mean diffs ", len(mean_list_of_diffs))
  
    return mean_list_of_diffs, std_list_of_diffs

def avg_std_Ids(group_datafiles):
    list_of_Ids = []
    for datafile in group_datafiles:
        Ids_datafile = datafile.get_Ids()
        list_of_Ids.append(Ids_datafile)
    
    max_length = max(len(sub_array) for sub_array in list_of_Ids)
    padded_Ids = np.array([sub_array + [np.nan]*(max_length - len(sub_array)) for sub_array in list_of_Ids])

    mean_list_of_Ids = np.mean(padded_Ids, axis=0)
    std_list_of_Ids = np.std(padded_Ids, axis=0)
    return mean_list_of_Ids, std_list_of_Ids

def avg_std_stats(group_datafiles): 

    list_of_bsl_m = []
    list_of_inf_m = []
    list_of_wash_m = []

    for datafile in group_datafiles:
        bsl_m_datafile, _, inf_m_datafile, _, wash_m_datafile, _ = datafile.get_values_barplot()
        list_of_bsl_m.append(bsl_m_datafile)
        list_of_inf_m.append(inf_m_datafile)
        list_of_wash_m.append(wash_m_datafile)

    try:
        max_length = max(len(sub_array) for sub_array in list_of_bsl_m)
        max_length = max(len(sub_array) for sub_array in list_of_inf_m)
        max_length = max(len(sub_array) for sub_array in list_of_wash_m)

        padded_bsl_m = np.array([sub_array + [np.nan]*(max_length - len(sub_array)) for sub_array in list_of_bsl_m])
        padded_inf_m = np.array([sub_array + [np.nan]*(max_length - len(sub_array)) for sub_array in list_of_inf_m])
        padded_wash_m = np.array([sub_array + [np.nan]*(max_length - len(sub_array)) for sub_array in list_of_wash_m])

        mean_list_of_bsl_m = np.mean(padded_bsl_m, axis=0)
        mean_list_of_inf_m = np.mean(padded_inf_m, axis=0)
        mean_list_of_wash_m = np.mean(padded_wash_m, axis=0)

        std_list_of_bsl_m = np.std(padded_bsl_m, axis=0)
        std_list_of_inf_m = np.std(padded_inf_m, axis=0)
        std_list_of_wash_m = np.std(padded_wash_m, axis=0)

    except:
        mean_list_of_bsl_m = np.mean(list_of_bsl_m, axis=0)
        mean_list_of_inf_m = np.mean(list_of_inf_m, axis=0)
        mean_list_of_wash_m = np.mean(list_of_wash_m, axis=0)

        std_list_of_bsl_m = np.std(list_of_bsl_m, axis=0)
        std_list_of_inf_m = np.std(list_of_inf_m, axis=0)
        std_list_of_wash_m = np.std(list_of_wash_m, axis=0)

    return mean_list_of_bsl_m, std_list_of_bsl_m, mean_list_of_inf_m, std_list_of_inf_m, mean_list_of_wash_m, std_list_of_wash_m



###### MAIN ######################################################


files = find_nm_files(files_directory)
file_meta_info = open(meta_info_directory, 'r')  
info_df = pd.read_csv(file_meta_info, header=0, sep=';')

datafiles_keta = []
datafiles_APV = []
datafiles_control = []


#PDF creation per file

for file in files:
    try:
        
        print(file)       
        datafile = DataFile_washout(file)
        add_metadata(datafile)     
        #print(datafile.infos['Group']) 
        
        if datafile.infos['Group'] == 'control':
            datafiles_control.append(datafile)
        elif datafile.infos['Group'] == 'KETA':
            datafiles_keta.append(datafile)
        elif datafile.infos['Group'] == 'APV':
            datafiles_APV.append(datafile)

        pdf = PdfPage(debug=False)
        pdf.fill_PDF(datafile, debug=False)
        plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/washout/{datafile.filename}.pdf')
        print("File saved successfully :", file, '\n')

    except Exception as e:
        print(f"Error analysing this file : {e}")
    

'''
# PDF for APV
num_files1 = len(datafiles_APV)
mean_diffs_APV, std_diffs_APV = avg_std_diffs(datafiles_APV)
mean_Ids_APV, std_Ids_APV = avg_std_Ids(datafiles_APV)
baseline_m, bsl_std, inf_m, inf_std, wash_m, wash_std = avg_std_stats(datafiles_APV)
barplot = {'Baseline (5 last)':baseline_m, 'Infusion (5 last)':inf_m, 'Washout (5 last)':wash_m}
pdf1 = PdfPage(debug=False)
pdf1.fill_PDF_merge(mean_diffs_APV, std_diffs_APV, num_files1, "D-AP5", mean_Ids_APV, std_Ids_APV, barplot)
plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/washout/DAPV_merge.pdf')

# PDF for control
num_files2 = len(datafiles_control)
mean_diffs_control, std_diffs_control = avg_std_diffs(datafiles_control)
mean_Ids_control, std_Ids_control = avg_std_Ids(datafiles_control)
baseline_m, bsl_std, inf_m, inf_std, wash_m, wash_std = avg_std_stats(datafiles_control)
barplot = {'Baseline (5 last)':baseline_m, 'Infusion (5 last)':inf_m, 'Washout (5 last)':wash_m}
pdf2 = PdfPage(debug=False)
pdf2.fill_PDF_merge(mean_diffs_control, std_diffs_control, num_files2, "control",mean_Ids_control, std_Ids_control, barplot )
plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/washout/control_merge.pdf')

# PDF for keta
num_files3 = len(datafiles_keta)
mean_diffs_keta, std_diffs_keta = avg_std_diffs(datafiles_keta)
mean_Ids_keta, std_Ids_keta = avg_std_Ids(datafiles_keta)
baseline_m, bsl_std, inf_m, inf_std, wash_m, wash_std = avg_std_stats(datafiles_keta)
barplot = {'Baseline (5 last)':baseline_m, 'Infusion (5 last)':inf_m, 'Washout (5 last)':wash_m}
pdf3 = PdfPage(debug=False)
pdf3.fill_PDF_merge(mean_diffs_keta, std_diffs_keta, num_files3, "ketamine", mean_Ids_keta, std_Ids_keta, barplot)
plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/washout/keta_merge.pdf')
'''



#Execute only if the Python script is being executed as the main program. 
'''
if __name__=='__main__':
    
    #filename = os.path.join(os.path.expanduser('~'), 'DATA', 'Dataset1', 'nm12Jun2024c0_000_AMPA.pdf')
    datafile = DataFile('D:/Internship_Rebola_ICM/DATA_TO_ANALYSE/nm28May2024c1/nm28May2024c1_001.pxp')
    #datafile = DataFile('C:/Users/laura.gonzalez/DATA/RAW_DATA/model_cell/nm24Jun2024c0_000.pxp')
    pdf = PdfPage(debug=True)
    pdf.fill_PDF(datafile, debug=True)
    plt.show()
'''

'''
print(info_df)
Files_APV = info_df.loc[info_df['Group'] == 'APV']['Files']
Files_control = info_df.loc[info_df['Group'] == 'control']['Files']
Files_keta = info_df.loc[info_df['Group'] == 'KETA']['Files']
print(Files_APV)
print(Files_control)
print(Files_keta)
'''



'''
fig, ax = plt.subplots()
        ax.plot(batches_m_norm, marker="o", linewidth=0.5, markersize=2)
        ax.errorbar(range(len(batches_m_norm)), batches_m_norm, yerr=batches_std_norm, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
        ax.set_xlim(-1, 50 )
        ax.set_ylim( 0, 140)
        ax.set_ylabel("Normalized NMDAR-eEPSCs (%)")
        ax.set_xlabel("time (min)")
        ax.set_xticks(np.arange(0, 51, 5))
        ax.axvspan(info_df["infusion start"][i], info_df["infusion end"][i], color='lightgrey')
'''


#average_diffs(datafiles_control)


'''
for file in files:
    datafile = DataFile_washout(file)
    print(datafile.filename)
    print(info_df.loc[info_df['Files'] == datafile.filename])
    file_group = info_df.loc[info_df['Files'] == datafile.filename]['Group']
    print(file_group)

    if file_group == 'control':
        datafiles_control.append(datafile)
    elif file_group == 'KETA':
        datafiles_keta.append(datafile)
    elif file_group == 'APV':

###averages


'''