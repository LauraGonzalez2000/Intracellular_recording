import os
from trace_analysis_ratio import DataFile
from PdfPage_ratio import PdfPage
import matplotlib.pylab as plt

files_directory = 'C:/Users/laura.gonzalez/DATA/Ratio_experiment/RAW_DATA_AMPA_NMDA_RATIO-bis'

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

    return nm_paths

def get_datafiles(files):
    datafiles = []
    for file in files:
        try:
            datafile = DataFile(file)
            datafiles.append(datafile)
        except Exception as e:
            print(f"Error getting this file : {e}")
    return datafiles


if __name__=='__main__':
    
    files = find_nm_files(files_directory)
    datafiles = get_datafiles(files)

    data_list = []
    #PDF creation per file
    for datafile in datafiles:
        try:
            pdf = PdfPage(debug=False)
            pdf.fill_PDF(datafile, debug=False)
            plt.savefig(f'C:/Users/laura.gonzalez/Output_expe/Ratio_bis_PDFs/{datafile.filename}.pdf')  #plt.savefig(f'C:/Users/LauraGonzalez/Output_expe/Ratio_PDFs/{datafile.filename}.pdf') #laptop
            print("Individual PDF File saved successfully :", datafile.filename, '\n')

            data_dict = {'Filename': datafile.filename,
                            'Id (A)': datafile.Id_A,
                            'Rm (Ohm)': datafile.Rm,
                            'Ra (Ohm)': datafile.Ra,
                            'Cm (F)': datafile.Cm,
                            'Peak type' : datafile.type,
                            'Amplitude response 1 (nA)': datafile.amp_resp1,
                            'Amplitude response 2 (nA)': datafile.amp_resp2,
                            'Paired pulse ratio Amp2/Amp1': datafile.PPR,
                            'Rise_time 10-90% (ms)': datafile.rise_time,
                            'Decay time 50% (ms)': datafile.decay_time,
                            'Group': datafile.infos['Euthanize method']}
            data_list.append(data_dict)
            
        except Exception as e:
            print(f"Error creating the individual PDF file : {e}")



