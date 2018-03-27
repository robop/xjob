import DateUtils
import math
import holidays
import FRN

class liborLeg:
    # """ Need to decide how to manage past fixings """
    def __init__(self,
                 nominal,
                 startDate,
                 endDate,
                 spread,
                 frequency,
                 currency,
              #   koProb,
                 dayCount="Act/365",
                 adjMethod="Mod. Following",
                 isStub=True):
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

        # """ Additional structure to store prices for different dates: Makes it faster and easier to run bootstrap """
        self.prices = {}

        if self.currency == "USD":
            self.holidayArray = holidays.UnitedStates( )
        elif self.currency == "SEK":
            self.holidayArray = holidays.Sweden( )
        elif self.currency == "JPY":
            self.holidayArray = holidays.Japan( )

        self.cfDates = DateUtils.GenerateCashFlowDates( startDate, endDate, None, frequency, adjMethod, isStub,
                                                        self.holidayArray )
        self.pv = 0.0
        self.cfs = [ ]
        self.cfPVs = [ ]
        self.cfDays = [ ]
        self.dfs = [ ]
        self.pvTotal = 0.0

    def PresentValue(self,
                     discountCurve,
                     forwardCurve,
                     koProb,
                     refDate=DateUtils.DateToday( )):

        frn = FRN.frn(self.nominal, self.startDate, self.endDate, self.spread, self.frequency, self.currency)
        pv = 0.0
        for i in range(koProb):
            pv += frn.PresentValue(discountCurve, forwardCurve, refDate, self.cfDates[1][])