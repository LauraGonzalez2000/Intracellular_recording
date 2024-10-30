import numpy as np
from igor2.packed import load as loadpxp

from scipy.signal import butter, lfilter

import pandas as pd

#meta_info_directory = 'C:/Users/LauraGonzalez/DATA/Washout_experiment/Files-q.csv' #in laptop
meta_info_directory = 'C:/Users/laura.gonzalez/DATA/Washout_experiment/Files-SST-q.csv' #in PC

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
        self.get_diffs()
        self.correct_diffs()
        self.batches_correct_diffs()
        self.fill_infos()
        self.fill_stim()

    #Methods

    #initialize attributes
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
            print('len recording : ', len(self.recordings_f))
            return 0
        except Exception as e:
            print(f'Recordings were not loaded: {e}')
            return -1
        
    def get_diffs(self):
        diffs = []
        for recording in self.recordings_f:
            diff = self.find_diff(recording)
            diffs.append(diff)
        self.diffs = diffs
        return diffs
    
    def correct_diffs(self):
        noises = self.get_noises()
        diffs_c = []
        i=0
        for diff in self.diffs:
            diffs_c.append(diff-noises[i])
            i+=1
        self.corr_diffs = diffs_c
        return diffs_c
    
    def batches_correct_diffs(self):
        batches_c_diffs_mean, _  = self.get_batches(self.corr_diffs)
        self.batches_corr_diffs = batches_c_diffs_mean
        return batches_c_diffs_mean, _
    
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
                          #'Infusion start':str(info_df_datafile["infusion start"].item()),
                          #'Infusion end':str(info_df_datafile["infusion end"].item()),
                          'Infusion start':float(info_df_datafile["infusion start"].item()),
                          'Infusion end':float(info_df_datafile["infusion end"].item()),
                          'Group':str(info_df_datafile["Group"].item())
                          }
            print('OK infos were filled correctly')
        except Exception as e:
            print(f"Infos were not filled correctly: {e}")

    def fill_stim(self):
        keys = [
            b'nm_washout_keta2', 
            b'nm_washout_keta1', 
            b'nm_washout_keta', 
            b'nmStimSofia1', 
            b'nmStimSofia'
        ]
        for key in keys:
            try:
                pulse_DAC0 = self.pxp[1]['root'][key][b'DAC_0_0'].wave['wave']['wData']
                pulse_DAC1 = self.pxp[1]['root'][key][b'DAC_1_0'].wave['wave']['wData']
                self.stim = {'Cmd1': pulse_DAC0, 'Cmd2': pulse_DAC1}
                print("OK stimulation traces found")
                return
            except KeyError:
                continue
        print("- Stimulation traces not found")
        
    #process info
    

    def find_noise(self, rec, bsl_start=52000, bsl_end=58000):
        baseline = rec[bsl_start:bsl_end]
        mean_baseline = np.mean(baseline)
        min_baseline = np.min(baseline)
        noise = np.abs(mean_baseline - min_baseline)   
        #std_baseline = np.std(baseline)
        #noise = 2*std_baseline
        return noise

    def get_noises(self):
        noises = []
        for recording_f in self.recordings_f:
            noise = self.find_noise(recording_f)
            noises.append(noise)
        return noises

    def find_diff(self, rec, bsl_start=52000, bsl_end=58000):
        recording_baseline = rec[bsl_start:bsl_end]
        avg_baseline = np.mean(recording_baseline)
        recording_roi = rec[60200:62000]
        min = np.min(recording_roi)
        diff =  avg_baseline - min
        return diff

    def get_baselines(self, bsl_start=52000, bsl_end=58000, debug=False):
        baselines = []
        i=0
        for recording in self.recordings_f:
            baseline = recording[bsl_start:bsl_end]
            baselines.append(baseline)

            if debug:
                if np.mean(baseline) <= -0.7:
                    print("cell was lost at the sweep ", i, " ( = ", i/6, " min). The leak was ", np.mean(baseline) )

            i+=1

        return baselines
    
    def get_Ids(self):
        Ids = []
        for recording in self.recordings_f:
            baseline = recording[12000:19000]
            max = np.max(recording[19500:20500])
            Ids.append(max-baseline)
        return Ids
    
    def get_batches(self, list, batch_size=6):
        means = []
        std = []
        for i in range(0, len(list), batch_size):
            means.append(np.mean(list[i:i+batch_size]))
            std.append(np.std(list[i:i+batch_size]))
        return means, std

    def find_baseline_diffs_m(self):
        batches_diffs_m, _ = self.get_batches(self.corr_diffs) #noise is substracted

        if self.infos['Group'] == 'APV' or self.infos['Group']=='KETA' or self.infos['Group']=='MEMANTINE': 
            baseline_diffs_m = np.mean(batches_diffs_m[(int(self.infos["Infusion start"])-5):int(self.infos["Infusion start"])]) 
            print("took last 5 minutes before infusion. Should always be the case for this protocol when there is infusion")
            print("mean last 5 min", baseline_diffs_m)
            print("mean last 10 min", np.mean(batches_diffs_m[(int(self.infos["Infusion start"])-10):int(self.infos["Infusion start"])]) )
        elif self.infos['Group'] == 'control':
            baseline_diffs_m = np.mean(batches_diffs_m[5:10])    
            print("took 5 min between min 5 and min 10. This should apply when there is no infusion")
            print("mean last 5 min", baseline_diffs_m)
            print("mean last 10 min", np.mean(batches_diffs_m[0:10]))

        return baseline_diffs_m
    
    def normalize(self, list_m, list_std):
        baseline_diffs_m = self.find_baseline_diffs_m()
        # Normalization by baseline mean (Baseline at 100%)
        list_m_norm = (list_m / baseline_diffs_m) * 100  
        list_std_norm = (list_std / baseline_diffs_m) * 100  
        return list_m_norm, list_std_norm

    def get_subsets(self):
        batches_c_diffs_mean,  batches_c_diffs_std  = self.get_batches(self.corr_diffs)
        norm_batches_corr_diffs, _ = self.normalize(batches_c_diffs_mean,  batches_c_diffs_std)
        try:
            subset1 = norm_batches_corr_diffs[int(self.infos["Infusion start"])-5: int(self.infos["Infusion start"])]
            subset2 = norm_batches_corr_diffs[int(self.infos["Infusion end"])-5: int(self.infos["Infusion end"])]
            subset3 = norm_batches_corr_diffs[int(len(self.recordings)/6)-5:int(len(self.recordings)/6)]
        except:
            subset1 = norm_batches_corr_diffs[5:10]
            subset2 = norm_batches_corr_diffs[12:17]
            subset3 = norm_batches_corr_diffs[45:50]
            print("subsets 5-10_10-17_45-50")
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



    