import os
import matplotlib.pylab as plt
from trace_analysis_wash import DataFile_washout
import Curve_fit as cf
import numpy as np
from matplotlib.lines import Line2D


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
            DY = 0.20
            self.AXs['barplot'] = self.create_panel([X0, Y0, 0.6, DY])

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
                    self.AXs[key].axvspan(float(datafile.infos["Infusion start"]), float(datafile.infos["Infusion end"]), color='lightgrey')
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
                    self.AXs[key].axvspan(float(datafile.infos["Infusion start"]), float(datafile.infos["Infusion end"]), color='lightgrey')
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
                    self.AXs[key].axvspan(float(datafile.infos["Infusion start"]), float(datafile.infos["Infusion end"]), color='lightgrey') 
                except:
                    print("no infusion")

            elif key=='RespAnalyzed':
                batches_diffs_m, batches_diffs_std = datafile.batches_correct_diffs() #noise is substracted

                batches_diffs_m_norm, batches_diffs_std_norm =  datafile.normalize(batches_diffs_m, batches_diffs_std)
                #print("test if 100 : ",np.mean(batches_diffs_m_norm[0:10]))
                #print("test if 100 : ",np.mean(batches_diffs_m_norm[5:10]))

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
                    self.AXs[key].axvspan(float(datafile.infos["Infusion start"]), float(datafile.infos["Infusion end"]), color='lightgrey') 
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

    def fill_PDF_merge(self, diffs, num_files, group, Ids, leaks, barplot):
        
        colors = {'ketamine': 'purple', 'D-AP5': 'orange', 'control': 'grey', 'memantine': 'gold'}

        for key in self.AXs:
            if key =='Notes':
                txt = f"Group: {group}\nNumber of cells: {str(num_files)}"
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
            
            elif key=='Id (nA)':
                self.AXs[key].plot(Ids['mean'], marker="o", linewidth=0.5, markersize=2, color=colors[group])
                self.AXs[key].errorbar(range(len(Ids['mean'])), Ids['mean'], yerr=Ids['std'], linestyle='None', marker='_', color=colors[group], capsize=3, linewidth = 0.5)
                
                if len(Ids['mean'])> 50:
                    self.AXs[key].set_xlim(-1, len(Ids['mean']))
                    self.AXs[key].set_xticks(np.arange(0, len(Ids['mean'])+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50 )
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))

                
                self.AXs[key].set_ylabel("Id (=acces) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axvspan(10, 17, color='lightgrey')  #check this 

            elif key=='Leak (nA)':
                self.AXs[key].plot(leaks['mean'], marker="o", linewidth=0.5, markersize=2, color=colors[group])
                self.AXs[key].errorbar(range(len(leaks['mean'])), leaks['mean'], yerr=leaks['std'], linestyle='None', marker='_', color=colors[group], capsize=3, linewidth = 0.5)
                
                if len(leaks['mean'])> 50:
                    self.AXs[key].set_xlim(-1, len(leaks['mean']))
                    self.AXs[key].set_xticks(np.arange(0, len(leaks['mean'])+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                
                self.AXs[key].set_ylabel("Baseline (=leak) (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axvspan(10, 17, color='lightgrey')
            
            elif key=='Difference_peak_baseline':
                self.AXs[key].plot(diffs['mean'], marker="o", linewidth=0.5, markersize=2, color=colors[group])
                self.AXs[key].errorbar(range(len(diffs['mean'])), diffs['mean'], yerr=diffs['std'], linestyle='None', marker='_', color=colors[group], capsize=3, linewidth = 0.5)
                
                if len(diffs['mean'])> 50:
                    self.AXs[key].set_xlim(-1, len(diffs['mean']))
                    self.AXs[key].set_xticks(np.arange(0, len(diffs['mean'])+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                
                self.AXs[key].set_ylabel("Difference_peak_baseline (nA)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axvspan(10, 17, color='lightgrey')

            elif key=='RespAnalyzed':  # Normalization by baseline mean (Baseline at 100%)
                baseline_diffs_m = np.mean(diffs['mean'][5:10]) 
                batches_diffs_m_norm = (diffs['mean'] / baseline_diffs_m) * 100  
                batches_diffs_std_norm = (diffs['std'] / baseline_diffs_m) * 100  
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
                values = [barplot[key]['mean'] for key in keys]
                sem_values = [barplot[key]['sem'] for key in keys]
                self.AXs[key].bar(keys, values, color=colors[group], yerr=sem_values)
                self.AXs[key].set_xticklabels(keys, rotation=45, ha='right', fontsize=10)
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%)")

    def fill_final_results(self, final_dict, final_barplot, final_num_files, concentration, colors, GROUPS):
        
        for key in self.AXs:
            
            if key=='RespAnalyzed':  # Normalization by baseline mean (Baseline at 100%)  #why std negative?

                for group in GROUPS:
                    baseline_diffs_m = np.mean(final_dict[group]['mean'][5:10]) 
                    batches_diffs_m_norm = (final_dict[group]['mean'] / baseline_diffs_m) * 100  
                    batches_diffs_sem_norm = np.abs((final_dict[group]['sem'] / baseline_diffs_m) * 100 ) #batches_diffs_std_norm = np.abs((final_dict_std["ketamine"] / baseline_diffs_m) * 100 ) 
                    self.AXs[key].plot(batches_diffs_m_norm, marker="o", linewidth=0.5, markersize=2, label = f"{group} , {concentration[group]} , n= {final_num_files[group]}", color = colors[group])
                    self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=batches_diffs_sem_norm, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = colors[group])

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
                time_periods = list(final_barplot.keys())
                drug_types = list(final_barplot[time_periods[0]].keys())
                num_times = len(time_periods)
                num_drugs = len(drug_types)
                x = np.arange(num_drugs)  # label locations for each drug type
                width = 0.2  # width of each bar
                spacing = 0.05
                group_width = num_times * (width + spacing)
                time_positions = [i * group_width + j * (width + spacing) for i in range(num_drugs) for j in range(num_times)]
                time_labels = [time for _ in range(num_drugs) for time in time_periods]


                for i, time in enumerate(time_periods):
                    mean_values = [final_barplot[time][drug]['mean'] for drug in drug_types]
                    sem_values = [final_barplot[time][drug]['sem'] for drug in drug_types]

                    for j, drug in enumerate(drug_types):
                        self.AXs[key].bar(x[j] + i * width, mean_values[j], width, yerr=sem_values[j], 
                        color=colors[drug], label=time if j == 0 else "", capsize=5)

                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%)")
                self.AXs[key].set_xticks(time_positions)
                self.AXs[key].set_xticklabels(time_labels, rotation=45)
                legend_elements = [Line2D([0], [0], color=color, lw=4, label=drug) for drug, color in colors.items()]
                self.AXs[key].legend(handles=legend_elements, title="Drug Groups")

        return 0

if __name__=='__main__':
    base_path = os.path.join(os.path.expanduser('~'), 'DATA', 'Washout_experiment') 
    example = os.path.join(base_path, 'RAW-DATA-WASHOUT-PYR', 'nm17Jul2024c0', 'nm17Jul2024c0_000.pxp')
    datafile = DataFile_washout(example)
    print(datafile.filename)
    page = PdfPage()
    page.fill_PDF(datafile)
    plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/{datafile.filename}.pdf')
    plt.show()
