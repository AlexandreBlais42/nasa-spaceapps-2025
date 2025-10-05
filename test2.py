
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

ds = xr.open_dataset("MERRA-2.nc4")
keys = list(ds.keys())

for key in keys:
    data = ds[key].mean(dim=["time","lat","lon"])
    min_val = data.min().values
    max_val = data.max().values
    norm_data = (data - min_val) / (max_val - min_val)

    plt.plot(norm_data, label=key)

plt.title("Normalisation")
plt.ylabel("Valeur normal")
plt.legend()
plt.show(block = False)

plt.figure(figsize=(10,5))
for key in keys:
    data = ds[key].mean(dim=["time","lat","lon"])
    min_val = data.min().values
    max_val = data.max().values
    norm_data = (data - min_val) / (max_val - min_val)

    derivation = np.gradient(norm_data)
    plt.plot(derivation, label=key)

plt.title("Derivation")
plt.ylabel("valeur derive")
plt.legend()
plt.show()



