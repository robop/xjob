# -*- coding: utf-8 -*-
import YieldCurve
import DateUtils
import math
import matplotlib.pyplot as plt
import CCS
import DiscountCurve
from misc_util import lhs, randomPath, createVolSurface
import time
from numba import jit
import numpy as np
from marketData import *
import structuredSwap
import epe
import Interpolation
import FRN
import matplotlib.patches as mpatches

def mcTest(epeSimulations, structPVSimulations, correlation):
    import marketData
    # epeSimulations, structPVSimulations, correlation
    forwardCurve = YieldCurve.Curve(marketData.dates, liborUSD, "Act/365", "Linear")
    discCurveUSD = DiscountCurve.Dcurve(datesOisUSD, oisRatesUSD, "Act/365", "Linear")
    discCurveSEK = DiscountCurve.Dcurve(datesOisSEK,oisRatesSEK, "Act/365", "Linear")
    discCurveJPY = DiscountCurve.Dcurve(datesOisJPY, oisRatesJPY, "Act/365", "Linear")

    dates = [DateUtils.DateAddDelta(today, 0, i, 0) for i in range(1, 61, 3)] # 60 mån = 5 år, ökar datum med 1 M intervall

    crossSwap = CCS.CCS(1, dates[0], dates[-1], -0.0, "3m", "SEK")

    # -.,-.,-.,-.,-,,-.,-,-.,-,.-.,-.,.-.,-.,-.,-.,-.-,-,-,-.,--.,-.,-.,-..-,,.-.,-.,-.,-.,-.+???????







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

    # nominal = 1e9
    # endDate = DateUtils.DateAddDatePeriod(today, "3Y")
    # frn = FRN.frn(nominal, today, endDate, 0.0, "3m", "USD")
    # presentValueFRN = frn.PresentValue(discCurveUSD,forwardCurve,today,endDate)
    # print(presentValueFRN/1e9)

    # .--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--
    endDate = DateUtils.DateAddDatePeriod(today, "3Y")
    swap = structuredSwap.structuredSwap(1e9, 18000.0, 0.65, 1.05, 0.04, 0.001, 0.85, today, endDate, "3M", "JPY")
    spread = -0.004

    volFX = createVolSurface(today, 1/0.00943, volJPYUSD, volPeriod) # USDJPY
    volIndex = createVolSurface(today, 18000, volNikkei, volPeriod)

    nSim = epeSimulations
    #[EEVEKTOR, EEVEKTORLibor, index, fx] = epe.epeStruct(swap, discCurveJPY, discCurveUSD, forwardCurve, spread, "1m", 0.15, 0.075, 200)
    EEVEKTOR = np.zeros(36)
    EEVEKTORLibor = np.zeros(36)
    EPE = np.zeros(36)
    ENE = np.zeros(36)
    index = np.zeros(1097)
    fx = np.zeros(1097)

    for dask in range(nSim):
        [eeStruct, eeLibor, eeIndex, eeFX, dayBasis, indexCF] = epe.epeStruct(swap, discCurveJPY, discCurveUSD, forwardCurve,
                                                                              spread, "1m", volIndex, volFX, structPVSimulations, correlation)

        EEVEKTOR = np.add(EEVEKTOR, eeStruct)
        EEVEKTORLibor = np.add(EEVEKTORLibor, eeLibor)
        EEtotal = np.add(EEVEKTOR, EEVEKTORLibor)
        EPE = np.add(EPE, [max(EEtotal[i], 0) for i in range(len(EEtotal))])
        ENE = np.add( ENE, [ min( EEtotal[ i ], 0 ) for i in range( len( EEtotal ) ) ] )
        index = np.add(index, eeIndex)
        fx = np.add(fx, eeFX)

        # plt.figure(1)
        # plt.subplot(221)
        # plt.plot((EEVEKTOR * -1), 'g')
        # plt.plot(EEVEKTORLibor, 'r')
        # red_patch = mpatches.Patch( color='red', label='Libor Leg' )
        # ed_patch = mpatches.Patch( color='green', label='Struct Leg' )
        # plt.legend( handles=[ red_patch, ed_patch ])
        # plt.subplot(222)
        # plt.plot(EPE, 'r')
        # plt.plot(ENE, 'g')
        # epe_patch = mpatches.Patch(color='red', label='EPE')
        # ene_patch = mpatches.Patch( color='green', label='ENE' )
        # plt.legend( handles=[epe_patch, ene_patch])
        # plt.subplot( 212 )
        # plt.plot(eeIndex, 'b')
        # plt.plot(eeFX, 'k')
        # plt.plot( dayBasis, indexCF, 'co' )
        # index_patch = mpatches.Patch(color='blue', label='Nikkei225')
        # fx_patch = mpatches.Patch(color='k', label='USD/JPY')
        # plt.legend(handles=[index_patch, fx_patch])
        # plt.show()


    EEVEKTOR = np.divide(EEVEKTOR, nSim)
    #EEVEKTOR = np.add(EEVEKTOR, 1)

    EEVEKTORLibor = np.divide(EEVEKTORLibor, nSim)
    #EEVEKTORLibor = np.subtract(EEVEKTORLibor, 1)

    index = np.divide(index, nSim)
    fx = np.divide(fx, nSim)

    EPE = np.divide(EPE, nSim)
    ENE = np.divide(ENE, nSim)

    EEtotal = np.add(EEVEKTOR,EEVEKTORLibor)

    #EPE = [max(EEtotal[i], 0) for i in range(len(EEtotal))]
    #ENE = [min(EEtotal[i], 0) for i in range(len(EEtotal))]

    # print(EEVEKTOR)
    # print(EEVEKTORLibor)
    # timeVec = [i/365 for i in range(3*365)]
    # time2 = [i/12 for i in range(36)]
    # interpolatedEPE = [Interpolation.CubicSplineInterpolation(date, time2, EPE) for date in timeVec]
    # interpolatedENE = [Interpolation.CubicSplineInterpolation(date, time2, ENE) for date in timeVec]
    # interpolatedEEtotal = [Interpolation.CubicSplineInterpolation(date, time2, EEtotal) for date in timeVec]
    # plt.plot(EEVEKTOR, 'y--')
    # plt.plot(EEVEKTORLibor, 'b--')
    # plt.plot(EEtotal, 'k')
    # plt.figure(1)
    # plt.subplot(211)
    # plt.plot(EPE, 'g')
    # plt.plot(ENE, 'r')
    # plt.subplot(212)
    # plt.plot(index, 'r')
    # plt.plot(fx, 'b')
    #
    # plt.show()

    # .--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--

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


    return (EPE, ENE, EEVEKTOR, EEVEKTORLibor)
