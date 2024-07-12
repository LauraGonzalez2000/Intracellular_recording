
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

def add_metadata(datafile, i):
    file_meta_info = open('C:/Users/laura.gonzalez/Programming/Intracellular_recording/src/Files1.csv', 'r')  
    info_df = pd.read_csv(file_meta_info, header=0, sep=';')
    
    datafile.infos['File'] = info_df["Files"][i]
    datafile.infos['Euthanize method'] = info_df["euthanize method"][i]
    datafile.infos['Holding (mV)'] = info_df["Holding (mV)"][i]
    datafile.infos['Infusion substance'] = info_df["infusion"][i]
    datafile.infos['Infusion concentration'] = info_df["infusion concentration"][i]
    datafile.infos['Infusion start'] = info_df["infusion start"][i]
    datafile.infos['Infusion end'] = info_df["infusion end"][i]
      

###### MAIN ######################################################

directory = 'D:\Internship_Rebola_ICM\EXP-recordings\RAW-DATA-TO-ANALYSE-WASHOUT'
files = find_nm_files(directory)


#PDF creation per file
i=0
for file in files:
    try:
        print(file)
        datafile = DataFile_washout(file)
        add_metadata(datafile, i)
        #print(datafile.infos)
        pdf = PdfPage(debug=False)
        pdf.fill_PDF(datafile, debug=False)
        plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/{datafile.filename}.pdf')
        print("File saved successfully :", file, '\n')

    except Exception as e:
        print(f"Error analysing this file : {e}")
    i+=1



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
