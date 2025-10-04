import netCDF4 as nc
from tqdm import tqdm

file_path = 'MERRA-2.nc4'
ds = nc.Dataset(file_path)
#print(ds)
#print(ds.variables["AIRDENS"])
#print(ds.variables["CO"][0,0,:,:])
#print(ds.variables["DELP"])
#print(ds.variables["O3"])
#print(ds.variables["PS"])


from ImageGenerator import ImageGenerator, ImageGeneratorMethod

#print(ds.variables["time"][:])
#print(ds.variables["lev"][:])

satellite = "MERRA-2"
analysed_stuff = "O3"
constant_value = "lev" # NEED TO CHANGE INDEXES :(
dependant_value = "time" # NEED T CHANGE GIF NAME
pseudomatrix = ds.variables[analysed_stuff]

max = pseudomatrix[:].max()
min = pseudomatrix[:].min()

for ind_elev, elevation in tqdm(enumerate(ds.variables[constant_value][:])) :
    images = []
    for ind_time, time in enumerate(ds.variables[dependant_value][:]) :
        IG = image_generator = ImageGenerator(method=ImageGeneratorMethod.LOGARITHMIC)
        matrix = pseudomatrix[ind_time, ind_elev, :, :]
        image = image_generator.generateFromMatrix(matrix, matrix.shape, max, min)
        #image.save("test"+str(i)+".png")
        images.append(image)
    images[0].save(satellite +'/' + analysed_stuff + "/elevation-of-" + str(elevation) + '.gif', save_all=True, append_images=images, loop=0)
