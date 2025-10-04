import netCDF4 as nc
from tqdm import tqdm
from ImageGenerator import ImageGenerator, ImageGeneratorMethod
from pathlib import Path
import color
import numpy as np

file_path = 'MERRA-2.nc4'
ds = nc.Dataset(file_path)

satellite = "MERRA-2"
analysed_stuff = "O3"
constant_value = "lev" # NEED TO CHANGE INDEXES :(
dependant_value = "time" # NEED T CHANGE GIF NAME
pseudomatrix = ds.variables[analysed_stuff]

max = pseudomatrix[:].max()
min = pseudomatrix[:].min()

a = np.array([0.5, 0.5, 0.5])
b = np.array([0.50, 0.50, 0.50])
c = np.array([1.0, 1.0, 1.0])
d = np.array([0.00, 0.33, 0.67])

pall = color.create_palette(a, b, c, d)

for ind_elev, elevation in tqdm(enumerate(ds.variables[constant_value][:])) :
    images = []
    for ind_time, time in enumerate(ds.variables[dependant_value][:]) :
        image_generator = ImageGenerator(method=ImageGeneratorMethod.LOGARITHMIC, color=pall)
        matrix = pseudomatrix[ind_time, ind_elev, :, :]
        image = image_generator.generateFromMatrix(matrix, max, min)
        images.append(image)
    Path(satellite + '/' + analysed_stuff).mkdir(parents=True, exist_ok=True)
    images[0].save(satellite +'/' + analysed_stuff + "/" + str(elevation) + '.gif', save_all=True, append_images=images[1:], loop=0)
