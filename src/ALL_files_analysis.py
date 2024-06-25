
import os

from PdfPage import PdfPage
from trace_analysis import DataFile
from igor2.packed import load as loadpxp
import pprint
import matplotlib.pylab as plt
import pandas as pd
from openpyxl import load_workbook

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

'''
def auto_adjust_column_widths(filepath):
    workbook = load_workbook(filepath)
    for sheet in workbook.sheetnames:
        worksheet = workbook[sheet]
        for column_cells in worksheet.columns:
            max_length = 0
            column = column_cells[0].column_letter
            for cell in column_cells:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column].width = adjusted_width
    workbook.save(filepath)
'''
###### MAIN ######################################################

#files = find_nm_files('C:/Users/laura.gonzalez/DATA/DATA_TO_ANALYSE')
files = find_nm_files('D:\Internship_Rebola_ICM\RAW_DATA_TO_ANALYSE')

data_mem_list = []
data_resp_list = []

#PDF creation per file
for file in files:
    try:
        datafile = DataFile(file)
        pdf = PdfPage(debug=False)
        pdf.fill_PDF(datafile, debug=False)
        plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/{datafile.filename}.pdf')
        print("File saved successfully :", file, '\n')

        
        data_mem_dict = {'Filename': datafile.filename,
                        'Id (pA)': datafile.Id_A,
                        'Rm (MOhm)': datafile.Rm,
                        'Ra (MOhm)': datafile.Ra,
                        'Cm (pF)': datafile.Cm}
        data_mem_list.append(data_mem_dict)

        data_resp_dict = {'Filename': datafile.filename,
                          'Peak type' : datafile.type,
                          'Amplitude response 1 (pA)': datafile.amp_resp1,
                          'Amplitude response 2 (pA)': datafile.amp_resp2,
                          'Paired pulse ratio Amp2/Amp1': datafile.PPR,
                          'Rise_time 10-90% (ms)': datafile.rise_time,
                          'Decay time 50% (ms)': datafile.decay_time}
        data_resp_list.append(data_resp_dict)

    except:
        print("Error analysing this file :", file, '\n')

#Excel creation

try: 
    data_mem_for_excel = pd.DataFrame(data_mem_list)
    data_resp_for_excel = pd.DataFrame(data_resp_list)  
    print(data_mem_for_excel) 
    print(data_resp_for_excel)
    with pd.ExcelWriter('C:/Users/laura.gonzalez/DATA/output.xlsx', engine='openpyxl') as writer:
        data_mem_for_excel.to_excel(writer, sheet_name='Membrane characteristics', index=False)
        data_resp_for_excel.to_excel(writer, sheet_name='Response', index=False)
    #auto_adjust_column_widths('C:/Users/laura.gonzalez/DATA/output.xlsx')

    print("Excel file saved successfully.")
except:
    print("ERROR when saving the file to excel")



#analyse each file to plot



#Execute if the Python script is being executed as the main program. 
#If the script is being imported as a module in another script, not execute.

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
#print(datafile.response)
#pprint.pp(datafile)

#data = File('C:/Users/laura.gonzalez/DATA/RAW_DATA/nm02May2024c0/nm02May2024c0_000.pxp')  #in loop put "file"
#data.load_data()

#data_test = loadpxp('C:/Users/laura.gonzalez/DATA/RAW_DATA/nm12Jun2024c0/nm12Jun2024c0_000.pxp')
#print(data_test)
#print(data_test[0])
#print(len(data_test))   #len = 2 , first item? second item is a dict

#print(data_test[1].items())

'''
'''
recordings = data_test[1]['root'][b'RecordA0']
for value in recordings:
    print(value)


print(len(recordings
print(recordings)
'''
'''
#data_test[1][b'SampleInterval']
#print(data_test[1]['V_Flag'])
#print(data_test[1])


#recordings = get_recordings(data)


#record_a0 = data_test[1]['root'][b'RecordA0'] #['wave']['wData']
#print("RecordA0:", record_a0)

# Iterating over all RecordA keys
#record_keys = [key for key in data_test[1]['root'].keys() if key.startswith(b'RecordA')]
#for record_key in record_keys:
#    print(f"{record_key.decode('utf-8')}: {data['root'][record_key]}")
'''