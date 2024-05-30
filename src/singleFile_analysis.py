import numpy as np
import matplotlib.pylab as plt
import h5py
import statistics
from scipy.optimize import curve_fit

from PdfPage import PdfPage

#CONSTANTS######################################################################

WINDOW = 1 #window to remove artefact (1ms)
TIME_STEP = 0.01 #timestep data acquisition in Igor (0.01 ms)
NUM_DATAPOINTS = 200000 #amount of datapoints acquired (200 000) #may vary
STIM_PARAMS = '/nmMarieRecording_singleVCstim'  #Configuration of stimulation name  #may vary
PATH = r'\\l2export\iss02.rebola\analyzed\Sofia\Analysis IGOR files\HDF5 files\nm18Feb2021c1_006_HDF5'
DELTA_V = 1e-3

################################################################################
#Methods to process data

def get_raw_data(path):
    raw_data = h5py.File(path)
    return raw_data

def get_time(data): 
    try:
        timestep = data['SampleInterval'][()] #timestep data acquisition in Igor (0.01 ms)
        datapoints = data['SamplesPerWave'][()].astype(int) #amount of datapoints acquired (200 000)
        tot_time = np.round(timestep * datapoints).astype(int) 
        time = np.linspace(0, tot_time, num=datapoints)
        return time
    except: ## if information not present in file for some reason
        timestep_ = TIME_STEP 
        datapoints_ = NUM_DATAPOINTS     
        tot_time_ = np.round(timestep_ * datapoints_).astype(int) 
        time_ = np.linspace(0, tot_time_, num=datapoints_)
        print("Error getting time scale, by default 0-2000 ms with 0.01 timestep")
        return time_

#methods to obtain recordings
def get_recordings(data):
    recordings = []
    for key in data.keys():
        if key.startswith('Record'):
            recording = data[key][()]
            recordings.append(recording)
    return recordings

def get_recordings_aligned(record_data):
    record_data_aligned = []
    for recording in record_data: 
        recording_baseline = recording[0:50]
        average_baseline = statistics.mean(recording_baseline)
        recording_aligned = record_data - average_baseline
        record_data_aligned.append[recording_aligned]
    return record_data_aligned

def get_average_recordings(recordings):

    stacked_arrays = np.vstack(recordings)
    avg_data_list = np.mean(stacked_arrays, axis=0)

    return avg_data_list

def get_average_recordings_aligned(data):
    recordings = get_recordings(data) #ok
    average_data = get_average_recordings(recordings)
    data_baseline = average_data[0:50]
    average_baseline = statistics.mean(data_baseline)
    average_data_aligned = average_data - average_baseline
    return average_data_aligned

###############################################################################
#methods to analyse recordings

def get_boundaries(data):
    try: 
        Stim_params = data[STIM_PARAMS]  ##will not work with a different name!
        pulse_DAC1 = Stim_params['DAC_1_pulse'][()]
        keys_DAC1 = ['wave', 'train', 'tbgn', 'tend', 'interval', 'pulse', 'amp', 'width']
        params_DAC1 = extract_params(pulse_DAC1, keys_DAC1)
        start = params_DAC1['tbgn']
        stop =  params_DAC1['tend']
        start2 = start + params_DAC1['interval']
        stop2 = stop + params_DAC1['interval']
        #print("in loop: start :", start, ", stop : ", stop, ", start2 : ", start2, ", stop2 : ", stop2)  #erase when it is working
        return start, stop, start2, stop2
        
    except:
        print("stimulation parameters not found")
        return 1000, 1050, 1051, 1099

def get_peaks():  #to do: add generalized function to find peaks

    peaks = [100,200, 1000, 1050]  
    return peaks

################################################################################
#Models to fit the data
def model_function_constant(t, Iprev): #constant
    return 0*t + Iprev

def model_biexponential1(t, A, B, C, D, E): #biexponential model 1
    return A * (B*np.exp(-(t-100)/C) + (1-B)*np.exp(-(t-100)/D)) + E

def model_biexponential2(t, A, B, C, D, E): #biexponential model 2  #maybe useless if we use only first part
    return A * (B*np.exp(-(t-200)/C) + (1-B)*np.exp(-(t-200)/D)) + E

def get_fit(subset_range, model_function, time, average_data_aligned):
    params = []
    start, end = subset_range
    x_subset = time[start:end]
    y_subset = average_data_aligned[start:end]
    params, _ = curve_fit(model_function, x_subset, y_subset)   
    return x_subset, model_function(x_subset, *params)

def get_params(time, average_data_aligned): #add corresponding function

    subset_ranges = [(0, 10000), (10007, 20000)]                              #to do : generalize
    model_functions = [model_function_constant, model_biexponential1]   

    params = []
    # Plot each subset and its corresponding fit
    for subset_range, model_function in zip(subset_ranges, model_functions):
        start, end = subset_range
        x_subset = time[start:end]
        y_subset = average_data_aligned[start:end]
        # Fit the model to the subset
        popt, _ = curve_fit(model_function, x_subset, y_subset)
        params.append(popt)
        print("params", params)

    return params


################################################################################
#Methods to extract the values to plot

def get_pulse(data, name):

    Stim_params = data['/nmMarieRecording_singleVCstim']

    if name == "dac0":
        pulse_DAC0 = Stim_params['DAC_0_pulse'][()]
        keys_DAC0 = ['off', 'wave', 'pulse', 'amp', 'onset', 'width']
        params_DAC0 = {}
        for key in keys:
            value = str(pulse_data[0]).split('%s=' % key)[1].split(';')[0]
            if value.isdigit():
                params_DAC0[key] = int(value)
            elif value.isalpha():
                params_DAC0[key] = value
            else:
                print("error: value is not an integer nor a string")
        return params_DAC0 

    elif name == "dac1":
        pulse_DAC1 = Stim_params['DAC_1_pulse'][()]
        keys_DAC1 = ['wave', 'train', 'tbgn', 'tend', 'interval', 'pulse', 'amp', 'width']
        params_DAC1 = {}
        for key in keys:
            value = str(pulse_data[0]).split('%s=' % key)[1].split(';')[0]
            if value.isdigit():
                params_DAC1[key] = int(value)
            elif value.isalpha():
                params_DAC1[key] = value
            else:
                print("error: value is not an integer nor a string")
        return params_DAC1

def get_mem_values(data):

    peaks = get_peaks()
    print("peaks",peaks)
    print(data)
    Id = np.abs(data[peaks[0]*100+7])

    Ra = DELTA_V/Id

    Idss = 4  #Idss = params[2][4] - params[1][4]
    Rm = (DELTA_V - Ra * Idss) / Idss

    tau = 5   #tau = params[2][2]  
    Cm = tau / (1/(1/Ra + 1/Rm)) 

    ''' #alternative : calculate Cm with the area under the curve (decay)
    result_c2, error_c2 = integrate.quad(func_const2, 200, 300)
    result_d, error_d = integrate.quad(func2, 200, 300)
    AUC_d = result_d - result_c2
    Cm = AUC_d / dV
    
    #correcting for leak current
    correction = 1 + Ra / Rm
    Ra_c = Ra * correction
    Rm_c = Rm * correction
    Cm_c = Cm / (correction*correction)
    values = [Ra, Ra_c, Rm, Rm_c, Cm, Cm_c]
    '''
    return Id, Ra, Rm, Cm

def get_mem_values_across_time(data):
    recordings = get_recordings(data)
    Id_list = []
    Ra_list = []
    Rm_list = []
    Cm_list = []
    for recording in recordings: 
        Id_list.append(get_mem_values(recording)[0])
        Ra_list.append(get_mem_values(recording)[1])
        Rm_list.append(get_mem_values(recording)[2])
        Cm_list.append(get_mem_values(recording)[3])
    return Id_list, Ra_list, Rm_list, Cm_list

################################################################################
#Fill PDF
def fill_PDF(filename, debug=False):

    path = PATH
    data = get_raw_data(path)
    recordings_avg_aligned = get_average_recordings_aligned(data)
    time = get_time(data)

    page = PdfPage(debug=debug)
    
    
    print(page.AXs)

    for key in page.AXs:
        if key=='Notes':
            txt = ' ID file : '
            txt += path.split('\\')[-1]
            txt += ' \n '
            txt += 'Number of recordings : '
            txt += str(len(get_recordings(data)))
            txt += ' \n '
            page.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')

        elif key=='DAC0':
            page.AXs[key].set_ylabel(key)
            Stim_params = data['/nmMarieRecording_singleVCstim']
            Stim_params_ = Stim_params['DAC_0_0']
            dac0_pulse = np.array(Stim_params_)
            page.AXs[key].plot(time, dac0_pulse)  
        
        elif key=='DAC1':
            page.AXs[key].set_ylabel(key)
            Stim_params = data['/nmMarieRecording_singleVCstim']
            Stim_params_ = Stim_params['DAC_1_0']
            dac1_pulse = np.array(Stim_params_)
            page.AXs[key].plot(time, dac1_pulse)  

        elif key=='FullResp':
            page.AXs[key].set_ylabel(key)
            full_resp = recordings_avg_aligned
            stim1, stim2, _, _ = get_boundaries(data)
            artefact_cond = ((time>stim1) & (time<stim1+WINDOW)) | ((time>stim2) & (time<stim2+WINDOW)) 
            page.AXs[key].plot(time[~artefact_cond], full_resp[~artefact_cond])  

        elif key=='MemTest':
            page.AXs[key].set_ylabel(key)
            time_mem = time[9900:10500]
            resp_mem = recordings_avg_aligned[9900:10500]
            page.AXs[key].plot(time_mem, resp_mem, label = "Data")

            subset_ranges = [(9900, 10000), (10007, 10500)]
            model_functions = [model_function_constant, model_biexponential1]   #works better
            for subset_range, model_function in zip(subset_ranges, model_functions):
                x,y = get_fit(subset_range, model_function, time, recordings_avg_aligned)
                page.AXs[key].plot(x,y, color="red", label = "fit")

            
            Id_avg, Ra_avg, Rm_avg, Cm_avg  = get_mem_values(recordings_avg_aligned)

            txt = "Id : "
            txt += str('%.4f'%(Id_avg))
            txt += '\n'
            txt += "Ra : "
            txt += str('%.4f'%(Ra_avg))
            txt += '\n'
            txt += "Rm : "
            txt += str('%.4f'%(Rm_avg))
            txt += '\n'
            txt += "Cm : "
            txt += str('%.4f'%(Cm_avg))
            txt += '\n'
            page.AXs[key].annotate(txt,(0.5, 0.5), va='top', xycoords='axes fraction')
            
        elif key=='Id':
            page.AXs[key].set_ylabel(key)
            Id_list = get_mem_values_across_time(data)[0]
            page.AXs[key].plot(Id_list) 

        elif key=='Rm':
            page.AXs[key].set_ylabel(key)
            Rm_list = get_mem_values_across_time(data)[1]
            page.AXs[key].plot(Rm_list)  

        elif key=='Ra':
            page.AXs[key].set_ylabel(key)
            Ra_list = get_mem_values_across_time(data)[2]
            page.AXs[key].plot(Ra_list)  

        elif key=='Cm':
            page.AXs[key].set_ylabel(key)
            Rm_list = get_mem_values_across_time(data)[3]
            page.AXs[key].plot(Rm_list) 

        elif key=='RespAnalyzed':
            page.AXs[key].set_ylabel(key)
            time_stim = time[95000:110000]
            resp_stim = recordings_avg_aligned[95000:110000]
            stim1, stim2, _, _ = get_boundaries(data)
            artefact_cond = ((time_stim>stim1) & (time_stim<stim1+WINDOW)) | ((time_stim>stim2) & (time_stim<stim2+WINDOW))
            page.AXs[key].plot(time_stim[~artefact_cond], resp_stim[~artefact_cond])  

            
    page.save(filename.replace('hdf5', 'pdf'))

#for debug
if __name__=='__main__':
         
    import os 
         
    filename = os.path.join(os.path.expanduser('~'), 'DATA', 'Dataset1', 'test.pdf')

    fill_PDF(filename, debug=True)

    plt.show()

