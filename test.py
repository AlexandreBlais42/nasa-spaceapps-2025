import color
import numpy as np
from PIL import Image

width = 256
height = 16
step = width/256
colorbar = [[i for _ in range(height)] for i in range(width)]

a = np.array([0.5, 0.5, 0.5])
b = np.array([0.50, 0.50, 0.50])
c = np.array([0.88, 0.88, 0.88])
d = np.array([0.28, 0.61, 0.95])

pall = color.create_palette(a,b,c,d)

image = Image.fromarray(np.array(colorbar,dtype=np.uint8).T)
image.putpalette(pall)
image.show()


a = np.array([[1,2,3],
              [4,5,6]])

a = np.pad(a,1,constant_values=0)
print(a)