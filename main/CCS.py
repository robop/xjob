import DateUtils
import numpy as np
import math

class CCS:
#""" Need to decide how to manage past fixings """
    def __init__(self,
                nominal,
                startDate,
                endDate,
                spread,
                frequency,
                dayCount,
                adjMethod,
                currency,
                isStub):
        self.nominal = nominal
        self.startDate = startDate
        self.endDate = endDate
        self.spread = spread
        self.frequency = frequency
        self.dayCount = dayCount
        self.adjMethod = adjMethod
        self.currency = currency
        self.isStub = isStub

    #""" Additional structure to store prices for different dates: Makes it faster and easier to run bootstrap """
        self.prices = {}

        if self.currency == "USD":
            self.holidayArray = holidays.UnitedStates()
        elif self.currency == "SEK":
            self.holidayArray = holidays.Sweden()

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

    def PresentValue(self,
                discountCurve,
                forwardCurve,
                fxRate,
                discountCurveFix,
                fixRate,
                refDate=DateUtils.DateToday()):
        self.pv = 0.0
        self.cfs = []
        self.cfPVs = []
        self.cfDays = []
        self.dfs = []
        self.pvFix = 0.0
        self.cfsFix = []
        self.cfPVsFix = [ ]
        self.cfDaysFix = [ ]
        self.dfsFix = [ ]

        discountCurve.CurveDate(refDate)
        forwardCurve.CurveDate(refDate)
        discountCurveFix.CurveDate(refDate)

        for i in range(len(self.cfDates[0])):
        startDate = self.cfDates[0][i]
        endDate = self.cfDates[1][i]
        if DateUtils.DateDifferenceInDays(refDate, endDate) > 0:
            dt = DateUtils.GetPeriodLength(startDate, endDate, self.dayCount)
            forward = forwardCurve.ForwardRateFromDates(startDate, endDate, self.dayCount)
            rate = discountCurve.RateFromDate(endDate)
            t = DateUtils.DateDifferenceInYears(refDate, endDate)
            df = math.exp(-rate * t)
            cf = self.nominal * (forward + self.spread) * dt[1]

            #Samma som ovan fast för fix ben
            rateFix = discountCurveFix.RateFromDate(endDate)
            dfFix = math.exp(-rateFix * t)
            cfFix = self.nominal * fixRate * dt[1]

            self.cfs.append(cf)
            self.cfPVs.append(cf * df)

            #Samma som ovan fast för fix ben
            self.cfsFix.append(cfFix)
            self.cfPVsFix.append(cfFix * dfFix)

        else:
            cf = 0.0
            df = 1.0
            dt = [0.0, 0.0]
            self.cfs.append(cf)
            self.cfPVs.append(cf)

            # Samma som ovan fast för fix ben
            cfFix = 0.0
            dfFix = 1.0
            dt = [ 0.0, 0.0 ]
            self.cfs.append( cfFix )
            self.cfPVs.append( cfFix * dfFix )

        self.pv += cf * df
        self.pvFix += cfFix * dfFix

        self.dfs.append(df)
        self.cfDays.append(dt[0])

        self.dfsFix.append(dfFix)

        #Nu görs grejer på slutet, själva summeringen av ben
        rate = discountCurve.RateFromDate(self.endDate)
        t = DateUtils.DateDifferenceInYears(refDate, self.endDate)
        df = math.exp(-rate * t)

        rateFix = discountCurveFix.RateFromDate(self.endDate)
        dfFix = math.exp(-rateFix * t)

        self.cfs[-1] += self.nominal
        self.cfPVs[-1] += self.nominal * df
        self.pv += self.nominal * df

        self.cfsFix[ -1 ] += self.nominal
        self.cfPVsFix[ -1 ] += self.nominal * dfFix
        self.pvFix += self.nominal * dfFix

        self.pvTotal = self.pvFix - fxRate * self.pv

        return self.pvTotal