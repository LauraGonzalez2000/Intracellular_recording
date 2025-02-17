import numpy as np
from igor2.packed import load as loadpxp

from scipy.signal import butter, lfilter

import pandas as pd
import os

from scipy.stats import f_oneway, tukey_hsd, normaltest, kruskal, levene
import scikit_posthocs as sp


meta_info_directory = "Files.csv"
base_path = os.path.join(os.path.expanduser('~'), 'DATA', 'In_Vitro_experiments','Washout_experiment') #keep this aborescence if program used in other computers
meta_info_directory = os.path.join(base_path, meta_info_directory)


class DataFile_washout:

    #Constructor
    def __init__(self, file_path, debug=False):
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
        self.fill_infos(debug=debug)
        self.fill_stim()
        #self.clean_end(debug=debug)
        

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
            #print('len recording : ', len(self.recordings_f))
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
            diff_c = max(0.0, diff-noises[i])  #force positive number
            diffs_c.append(diff_c)
            i+=1
        self.corr_diffs = diffs_c
        return diffs_c
    
    def batches_correct_diffs(self):
        batches_c_diffs_mean, _  = self.get_batches(self.corr_diffs)
        self.batches_corr_diffs = batches_c_diffs_mean
        return batches_c_diffs_mean, _
    
    def fill_infos(self, debug=False):
        try:
            file_meta_info = open(meta_info_directory, 'r')  
            info_df = pd.read_csv(file_meta_info, header=0, sep=';')
            info_df_datafile = info_df.loc[info_df['Files'] == self.filename]

            if len(info_df_datafile) != 1:
                raise ValueError(f"Expected one matching row for filename {self.filename}, but found {len(info_df_datafile)}.")

            try: 
                inf_start = float(info_df_datafile["infusion start"].item().replace(',', '.'))
                inf_stop = float(info_df_datafile["infusion end"].item().replace(',', '.'))
            except: 
                inf_start = str(info_df_datafile["infusion start"].item())
                inf_stop = str(info_df_datafile["infusion end"].item())

            self.infos = {'SampleInterval' : self.pxp[1]['root'][b'SampleInterval'],
                          'SamplesPerWave' : self.pxp[1]['root'][b'SamplesPerWave'],
                          'FileDate' : self.pxp[1]['root'][b'FileDate'],
                          'FileTime' : self.pxp[1]['root'][b'FileTime'],
                          'File': self.filename,
                          'Euthanize method':str(info_df_datafile["euthanize method"].item()),
                          'Holding (mV)': str(info_df_datafile["Holding (mV)"].item()),
                          'Infusion substance':str(info_df_datafile["infusion"].item()),
                          'Infusion concentration': str(info_df_datafile["infusion concentration"].item()),
                          'Infusion start': inf_start,  
                          'Infusion end': inf_stop,  
                          'Group':str(info_df_datafile["Group"].item())}
            
            print('OK infos were filled correctly')

            if debug: 
                for key, value in self.infos.items():
                    print(f"The key '{key}' is {type(value)} and the value is {value}")
        
        except Exception as e:
            print(f"Infos were not filled correctly: {e}")

    def fill_stim(self):
        keys = [ b'nm_washout_keta2', b'nm_washout_keta1', b'nm_washout_keta', 
                 b'nmStimSofia1', b'nmStimSofia']
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
        for recording in self.recordings:  #calculate the Ids (access) without filtering!
            baseline = recording[0:5000]
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
        if self.infos['Group'] == 'D-AP5' or self.infos['Group']=='ketamine' or self.infos['Group']=='memantine': 
            baseline_diffs_m = np.mean(batches_diffs_m[(round(float(self.infos["Infusion start"]))-4):round(float(self.infos["Infusion start"]))+1])
        elif self.infos['Group'] == 'control':
            baseline_diffs_m = np.mean(batches_diffs_m[6:11])    
        return baseline_diffs_m
    

    #utils?
    def normalize(self, list_m, list_std):   # Normalization by baseline mean (Baseline at 100%)
        baseline_diffs_m = self.find_baseline_diffs_m()
        list_m_norm = (list_m / baseline_diffs_m) * 100  
        list_std_norm = (list_std / baseline_diffs_m) * 100  
        return list_m_norm, list_std_norm

    def get_subsets(self, wash='all'):
        batches_c_diffs_mean,  batches_c_diffs_std  = self.get_batches(self.corr_diffs)
        norm_batches_corr_diffs, _ = self.normalize(batches_c_diffs_mean,  batches_c_diffs_std)
        try:
            subset1 = norm_batches_corr_diffs[round(self.infos["Infusion start"])-4 : round(self.infos["Infusion start"])+1]
            subset2 = norm_batches_corr_diffs[round(self.infos["Infusion end"])-2   : round(self.infos["Infusion end"])+2]
            if wash=='all':
                subset3 = norm_batches_corr_diffs[round(len(self.recordings)/6)-5       : round(len(self.recordings)/6)]
            elif wash=='50 min':
                subset3 = norm_batches_corr_diffs[46-5:46]
                
            #subset1 = norm_batches_corr_diffs[int(self.infos["Infusion start"])-5: int(self.infos["Infusion start"])]
            #subset2 = norm_batches_corr_diffs[int(self.infos["Infusion end"])-5: int(self.infos["Infusion end"])]
            #subset3 = norm_batches_corr_diffs[int(len(self.recordings)/6)-5:int(len(self.recordings)/6)]
        except:
            if self.infos['Group']=='memantine':
                subset1 = norm_batches_corr_diffs[2:7]
                subset2 = norm_batches_corr_diffs[11:15]
                subset3 = norm_batches_corr_diffs[round(len(self.recordings)/6)-5       : round(len(self.recordings)/6)]
                #print("subsets 5-10_10-17_end-5-end")

            else: 
                subset1 = norm_batches_corr_diffs[6:11]
                subset2 = norm_batches_corr_diffs[15:19]
                subset3 = norm_batches_corr_diffs[45:50]
                #print("subsets 5-10_10-17_45-50")
        return subset1, subset2, subset3

    def get_barplot(self, wash='all'):
        subset1, subset2, subset3 = self.get_subsets(wash)
        barplot = {'End baseline' : {'values': subset1,  'mean' : np.mean(subset1), 'sem': np.std(subset1)/np.sqrt(len(subset1)),  'std': np.std(subset1)},
                   'End infusion' : {'values': subset2,  'mean' : np.mean(subset2), 'sem': np.std(subset2)/np.sqrt(len(subset2)),  'std': np.std(subset2)},
                   'End wash'     : {'values': subset3,  'mean' : np.mean(subset3), 'sem': np.std(subset3)/np.sqrt(len(subset3)),  'std': np.std(subset3)}}
        return barplot

    def clean_end(self, debug=False):

        erase1, erase2 = False, False
        Ids = self.get_Ids()
        Ids_batches, _ = self.get_batches(Ids)

        min = 0
        problem1 = 0
        start_pb1 = 0
        
        for Id in Ids_batches: 
            if Id < 0.29:
                
                if problem1==0: 
                    start_pb1 = min
                print(f'cell closed at min {min}')
                problem1 +=1
                
            min +=1

        if debug: 
            print("Ids batches : ", Ids_batches)
            print("len Ids batches: ", len(Ids_batches))
            print("problem1", problem1)
            print("start pb1", start_pb1)

        if problem1 > 15 :
            print(f'cell closed for {problem1} min -> end recording should be erased since min {start_pb1}')
            erase1 = True

        ########################################

        leaks = self.get_baselines()
        leaks_batches, _ = self.get_batches(leaks)
        min = 0
        problem2 = 0
        start_pb2 = 0
        for leak in leaks_batches:
            if leak < -1:
                if problem2==0: 
                    start_pb2 = min
                print(f'Leak is too big at min {min}')
                problem2 +=1
                
            min +=1

        if debug: 
            print("leak batches : ", leaks_batches)
            print("len leak batches: ", len(leaks_batches))
            print("problem2", problem2)
            print("start pb2", start_pb2)

        if problem2 > 3 and start_pb2 > len(leaks_batches) - 10 :
            print(f'cell died for {problem2} min -> end recording should be erased since min {start_pb2}')
            erase2 = True


        ######################## cleaning end #######################

        if erase1 or erase2: 
        
            if erase1 and not erase2: 
                min_cutoff = start_pb1
            
            if erase2 and not erase1:
                min_cutoff = start_pb2

            if erase1 and erase2 :
                print(start_pb1, start_pb2)
                min_cutoff = np.min(start_pb1, start_pb2)
                print(self.batches_corr_diffs)
                print(len(self.batches_corr_diffs))

            print(len(self.batches_corr_diffs))
            #self.batches_corr_diffs = self.batches_corr_diffs[0:min_cutoff]
            #self.batches_corr_diffs[min_cutoff:] = np.nan
            self.batches_corr_diffs = [val if idx < min_cutoff else float('nan') for idx, val in enumerate(self.batches_corr_diffs)]
            print(len(self.batches_corr_diffs))

        return 0
    
    def calc_stats(self):
        values_barplot = self.get_barplot()

        parametric = self.test_parametric_conditions(values_barplot)
        # One way ANOVA test
        # null hypothesis : all groups are statistically similar
        if parametric:
            print("Parametric test")
            F_stat, p_val = f_oneway(values_barplot['End baseline']['values'], 
                                     values_barplot['End infusion']['values'], 
                                     values_barplot['End wash']['values'] )
            #print("F ", F_stat) 
            #print("p value", p_val)   
            if p_val < 0.05: #we can reject the null hypothesis, therefore there exists differences between groups
                #In order to differenciate groups, Tukey post hoc test    #could be Dunnett -> compare with control?
                Tukey_result = tukey_hsd(values_barplot['End baseline']['values'], 
                                         values_barplot['End infusion']['values'], 
                                         values_barplot['End wash']['values'] )
                #print("Tukey stats ", Tukey_result.statistic) 
                #print("Tukey pvalues", Tukey_result.pvalue)   
                final_stats = Tukey_result.pvalue
        # Non parametric test : Kruskal Wallis test
        # Tests the null hypothesis that the population median of all of the groups are equal.
        else: 
            print("Non parametric test")
            F_stat, p_val = kruskal(values_barplot['End baseline']['values'], 
                                    values_barplot['End infusion']['values'], 
                                    values_barplot['End wash']['values'])
            #print("F ", F_stat) 
            #print("p value", p_val) 
            #print("p_val KW : ", p_val)
            if p_val < 0.05:
                #we can reject the null hypothesis, therefore there exists differences between groups
                #In order to differenciate groups, Dunn's post hoc test
                p_values = sp.posthoc_dunn(values_barplot['End baseline']['values'], 
                                           values_barplot['End infusion']['values'], 
                                           values_barplot['End wash']['values'] , 
                                           p_adjust='holm')
                final_stats = p_values
        #print("final stats : ", final_stats)
        return final_stats

    def test_parametric_conditions(self, values_barplot):
        parametric=True
        #test conditions to apply statistical test:
            
        #test normality (The three groups are normally distributed): 
        res1 = normaltest(values_barplot['End baseline']['values'])
        res2 = normaltest(values_barplot['End infusion']['values'])
        res3 = normaltest(values_barplot['End wash']['values'])
        if res1.statistic==np.float64(np.nan) or res2.statistic==np.float64(np.nan) or res3.statistic==np.float64(np.nan):
            parametric=False
            
        #test homoscedasticity (The three groups have a homogeneity of variance; meaning the population variances are equal):
        #The Levene test tests the null hypothesis that all input samples are from populations with equal variances.
        statistic, p_value = levene(values_barplot['End baseline']['values'], 
                                    values_barplot['End infusion']['values'], 
                                    values_barplot['End wash']['values'])
        if p_value <0.05:
            #null hypothesis is rejected, the population variances are not equal!
            parametric=False
        return parametric