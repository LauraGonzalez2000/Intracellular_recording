import numpy as np
import matplotlib.pylab as plt
import h5py
import statistics

from PdfPage import PdfPage

######################################################################

def get_data(path):
    data = h5py.File(path)
    return data


def get_xscale(data): 
    try:
        timestep = data['SampleInterval'][()] #timestep data acquisition in Igor (0.01 ms)
        datapoints = data['SamplesPerWave'][()].astype(int) #amount of datapoints acquired (200 000)
        tot_time = np.round(timestep * datapoints).astype(int) 
        xscale = np.linspace(0, tot_time, num=datapoints)
        #print(xscale)
        return xscale
    except: ##information not present in file for some reason
        timestep_ = 0.01 #timestep data acquisition in Igor (0.01 ms)
        datapoints_ = 200000 #amount of datapoints acquired (200 000)    ##### not always
        tot_time_ = np.round(timestep_ * datapoints_).astype(int) 
        xscale_ = np.linspace(0, tot_time_, num=datapoints_)
        #print(xscale)
        print("Error getting xscale, by default 0-2000 ms with 0.01 timestep")
        return xscale

def get_recordings(data):
    record_data = {}
    for key in data.keys():
        if key.startswith('Record'):
            record_data[key] = data[key][()]  
    return record_data

def get_average_recordings(Recordings):
    avg_data = np.mean(list(Recordings.values()), axis=0)
    return avg_data

def get_data_aligned(path):
    data = get_data(path)
    recordings = get_recordings(data)
    average_data = get_average_recordings(recordings)
    data_baseline = average_data[0:50]
    average_baseline = statistics.mean(data_baseline)
    average_data_aligned = average_data - average_baseline
    return average_data_aligned

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

def get_pulse(data, name):

    Stim_params = data['/nmMarieRecording_singleVCstim']

    if name == "dac0":
        pulse_DAC0 = Stim_params['DAC_0_pulse'][()]
        keys_DAC0 = ['off', 'wave', 'pulse', 'amp', 'onset', 'width']
        params_DAC0 = extract_params(pulse_DAC0, keys_DAC0)
        print(params_DAC0)
        return params_DAC0 

    elif name == "dac1":
        pulse_DAC1 = Stim_params['DAC_1_pulse'][()]
        keys_DAC1 = ['wave', 'train', 'tbgn', 'tend', 'interval', 'pulse', 'amp', 'width']
        params_DAC1 = extract_params(pulse_DAC1, keys_DAC1)
        return params_DAC1


########################################################

def func(filename, 
         params1=0,
         params2=3,
         debug=False):

    path = r'\\l2export\iss02.rebola\analyzed\Sofia\Analysis IGOR files\HDF5 files\nm18Feb2021c1_006_HDF5'
    data = get_data(path)
    recordings_aligned = get_data_aligned(path)

    page = PdfPage(debug=debug)

    
    print(page.AXs)

    for key in page.AXs:
        if key=='Notes':
            txt = ' ID file'
            txt += ' \n '
            txt += 'ID animal'
            txt += ' \n '
            txt += 'Number of recordings'
            txt += ' \n '
            page.AXs['Notes'].annotate(txt,
                                       (0, 1), va='top',
                                       xycoords='axes fraction')
        elif key=='DAC0':
            page.AXs[key].set_ylabel(key)
            
            
            time = get_xscale(data)

            Stim_params = data['/nmMarieRecording_singleVCstim']
            Stim_params_ = Stim_params['DAC_0_0']
            dac0_pulse = np.array(Stim_params_)
            
            page.AXs[key].plot(time, dac0_pulse)  
        
        elif key=='DAC1':
            page.AXs[key].set_ylabel(key)
            time = get_xscale(data)

            Stim_params = data['/nmMarieRecording_singleVCstim']
            Stim_params_ = Stim_params['DAC_1_0']
            dac1_pulse = np.array(Stim_params_)

            
            page.AXs[key].plot(time, dac1_pulse)  

        elif key=='FullResp':
            page.AXs[key].set_ylabel(key)
            time = get_xscale(data)
            full_resp = recordings_aligned
            page.AXs[key].plot(time, full_resp)  

        elif key=='MemTest':
            page.AXs[key].set_ylabel(key)
            time_mem = get_xscale(data)[0:30000]
            resp_mem = recordings_aligned[0:30000]
            page.AXs[key].plot(time_mem, resp_mem)  

        elif key=='I0':
            page.AXs[key].set_ylabel(key)
            page.AXs[key].plot(np.random.randn(100))  #add corresponding info

        elif key=='Rm':
            page.AXs[key].set_ylabel(key)
            page.AXs[key].plot(np.random.randn(100))  #add corresponding info

        elif key=='Rs':
            page.AXs[key].set_ylabel(key)
            page.AXs[key].plot(np.random.randn(100))  #add corresponding info

        elif key=='RespAnalyzed':
            page.AXs[key].set_ylabel(key)
            time_stim = get_xscale(data)[95000:110000]
            resp_stim = recordings_aligned[95000:110000]
            page.AXs[key].plot(time_stim, resp_stim)  

            
    page.save(filename.replace('hdf5', 'pdf'))




if __name__=='__main__':
         
    import os 
         
    filename = os.path.join(os.path.expanduser('~'), 'DATA', 'Dataset1', 'test.pdf')

    func(filename, debug=True)

    plt.show()

