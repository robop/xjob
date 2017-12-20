"""Här skapas en enkel Monte Carlo"""

import math
import normal_approximation
import numpy as np

def MonteCarloPath(S0, corr, rate, vol, tVec):
    """Antag att alla invariabler är arrayer"""
    St = S0
    path = St
    n = len(tVec) # Längen, möjligen fel om 1xN ist för Nx1

    """Gör korrelereade slumptal"""
    L = np.linalg.cholesky(corr) # skapar en 3x3 lower triangular av corrmatris
    u = np.random.normal(0.0, 1.0, (len(corr), n)) # Här ska vi ha en 3xN
    u_corr = np.dot(L,u) # gör slumptalen korrelerade enligt matris

    """Skapa the path"""
    for i in range(n - 1)
        dt = tVec[ i + 1 ] - tVec[ i ]
        # 2do: skapa värde på St, gärna i vektorform dvs en kolonn åt gången så man slipper inre loop
        # append till path
    return path