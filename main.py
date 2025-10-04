import netCDF4 as nc

file_path = 'MERRA-2.nc4'
ds = nc.Dataset(file_path)
#print(ds)
#print(ds.variables["AIRDENS"])
#print(ds.variables["CO"][0,0,:,:])
#print(ds.variables["DELP"])
#print(ds.variables["O3"])
#print(ds.variables["PS"])
matrix = ds.variables["CO"][0,0,:,:]

from ImageGenerator import ImageGenerator, ImageGeneratorMethod

# data[:,:,0,0]
IG = image_generator = ImageGenerator()
image = image_generator.generateFromMatrix(matrix, matrix.shape)
image.save("test.png")