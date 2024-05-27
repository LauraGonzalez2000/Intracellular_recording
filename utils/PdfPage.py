import matplotlib.pylab as plt

class PdfPage:

    def __init__(self):
        
        # figure in A0 format
        self.fig = plt.figure(figsize=(8.41,11.90))

        # default start and width for axes
        X0, DX = 0.1, 0.85 # x coords

        # dictionary of axes
        self.AXs = {}

        # build the axes one by one
        Y0, DY = 0.05, 0.1
        self.AXs['FullCmd'] = self.create_panel([X0, Y0, DX, DY])
        Y0 += DY+0.02
        DY = 0.15
        self.AXs['FullResp'] = self.create_panel([X0, Y0, DX, DY])
        Y0 += DY+0.02
        DY = 0.2
        self.AXs['MemTest'] = self.create_panel([X0, Y0, 0.35, DY])
        DY = 0.07
        self.AXs['I0'] = self.create_panel([0.5, Y0, 0.45, DY])
        Y0 += DY
        self.AXs['Rm'] = self.create_panel([0.5, Y0, 0.45, DY])
        Y0 += DY
        self.AXs['Rs'] = self.create_panel([0.5, Y0, 0.45, DY])
        Y0 += 0.1
        DY = 0.3
        self.AXs['RespAnalyzed'] = self.create_panel([X0, Y0, DX, DY])


    def create_panel(self, coords):
        """ 
        coords: (x0, y0, dx, dy)
                from left to right
                from top to bottom (unlike matplotlib)
        """
        coords[1] = 1-coords[1]-coords[3]
        ax = self.fig.add_axes(rect=coords)

        return ax

    def save(self, filename):
        """ 
        """
        self.fig.savefig(filename)

        

if __name__=='__main__':
    
    page = PdfPage()
    page.save('test.pdf')
    plt.show()

