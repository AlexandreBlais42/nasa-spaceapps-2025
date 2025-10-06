import color
import numpy as np
from PIL import Image
from GIFGenerator import GIFGenerator


def colorbar(abcd,tmax=1):
    width = 256
    height = 20
    step = width/256
    colorbar = [[i*step for _ in range(height)] for i in range(width)]
    pall = color.create_palette(*abcd)

    image = Image.fromarray(np.array(colorbar,dtype=np.uint8).T)
    image.putpalette(pall)
    # image.show()
    return image


a = np.array([0.50, 0.50, 0.50])
b = np.array([0.50, 0.50, 0.50])
c = np.array([2.60, 1.30, 0.15])
d = np.array([0.50, 0.20, 0.25])
a = np.array([0.50, 0.50, 0.50])
b = np.array([0.50, 0.50, 0.50])
c = np.array([1.43, 1.40, 1.29])
d = np.array([0.63, 0.33, 0.77])
# pall2 = color.create_palette(a, b, c, d)

# GIFGenerator.changePalette("C:/Users/pouli/Documents/Nasa/nasa-spaceapps-2025/MERRA-2/AIRDENS",pall2)


# make_colorbar_image(a,b,c,d).show()
color.colorbar_me([a,b,c,d]).show()