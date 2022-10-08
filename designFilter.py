import numpy as np
import random
import scipy as sp
import scipy.interpolate as interpolate
import scipy.integrate as integrate
import sys

FILTER_ORDER = 31
STEP = 0.01
OSF = 2.040816327
OBG = 354.8133892
SBB = 512
PBB = 512

random.seed()

f = np.array([20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500])

af = np.array([0.532, 0.506, 0.480, 0.455, 0.432, 0.409, 0.387, 0.367, 0.349, 0.330, 0.315, 0.301, 0.288, 0.276, 0.267, 0.259, 0.253, 0.250, 0.246, 0.244, 0.243, 0.243, 0.243, 0.242, 0.242, 0.245, 0.254, 0.271, 0.301])

Lu = np.array([-31.6, -27.2, -23.0, -19.1, -15.9, -13.0, -10.3, -8.1, -6.2, -4.5, -3.1, -2.0, -1.1, -0.4, 0.0, 0.3, 0.5, 0.0, -2.7, -4.1, -1.0, 1.7, 2.5, 1.2, -2.1, -7.1, -11.2, -10.7, -3.1])

Tf = np.array([78.5, 68.7, 59.5, 51.1, 44.0, 37.5, 31.5, 26.5, 22.1, 17.9, 14.4, 11.4, 8.6, 6.2, 4.4, 3.0, 2.2, 2.4, 3.5, 1.7, -1.3, -4.2, -6.0, -5.4, -1.5, 6.0, 12.6, 13.9, 12.3])

np.set_printoptions(suppress = True, threshold = 5000)

phon = 0

if((phon < 0) or (phon > 90)):
    print("Phon value out of bounds!")
    spl = 0
    freq = 0
else:
    # Setup user-defined values for equation
    Ln = phon

    # Deriving sound pressure level from loudness level (iso226 sect 4.1)
    # Af=4.47E-3 * (10.^(0.025*Ln) - 1.15) + (0.4*10.^(((Tf+Lu)/10)-9 )).^af
    Af=-0.0006705 + np.power((0.4 * np.power(10.0, ((Tf+Lu) / 10.0) - 9.0)),af)
    Lp=((10.0 / af) * np.log10(Af)) - Lu + 94

    f = np.append(f, 22050)
    Lp = np.append(Lp, 96)
    prcp = interpolate.CubicSpline(f, Lp, bc_type="natural")

def prcp2(f):
    h1 = -0.000000000000000000000004737338981378384 * f * f * f * f * f * f + 0.000000000000002043828333606125 * f * f * f * f - 0.0000001363894795463638 * f * f + 1
    h2 = 0.0000000000000000001306612257412824 * f * f * f * f * f - 0.00000000002118150887518656 * f * f * f + 0.0005559488023498642 * f
    rItu = 0.0001246332637532143 * f / np.sqrt((h1 * h1 + h2 * h2))
    return (18.2053714 + 20 * np.log10(rItu))

def weight(osf, outbandGain, f):
    return (f >= 0.5 / osf) * (outbandGain) ** (osf - 1) + (f < 0.5 / osf) / outbandGain

def residual(f, xRoot, yRoot):
    w = weight(OSF, OBG, f)
    response = np.prod(sAbs(np.exp(2j * np.pi * f) - np.expand_dims(np.array(xRoot), 1)), axis = 0) / np.prod(sAbs(np.exp(2j * np.pi * f) - np.expand_dims(np.array(yRoot), 1)), axis = 0)
    return w * w * response

sAbs = lambda z: z.real * z.real + z.imag * z.imag

# xRoot = np.append(np.array(np.repeat(0.95+0j, FILTER_ORDER)),1)
yRoot = np.array([0])
xRoot = np.sqrt(np.random.rand(FILTER_ORDER + 1)) * np.exp(np.append(2j * np.pi * np.random.rand(FILTER_ORDER), 0))
xRoot = 0.01 * (np.floor(100 * xRoot.real) + np.floor(100 * xRoot.imag) * 1j)
# yRoot = 0.9 * np.around(np.exp(1j * np.array(np.linspace(np.pi * 1 / (4 * FILTER_ORDER), np.pi, FILTER_ORDER, endpoint = False))),2)
#total = integrate.fixed_quad(residual, 0, 0.5 / OSF, (np.append(xRoot, np.conj(xRoot)), np.append(yRoot, np.conj(yRoot))), n = SBB)[0] + integrate.fixed_quad(residual, 0.5 / OSF, 0.5, (np.append(xRoot, np.conj(xRoot)), np.append(yRoot, np.conj(yRoot))), n = PBB)[0]
# total = residual(np.linspace(0, 0.5, 4096, endpoint = False) + 1 / 8192, np.append(xRoot, np.conj(xRoot[:-1])), np.append(yRoot, np.conj(yRoot[:-1])))
total = 1.8 * integrate.fixed_quad(residual, 0, 0.5 / OSF, (np.append(xRoot, np.conj(xRoot[:-1])), np.append(yRoot, np.conj(yRoot[:-1]))), n = SBB)[0] + 0.2 * integrate.fixed_quad(residual, 0.5 / OSF, 0.5, (np.append(xRoot, np.conj(xRoot[:-1])), np.append(yRoot, np.conj(yRoot[:-1]))), n = PBB)[0]
print(total)

bestXRoot = np.copy(xRoot)
bestYRoot = np.copy(yRoot)
bestTotal = total

increment = 0.05

T = 10000
count = 0

for step in [0.01, 0.001, 0.0001]:
    i = 0
    xRoot = np.copy(bestXRoot)
    yRoot = np.copy(bestYRoot)
    while i < 1000:
        j = 0
        while j < FILTER_ORDER + 1:
            newXRoot = np.copy(xRoot)
            newYRoot = np.copy(yRoot)
            if j < FILTER_ORDER:
                newXRoot[j] += random.choice((-1, 1)) * step + random.choice((-1, 1)) * step * 1j
            else:
                newXRoot[j] += random.choice((-1, 1)) * step
            newTotal = 1.8 * integrate.fixed_quad(residual, 0, 0.5 / OSF, (np.append(newXRoot, np.conj(newXRoot[:-1])), np.append(newYRoot, np.conj(newYRoot[:-1]))), n = SBB)[0] + 0.2 * integrate.fixed_quad(residual, 0.5 / OSF, 0.5, (np.append(newXRoot, np.conj(newXRoot[:-1])), np.append(newYRoot, np.conj(newYRoot[:-1]))), n = PBB)[0]
            #newTotal = residual(np.linspace(0, 0.5, 4096, endpoint = False) + 1 / 8192, np.append(newXRoot, np.conj(newXRoot[:-1])), np.append(newYRoot, np.conj(newYRoot[:-1])))
            #newTotal = 1 * sum(newTotal[0:int(4096//OSF)]) + 1 * sum(newTotal[int(4096//OSF):])
            if(np.max(sAbs(newXRoot)) >= 1 or np.max(sAbs(newYRoot)) >= 1):
                j += 1
                continue
            if(newTotal < bestTotal):
                bestXRoot = np.copy(newXRoot)
                bestYRoot = np.copy(newYRoot)
                bestTotal = newTotal
                i = 0
            if(newTotal < total + T):
                xRoot = np.copy(newXRoot)
                yRoot = np.copy(newYRoot)
                total = newTotal
                i = 0
            j += 1
        T *= 0.9999
        i += 1
        count += 1
        if(count % 250 == 0):
            print(count, i, bestTotal)


xPoly = np.polynomial.Polynomial.fromroots(np.append(bestXRoot, np.conjugate(bestXRoot)))
yPoly = np.polynomial.Polynomial.fromroots(np.append(bestYRoot, np.conjugate(bestYRoot)))
print(bestXRoot, bestYRoot)
print(yPoly - xPoly, xPoly)
print(bestTotal)