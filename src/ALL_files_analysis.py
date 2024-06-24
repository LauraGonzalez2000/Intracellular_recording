
import os

from PdfPage import PdfPage
from trace_analysis import DataFile
from igor2.packed import load as loadpxp
import pprint
import matplotlib.pylab as plt

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

###### MAIN ######################################################

files = find_nm_files('C:/Users/laura.gonzalez/DATA/RAW_DATA')

'''
for file in files:
    datafile = DataFile(file)

    #fill_PDF(filename, debug=True)
   
    #analyse each file to create excel

    #analyse each file to plot

'''
#### try with one file, then put this inside the loop:
#datafile = DataFile('C:/Users/laura.gonzalez/DATA/RAW_DATA/nm12Jun2024c0/nm12Jun2024c0_000.pxp')
#pdf = PdfPage(debug=True)
#print(pdf)
#fill_PDF("nm12Jun2024c0_000", debug=True)


#Execute if the Python script is being executed as the main program. 
#If the script is being imported as a module in another script, not execute.
if __name__=='__main__':
    #filename is the full path to the PDF file 
    #filename = os.path.join(os.path.expanduser('~'), 'DATA', 'Dataset1', 'nm12Jun2024c0_000_AMPA.pdf')
    datafile = DataFile('C:/Users/laura.gonzalez/DATA/RAW_DATA/nm12Jun2024c0/nm12Jun2024c0_000.pxp')
    pdf = PdfPage(debug=True)
    pdf.fill_PDF(datafile, debug=True)
    plt.show()
    









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