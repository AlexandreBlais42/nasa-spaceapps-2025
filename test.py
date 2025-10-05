import color
import numpy as np
from PIL import Image
from GIFGenerator import GIFGenerator



def colorbar(abcd):
    width = 256
    height = 16
    step = width/256
    colorbar = [[i for _ in range(height)] for i in range(width)]
    pall = color.create_palette(*abcd)

    image = Image.fromarray(np.array(colorbar,dtype=np.uint8).T)
    image.putpalette(pall)
    image.show()
    return image

a = np.array([0.50, 0.50, 0.50])
b = np.array([0.50, 0.50, 0.50])
c = np.array([2.00, 1.00, 0.00])
d = np.array([0.50, 0.20, 0.25])
pall2 = color.create_palette(a, b, c, d)

GIFGenerator.changePalette("C:/Users/pouli/Documents/Nasa/nasa-spaceapps-2025/MERRA-2/AIRDENS",pall2)