from math import log
from enum import Enum
from typing import Tuple
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

    def generateFromMatrix(self, matrix, size: Tuple[int, int]) -> Image.Image:
        minimum_value = matrix[0][0]
        maximum_value = matrix[0][0]
        for row in matrix:
            for value in row:
                value = self.method.transform(value)
                minimum_value = min(minimum_value, value)
                maximum_value = max(maximum_value, value)

        image = Image.new("L", size)
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                value = self.method.transform(value)
                value = (value - minimum_value) / (maximum_value - minimum_value) * 255
                image.putpixel((i, j), int(value))

        return image


if __name__ == "__main__":
    image_generator = ImageGenerator(method=ImageGeneratorMethod.LOGARITHMIC)
    image = image_generator.generateFromMatrix([[1, 100], [10, 1]], (2, 2))
    image.save("/tmp/test.png")
