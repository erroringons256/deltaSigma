import numpy as np

xRoot = np.array([0.5+0.8j])
xPoly = np.polynomial.Polynomial.fromroots(np.append(xRoot, np.conjugate(xRoot)))
yRoot = np.array([-0.2+0.5j])
yPoly = np.polynomial.Polynomial.fromroots(np.append(yRoot, np.conjugate(yRoot)))
maxLoci = np.array([], dtype="float64")

i = 0
increment = 1 / 1000
while i <= 1.0:
    maxLoci = np.append(maxLoci, np.amax(np.abs((xPoly + i * (yPoly - xPoly)).roots())))
    i += increment

print(np.amax(maxLoci))