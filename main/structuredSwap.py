# -*- coding: utf-8 -*-
import DateUtils
import math
import holidays
import matplotlib.pyplot as plt

class structuredSwap:
#""" Need to decide how to manage past fixings """
    def __init__(self,
                nominal,
                initial,
                knockIn,
                knockOut,
                highRate,
                lowRate,
                strike,
                startDate,
                endDate,
                frequency,
                currency,
                dayCount = "Act/365",
                adjMethod = "Mod. Following",
                isStub = True):
        self.nominal = nominal
        self.startDate = startDate
        self.endDate = endDate
        self.frequency = frequency
        self.dayCount = dayCount
        self.adjMethod = adjMethod
        self.currency = currency
        self.isStub = isStub
        self.initial = initial
        self.knockInLevel = knockIn * initial
        self.knockOutLevel = knockOut * initial
        self.highRate = highRate
        self.lowRate = lowRate
        self.strikeLevel = strike * initial

    #""" Additional structure to store prices for different dates: Makes it faster and easier to run bootstrap """
        self.prices = {}


        if self.currency == "USD":
            self.holidayArray = holidays.UnitedStates()
        elif self.currency == "SEK":
            self.holidayArray = holidays.Sweden()
        elif self.currency == "JPY":
            self.holidayArray = holidays.Japan()


        self.cfDates = DateUtils.GenerateCashFlowDates(startDate, endDate, None, frequency, adjMethod, isStub, self.holidayArray)
        self.pv = 0.0
        self.cfs = []
        self.cfPVs = []
        self.cfDays = []
        self.dfs = []
        self.pvTotal = 0.0



    def Price(self, date, price=None):
        if not price:
            return self.prices[date]

        self.prices[date] = price

    def Initial(self, initial=None):
        if not initial:
            return self.initial

        self.knockInLevel = self.knockInLevel / self.initial * initial
        self.knockOutLevel = self.knockOutLevel / self.initial * initial
        self.strikeLevel = self.strikeLevel / self.initial * initial
        self.initial = initial

    def PresentValue(self,
                     indexVector,
                     discountCurve,
                     isKnockIn,
                     refDate=DateUtils.DateToday( )):
        self.pv = 0.0
        self.cfs = []
        #self.cf = []
        self.koPos = 0
        self.isKnockedIn = (min(indexVector) < self.knockInLevel) or isKnockIn
        self.isKnockedOut = False
        tempCFDates = self.cfDates
        koDate = None

        # Kolla om refDate är senare än sista kassaflödet
        if refDate > tempCFDates[1][-1]:
            return self.pv

        # Ta bort kf datum som ligger tidigare än refDate
        while refDate > tempCFDates[1][0]:
            tempCFDates = (tempCFDates[0][1::], tempCFDates[1][1::])

        for i in range(len(tempCFDates[0])):
            cfIndex = DateUtils.DateDifferenceInDays(refDate, tempCFDates[1][i])
            dt = DateUtils.DateDifferenceInYears(tempCFDates[0][i], tempCFDates[1][i])
            df = discountCurve.DiscountFromDate(tempCFDates[1][i])
            St = indexVector[cfIndex]

            if not self.isKnockedOut:
                if St >= self.strikeLevel:
                    self.cfs.append(self.nominal * dt * self.highRate) # lägg till dagar till kassaflöde ????
                else:
                    self.cfs.append( self.nominal * dt * self.lowRate )  # lägg till dagar till kassaflöde ????

                if St >= self.knockOutLevel:
                    """We add the nominal cash flow to the position of 'index' """
                    self.cfs[i] += self.nominal
                    self.isKnockedOut = True
                    koDate = tempCFDates[1][i]
                    self.koPos = i
                elif i == len(tempCFDates[0]) - 1:
                    # Om vi är på sista kassaflödet och inte utknockade
                    if self.isKnockedIn:
                        self.cfs[i] += self.nominal * min(St / self.initial, 1.0)
                    else:
                        self.cfs[ i ] += self.nominal

            else:
                self.cfs.append( 0.0 )

            self.pv += self.cfs[ i ] * df

        # print(self.pv/self.nominal)
        #
        # dates = [ DateUtils.DateAddDelta( refDate, 0, 0, i ) for i in range( 1, 3*365+2) ]
        # times = [ DateUtils.DateDifferenceInYears( refDate, date ) for date in dates ]
        # plt.plot(times, indexVector )
        # plt.show()
        return [self.pv, koDate, self.isKnockedIn]


# endDate = DateUtils.DateAddDatePeriod(today, "3Y")
# swap = structuredSwap.structuredSwap(1e9, 18000.0, 0.65, 1.05, 0.04, 0.001, 0.85, today, endDate, "1M", "JPY")
#
# drift = [0.0003 for i in range(3*365)]
# mcPV = 0
# for i in range(100000):
#     indexVector = randomPath(18000, lhs(3*365), drift, 0.15, 1.0/365)
#     PV = swap.PresentValue(indexVector, discCurveSEK, today) # Lägg till ois jpy
#     mcPV += PV
#
# print(mcPV/1e9/100000)
# 1.045565783530332