import misc_util
import DateUtils
import matplotlib.pyplot as plt
import numpy as np

def epeStruct(swap, discCurve, valFreq, volatility, simulationTimes):
    # swap = structSwap objekt, discCurve = diskontering objekt, valFreq = [år, mån, dagar]

    loopDate = swap.startDate
    pvVector = []

    cfDates = DateUtils.GenerateCashFlowDates(swap.startDate, swap.endDate, "dummyForEndDateIsNotNone", valFreq)[1]
    epeTimes = len(cfDates)
    randomValues = misc_util.lhs(epeTimes)
    timeVec = [DateUtils.DateDifferenceInYears(loopDate, date) for date in cfDates]
    rate = [discCurve.RateFromTime(timeVec[i]) for i in range(epeTimes)]

    # -------------------------------------------------------------------------------------------
    cfDatesTemp = [DateUtils.DateAddDelta(swap.startDate, 0, 0, i)
                   for i in range(1, 1 + DateUtils.DateDifferenceInDays(swap.startDate,swap.endDate))]
    epeTimesTemp = len(cfDatesTemp)
    randomValuesTemp = misc_util.lhs(epeTimesTemp)
    timeVecTemp = [DateUtils.DateDifferenceInYears(loopDate, date) for date in cfDatesTemp]
    rateTemp = [discCurve.RateFromTime(timeVecTemp[i]) for i in range(epeTimesTemp)]


    indexPathTemp = misc_util.randomPath2(swap.Initial(), randomValuesTemp, rateTemp, volatility, timeVecTemp)
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
    indexPath = misc_util.randomPath2(swap.Initial(), randomValues, rate, volatility, timeVec)

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
            dayDates = [DateUtils.DateAddDelta(loopDate, 0, 0, i) for i in range(days)]
            dailyTimeVec = [ DateUtils.DateDifferenceInYears( loopDate, date ) for date in dayDates ]
            dailyRate = [discCurve.RateFromTime(dailyTimeVec[i]) for i in range(days)]

            innerPV = 0
            isKnockIn = (min(indexPathTemp[0:cfIndex[i]])) < swap.knockInLevel
            #print("Min av indexpath [0, i]", min(indexPathTemp[0:cfIndex[i]]))

            # Beräkna värdet i given tidpunkt
            for j in range(simulationTimes):

                indexVec = misc_util.randomPath(indexPathTemp[cfIndex[i]], misc_util.lhs(days), dailyRate, volatility, 1.0/365)
                pv = swap.PresentValue(indexVec, discCurve, isKnockIn, loopDate)
                innerPV -= pv

            pvVector.append(innerPV/simulationTimes/1e9)

            # Kolla om vi är utknockade
            #print("cfIndex[i]", cfIndex[i])
            if i >= indexus and indexus != - 144:
                #print("cf index för ko", cfIndex[i], "indexvärde", indexPathTemp[cfIndex[i]],"epe pv", innerPV)
                #print("cfIndex", cfIndex)
                isKnockedOutAndDead = True
        else:
            pvVector.append( 0.0 )

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
    return pvVector