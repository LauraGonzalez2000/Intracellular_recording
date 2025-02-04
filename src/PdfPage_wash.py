import os
import matplotlib.pylab as plt
from trace_analysis_wash import DataFile_washout
import Curve_fit as cf
import numpy as np
from matplotlib.lines import Line2D


class PdfPage:

    def __init__(self, PDF_sheet,
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

        if PDF_sheet == 'individual':
            # build the axes one by one
            Y0, DY = 0.05, 0.13
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

        elif PDF_sheet == 'group analysis':
            # build the axes one by one
            Y0, DY = 0.05, 0.07
            self.AXs['Notes'] = self.create_panel([X0, Y0, DX, DY], 'Notes')
            self.AXs['Notes'].axis('off')

            Y0 += 0.08
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


        elif PDF_sheet == 'final':
            X0, DX, Y0, DY = 0.12, 0.85, 0.05, 0.25
            self.AXs['RespAnalyzed'] = self.create_panel([X0, Y0, DX, DY], 'Response')

            Y0 += 0.32
            DY = 0.25
            self.AXs['barplot'] = self.create_panel([X0, Y0, 0.85, DY], 'Barplot')
            #self.AXs['barplot'] = self.create_panel([X0, Y0, 0.85, DY], 'Barplot 33 min wash')

            #Y0 += 0.32
            #DY = 0.25
            #self.AXs['barplot2'] = self.create_panel([X0, Y0, 0.50, DY], 'Barplot memantine 33 min vs 50 min wash')

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

    def fill_PDF(self, datafile, wash= 'all', debug=False): 

        colors = {'KETA': 'purple', 'APV': 'orange', 'control': 'grey', 'MEMANTINE': 'gold'}

        for key in self.AXs:
            
           
            if key=='Notes': ##includes metadata         
                txt = f"ID file data: {datafile.filename}\nNumber of sweeps: {len(datafile.recordings)}\nEuthanize method: {datafile.infos['Euthanize method']}\nHolding:{datafile.infos['Holding (mV)']}\nInfusion:{datafile.infos['Infusion substance']}\nInfusion concentration:{datafile.infos['Infusion concentration']}\nInfusion start:{datafile.infos['Infusion start']}\nInfusion end:{datafile.infos['Infusion end']}\n"
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
              
            elif key=='Id (nA)':  #peak membrane test
                Ids = datafile.get_Ids()
                Ids_m, Ids_std = datafile.get_batches(Ids)
                #print(Ids_m)
                #print(datafile.infos['Group'])
                self.AXs[key].plot(Ids_m, marker="o", linewidth=0.5, markersize=2, color=colors[datafile.infos['Group']])
                self.AXs[key].errorbar(range(len(Ids_m)), Ids_m, yerr=Ids_std, linestyle='None', marker='_', color=colors[datafile.infos['Group']], capsize=3, linewidth = 0.5)
                if len(Ids_m)> 50:
                    self.AXs[key].set_xlim(-1, len(Ids_m))
                    self.AXs[key].set_xticks(np.arange(0, len(Ids_m)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50 )
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))

                self.AXs[key].set_ylabel("Acces (nA) \n(± Std)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axhline(0.29, color="firebrick", linestyle="-", linewidth=0.8)
                
                try:
                    self.AXs[key].axvspan(float(datafile.infos["Infusion start"]), float(datafile.infos["Infusion end"]), color='lightgrey')
                except:
                    print("metadata not added correctly or no infusion")

            elif key=='Leak (nA)':    #baseline 
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

                self.AXs[key].set_ylabel("Leak (nA) \n(± Std)")
                self.AXs[key].set_xlabel("time (min)")

                if any(baseline < -0.7 for baseline in baselines_m): 
                    self.AXs[key].axhline(-0.70, color="firebrick", linestyle="-", linewidth=0.8)
                
                try:
                    self.AXs[key].axvspan(float(datafile.infos["Infusion start"]), float(datafile.infos["Infusion end"]), color='lightgrey')
                except Exception as e:
                    print(f"metadata not added correctly - or no infusion {e}")
            
            elif key=='Difference_peak_baseline': #plot with noise   
                batches_m, batches_std = datafile.get_batches(datafile.diffs) #with noise
                #print("values for individual pdf", len(batches_m)) 
                self.AXs[key].plot(batches_m, marker="o", linewidth=0.5, markersize=2, color= colors[datafile.infos['Group']], label='Response')
                self.AXs[key].errorbar(range(len(batches_m)), batches_m, yerr=batches_std, linestyle='None', marker='_', color=colors[datafile.infos['Group']], capsize=3, linewidth = 0.5)
                
                if len(batches_m)> 50:
                    self.AXs[key].set_xlim(-1, len(batches_m))
                    self.AXs[key].set_xticks(np.arange(0, len(batches_m)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50 )
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                
                
                self.AXs[key].set_ylabel("Difference \n peak-baseline (nA) (± Std)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axhline(0.02, color="firebrick", linestyle="-", linewidth=0.8)
                
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
                #batches_diffs_m, batches_diffs_std = datafile.batches_correct_diffs() #noise is substracted
                
                batches_diffs_m, batches_diffs_std = datafile.batches_corr_diffs, np.std(datafile.batches_corr_diffs)
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
                
                self.AXs[key].set_ylabel("Normalized \nNMDAR-eEPSCs (%) (± Std)")
                self.AXs[key].set_xlabel("time (min)")
                try:
                    self.AXs[key].axvspan(float(datafile.infos["Infusion start"]), float(datafile.infos["Infusion end"]), color='lightgrey') 
                except:
                    print("no infusion")
                self.AXs[key].axhline(100, color="grey", linestyle="--")
                self.AXs[key].axhline(0, color="grey", linestyle="--")

            elif key=='barplot':
                barplot = datafile.get_barplot(wash='all')
                keys = list(barplot.keys())
                means = [barplot[key]['mean'] for key in keys]
                sem_values = [barplot[key]['sem'] for key in keys]

                # Create the bar plot
                self.AXs[key].bar(
                    keys, means, color=colors[datafile.infos['Group']], yerr=sem_values, capsize=5, alpha=0.8
                )

                # Add scatter points for individual values
                for i, key_name in enumerate(keys):
                    if barplot[key_name]['values'] is not None:
                        scatter_x = np.full_like(barplot[key_name]['values'], fill_value=i, dtype=float)  # Align with bar index
                        scatter_x += (np.random.rand(len(scatter_x)) - 0.5) * 0.2  # Add small jitter for clarity
                        scatter_y = barplot[key_name]['values']
                        self.AXs[key].scatter(scatter_x, scatter_y, color='black', s=10, alpha=0.7)

                # Customize axes
                self.AXs[key].set_xticks(range(len(keys)))  # Align xticks with bar positions
                self.AXs[key].set_xticklabels(keys, rotation=45, ha='right', fontsize=10)
                self.AXs[key].set_ylabel("Normalized \nNMDAR-eEPSCs (%) (± SEM)")

    def fill_PDF_merge(self, num_files, group, my_list, barplot):

        
        colors = {'ketamine': 'purple', 'D-AP5': 'orange', 'control': 'grey', 'memantine': 'gold'}
        #colors = {'ketamine': 'purple', 'control': 'grey', 'memantine': 'gold'}

        for key in self.AXs:
            if key =='Notes':
                txt = f"Group: {group}\nNumber of cells: {str(num_files)}"
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
            
            elif key=='Id (nA)':
                self.AXs[key].plot(my_list['Ids']['mean'][0], marker="o", linewidth=0.5, markersize=2, color=colors[group])
    
                self.AXs[key].errorbar(range(len(my_list['Ids']['mean'][0])), my_list['Ids']['mean'][0], yerr=my_list['Ids']['std'][0], linestyle='None', marker='_', color=colors[group], capsize=3, linewidth = 0.5)
                
                if len(my_list['Ids']['mean'])> 50:
                    self.AXs[key].set_xlim(-1, len(my_list['Ids']['mean'][0]))
                    self.AXs[key].set_xticks(np.arange(0, len(my_list['Ids']['mean'][0])+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50 )
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))

                
                self.AXs[key].set_ylabel("Acces (nA) (± Std)")
                self.AXs[key].set_xlabel("time (min)")

                if group=='memantine':
                    self.AXs[key].axvspan(6, 13, color='lightgrey') 
                elif group=='ketamine' or group=='D-AP5':
                    self.AXs[key].axvspan(10, 17, color='lightgrey')
                self.AXs[key].axvline(50, color="grey", linestyle="-")

                self.AXs[key].axhline(0.29, color="firebrick", linestyle="-", linewidth=0.8)

            elif key=='Leak (nA)':
                self.AXs[key].plot(my_list['Leaks']['mean'][0], marker="o", linewidth=0.5, markersize=2, color=colors[group])
                self.AXs[key].errorbar(range(len(my_list['Leaks']['mean'][0])), my_list['Leaks']['mean'][0], yerr=my_list['Leaks']['std'][0], linestyle='None', marker='_', color=colors[group], capsize=3, linewidth = 0.5)

                if len(my_list['Leaks']['mean'][0])> 50:
                    self.AXs[key].set_xlim(-1, len(my_list['Leaks']['mean'][0]))
                    self.AXs[key].set_xticks(np.arange(0, len(my_list['Leaks']['mean'][0])+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                self.AXs[key].set_ylabel("Leak (nA) (± Std)")
                self.AXs[key].set_xlabel("time (min)")

                if group=='memantine':
                    self.AXs[key].axvspan(6, 13, color='lightgrey') 
                elif group=='ketamine' or group=='D-AP5':
                    self.AXs[key].axvspan(10, 17, color='lightgrey')

                #self.AXs[key].axvspan(10, 17, color='lightgrey')
                self.AXs[key].axvline(50, color="grey", linestyle="-")
                if any(baseline < -0.7 for baseline in my_list['Leaks']['mean'][0]): 
                    self.AXs[key].axhline(-0.70, color="firebrick", linestyle="-", linewidth=0.8)
            
            elif key=='Difference_peak_baseline':
                self.AXs[key].plot(my_list['Diffs']['mean'][0], marker="o", linewidth=0.5, markersize=2, color=colors[group])
                self.AXs[key].errorbar(range(len(my_list['Diffs']['mean'][0])), my_list['Diffs']['mean'][0], yerr=my_list['Diffs']['std'][0], linestyle='None', marker='_', color=colors[group], capsize=3, linewidth = 0.5)
                #print("len for merge plot ", len(my_list['Diffs']['mean']))
                if len(my_list['Diffs']['mean'][0])> 50:
                    self.AXs[key].set_xlim(-1, len(my_list['Diffs']['mean'][0]))
                    self.AXs[key].set_xticks(np.arange(0, len(my_list['Diffs']['mean'][0])+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                
                self.AXs[key].set_ylabel("Difference Peak-baseline (nA) (± Std)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axhline(0, color="grey", linestyle="--")

                if group=='memantine':
                    self.AXs[key].axvspan(6, 13, color='lightgrey') 
                elif group=='ketamine' or group=='D-AP5':
                    self.AXs[key].axvspan(10, 17, color='lightgrey')
                self.AXs[key].axvline(50, color="grey", linestyle="-")
                #self.AXs[key].axvspan(10, 17, color='lightgrey')

            elif key=='RespAnalyzed':  # Normalization by baseline mean (Baseline at 100%)
                if group=='memantine':
                    baseline_diffs_m = np.mean(my_list['Diffs']['mean'][0][2:7]) 
                else:
                    baseline_diffs_m = np.mean(my_list['Diffs']['mean'][0][6:11])
                batches_diffs_m_norm = (my_list['Diffs']['mean'][0] / baseline_diffs_m) * 100  
                batches_diffs_std_norm = (my_list['Diffs']['std'][0] / baseline_diffs_m) * 100  
                #print("values for merge", len(batches_diffs_m_norm ))
                self.AXs[key].plot(batches_diffs_m_norm, marker="o", linewidth=0.5, markersize=2, color=colors[group])
                self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=batches_diffs_std_norm, linestyle='None', marker='_', color=colors[group], capsize=3, linewidth = 0.5)
                if len(batches_diffs_m_norm)> 50:
                    self.AXs[key].set_xlim(-1, len(batches_diffs_m_norm))
                    self.AXs[key].set_xticks(np.arange(0, len(batches_diffs_m_norm)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))

                #self.AXs[key].set_ylim( -10, 170)
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%) (± Std)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axhline(100, color="grey", linestyle="--")
                self.AXs[key].axhline(0, color="grey", linestyle="--")
                self.AXs[key].axvline(50, color="grey", linestyle="-")

                if group=='memantine':
                    self.AXs[key].axvspan(6, 13, color='lightgrey') 
                elif group=='ketamine' or group=='D-AP5':
                    self.AXs[key].axvspan(10, 17, color='lightgrey')

                #self.AXs[key].axvspan(10, 17, color='lightgrey')

            elif key == 'barplot':
                # Extract data
                keys = list(barplot.keys())
                means = [np.mean(barplot[key]['mean']) for key in keys]
                sem_values = [barplot[key]['sem'] for key in keys]

                # Create the bar plot
                self.AXs[key].bar(
                    keys, means, color=colors[group], yerr=sem_values, capsize=5, alpha=0.8
                )

                # Add scatter points for individual values
                for i, key_name in enumerate(keys):
                    if barplot[key_name]['mean'] is not None:
                        scatter_x = np.full_like(barplot[key_name]['mean'], fill_value=i, dtype=float)  # Align with bar index
                        scatter_x += (np.random.rand(len(scatter_x)) - 0.5) * 0.2  # Add small jitter for clarity
                        scatter_y = barplot[key_name]['mean']
                        self.AXs[key].scatter(scatter_x, scatter_y, color='black', s=10, alpha=0.7)

                # Customize axes
                self.AXs[key].set_xticks(range(len(keys)))  # Align xticks with bar positions
                self.AXs[key].set_xticklabels(keys, rotation=45, ha='right', fontsize=10)
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%) (± SEM)")
            
    def fill_final_results(self, final_dict, final_barplot, final_num_files, concentration, colors, GROUPS, final_barplot2):
        
        for key in self.AXs:
            
            if key=='RespAnalyzed':  # Normalization by baseline mean (Baseline at 100%)  #why std negative?

                for group in GROUPS:
                    baseline_diffs_m = np.mean(final_dict[group]['mean'][6:11]) #memantine has nan for the first values
                    batches_diffs_m_norm   = (final_dict[group]['mean'] / baseline_diffs_m) * 100  
                    batches_diffs_std_norm = (final_dict[group]['std']  / baseline_diffs_m) * 100  
                    batches_diffs_sem_norm = (final_dict[group]['sem']  / baseline_diffs_m) * 100 
                    print("values for graph ", batches_diffs_m_norm)
                    self.AXs[key].plot(batches_diffs_m_norm, marker="o", linewidth=0.5, markersize=2, label = f"{group} , {concentration[group]} , n= {final_num_files[group]}", color = colors[group])
                    self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=batches_diffs_sem_norm, linestyle='None', marker='_', capsize=3, linewidth = 0.5, color = colors[group])

                #self.AXs[key].set_xlim(-1, 63 )
                self.AXs[key].set_xlim(-1, 50 )
                #self.AXs[key].set_ylim( -10, 170)
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%) (± SEM)")
                self.AXs[key].set_xlabel("time (min)")
                #self.AXs[key].set_xticks(np.arange(0, 63, 5))
                self.AXs[key].axhline(100, color="grey", linestyle="--")
                self.AXs[key].axhline(0, color="grey", linestyle="--")
                self.AXs[key].axvspan(10, 17, color='lightgrey')
                #self.AXs[key].axvline(50, color="grey", linestyle="-")
                #self.AXs[key].legend()
                '''
            elif key=='barplot':

                # Extract the data for plotting
                timings = list(final_barplot.keys())
                drugs = list(final_barplot[timings[0]].keys())
                num_times = len(timings)
                num_drugs = len(drugs)
                #drugs = ["control", "ketamine", "D-AP5"]
                #timings = ["End baseline", "End infusion", "End wash"]

                # Rearrange data: Group by timings, with drugs within each group
                timing_means = [[final_barplot[timing][drug]['mean'] for drug in drugs] for timing in timings]
                timing_sems = [[final_barplot[timing][drug]['sem'] for drug in drugs] for timing in timings]

                # Bar positions
                x = np.arange(len(drugs))
                width = 0.25

                # Plot bars for each timing
                
                for i, (timing_mean, timing_sem) in enumerate(zip(timing_means, timing_sems)):
                    self.AXs[key].bar(x + i * width, timing_mean, width, yerr=timing_sem, color=[colors[drug] for drug in drugs], capsize=5)

                # Formatting the plot
                #self.AXs[key].set_xlabel('Drugs', fontsize=12)
                self.AXs[key].set_ylabel('Normalized NMDAR-eEPSCs (%) (± SEM)', fontsize=12)
                self.AXs[key].set_xticks(x + width)
                self.AXs[key].set_xticklabels(drugs)
                #self.AXs[key].legend(title="Timings")
                '''
            
            elif key=='barplot': 

                time_periods = list(final_barplot.keys())
                drug_types = list(final_barplot[time_periods[0]].keys())
                x = np.arange(len(drug_types))  # location for each group
                width = 0.2  # width of each bar
                spacing = 0.05 #space between bars
                ticks = []

                # Iterate through time periods and drug types for bar plot
                for i, time in enumerate(time_periods):
                    mean_values = [np.mean(final_barplot[time][drug]['mean']) for drug in drug_types]
                    sem_values = [np.std(final_barplot[time][drug]['mean'])/np.sqrt(len(final_barplot[time][drug]['mean'])) for drug in drug_types]
                    #sem_values = [np.mean(final_barplot[time][drug]['sem']) for drug in drug_types]
                    print("mean values \n", mean_values)
                    print("sem values \n", sem_values)
                    for j, drug in enumerate(drug_types):
                        position = x[j] + i * (width + spacing)
                        self.AXs[key].bar(position, mean_values[j], width, yerr=sem_values[j], color=colors[drug], label=time if j == 0 else "", capsize=5)
                        ticks.append(position)

                        # Overlay scatter points for individual values
                        if final_barplot[time][drug]['mean'] is not None:
                            scatter_x = np.full_like(np.mean(final_barplot[time][drug]['values'], axis=1), fill_value=position, dtype=float)
                            scatter_x += (np.random.rand(len(scatter_x)) - 0.5) * width * 0.5  # Add small jitter
                            scatter_y = np.mean(final_barplot[time][drug]['values'], axis=1)
                            self.AXs[key].scatter(scatter_x, scatter_y, color='black', s=10, alpha=0.7)

                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%) (± SEM)")
                # Set ticks
                ticks.sort()
                
                if len(drug_types)==4:
                     labels_ticks = ['6-11', '15-19', '45-50', '6-11', '15-19', '45-50', '6-11', '15-19', '45-50','6-11', '15-19', '45-50' ]
                     labels_groupticks = ['\n\nControl', '\n\nKetamine', '\n\nD-APV', '\n\nMemantine']

                if len(drug_types)==3:
                     labels_ticks = ['6-11', '15-19', '45-50', '6-11', '15-19', '45-50', '6-11', '15-19', '45-50' ]
                     labels_groupticks = ['\n\nControl', '\n\nKetamine', '\n\nD-APV']

                self.AXs[key].set_xticks(ticks, labels = labels_ticks)
                group_ticks = [x_val + (width + spacing) for x_val in x]
                sec = self.AXs[key].secondary_xaxis(location=0)
                sec.set_xticks(group_ticks, labels=labels_groupticks) # Center xticks under groups
                sec.tick_params('x', length=0)
                
                #legend
                #legend_elements = [Line2D([0], [0], color=color, lw=4, label=drug) for drug, color in colors.items()]
                #self.AXs[key].legend(handles=legend_elements, title="Drug Groups")

            
            elif key=='barplot2':
                barplot = final_barplot2
                print("final barplot 2 : ",barplot)
                keys = list(barplot.keys())
                means = [barplot[key]['mean'] for key in keys]
                sem_values = [barplot[key]['sem'] for key in keys]

                # Create the bar plot
                self.AXs[key].bar(
                    keys, means, color=colors['memantine'], yerr=sem_values, capsize=5, alpha=0.8
                )

                # Add scatter points for individual values
                for i, key_name in enumerate(keys):
                    if barplot[key_name]['values'] is not None:
                        scatter_x = np.full_like(barplot[key_name]['values'], fill_value=i, dtype=float)  # Align with bar index
                        scatter_x += (np.random.rand(len(scatter_x)) - 0.5) * 0.2  # Add small jitter for clarity
                        scatter_y = barplot[key_name]['values']
                        self.AXs[key].scatter(scatter_x, scatter_y, color='black', s=10, alpha=0.7)

                # Customize axes
                self.AXs[key].set_xticks(range(len(keys)))  # Align xticks with bar positions
                self.AXs[key].set_xticklabels(keys, rotation=45, ha='right', fontsize=10)
                self.AXs[key].set_ylabel("Normalized NMDAR-eEPSCs (%)")
        return 0

if __name__=='__main__':
    base_path = os.path.join(os.path.expanduser('~'), 'DATA', 'Washout_experiment') 
    example = os.path.join(base_path, 'RAW-DATA-WASHOUT-PYR', 'nm17Jul2024c0', 'nm17Jul2024c0_000.pxp')
    datafile = DataFile_washout(example)
    print(datafile.filename)
    page = PdfPage(PDF_sheet='individual', debug=False)
    page.fill_PDF(datafile)
    #plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/{datafile.filename}.pdf')
    plt.show()
