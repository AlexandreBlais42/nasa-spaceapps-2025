import netCDF4 as nc
from tqdm import tqdm
from ImageGenerator import ImageGenerator, ImageGeneratorMethod
from pathlib import Path

file_path = 'MERRA-2.nc4'
ds = nc.Dataset(file_path)

satellite = "MERRA-2"
analysed_stuff = "DELP"
constant_value = "lev" # NEED TO CHANGE INDEXES :(
dependant_value = "time" # NEED T CHANGE GIF NAME
pseudomatrix = ds.variables[analysed_stuff]

max = pseudomatrix[:].max()
min = pseudomatrix[:].min()

for ind_elev, elevation in tqdm(enumerate(ds.variables[constant_value][:])) :
    images = []
    for ind_time, time in enumerate(ds.variables[dependant_value][:]) :
        image_generator = ImageGenerator(method=ImageGeneratorMethod.LOGARITHMIC)
        matrix = pseudomatrix[ind_time, ind_elev, :, :]
        image = image_generator.generateFromMatrix(matrix, max, min)
        #image.save("test"+str(i)+".png")
        images.append(image)
    Path(satellite + '/' + analysed_stuff).mkdir(parents=True, exist_ok=True)
    images[0].save(satellite +'/' + analysed_stuff + "/" + str(elevation) + '.gif', save_all=True, append_images=images, loop=0)
