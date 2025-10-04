import netCDF4 as nc

file_path = 'carboneMonoxide.nc'
ds = nc.Dataset(file_path)
print(ds)
