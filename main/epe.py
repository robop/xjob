# -*- coding: utf-8 -*-
import misc_util
import DateUtils
import matplotlib.pyplot as plt
import numpy as np
import FRN

def epeStruct(swap, discCurve, discCurveFRN, forwardCurve, spread, valFreq, volIndex, volFX, simulationTimes, correlationMatrix):
    # swap = structSwap objekt, discCurve = diskontering objekt, valFreq = [år, mån, dagar]
    fxJPYUSD = 0.00943
    fxNominal = swap.nominal / fxJPYUSD
    frn = FRN.frn(fxNominal, swap.startDate, swap.endDate, spread, swap.frequency, swap.currency)

    loopDate = swap.startDate
    pvVector = []
    pvVectorLibor = []

    cfDates = DateUtils.GenerateCashFlowDates(swap.startDate, swap.endDate, "dummyForEndDateIsNotNone", valFreq)[1]
    epeTimes = len(cfDates)
    randomValues = misc_util.lhs(epeTimes)
    timeVec = [DateUtils.DateDifferenceInYears(loopDate, date) for date in cfDates]
    rate = [discCurve.RateFromTime(timeVec[i]) for i in range(epeTimes)]

    # -------------------------------------------------------------------------------------------
    cfDatesTemp = [DateUtils.DateAddDelta(swap.startDate, 0, 0, i)
                   for i in range(1, 1 + DateUtils.DateDifferenceInDays(swap.startDate,swap.endDate))]
    epeTimesTemp = len(cfDatesTemp)
    timeVecTemp = [DateUtils.DateDifferenceInYears(loopDate, date) for date in cfDatesTemp]

    # rateTemp är jpy, rateFRN är usd
    rateTemp = [discCurve.RateFromTime(timeVecTemp[i]) for i in range(epeTimesTemp)]
    rateFRN = [ discCurveFRN.RateFromTime( timeVecTemp[ i ] ) for i in range( epeTimesTemp ) ]
    rateFX = np.subtract(rateTemp, rateFRN)


    randomValuesTemp = misc_util.lhs( epeTimesTemp )
    randomValuesFX = misc_util.lhs(epeTimesTemp)

    #correlationMatrix = [[1, 0.7], [0.7, 1]]
    [randomValuesTemp,randomValuesFX] = misc_util.cholesky(correlationMatrix, [randomValuesTemp, randomValuesFX])

    rateWithDividend = np.subtract(rateTemp, 0.016)
    indexPathTemp = misc_util.randomPath2(swap.Initial(), randomValuesTemp, rateWithDividend, volIndex, timeVecTemp)
    fxPath = misc_util.randomPath2( fxJPYUSD, randomValuesFX, rateFX, volFX, timeVecTemp )
    cfIndex = []
    timeDiffFactor = (DateUtils.DateDifferenceInDays(swap.startDate, swap.cfDates[1][0]) / DateUtils.DateDifferenceInDays(swap.startDate, cfDates[0]) )
    for i in range(len(cfDatesTemp)):
        if cfDatesTemp[i] == cfDates[0]:
            cfIndex.append(i - 1)
            cfDates = cfDates[1::]

    realCF = [DateUtils.DateDifferenceInDays(swap.startDate, swap.cfDates[1][i]) for i in range(len(swap.cfDates[1]))] # vektor med dagar till reala cf
    indexus = -144

    for i in range(len(realCF)):
        if indexPathTemp[realCF[i]] >= swap.knockOutLevel:
            indexus = round(timeDiffFactor) + i * round(timeDiffFactor) - 1
            break
    #print("indexus", indexus)
    # -------------------------------------------------------------------------------------------
    indexPath = misc_util.randomPath2(swap.Initial(), randomValues, rate, volIndex, timeVec)

    """valfreq = '12m' """
    yymmdd = [0, 0, 0]
    n = len(valFreq)-1
    unit = valFreq[-1]
    if unit in [ "d", "D" ]:
        yymmdd[2] = int(valFreq[0:n])
    if unit in [ "m", "M" ]:
        yymmdd[ 1 ] = int(valFreq[ 0:n ])
    if unit in [ "y", "Y" ]:
        yymmdd[ 0 ] = int(valFreq[ 0:n ])

    isKnockedOutAndDead = False
    knockOutIndex = 0

    for i in range (epeTimes):
        if not isKnockedOutAndDead:
            # Inledande definitioner och beräkningar
            loopDate = DateUtils.DateAddDelta( loopDate, yymmdd[0], yymmdd[1], yymmdd[2])
            days = DateUtils.DateDifferenceInDays(loopDate,swap.endDate)
            dayDates = [DateUtils.DateAddDelta(loopDate, 0, 0, j) for j in range(days)]
            dailyTimeVec = [ DateUtils.DateDifferenceInYears( loopDate, date ) for date in dayDates ]
            dailyTimeVec = np.add(dailyTimeVec, DateUtils.DateDifferenceInYears(swap.startDate,loopDate))
            dailyRate = [discCurve.RateFromTime(dailyTimeVec[j]) for j in range(days)] # Är denna rätt tid på????

            innerPV = 0
            innerPVLibor = 0
            isKnockIn = (min(indexPathTemp[0:cfIndex[i]])) < swap.knockInLevel
            #print("Min av indexpath [0, i]", min(indexPathTemp[0:cfIndex[i]]))
            numOfKI = 0
            # Beräkna värdet för struct ben i given tidpunkt
            for j in range(simulationTimes):

                #indexVec = misc_util.randomPath(indexPathTemp[cfIndex[i]], misc_util.lhs(days), dailyRate, volIndex, 1.0/365)
                indexVec = misc_util.randomPath2(indexPathTemp[cfIndex[i]], misc_util.lhs(days), dailyRate, volIndex, dailyTimeVec)
                [pvStruct, koDate, knockIN] = swap.PresentValue(indexVec, discCurve, isKnockIn, loopDate)
                pvLibor = frn.PresentValue(discCurveFRN, forwardCurve, loopDate, koDate)
                innerPV -= pvStruct
                innerPVLibor += pvLibor
                if knockIN:
                    numOfKI += 1

            #print( i, ":a månaden", numOfKI/simulationTimes*100, "%")
            pvVector.append(innerPV / (simulationTimes * swap.nominal))
            pvVectorLibor.append((fxPath[cfIndex[i]] * innerPVLibor) / (simulationTimes * swap.nominal))

            # Kolla om vi är utknockade
            #print("cfIndex[i]", cfIndex[i])
            if i >= indexus and indexus != - 144:
                #print("cf index för ko", cfIndex[i], "indexvärde", indexPathTemp[cfIndex[i]],"epe pv", innerPV)
                #print("cfIndex", cfIndex)
                isKnockedOutAndDead = True
        else:
            pvVector.append( 0.0 )
            pvVectorLibor.append(0.0)

    #print("PV vektor \n", pvVector)

    # plt.figure(1)
    # # plt.subplot( 211 )
    # # plt.plot(indexPath)
    # plt.plot( [ 0, 36/12 ], [ 11700/18000, 11700/18000 ], 'y--')
    # plt.plot([0, 36/12], [18900/18000, 18900/18000], 'r--')
    # # plt.subplot( 212 )
    # plt.plot([timeVecTemp[cfIndex[i]] for i in range(len(cfIndex))], pvVector)
    # # plt.axis([0, 36, 0.85, 1.3])
    # plt.plot([0, 3], [0.85, 0.85], 'g--')
    # plt.plot([i/365 for i in range(len(indexPathTemp))], np.divide(indexPathTemp, 18000))


    # ----------------------
    swapCFDates = swap.cfDates[1]
    yearBasis = [DateUtils.DateDifferenceInYears(swap.startDate, swapCFDates[i]) for i in range(len(swapCFDates))]
    dayBasis = [DateUtils.DateDifferenceInDays(swap.startDate, swapCFDates[i]) for i in range(len(swapCFDates))]
    indexCF = [indexPathTemp[dayBasis[i]] for i in range(len(dayBasis))]
    indexCF = np.divide(indexCF, 18000)
    # ----------------------
    # print("CF datum i år nu \n", yearBasis)
    # print("CF datum i dagar", dayBasis)
    # plt.plot(yearBasis, indexCF, 'bo')
    # plt.show()

    returnIndex = np.divide(indexPathTemp, swap.Initial())
    returnFX = np.divide(fxPath, fxJPYUSD)

    return [pvVector, pvVectorLibor, returnIndex, returnFX, dayBasis, indexCF]