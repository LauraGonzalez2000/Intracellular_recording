import numpy as np
import pandas as pd
import Curve_fit as cf
from igor2.packed import load as loadpxp
from scipy.ndimage import gaussian_filter1d

class DataFile:
    #Constructor
    def __init__(self, file_path, info_df):
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
        self.fill_stim()
        self.get_time()
        

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
            avg_baseline = np.mean(avg_data[0:50])
            average_data_aligned = avg_data - avg_baseline
            self.avg_response = average_data_aligned
            print("OK average_recordings_aligned found")
        except: 
            print("Error method get_average_recordings_aligned(self)")
            return -1
        return average_data_aligned
    
    def smooth_gauss_avg(self, sigma=4):
        try: 
            smooth_avg = gaussian_filter1d(self.avg_response, sigma)
            self.smooth_avg_response = smooth_avg
            print("OK smoothing of average_recordings_aligned")
        except Exception as e:
            print(f'Error with smoothing {e}')
        return smooth_avg
    
    def fill_infos(self, info_df):
        try:
           
            meta_info_df = info_df.loc[info_df['Files'] == self.filename]

            if len(meta_info_df) != 1:
                raise ValueError(f"Expected one matching row for filename {self.filename}, but found {len(meta_info_df)}.")
        
            self.infos = {'SampleInterval' : self.pxp[1]['root'][b'SampleInterval'],
                          'SamplesPerWave' : self.pxp[1]['root'][b'SamplesPerWave'],
                          'FileDate' : self.pxp[1]['root'][b'FileDate'],
                          'FileTime' : self.pxp[1]['root'][b'FileTime'],
                          'Type': str(meta_info_df["Type"].item()),
                          'Euthanize method':str(meta_info_df["euthanize method"].item()),
                          'Holding (mV)': str(meta_info_df["Holding (mV)"].item()),
                          'Drug1':str(meta_info_df["Drug1"].item()),
                          'Drug2': str(meta_info_df["Drug2"].item())
                          }
            print('OK infos were filled correctly')
        except Exception as e:
            print(f"Infos were not filled correctly: {e}")

    def fill_stim(self):
        try: 
            pulse_DAC0 = self.pxp[1]['root'][b'nmStimSofia1'][b'DAC_0_0'].wave['wave']['wData']
            pulse_DAC1 = self.pxp[1]['root'][b'nmStimSofia1'][b'DAC_1_0'].wave['wave']['wData']
            self.stim = {'Cmd1' : pulse_DAC0,
                         'Cmd2' : pulse_DAC1}
            print("OK stimulation traces found")
        except:
            try:
                pulse_DAC0 = self.pxp[1]['root'][b'nmStimSofia'][b'DAC_0_0'].wave['wave']['wData']
                pulse_DAC1 = self.pxp[1]['root'][b'nmStimSofia'][b'DAC_1_0'].wave['wave']['wData']
                self.stim = {'Cmd1' : pulse_DAC0,
                             'Cmd2' : pulse_DAC1}
                print("OK stimulation traces found")
            except Exception as e:
                print(f"stimulation parameters not found : {e}")

    def get_time(self, timestep_ = 0.01, datapoints_ = 100000): 
        try:
            timestep = self.infos['SampleInterval'] #timestep data acquisition in Igor (0.01 ms)
            datapoints = self.infos['SamplesPerWave'].astype(int)  #amount of datapoints acquired (200 000)
            tot_time = np.round(timestep * datapoints).astype(int) 
            time = np.linspace(0, tot_time, num=datapoints)
            print("OK time scale found")
            self.time=time
            return time
        except BaseException: ## if information not present in file for some reason    
            tot_time_ = np.round(timestep_ * datapoints_).astype(int) 
            time_ = np.linspace(0, tot_time_, num=datapoints_)
            print("Error getting time scale, by default 0-2000 ms with 0.01 timestep")
            self.time=time_
            return time_
  

    #Methods to analyse data
 
    def get_baselines(self):
        averages_baselines = []
        for recording in self.response: 
            recording_baseline = recording[0:50]
            average_baseline = np.mean(recording_baseline)
            averages_baselines.append(average_baseline)
        return averages_baselines

    def get_boundaries(self): #to FIX
        return 600, 650, 700, 750

    def get_mem_values(self, recording, time, delta_v = 5*1e-3): 

        Id = np.abs(np.min(recording[10000:11000])) #in nano amperes, check if work
        Id_A = Id * 1e-9   # in amperes

        Ra = np.abs(delta_v/Id_A)  #in ohm   (volts/amperes)

        baseline = np.abs(np.mean(recording[0:50]))
        Idss = np.abs(np.mean(recording[16000:19000]))   # in nano amperes
        #print("Idss ",Idss)
        Idss2 = Idss - baseline
        #print("Idss2 ",Idss2)
        Idss_A = Idss2 * 1e-9   # in amperes

        
        #Rm = (delta_v - Ra * Idss_A) / Idss_A #in Ohm
        Rm = delta_v / Idss_A #in Ohm


        try:
            params_exp1 = cf.get_params_function(cf.model_biexponential1, 10007, 20000, recording, time)
            
        except: 
            params_exp1 = cf.get_params_function(cf.model_exponential, 10007, 20000, recording, time)
        
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
        self.Id_A = Id_A
        self.Ra = Ra
        self.Rm = Rm
        self.Cm = Cm

        return Id_A, Ra, Rm, Cm

    def get_mem_values_across_time(self, time):
        Id_list, Ra_list, Rm_list, Cm_list = [], [], [], []
        #i = 0
        for recording in self.response: 
            #print(i)
            values = self.get_mem_values(recording, time)
            Id_list.append(values[0]*1e12)
            Ra_list.append(values[1]/1e6)
            Rm_list.append(values[2]/1e6)
            Cm_list.append(values[3]*1e12)
            #i+=1
        
        #print(Id_list)
        return Id_list, Ra_list, Rm_list, Cm_list
             
    def calc_values(self, bis=False):
        self.get_mem_values(self.avg_response, self.time)
        #print("calc_values ", self.infos['Type'])
        if self.infos['Type']=='AMPA':
            self.analyse_neg_peak()
        elif self.infos['Type']=='NMDA':
            self.analyse_pos_peak()
        elif self.infos['Type']=='AMPA,NMDA':
            self.analyse_pos_peak(bis)   
        return 0

    def analyse_neg_peak(self):
        #print("neg called")
        peak = "negative"
        
        start, stop, start2, stop2 = self.get_boundaries()
        #start_ = (start+1)*100
        start_ = (start+1)*100
        stop_ = (stop-1)*100
        start2_ = (start2+1)*100
        stop2_ = (stop2-1)*100
        #check this with new boundary function

        #print("start", start_)
        #print("stop", stop_)

        #100500
        #print("values where to look for min ", self.avg_response[start_:stop_])
        amp_resp1 = np.min(self.smooth_avg_response[start_:stop_])  ## stimulation at 100 000th datapoint aka 1 000 ms
        #print("min found : ", amp_resp1)
        time_peak_resp1 = np.argmin(self.smooth_avg_response[start_:stop_])
        #print(time_peak_resp1)
        #105500
        amp_resp2 = np.min(self.smooth_avg_response[start2_:stop2_])  ## stimulation at 105 000th datapoint aka 1 050 ms

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
        
        range = self.smooth_avg_response[start_:stop_]
        
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
        range = self.smooth_avg_response[start_ + time_peak_resp1 : stop_]
        
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
        
        self.amp_resp1 = amp_resp1
        self.amp_resp2 = amp_resp2
        self.PPR = PPR
        self.rise_time = rise_time
        self.decay_time = decay_time


        return peak, amp_resp1, amp_resp2, PPR, rise_time, decay_time

    def analyse_pos_peak(self, bis=False):
        
        #print("pos called")
        peak = "positive"
        #data = get_data(path)
        #average_data = get_average_recordings(get_recordings(data))
        #average_data_aligned = get_data_aligned(average_data)

        
        start, stop, start2, stop2 = self.get_boundaries()
        start_ = (start+1)*100   #usually, 100100
        stop_ = (stop-1)*100     #usually, 104900
        start2_ = (start2+1)*100 #usually, 105100
        stop2_ = (stop2-1)*100   #usually, 109900
        
        #print("hey")
        #print("start_ : ", start_, "stop_ : ", stop_)
        #print("len ",len(self.avg_response))
        #print("values where to look for maximum ",self.avg_response[start_:stop_])
        amp_resp1 = np.max(self.smooth_avg_response[start_:stop_])  ## stimulation at 100 000th datapoint aka 1 000 ms   #changed to max
        #print("max found : ", amp_resp1)
        index_peak_resp1 = np.argmax(self.smooth_avg_response[start_:stop_])  
        time_peak_resp1 = (start_ + index_peak_resp1)/100
        
        #print(index_peak_resp1)
        
        #print("time peak response 1: ", time_peak_resp1)
        
        if bis==False:
            amp_resp2 = np.max(self.smooth_avg_response[start2_:stop2_])  ## stimulation at 105 000th datapoint aka 1 050 ms   #changed to max
        elif bis==True:
            amp_resp2 = np.mean(self.smooth_avg_response[start_+5990:start_+6090])  ## stimulation 60 ms after

        PPR = amp_resp2/amp_resp1
        #####################################################################
        
        ##rise time 10-90%
        
        bound1 = 0.1 * amp_resp1
        bound2 = 0.9 * amp_resp1
        
        range = self.smooth_avg_response[start_:stop_]  #generalize boundaries
        
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
        range = self.smooth_avg_response[int(time_peak_resp1*100) :stop_] #generalize boundaries
        
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

        out_value = np.abs(700 - time_peak_resp1)
        #print("out_value " ,out_value)
        if decay_time > out_value:
            decay_time = out_value

        '''
        print("Amplitude response 1 (nA) : ", amp_resp1 )
        print("Amplitude response 2 (nA) : ", amp_resp2 )
        print("Paired pulse ratio Amp2/Amp1: ", PPR )
        print("Rise_time 10-90% : ", rise_time, "ms.")
        print("Decay time 50% : ", decay_time, " ms.")


        '''

        self.amp_resp1 = amp_resp1
        self.amp_resp2 = amp_resp2
        self.PPR = PPR
        self.rise_time = rise_time
        self.decay_time = decay_time

        return peak, amp_resp1, amp_resp2, PPR, rise_time, decay_time
       

