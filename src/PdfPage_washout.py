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

        Y0 += 0.14
        DY = 0.06
        self.AXs['Id (nA)'] = self.create_panel([X0, Y0, DX, DY])

        Y0 += 0.10
        DY = 0.06
        self.AXs['Leak (nA)'] = self.create_panel([X0, Y0, DX, DY])

        Y0 += 0.10
        DY = 0.18
        self.AXs['Difference_peak_baseline'] = self.create_panel([X0, Y0, DX, DY], 'Response')

        Y0 += 0.22
        DY = 0.18
        self.AXs['RespAnalyzed'] = self.create_panel([X0, Y0, DX, DY])

        Y0 += 0.22
        DY = 0.13
        self.AXs['barplot'] = self.create_panel([X0, Y0, 0.4, DY],'Statistics')

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


        for key in self.AXs:
           
            if key=='Notes': ##includes metadata             
                txt = f"ID file data: {datafile.filename}\nNumber of recordings: {len(datafile.recordings)}\nID file excel: {datafile.infos['File']}\nEuthanize method: {datafile.infos['Euthanize method']}\nHolding:{datafile.infos['Holding (mV)']}\nInfusion:{datafile.infos['Infusion substance']}\nInfusion concentration:{datafile.infos['Infusion concentration']}\nInfusion start:{datafile.infos['Infusion start']}\nInfusion end:{datafile.infos['Infusion end']}\n"
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
              
            elif key=='Id (nA)':            
                Ids = datafile.get_Ids()
                Ids_m, Ids_std = datafile.get_batches(Ids)
                self.AXs[key].plot(Ids_m, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(Ids_m)), Ids_m, yerr=Ids_std, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                self.AXs[key].set_ylabel("Id (=acces) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                try:
                    self.AXs[key].axvspan(int(datafile.infos["Infusion start"]), int(datafile.infos["Infusion end"]), color='lightgrey')
                except:
                    print("metadata not added correctly or no infusion")

            elif key=='Leak (nA)':      
                baselines = datafile.get_baselines()
                baselines_m, baselines_std = datafile.get_batches(baselines)
                self.AXs[key].plot(baselines_m, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(baselines_m)), baselines_m, yerr=baselines_std, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                self.AXs[key].set_ylabel("Baseline (=leak) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                try:
                    self.AXs[key].axvspan(int(datafile.infos["Infusion start"]), int(datafile.infos["Infusion end"]), color='lightgrey')
                except Exception as e:
                    print(f"metadata not added correctly - or no infusion {e}")
            
            elif key=='Difference_peak_baseline': #plot with noise       
                batches_m, batches_std = datafile.get_batches(datafile.diffs) #with noise
                self.AXs[key].plot(batches_m, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(batches_m)), batches_m, yerr=batches_std, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                self.AXs[key].set_ylabel("Difference_peak_baseline (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                #plot also noises
                noises = datafile.get_noises() 
                noises_m, noises_std = datafile.get_batches(noises) 
                self.AXs[key].plot(noises_m, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(noises_m)), noises_m, yerr=noises_std, linestyle='None', marker='_', color='red', capsize=3, linewidth = 0.5)
                try:
                    self.AXs[key].axvspan(int(datafile.infos["Infusion start"]), int(datafile.infos["Infusion end"]), color='lightgrey') 
                except:
                    print("no infusion")

            elif key=='RespAnalyzed':
                batches_diffs_m, batches_diffs_std = datafile.batches_correct_diffs() #noise is substracted
                batches_diffs_m_norm, batches_diffs_std_norm = datafile.normalize(batches_diffs_m, batches_diffs_std)
                self.AXs[key].plot(batches_diffs_m_norm, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=np.abs(batches_diffs_std_norm), linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                try:
                    self.AXs[key].axvspan(int(datafile.infos["Infusion start"]), int(datafile.infos["Infusion end"]), color='lightgrey') 
                except:
                    print("no infusion")
                self.AXs[key].axhline(100, color="grey", linestyle="--")
                self.AXs[key].axhline(0, color="grey", linestyle="--")

                '''
            elif key=='barplot':
                baseline_m, bsl_std, inf_m, inf_std, wash_m, wash_std = datafile.get_values_barplot()
                barplot = {'Baseline (5 last)':baseline_m, 'Infusion (5 last)':inf_m, 'Washout (5 last)':wash_m}
                self.AXs[key].bar(list(barplot.keys()), list(barplot.values()), width = 0.4)
                '''

            elif key=='barplot':
                values = datafile.get_values_barplot()
                #print(values)
                categories = ['Baseline (5 last)', 'Infusion (5 last)', 'Washout (5 last)']
                means = values[0::2]
                std_devs = values[1::2]
                #print(means)
                self.AXs[key].bar(categories, means, yerr=std_devs, width=0.4, capsize=5)

    def fill_PDF_merge(self, mean_diffs, std_diffs, num_files, group, mean_Ids, std_Ids, mean_leaks, std_leaks, barplot):

        for key in self.AXs:
            if key =='Notes':
                txt = f"Group: {group}\nNumber of files: {str(num_files)}"
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
            
            elif key=='Id (nA)':
                self.AXs[key].plot(mean_Ids, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(mean_Ids)), mean_Ids, yerr=std_Ids, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                self.AXs[key].set_ylabel("Id (=acces) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                try:
                    self.AXs[key].axvspan(int(datafile.infos["Infusion start"]), int(datafile.infos["Infusion end"]), color='lightgrey')
                except:
                    print("metadata not added correctly or no infusion")

            elif key=='Leak (nA)':
                self.AXs[key].plot(mean_leaks, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(mean_leaks)), mean_leaks, yerr=std_leaks, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                self.AXs[key].set_ylabel("Baseline (=leak) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                try:
                    self.AXs[key].axvspan(int(datafile.infos["Infusion start"]), int(datafile.infos["Infusion end"]), color='lightgrey')
                except Exception as e:
                    print(f"metadata not added correctly - or no infusion {e}")
            
            elif key=='Difference_peak_baseline':
                self.AXs[key].plot(mean_diffs, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(mean_diffs)), mean_diffs, yerr=std_diffs, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                self.AXs[key].set_ylabel("Difference_peak_baseline (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))

            elif key=='RespAnalyzed':  # Normalization by baseline mean (Baseline at 100%)
                print("len mean diffs ", len(mean_diffs))
                baseline_diffs_m = np.mean(mean_diffs[0:10]) 
                batches_diffs_m_norm = (mean_diffs / baseline_diffs_m) * 100  
                batches_diffs_std_norm = (std_diffs / baseline_diffs_m) * 100  
                self.AXs[key].plot(batches_diffs_m_norm, marker="o", linewidth=0.5, markersize=2)
                self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=batches_diffs_std_norm, linestyle='None', marker='_', color='blue', capsize=3, linewidth = 0.5)
                self.AXs[key].set_xlim(-1, 50 )
                #self.AXs[key].set_ylim( -10, 170)
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                self.AXs[key].axhline(100, color="grey", linestyle="--")

            elif key=='barplot':
                self.AXs[key].bar(list(barplot.keys()), list(barplot.values()), width = 0.4)
    
if __name__=='__main__':
    datafile = DataFile_washout('D:/Internship_Rebola_ICM/EXP-recordings/RAW-DATA-TO-ANALYSE-WASHOUT/nm04Jul2024c1/nm04Jul2024c1_000.pxp')
    page = PdfPage()
    page.fill_PDF(datafile)
    plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/{datafile.filename}.pdf')
    plt.show()
