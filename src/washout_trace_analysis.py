import numpy as np
import statistics
from igor2.packed import load as loadpxp

from scipy.signal import butter, lfilter, freqz

import pandas as pd


meta_info_directory = 'C:/Users/laura.gonzalez/Programming/Intracellular_recording/src/Files1test.csv'

class DataFile_washout:

    #Constructor
    def __init__(self, file_path):
        self.file_path = file_path
        self.filename = self.file_path.split('/')[-1].replace('.pxp', '')
        self.infos = {}
        self.stim = {}
        self.recordings = None
        self.recordings_f = None
        self.load_data()
        self.get_recordings()
        self.fill_infos()
        self.fill_stim()

    #Methods
    def load_data(self):
        try:
            self.pxp = loadpxp(self.file_path)
            print("OK data was loaded")
        except Exception as e:
            print(f"Data was not loaded: {e}")
            return -1
        return self.pxp
    

    def butter_lowpass_filter(self, data, cutoff=1.1, fs=100, order=6):   #math class
        b, a = butter(order, cutoff, fs=fs, btype='low', analog=False)
        y = lfilter(b, a, data)
        return y
  
    def get_recordings(self):
        try:
            DATA = []
            DATA_f = []
            i = 0
            while True:
                key = b'RecordA%i' % i
                if key in self.pxp[1]['root']:
                    recording = self.pxp[1]['root'][key].wave['wave']['wData']
                    DATA.append(recording)
                    
                    recording_ = np.concatenate((recording[:59999], recording[60060:69999],recording[70060:])) #remove artefact
                    recording_f = self.butter_lowpass_filter(recording_)
                    DATA_f.append(recording_f)
                    i += 1
                else:
                    break
            self.recordings = np.array(DATA, dtype=np.float16 ) #uses less memory
            self.recordings_f = np.array(DATA_f, dtype=np.float16 ) #uses less memory

            print('OK Recordings were loaded')
            return 0
        except Exception as e:
            print(f'Recordings were not loaded: {e}')
            return -1
        
    def get_batches(self, list, batch_size=6):
        means = []
        std = []
        for i in range(0, len(list), batch_size):
            means.append(np.mean(list[i:i+batch_size]))
            #sem.append(stats.sem(list[i:i+batch_size]))
            std.append(np.std(list[i:i+batch_size]))
        return means, std


    def find_noise(self, recording):
        baseline = recording[52000:58000]
        mean_baseline = np.mean(baseline)
        std_baseline = np.std(baseline)
        min_baseline = np.min(baseline)
        noise = np.abs(mean_baseline - min_baseline)
        #noise = 2*std_baseline
        #print("noise : ", noise)
        return noise

    def get_noises(self):
        noises = []
        for recording in self.recordings_f:
            noise = self.find_noise(recording)
            noises.append(noise)
        return noises


    def find_diff(self, recording):

        #find baseline
        recording_baseline = recording[52000:58000]
        avg_baseline = statistics.mean(recording_baseline)

        #find minimum
        recording_roi = recording[60200:62000]
        min = np.min(recording_roi)

        #compute diff
        diff =  avg_baseline - min

        #print("baseline : ",avg_baseline)
        #print("min : ",min)
        #print("diff : ",diff)

        return diff

    def get_diffs(self):
        diffs = []
        for recording in self.recordings_f:
            diff = self.find_diff(recording)
            diffs.append(diff)
        self.diffs = diffs
        return diffs
    
    def correct_diffs(self,diffs, noises):
        diffs_c = []
        i=0
        #for diff in diffs:
        #    if np.abs(diff)<np.abs(noises[i]): diffs_c.append(0)
        #    else:diffs_c.append(diff)
        #    i+=1
        for diff in diffs:
            diffs_c.append(diff-noises[i])
            i+=1

        self.corr_diffs = diffs_c

        return diffs_c


    def get_baselines(self):
        baselines = []
        i=0
        for recording in self.recordings_f:
            baseline = recording[52000:58000]  #good values?
            baselines.append(baseline)
            if np.mean(baseline) <= -0.7:
                print("cell was lost at the sweep ", i, " ( = ", i/6, " min). The leak was ", np.mean(baseline) )
            i+=1
        return baselines
    
    def get_Ids(self):
        Ids = []
        for recording in self.recordings:
            baseline = recording[12000:19000]
            max = np.max(recording[19000:21000])
            Ids.append(max-baseline)
        return Ids
    
    def get_time(self, timestep_ = 0.01, datapoints_ = 100000): 
        try:
            timestep = self.infos['SampleInterval'] #timestep data acquisition in Igor (0.01 ms)
            datapoints = self.infos['SamplesPerWave'].astype(int)  #amount of datapoints acquired (200 000)
            tot_time = np.round(timestep * datapoints).astype(int) 
            time = np.linspace(0, tot_time, num=datapoints)
            print("OK time scale found")
            return time
        except BaseException: ## if information not present in file for some reason    
            tot_time_ = np.round(timestep_ * datapoints_).astype(int) 
            time_ = np.linspace(0, tot_time_, num=datapoints_)
            print("Error getting time scale, by default 0-2000 ms with 0.01 timestep")
            return time_
        
    def fill_infos(self):
        try:
            file_meta_info = open(meta_info_directory, 'r')  
            info_df = pd.read_csv(file_meta_info, header=0, sep=';')
            info_df_datafile = info_df.loc[info_df['Files'] == self.filename]

            if len(info_df_datafile) != 1:
                raise ValueError(f"Expected one matching row for filename {self.filename}, but found {len(info_df_datafile)}.")
        

            self.infos = {'SampleInterval' : self.pxp[1]['root'][b'SampleInterval'],
                          'SamplesPerWave' : self.pxp[1]['root'][b'SamplesPerWave'],
                          'FileDate' : self.pxp[1]['root'][b'FileDate'],
                          'FileTime' : self.pxp[1]['root'][b'FileTime'],
                          'File': str(info_df_datafile["Files"].item()),
                          'Euthanize method':str(info_df_datafile["euthanize method"].item()),
                          'Holding (mV)': str(info_df_datafile["Holding (mV)"].item()),
                          'Infusion substance':str(info_df_datafile["infusion"].item()),
                          'Infusion concentration': str(info_df_datafile["infusion concentration"].item()),
                          'Infusion start':str(info_df_datafile["infusion start"].item()),
                          'Infusion end':str(info_df_datafile["infusion end"].item()),
                          'Group':str(info_df_datafile["Group"].item())
                          }
            print('OK infos were filled correctly')
        except Exception as e:
            print(f"Infos were not filled correctly: {e}")

    def fill_stim(self):
        try: 
            pulse_DAC0 = self.pxp[1]['root'][b'nm_washout_keta2'][b'DAC_0_0'].wave['wave']['wData']  #nm_washout_keta2 changes depending on file
            pulse_DAC1 = self.pxp[1]['root'][b'nm_washout_keta2'][b'DAC_1_0'].wave['wave']['wData']
            self.stim = {'Cmd1' : pulse_DAC0,
                         'Cmd2' : pulse_DAC1}
            print("OK stimulation traces found")
        except Exception as e:
            try:
                pulse_DAC0 = self.pxp[1]['root'][b'nm_washout_keta1'][b'DAC_0_0'].wave['wave']['wData']  #nm_washout_keta2 changes depending on file
                pulse_DAC1 = self.pxp[1]['root'][b'nm_washout_keta1'][b'DAC_1_0'].wave['wave']['wData']
                self.stim = {'Cmd1' : pulse_DAC0,
                             'Cmd2' : pulse_DAC1}
                print("OK stimulation traces found")
            except:
                try:
                    pulse_DAC0 = self.pxp[1]['root'][b'nm_washout_keta'][b'DAC_0_0'].wave['wave']['wData']  #nm_washout_keta2 changes depending on file
                    pulse_DAC1 = self.pxp[1]['root'][b'nm_washout_keta'][b'DAC_1_0'].wave['wave']['wData']
                    self.stim = {'Cmd1' : pulse_DAC0,
                                 'Cmd2' : pulse_DAC1}
                    print("OK stimulation traces found")
                except:
                    try:
                        pulse_DAC0 = self.pxp[1]['root'][b'nmStimSofia1'][b'DAC_0_0'].wave['wave']['wData']  #nm_washout_keta2 changes depending on file
                        pulse_DAC1 = self.pxp[1]['root'][b'nmStimSofia1'][b'DAC_1_0'].wave['wave']['wData']
                        self.stim = {'Cmd1' : pulse_DAC0,
                                     'Cmd2' : pulse_DAC1}
                        print("OK stimulation traces found")
                    except:
                        try:
                            pulse_DAC0 = self.pxp[1]['root'][b'nmStimSofia'][b'DAC_0_0'].wave['wave']['wData']  #nm_washout_keta2 changes depending on file
                            pulse_DAC1 = self.pxp[1]['root'][b'nmStimSofia'][b'DAC_1_0'].wave['wave']['wData']
                            self.stim = {'Cmd1' : pulse_DAC0,
                                         'Cmd2' : pulse_DAC1}
                            print("OK stimulation traces found")
                        except:
                            print(f'Stimulation parameters not found: {e}')
    
    
    def get_subsets(self):

        diffs = self.get_diffs() 
        batches_diff_m, _ = self.get_batches(diffs)
        try:
            subset1 = batches_diff_m[int(self.infos["Infusion start"])-5: int(self.infos["Infusion start"])]
            subset2 = batches_diff_m[int(self.infos["Infusion end"])-5: int(self.infos["Infusion end"])]
            subset3 = batches_diff_m[int(len(self.recordings)/6)-5:int(len(self.recordings)/6)]
        except:
            subset1 = batches_diff_m[5:10]
            subset2 = batches_diff_m[12: 17]
            subset3 = batches_diff_m[45:50]

        return subset1, subset2, subset3
    
    def get_values_barplot(self):

        subset1, subset2, subset3 = self.get_subsets()
        bsl_m = np.mean(subset1)
        bsl_std = np.std(subset1)
        inf_m = np.mean(subset2)
        inf_std = np.std(subset2)
        wash_m = np.mean(subset3)
        wash_std = np.std(subset3)

        return bsl_m, bsl_std, inf_m, inf_std, wash_m, wash_std


    '''
    def find_diff(recording):

        #find baseline
        recording_baseline = recording[52000:58000]
        avg_baseline = statistics.mean(recording_baseline)

        #find minimum
        recording_roi = recording[60200:62000]
        min = np.min(recording_roi)

        #compute diff
        diff =  min - avg_baseline

        #print("baseline : ",avg_baseline)
        #print("min : ",min)
        #print("diff : ",diff)

        return diff
    '''
    '''
    def get_diffs(recordings):
        diffs = []
        for recording in recordings:
            diff = find_diff(recording)
            if diff>-0.17 :
                diffs.append(diff)
        return diffs
    '''
