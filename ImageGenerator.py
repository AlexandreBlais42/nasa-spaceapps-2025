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
                return np.log(value)

            case _:
                raise InvalidImageGeneratorMethodException


class ImageGenerator:
    def __init__(self, method=ImageGeneratorMethod.LINEAR,color=np.array):
        self.method = method
        self.color = color

    def generateFromMatrix(self, matrix: np.ndarray, minimum_value=None, maximum_value=None) -> Image.Image:
        if minimum_value is None or maximum_value is None:
            minimum_value = matrix.min()
            maximum_value = matrix.max()

        minimum_value = self.method.transform(minimum_value)
        maximum_value = self.method.transform(maximum_value)

        matrix = 1- ( 255 * self.method.transform(matrix) - minimum_value) / (maximum_value - minimum_value)
        image_temp = Image.fromarray(matrix.astype(np.uint8))
        p_img = Image.new('P',(1,1))
        p_img.putpalette(self.color)
        return image_temp.quantize(palette=p_img,dither=0)


if __name__ == "__main__":
    image_generator = ImageGenerator()
    image = image_generator.generateFromMatrix(np.array([[1, 100], [10, 1]]), (2, 2))
    image.save("/tmp/test.png")
