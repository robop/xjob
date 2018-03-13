"""Misc functions"""

import numpy as np
from scipy.special import ndtri as norminv

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