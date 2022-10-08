import numpy as np
import random

FFT_POINTS = 4096
INTEGRATION_COEFFICIENT = 1 / FFT_POINTS
NUM_FILTER_COEF = 128

np.set_printoptions(suppress = True, precision = 6)

# Misc. utility functions
target = lambda f: 1000 * (np.abs(f) < 0.25) + 0.001 * (np.abs(f) >= 0.25)
generateNeighbour = lambda x, step: x + step * (2 * (random.random() < 0.5) - 1)
sAbs = lambda z: z.real * z.real + z.imag * z.imag
def integrate(x):
    x = np.array(x)
    return INTEGRATION_COEFFICIENT * (np.sum(x) - 0.5 * (x[0] + x[-1]))
def residual(filterCoefficient):
    filterCoefficient = np.array(filterCoefficient)
    filterResponse = np.fft.rfft(filterCoefficient, n = FFT_POINTS)
    targetResponse = target(np.fft.rfftfreq(FFT_POINTS))
    residual = sAbs(filterResponse / targetResponse)
    pbStart = 0
    pbEnd = int(FFT_POINTS * 0.24) + 1
    pbResidual = residual[pbStart:pbEnd]
    pbdResidual = pbResidual[1:] - pbResidual[:-1]
    pbdResidual *= pbdResidual
    return 0.002 * integrate(residual) + 0.998 * integrate(pbdResidual)

random.seed()
filterCoefficient = np.append(1.0, np.repeat(0.0, 127))

count = 0
threshold = 1000
i = 0

filterResidual = residual(filterCoefficient)
bestFilterCoefficient = filterCoefficient.copy()
bestFilterResidual = filterResidual

for step in [0.01, 0.001, 0.0001, 0.00001, 0.000001]:
    while(i < 1000):
        i += 1
        count += 1
        j = 1
        while(j < NUM_FILTER_COEF):
            newFilterCoefficient = filterCoefficient.copy()
            newFilterCoefficient[j] = generateNeighbour(newFilterCoefficient[j], step)
            newFilterResidual = residual(newFilterCoefficient)
            if(newFilterResidual < bestFilterResidual):
                bestFilterCoefficient = newFilterCoefficient.copy()
                bestFilterResidual = newFilterResidual
            if(newFilterResidual < filterResidual + threshold):
                filterCoefficient = newFilterCoefficient.copy()
                filterResidual = newFilterResidual
                i = 0
            j += 1
        if(count % 1000 == 0):
            print(count, bestFilterResidual, filterResidual, threshold)
        threshold *= 0.999
print(repr(bestFilterCoefficient), bestFilterResidual)
print(1 / np.polynomial.Polynomial(bestFilterCoefficient).roots())