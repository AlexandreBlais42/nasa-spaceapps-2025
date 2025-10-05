import netCDF4 as nc
from tqdm import tqdm
from ImageGenerator import ImageGenerator, ImageGeneratorMethod
from pathlib import Path
import color
import numpy as np
import os

#file_path = 'MERRA2-DATA/MERRA2_100.tavgM_2d_chm_Nx.198001.nc4'
paths = []
directory = 'MERRA2-DATA'
for entry in os.scandir(directory):  
    if entry.is_file():  # check if it's a file
        paths.append(entry.path)
#print(paths)
#print(len(paths))

dss = []
for path in paths :
    dss.append(nc.Dataset(path))

satellite = "MERRA2_monthly_mean"
#print(dss[0])
print(dss[0].variables.keys())
#print(dss[0].variables["LWI"])

analysed_stuff = "LWI"
#constant_value = "lev" # NEED TO CHANGE INDEXES :(
dependant_value = "time" # NEED T CHANGE GIF NAME
max_list = [dss[v].variables[analysed_stuff][:].max() for v in range(len(dss))]
min_list = [dss[v].variables[analysed_stuff][:].min() for v in range(len(dss))]

max = max(max_list)
min = min(min_list)

a = np.array([0.5, 0.5, 0.5])
b = np.array([0.50, 0.50, 0.50])
c = np.array([1.0, 1.0, 1.0])
d = np.array([0.00, 0.33, 0.67])

pall = color.create_palette(a, b, c, d)

images = []

for i in range(len(dss)):
    pseudomatrix = dss[i].variables[analysed_stuff]
    image_generator = ImageGenerator(method=ImageGeneratorMethod.LOGARITHMIC, color=pall)
    matrix = pseudomatrix[0, :, :]
    image = image_generator.generateFromMatrix(matrix, max, min)
    images.append(image)
    Path(satellite + '/' + analysed_stuff).mkdir(parents=True, exist_ok=True)
    #str(1980+i//12) + str(f"{i%12:02d}")
images[0].save(satellite +'/' + analysed_stuff + "/" + analysed_stuff + '.gif', save_all=True, append_images=images[1:], loop=0)
