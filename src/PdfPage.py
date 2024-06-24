import os
import matplotlib.pylab as plt
from trace_analysis import DataFile
import numpy as np


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

    def fill_PDF(self, datafile, debug=False): 

        time = datafile.get_time()

        for key in self.AXs:
            if key=='Notes':
                txt = f"ID file: {datafile.file_path} \n Number of recordings: {len(datafile.response)} \n"
                self.AXs[key].annotate(txt,(0, 1), va='top', xycoords='axes fraction')
                print("Notes")

            elif key=='V_cmd0':
                self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("voltage (V)", (-0.12, -0.2), xycoords='axes fraction', rotation=90)
                self.AXs[key].plot(time, datafile.stim['Cmd1'])  
                print("V_cmd0")
            
            elif key=='V_cmd1':
                self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("voltage (V)", (-0.12, -0.8), xycoords='axes fraction', rotation=90)
                self.AXs[key].plot(time, datafile.stim['Cmd2'])  
                print("V_cmd1")

            elif key=='FullResp':
                self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("current (A)", (-0.12, 0.1), xycoords='axes fraction', rotation=90)
                stim1, _, stim2, _ = datafile.get_boundaries()
                artefact_cond = ((time>stim1) & (time<stim1+1)) | ((time>stim2) & (time<stim2+1)) 
                self.AXs[key].plot(time[~artefact_cond], datafile.avg_response[~artefact_cond]) 
                print("Full_resp")
                #plt.plot(time[~artefact_cond], datafile.avg_response[~artefact_cond]) 
                #plt.show()
                

            elif key=='MemTest':
                self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("current (A)", (-0.30, 0.4), xycoords='axes fraction', rotation=90)
                time_mem = time[9900:10600]
                resp_mem = datafile.avg_response[9900:10600]
                self.AXs[key].plot(time_mem, resp_mem, label = "Data")
                print("mem_test")
                
                my_range = (10007, 10600)
                my_func = datafile.model_biexponential1  
                
                x,y = datafile.get_fit(my_range, my_func, time, datafile.avg_response)
                '''
                self.AXs[key].plot(x,y, color="red", label = "fit")
                Id_avg, Ra_avg, Rm_avg, Cm_avg  = datafile.get_mem_values(datafile.avg_response, time)
                
                txt = (f"Id : {Id_avg*1e12:.1f} pA \n"
                       f"Rm : {Rm_avg/1e6:.1f} M$\\Omega$ \n"
                       f"Ra : {Ra_avg/1e6:.1f} MOhm \n"
                       f"Cm : {Cm_avg*1e12:.1f} pF \n")
                self.AXs[key].annotate(txt,(0.35, 0.5), va='top', xycoords='axes fraction')
                params_exp = datafile.get_params_function(model_biexponential1, 10007, 20000, datafile.avg_response, time)
                self.AXs[key].fill_between(time_mem,model_biexponential1(time_mem,params_exp[0],params_exp[1],params_exp[2],params_exp[3],params_exp[4] ), model_function_constant(time_mem, params_exp[4] ),where=((time_mem >= 100) & (time_mem <= 200)), alpha=0.3, color='skyblue')
                '''

            elif key=='Leak (pA)':
                txt = f"Leak \n (A)"
                self.AXs[key].annotate(txt, (-0.28, 0.2), xycoords='axes fraction', rotation=90)
                averages_baselines = datafile.get_baselines()
                self.AXs[key].plot(averages_baselines) 
                mean_leak = np.full((40,1), np.mean(averages_baselines))
                self.AXs[key].plot(np.linspace(0,40,40), mean_leak, color="lightblue")
                print("leak")

            elif key=='Rm (MOhm)':
                txt = 'Rm '
                txt+= '\n'
                txt += '(MOhm)'
                self.AXs[key].annotate(txt, (-0.28, 0.2), xycoords='axes fraction', rotation=90)
                Rm_list = datafile.get_mem_values_across_time(time)[1]
                self.AXs[key].plot(Rm_list)  
                mean_Rm_list = np.full((40,1), np.mean(Rm_list))
                self.AXs[key].plot(np.linspace(0,40,40), mean_Rm_list, color="lightblue")
                print("Rm")

            elif key=='Ra (MOhm)':
                txt = 'Ra '
                txt+= '\n'
                txt += '(MOhm)'
                self.AXs[key].annotate(txt, (-0.28, 0.2), xycoords='axes fraction', rotation=90)
                Ra_list = datafile.get_mem_values_across_time(time)[2]
                self.AXs[key].plot(Ra_list)  
                mean_Ra_list = np.full((40,1), np.mean(Ra_list))
                self.AXs[key].plot(np.linspace(0,40,40), mean_Ra_list, color="lightblue")
                print("Ra")
                
            elif key=='Cm (pF)':
                txt = 'Cm '
                txt+= '\n'
                txt += '(pF)'
                self.AXs[key].annotate(txt, (-0.28, 0.2), xycoords='axes fraction', rotation=90)
                self.AXs[key].set_xlabel("sweep")
                Cm_list = datafile.get_mem_values_across_time(time)[3]
                self.AXs[key].plot(Cm_list)  
                mean_Cm_list = np.full((40,1), np.mean(Cm_list))
                self.AXs[key].plot(np.linspace(0,40,40), mean_Cm_list, color="lightblue")
                print(np.mean(Cm_list))
                print("Cm")

            elif key=='RespAnalyzed':
                self.AXs[key].set_xlabel("time (ms)")
                self.AXs[key].annotate("current (A)", (-0.12, 0.4), xycoords='axes fraction', rotation=90)
                time_stim = time[55000:80000]
                resp_stim = datafile.avg_response[55000:80000]
                stim1, _, stim2, _ = datafile.get_boundaries()
                artefact_cond = ((time_stim>stim1) & (time_stim<stim1+1)) | ((time_stim>stim2) & (time_stim<stim2+1))
                self.AXs[key].plot(time_stim[~artefact_cond], resp_stim[~artefact_cond])  
                if datafile.get_resp_nature() : peak, amp_resp1, amp_resp2, PPR, rise_time, decay_time = datafile.analyse_neg_peak()
                else : peak, amp_resp1, amp_resp2, PPR, rise_time, decay_time = datafile.analyse_pos_peak()
                txt = (f"Peak1 : {amp_resp1*1e3:.2f} pA \n"
                       f"Peak2 : {amp_resp2*1e3:.2f} pA \n"
                       f"Rise time  : {rise_time:.2f} ms \n"
                       f"Decay time : {decay_time:.2f} ms \n")
                self.AXs[key].annotate(txt,(0.65, 0.3), va='top', xycoords='axes fraction')
                print("response")
        
    
if __name__=='__main__':

    datafile = DataFile('C:/Users/laura.gonzalez/DATA/RAW_DATA/nm12Jun2024c0/nm12Jun2024c0_000.pxp')
    page = PdfPage()
    page.fill_PDF(datafile)
    plt.show()

