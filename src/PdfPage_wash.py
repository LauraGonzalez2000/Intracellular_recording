import os
import matplotlib.pylab as plt
from trace_analysis_wash import DataFile_washout
import Curve_fit as cf
import numpy as np


class PdfPage:

    def __init__(self, 
                 structure_dict={},
                 debug=False, final=False):
        
        # figure in A0 format
        if debug:
            self.fig = plt.figure(figsize=(8.41/1.3,11.90/1.3))
        else:
            self.fig = plt.figure(figsize=(8.41,11.90))

        # default start and width for axes
        X0, DX = 0.12, 0.85 # x coords

        # dictionary of axes
        self.AXs = {}

        if final==False:
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
            self.AXs['barplot'] = self.create_panel([X0, Y0, 0.4, DY])

        elif final==True:
            X0, DX, Y0, DY = 0.12, 0.85, 0.05, 0.18
            self.AXs['RespAnalyzed'] = self.create_panel([X0, Y0, DX, DY])

            Y0 += 0.32
            DY = 0.13
            self.AXs['barplot'] = self.create_panel([X0, Y0, 0.4, DY])

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

        colors = {'KETA': 'purple', 'APV': 'orange', 'control': 'grey', 'MEMANTINE': 'gold'}

        for key in self.AXs:
           
            if key=='Notes': ##includes metadata             
                txt = f"ID file data: {datafile.filename}\nNumber of recordings: {len(datafile.recordings)}\nID file excel: {datafile.infos['File']}\nEuthanize method: {datafile.infos['Euthanize method']}\nHolding:{datafile.infos['Holding (mV)']}\nInfusion:{datafile.infos['Infusion substance']}\nInfusion concentration:{datafile.infos['Infusion concentration']}\nInfusion start:{datafile.infos['Infusion start']}\nInfusion end:{datafile.infos['Infusion end']}\n"
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
              
            elif key=='Id (nA)':            
                Ids = datafile.get_Ids()
                Ids_m, Ids_std = datafile.get_batches(Ids)
                self.AXs[key].plot(Ids_m, marker="o", linewidth=0.5, markersize=2, color=colors[datafile.infos['Group']])
                self.AXs[key].errorbar(range(len(Ids_m)), Ids_m, yerr=Ids_std, linestyle='None', marker='_', color=colors[datafile.infos['Group']], capsize=3, linewidth = 0.5)
                
                if len(Ids_m)> 50:
                    self.AXs[key].set_xlim(-1, len(Ids_m))
                    self.AXs[key].set_xticks(np.arange(0, len(Ids_m)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50 )
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))

                self.AXs[key].set_ylabel("Id (=acces) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                
                try:
                    self.AXs[key].axvspan(int(datafile.infos["Infusion start"]), int(datafile.infos["Infusion end"]), color='lightgrey')
                except:
                    print("metadata not added correctly or no infusion")

            elif key=='Leak (nA)':      
                baselines = datafile.get_baselines()
                baselines_m, baselines_std = datafile.get_batches(baselines)
                self.AXs[key].plot(baselines_m, marker="o", linewidth=0.5, markersize=2, color= colors[datafile.infos['Group']])
                self.AXs[key].errorbar(range(len(baselines_m)), baselines_m, yerr=baselines_std, linestyle='None', marker='_', color=colors[datafile.infos['Group']], capsize=3, linewidth = 0.5)

                if len(baselines_m)> 50:
                    self.AXs[key].set_xlim(-1, len(baselines_m))
                    self.AXs[key].set_xticks(np.arange(0, len(baselines_m)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50 )
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))

                self.AXs[key].set_ylabel("Baseline (=leak) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                
                try:
                    self.AXs[key].axvspan(int(datafile.infos["Infusion start"]), int(datafile.infos["Infusion end"]), color='lightgrey')
                except Exception as e:
                    print(f"metadata not added correctly - or no infusion {e}")
            
            elif key=='Difference_peak_baseline': #plot with noise       
                batches_m, batches_std = datafile.get_batches(datafile.diffs) #with noise
                self.AXs[key].plot(batches_m, marker="o", linewidth=0.5, markersize=2, color= colors[datafile.infos['Group']], label='Response')
                self.AXs[key].errorbar(range(len(batches_m)), batches_m, yerr=batches_std, linestyle='None', marker='_', color=colors[datafile.infos['Group']], capsize=3, linewidth = 0.5)
                
                if len(batches_m)> 50:
                    self.AXs[key].set_xlim(-1, len(batches_m))
                    self.AXs[key].set_xticks(np.arange(0, len(batches_m)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50 )
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                
                
                self.AXs[key].set_ylabel("Difference_peak_baseline (nA)")
                self.AXs[key].set_xlabel("time (min)")
                
                #plot also noises
                noises = datafile.get_noises() 
                noises_m, noises_std = datafile.get_batches(noises) 
                self.AXs[key].plot(noises_m, marker="o", linewidth=0.5, markersize=2, label='noise', color='black')
                self.AXs[key].errorbar(range(len(noises_m)), noises_m, yerr=noises_std, linestyle='None', marker='_', color='black', capsize=3, linewidth = 0.5)
                self.AXs[key].legend()
                try:
                    self.AXs[key].axvspan(int(datafile.infos["Infusion start"]), int(datafile.infos["Infusion end"]), color='lightgrey') 
                except:
                    print("no infusion")

            elif key=='RespAnalyzed':
                batches_diffs_m, batches_diffs_std = datafile.batches_correct_diffs() #noise is substracted

                batches_diffs_m_norm, batches_diffs_std_norm =  datafile.normalize(batches_diffs_m, batches_diffs_std)
                print("test if 100 : ",np.mean(batches_diffs_m_norm[0:10]))
                print("test if 100 : ",np.mean(batches_diffs_m_norm[5:10]))

                self.AXs[key].plot(batches_diffs_m_norm, marker="o", linewidth=0.5, markersize=2, color= colors[datafile.infos['Group']])
                self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=np.abs(batches_diffs_std_norm), linestyle='None', marker='_', color=colors[datafile.infos['Group']], capsize=3, linewidth = 0.5)
                
                if len(batches_diffs_m_norm)> 50:
                    self.AXs[key].set_xlim(-1, len(batches_diffs_m_norm))
                    self.AXs[key].set_xticks(np.arange(0, len(batches_diffs_m_norm)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50 )
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%)")
                self.AXs[key].set_xlabel("time (min)")
                
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
                self.AXs[key].bar(categories, means, yerr=std_devs, width=0.4, capsize=5, color=colors[datafile.infos['Group']])

    def fill_PDF_merge(self, mean_diffs, std_diffs, num_files, group, mean_Ids, std_Ids, mean_leaks, std_leaks, barplot, temp_barplot_sem):
        
        colors = {'ketamine': 'purple', 'D-AP5': 'orange', 'control': 'grey', 'memantine': 'gold'}

        for key in self.AXs:
            if key =='Notes':
                txt = f"Group: {group}\nNumber of cells: {str(num_files)}"
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
            
            elif key=='Id (nA)':
                self.AXs[key].plot(mean_Ids, marker="o", linewidth=0.5, markersize=2, color=colors[group])
                self.AXs[key].errorbar(range(len(mean_Ids)), mean_Ids, yerr=std_Ids, linestyle='None', marker='_', color=colors[group], capsize=3, linewidth = 0.5)
                
                if len(mean_Ids)> 50:
                    self.AXs[key].set_xlim(-1, len(mean_Ids))
                    self.AXs[key].set_xticks(np.arange(0, len(mean_Ids)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50 )
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))

                
                self.AXs[key].set_ylabel("Id (=acces) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axvspan(10, 17, color='lightgrey')  #check this 

            elif key=='Leak (nA)':
                self.AXs[key].plot(mean_leaks, marker="o", linewidth=0.5, markersize=2, color=colors[group])
                self.AXs[key].errorbar(range(len(mean_leaks)), mean_leaks, yerr=std_leaks, linestyle='None', marker='_', color=colors[group], capsize=3, linewidth = 0.5)
                
                if len(mean_leaks)> 50:
                    self.AXs[key].set_xlim(-1, len(mean_leaks))
                    self.AXs[key].set_xticks(np.arange(0, len(mean_leaks)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                
                self.AXs[key].set_ylabel("Baseline (=leak) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axvspan(10, 17, color='lightgrey')
            
            elif key=='Difference_peak_baseline':
                self.AXs[key].plot(mean_diffs, marker="o", linewidth=0.5, markersize=2, color=colors[group])
                self.AXs[key].errorbar(range(len(mean_diffs)), mean_diffs, yerr=std_diffs, linestyle='None', marker='_', color=colors[group], capsize=3, linewidth = 0.5)
                
                if len(mean_diffs)> 50:
                    self.AXs[key].set_xlim(-1, len(mean_diffs))
                    self.AXs[key].set_xticks(np.arange(0, len(mean_diffs)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                
                self.AXs[key].set_ylabel("Difference_peak_baseline (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axvspan(10, 17, color='lightgrey')

            elif key=='RespAnalyzed':  # Normalization by baseline mean (Baseline at 100%)
                baseline_diffs_m = np.mean(mean_diffs[5:10]) 
                batches_diffs_m_norm = (mean_diffs / baseline_diffs_m) * 100  
                batches_diffs_std_norm = (std_diffs / baseline_diffs_m) * 100  
                self.AXs[key].plot(batches_diffs_m_norm, marker="o", linewidth=0.5, markersize=2, color=colors[group])
                self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=batches_diffs_std_norm, linestyle='None', marker='_', color=colors[group], capsize=3, linewidth = 0.5)
                if len(batches_diffs_m_norm)> 50:
                    self.AXs[key].set_xlim(-1, len(batches_diffs_m_norm))
                    self.AXs[key].set_xticks(np.arange(0, len(batches_diffs_m_norm)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))

                #self.AXs[key].set_ylim( -10, 170)
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axhline(100, color="grey", linestyle="--")
                self.AXs[key].axhline(0, color="grey", linestyle="--")
                self.AXs[key].axvspan(10, 17, color='lightgrey')
             
            elif key=='barplot':
                keys   = list(barplot.keys())
                values = list(barplot.values())
                yerr_  = np.std(values)/np.sqrt(len(values)) #dof=1 not 0  (or the opposite)
                self.AXs[key].bar(keys, values, color=colors[group])
                self.AXs[key].errorbar(range(len(keys)), values, yerr=yerr_, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = colors[group])
                self.AXs[key].set_xticklabels(list(barplot.keys()), rotation=45, ha='right', fontsize=10)
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%)")

    def fill_final_results(self, final_dict, final_dict_sem, final_barplot, final_num_files):
        for key in self.AXs:
            
            if key=='RespAnalyzed':  # Normalization by baseline mean (Baseline at 100%)  #why std negative?
                baseline_diffs_m = np.mean(final_dict["ketamine"][5:10]) 
                batches_diffs_m_norm = (final_dict["ketamine"] / baseline_diffs_m) * 100  
                #batches_diffs_std_norm = np.abs((final_dict_std["ketamine"] / baseline_diffs_m) * 100 ) 
                batches_diffs_sem_norm = np.abs((final_dict_sem["ketamine"] / baseline_diffs_m) * 100 ) 
                self.AXs[key].plot(batches_diffs_m_norm, marker="o", linewidth=0.5, markersize=2, label = f"ketamine 100uM n= {final_num_files[0]}", color = 'purple')
                self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=batches_diffs_sem_norm, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = 'purple')
                #self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=batches_diffs_std_norm, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = 'purple')
                    
                '''
                baseline_diffs_m1 = np.mean(final_dict["D-AP5"][5:10]) 
                batches_diffs_m_norm1 = (final_dict["D-AP5"] / baseline_diffs_m1) * 100  
                #batches_diffs_std_norm1 = np.abs((final_dict_std["D-AP5"] / baseline_diffs_m1) * 100  )
                batches_diffs_sem_norm1 = np.abs((final_dict_sem["D-AP5"] / baseline_diffs_m1) * 100 ) 
                self.AXs[key].plot(batches_diffs_m_norm1, marker="o", linewidth=0.5, markersize=2, label = f"D-AP5 50uM n= {final_num_files[1]}", color = 'orange')
                self.AXs[key].errorbar(range(len(batches_diffs_m_norm1)), batches_diffs_m_norm1, yerr=batches_diffs_sem_norm1, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = 'orange')
                #self.AXs[key].errorbar(range(len(batches_diffs_m_norm1)), batches_diffs_m_norm1, yerr=batches_diffs_std_norm1, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = 'orange')
                '''
                baseline_diffs_m2 = np.mean(final_dict["control"][5:10]) 
                batches_diffs_m_norm2 = (final_dict["control"] / baseline_diffs_m2) * 100  
                #batches_diffs_std_norm2 = np.abs((final_dict_std["control"] / baseline_diffs_m2) * 100 )
                batches_diffs_sem_norm2 = np.abs((final_dict_sem["control"] / baseline_diffs_m2) * 100 ) 
                self.AXs[key].plot(batches_diffs_m_norm2, marker="o", linewidth=0.5, markersize=2, label = f"control n= {final_num_files[2]}", color = 'grey')
                self.AXs[key].errorbar(range(len(batches_diffs_m_norm2)), batches_diffs_m_norm2, yerr=batches_diffs_sem_norm2, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = 'grey')
                #self.AXs[key].errorbar(range(len(batches_diffs_m_norm2)), batches_diffs_m_norm2, yerr=batches_diffs_std_norm2, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = 'grey')

                baseline_diffs_m3 = np.mean(final_dict["memantine"][5:10]) 
                batches_diffs_m_norm3 = (final_dict["memantine"] / baseline_diffs_m3) * 100  
                #batches_diffs_std_norm3 = np.abs((final_dict_std["memantine"] / baseline_diffs_m3) * 100 )
                batches_diffs_sem_norm3 = np.abs((final_dict_sem["memantine"] / baseline_diffs_m3) * 100 ) 
                self.AXs[key].plot(batches_diffs_m_norm3, marker="o", linewidth=0.5, markersize=2, label = f"memantine n= {final_num_files[2]}", color = 'gold')
                self.AXs[key].errorbar(range(len(batches_diffs_m_norm3)), batches_diffs_m_norm3, yerr=batches_diffs_sem_norm3, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = 'gold')
                #self.AXs[key].errorbar(range(len(batches_diffs_m_norm2)), batches_diffs_m_norm2, yerr=batches_diffs_std_norm2, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = 'grey')
                    
                self.AXs[key].set_xlim(-1, 50 )
                #self.AXs[key].set_ylim( -10, 170)
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].set_xticks(np.arange(0, 51, 5))
                self.AXs[key].axhline(100, color="grey", linestyle="--")
                self.AXs[key].axhline(0, color="grey", linestyle="--")
                self.AXs[key].axvspan(10, 17, color='lightgrey')
                #self.AXs[key].legend()

            elif key=='barplot':
                #colors = ['purple', 'purple', 'purple', 'orange', 'orange', 'orange', 'grey', 'grey', 'grey']
                colors = ['purple', 'purple', 'purple', 'grey', 'grey', 'grey', 'gold', 'gold', 'gold']

                bar_positions = [0, 1, 2, 3, 4, 5, 6, 7, 8]
                keys   = list(final_barplot.keys())
                values = list(final_barplot.values())
                yerr_  = np.std(values)/np.sqrt(len(values)) #dof=1 not 0  (or the opposite)
                self.AXs[key].bar(keys, values, color=colors)
                self.AXs[key].errorbar(range(len(keys)), values, yerr=yerr_, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = 'black')
                self.AXs[key].set_xticks(bar_positions)
                self.AXs[key].set_xticklabels(list(final_barplot.keys()), rotation=45, ha='right', fontsize=10)
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%)")
            
        return 0

if __name__=='__main__':
    datafile = DataFile_washout('D:/Internship_Rebola_ICM/EXP-recordings/RAW-DATA-TO-ANALYSE-WASHOUT/nm04Jul2024c1/nm04Jul2024c1_000.pxp')
    page = PdfPage()
    page.fill_PDF(datafile)
    plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/{datafile.filename}.pdf')
    plt.show()
