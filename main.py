import netCDF4 as nc
from tqdm import tqdm
from ImageGenerator import ImageGenerator, ImageGeneratorMethod
from pathlib import Path
import color
import numpy as np
import os

file_path = 'antarctica_ice_velocity_450m_v2.nc'
#paths = []
#directory = 'MERRA2-DATA'
#for entry in os.scandir(directory):  
#    if entry.is_file():
#        paths.append(entry.path)

ds = nc.Dataset(file_path)

def palette(  t:float,  a:np.array,  b:np.array,  c:np.array, d:np.array ):
    return a + b*np.cos( 6.283185*(c*t+d) );

a = np.array([0.4, 0.4, 0.4])
b = np.array([0.6, 0.6, 0.6])
c = np.array([1.0, 1.0, 1.0])
d = np.array([0.00, 0.33, 0.67])

step = 1/256
pall = [0] * 256
for t in range(0, 256):
    pa = (palette((t*step), a, b, c, d) * 256).astype(np.uint8)
    pall[t] = pa

def flatten(xss):
    return [x for xs in xss for x in xs]

pall = flatten(pall)

print(ds)
print(ds.variables.keys())
#print(ds.variables["CNT"])
#print(ds.groups["PRODUCT"].variables["carbonmonoxide_total_column_corrected"].dimensions)

list = ["VX", "VY", "STDX", "STDY", "ERRX", "ERRY", "CNT"]

for analysed_stuff in list :
    matrix = ds.variables[analysed_stuff][:]
    max = matrix.max()
    min = matrix.min()
    image_generator = ImageGenerator(method=ImageGeneratorMethod.LOGARITHMIC, color=pall)
    image = image_generator.generateFromMatrix(matrix, max, min)
    image.save(analysed_stuff + ".png")