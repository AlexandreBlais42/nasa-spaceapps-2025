import netCDF4 as nc
from tqdm import tqdm
from ImageGenerator import ImageGenerator, ImageGeneratorMethod
from pathlib import Path

import numpy as np

def palette(  t:float,  a:np.array,  b:np.array,  c:np.array, d:np.array ):
    return a + b*np.cos( 6.283185*(c*t+d) );

a = np.array([0.5, 0.5, 0.5])
b = np.array([0.5, 0.5, 0.5])
c = np.array([1.0, 1.0, 1.0])
d = np.array([0.00, 0.33, 0.67])

step = 1/256
pall = [0] * 256
for t in range(0,256):
    pa = (palette((t*step),a,b,c,d) * 256).astype(np.uint8)
    pall[t] = pa

def flatten(xss):
    return [x for xs in xss for x in xs]

pall = flatten(pall)

file_path = 'MERRA-2.nc4'
ds = nc.Dataset(file_path)

satellite = "MERRA-2"
analysed_stuff = "O3"
constant_value = "lev" # NEED TO CHANGE INDEXES :(
dependant_value = "time" # NEED T CHANGE GIF NAME
pseudomatrix = ds.variables[analysed_stuff]

max = pseudomatrix[:].max()
min = pseudomatrix[:].min()
ind_elev = 41
elevation = ds.variables[constant_value][ind_elev]
images = []
for ind_time, time in enumerate(ds.variables[dependant_value][:]) :
    image_generator = ImageGenerator(method=ImageGeneratorMethod.LOGARITHMIC,color=pall)
    matrix = pseudomatrix[ind_time, ind_elev, :, :]
    image = image_generator.generateFromMatrix(matrix, max, min)
    #image.save("test"+str(i)+".png")
    images.append(image)
Path(satellite + '/' + analysed_stuff).mkdir(parents=True, exist_ok=True)
images[0].save(satellite +'/' + analysed_stuff + "/" + str(elevation) + '.gif', save_all=True, append_images=images, loop=0)

