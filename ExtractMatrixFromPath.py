import netCDF4 as nc
from pathlib import Path
import os


def extractMatrix(satellite: str, folder: bool, path: Path, analysed_stuff: str):
    matrices = []
    paths = []
    if not folder:
        ds = nc.Dataset(path)
        return ds.variables[analysed_stuff][:]

    directory = satellite+"_DATA"
    for entry in os.scandir(directory):
        if entry.is_file():
            paths.append(entry.path)
    dss = []
    for path in paths:
        dss.append(nc.Dataset(path))
    liste = []
    for v in dss[0].variables.keys():
        if v.isupper():
            liste.append(v)
        assert(len(dss[v].variables[analysed_stuff][:].shape) == 2) # :(
        matrices.append(dss[v].variables[analysed_stuff][:])

    return matrices

print(extractMatrix("MERRA-2", False, Path("MERRA-2.nc4"), "CO"))
