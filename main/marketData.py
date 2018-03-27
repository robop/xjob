# -*- coding: utf-8 -*-
import DateUtils

today = DateUtils.DateToday()
today = DateUtils.DateObjectFromString("2018-03-19")

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

periodsOisUSD = ["1W", "2W", "3W", "1M", "2m", "3m", "4m", "5m", "6m", "9m", "1y", "18m", "2y", "3y", "4y", "5y"]
datesOisUSD = [DateUtils.DateAddDatePeriod(today, period) for period in periodsOisUSD]
oisRatesUSD = [0.51755, 0.583875, 0.603787, 0.6225877, 0.644251,
             0.658095, 0.675858, 0.691406, 0.713412, 0.786797,
             0.86502, 1.020157, 1.156512, 1.405294, 1.590032, 1.735819]
oisRatesUSD = [0.01*libor for libor in oisRatesUSD]

periodsOisJPY = ["2d", "1w", "2w", "3w", "4w", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m",
           "10m", "11m", "1y", "18m", "2y", "3y"]
datesOisJPY = [DateUtils.DateAddDatePeriod(today, period) for period in periodsOisJPY]
oisRatesJPY = [-0.024000111, -0.042666863, -0.0450004, -0.050479008, -0.055115677, -0.058860059, -0.069027324,
             -0.077153031,  -0.084227856, -0.091289929, -0.098337368, -0.10438085, -0.110417947, -0.116453151,
             -0.119499762, -0.125523156, -0.125523156, -0.16019527, -0.181629865]
oisRatesJPY = [0.01*libor for libor in oisRatesJPY]

# Volatilities
volPeriod = ["1m", "3m", "6m", "1y", "2y", "3y"]
volJPYUSD = [8.62, 8.56, 9.04, 9.48, 9.68, 9.87]
volJPYUSD = [0.01*vol for vol in volJPYUSD]
volUSDSEK = [7.99, 7.89, 8.56, 8.97, 9.35, 9.62]
volUSDSEK = [0.01*vol for vol in volUSDSEK]
volNikkei = [0.1766, 0.1771, 0.1795, 0.1790, 0.1718, 0.1684]