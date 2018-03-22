"""Misc functions"""

import numpy as np
from scipy.special import ndtri as norminv
from math import exp, sqrt, log

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
        # if i == 0:
        #     dt = time[0]
        # else:
        #     dt = time[i] - time[i-1]
        #print(n,i,time[i], time[i-1],dt)
        St = St * exp(det*deltaTime + vol*sqrt(deltaTime)*x[i])
        path.append( St )

    return path

def randomPath2(S0,x,rate,vol,time):

    St = S0
    path = [St]
    n = len(x)
    for i in range(n):
        det = rate[i] - 0.5 * vol * vol
        if i == 0:
            dt = time[0]
        else:
            dt = time[i] - time[i-1]
        #print(n,i,time[i], time[i-1],dt)
        St = St * exp(det*dt + vol*sqrt(dt)*x[i])
        path.append( St )

    return path