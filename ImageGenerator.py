from enum import Enum
import numpy as np
from PIL import Image, ImageOps, ImageSequence
import math

class ImageGeneratorMethod(Enum):
    LINEAR = 0
    LOGARITHMIC = 1
    SUPERPOSITION = 2

    def transform(self, value):
        match self.value:
            case ImageGeneratorMethod.LINEAR.value:
                return value
            case ImageGeneratorMethod.LOGARITHMIC.value:
                return np.log(value)
            case ImageGeneratorMethod.SUPERPOSITION.value:
                return np.sqrt(value) * np.log(value)
            case _:
                raise InvalidImageGeneratorMethodException


class ImageGenerator:
    def __init__(self, method=ImageGeneratorMethod.LOGARITHMIC, color=np.array):
        self.method = method
        self.color = color

    def Sobel(self, matrix):
        sobel_matrix = np.empty(matrix.shape)
        linear_matrix = np.log10(matrix)
        pad_matrix = np.pad(linear_matrix,1,constant_values=0)

        height,width = matrix.shape

        gx = np.array([[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]])

        gy = np.array([[-1, -2, -1],
                    [ 0,  0,  0],
                    [ 1,  2,  1]])

        for i in range(0+1,height):
            for j in range(0+1,width):
                around = pad_matrix[i-1:i+2,j-1:j+2]

                x = np.sum(gx * around)
                y = np.sum(gy * around)

                sobel_matrix[i][j] = matrix[i][j] * np.sqrt(x*x+y*y)

        # sobel_matrix = np.sign(sobel_matrix) * np.power(10,sobel_matrix)

        minimum_value = sobel_matrix.min()
        maximum_value = sobel_matrix.max()

        matrix = (sobel_matrix - minimum_value) / (maximum_value - minimum_value)

        return sobel_matrix - minimum_value

    def changeColor(gif,newPalette):
        gif = Image.open(gif)
        frames = []
        for frame in ImageSequence.Iterator(gif):
            conv = frame.convert('RGB')

            p_img = Image.new('P',(1,1))
            p_img.putpalette(newPalette)
            frames.append(conv.quantize(palette=p_img,dither=0))

        return frames






    def generateFromMatrix(self, matrix: np.ndarray, minimum_value=None, maximum_value=None) -> Image.Image:
        if minimum_value is None or maximum_value is None:
            minimum_value = matrix.min()
            maximum_value = matrix.max()

        if(ImageGeneratorMethod != ImageGeneratorMethod.SUPERPOSITION):
            minimum_value = self.method.transform(minimum_value)
            maximum_value = self.method.transform(maximum_value)

            matrix = (1- (self.method.transform(matrix) - minimum_value) / (maximum_value - minimum_value))
        else :            
        
            self.method = ImageGeneratorMethod.LINEAR
            minimum_value = self.method.transform(minimum_value)
            maximum_value = self.method.transform(maximum_value)

            matrix1 = (1- (self.method.transform(matrix) - minimum_value) / (maximum_value - minimum_value))

            self.method = ImageGeneratorMethod.LOGARITHMIC
            minimum_value = self.method.transform(minimum_value)
            maximum_value = self.method.transform(maximum_value)

            matrix2 = (1- (self.method.transform(matrix) - minimum_value) / (maximum_value - minimum_value))

            matrix = matrix1 + matrix2
            minimum_value = matrix.min()
            maximum_value = matrix.max()
            matrix = (matrix - minimum_value) / (maximum_value - minimum_value)


        # matrix = self.Sobel(matrix)
        matrix *= 255
        image_temp = Image.fromarray(matrix.astype(np.uint8))
        p_img = Image.new('P', (1, 1))
        p_img.putpalette(self.color)
        return ImageOps.flip(image_temp.quantize(palette=p_img, dither=0))



if __name__ == "__main__":
    image_generator = ImageGenerator()
    image = image_generator.generateFromMatrix(np.array([[1, 100], [10, 1]]), (2, 2))
    image.save("/tmp/test.png")
