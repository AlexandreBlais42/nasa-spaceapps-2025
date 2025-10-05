import numpy as np
import netCDF4 as nc


class DataExtractor:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def getData(self):
        dataset = nc.Dataset(self.filepath)
        data = {}

        for key, value in dataset.variables.items():
            good_axises = ["time", "lev", "lon", "lat"]
            if key in good_axises:
                continue

            dimensions = value.dimensions
            good_dimensions = []
            for dim in dimensions:
                if dim in good_axises:
                    good_dimensions.append(dim)
                else:
                    good_dimensions.append(None)

            matrix = value[*map(lambda x: slice(None) if x is not None else 0, good_dimensions)]
            while len(matrix.shape) < len(good_axises):
                matrix = matrix[..., np.newaxis]

            good_dimensions = [i for i in good_dimensions if i is not None]
            matrix = np.moveaxis(matrix, range(len(good_dimensions)), [good_axises.index(i) for i in good_dimensions])

            data[key] = matrix

        return data


if __name__ == "__main__":
    data_extractor = DataExtractor("MERRA-2.nc4")
    data = data_extractor.getData()
