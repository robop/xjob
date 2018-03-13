import YieldCurve
import DateUtils
import math
import matplotlib.pyplot as plt


today = DateUtils.DateToday()
periods = ["1d", "1m", "3m", "6m", "1y", "2y", "3y", "5y"]
dates = [DateUtils.DateAddDatePeriod(today, period) for period in periods]
zeroRates = [1.458016662, 1.571972983, 1.767105779, 1.869638373, 2.044985355, 2.273314482, 2.401155174, 2.529756501]
print(dates)
print(zeroRates)

curve = YieldCurve.Curve(dates, zeroRates, "Act/365", "Cubic Spline")

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

"""Many curves, for different time steps, tar fram """
refDates = [DateUtils.DateAddDatePeriod(today, str(i) + "m") for i in range(1, 36)]
curves = [curve]
for refDate in refDates:
    futureDates = [DateUtils.DateAddDatePeriod(refDate, period) for period in periods]
    futureRates = [curve.ForwardRateFromDates(refDate, date, "Act/365") for date in futureDates]

    futureCurve = YieldCurve.Curve(futureDates, futureRates, "Act/365", "Cubic Spline", "Flat", refDate)

    curves.append(futureCurve)

print(curves[6].RateFromDate("2018-12-08"))


""""FÖR CCS"""
dates = [DateUtils.DateAddDelta(today, 0, i, 0) for i in range(1, 61)]
times = [DateUtils.DateDifferenceInYears(today, date) for date in dates]
rates = [curve.RateFromDate(date) for date in dates]

plt.plot(times, rates)
plt.show()

"""tar fram 3m forwardRate för varje period från zero coupon kurvan"""
datePeriod = "3m"
endDates = [DateUtils.DateAddDatePeriod(date, datePeriod) for date in dates]
forwRates = [curve.ForwardRateFromDates(dates[i], endDates[i]) for i in range(len(dates))]

plt.plot(times, forwRates)
plt.show()


