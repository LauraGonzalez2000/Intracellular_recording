
import os

#from PdfPage import PdfPage
from PdfPage_washout import PdfPage
#from trace_analysis import DataFile
from washout_trace_analysis import DataFile_washout
from igor2.packed import load as loadpxp
import pprint
import matplotlib.pylab as plt
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter

import numpy as np

#from openpyxl import load_workbook

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

def add_metadata(datafile, i):  #change to not need i
    file_meta_info = open('C:/Users/laura.gonzalez/Programming/Intracellular_recording/src/Files1q.csv', 'r')  
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

def average_diffs(group_datafiles):
    diffs = []
    print("group ",group_datafiles," len group ",len(group_datafiles))
    for datafile in group_datafiles:
        print("num recordings in datafile", len(datafile.recordings))
        diff = datafile.get_diffs3()
        #print(diff)
        print("len diff", len(diff))
        diffs.append(diff)

    #print("diffs ",diffs)
    #print("len diffs ",len(diffs))

    #ensure same size
    max_length = max(len(sub_array) for sub_array in diffs)
    padded_diffs = np.array([sub_array + [np.nan]*(max_length - len(sub_array)) for sub_array in diffs])


    mean_diffs = np.mean( padded_diffs, axis=0 )
        #mean_diffs = np.mean(diffs)
    print("mean diffs ", mean_diffs)
    print("len mean diffs ", len(mean_diffs))
  
    return mean_diffs


###### MAIN ######################################################

directory = 'D:\Internship_Rebola_ICM\EXP-recordings\RAW-DATA-TO-ANALYSE-WASHOUT-q'
files = find_nm_files(directory)


file_meta_info = open('C:/Users/laura.gonzalez/Programming/Intracellular_recording/src/Files1q.csv', 'r')  
info_df = pd.read_csv(file_meta_info, header=0, sep=';')

datafiles_keta = []
datafiles_APV = []
datafiles_control = []


#PDF creation per file

i=0
for file in files:
    try:
        print(file)
        datafile = DataFile_washout(file)
        add_metadata(datafile, i)
        
        if datafile.infos['Group'] == 'control':
            datafiles_control.append(datafile)
        elif datafile.infos['Group'] == 'KETA':
            datafiles_keta.append(datafile)
        elif datafile.infos['Group'] == 'APV':
            datafiles_APV.append(datafile)

        #pdf = PdfPage(debug=False)
        #pdf.fill_PDF(datafile, debug=False)
        #plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/washout/{datafile.filename}.pdf')
        #print("File saved successfully :", file, '\n')

    except Exception as e:
        print(f"Error analysing this file : {e}")
    i+=1


mean_diffs_APV = average_diffs(datafiles_APV)
mean_diffs_control = average_diffs(datafiles_control)
mean_diffs_keta = average_diffs(datafiles_keta)

# Create a figure and subplots
fig, axs = plt.subplots(3, 1, figsize=(10, 15))

# Plot for APV
axs[0].plot(mean_diffs_APV, marker='o', linestyle='-', color='b')
axs[0].set_title('Mean Differences - APV')
axs[0].set_xlabel('Index')
axs[0].set_ylabel('Mean Difference')
axs[0].grid(True)

# Plot for control
axs[1].plot(mean_diffs_control, marker='o', linestyle='-', color='b')
axs[1].set_title('Mean Differences - Control')
axs[1].set_xlabel('Index')
axs[1].set_ylabel('Mean Difference')
axs[1].grid(True)

# Plot for keta
axs[2].plot(mean_diffs_keta, marker='o', linestyle='-', color='b')
axs[2].set_title('Mean Differences - Keta')
axs[2].set_xlabel('Index')
axs[2].set_ylabel('Mean Difference')
axs[2].grid(True)

# Adjust layout and show plot
plt.tight_layout()
plt.show()






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