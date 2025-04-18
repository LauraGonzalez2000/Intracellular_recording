import numpy as np
import pandas as pd
import Curve_fit as cf
from igor2.packed import load as loadpxp
from scipy.ndimage import gaussian_filter1d

import json

class DataFile:
    #Constructor
    def __init__(self, file_path, info_df):
        # Load the config file
        with open('config/config.json', 'r') as f:
            self.config = json.load(f)
        self.file_path = file_path
        self.filename = self.file_path.split('/')[-1].replace('.pxp', '')
        self.infos = {}
        self.stim = {}
        self.response = None
        self.avg_response = None
        self.type = None
        self.load_data()
        self.get_recordings()
        self.get_average_recordings_aligned()
        self.smooth_gauss_avg()
        self.fill_infos(info_df)
        self.get_stim_traces()
        self.get_time()
        self.get_mem_values_across_time(self.time)

    #Methods to extract data
    def load_data(self):
        print("File :")
        print(self.file_path)
        try:
            self.pxp = loadpxp(self.file_path)
            print("OK data was loaded")
        except Exception as e:
            print(f"data was not loaded : {e}")
            return -1

        return self.pxp

    def get_recordings(self):
        try:
            DATA = []
            i = 0
            while True:
                key = b'RecordA%i' % i
                if key in self.pxp[1]['root']:
                    DATA.append(self.pxp[1]['root'][key].wave['wave']['wData'])
                    i += 1
                else:
                    break
            self.response = np.array(DATA)
            print('OK Recordings were loaded')
            return self.response
        except Exception as e:
            print(f'Recordings were not loaded: {e}')
            return -1

    def get_average_recordings_aligned(self):
        try:
            avg_data = np.mean(self.response, axis=0)
            bsl_start = self.config["bsl_start"]
            bsl_end = self.config["bsl_end"]
            avg_baseline = np.mean(avg_data[bsl_start:bsl_end])
            average_data_aligned = avg_data - avg_baseline
            self.avg_response = average_data_aligned
            print("OK average_recordings_aligned found")
        except: 
            print("Error method get_average_recordings_aligned(self)")
            return -1
        return average_data_aligned
    
    def smooth_gauss_avg(self):
        try: 
            sigma = self.config["gauss_sigma"]
            smooth_avg = gaussian_filter1d(self.avg_response, sigma)
            self.smooth_avg_response = smooth_avg
            print("OK smoothing of average_recordings_aligned")
        except Exception as e:
            print(f'Error with smoothing {e}')
        return smooth_avg
    
    def fill_infos(self, info_df):
        try:

            meta_info_df = info_df.loc[(info_df['subfile1'] == self.filename) | (info_df['subfile2'] == self.filename)]

            if len(meta_info_df) != 1:
                raise ValueError(f"Expected one matching row for filename {self.filename}, but found {len(meta_info_df)}.")

            if (info_df['subfile1'] == self.filename).any():
                self.infos = {'SampleInterval' : self.pxp[1]['root'][b'SampleInterval'],
                            'SamplesPerWave' : self.pxp[1]['root'][b'SamplesPerWave'],
                            'FileDate' : self.pxp[1]['root'][b'FileDate'],
                            'FileTime' : self.pxp[1]['root'][b'FileTime'],
                            'Type': 'AMPA',
                            'Euthanize method':str(meta_info_df["Euthanizing method"].item()),
                            'Holding (mV)': '-70',
                            'Drug1': 'PTX',
                            'Drug2': ''
                            }
                
            elif (info_df['subfile2'] == self.filename).any():
                self.infos = {'SampleInterval' : self.pxp[1]['root'][b'SampleInterval'],
                            'SamplesPerWave' : self.pxp[1]['root'][b'SamplesPerWave'],
                            'FileDate' : self.pxp[1]['root'][b'FileDate'],
                            'FileTime' : self.pxp[1]['root'][b'FileTime'],
                            'Type': 'NMDA',
                            'Euthanize method':str(meta_info_df["Euthanizing method"].item()),
                            'Holding (mV)': '40',
                            'Drug1': 'PTX',
                            'Drug2': 'NBQX'
                            }
            print('OK infos were filled correctly')
        except Exception as e:
            print(f"Infos were not filled correctly: {e}")

    def get_stim_traces(self):
        
        possible_keys = [s.encode() for s in self.config["keys_stimulation"]]
        for key in possible_keys:
            try:
                group = self.pxp[1]['root'][key]
                pulse_DAC0 = group[b'DAC_0_0'].wave['wave']['wData']
                pulse_DAC1 = group[b'DAC_1_0'].wave['wave']['wData']
                self.stim = {'Cmd1': pulse_DAC0, 'Cmd2': pulse_DAC1}
                print(f"OK stimulation traces found ({key.decode()})")
                return
            except KeyError:
                continue
            except Exception as e:
                print(f"Unexpected error while accessing {key}: {e}")
                return
        print("Stimulation parameters not found in any known key.")

    def get_time(self): 
        try:
            timestep = self.infos['SampleInterval'] 
            datapoints = self.infos['SamplesPerWave'].astype(int)
            tot_time = np.round(timestep * datapoints).astype(int) 
            time = np.linspace(0, tot_time, num=datapoints)
            print("OK time scale found")
            self.time=time
            return time
        except BaseException: ## if information not present in file for some reason   
            timestep_ = self.config["timestep_"] 
            datapoints_ = self.config["datapoints_"] 
            tot_time_ = np.round(timestep_ * datapoints_).astype(int) 
            time_ = np.linspace(0, tot_time_, num=datapoints_)
            print("Error getting time scale, by default 0-2000 ms with 0.01 timestep")
            self.time=time_
            return time_
  

    #Methods to analyse data
 
    def get_baselines(self):
        averages_baselines = []
        for recording in self.response: 
            bsl_start = self.config["bsl_start"]
            bsl_end = self.config["bsl_end"]
            recording_baseline = recording[bsl_start:bsl_end]
            average_baseline = np.mean(recording_baseline)
            averages_baselines.append(average_baseline)
        return averages_baselines

    def get_boundaries(self): #to FIX
        bound1_start = self.config["bound1_start"]
        bound1_end = self.config["bound1_end"] 
        bound2_start = self.config["bound2_start"]
        bound2_end = self.config["bound2_end"]
        return bound1_start, bound1_end, bound2_start, bound2_end

    def get_mem_values(self, recording, time, delta_v = 5*1e-3): 
        Id_bound_start = self.config["Id_bound_start"]
        Id_bound_stop = self.config["Id_bound_stop"]
        Id = np.abs(np.min(recording[Id_bound_start:Id_bound_stop])) #in nano amperes, check if work
        Id_A = Id * 1e-9   # in amperes

        Ra = np.abs(delta_v/Id_A)  #in ohm   (volts/amperes)

        bsl_start = self.config["bsl_start"]
        bsl_end = self.config["bsl_end"]
        Idss_bound_start = self.config["Idss_bound_start"]
        Idss_bound_stop = self.config["Idss_bound_stop"]
        baseline = np.abs(np.mean(recording[bsl_start:bsl_end]))      # in nano amperes
        Idss = np.abs(np.mean(recording[Idss_bound_start:Idss_bound_stop]))   # in nano amperes
        Idss2 = Idss - baseline
        Idss_A = Idss2 * 1e-9   # in amperes
        baseline_A = baseline * 1e-9  # in amperes

        #Rm = (delta_v - Ra * Idss_A) / Idss_A #in Ohm
        Rm = delta_v / Idss_A #in Ohm

        start_fit = self.config["start_fit"]
        end_fit = self.config["end_fit"]
        try:
            params_exp1 = cf.get_params_function(cf.model_biexponential1, start_fit, end_fit, recording, time)
            
        except: 
            params_exp1 = cf.get_params_function(cf.model_exponential, start_fit, end_fit, recording, time)
        
        #print( params_exp1[2])
        tau = np.abs(params_exp1[2])  #in ms
        tau_s = tau * 1e-3  #in s
        #print(tau)
        Cm = np.abs(tau_s / (1/(1/Ra + 1/Rm)) ) #in F

        #print("mem values")
        #print("Id ", Id_A)
        #print("Rm ", Rm)
        #print("Ra ", Ra)
        #print("Cm", Cm)

        #assign attribute values
        self.baseline = baseline_A
        self.Id_A = Id_A
        self.Ra = Ra
        self.Rm = Rm
        self.Cm = Cm

        return baseline_A, Id_A, Ra, Rm, Cm

    def get_mem_values_across_time(self, time):
        baseline_list, Id_list, Ra_list, Rm_list, Cm_list = [], [], [], [], []

        for recording in self.response: 
            values = self.get_mem_values(recording, time)
            baseline_list.append(values[0]*1e12)
            Id_list.append(values[1]*1e12)
            Ra_list.append(values[2]/1e6)
            Rm_list.append(values[3]/1e6)
            Cm_list.append(values[4]*1e12)
            
        self.baseline_std = np.std(baseline_list)  #compare with self.baseline_sd
        print("std : ", self.baseline_std)
        return Id_list, Ra_list, Rm_list, Cm_list
             
    def calc_values(self, bis=False):
        self.get_mem_values(self.avg_response, self.time)  #useless here?
        if self.infos['Type']=='AMPA':
            self.analyse_neg_peak()
        elif self.infos['Type']=='NMDA':
            self.analyse_pos_peak()
        elif self.infos['Type']=='AMPA,NMDA':
            self.analyse_pos_peak(bis)   
        return 0

    def analyse_neg_peak(self):
        
        peak = "negative"
        
        start, stop, start2, stop2 = self.get_boundaries()
        start_ = start*100
        stop_ = stop*100
        start2_ = start2*100
        stop2_ = stop2*100
        
        amp_resp1 = np.min(self.smooth_avg_response[start_:stop_])  ## stimulation at 100 000th datapoint aka 1 000 ms
        time_peak_resp1 = np.argmin(self.smooth_avg_response[start_:stop_])
        #print("min found : ", amp_resp1)
        #print(time_peak_resp1)
    
        amp_resp2 = np.min(self.smooth_avg_response[start2_:stop2_])  ## stimulation at 105 000th datapoint aka 1 050 ms
        PPR = amp_resp2/amp_resp1
        
        #####################################################################
        
        ##rise time 10-90%
        
        bound1 = 0.1 * amp_resp1
        bound2 = 0.9 * amp_resp1
        
        range = self.smooth_avg_response[start_:stop_]
        
        peak_rise_start = self.config["peak_rise_start"]
        i = peak_rise_start
        j = peak_rise_start

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
        range = self.smooth_avg_response[start_ + time_peak_resp1 : stop_]
        

        k = self.config["peak_decay_start"]
        time = 0

        for value in range : 
            if value > bound:
                time = k
                break;
            k+= 0.01 
        
        decay_time = np.abs(time - self.config["peak_decay_start"])

        print("Amplitude response 1 (nA) : ", amp_resp1 )
        print("Amplitude response 2 (nA) : ", amp_resp2 )
        print("Paired pulse ratio Amp2/Amp1: ", PPR )
        print("Rise_time 10-90% : ", rise_time, "ms.")
        print("Decay time 50% : ", decay_time, " ms.")
        
        self.amp_resp1 = amp_resp1
        self.amp_resp2 = amp_resp2
        self.PPR = PPR
        self.rise_time = rise_time
        self.decay_time = decay_time

        return peak, amp_resp1, amp_resp2, PPR, rise_time, decay_time

    def analyse_pos_peak(self):
        
        peak = "positive"
        
        start, stop, start2, stop2 = self.get_boundaries()
        start_ = start*100
        stop_ = stop*100
        start2_ = start2*100
        stop2_ = stop2*100
        
        amp_resp1 = np.max(self.smooth_avg_response[start_:stop_])  ## stimulation at 100 000th datapoint aka 1 000 ms   #changed to max
        index_peak_resp1 = np.argmax(self.smooth_avg_response[start_:stop_])  
        time_peak_resp1 = (start_ + index_peak_resp1)/100
        
        #print("max found : ", amp_resp1)
        #print(index_peak_resp1)
        #print("time peak response 1: ", time_peak_resp1)
        
        amp_resp2 = np.max(self.smooth_avg_response[start2_:stop2_])  ## stimulation at 105 000th datapoint aka 1 050 ms   #changed to max
        
        PPR = amp_resp2/amp_resp1
        #####################################################################
        
        ##rise time 10-90%
        
        bound1 = 0.1 * amp_resp1
        bound2 = 0.9 * amp_resp1
        
        range = self.smooth_avg_response[start_:stop_]  #generalize boundaries
        
        l = self.config['peak_rise_start']  #generalize
        m = self.config['peak_rise_start']  #generalize
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
        range = self.smooth_avg_response[int(time_peak_resp1*100) :stop_] #generalize boundaries
        
        #print(start_)
        #print(start_ + index_peak_resp1)
        #print(stop_)
        k = self.config['peak_decay_start_pos'] 
        time = 0
        for value in range : 
            if value < bound:
                time = k
                break;
            k+= 0.01 
            
        decay_time = np.abs(time - time_peak_resp1)

        out_value = np.abs(self.config["time_stim2"] - time_peak_resp1)
        #print("out_value " ,out_value)
        if decay_time > out_value:
            decay_time = out_value

        print("Amplitude response 1 (nA) : ", amp_resp1 )
        print("Amplitude response 2 (nA) : ", amp_resp2 )
        print("Paired pulse ratio Amp2/Amp1: ", PPR )
        print("Rise_time 10-90% : ", rise_time, "ms.")
        print("Decay time 50% : ", decay_time, " ms.")

        self.amp_resp1 = amp_resp1
        self.amp_resp2 = amp_resp2
        self.PPR = PPR
        self.rise_time = rise_time
        self.decay_time = decay_time

        return peak, amp_resp1, amp_resp2, PPR, rise_time, decay_time
       

    
    '''
    def get_std_baseline(self):
        baseline = self.response[bsl_start:bsl_end]
        self.baseline_sd = baseline
        print("sd", self.baseline_sd)
        return 0
    '''