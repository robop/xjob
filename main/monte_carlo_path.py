"""Här skapas en enkel Monte Carlo"""

import math
import normal_approximation
import numpy.linalg

def MonteCarloPath(S0, corr, rate, vol, tVec):
    """Antag att alla invariabler är arrayer"""
    St = S0
    L = numpy.linalg.cholesky(corr) # skapar en 3x3 cholesky av corrmatris
#    u = random skapa här 3xlen(tVec) normal random
    u_corr = numpy.dot(L,u) # gör matrismultiplication
    """Det som är kvar: loopa och skapa path, förutsatt att allt funkar"""


