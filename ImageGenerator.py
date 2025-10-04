from math import log
from enum import Enum
from typing import Tuple
import numpy as np
from PIL import Image

class ImageGeneratorMethod(Enum):
    LINEAR = 0
    LOGARITHMIC = 1

    def transform(self, value):
        match self.value:
            case ImageGeneratorMethod.LINEAR.value:
                return value

            case ImageGeneratorMethod.LOGARITHMIC.value:
                return log(value)

            case _:
                raise InvalidImageGeneratorMethodException


class ImageGenerator:
    def __init__(self, method=ImageGeneratorMethod.LINEAR):
        self.method = method;

    def generateFromMatrix(self, matrix: np.ndarray, minimum_value=None, maximum_value=None) -> Image.Image:
        if minimum_value is None or maximum_value is None:
            minimum_value = matrix.min()
            maximum_value = matrix.max()

        minimum_value = self.method.transform(minimum_value)
        maximum_value = self.method.transform(maximum_value)

        matrix = (matrix - minimum_value) / (maximum_value - minimum_value) * 255
        return Image.fromarray(matrix.astype(np.uint8))


if __name__ == "__main__":
    image_generator = ImageGenerator()
    image = image_generator.generateFromMatrix(np.array([[1, 100], [10, 1]]), (2, 2))
    image.save("/tmp/test.png")
