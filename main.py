import netCDF4 as nc
from tqdm import tqdm
from ImageGenerator import ImageGenerator, ImageGeneratorMethod
from pathlib import Path
import color
import numpy as np
import os

#file_path = 'antarctica_ice_velocity_450m_v2.nc'

janick = False

satellite = "GEOSS"
paths = []
directory = 'GEOSS_DATA'
for entry in os.scandir(directory):
    if entry.is_file():
        paths.append(entry.path)

dss = []
for path in paths:
    dss.append(nc.Dataset(path))

def palette( t:float,  a:np.array,  b:np.array,  c:np.array, d:np.array ):
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

#print(ds)
#print(dss[0].variables.keys())
#print(ds.variables["CNT"])
#print(ds.groups["PRODUCT"].variables["carbonmonoxide_total_column_corrected"].dimensions)

list = []
for v in dss[0].variables.keys():
    if v.isupper():
        list.append(v)

for analysed_stuff in list:
    max_list = [dss[v].variables[analysed_stuff][:].max() for v in range(len(dss))]
    min_list = [dss[v].variables[analysed_stuff][:].min() for v in range(len(dss))]
    maximum = max(max_list)
    minimum = min(min_list)
    images = []
    for i in range(len(dss)):
        pseudomatrix = dss[i].variables[analysed_stuff]
        image_generator = ImageGenerator(method=ImageGeneratorMethod.LOGARITHMIC, color=pall)
        matrix = pseudomatrix[:]
        image = image_generator.generateFromMatrix(matrix, maximum, minimum)
        images.append(image)
        Path(satellite).mkdir(parents=True, exist_ok=True)
        if janick:
            Path(satellite + '/' + analysed_stuff).mkdir(parents=True, exist_ok=True)
            image.save(satellite + '/' + analysed_stuff + '/' + str(i) + ".png")
    if not janick:
        images[0].save(satellite +'/' + analysed_stuff + '.gif', save_all=True, append_images=images[1:], loop=0)
