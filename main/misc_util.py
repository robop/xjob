# -*- coding: utf-8 -*-
"""Misc functions"""

import numpy as np
from scipy.special import ndtri as norminv
from math import exp, sqrt, log
import VolatilitySurface
import DateUtils

"""Creates standard normal random numbers"""
def lhs(x):

    pi = np.random.permutation(x)
    U = np.random.uniform(0.0, 1.0, x)
    V = (pi + U)/x

    for i in range(x):
        V[i] = norminv(V[i])

    return V

"""Correlates series of random number using cholesky decomposition"""
def cholesky(corr,u):

    L = np.linalg.cholesky( corr )  # skapar en 3x3 lower triangular av corrmatris
    u_corr = np.dot( L, u )  # gör slumptalen korrelerade enligt matris

    return u_corr

"""Creates a random path """
def randomPath(S0,x,rate,vol,deltaTime):

    St = S0
    path = [St]
    n = len(x)
    for i in range(n):
        det = rate[i] - 0.5 * vol * vol

        St = St * exp(det*deltaTime + vol*sqrt(deltaTime)*x[i])
        path.append( St )

    return path

def randomPath2(S0,x,rate,vol,time):

    St = S0
    path = [St]
    n = len(x)

    for i in range(n):
        if type( vol ) is not float:
            volTemp = vol.ForwardVolatilityFromTimes( path[-1], 0, time[ i ] )
        else:
            volTemp = vol

        det = rate[i] - 0.5 * volTemp * volTemp
        if i == 0:
            dt = time[0]
        else:
            dt = time[i] - time[i-1]

        St = St * exp(det*dt + volTemp*sqrt(dt)*x[i])
        path.append( St )

    return path

"""Create a volatility surface"""
def createVolSurface(date, spotPrice, volatility, volPeriod):
    strikeInter = "Linear"
    expiryInter = "Linear in Volatility"
    volSurface = VolatilitySurface.VolatilitySurface( strikeInter, expiryInter, date)

    strikes = [ 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0 ]
    strikes = [ 0.01 * spotPrice * strike for strike in strikes ]

    for i in range( len( volatility ) ):
        expiryDate = DateUtils.DateAddDatePeriod( date, volPeriod[ i ] )
        volatilities = [ volatility[i] for j in range( 7 ) ]
        volSurface.AddSkew( strikes, volatilities, expiryDate )

    return volSurface