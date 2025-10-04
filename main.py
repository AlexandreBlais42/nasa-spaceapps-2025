import netCDF4 as nc
from tqdm import tqdm

from ImageGenerator import ImageGenerator, ImageGeneratorMethod


file_path = 'MERRA-2.nc4'
ds = nc.Dataset(file_path)
#print(ds)
#print(ds.variables["AIRDENS"])
#print(ds.variables["CO"][0,0,:,:])
#print(ds.variables["DELP"])
#print(ds.variables["O3"])
#print(ds.variables["PS"])

images = []
for i, time in tqdm(enumerate(ds.variables["time"][:])) :
    image_generator = ImageGenerator()
    matrix = ds.variables["CO"][i,0,:,:]
    image = image_generator.generateFromMatrix(matrix, matrix.shape)
    images.append(image)

images[0].save('test.gif', save_all=True, append_images=images, loop=0)
