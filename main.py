import netCDF4 as nc

file_path = 'MERRA-2.nc4'
ds = nc.Dataset(file_path)
print(ds)
