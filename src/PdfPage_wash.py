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
            Y0, DY = 0.05, 0.09
            self.AXs['Notes'] = self.create_panel([X0, Y0, DX, DY], 'Notes')
            self.AXs['Notes'].axis('off')

            Y0 += 0.11
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
            DY = 0.17
            self.AXs['barplot'] = self.create_panel([X0, Y0, 0.4, DY])

            Y0 += 0.01
            DY = 0.17
            X0 = 0.55
            DX = 0.40
            self.AXs['stats'] = self.create_panel([X0, Y0, DX, DY], 'Statistics')
            self.AXs['stats'].axis('off')

        elif PDF_sheet == 'group analysis':
            # build the axes one by one
            Y0, DY = 0.05, 0.05
            self.AXs['Notes'] = self.create_panel([X0, Y0, DX, DY], 'Notes')
            self.AXs['Notes'].axis('off')

            Y0 += 0.06
            DY = 0.06
            self.AXs['Id (nA)'] = self.create_panel([X0, Y0, DX, DY])

            Y0 += 0.12
            DY = 0.06
            self.AXs['Leak (nA)'] = self.create_panel([X0, Y0, DX, DY])

            Y0 += 0.12
            DY = 0.18
            self.AXs['Difference_peak_baseline'] = self.create_panel([X0, Y0, DX, DY], 'Response')

            Y0 += 0.24
            DY = 0.18
            self.AXs['RespAnalyzed'] = self.create_panel([X0, Y0, DX, DY])

            Y0 += 0.24
            DY = 0.13
            self.AXs['barplot'] = self.create_panel([X0, Y0, 0.4, DY])

            Y0 += 0.01
            DY = 0.17
            X0 = 0.55
            DX = 0.40
            self.AXs['stats'] = self.create_panel([X0, Y0, DX, DY], 'Statistics')
            self.AXs['stats'].axis('off')

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

            Y0 += 0.32
            DY = 0.17
            DX = 0.40
            self.AXs['stats1'] = self.create_panel([X0, Y0, DX, DY], 'Statistics')
            self.AXs['stats1'].axis('off')

            Y0 += 0.15
            DY = 0.17
            DX = 0.40
            self.AXs['stats2'] = self.create_panel([X0, Y0, DX, DY])
            self.AXs['stats2'].axis('off')

            Y0 = Y0 -0.15
            DY = 0.17
            X0 = 0.5
            DX = 0.40
            self.AXs['stats3'] = self.create_panel([X0, Y0, DX, DY])
            self.AXs['stats3'].axis('off')

            Y0 += 0.15
            DY = 0.17
            X0 = 0.5
            DX = 0.40
            self.AXs['stats4'] = self.create_panel([X0, Y0, DX, DY])
            self.AXs['stats4'].axis('off')

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

    def fill_PDF(self, datafile, GROUPS, wash= 'all', debug=False): 

        for key in self.AXs:
            print(self.AXs)
            
            if key=='Notes': ##includes metadata   
                if debug: 
                    print("Start ", key)   
                txt = ( f"ID file data: {datafile.filename}\n"
                        f"Number of sweeps: {len(datafile.recordings)}\n"
                        f"Euthanize method: {datafile.infos['Euthanize method']}\n"
                        f"Holding: {datafile.infos['Holding (mV)']}\n"
                        f"Infusion: {datafile.infos['Infusion substance']}\n"
                        f"Infusion concentration: {datafile.infos['Infusion concentration']}\n"
                        f"Infusion start: {datafile.infos['Infusion start']}\n"
                        f"Infusion end: {datafile.infos['Infusion end']}\n") 
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
                if debug: 
                    print("End ", key)   

            elif key=='Id (nA)':  #peak membrane test
                if debug: 
                    print("Start ", key)
                Ids = datafile.get_Ids()
                Ids_m, Ids_std = datafile.get_batches(Ids)
                x_vals = range(len(Ids_m))
                colors_for_points = ['firebrick' if y < 0.29 else GROUPS[datafile.infos['Group']]['color'] for y in Ids_m] 
                
                # Plot the main line connecting all points
                self.AXs[key].plot(x_vals, Ids_m, color=GROUPS[datafile.infos['Group']]['color'], linewidth=0.5)
                # Overlay individual points with their respective colors
                for xval, Ids_m_value, Ids_std_value, color in zip(x_vals, Ids_m, Ids_std, colors_for_points):
                    self.AXs[key].plot(xval, Ids_m_value, 
                                       marker="o", markersize=2, color=color)
                    self.AXs[key].errorbar(xval, Ids_m_value, yerr=Ids_std_value, 
                                           linestyle='None', marker='None', color=color, 
                                           capsize=3, linewidth = 0.5, capthick=0.5)   
                if len(Ids_m)> 50:
                    self.AXs[key].set_xlim(-1, len(Ids_m))
                    self.AXs[key].set_xticks(np.arange(0, len(Ids_m)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50 )
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                self.AXs[key].set_ylabel("Acces (nA) \n(± Std)")
                self.AXs[key].set_xlabel("time (min)")

                if any(id < 0.29 for id in Ids_m): 
                    self.AXs[key].axhline(0.29, color="firebrick", linestyle="-", linewidth=0.8)

                #self.AXs[key].axhline(0.29, color="firebrick", linestyle="-", linewidth=0.8) 
                try:
                    self.AXs[key].axvspan(float(datafile.infos["Infusion start"]), float(datafile.infos["Infusion end"]), color='lightgrey')
                except:
                    print("metadata not added correctly or no infusion")
                if debug: 
                    print("End ", key)

            elif key=='Leak (nA)':    #baseline 
                if debug:
                    print("Start ", key) 
     
                baselines = datafile.get_baselines()
                baselines_m, baselines_std = datafile.get_batches(baselines)
                
                x_vals = range(len(baselines_m))
                colors_for_points = ['firebrick' if y < -0.7 else GROUPS[datafile.infos['Group']]['color'] for y in baselines_m]

                # Plot the main line connecting all points
                self.AXs[key].plot(x_vals, baselines_m, 
                                   color=GROUPS[datafile.infos['Group']]['color'], linewidth=0.5)
                # Overlay individual points with their respective colors
                for xval, baselines_m_value, baselines_std_value, color in zip(x_vals, baselines_m, baselines_std, colors_for_points):
                    self.AXs[key].plot(xval, baselines_m_value, 
                                       marker="o", markersize=2, color=color)
                    self.AXs[key].errorbar(xval, baselines_m_value, yerr=baselines_std_value, 
                                           linestyle='None', marker='None', color=color, 
                                           capsize=3, linewidth = 0.5, capthick=0.5)
                   
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
                if debug: 
                    print("End ", key)
            
            elif key=='Difference_peak_baseline': #plot with noise    
                if debug: 
                    print("Start ", key)
                batches_m, batches_std = datafile.get_batches(datafile.diffs) #with noise
                #print("values for individual pdf", len(batches_m)) 
                self.AXs[key].plot(batches_m, 
                                   marker="o", linewidth=0.5, markersize=2, 
                                   color= GROUPS[datafile.infos['Group']]['color'], label='Response')
                self.AXs[key].errorbar(range(len(batches_m)), batches_m, yerr=batches_std, 
                                       linestyle='None', marker='None', color=GROUPS[datafile.infos['Group']]['color'], 
                                       capsize=3, linewidth = 0.5, capthick=0.5)
                
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
                self.AXs[key].errorbar(range(len(noises_m)), noises_m, yerr=noises_std, linestyle='None', marker='None', color='black', capsize=3, linewidth = 0.5, capthick=0.5)
                self.AXs[key].legend()
                try:
                    self.AXs[key].axvspan(float(datafile.infos["Infusion start"]), float(datafile.infos["Infusion end"]), color='lightgrey') 
                except:
                    print("no infusion")
                if debug: 
                    print("End ", key)

            elif key=='RespAnalyzed':
                if debug: 
                    print("Start ", key)
                batches_diffs_m, batches_diffs_std = datafile.get_batches(datafile.corr_diffs)
                if debug:
                    print("batches_diffs_m ", batches_diffs_m)
                    print("batches_diffs_std ", batches_diffs_std)
                batches_diffs_m_norm, batches_diffs_std_norm =  datafile.normalize(batches_diffs_m, batches_diffs_std)
                if debug:
                    print("batches_diffs_m_norm ", batches_diffs_m_norm)
                    print("batches_diffs_std_norm ", batches_diffs_std_norm)

                self.AXs[key].plot(batches_diffs_m_norm, marker="o", linewidth=0.5, markersize=2, color= GROUPS[datafile.infos['Group']]['color'])
                self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=np.abs(batches_diffs_std_norm), 
                                       linestyle='None', marker='None', color=GROUPS[datafile.infos['Group']]['color'], 
                                       capsize=3, linewidth = 0.5, capthick=0.5)
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
                if debug: 
                    print("End ", key)

            elif key=='barplot':  
                if debug: 
                    print("Start ", key)
                barplot = datafile.get_barplot(wash)
                keys = list(barplot.keys())
                means = [barplot[key]['mean'] for key in keys]
                sem_values = [barplot[key]['sem'] for key in keys]
                # Create the bar plot
                self.AXs[key].bar(keys, means, yerr=sem_values,
                                  color=GROUPS[datafile.infos['Group']]['color'], 
                                  capsize=10, alpha=0.8,
                                  linewidth = 0.7) 
                # Add scatter points for individual values
                for i, key_name in enumerate(keys):
                    if barplot[key_name]['values'] is not None:
                        scatter_x = np.full_like(barplot[key_name]['values'], fill_value=i, dtype=float)  # Align with bar index
                        scatter_x += (np.random.rand(len(scatter_x)) - 0.5) * 0.2  # Add small jitter for clarity
                        scatter_y = barplot[key_name]['values']
                        self.AXs[key].scatter(scatter_x, scatter_y, color='black', s=10, alpha=0.7)
                # Customize axes
                self.AXs[key].set_xticks(range(len(keys)))  # Align xticks with bar positions
                self.AXs[key].set_xticklabels(keys, rotation=0, ha='center', fontsize=10)
                self.AXs[key].set_ylabel("Normalized \nNMDAR-eEPSCs (%) (± SEM)")

                #ADD STATISTICS
                values_barplot = datafile.get_barplot()
                normality, homoscedasticity, parametric = datafile.test_parametric_conditions(values_barplot)
                F_stat1, p_val1 = datafile.calc_stats1(values_barplot, parametric)
                
                if np.isnan(p_val1):
                    print("no significance")
                    print("check case")
                    continue
                
                if p_val1 <0.05:  #let's see which group is different from which
                    print("At least one group is different from the others")
                    y_pos_m = 0
                    final_stats = datafile.calc_stats2(values_barplot, parametric)

                    for j1, time1 in enumerate(keys):
                        
                        for j2, time2 in enumerate(keys):
                            if j1 < j2:  # Avoid duplicate comparisons (i.e., comparing the same time to itself)
                                p_value = final_stats[j1, j2]
                                if np.isnan(p_value):
                                    significance = 'ns'
                                elif (p_value>0.05):
                                    significance = 'ns'  # Default is "not significant"
                                elif p_value < 0.001:
                                    significance = '***'
                                elif p_value < 0.01:
                                    significance = '**'
                                elif p_value < 0.05:
                                    significance = '*'
                                # Get the y positions for both bars being compared
                                y_pos1 = means[j1] + sem_values[j1]
                                y_pos2 = means[j2] + sem_values[j2]
                                y_pos = max(y_pos1, y_pos2) + 15 # Place the significance line above the highest bar
                                if y_pos==y_pos_m:
                                    y_pos +=12
                                y_pos_m=y_pos
                                # Calculate the position to place the significance line
                                x1 =  j1 
                                x2 =  j2 
                                # Draw a line between the bars
                                self.AXs[key].plot([x1, x2], [y_pos, y_pos], color='black', lw=0.8)
                                self.AXs[key].plot([x1, x1], [y_pos-3, y_pos], color='black', lw=0.8)
                                self.AXs[key].plot([x2, x2], [y_pos-3, y_pos], color='black', lw=0.8)
                                # Annotate the significance above the line
                                self.AXs[key].text((x1 + x2) / 2, y_pos + 0.03, f"{significance}", ha='center', va='bottom', fontsize=8)
                if debug: 
                    print("End ", key)

            elif key=='stats':
                if debug: 
                    print("Start ", key)   
                
                values_barplot = datafile.get_barplot()
                normality, homoscedasticity, parametric = datafile.test_parametric_conditions(values_barplot)
                F_stat1, p_val1 = datafile.calc_stats1(values_barplot, parametric)

                txt = ( f"\nNormality: {normality},  Homoscedasticity: {homoscedasticity}\n")
                if parametric: 
                    txt2 = (f"Parametric\n1wayANOVA\n")
                else: 
                    txt2 = (f"Non parametric\n\nKruskalwallis\n")
                txt3 = (f"F_val = {F_stat1:.3f}, p_val = {p_val1:.3f}\n\n") 
                
                if p_val1 < 0.05:
                    final_stats = datafile.calc_stats2(values_barplot, parametric)
                    if parametric: 
                        txt4 = (f"Tukey test\n")
                    else:
                        txt4 = (f"Dunn test holm adjust\n")
                    
                    txt5 = (f"Bsl vs Inf p= {final_stats[0,1]:.3f}\n"
                            f"Bsl vs Wash p= {final_stats[0,2]:.3f}\n"
                            f"Inf vs Wash p= {final_stats[1,2]:.3f}")
                            
                    self.AXs[key].annotate(txt + txt2 + txt3 + txt4 + txt5,(0, 1), va='top', xycoords='axes fraction')
                else: 
                    self.AXs[key].annotate(txt + txt2 + txt3,(0, 1), va='top', xycoords='axes fraction')

                if debug: 
                    print("End ", key)   

    def fill_PDF_merge(self, num_files, group, my_list, barplot, GROUPS, stats, debug):
        for key in self.AXs:
            if key =='Notes':
                txt = f"Group: {group}\nNumber of cells: {str(num_files)}"  #change for label and remove group 
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
            
            elif key=='Id (nA)':
                
                x_vals = range(len(my_list['Ids']['mean'][0]))
                y_vals = my_list['Ids']['mean'][0]
                y_vals_std = my_list['Ids']['std'][0]
                colors_for_points = ['firebrick' if y < 0.29 else GROUPS['color'] for y in y_vals]
                
                if debug:
                    print('Id (nA)')
                    print("Means : ", y_vals)
                    print("Stds : ", y_vals_std)

                self.AXs[key].plot(y_vals, marker="o", linewidth=0.5, markersize=2, color=GROUPS['color'])
                # Plot each point individually with the respective color
                for x, y, y_std, color in zip(x_vals, y_vals, y_vals_std,colors_for_points):
                    self.AXs[key].plot(x, y, marker="o", markersize=2, color=color, linewidth=0.5)
                    self.AXs[key].errorbar(x, y, yerr=y_std, 
                                           linestyle='None', marker='None', color=color, 
                                           capsize=3, linewidth=0.5, capthick=0.5)

                if len(y_vals) > 50:
                    self.AXs[key].set_xlim(-1, len(y_vals))
                    self.AXs[key].set_xticks(np.arange(0, len(y_vals) + 1, 5))
                else:
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))

                self.AXs[key].set_ylabel("Acces (nA) \n(± Std)")
                self.AXs[key].set_xlabel("time (min)")

                if (group=='memantine'):
                    self.AXs[key].axvspan(6, 13, color='lightgrey')  ###FIX
                elif (group=='ketamine'):
                    self.AXs[key].axvspan(10, 17, color='lightgrey')  ###FIX
                elif ((group=='D-AP5')):
                    self.AXs[key].axvspan(10, 17, color='lightgrey')  ###FIX
                self.AXs[key].axvline(50, color="grey", linestyle="-")

                if any(baseline < 0.29 for baseline in y_vals): 
                    self.AXs[key].axhline(0.29, color="firebrick", linestyle="-", linewidth=0.8)
               
            elif key=='Leak (nA)':
                x_vals = range(len(my_list['Leaks']['mean'][0]))
                y_vals = my_list['Leaks']['mean'][0]
                std_vals = my_list['Leaks']['std'][0]
                colors_for_points = ['firebrick' if y < -0.7 else GROUPS['color'] for y in y_vals]

                if debug:
                    print('Leak (nA)')
                    print("Means : ", y_vals)
                    print("Stds : ", std_vals)

                self.AXs[key].plot(y_vals, marker="o", linewidth=0.5, markersize=2, color=GROUPS['color'])
                for x, y, y_std, color in zip(x_vals, y_vals, std_vals, colors_for_points):
                    self.AXs[key].plot(x, y, marker="o", markersize=2, color=color, linewidth=0.5)
                    self.AXs[key].errorbar(x, y, yerr=y_std, 
                                           linestyle='None', marker='None', color=color, 
                                           capsize=3, linewidth=0.5, capthick=0.5)

                if len(y_vals)> 50:
                    self.AXs[key].set_xlim(-1, len(y_vals))
                    self.AXs[key].set_xticks(np.arange(0, len(y_vals)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                self.AXs[key].set_ylabel("Leak (nA) \n(± Std)")
                self.AXs[key].set_xlabel("time (min)")
                if (group=='memantine'):
                    self.AXs[key].axvspan(6, 13, color='lightgrey') ###FIX
                elif ((group=='ketamine')):
                    self.AXs[key].axvspan(10, 17, color='lightgrey') ###FIX
                elif ((group=='D-AP5')):
                    self.AXs[key].axvspan(10, 17, color='lightgrey') ###FIX
                self.AXs[key].axvline(50, color="grey", linestyle="-")
                if any(baseline < -0.7 for baseline in my_list['Leaks']['mean'][0]): 
                    self.AXs[key].axhline(-0.70, color="firebrick", linestyle="-", linewidth=0.8)
            
            elif key=='Difference_peak_baseline':
                x_vals = range(len(my_list['Diffs']['mean'][0]))
                y_vals = my_list['Diffs']['mean'][0]
                std_vals = my_list['Diffs']['std'][0]

                self.AXs[key].plot(y_vals, marker="o", linewidth=0.5, markersize=2, color=GROUPS['color'])
                self.AXs[key].errorbar(x_vals, y_vals, yerr=std_vals, 
                                       linestyle='None', marker='None', color=GROUPS['color'], 
                                       capsize=3, linewidth = 0.5, capthick=0.5)
                
                if len(y_vals)> 50:
                    self.AXs[key].set_xlim(-1, len(y_vals))
                    self.AXs[key].set_xticks(np.arange(0, len(y_vals)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))
                
                self.AXs[key].set_ylabel("Difference \nPeak-baseline (nA) (± Std)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axhline(0, color="grey", linestyle="--")

                if (group=='memantine'):
                    self.AXs[key].axvspan(6, 13, color='lightgrey') 
                elif ((group=='ketamine')):
                    self.AXs[key].axvspan(10, 17, color='lightgrey')
                elif ((group=='D-AP5')):
                    self.AXs[key].axvspan(10, 17, color='lightgrey')
                self.AXs[key].axvline(50, color="grey", linestyle="-")
                
            elif key=='RespAnalyzed':  # Normalization by baseline mean (Baseline at 100%)
                if (group=='memantine'):
                    baseline_diffs_m = np.mean(my_list['Diffs']['mean'][0][2:7]) 
                else:
                    baseline_diffs_m = np.mean(my_list['Diffs']['mean'][0][6:11])
                batches_diffs_m_norm = (my_list['Diffs']['mean'][0] / baseline_diffs_m) * 100  
                batches_diffs_std_norm = (my_list['Diffs']['std'][0] / baseline_diffs_m) * 100  
                

                self.AXs[key].plot(batches_diffs_m_norm, marker="o", linewidth=0.5, markersize=2, color=GROUPS['color'])
                self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=batches_diffs_std_norm, 
                                       linestyle='None', marker='None', color=GROUPS['color'], 
                                       capsize=3, linewidth = 0.5, capthick=0.5)
                if len(batches_diffs_m_norm)> 50:
                    self.AXs[key].set_xlim(-1, len(batches_diffs_m_norm))
                    self.AXs[key].set_xticks(np.arange(0, len(batches_diffs_m_norm)+1, 5))
                else : 
                    self.AXs[key].set_xlim(-1, 50)
                    self.AXs[key].set_xticks(np.arange(0, 51, 5))

                self.AXs[key].set_ylabel("Normalized \nNMDAR-eEPSCs (%) (± Std)")
                self.AXs[key].set_xlabel("time (min)")
                self.AXs[key].axhline(100, color="grey", linestyle="--")
                self.AXs[key].axhline(0, color="grey", linestyle="--")
                self.AXs[key].axvline(50, color="grey", linestyle="-")

                if (group=='memantine'):
                    self.AXs[key].axvspan(6, 13, color='lightgrey') 
                elif ((group=='ketamine')):
                    self.AXs[key].axvspan(10, 17, color='lightgrey')
                elif ((group=='D-AP5')):
                    self.AXs[key].axvspan(10, 17, color='lightgrey')
   
            elif key == 'barplot':
                
                # Extract data
                keys = list(barplot.keys())
                means = [np.nanmean(barplot[key]['mean']) for key in keys]
                sem_values = [barplot[key]['sem'] for key in keys]
                
                # Create the bar plot
                self.AXs[key].bar(keys, means, yerr=sem_values,
                                  color=GROUPS['color'],  capsize=10, 
                                  alpha=0.8, linewidth = 0.7)
                
                # Add scatter points for individual values
                for i, key_name in enumerate(keys):
                    if barplot[key_name]['mean'] is not None:
                        scatter_x = np.full_like(barplot[key_name]['mean'], fill_value=i, dtype=float)  # Align with bar index
                        scatter_x += (np.random.rand(len(scatter_x)) - 0.5) * 0.2  # Add small jitter for clarity
                        scatter_y = barplot[key_name]['mean']
                        self.AXs[key].scatter(scatter_x, scatter_y, color='black', s=10, alpha=0.7)
                
                # Customize axes
                self.AXs[key].set_xticks(range(len(keys)))  # Align xticks with bar positions
                self.AXs[key].set_xticklabels(keys, rotation=0, ha='center', fontsize=10)
                self.AXs[key].set_ylabel("Normalized \nNMDAR-eEPSCs (%) (± SEM)")
               
                #ADD STATISTICS
                if np.isnan(stats['final_stats'].any()):
                    break;
               
                if stats['p_val'] <0.05:  #let's see which group is different from which
                    print("final_stats : ")
                    print(stats['final_stats'])
                    #print("At least one group is different from the others")
                    significance = 'ns'
                    y_pos_m = 0
                    for j1, time1 in enumerate(keys):
                        for j2, time2 in enumerate(keys):
                            if j1 < j2:  # Avoid duplicate comparisons (i.e., comparing the same time to itself)
                                significance = 'ns'
                                p_value = stats['final_stats'][j1, j2]
                                if p_value < 0.001:
                                    significance = '***'
                                elif p_value < 0.01:
                                    significance = '**'
                                elif p_value < 0.05:
                                    significance = '*'
                                # Get the y positions for both bars being compared
                                y_pos1 = means[j1] + sem_values[j1]  #np.mean(means[j1]) + np.std(means[j1]) / np.sqrt(len(means[j1]))
                                y_pos2 = means[j2] + sem_values[j2]  #np.mean(means[j2]) + np.std(means[j2]) / np.sqrt(len(means[j2]))
                                y_pos = max(y_pos1, y_pos2) + 30 # Place the significance line above the highest bar
                                if y_pos==y_pos_m:
                                    y_pos +=20
                                y_pos_m=y_pos
                                # Calculate the position to place the significance line
                                x1 =  j1 
                                x2 =  j2 
                                
                                # Draw a line between the bars
                                self.AXs[key].plot([x1, x2], [y_pos, y_pos], color='black', lw=0.8)
                                self.AXs[key].plot([x1, x1], [y_pos-3, y_pos], color='black', lw=0.8)
                                self.AXs[key].plot([x2, x2], [y_pos-3, y_pos], color='black', lw=0.8)
                                    
                                # Annotate the significance above the line
                                self.AXs[key].text((x1 + x2) / 2, y_pos + 0.05, f"{significance}", ha='center', va='bottom', fontsize=8)

            elif key=='stats':
                if debug: 
                    print("Start ", key)   
                txt = ( f"\nNormality: {stats['Normality']},  Homoscedasticity: {stats['Homescedasticity']}\n")
                txt2 = (f"Parametric {stats['Parametric']}\n\n{stats['Test']}\n")
                txt3 = (f"F_val = {stats['F_stat']:.3f}, p_val = {stats['p_val']:.3f}\n\n") 

                if stats['p_val'] < 0.05:
                    if stats['Parametric']: 
                        txt4 = (f"Tukey test\n")
                    else:
                        txt4 = (f"Dunn test holm adjust\n")
                    
                    if (group == 'memantine'):
                        txt5 = (f"Bsl vs Inf p= {stats['final_stats'][0,1]:.3f}\n"
                                f"Bsl vs Wash p= {stats['final_stats'][0,2]:.3f}\n"
                                f"Bsl vs Wash_ p= {stats['final_stats'][0,3]:.3f}\n"
                                f"Inf vs Wash p= {stats['final_stats'][1,2]:.3f}\n"
                                f"Inf vs Wash_ p= {stats['final_stats'][1,3]:.3f}\n"
                                f"Wash vs Wash_ p= {stats['final_stats'][2,3]:.3f}\n")  
                    else:
                        txt5 = (f"Bsl vs Inf p= {stats['final_stats'][0,1]:.3f}\n"
                                f"Bsl vs Wash p= {stats['final_stats'][0,2]:.3f}\n"
                                f"Inf vs Wash p= {stats['final_stats'][1,2]:.3f}")
                            
                    self.AXs[key].annotate(txt + txt2 + txt3 + txt4 + txt5,(0, 1), 
                                           va='top', 
                                           xycoords = 'axes fraction', 
                                           fontsize = 9, 
                                           linespacing = 0.9)
                else: 
                    self.AXs[key].annotate(txt + txt2 + txt3,(0, 1), va='top', xycoords='axes fraction')
                
                if debug: 
                    print("End ", key)   

    def fill_final_results(self, final_dict, final_barplot, GROUPS, final_barplot2, stats, debug):
        
        for key in self.AXs:
            
            
            if key=='RespAnalyzed':  # Normalization by baseline mean (Baseline at 100%)  #why std negative?
                
                for group in GROUPS:
                    baseline_diffs_m = np.nanmean(final_dict[group]['mean'][6:11]) #memantine has nan for the first values
                    batches_diffs_m_norm   = (final_dict[group]['mean'] / baseline_diffs_m) * 100  
                    batches_diffs_std_norm = (final_dict[group]['std']  / baseline_diffs_m) * 100  
                    batches_diffs_sem_norm = (final_dict[group]['sem']  / baseline_diffs_m) * 100 
                    #print("values for graph ", batches_diffs_m_norm)
                    self.AXs[key].plot(batches_diffs_m_norm, marker="o", linewidth=0.5, markersize=2, label = f"{group} , {GROUPS[group]['concentration']} , n= {GROUPS[group]['num_files']}", color = GROUPS[group]['color'])
                    self.AXs[key].errorbar(range(len(batches_diffs_m_norm)), batches_diffs_m_norm, yerr=batches_diffs_sem_norm, 
                                           linestyle='None', marker='None', color = GROUPS[group]['color'],
                                           capsize=3, linewidth = 0.5, capthick=0.5)

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
                    for j, drug in enumerate(drug_types):
                        position = x[j] + i * (width + spacing)
                        self.AXs[key].bar(position, mean_values[j], yerr=sem_values[j],
                                          width=width, color=GROUPS[drug]['color'], label=time if j == 0 else "", 
                                          capsize=10, linewidth=0.7)
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
                
                #ADD STATISTICS
                stats_for_excel = []

                for i, drug in enumerate(drug_types):
                    y_pos_m = 0

                    stats_for_excel.append(stats)

                    for j1, time1 in enumerate(time_periods):
                        for j2, time2 in enumerate(time_periods):
                            if j1 < j2:  # Avoid duplicate comparisons (i.e., comparing the same time to itself)
                                significance = 'ns'
                                
                                if np.isnan(stats[drug]['final_stats'].all()):
                                    break
                                
                                else:
                                    
                                    p_value = stats[drug]['final_stats'][j1, j2]
                                    if (p_value>0.05):
                                        significance = 'ns'  # Default is "not significant"
                                    elif p_value < 0.001:
                                        significance = '***'
                                    elif p_value < 0.01:
                                        significance = '**'
                                    elif p_value < 0.05:
                                        significance = '*'
                                    # Get the y positions for both bars being compared
                                    y_pos1 = np.mean(final_barplot[time1][drug]['mean']) + np.std(final_barplot[time1][drug]['mean']) / np.sqrt(len(final_barplot[time1][drug]['mean']))
                                    y_pos2 = np.mean(final_barplot[time2][drug]['mean']) + np.std(final_barplot[time2][drug]['mean']) / np.sqrt(len(final_barplot[time2][drug]['mean']))
                                    y_pos = max(y_pos1, y_pos2) + 30 # Place the significance line above the highest bar
                                    if y_pos==y_pos_m:
                                        y_pos +=20
                                    y_pos_m=y_pos
                                
                                    # Calculate the position to place the significance line
                                    x1 = x[i] + j1 * (width + spacing)
                                    x2 = x[i] + j2 * (width + spacing)
                            
                                    # Draw a line between the bars
                                    self.AXs[key].plot([x1, x2], [y_pos, y_pos], color='black', lw=0.8)
                                    self.AXs[key].plot([x1, x1], [y_pos-3, y_pos], color='black', lw=0.8)
                                    self.AXs[key].plot([x2, x2], [y_pos-3, y_pos], color='black', lw=0.8)
                
                                    # Annotate the p-value above the line
                                    self.AXs[key].text((x1 + x2) / 2, y_pos + 0.05, f"{significance}", ha='center', va='bottom', fontsize=8)
                                
            elif key=='barplot2':
                barplot = final_barplot2
                print("final barplot 2 : ",barplot)
                keys = list(barplot.keys())
                means = [barplot[key]['mean'] for key in keys]
                sem_values = [barplot[key]['sem'] for key in keys]

                # Create the bar plot
                self.AXs[key].bar(keys, means, yerr=sem_values,
                                  color=GROUPS['memantine']['color'],  
                                  capsize=10, alpha=0.8, linewidth=0.7)

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

            elif key=='stats1':
                if debug: 
                    print("Start ", key)  
                

                txt = ( f"\nControl\nNormality: {stats['control']['Normality']},  Homoscedasticity: {stats['control']['Homescedasticity']}\n")
                if stats['control']['Parametric']: 
                    txt2 = (f"Parametric\n1wayANOVA\n")
                else: 
                    txt2 = (f"Non parametric\n\nKruskalwallis\n")
                txt3 = (f"F_val = {stats['control']['F_stat']:.3f}, p_val = {stats['control']['p_val']:.3f}\n\n") 
                

                if stats['control']['p_val'] < 0.05:
                    if stats['control']['Parametric']: 
                        txt4 = (f"Tukey test\n")
                    else:
                        txt4 = (f"Dunn test holm adjust\n")
                        
                    txt5 = (f"Bsl vs Inf p= {stats['control']['final_stats'][0,1]:.3f}\n"
                                f"Bsl vs Wash p= {stats['control']['final_stats'][0,2]:.3f}\n"
                                f"Inf vs Wash p= {stats['control']['final_stats'][1,2]:.3f}")
                               
                    self.AXs[key].annotate(txt + txt2 + txt3 + txt4 + txt5,(0, 1), va='top', xycoords='axes fraction')
                else: 
                    self.AXs[key].annotate(txt + txt2 + txt3,(0, 1), va='top', xycoords='axes fraction')
                
                if debug: 
                    print("End ", key)   

            elif key=='stats2':
                if debug: 
                    print("Start ", key)  

                txt = ( f"Ketamine\nNormality: {stats['ketamine']['Normality']}, Homoscedasticity: {stats['ketamine']['Homescedasticity']}\n")
                if stats['ketamine']['Parametric']: 
                    txt2 = (f"Parametric\n1wayANOVA\n")
                else: 
                    txt2 = (f"Non parametric\n\nKruskalwallis\n")
                txt3 = (f"F_val = {stats['ketamine']['F_stat']:.3f}, p_val = {stats['ketamine']['p_val']:.3f}\n\n") 
                    

                if stats['ketamine']['p_val'] < 0.05:
                    if stats['ketamine']['Parametric']: 
                        txt4 = (f"Tukey test\n")
                    else:
                        txt4 = (f"Dunn test holm adjust\n")
                        
                    txt5 = (f"Bsl vs Inf p= {stats['ketamine']['final_stats'][0,1]:.3f}\n"
                                f"Bsl vs Wash p= {stats['ketamine']['final_stats'][0,2]:.3f}\n"
                                f"Inf vs Wash p= {stats['ketamine']['final_stats'][1,2]:.3f}")
                                
                    self.AXs[key].annotate(txt + txt2 + txt3 + txt4 + txt5,(0, 1), va='top', xycoords='axes fraction')
                else: 
                    self.AXs[key].annotate(txt + txt2 + txt3,(0, 1), va='top', xycoords='axes fraction')

                if debug: 
                    print("End ", key) 

            elif key=='stats3':
                if debug: 
                    print("Start ", key)  

                

                txt = ( f"D-AP5\nNormality: {stats['D-AP5']['Normality']}, Homoscedasticity: {stats['D-AP5']['Homescedasticity']}\n")
                if stats['D-AP5']['Parametric']: 
                    txt2 = (f"Parametric\n1wayANOVA\n")
                else: 
                    txt2 = (f"Non parametric\n\nKruskalwallis\n")
                txt3 = (f"F_val = {stats['D-AP5']['F_stat']:.3f}, p_val = {stats['D-AP5']['p_val']:.3f}\n\n") 
                    

                if stats['D-AP5']['p_val'] < 0.05:
                    if stats['D-AP5']['Parametric']: 
                        txt4 = (f"Tukey test\n")
                    else:
                        txt4 = (f"Dunn test holm adjust\n")
                        
                    txt5 = (f"Bsl vs Inf p= {stats['D-AP5']['final_stats'][0,1]:.3f}\n"
                                f"Bsl vs Wash p= {stats['D-AP5']['final_stats'][0,2]:.3f}\n"
                                f"Inf vs Wash p= {stats['D-AP5']['final_stats'][1,2]:.3f}")
                                
                    self.AXs[key].annotate(txt + txt2 + txt3 + txt4 + txt5,(0, 1), va='top', xycoords='axes fraction')
                else: 
                    self.AXs[key].annotate(txt + txt2 + txt3,(0, 1), va='top', xycoords='axes fraction')

                if debug: 
                    print("End ", key) 

            elif key=='stats4':
                if debug: 
                    print("Start ", key)  
 
                txt = ( f"Memantine\nNormality: {stats['memantine']['Normality']}, Homoscedasticity: {stats['memantine']['Homescedasticity']}\n")
                if stats['memantine']['Parametric']: 
                    txt2 = (f"Parametric\n1wayANOVA\n")
                else: 
                    txt2 = (f"Non parametric\n\nKruskalwallis\n")
                txt3 = (f"F_val = {stats['memantine']['F_stat']:.3f}, p_val = {stats['memantine']['p_val']:.3f}\n\n") 
                    

                if stats['memantine']['p_val'] < 0.05:
                    if stats['memantine']['Parametric']: 
                        txt4 = (f"Tukey test\n")
                    else:
                        txt4 = (f"Dunn test holm adjust\n")
                        
                    txt5 = (f"Bsl vs Inf p= {stats['memantine']['final_stats'][0,1]:.3f}\n"
                                f"Bsl vs Wash p= {stats['memantine']['final_stats'][0,2]:.3f}\n"
                                f"Inf vs Wash p= {stats['memantine']['final_stats'][1,2]:.3f}")
                                
                    self.AXs[key].annotate(txt + txt2 + txt3 + txt4 + txt5,(0, 1), va='top', xycoords='axes fraction')
                else: 
                    self.AXs[key].annotate(txt + txt2 + txt3,(0, 1), va='top', xycoords='axes fraction')


                if debug: 
                    print("End ", key)    

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
