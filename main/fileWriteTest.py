# -*- coding: utf-8 -*-
import numpy as np
import shelve
import monteCarloTest as mct
import matplotlib.pyplot as plt

def natt(simEPE, simPV, simThis):
    # Creates the shelve .db file if it doesn't exist
    s = shelve.open("Natt")
    for i in range(simThis):
        q = str(i)

        f = 'Corr0'
        s[q+f] = mct.mcTest(simEPE, simPV, [[1, 0], [0, 1]])

        f = 'Corr-0.5'
        s[ q + f ] = mct.mcTest( simEPE, simPV, [ [ 1, -0.5 ], [ -0.5, 1 ] ] )

        f = 'Corr0.5'
        s[ q + f ] = mct.mcTest( simEPE, simPV, [ [ 1, 0.5 ], [ 0.5, 1 ] ] )

        print(i)
    s.close()
    return 0

def dag():
    s = shelve.open("Natt")
    for key in s:
        s1 = s[key]
        print(key)
        EPE = s1[ 0 ]
        ENE = s1[ 1 ]
        PVStruct = s1[ 2 ]
        PVLibor = s1[ 3 ]
        PVSwap = np.add(PVStruct, PVLibor)

        plt.subplot( 311 )
        plt.plot(EPE, 'g')
        plt.plot(ENE, 'r')

        plt.subplot(312)
        plt.plot(-1*PVStruct)
        plt.plot(PVLibor)

        plt.subplot(313)
        plt.plot(PVSwap)

        plt.show()

    s.close()

    return 0

natt(1000, 1000, 10)
#dag()