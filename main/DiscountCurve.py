import math
import DateUtils
import Interpolation

class Dcurve:
    def __init__(self, \
                 dates: object, \
                 rates: object, \
                 dayCount: object = "Act/365", \
                 interpolation: object = "Hermite", \
                 extrapolation: object = "Flat", \
                 refDate: object = DateUtils.DateToday( ) \
                 ) -> object:
        self.dates = dates
        self.points = [ ]
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

        self.ConvertDatesToTimes( )

    def CurveDate(self, refDate=None):
        if refDate:
            self.refDate = refDate
        else:
            return self.refDate

    def ConvertDatesToTimes(self):
        self.points = []
        for date in self.dates:
            timePoint = DateUtils.GetPeriodLength(self.refDate, date, self.dayCount)[1]
            self.points.append(timePoint)

    def DiscountFromDate(self, date):
        T = DateUtils.GetPeriodLength( self.refDate, date, self.dayCount )[ 1 ]
        return self.DiscountFromTime( T )

    def DiscountFromTime(self, point):
        rateDiscount = self.inter(point, self.points, self.rates, self.extra, self.extra)
        return math.exp(- rateDiscount * point) # T ovan blir point här

    def RateFromTime(self, point):
        rate = self.inter( point, self.points, self.rates, self.extra, self.extra )
        return rate