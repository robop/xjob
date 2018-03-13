import math
import DateUtils
import Interpolation

class Curve:
    def __init__(self, \
                 dates: object, \
                 rates: object, \
                 dayCount: object = "Act/365", \
                 interpolation: object = "Hermite", \
                 extrapolation: object = "Flat", \
                 refDate: object = DateUtils.DateToday() \
                 ) -> object:
        self.dates = dates
        self.points = []
        self.rates = rates
        self.inter = interpolation
        self.dayCount = dayCount
        self.refDate = refDate
        self.extra = extrapolation
        self.shift = 0.0
        self.isShifted = False
        self.curveName = None

        """ Comparing integers is more efficient than strings """
        if interpolation == "Linear":
            self.inter = Interpolation.LinearInterpolation
        elif interpolation == "Hermite":
            self.inter = Interpolation.HermiteInterpolation
        elif interpolation == "Cubic Spline":
            self.inter = Interpolation.CubicSplineInterpolation
        elif interpolation == "Cubic Spline Log Disc":
            self.inter = Interpolation.CubicSplineLogDiscountInterpolation
        elif interpolation == "Log Linear":
            self.inter = Interpolation.LogLinearInterpolation
        elif interpolation == "Linear Log Disc":
            self.inter = Interpolation.LogDiscountLinearInterpolation
        else:
            self.inter = Interpolation.LinearInterpolation

        self.ConvertDatesToTimes()

    def CurveName(self, curveName=None):
        if curveName:
            self.curveName = curveName
        else:
            return self.curveName

    def CurveDate(self, refDate=None):
        if refDate:
            self.refDate = refDate
        else:
            return self.refDate

    def Shift(self, shift):
        """ Shift in basis points"""
        self.shift = shift*1.0e-4
        self.isShifted = True
        self.rates = [rate + self.shift for rate in self.rates]

    def Unshift(self):
        if self.isShifted:
            self.rates = [rate - self.shift for rate in self.rates]
        self.isShifted = False
        self.shift = 0.0

    def Dates(self, dates=None):
        if dates != None:
            self.dates = dates
            self.ConvertDatesToTimes()
        else:
            return self.dates

    def Rates(self, rates=None):
        if rates != None:
            self.rates = rates
        else:
            return self.rates

    def ConvertDatesToTimes(self):
        self.points = []
        for date in self.dates:
            timePoint = DateUtils.GetPeriodLength(self.refDate, date, self.dayCount)[1]
            self.points.append(timePoint)

    def RateFromDate(self, date):
        T = DateUtils.GetPeriodLength(self.refDate, date, self.dayCount)[1]
        return self.RateFromTime(T)

    def RateFromTime(self, point):
        return self.inter(point, self.points, self.rates, self.extra, self.extra)

    def RateFromTypeAndTime(self, T, rateType, dayCount):
        """ Rates in the curve are assumed to be continuous, Act/365 """
        rate = self.RateFromTime(T)

        if dayCount == "Act/365":
            T2 = T
        elif dayCount == "Act/360":
            T2 = T * 365.0 / 360.0
        elif dayCount == "30/360":
            years = int(T)
            months = int((T - years) * 12)
            days = int((T - years - months / 12.0) * 365)

            date = str(DateUtils.DateAddDelta(self.refDate, years, months, days))
            T2 = DateUtils.GetPeriodLength(self.refDate, date, dayCount)

        if rateType == "Simple":
            return (math.exp(rate * T) - 1.0) / T2
        elif rateType == "Annual":
            return pow(math.exp(rate * T), 1.0 / T2) - 1
        elif rateType == "Semi-Annual":
            return 2 * (pow(math.exp(rate * T), 1.0 / (2 * T2)) - 1)
        elif rateType == "Quarterly":
            return 4 * (pow(math.exp(rate * T), 1.0 / (4 * T2)) - 1)
        elif rateType == "Monthly":
            return 12 * (pow(math.exp(rate * T), 1.0 / (12 * T2)) - 1)

    def RateFromTypeAndDate(self, date, rateType, dayCount):
        """ Rates in the curve are assumed to be continuous, Act/365 """
        T = DateUtils.DateDifferenceInYears(self.refDate, date)
        rate = self.RateFromTime(T)

        if dayCount == "Act/365":
            T2 = T
        elif dayCount == "Act/360":
            T2 = DateUtils.GetPeriodLength(self.refDate, date, dayCount)
        elif dayCount == "30/360":
            T2 = DateUtils.GetPeriodLength(self.refDate, date, dayCount)

        if rateType == "Simple":
            return (math.exp(rate * T) - 1.0) / T2
        elif rateType == "Annual":
            return pow(math.exp(rate * T), 1.0 / T2) - 1
        elif rateType == "Semi-Annual":
            return 2 * (pow(math.exp(rate * T), 1.0 / (2 * T2)) - 1)
        elif rateType == "Quarterly":
            return 4 * (pow(math.exp(rate * T), 1.0 / (4 * T2)) - 1)
        elif rateType == "Monthly":
            return 12 * (pow(math.exp(rate * T), 1.0 / (12 * T2)) - 1)

    def ForwardRate(self, startTime, endTime, periodLength):
        """ The periodLength should take into account the dayCount convention """
        rateStart = self.RateFromTime(startTime)
        rateEnd = self.RateFromTime(endTime)

        """ D is the continuous forward rate """
        D = math.exp(-rateEnd * endTime + rateStart * startTime)

        """ forw is the simple forward rate: Typically used for floating interest rate cash flows """
        forw = (1 - D) / (D * periodLength)

        return forw

    def ForwardRateFromDates(self, startDate, endDate, dayCount=None):
        """ Using the inputted dayCount method for the simple rate """
        rateStart = self.RateFromDate(startDate)
        rateEnd = self.RateFromDate(endDate)
        tStart = DateUtils.DateDifferenceInYears(self.refDate, startDate)
        tEnd = DateUtils.DateDifferenceInYears(self.refDate, endDate)

        """ D is the continuous forward rate """
        D = math.exp(-rateEnd * tEnd + rateStart * tStart)

        """ forw is the simple forward rate: Typically used for floating interest rate cash flows """
        if dayCount:
            dt = DateUtils.GetPeriodLength(startDate, endDate, dayCount)
            forw = (1 - D) / (D * (dt[1]))
        else:
            """ We use Act/365, the dayCount convention of the stored rates """
            forw = (1 - D) / (D * (tEnd - tStart))

        return forw

    def ForwardRateFromTimes(self, startTime, endTime):
        """ Does not take into account day count conventions """
        rateStart = self.RateFromTime(startTime)
        rateEnd = self.RateFromTime(endTime)

        """ D is the continuous forward rate """
        D = math.exp(-rateEnd * endTime) / math.exp(-rateStart * startTime)

        """ forw is the simple forward rate: Typically used for floating interest rate cash flows """
        forw = (1 - D) / (D * (endTime - startTime))

        return forw

    def DiscountFactorFromDates(self, startDate, endDate, rateType):
        startTime = DateUtils.DateDifferenceInYears(self.refDate, startDate)
        endTime = DateUtils.DateDifferenceInYears(self.refDate, endDate)
        return self.DiscountFactorFromTimes(startTime, endTime, rateType)

    def DiscountFactorFromTimes(self, startTime, endTime, rateType):
        """ Computes the discount factor between two times, defaults to continuous rateType """
        T = endTime - startTime
        if startTime == 0:
            rate = self.RateFromTime(endTime)
        else:
            rate = self.ForwardRateFromTimes(startTime, endTime)

        if rateType == "Continuous":
            return math.exp(-rate * T)
        elif rateType == "Simple":
            return 1.0 / (1 + rate * T)
        elif rateType == "Annual":
            return 1.0 / pow(1 + rate, T)
        elif rateType == "Semi-Annual":
            return 1.0 / pow(1 + rate / 2.0, 2 * T)
        elif rateType == "Quarterly":
            return 1.0 / pow(1 + rate / 4.0, 4 * T)
        elif rateType == "Monthly":
            return 1.0 / pow(1 + rate / 12.0, 12 * T)

        return math.exp(-rate * T)
