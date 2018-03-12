import YieldCurve
import DateUtils
import math

today = DateUtils.DateToday()
periods = ["1d", "1m", "3m", "6m", "1y", "2y", "3y", "5y"]
dates = [DateUtils.DateAddDatePeriod(today, period) for period in periods]
rates = [0.03 - 0.02 * math.exp(-0.1 * i * i) for i in range(len(dates))]
print(dates)
print(rates)

curve = YieldCurve.Curve(dates, rates, "Act/365", "Cubic Spline")

""" Examples """
print(curve.RateFromDate("2018-09-08"))
print(curve.ForwardRateFromDates("2018-09-08", "2018-12-08", "Act/365"))

""" What does the (expected) curve look like in 6m"""
refDate = "2018-09-08"
futureDates = [DateUtils.DateAddDatePeriod(refDate, period) for period in periods]
futureRates = [curve.ForwardRateFromDates(refDate, date, "Act/365") for date in futureDates]

print(futureDates)
print(futureRates)

futureCurve = YieldCurve.Curve(futureDates, futureRates, "Act/365", "Cubic Spline", "Flat", refDate)

print(curve.ForwardRateFromDates("2018-09-08", "2018-12-08", "Act/365"))
print(futureCurve.RateFromDate("2018-12-08"))

rate = futureCurve.RateFromDate("2018-12-08")
t = DateUtils.DateDifferenceInYears("2018-09-08", "2018-12-08")
t360 = DateUtils.GetPeriodLength("2018-09-08", "2018-12-08", "30/360")
print(t, t360)
disc = math.exp(-rate * t)
print(disc)

"""Many curves, for different time steps"""
refDates = [DateUtils.DateAddDatePeriod(today, str(i) + "m") for i in range(1, 37)]
curves = [curve]
for refDate in refDates:
    futureDates = [DateUtils.DateAddDatePeriod(refDate, period) for period in periods]
    futureRates = [curve.ForwardRateFromDates(refDate, date, "Act/365") for date in futureDates]

    futureCurve = YieldCurve.Curve(futureDates, futureRates, "Act/365", "Cubic Spline", "Flat", refDate)

    curves.append(futureCurve)

print(curves[6].RateFromDate("2018-12-08"))