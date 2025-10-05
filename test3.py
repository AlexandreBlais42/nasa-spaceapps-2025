import xarray as xr
import matplotlib.pyplot as plt
ds = xr.open_dataset("antartic.nc")
print(ds)
keys = list(ds.keys())
print(keys)

#data = ds["ndvi"].values[0,0]
#print(data)
#palette = ds["palette"].values

#rgb = palette[data] 
#print(rgb)
data = ds["STDX"]
print(ds["coord_system"])
#data2 = ds["STDY"]

plt.figure(figsize=(10,5))
data.plot(cmap="RdYlGn")
#data2.plot(cmap="RdYlGn")
plt.show()
