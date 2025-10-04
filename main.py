import netCDF4 as nc

file_path = 'MERRA-2.nc4'
ds = nc.Dataset(file_path)
#print(ds)
#print(ds.variables["AIRDENS"])
#print(ds.variables["CO"][0,0,:,:])
#print(ds.variables["DELP"])
#print(ds.variables["O3"])
#print(ds.variables["PS"])


from ImageGenerator import ImageGenerator, ImageGeneratorMethod

print(ds.variables["time"][:])
#exit(0)

images = []
for i, time in enumerate(ds.variables["time"][:]) :
    IG = image_generator = ImageGenerator()
    matrix = ds.variables["CO"][i,0,:,:]
    image = image_generator.generateFromMatrix(matrix, matrix.shape)
    #image.save("test"+str(i)+".png")
    images.append(image)

images[0].save('test.gif', save_all=True, append_images=images)

# data[:,:,0,0]
