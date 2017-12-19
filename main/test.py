"""Testar grejer"""

# from normal_approximation import *
import normal_approximation
import numpy
import numba

x = 0
y = normal_approximation.N( x )
print( y )


def cholesky(M):
    L = numpy.linalg.cholesky( M )

    return L


#@numba.jit()
def sum2d(arr):
    M, N = arr.shape
    result = 0.0
    for i in range( M ):
        for j in range( N ):
            result += arr[ i, j ]
    return result

import time
start = time.time()
Q = numpy.array([[1,2,3,4,5],[2,3,4,5,6],[3,4,5,6,7],[4,5,6,7,8],[5,6,7,8,9]])
F = sum2d(Q)
end = time.time()
print(F)
print(end - start)