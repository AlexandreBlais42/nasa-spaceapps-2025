import netCDF4 as nc
from ImageGenerator import ImageGenerator, ImageGeneratorMethod
from pathlib import Path
import numpy as np
import os


def extractMatrix(satellite, folder, path, analysed_stuff) :
    """
    satellite : String
    folder : bool
    path : Path
    analysed_stuff : String
    """
    matrices = []
    paths = []
    if folder :
        directory = satellite+"_DATA"
        for entry in os.scandir(directory):
            if entry.is_file():
                paths.append(entry.path)
        dss = []
        for path in paths :
            dss.append(nc.Dataset(path))
        liste = []
        for v in dss[0].variables.keys() :
            if v.isupper() :
                liste.append(v)
        assert(len(dss[v].variables[analysed_stuff][:].shape) == 2) # :(
        for v in range(len(liste)) :
            matrices.append(dss[v].variables[analysed_stuff][:])
    else :
        ds = nc.Dataset(path)
        return ds.variables[analysed_stuff][:]
    return matrices

print(extractMatrix("MERRA-2", False, "MERRA-2.nc4", "CO"))