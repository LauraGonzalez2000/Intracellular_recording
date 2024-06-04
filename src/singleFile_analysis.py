import numpy as np
import matplotlib.pylab as plt
import h5py
import statistics
from scipy.optimize import curve_fit
from scipy.signal import find_peaks

from PdfPage import PdfPage

#CONSTANTS######################################################################

WINDOW = 1 #window to remove artefact (1ms)
TIME_STEP = 0.01 #timestep data acquisition in Igor (0.01 ms)
NUM_DATAPOINTS = 200000 #amount of datapoints acquired (200 000) #may vary
#STIM_PARAMS = '/nmMarieRecording_singleVCstim'  #Configuration of stimulation name  #may vary
STIM_PARAMS = '/nmStimSofia1' 
#PATH = r'\\l2export\iss02.rebola\analyzed\Sofia\Analysis IGOR files\HDF5 files\nm18Feb2021c1_006_HDF5'
PATH = r'C:\Users\laura.gonzalez\DATA\HDF5 files\nm03Jun2024c0_001_HDF5'
DELTA_V = 1e-3 #10 mV = 10^-3 V

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

def extract_params(pulse_data, keys):
    params = {}
    for key in keys:
        value = str(pulse_data[0]).split('%s=' % key)[1].split(';')[0]
        if value.isdigit():
            params[key] = int(value)
        elif value.isalpha():
            params[key] = value
        else:
            print("error: value is not an integer nor a string")
    return params

def get_boundaries(data): #to do: not working, always uses exception, to FIX
    try: 
        Stim_params = data[STIM_PARAMS]  
        #print("Stim params", Stim_params)
        pulse_DAC1 = Stim_params['DAC_1_pulse'][()]
        #print("DAC1", pulse_DAC1)
        keys_DAC1 = ['wave', 'train', 'tbgn', 'tend', 'interval', 'pulse', 'amp', 'width']
        params_DAC1 = extract_params(pulse_DAC1, keys_DAC1)
        #print("params_DAC1", params_DAC1)
        start = params_DAC1['tbgn']
        stop =  params_DAC1['tend']
        start2 = start + params_DAC1['interval']
        stop2 = stop + params_DAC1['interval']
        #print("in loop: start :", start, ", stop : ", stop, ", start2 : ", start2, ", stop2 : ", stop2)  #erase when it is working
        #return start, stop, start2, stop2   #use this when code is fixed
        
    except:
        print("stimulation parameters not found")
        #return 1000, 1050, 1051, 1099
        return 600, 700, 701, 801
    
    return 600, 700, 701, 801 #remove this when code is fixed

def get_peaks():  #to do: add generalized function to find peaks
    #peaks = [100,200, 1000, 1050]  
    peaks = [100, 200, 600, 700]
    return peaks

def get_peaks_():  #to do: add generalized function to find peaks
    #peaks = [1007, 1057]  
    peaks = [607, 707]
    return peaks

#finds if peak is positive or negative
def get_resp_nature(average_data_aligned):
    
    #min = np.min(average_data_aligned[100100:100500])
    #max = np.max(average_data_aligned[100100:100500])
    min = np.min(average_data_aligned[60100:69900])
    max = np.max(average_data_aligned[60100:69900])

    diff = max+min

    if diff == 0 : 
        print("Error : no peak")
        
    elif diff < 0 :  #negative peak
        return True
        
    elif diff > 0 :  #positive peak
        return False

#returns value of index and of peak
def get_peak_resp(average_data_aligned):

    if get_resp_nature(average_data_aligned): 
        peak = np.min(average_data_aligned[60100:69900])
        peak_index = np.argmin(average_data_aligned[60100:69900])
    else : 
        peak = np.max(average_data_aligned[60100:69900])
        peak_index = np.argmax(average_data_aligned[60100:69900])

    return peak_index, peak


################################################################################
#Models to fit the data
def model_function_constant(t, Iprev): #constant
    return 0*t + Iprev

def model_biexponential1(t, A, B, C, D, E): #biexponential model 1
    return A * (B*np.exp(-(t-100)/C) + (1-B)*np.exp(-(t-100)/D)) + E

def model_biexponential2(t, A, B, C, D, E): #biexponential model 2  #maybe useless if we use only first part
    return A * (B*np.exp(-(t-200)/C) + (1-B)*np.exp(-(t-200)/D)) + E

#useless
def get_fit(subset_range, model_function, time, average_data_aligned):
    params = []
    start, end = subset_range
    x_subset = time[start:end]
    y_subset = average_data_aligned[start:end]
    params, _ = curve_fit(model_function, x_subset, y_subset)   
    return x_subset, model_function(x_subset, *params)

def get_params_function(model_function, start, end, recording, time):
    x_subset = time[start:end]
    y_subset = recording[start:end]
    params, _ = curve_fit(model_function, x_subset, y_subset)
    return params

#useless
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
        #print("params", params)

    return params

#useless
def get_params_resp(time, average_data_aligned): #add corresponding function

    #subset_ranges = [(100000, 100050), (100050, 104999)]                              #to do : generalize
    subset_ranges = [(60000, 70000), (70000, 80000)]
    model_functions = [model_biexponential1, model_biexponential1]   

    params = []
    # Plot each subset and its corresponding fit
    for subset_range, model_function in zip(subset_ranges, model_functions):
        start, end = subset_range
        #print(start, end)
        x_subset = time[start:end]
        #print(x_subset)
        y_subset = average_data_aligned[start:end]
        #print(len(time))
        #print(len(average_data_aligned))
        #print(len(y_subset))
        #print(y_subset)
        # Fit the model to the subset
        popt, _ = curve_fit(model_function, x_subset, y_subset)
        params.append(popt)
        #print("params", params)

    return params


################################################################################
#Methods to extract the values to plot

def get_pulse(data, name):

    #Stim_params = data['/nmMarieRecording_singleVCstim']
    Stim_params = data[STIM_PARAMS]


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

#from a recording or average of recordings and the timescale, output the membrane characteristics
def get_mem_values(recording, time): 

    peaks = get_peaks()
    Id = np.abs(recording[peaks[0]*100+7])  #in nano amperes

    Id_A = Id * 1e-9   # in amperes

    Ra = np.abs(DELTA_V/Id_A)  #in ohm   (volts/amperes)

    Idss = np.abs(np.mean(recording[16000:19000]))   # in nano amperes
    Idss_A = Idss * 1e-9   # in amperes

    Rm = (DELTA_V - Ra * Idss_A) / Idss_A #in Ohm

    params_exp1 = get_params_function(model_biexponential1, 10007, 20000, recording, time)
    tau = np.abs(params_exp1[2])  
    Cm = np.abs(tau / (1/(1/Ra + 1/Rm)) )

    ''' 
    #alternative : calculate Cm with the area under the curve (decay)
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

def get_mem_values_across_time(data, time):
    recordings = get_recordings(data)
    Id_list = []
    Ra_list = []
    Rm_list = []
    Cm_list = []
    for recording in recordings: 
        Id_list.append(get_mem_values(recording, time)[0])
        Ra_list.append(get_mem_values(recording, time)[1])
        Rm_list.append(get_mem_values(recording, time)[2])
        Cm_list.append(get_mem_values(recording, time)[3])
    return Id_list, Ra_list, Rm_list, Cm_list

def analyse_neg_peak(average_data_aligned, data):
    peak = "negative"
    
    #data = get_data(path)
    #average_data = get_average_recordings(get_recordings(data))
    #average_data_aligned = get_data_aligned(average_data)

    start, stop, start2, stop2 = get_boundaries(data)
    start_ = (start+1)*100
    stop_ = (stop-1)*100
    start2_ = (start2+1)*100
    stop2_ = (stop2-1)*100
    #print(start_, stop_, start2_, stop2_)

    #100500
    amp_resp1 = np.min(average_data_aligned[start_:stop_])  ## stimulation at 100 000th datapoint aka 1 000 ms
    time_peak_resp1 = np.argmin(average_data_aligned[start_:stop_])
    #print(time_peak_resp1)
    #105500
    amp_resp2 = np.min(average_data_aligned[start2_:stop2_])  ## stimulation at 105 000th datapoint aka 1 050 ms

    '''
    amp_resp1 = np.min(average_data_aligned[100100:100500])  ## stimulation at 100 000th datapoint aka 1 000 ms
    time_peak_resp1 = np.argmin(average_data_aligned[100100:100500])
    amp_resp2 = np.min(average_data_aligned[105100:105500])  ## stimulation at 105 000th datapoint aka 1 050 ms
    '''
    PPR = amp_resp2/amp_resp1
      
    
    
    #####################################################################
    
    ##rise time 10-90%
    
    bound1 = 0.1 * amp_resp1
    bound2 = 0.9 * amp_resp1
    
    range = average_data_aligned[start_:stop_]
    
    i = 600.4
    j = 600.4
    time1 = 0
    time2 = 0
    for value in range : 
        if value < bound2: 
            time2 = i
            break;
        i+= 0.01   
        
    for value in range : 
        if value < bound1: 
            time1 = j
            break;
        j+= 0.01      
        
    rise_time = np.abs(time2-time1)    
    
    
    
    ##decay time 50%
    
    bound = 0.5 * amp_resp1
    range = average_data_aligned[start_ + time_peak_resp1 :stop_]
    
    k = 601.70 
    time = 0
    for value in range : 
        if value > bound:
            time = k
            break;
        k+= 0.01 
    
    decay_time = np.abs(time - 601.70)

    '''
    print("Amplitude response 1 (nA) : ", amp_resp1 )
    print("Amplitude response 2 (nA) : ", amp_resp2 )
    print("Paired pulse ratio Amp2/Amp1: ", PPR )
    print("Rise_time 10-90% : ", rise_time, "ms.")
    print("Decay time 50% : ", decay_time, " ms.")
    '''
    
    return peak, amp_resp1,amp_resp2, PPR, rise_time, decay_time

def analyse_pos_peak(average_data_aligned, data):
    
    peak = "positive"
    #data = get_data(path)
    #average_data = get_average_recordings(get_recordings(data))
    #average_data_aligned = get_data_aligned(average_data)

    
    start, stop, start2, stop2 = get_boundaries(data)
    start_ = (start+1)*100   #usually, 100100
    stop_ = (stop-1)*100     #usually, 104900
    start2_ = (start2+1)*100 #usually, 105100
    stop2_ = (stop2-1)*100   #usually, 109900
    
      
    amp_resp1 = np.max(average_data_aligned[start_:stop_])  ## stimulation at 100 000th datapoint aka 1 000 ms   #changed to max
    index_peak_resp1 = np.argmax(average_data_aligned[start_:stop_])  #not really
    time_peak_resp1 = (start_ + index_peak_resp1)/100
    
    #print(index_peak_resp1)
    
    #print("time peak response 1: ", time_peak_resp1)
    
    amp_resp2 = np.max(average_data_aligned[start2_:stop2_])  ## stimulation at 105 000th datapoint aka 1 050 ms   #changed to max
    PPR = amp_resp2/amp_resp1
      
    
    
    #####################################################################
    
    ##rise time 10-90%
    
    bound1 = 0.1 * amp_resp1
    bound2 = 0.9 * amp_resp1
    
    range = average_data_aligned[start_:stop_]  #generalize boundaries
    
    l = 600.4  #generalize
    m = 600.4  #generalize
    time1 = 0
    time2 = 0
    
    for value in range : 
        if value > bound1: 
            time1 = m
            break;
        m+= 0.01  
        
    for value in range : 
        if value > bound2: 
            time2 = l
            break;
        l+= 0.01   
        
    rise_time = np.abs(time2-time1)    
    
    
    
    #####################################################################
    
    ##decay time 50%
    
    bound = 0.5 * amp_resp1
    range = average_data_aligned[int(time_peak_resp1*100) :stop_] #generalize boundaries
    
    #print(start_)
    #print(start_ + index_peak_resp1)
    #print(stop_)
    k = 605 
    time = 0
    for value in range : 
        if value < bound:
            time = k
            break;
        k+= 0.01 
        
    #print("time50", time)
    #print("time peak", time_peak_resp1)
    #print("decay_time", time - time_peak_resp1)
    decay_time = np.abs(time - time_peak_resp1)

    '''
    print("Amplitude response 1 (nA) : ", amp_resp1 )
    print("Amplitude response 2 (nA) : ", amp_resp2 )
    print("Paired pulse ratio Amp2/Amp1: ", PPR )
    print("Rise_time 10-90% : ", rise_time, "ms.")
    print("Decay time 50% : ", decay_time, " ms.")
    '''
    
    return peak, amp_resp1, amp_resp2, PPR, rise_time, decay_time
################################################################################
#Fill PDF
def fill_PDF(filename, debug=False):

    path = PATH
    data = get_raw_data(path)
    recordings_avg_aligned = get_average_recordings_aligned(data)
    time = get_time(data)

    page = PdfPage(debug=debug)
    
    
    #print(page.AXs)

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
            Stim_params = data[STIM_PARAMS]
            Stim_params_ = Stim_params['DAC_0_0']
            dac0_pulse = np.array(Stim_params_)
            page.AXs[key].plot(time, dac0_pulse)  
        
        elif key=='DAC1':
            page.AXs[key].set_ylabel(key)
            Stim_params = data[STIM_PARAMS]
            Stim_params_ = Stim_params['DAC_1_0']
            dac1_pulse = np.array(Stim_params_)
            page.AXs[key].plot(time, dac1_pulse)  

        elif key=='FullResp':
            page.AXs[key].set_ylabel(key)
            full_resp = recordings_avg_aligned
            stim1, stim2, _, _ = get_boundaries(data)
            #print(stim1, stim2, WINDOW)
            artefact_cond = ((time>stim1) & (time<stim1+WINDOW)) | ((time>stim2) & (time<stim2+WINDOW)) 
            page.AXs[key].plot(time[~artefact_cond], full_resp[~artefact_cond])  

        elif key=='MemTest':
            page.AXs[key].set_ylabel(key)
            time_mem = time[9900:10600]
            resp_mem = recordings_avg_aligned[9900:10600]
            page.AXs[key].plot(time_mem, resp_mem, label = "Data")

            subset_ranges = [(9900, 10000), (10007, 10600)]
            model_functions = [model_function_constant, model_biexponential1]   #works better
            for subset_range, model_function in zip(subset_ranges, model_functions):
                x,y = get_fit(subset_range, model_function, time, recordings_avg_aligned)
                page.AXs[key].plot(x,y, color="red", label = "fit")

            
            Id_avg, Ra_avg, Rm_avg, Cm_avg  = get_mem_values(recordings_avg_aligned, time)

            txt = "Id : "
            txt += str('%.4f'%(Id_avg*1e3))
            txt += " pA "
            txt += '\n'
            txt += "Rm : "
            txt += str('%.4f'%(Rm_avg/1e6))
            txt += " MOhm "
            txt += '\n'
            txt += "Ra : "
            txt += str('%.4f'%(Ra_avg/1e6))
            txt += " MOhm "
            txt += '\n'
            txt += "Cm : "
            txt += str('%.4f'%(Cm_avg*1e6))
            txt += " µF "
            txt += '\n'
            page.AXs[key].annotate(txt,(0.35, 0.5), va='top', xycoords='axes fraction')

            params_exp = get_params_function(model_biexponential1, 10007, 20000, recordings_avg_aligned, time)
            page.AXs[key].fill_between(time_mem,model_biexponential1(time_mem,params_exp[0],params_exp[1],params_exp[2],params_exp[3],params_exp[4] ), model_function_constant(time_mem, params_exp[4] ),where=((time_mem >= 100) & (time_mem <= 200)), alpha=0.3, color='skyblue')


        elif key=='Id':
            page.AXs[key].set_ylabel(key)
            Id_list = get_mem_values_across_time(data, time)[0]
            page.AXs[key].plot(Id_list) 

        elif key=='Rm':
            page.AXs[key].set_ylabel(key)
            Rm_list = get_mem_values_across_time(data, time)[1]
            page.AXs[key].plot(Rm_list)  

        elif key=='Ra':
            page.AXs[key].set_ylabel(key)
            Ra_list = get_mem_values_across_time(data, time)[2]
            page.AXs[key].plot(Ra_list)  

        elif key=='Cm':
            page.AXs[key].set_ylabel(key)
            Cm_list = get_mem_values_across_time(data, time)[3]
            page.AXs[key].plot(Cm_list)  

        elif key=='RespAnalyzed':
            page.AXs[key].set_ylabel(key)
            time_stim = time[55000:80000]
            resp_stim = recordings_avg_aligned[55000:80000]
            stim1, stim2, _, _ = get_boundaries(data)
            artefact_cond = ((time_stim>stim1) & (time_stim<stim1+WINDOW)) | ((time_stim>stim2) & (time_stim<stim2+WINDOW))
            page.AXs[key].plot(time_stim[~artefact_cond], resp_stim[~artefact_cond])  

            if get_resp_nature(recordings_avg_aligned) : 
                peak, amp_resp1, amp_resp2, PPR, rise_time, decay_time = analyse_neg_peak(recordings_avg_aligned, data)
            else : 
                peak, amp_resp1, amp_resp2, PPR, rise_time, decay_time = analyse_pos_peak(recordings_avg_aligned, data)
            
            #text
            txt = "Peak1 : "
            txt += str('%.4f'%(amp_resp1*1e3))
            txt += " pA "
            txt += '\n'
            txt += "Peak2 : "
            txt += str('%.4f'%(amp_resp2*1e3))
            txt += " pA "
            txt += '\n'
            txt += "Rise time : "
            txt += str('%.4f'%(rise_time))
            txt += " ms "
            txt += '\n'
            txt += "Decay time : "
            txt += str('%.4f'%(decay_time))
            txt += " ms "
            txt += '\n'
            page.AXs[key].annotate(txt,(0.65, 0.3), va='top', xycoords='axes fraction')

            '''
            subset_ranges = [(9900, 10000), (10007, 10500)]
            model_functions = [model_function_constant, model_biexponential1]   #works better
            for subset_range, model_function in zip(subset_ranges, model_functions):
                x,y = get_fit(subset_range, model_function, time, recordings_avg_aligned)
                page.AXs[key].plot(x,y, color="red", label = "fit")
        
            '''            
            '''
            params_resp = get_params_resp(time, recordings_avg_aligned)
            #rise time
            rise_time = get_rise_time(time_stim, params_resp)

            #plot peaks
            #peaks = my_find_peaks(resp_stim[~artefact_cond])
            #print("peaks", peaks)
            #peaks = get_peaks_()
            #print("peaks", peaks)
            #page.AXs[key].plot(peaks, resp_stim[peaks], "X")
            '''
            
    page.save(filename.replace('hdf5', 'pdf'))

#for debug
if __name__=='__main__':
         
    import os 
         
    filename = os.path.join(os.path.expanduser('~'), 'DATA', 'Dataset1', 'nm03Jun2024c0_001_NMDA.pdf')

    fill_PDF(filename, debug=True)

    plt.show()

