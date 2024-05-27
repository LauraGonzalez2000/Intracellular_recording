import numpy as np
import matplotlib.pylab as plt

from PdfPage import PdfPage


def func(filename, 
         params1=0,
         params2=3,
         debug=False):

    
    page = PdfPage(debug=debug)

    
    print(page.AXs)

    for key in page.AXs:
        if key=='Notes':
            txt = 'ID'
            txt += ' + subject type'
            txt += ' \n '
            txt += 'some other annotation'
            page.AXs['Notes'].annotate(txt,
                                       (0, 1), va='top',
                                       xycoords='axes fraction')
            
        else:
            page.AXs[key].set_ylabel(key)
            page.AXs[key].plot(np.random.randn(100))

    page.save(filename.replace('hdf5', 'pdf'))


if __name__=='__main__':
         
    import os 
         
    filename = os.path.join(os.path.expanduser('~'), 'DATA', 'Dataset1', 'test.pdf')

    func(filename, debug=True)

    plt.show()

