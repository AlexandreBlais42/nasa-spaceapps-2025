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

for ind_elev, elevation in tqdm(enumerate(ds.variables["lev"][:])) :
    images = []
    for ind_time, time in enumerate(ds.variables["time"][:]) :
        IG = image_generator = ImageGenerator()
        matrix = ds.variables["CO"][ind_time, ind_elev, :, :]
        image = image_generator.generateFromMatrix(matrix, matrix.shape)
        #image.save("test"+str(i)+".png")
        images.append(image)

    images[0].save("test" + str(elevation) + '.gif', save_all=True, append_images=images)

