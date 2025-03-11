import matplotlib.pylab as plt
import Curve_fit as cf
import numpy as np
import pandas as pd
from scipy.stats import f_oneway, tukey_hsd, normaltest, kruskal, levene
import scikit_posthocs as sp
import openpyxl

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

        Y0 += 0.06
        DY = 0.03
        self.AXs['V_cmd0'] = self.create_panel([X0, Y0, DX, DY], 'V cmd 0')

        Y0 += 0.08
        DY = 0.03
        self.AXs['V_cmd1'] = self.create_panel([X0, Y0, DX, DY], 'V cmd 1')

        Y0 += 0.08
        DY = 0.08
        self.AXs['FullResp'] = self.create_panel([X0, Y0, DX, DY], 'Full Response')

        Y0 += 0.14
        DY = 0.24
        self.AXs['MemTest'] = self.create_panel([X0, Y0, 0.35, DY], 'Membrane Characteristics')

        DY = 0.06
        self.AXs['Leak (pA)'] = self.create_panel([0.60, Y0, 0.37, DY])

        Y0 += 0.06
        self.AXs['Rm (MOhm)'] = self.create_panel([0.60, Y0, 0.37, DY])

        Y0 += 0.06
        self.AXs['Ra (MOhm)'] = self.create_panel([0.60, Y0, 0.37, DY])

        Y0 += 0.06
        self.AXs['Cm (pF)'] = self.create_panel([0.60, Y0, 0.37, DY])

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

    def fill_PDF(self, datafile, debug=False, bis=False): 

        time = datafile.time

        for key in self.AXs:
            if key=='Notes':
                txt = f"ID file: {datafile.filename} \n Number of recordings: {len(datafile.response)} \n"
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
                
            elif key=='V_cmd0':
                self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("voltage (V)", (-0.12, -0.2), xycoords='axes fraction', rotation=90)
                self.AXs[key].plot(time, datafile.stim['Cmd1'])  
                
            elif key=='V_cmd1':
                self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("voltage (V)", (-0.12, -0.8), xycoords='axes fraction', rotation=90)
                self.AXs[key].plot(time, datafile.stim['Cmd2'])  
                
            elif key=='FullResp':
                self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("current (A)", (-0.12, 0.1), xycoords='axes fraction', rotation=90)
                stim1, _, stim2, _ = datafile.get_boundaries()
                artefact_cond = ((time>stim1) & (time<stim1+1)) | ((time>stim2) & (time<stim2+1)) 
                self.AXs[key].plot(time[~artefact_cond], datafile.avg_response[~artefact_cond]) 
                
            elif key=='MemTest':
                self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("current (A)", (-0.30, 0.4), xycoords='axes fraction', rotation=90)
                time_mem = time[9900:11000]
                resp_mem = datafile.avg_response[9900:11000]
                self.AXs[key].plot(time_mem, resp_mem, label = "Data")
                my_range = (10007, 11000)
                try :
                    my_func = cf.model_biexponential1  
                    x,y = cf.get_fit(my_range, my_func, time, datafile.avg_response)
                    self.AXs[key].plot(x,y, color="red", label = "fit")
                except: 
                    print("error with curve fitting with biexponential")
                    try : 
                        my_func = cf.model_exponential
                        x,y = cf.get_fit(my_range, my_func, time, datafile.avg_response)
                        self.AXs[key].plot(x,y, color="red", label = "fit")
                    except: 
                        print("error with curve fitting with exponential")
                
                Id_avg, Ra_avg, Rm_avg, Cm_avg  = datafile.get_mem_values(datafile.avg_response, time)
                txt = (f"Id : {Id_avg*1e12:.1f} pA \n Rm : {Rm_avg/1e6:.1f} M$\\Omega$ \n Ra : {Ra_avg/1e6:.1f} M$\\Omega$ \n Cm : {Cm_avg*1e12:.1f} pF \n")
                self.AXs[key].annotate(txt,(0.35, 0.5), va='top', xycoords='axes fraction')
                try: 
                    params_exp = cf.get_params_function(cf.model_biexponential1, 10007, 20000, datafile.avg_response, time)
                    self.AXs[key].fill_between(time_mem, cf.model_biexponential1(time_mem,params_exp[0],params_exp[1],params_exp[2],params_exp[3],params_exp[4]), cf.model_function_constant(time_mem, params_exp[4] ),where=((time_mem >= 100) & (time_mem <= 200)), alpha=0.3, color='skyblue')
                except: 
                    params_exp = cf.get_params_function(cf.model_exponential, 10007, 20000, datafile.avg_response, time)
                    #print(params_exp)
                    self.AXs[key].fill_between(time_mem,cf.model_exponential(time_mem,params_exp[0],params_exp[1],params_exp[2],params_exp[3]), cf.model_function_constant(time_mem, params_exp[3] ),where=((time_mem >= 100) & (time_mem <= 200)), alpha=0.3, color='skyblue')
                
            elif key=='Leak (pA)':
                txt = f"Leak \n(A)"
                self.AXs[key].annotate(txt, (-0.29, 0.2), xycoords='axes fraction', rotation=0)
                averages_baselines = datafile.get_baselines()
                mean_leak = [np.mean(averages_baselines)] * len(averages_baselines)
                self.AXs[key].plot(averages_baselines) 
                self.AXs[key].plot(mean_leak, color="lightblue")

            elif key=='Rm (MOhm)':
                txt = f'Rm \n(M$\\Omega$)'
                self.AXs[key].annotate(txt, (-0.29, 0.2), xycoords='axes fraction', rotation=0)
                Rm_list = datafile.get_mem_values_across_time(time)[2]
                mean_Rm_list = [np.mean(Rm_list)] * len(Rm_list)
                self.AXs[key].plot(Rm_list)  
                self.AXs[key].plot(mean_Rm_list, color="lightblue")

            elif key=='Ra (MOhm)':
                txt = 'Ra \n(M$\\Omega$)'
                self.AXs[key].annotate(txt, (-0.29, 0.2), xycoords='axes fraction', rotation=0)
                Ra_list = datafile.get_mem_values_across_time(time)[1]
                mean_Ra_list = [np.mean(Ra_list)] * len(Ra_list)
                self.AXs[key].plot(Ra_list)  
                self.AXs[key].plot(mean_Ra_list, color="lightblue")
                
            elif key=='Cm (pF)':
                txt = 'Cm \n(pF) '
                self.AXs[key].annotate(txt, (-0.29, 0.2), xycoords='axes fraction', rotation=0)
                self.AXs[key].set_xlabel("sweep")
                Cm_list = datafile.get_mem_values_across_time(time)[3]
                mean_Cm_list = [np.mean(Cm_list)] * len(Cm_list)
                self.AXs[key].plot(Cm_list)  
                self.AXs[key].plot(mean_Cm_list, color="lightblue")

            elif key=='RespAnalyzed':
                self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("current (A)", (-0.12, 0.4), xycoords='axes fraction', rotation=90)
                time_stim = time[55000:80000]
                resp_stim = datafile.smooth_avg_response[55000:80000]
                stim1, stim2 = 600, 700
                artefact_cond = ((time_stim>stim1-1) & (time_stim<stim1+1)) | ((time_stim>stim2-1) & (time_stim<stim2+1))
                self.AXs[key].plot(time_stim[~artefact_cond], resp_stim[~artefact_cond])  

                amp_resp1 = datafile.amp_resp1
                amp_resp2 = datafile.amp_resp2
                rise_time = datafile.rise_time
                decay_time = datafile.decay_time

                if bis==False:
                    txt = (f"Peak1 : {amp_resp1*1e3:.2f} pA \n"
                        f"Peak2 : {amp_resp2*1e3:.2f} pA \n"
                        f"Rise time  : {rise_time:.2f} ms \n"
                        f"Decay time : {decay_time:.2f} ms \n")
                if bis==True:
                    txt = (f"AMPA component : {amp_resp1*1e3:.2f} pA \n"
                        f"NMDA component : {amp_resp2*1e3:.2f} pA \n")
                       # f"Rise time  : {rise_time:.2f} ms \n"
                       # f"Decay time : {decay_time:.2f} ms \n")

                self.AXs[key].annotate(txt,(0.65, 0.3), va='top', xycoords='axes fraction')

    def fill_PDF_barplots(self, file_path, metrics, STATS=False):
        # Read the Excel file into a DataFrame
            
        IGOR_results_df = pd.read_excel(file_path, header=0)
        print(IGOR_results_df)
        
        # Group labels
        labels = ['xyla eutha', 'Ketaxyla' , 'keta xyla eutha']
        group_queries = ["Group=='xyla euthasol'", "Group=='ketaxyla'",  "Group=='keta xyla euthasol'"]
        colors = ['grey',  'orange',  'purple']
        
        # Number of plots based on the number of metrics
        num_metrics = len(metrics)
        
        # Set up the figure and subplots
        fig, axes = plt.subplots(3, 4, figsize=(14, 16))
        axes = axes.flatten()
        
        #plt.subplots(1, num_metrics, figsize=(10 * num_metrics, 6), sharey=False)
        
        # Ensure axes is always a list (in case there's only one metric)
        if num_metrics == 1:
            axes = [axes]
        
        stats_for_excel = []
        # Loop through each metric and plot
        for idx, metric in enumerate(metrics):
            means = []
            sems = []
            individual_data = []
            # Collect data for each group
            for query in group_queries:
                df_temp = IGOR_results_df.query(query)[metric]
                means.append(df_temp.mean())
                sems.append(df_temp.sem())
                individual_data.append(df_temp)
            
            # Bar plot with error bars
            bar_positions = np.arange(len(labels))
            axes[idx].bar(bar_positions, means, yerr=sems, color=colors, width=0.6, capsize=5, alpha=0.6, label='Mean ± SEM')
            
            # Plot individual data points
            for i, df in enumerate(individual_data):
                axes[idx].scatter(np.full(df.shape, bar_positions[i]), df, color='black', zorder=5)
            
            axes[idx].spines['top'].set_visible(False)
            axes[idx].spines['right'].set_visible(False)
            
            # Add title and labels to each subplot
            axes[idx].set_title(f'{metric}')
            axes[idx].set_xticks(bar_positions)
            axes[idx].set_xticklabels(labels)
            #axes[idx].set_ylabel('Amplitude (pA)')
            if (STATS==True) : 
                #ADD STATISTICS
                stats = self.calc_stats(metric, IGOR_results_df)
                print(stats)
                stats_for_excel.append(stats)

                y_pos_m = 0
                keys = ['xyla euthasol', 'ketaxyla', 'keta xyla euthasol'] 
                for j1, group1 in enumerate(keys):
                    for j2, group2 in enumerate(keys):
                        if j1 < j2:  # Avoid duplicate comparisons (i.e., comparing the same time to itself)
                            significance = 'ns'
                            p_value = stats['final_stats'][j1, j2]
                            if (np.isnan(p_value).all()):
                                significance = 'ns'  # Default is "not significant"
                            elif (p_value>0.05):
                                significance = 'ns'  # Default is "not significant"
                            elif (p_value < 0.001):
                                significance = '***'
                            elif (p_value < 0.01):
                                significance = '**'
                            elif (p_value < 0.05):
                                significance = '*'

                            if significance!='ns':
                                # Get the y positions for both bars being compared
                                y_pos1 = means[j1] + sems[j1]
                                y_pos2 = means[j2] + sems[j2]
                                y_pos = max(y_pos1, y_pos2) + 15 # Place the significance line above the highest bar
                                if y_pos==y_pos_m:
                                    y_pos +=12
                                y_pos_m=y_pos
                                # Calculate the position to place the significance line
                                x1 =  j1 
                                x2 =  j2 
                                # Draw a line between the bars
                                axes[idx].plot([x1, x2], [y_pos, y_pos], color='black', lw=0.8)
                                axes[idx].plot([x1, x1], [y_pos-3, y_pos], color='black', lw=0.8)
                                axes[idx].plot([x2, x2], [y_pos-3, y_pos], color='black', lw=0.8)
                                                
                                # Annotate the significance above the line
                                axes[idx].text((x1 + x2) / 2, y_pos + 0.03, f"{significance}", ha='center', va='bottom', fontsize=8)
                
                self.save_stats(stats_for_excel)
        # Delete any remaining unused subplots (if any)
        for idx in range(num_metrics, len(axes)):
            fig.delaxes(axes[idx])

        # Adjust layout to prevent overlap
        plt.tight_layout()
       
        return 0

    def test_parametric_conditions(self, values1, values2, values3):
        norm = True
        homes = True
        parametric=True
        #test conditions to apply statistical test:
            
        #test normality (The three groups are normally distributed): 
        stat1, p_val1 = normaltest(values1)
        stat2, p_val2 = normaltest(values2)
        stat3, p_val3 = normaltest(values3)
        if (np.isnan(p_val1)):
            norm=False
            print("issue with normality check")
        if (np.isnan(p_val2)):
            norm=False
            print("issue with normality check")
        if (np.isnan(p_val3)):
            norm=False
            print("issue with normality check")
        if (p_val1< 0.05):
            norm=False
            print("data is not normally distributed")
        if (p_val2< 0.05): 
            norm=False
            print("data is not normally distributed")
        if (p_val3< 0.05):
            norm=False
            print("data is not normally distributed")

            
        #test homoscedasticity (The three groups have a homogeneity of variance; meaning the population variances are equal):
        #The Levene test tests the null hypothesis that all input samples are from populations with equal variances.
        statistic, p_value = levene(values1, 
                                    values2, 
                                    values3)
        if (np.isnan(p_value)):
            norm=False
            print("issue with homoscedasticity check")
        if (p_value <0.05):
            #null hypothesis is rejected, the population variances are not equal!
            homes=False
            print("data does not have equal variances")

        if (norm==False): 
            parametric=False
            print("non parametric tests should be used")

        if (homes==False):
            parametric=False
            print("non parametric tests should be used")

        return norm, homes, parametric

    def calc_stats(self, metric, IGOR_results_df ):
        final_stats = np.array([[np.nan, np.nan, np.nan],
                                [np.nan, np.nan, np.nan],
                                [np.nan, np.nan, np.nan]])
        #statistic performed within a specific group:
        values_xe = IGOR_results_df.loc[IGOR_results_df['Group']=='xyla euthasol',  metric].values
        values_kx = IGOR_results_df.loc[IGOR_results_df['Group']=='ketaxyla',  metric].values
        values_kxe = IGOR_results_df.loc[IGOR_results_df['Group']=='keta xyla euthasol',  metric].values


        norm, homes, parametric = self.test_parametric_conditions(values_xe, values_kx, values_kxe)
        test2 = ""
        # One way ANOVA test
        # null hypothesis : all groups are statistically similar
        if parametric:
            print("Parametric test")
            test = 'ONE_WAY_ANOVA'
            F_stat, p_val = f_oneway(values_xe, 
                                     values_kx, 
                                     values_kxe )
            #print("F ", F_stat) 
            #print("p value", p_val)   
            if (p_val < 0.05): #we can reject the null hypothesis, therefore there exists differences between groups
                #In order to differenciate groups, Tukey post hoc test    #could be Dunnett -> compare with control?
                test2='Tukey test'
                Tukey_result = tukey_hsd(values_xe, 
                                         values_kx, 
                                         values_kxe )
                    
                #print("Tukey stats ", Tukey_result.statistic) 
                #print("Tukey pvalues", Tukey_result.pvalue)   
                final_stats = Tukey_result.pvalue

        # Non parametric test : Kruskal Wallis test
        # Tests the null hypothesis that the population median of all of the groups are equal.
        else: 
            print("Non parametric test")
            test = 'KRUSKAL_WALLIS'
            F_stat, p_val = kruskal(values_xe, 
                                    values_kx, 
                                    values_kxe)
            #print("F ", F_stat) 
            #print("p value", p_val) 
            #print("p_val KW : ", p_val)
            
            if (p_val < 0.05):
                test2='Dunn test, bonferroni adjust'
                #we can reject the null hypothesis, therefore there exists differences between groups
                #In order to differenciate groups, Dunn's post hoc test
                data = {"Value":list(values_xe)+
                                list(values_kx)+
                                list(values_kxe),
                        "Group":(["values_xe"] * len(list(values_xe)))+
                                (["values_kx"] * len(list(values_kx)))+
                                (["values_kxe"] * len(list(values_kxe)))}
                df = pd.DataFrame(data)
                p_values = sp.posthoc_dunn(df, val_col="Value", group_col="Group", p_adjust='bonferroni')
                p_values_array = p_values.to_numpy()
                '''
                p_values = sp.posthoc_dunn(values_xe, 
                                           values_kx, 
                                           values_kxe, 
                                           p_adjust='holm')
                '''
                final_stats = p_values_array

        #print("final stats : ")
        #print(final_stats)

        stats = {'Barplot':metric,
                 'Normality': norm,
                 'Homescedasticity': homes,
                 'Parametric': parametric,
                 'Test': test,
                 'F_stat': F_stat,
                 'p_val': p_val, 
                 'Supplementary test':test2,
                 'final_stats':final_stats}
            
        return stats
    
    def save_stats(self, data_list):
        try:
            data_for_excel = pd.DataFrame(data_list)
            path = 'C:/Users/sofia/Output_expe/In_Vitro/ratio/statistics_ratio.xlsx'
            with pd.ExcelWriter(path, engine='openpyxl') as writer: 
                data_for_excel.to_excel(writer, sheet_name='Data analysis', index=False)
                worksheet = writer.sheets['Data analysis']
                # Adjust column widths for data_for_excel
                for column in data_for_excel:
                    column_length = max(data_for_excel[column].astype(str).map(len).max(), len(column))
                    col_idx = data_for_excel.columns.get_loc(column)
                    worksheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx + 1)].width = column_length
            print("stats file saved successfully.")
        except Exception as e:
            print(f"ERROR when saving the stats file : {e}")
        return 0

if __name__=='__main__':
    from trace_analysis_ratio import DataFile
    datafile = DataFile('D:/Internship_Rebola_ICM/DATA_TO_ANALYSE/nm28May2024c1/nm28May2024c1_001.pxp')
    page = PdfPage()
    page.fill_PDF(datafile)
    plt.savefig(f'C:/Users/laura.gonzalez/DATA/PDFs/{datafile.filename}.pdf')
    plt.show()
