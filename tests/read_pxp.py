import numpy as np
import matplotlib.pylab as plt
import os

from igor2.packed import load as loadpxp

data = loadpxp('C:/Users/laura.gonzalez/DATA/nm28May2024c0/nm28May2024c0_000.pxp')

files = os.listdir('C:/Users/laura.gonzalez/DATA')
for file in files:
    if 'nm' in file:
        print('- ', file)


data = loadpxp('C:/Users/laura.gonzalez/DATA/nm28May2024c0/nm28May2024c0_000.pxp')
print('hey', data, 'hey')
