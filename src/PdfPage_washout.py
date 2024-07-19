import os
import matplotlib.pylab as plt
from washout_trace_analysis import DataFile_washout
import Curve_fit as cf
import numpy as np

from igor2.packed import load as loadpxp

class PdfPage:

    def __init__(self, 
                 structure_dict={},
                 debug=False):
        
        # figure in A0 format
        if debug:
            self.fig = plt.figure(figsize=(8.41/1.3,11.90/1.3))
        else:
            self.fig = plt.figure(figsize=(8.41,11.90))

        # default start and width for axes
        X0, DX = 0.12, 0.85 # x coords

        # dictionary of axes
        self.AXs = {}

        # build the axes one by one
        Y0, DY = 0.05, 0.18
        self.AXs['Notes'] = self.create_panel([X0, Y0, DX, DY], 'Notes')
        self.AXs['Notes'].axis('off')

        Y0 += 0.16
        DY = 0.03
        self.AXs['V_cmd0'] = self.create_panel([X0, Y0, DX, DY], 'V cmd 0')

        Y0 += 0.08
        DY = 0.03
        self.AXs['V_cmd1'] = self.create_panel([X0, Y0, DX, DY], 'V cmd 1')

        DY = 0.06
        Y0 += 0.06
        self.AXs['Id (nA)'] = self.create_panel([X0, Y0, DX, DY])

        DY = 0.06
        Y0 += 0.06
        self.AXs['Leak (nA)'] = self.create_panel([X0, Y0, DX, DY])

        Y0 += 0.12
        DY = 0.24
        self.AXs['Difference_peak_baseline'] = self.create_panel([X0, Y0, DX, DY], 'Response')

        Y0 += 0.12
        DY = 0.24
        self.AXs['RespAnalyzed'] = self.create_panel([X0, Y0, DX, DY], 'Response')

    def create_panel(self, coords, title=None):
        """ 
        coords: (x0, y0, dx, dy)
                from left to right
                from top to bottom (unlike matplotlib)
        """
        coords[1] = 1-coords[1]-coords[3]
        ax = self.fig.add_axes(rect=coords)

        if title:
            ax.set_title(title, loc='left', pad=2, fontsize=10)
        return ax

    def fill_PDF(self, datafile, debug=False): 

        time = datafile.get_time()

        for key in self.AXs:
            if key=='Notes': ##includes metadata
                txt = f"ID file: {datafile.filename}\nNumber of recordings: {len(datafile.recordings)}\n"
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
                try:
                    txt2 = f"ID file: {datafile.infos['Files']}\nEuthanize method: {datafile.infos['Euthanize method']}\nHolding:{datafile.infos['Holding (mV)']}\nInfusion:{datafile.infos['Infusion substance']}\nInfusion concentration:{datafile.infos['Infusion concentration']}\nInfusion start:{datafile.infos['Infusion start']}\nInfusion end:{datafile.infos['Infusion end']}\n"
                    self.AXs[key].annotate(txt2,(0, 1), va='top', xycoords='axes fraction')
                except:
                    print("metadata not added correctly")
                
            elif key=='V_cmd0':
                #self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("voltage (V)", (-0.12, -0.2), xycoords='axes fraction', rotation=90)
                self.AXs[key].plot(time, datafile.stim['Cmd1'])  
                
            elif key=='V_cmd1':
                #self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("voltage (V)", (-0.12, -0.8), xycoords='axes fraction', rotation=90)
                self.AXs[key].plot(time, datafile.stim['Cmd2'])  
                
                
            elif key=='Leak (nA)':
                #txt = f"Leak \n(A)"
                #self.AXs[key].annotate(txt, (-0.29, 0.2), xycoords='axes fraction', rotation=0)
                baselines = datafile.get_baselines()
                #print("baselines ",baselines)
                #print(len(baselines))
            
                baselines_m, baselines_std = datafile.get_batches(baselines)
                self.AXs[key].plot(baselines_m, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(baselines_m)), baselines_m, yerr=baselines_std, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                #self.AXs[key].set_ylim( -0.6, 0.1)
                self.AXs[key].set_ylabel("Baseline (=leak) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                try:
                    self.AXs[key].axvspan(datafile.infos["Infusion start"], datafile.infos["Infusion end"], color='lightgrey')
                except:
                    print("metadata not added correctly - or no infusion")
                #averages_baselines = datafile.get_baselines()
                #mean_leak = [np.mean(averages_baselines)] * len(averages_baselines)
                #self.AXs[key].plot(averages_baselines) 
                #self.AXs[key].plot(mean_leak, color="lightblue")

            elif key=='Id (nA)':
                Ids = datafile.get_Ids()
                Ids_m, Ids_std = datafile.get_batches(Ids)

                self.AXs[key].plot(Ids_m, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(Ids_m)), Ids_m, yerr=Ids_std, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                #self.AXs[key].set_ylim( 0, 140)
                self.AXs[key].set_ylabel("Id (=acces) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                try:
                    self.AXs[key].axvspan(datafile.infos["Infusion start"], datafile.infos["Infusion end"], color='lightgrey')
                except:
                    print("metadata not added correctly or no infusion")

            elif key=='Difference_peak_baseline':
                self.AXs[key].set_xlabel("time (ms)")
                diffs = datafile.get_diffs3() #noise was removed here
                batches_m, batches_std = datafile.get_batches(diffs)


                self.AXs[key].plot(batches_m, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(batches_m)), batches_m, yerr=batches_std, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                #self.AXs[key].set_ylim( -10, 140)
                self.AXs[key].set_ylabel("Difference_peak_baseline (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                try:
                    self.AXs[key].axvspan(datafile.infos["Infusion start"], datafile.infos["Infusion end"], color='lightgrey') #to fix
                except:
                    print("no infusion")


                
            elif key=='RespAnalyzed':
                self.AXs[key].set_xlabel("time (ms)")
                #self.AXs[key].annotate("current (A)", (-0.12, 0.4), xycoords='axes fraction', rotation=90)

                diffs = datafile.get_diffs3() #noise was removed here
                #print(diffs[datafile.infos["Infusion start"][i]*6:datafile.infos["Infusion end"][i]*6])
                #print(diffs)
                #print(len(diffs))
                batches_m, batches_std = datafile.get_batches(diffs)

                 # Standardization by baseline mean (Baseline at 100%)
                #print(datafile.infos["Infusion start"])
                baseline_m = np.mean(batches_m[(datafile.infos["Infusion start"]-5):datafile.infos["Infusion start"]])  #to fix
                batches_m_norm = (batches_m / baseline_m) * 100  
                batches_std_norm = (batches_std / baseline_m) * 100  
                
                self.AXs[key].plot(batches_m_norm, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(batches_m_norm)), batches_m_norm, yerr=batches_std_norm, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                self.AXs[key].set_ylim( -10, 140)
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                try:
                    self.AXs[key].axvspan(datafile.infos["Infusion start"], datafile.infos["Infusion end"], color='lightgrey') #to fix
                except:
                    print("no infusion")
                self.AXs[key].axhline(100, color="grey", linestyle="--")

        
if __name__=='__main__':
    #datafile = DataFile('C:/Users/laura.gonzalez/DATA/RAW_DATA/nm14Jun2024c0/nm14Jun2024c0_000.pxp')
    #datafile = DataFile('C:/Users/laura.gonzalez/DATA/RAW_DATA/model_cell/nm24Jun2024c0_000.pxp')
    datafile = DataFile_washout('D:/Internship_Rebola_ICM/EXP-recordings/RAW-DATA-TO-ANALYSE-WASHOUT/nm04Jul2024c1/nm04Jul2024c1_000.pxp')
    page = PdfPage()
    page.fill_PDF(datafile)
    plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/{datafile.filename}.pdf')
    plt.show()
