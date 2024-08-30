
import os

from PdfPage_ratio import PdfPage
from trace_analysis_ratio import DataFile
import matplotlib.pylab as plt
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
import numpy as np
#from openpyxl import load_workbook

files_directory = 'C:/Users/LauraGonzalez/DATA/Ratio_experiment/RAW_DATA_AMPA_NMDA_RATIO-q'

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

def plot_barplots(file_path, metrics):
    # Read the Excel file into a DataFrame
    IGOR_results_df = pd.read_excel(file_path, header=0)
    
    # Group labels
    labels = ['Ketaxyla', 'xyla eutha', 'keta xyla eutha']
    group_queries = ["Group=='Ketaxyla'", "Group=='xyla eutha'", "Group=='keta xyla eutha'"]
    colors = ['blue', 'green', 'orange']
    
    # Number of plots based on the number of metrics
    num_metrics = len(metrics)
    
    # Set up the figure and subplots
    fig, axes = plt.subplots(3, 4, figsize=(14, 16))
    axes = axes.flatten()
    
    #plt.subplots(1, num_metrics, figsize=(10 * num_metrics, 6), sharey=False)
    
    # Ensure axes is always a list (in case there's only one metric)
    if num_metrics == 1:
        axes = [axes]
    
    # Loop through each metric and plot
    for idx, metric in enumerate(metrics):
        means = []
        sems = []
        individual_data = []
        
        # Collect data for each group
        for query in group_queries:
            df_temp = IGOR_results_df.query(query)[metric]
            means.append(df_temp.mean())
            sems.append(df_temp.sem())
            individual_data.append(df_temp)
        
        # Bar plot with error bars
        bar_positions = np.arange(len(labels))
        axes[idx].bar(bar_positions, means, yerr=sems, color=colors, width=0.6, capsize=5, alpha=0.6, label='Mean ± SEM')
        
        # Plot individual data points
        for i, df in enumerate(individual_data):
            axes[idx].scatter(np.full(df.shape, bar_positions[i]), df, color='black', zorder=5)
        
        axes[idx].spines['top'].set_visible(False)
        axes[idx].spines['right'].set_visible(False)
        
        # Add title and labels to each subplot
        axes[idx].set_title(f'{metric}')
        axes[idx].set_xticks(bar_positions)
        axes[idx].set_xticklabels(labels)
        #axes[idx].set_ylabel('Amplitude (pA)')

    # Delete any remaining unused subplots (if any)
    for idx in range(num_metrics, len(axes)):
        fig.delaxes(axes[idx])
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.show()

###### MAIN ######################################################

files = find_nm_files(files_directory)

data_mem_list = []
data_resp_list = []

#PDF creation per file
for file in files:
    try:
        datafile = DataFile(file)
        pdf = PdfPage(debug=False)
        pdf.fill_PDF(datafile, debug=False)
        plt.savefig(f'C:/Users/LauraGonzalez/Output_expe/Ratio_PDFs/{datafile.filename}.pdf')
        print("File saved successfully :", file, '\n')

        
        data_mem_dict = {'Filename': datafile.filename,
                        'Id (A)': datafile.Id_A,
                        'Rm (Ohm)': datafile.Rm,
                        'Ra (Ohm)': datafile.Ra,
                        'Cm (F)': datafile.Cm}
        data_mem_list.append(data_mem_dict)

        data_resp_dict = {'Filename': datafile.filename,
                          'Peak type' : datafile.type,
                          'Amplitude response 1 (nA)': datafile.amp_resp1,
                          'Amplitude response 2 (nA)': datafile.amp_resp2,
                          'Paired pulse ratio Amp2/Amp1': datafile.PPR,
                          'Rise_time 10-90% (ms)': datafile.rise_time,
                          'Decay time 50% (ms)': datafile.decay_time}
        data_resp_list.append(data_resp_dict)
    except Exception as e:
        print(f"Error analysing this file : {e}")

#Excel creation

try:
    data_mem_for_excel = pd.DataFrame(data_mem_list)
    data_resp_for_excel = pd.DataFrame(data_resp_list)

    # Create a Pandas Excel writer using openpyxl as the engine
    with pd.ExcelWriter('C:/Users/LauraGonzalez/Output_expe/ratio_prog.xlsx', engine='openpyxl') as writer:
        data_mem_for_excel.to_excel(writer, sheet_name='Membrane characteristics', index=False)
        data_resp_for_excel.to_excel(writer, sheet_name='Response', index=False)

        # Access the workbook and the sheets
        workbook  = writer.book
        worksheet_mem = writer.sheets['Membrane characteristics']
        worksheet_resp = writer.sheets['Response']

        # Adjust column widths for data_mem_for_excel
        for column in data_mem_for_excel:
            column_length = max(data_mem_for_excel[column].astype(str).map(len).max(), len(column))
            col_idx = data_mem_for_excel.columns.get_loc(column)
            worksheet_mem.column_dimensions[openpyxl.utils.get_column_letter(col_idx + 1)].width = column_length

        # Adjust column widths for data_resp_for_excel
        for column in data_resp_for_excel:
            column_length = max(data_resp_for_excel[column].astype(str).map(len).max(), len(column))
            col_idx = data_resp_for_excel.columns.get_loc(column)
            worksheet_resp.column_dimensions[openpyxl.utils.get_column_letter(col_idx + 1)].width = column_length

    print("Excel file saved successfully.")
except Exception as e:
    print(f"ERROR when saving the file to excel: {e}")

#analyse each file to plot

#debug with IGOR results
#read_IGOR_results('C:/Users/LauraGonzalez/Output_expe/ratio_results_.xlsx')
metrics = ["1 AMPA Amplitude (pA)", "1 AMPA rise time (10-90%)", "1 AMPA decay time (50%)", "2 AMPA Amplitude (pA)",
           "1 NMDA Amplitude (pA)", "1 NMDA rise time (10-90%)", "1 NMDA decay time (50%)", "2 NMDA Amplitude (pA)",
           "1 NMDA/AMPA", "2 NMDA/AMPA"]  
plot_barplots('C:/Users/LauraGonzalez/Output_expe/ratio_results_.xlsx', metrics)



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
