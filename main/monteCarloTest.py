import YieldCurve
import DateUtils
import math
import matplotlib.pyplot as plt
import CCS
import DiscountCurve
from misc_util import lhs, randomPath
import time
from numba import jit
import numpy as np
from marketData import *
import structuredSwap
import epe
import Interpolation


forwardCurve = YieldCurve.Curve(dates, liborUSD, "Act/365", "Linear")
discCurveUSD = DiscountCurve.Dcurve(datesOisUSD, oisRatesUSD, "Act/365", "Linear")
discCurveSEK = DiscountCurve.Dcurve(datesOisSEK,oisRatesSEK, "Act/365", "Linear")
discCurveJPY = DiscountCurve.Dcurve(datesOisJPY, oisRatesJPY, "Act/365", "Linear")

dates = [DateUtils.DateAddDelta(today, 0, i, 0) for i in range(1, 61, 3)] # 60 mån = 5 år, ökar datum med 1 M intervall

crossSwap = CCS.CCS(1, dates[0], dates[-1], -0.0, "3m", "SEK")

# CCSPV = crossSwap.PresentValue(discCurveUSD, forwardCurve, 1, discCurveSEK, 0.03) # Räntan

"""Här börjar monte carlito"""

#@jit
def CarlosCCS():
    N = 365 # år
    M = 100


    dates = [ DateUtils.DateAddDelta( today, 0, i, 0 ) for i in
              range( 1, 61) ]  # 60 mån = 5 år, ökar datum med 1 M intervall
    timeVec = [ DateUtils.DateDifferenceInYears( today, date ) for date in dates]  # tar fram tidsskillnad i år för
    N = len(dates)
    FX = [ lhs( N ) for i in range( M ) ]


    fxDrift = [discCurveUSD.RateFromTime(timeVec[i]) - discCurveSEK.RateFromTime(timeVec[i]) for i in range(N)]
    Q = [randomPath( 8.2, FX[i], fxDrift, 0.005, timeVec ) for i in range(M)]


    expectedValue = np.zeros(N)
    for j in range(N): #Vill prissätta månadsvis

        for i in range(M): # antal simuleringar för varje tidpunkt (ÖKA)
            expectedValue[j] += crossSwap.PresentValue(discCurveUSD, forwardCurve, Q[i][j], discCurveSEK, 0.03, dates[j])

        expectedValue[j] = expectedValue[j] / M

    plt.plot(timeVec[0:N],expectedValue)
    plt.show()
    return expectedValue

endDate = DateUtils.DateAddDatePeriod(today, "3Y")
swap = structuredSwap.structuredSwap(1e9, 18000.0, 0.65, 1.05, 0.04, 0.001, 0.85, today, endDate, "3M", "JPY")

nSim = 9
EEVEKTOR = epe.epeStruct(swap, discCurveJPY, "1m", 0.15, 100)

for dask in range(nSim):
    eee = epe.epeStruct(swap, discCurveJPY, "1m", 0.15, 100)

    EEVEKTOR = np.add(EEVEKTOR, eee)

EEVEKTOR = np.divide(EEVEKTOR, nSim+1)
EEVEKTOR = np.add(EEVEKTOR, 1)


print(EEVEKTOR)
timeVec = [i/365 for i in range(3*365)]
time2 = [i/12 for i in range(36)]
interpolatedEE = [Interpolation.CubicSplineInterpolation(date, time2, EEVEKTOR) for date in timeVec]
plt.plot(timeVec, interpolatedEE)
plt.show()


# endDate = DateUtils.DateAddDatePeriod(today, "3Y")
# swap = structuredSwap.structuredSwap(1e9, 18000.0, 0.65, 1.05, 0.04, 0.001, 0.85, today, endDate, "3M", "JPY")
# print(swap.startDate)
#
# #drift = [0.0003 for i in range(3*7000)]
# dateJPY = [DateUtils.DateAddDelta(today, 0, i, 0) for i in range(1, 37)]
# timeJPY = [DateUtils.DateDifferenceInYears(today, date) for date in dateJPY]
# rateJPY = [discCurveJPY.RateFromTime(timeJPY[i]) for i in range(len(timeJPY))]
# mcPV = 0
#
#
# loopDate = today
# totPv = []
# path = randomPath(18000, lhs(len(timeJPY)), timeJPY, 0.15, 30.0/365)
# for j in range(len(timeJPY)):
#     loopDate = DateUtils.DateAddDelta(today, 0, j, 0)
#     days = DateUtils.DateDifferenceInDays(loopDate,endDate)
#
#     mcPV = 0
#     for i in range( 100 ):
#         indexVector = randomPath( path[j], lhs(days), rateJPY, 0.15, 1.0 / 365 )
#         PV = swap.PresentValue( indexVector, discCurveJPY, loopDate)  # Lägg till ois jpy
#         mcPV += PV
#
#     totPv.append(mcPV/100/1e9 - 1)
#
# plt.plot([i for i in range(36)], totPv)
# plt.show()
#1.045565783530332



