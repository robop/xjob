import YieldCurve
import DateUtils
import math
import matplotlib.pyplot as plt
import CCS
import DiscountCurve



today = DateUtils.DateToday()
periods = ["2d", "1W", "1M", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "10m",
           "11m", "1y", "18m", "2y", "30m", "3y", "42m", "4y", "54m", "5y"]
dates = [DateUtils.DateAddDatePeriod(today, period) for period in periods]
liborUSD = [1.466307352, 1.611028226, 1.82414815, 1.942546091, 2.209907775, 2.138366588, 2.147367374,
            2.279009258, 2.241523629, 2.24420776, 2.333095078, 2.311442062,
            2.318825528, 2.387899894, 2.478840538, 2.581486224, 2.637993327,
            2.684525384, 2.711493379, 2.737739199, 2.752751009, 2.768888473]
liborUSD = [0.01*libor for libor in liborUSD]

periodsOisSEK = ["1d", "1m", "2m", "3m", "6m", "9m", "1y", "18m", "2y", "3y", "4y", "5y"]
datesOisSEK = [DateUtils.DateAddDatePeriod(today, period) for period in periodsOisSEK]
oisRatesSEK = [-0.265195519, -0.515237009, -0.518146377, -0.556769207, -0.551247941, -0.571856724,
               -0.577879729, -0.559908694, -0.519926627, -0.41376262, -0.255675858, -0.105256406]
oisRatesSEK = [0.01*libor for libor in oisRatesSEK]

periodsOis = ["1W", "2W", "3W", "1M", "2m", "3m", "4m", "5m", "6m", "9m", "1y", "18m", "2y", "3y", "4y", "5y"]
datesOisUSD = [DateUtils.DateAddDatePeriod(today, period) for period in periodsOis]
oisRatesUSD = [0.51755, 0.583875, 0.603787, 0.6225877, 0.644251,
             0.658095, 0.675858, 0.691406, 0.713412, 0.786797,
             0.86502, 1.020157, 1.156512, 1.405294, 1.590032, 1.735819]
oisRatesUSD = [0.01*libor for libor in oisRatesUSD]


forwardCurve = YieldCurve.Curve(dates, liborUSD, "Act/365", "Linear")
#discCurve = DiscountCurve.Dcurve(dates, liborUSD, "Act/365", "Linear")
discCurveUSD = DiscountCurve.Dcurve(datesOisUSD, oisRatesUSD, "Act/365", "Linear")
discCurveSEK = DiscountCurve.Dcurve(datesOisSEK,oisRatesSEK, "Act/365", "Linear")

""" Examples """
# print(forwardCurve.RateFromDate("2018-09-08"))
# print("Forward")
# print(forwardCurve.ForwardRateFromDates("2018-09-08", "2018-12-08", "Act/365"))
# print("slut")
# print(forwardCurve.ForwardRateFromDates("2018-09-08", "2023-09-08", "Act/365"))
# """ What does the (expected) forwardCurve look like in 6m"""
# refDate = "2018-09-08"
# futureDates = [DateUtils.DateAddDatePeriod(refDate, period) for period in periods]
# futureRates = [forwardCurve.ForwardRateFromDates(refDate, date, "Act/365") for date in futureDates]
#
# print(futureDates)
# print(futureRates)
#
# futureCurve = YieldCurve.Curve(futureDates, futureRates, "Act/365", "Cubic Spline", "Flat", refDate)
#
# print(forwardCurve.ForwardRateFromDates("2018-09-08", "2018-12-08", "Act/365"))
# print(futureCurve.RateFromDate("2018-12-08"))
#
# rate = futureCurve.RateFromDate("2018-12-08")
# t = DateUtils.DateDifferenceInYears("2018-09-08", "2018-12-08")
# t360 = DateUtils.GetPeriodLength("2018-09-08", "2018-12-08", "30/360")
# print(t, t360)
# disc = math.exp(-rate * t)
# print(disc)
#
# """Many curves, for different time steps, tar fram """
# refDates = [DateUtils.DateAddDatePeriod(today, str(i) + "m") for i in range(1, 36)]
# curves = [forwardCurve]
# for refDate in refDates:
#     futureDates = [DateUtils.DateAddDatePeriod(refDate, period) for period in periods]
#     futureRates = [forwardCurve.ForwardRateFromDates(refDate, date, "Act/365") for date in futureDates]
#
#     futureCurve = YieldCurve.Curve(futureDates, futureRates, "Act/365", "Cubic Spline", "Flat", refDate)
#
#     curves.append(futureCurve)
#
# print(curves[6].RateFromDate("2018-12-08"))
#

""""FÖR CCS"""
dates = [DateUtils.DateAddDelta(today, 0, i, 0) for i in range(1, 61, 3)] # 60 mån = 5 år, ökar datum med 1 M intervall
times = [DateUtils.DateDifferenceInYears(today, date) for date in dates] # tar fram tidsskillnad i år för
rates = [forwardCurve.RateFromDate(date) for date in dates] # tar fram räntorna
ratesUSD = [discCurveUSD.DiscountFromDate(date) for date in dates] # tar fram räntorna
ratesSEK = [discCurveSEK.DiscountFromDate(date) for date in dates] # tar fram räntorna


plt.plot(times, rates)
plt.show()

"""tar fram 3m forwardRate för varje period från zero coupon kurvan"""
datePeriod = "3m"
endDates = [DateUtils.DateAddDatePeriod(date, datePeriod) for date in dates]
forwRates = [forwardCurve.ForwardRateFromDates(dates[i], endDates[i]) for i in range(len(dates))]
#discRates = [discCurve.DiscountFromDate(dates[i], endDates[i]) for i in range(len(dates))]

crossSwap = CCS.CCS(1, dates[0], dates[-1], -0.0, "3m", "SEK")

CCSPV = crossSwap.PresentValue(discCurveUSD, forwardCurve, 1, discCurveSEK, 0.03) # Räntan
print(CCSPV)
plt.plot(times, forwRates)
plt.show()

# TODO: Utveckla CCS mot strukturerad