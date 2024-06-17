import numpy as np
import matplotlib.pylab as plt

from igor2.packed import load as loadpxp

class DataFile:

    #constructor
    def __init__(self, file_path):
        self.file_path = file_path
        self.infos = {}
        self.stim = {}
        self.response = None
        self.load_data()
        self.get_recordings()
        self.fill_infos()
        self.fill_stim()



    #Methods to extract data
    def load_data(self):

        try:
            self.pxp = loadpxp(self.file_path)
            print("data was loaded")
        except:
            print("data was not loaded")
            return -1

        return self.pxp

    def get_recordings(self):
        try:
            DATA = []
            for i in range(39):
                DATA.append(self.pxp[1]['root'][b'RecordA%i'%i].wave['wave']['wData'])
            self.response = np.array(DATA)
            print('recordings were loaded')
            return self.response
        except:
            print('recordings were not loaded')
            return -1

    def fill_infos(self):
        try:
            self.infos = {'SampleInterval' : self.pxp[1]['root'][b'SampleInterval'],
                          'SamplesPerWave' : self.pxp[1]['root'][b'SamplesPerWave'],
                          'FileDate' : self.pxp[1]['root'][b'FileDate'],
                          'FileTime' : self.pxp[1]['root'][b'FileTime'],
                          }
            print('infos were filled correctly')
        except:
            print('infos were not filled correctly')

    def fill_stim(self):
        try: 
            pulse_DAC0 = self.pxp[1]['root'][b'nmStimSofia1'][b'DAC_0_0'].wave['wave']['wData']
            pulse_DAC1 = self.pxp[1]['root'][b'nmStimSofia1'][b'DAC_1_0'].wave['wave']['wData']
            self.stim = {'Cmd1' : pulse_DAC0,
                         'Cmd2' : pulse_DAC1}
            print("stimulation traces found")
        except:
            print("stimulation parameters not found")
        

    #methods to analyze data

    '''
        self.stim = {'voltage-pulse-cmd1':(1,Y),
                      'ectrical-stim'

        self.stim = (1,Y),
                        (1,Y)]

        self.data = [(40,100000),
                     (X,Y)]

        self.channel1 = (X,Y)
    '''

