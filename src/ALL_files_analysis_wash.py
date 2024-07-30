
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

files_directory = 'D:\Internship_Rebola_ICM\EXP-recordings\RAW-DATA-TO-ANALYSE-WASHOUT'
meta_info_directory = 'C:/Users/laura.gonzalez/Programming/Intracellular_recording/src/Files1.csv'

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

def avg_std_Ids(group_datafiles): #to fix!!!
    list_of_Ids = []
    for datafile in group_datafiles:
        Ids_datafile = datafile.get_Ids()
        value = np.mean(Ids_datafile, axis=1) #why size 7000 and not 1? Not normal to have to do a mean here
        list_of_Ids.append(value) 

    mean_list_of_Ids = np.mean(list_of_Ids, axis=0)
    std_list_of_Ids = np.std(list_of_Ids, axis=0)

    return mean_list_of_Ids, std_list_of_Ids

def avg_std_leaks(group_datafiles):
    list_of_leaks = []
    for datafile in group_datafiles:
        leaks_datafile = datafile.get_baselines()
        value = np.mean(leaks_datafile, axis=1)#why size 7000 and not 1? Not normal to have to do a mean here
        #print("value", value)
        list_of_leaks.append(value) 

    value2 = np.mean(list_of_leaks, axis=0)
    #print("value2", value2)
    mean_list_of_leaks = value2

    std_list_of_leaks = np.std(list_of_leaks, axis=0)

    return mean_list_of_leaks, std_list_of_leaks

def avg_std_diffs(group_datafiles):
    list_of_diffs = []
    for datafile in group_datafiles:
        diffs_datafile = datafile.get_diffs()
        #print(diffs_datafile)
        list_of_diffs.append(diffs_datafile)

    #ensure same size
    max_length = max(len(sub_array) for sub_array in list_of_diffs)
    padded_diffs = np.array([sub_array + [np.nan]*(max_length - len(sub_array)) for sub_array in list_of_diffs])

    mean_list_of_diffs = np.mean(padded_diffs, axis=0)
    #print(mean_list_of_diffs )
    std_list_of_diffs = np.std(padded_diffs, axis=0)

    return mean_list_of_diffs, std_list_of_diffs

def avg_std_stats(group_datafiles): 

    list_of_bsl_m = []
    list_of_inf_m = []
    list_of_wash_m = []

    for datafile in group_datafiles:

        diffs_c = datafile.corr_diffs #noise was removed here
        batches_diff_m, _ = datafile.get_batches(diffs_c)

        subset1 = batches_diff_m[5:10]
        subset2 = batches_diff_m[12:17]
        subset3 = batches_diff_m[45:50]
    
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
        #print("end baseline", mean_list_of_bsl_m)
        #print("end infusion", mean_list_of_inf_m)
        #print("end washout", mean_list_of_wash_m)

    return mean_list_of_bsl_m, std_list_of_bsl_m, mean_list_of_inf_m, std_list_of_inf_m, mean_list_of_wash_m, std_list_of_wash_m

def create_group_pdf(datafiles, label, filename):
    try:
        num_files = len(datafiles)
        mean_diffs, std_diffs = avg_std_diffs(datafiles)
        mean_Ids, std_Ids = avg_std_Ids(datafiles)
        mean_leaks, std_leaks = avg_std_leaks(datafiles)
        baseline_m, bsl_std, inf_m, inf_std, wash_m, wash_std = avg_std_stats(datafiles)
        barplot = {'Baseline (5 last)': baseline_m, 'Infusion (5 last)': inf_m, 'Washout (5 last)': wash_m}
        
        pdf = PdfPage(debug=False)
        pdf.fill_PDF_merge(mean_diffs, std_diffs, num_files, label, mean_Ids, std_Ids, mean_leaks, std_leaks, barplot)
        plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/washout/{filename}.pdf')
        print(f"{label} PDF saved")
    except Exception as e:
        print(f"Error doing group analysis for {label}: {e}")


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
    


create_group_pdf(datafiles_APV, "D-AP5", "DAPV_merge")
create_group_pdf(datafiles_control, "control", "control_merge")
create_group_pdf(datafiles_keta, "ketamine", "keta_merge")


'''
try: 
    # PDF for APV
    num_files1 = len(datafiles_APV)
    mean_diffs_APV, std_diffs_APV = avg_std_diffs(datafiles_APV)
    mean_Ids_APV, std_Ids_APV = avg_std_Ids(datafiles_APV)
    mean_leaks_APV, std_leaks_APV = avg_std_leaks(datafiles_APV)
    baseline_m, bsl_std, inf_m, inf_std, wash_m, wash_std = avg_std_stats(datafiles_APV)
    barplot = {'Baseline (5 last)':baseline_m, 'Infusion (5 last)':inf_m, 'Washout (5 last)':wash_m}
    pdf1 = PdfPage(debug=False)
    pdf1.fill_PDF_merge(mean_diffs_APV, std_diffs_APV, num_files1, "D-AP5", mean_Ids_APV, std_Ids_APV, mean_leaks_APV, std_leaks_APV, barplot)
    plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/washout/DAPV_merge.pdf')
    print("DAP5 PDF saved")
except Exception as e:
     print(f"Error doing group analysis for DAP5 : {e}")

try: 
    # PDF for control
    num_files2 = len(datafiles_control)
    mean_diffs_control, std_diffs_control = avg_std_diffs(datafiles_control)
    mean_Ids_control, std_Ids_control = avg_std_Ids(datafiles_control)
    mean_leaks_control, std_leaks_control = avg_std_leaks(datafiles_control)
    baseline_m, bsl_std, inf_m, inf_std, wash_m, wash_std = avg_std_stats(datafiles_control)
    barplot = {'Baseline (5 last)':baseline_m, 'Infusion (5 last)':inf_m, 'Washout (5 last)':wash_m}
    pdf2 = PdfPage(debug=False)
    pdf2.fill_PDF_merge(mean_diffs_control, std_diffs_control, num_files2, "control", mean_Ids_control, std_Ids_control, mean_leaks_control, std_leaks_control, barplot )
    plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/washout/control_merge.pdf')
    print("control PDF saved")
except Exception as e:
     print(f"Error doing group analysis for control : {e}")

try:
    # PDF for keta
    num_files3 = len(datafiles_keta)
    mean_diffs_keta, std_diffs_keta = avg_std_diffs(datafiles_keta)
    mean_Ids_keta, std_Ids_keta = avg_std_Ids(datafiles_keta)
    mean_leaks_keta, std_leaks_keta = avg_std_leaks(datafiles_keta)
    baseline_m, bsl_std, inf_m, inf_std, wash_m, wash_std = avg_std_stats(datafiles_keta)
    barplot = {'Baseline (5 last)':baseline_m, 'Infusion (5 last)':inf_m, 'Washout (5 last)':wash_m}
    pdf3 = PdfPage(debug=False)
    pdf3.fill_PDF_merge(mean_diffs_keta, std_diffs_keta, num_files3, "ketamine", mean_Ids_keta, std_Ids_keta, mean_leaks_keta, std_leaks_keta, barplot)
    plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/washout/keta_merge.pdf')
    print("keta PDF saved")
except Exception as e:
     print(f"Error doing group analysis for keta : {e}")
'''



'''
#Execute only if the Python script is being executed as the main program. 
if __name__=='__main__':
    #filename = os.path.join(os.path.expanduser('~'), 'DATA', 'Dataset1', 'nm12Jun2024c0_000_AMPA.pdf')
    datafile = DataFile('D:/Internship_Rebola_ICM/DATA_TO_ANALYSE/nm28May2024c1/nm28May2024c1_001.pxp')
    #datafile = DataFile('C:/Users/laura.gonzalez/DATA/RAW_DATA/model_cell/nm24Jun2024c0_000.pxp')
    pdf = PdfPage(debug=True)
    pdf.fill_PDF(datafile, debug=True)
    plt.show()
'''
