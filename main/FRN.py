import DateUtils
import math
import holidays

class frn:
#""" Need to decide how to manage past fixings """
    def __init__(self,
                nominal,
                startDate,
                endDate,
                spread,
                frequency,
                currency,
               # koProb,
                dayCount = "Act/365",
                adjMethod = "Mod. Following",
                isStub = True):
        self.nominal = nominal
        self.startDate = startDate
        self.endDate = endDate
        self.spread = spread
        self.frequency = frequency
        self.dayCount = dayCount
        self.adjMethod = adjMethod
        self.currency = currency
       # self.koProb = koProb
        self.isStub = isStub

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
            return self.nominal

    def PresentValue(self,
                discountCurve,
                forwardCurve,
                refDate=DateUtils.DateToday(),
                endDate = None):
        self.pv = 0.0
        self.cfs = []
        self.cfPVs = []
        self.cfDays = []
        self.dfs = []
        tempCFDates = self.cfDates

        if endDate:
            # Ta bort kf datum som ligger tidigare än refDate
            while endDate > tempCFDates[ 1 ][ -1 ]:
                tempCFDates = (tempCFDates[ 0 ][ 0:-2 ], tempCFDates[ 1 ][ 0:-2 ])

        discountCurve.CurveDate(refDate)
        forwardCurve.CurveDate(refDate)

        for i in range(len(tempCFDates[0])):
            startDate = tempCFDates[0][i]
            endDate = tempCFDates[1][i]

            if DateUtils.DateDifferenceInDays(refDate, endDate) > 0:
                dt = DateUtils.GetPeriodLength(startDate, endDate, self.dayCount)
                forward = forwardCurve.ForwardRateFromDates(startDate, endDate, self.dayCount)
                df = discountCurve.DiscountFromDate(endDate)
                cf = self.nominal * (forward + self.spread) * dt[1]

                self.cfs.append(cf)
                self.cfPVs.append(cf * df)

            else:
                cf = 0.0
                df = 1.0
                dt = [0.0, 0.0]
                self.cfs.append(cf)
                self.cfPVs.append(cf)

            self.pv += cf * df

            self.dfs.append(df)
            self.cfDays.append(dt[0])


        #Nu görs grejer på slutet, själva summeringen av ben
        df = discountCurve.DiscountFromDate(tempCFDates[1][-1])

        self.cfs[-1] += self.nominal
        self.cfPVs[-1] += self.nominal * df
        self.pv += self.nominal * df

        return self.pv