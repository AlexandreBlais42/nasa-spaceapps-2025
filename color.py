import numpy as np

def palette(t: float, a: np.array, b: np.array, c: np.array, d: np.array):
    return a + b * np.cos(6.283185 * (c * t + d))

a = np.array([0.48, 0.48, 0.48])
b = np.array([0.5, 0.5, 0.5])
c = np.array([1.0, 1.0, 1.0])
d = np.array([0.00, 0.33, 0.67])

def create_palette(a: np.array, b: np.array, c: np.array, d: np.array):
    step = 1/256
    pall = [0] * 256
    for t in range(0,256):
        pa = (palette((t*step),a,b,c,d) * 256).astype(np.uint8)
        pall[t] = pa

    def flatten(xss):
        return [x for xs in xss for x in xs]

    return flatten(pall)
