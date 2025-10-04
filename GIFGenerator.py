from threading import Thread
from typing import Set
from pathlib import Path
from time import sleep

import netCDF4 as nc

from ImageGenerator import ImageGenerator, ImageGeneratorMethod


class GIFGenerator:
    def __init__(self, filepath: str, variable: str):
        self.filepath = filepath
        self.variable = variable

    def setPreferedElevation(self, elevation: int):
        self.prefered_elevation = elevation

    def startGeneratingGifs(self):
        thread = Thread(target=self.generateGifs, args=(),)
        thread.start()

    def generateGifs(self):
        self.dataset = nc.Dataset(self.filepath)
        self.variable = self.variable
        self.elevations = self.dataset.variables["lev"][:]
        self.elevations_to_generate: Set[int] = set(range(len(self.elevations)))
        self.prefered_elevation = 0
        self.times = self.dataset.variables["time"]

        self.data_matrix = self.dataset.variables[self.variable][:]
        self.data_maximum = self.data_matrix.max()
        self.data_minimum = self.data_matrix.min()
        self.image_generator = ImageGenerator(method=ImageGeneratorMethod.LOGARITHMIC)
        self.satellite_name = self.filepath.split(".")[0]
        self.dirpath = f"{self.satellite_name}/{self.variable}/"

        while self.elevations_to_generate:
            elevation_to_generate = self.prefered_elevation
            if self.prefered_elevation not in self.elevations_to_generate:
                elevation_to_generate = list(self.elevations_to_generate)[0]
            self.generateElevation(elevation_to_generate)

    def generateElevation(self, elevation_index: int):
        self.elevations_to_generate.remove(elevation_index)
        images = []
        for i in range(len(self.times)):
            matrix = self.data_matrix[i, elevation_index, :, :]
            image = self.image_generator.generateFromMatrix(matrix, self.data_maximum, self.data_minimum)
            images.append(image)

        filename = f"elevation-of-{self.elevations[elevation_index]}.gif"

        Path(self.dirpath).mkdir(parents=True, exist_ok=True)
        images[0].save(self.dirpath + filename, save_all=True, append_images=images, loop=0)

if __name__ == "__main__":
    gif_generator = GIFGenerator("MERRA-2.nc4", "O3")
    gif_generator.startGeneratingGifs();
    sleep(10)
