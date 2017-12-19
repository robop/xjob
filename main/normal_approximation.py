"""Approximation of the Normal Distribution"""

from math import exp


def N(x):

    y = abs(x)
    if y > 37:
        nd = 0
    else:
        e = exp(-y * y / 2.0)
        if y < 7.07106781186547:
            sumA = 0.0352624965998911 * y + 0.700383064443688
            sumA = sumA * y + 6.37396220353165
            sumA = sumA * y + 33.912866078383
            sumA = sumA * y + 112.079291497871
            sumA = sumA * y + 221.213596169931
            sumA = sumA * y + 220.206867912376
            sumB = 0.0883883476483184 * y + 1.75566716318264
            sumB = sumB * y + 16.064177579207
            sumB = sumB * y + 86.7807322029461
            sumB = sumB * y + 296.564248779674
            sumB = sumB * y + 637.333633378831
            sumB = sumB * y + 793.826512519948
            sumB = sumB * y + 440.413735824752
            nd = e * sumA / sumB
        else:
            sumA = y + 0.65
            sumA = y + 4.0 / sumA
            sumA = y + 3.0 / sumA
            sumA = y + 2.0 / sumA
            sumA = y + 1.0 / sumA
            nd = e / (sumA * 2.506628274631)
    if x > 0:
        nd = 1.0 - nd
    return nd
