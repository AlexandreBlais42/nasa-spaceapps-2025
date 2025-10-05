import color
import numpy as np
from PIL import Image
from GIFGenerator import GIFGenerator

width = 256
height = 16
step = width/256
colorbar = [[i for _ in range(height)] for i in range(width)]

a = np.array([0.5, 0.5, 0.5])
b = np.array([0.50, 0.50, 0.50])
c = np.array([0.80, 0.80, 0.80])
d = np.array([0.28, 0.61, 0.85])

pall = color.create_palette(a,b,c,d)

image = Image.fromarray(np.array(colorbar,dtype=np.uint8).T)
image.putpalette(pall)
image.show()


GIFGenerator.changePalette("C:/Users/pouli/Documents/Nasa/nasa-spaceapps-2025/MERRA-2/O3",pall)