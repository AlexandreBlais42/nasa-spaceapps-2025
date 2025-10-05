from threading import Thread
from typing import Set
from pathlib import Path
from time import sleep
import numpy as np
import color
import os

import netCDF4 as nc

from ImageGenerator import ImageGenerator, ImageGeneratorMethod

a = np.array([0.50, 0.50, 0.50])
b = np.array([0.50, 0.50, 0.50])
c = np.array([1.00, 1.00, 1.00])
d = np.array([0.00, 0.33, 0.67])
pall = color.create_palette(a, b, c, d)

class GIFGenerator:
    def __init__(self, filepath: str, variable: str, color=pall):
        self.filepath = filepath
        self.variable = variable
        self.color = color

    def setPreferedlevel(self, level: int):
        self.prefered_level = level

    def startGeneratingGifs(self):
        thread = Thread(target=self.generateGifs, args=(), )
        thread.start()

    def changePalette(dirpath, newPalette):
        for gif in os.listdir(dirpath):
            newGif = ImageGenerator.changeColor(dirpath+'/'+gif,newPalette)
            newGif[0].save(dirpath+'/'+gif,save_all=True, append_images=newGif[1:], loop=0)
            #perte de résolution

    def generateGifs(self):
        self.dataset = nc.Dataset(self.filepath)
        
        pall = color.create_palette(*color)

        #Verification of lev layers
        dimensions = self.dataset.variables[self.variable].dimensions
        self.haslevels = True
        if "lev" not in dimensions:
            self.levels = [1]
        if "lev" not in dimensions:
            self.levels = [1.0]
            self.haslevels = False
        else:
            self.levels = self.dataset.variables["lev"][:]
        self.levels_to_generate: Set[int] = set(range(len(self.levels)))
        self.prefered_level = 0
        self.times = self.dataset.variables["time"]

        self.data_matrix = self.dataset.variables[self.variable][:]

        self.data_maximum = self.data_matrix.max()
        self.data_minimum = self.data_matrix.min()
        self.image_generator = ImageGenerator(method=ImageGeneratorMethod.LOGARITHMIC, color=pall)
        self.satellite_name = Path(self.filepath).stem
        self.dirpath = f"{self.satellite_name}/{self.variable}/"

        while self.levels_to_generate:
            level_to_generate = self.prefered_level
            if self.prefered_level not in self.levels_to_generate:
                level_to_generate = list(self.levels_to_generate)[0]
            self.generateLevel(level_to_generate)

    def generateLevel(self, level_index: int):
        print(f"Generated level {level_index}")
        self.levels_to_generate.remove(level_index)
        images = []
        for i in range(len(self.times)):
            if self.haslevels:
                matrix = self.data_matrix[i, level_index, :, :]
            else:
                matrix = self.data_matrix[i, :, :]
            image = self.image_generator.generateFromMatrix(matrix, self.data_maximum, self.data_minimum)
            images.append(image)

        filename = f"{self.levels[level_index]}.gif"

        Path(self.dirpath).mkdir(parents=True, exist_ok=True)
        images[0].save(self.dirpath + filename, save_all=True, append_images=images[1:], loop=0)

if __name__ == "__main__":
    gif_generator = GIFGenerator("MERRA-2.nc4", "AIRDENS")
    gif_generator.startGeneratingGifs()
    sleep(10)
