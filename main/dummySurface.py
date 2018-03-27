# -*- coding: utf-8 -*-
import VolatilitySurface
import DateUtils

def CreateDummySurface(date, spotPrice, volatility, name):
    strikeInter = "Linear"
    expiryInter = "Linear in Volatility"
    volSurface = VolatilitySurface.VolatilitySurface(strikeInter, expiryInter)

    strikes = [70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0]
    strikes = [0.01 * spotPrice * strike for strike in strikes]

    expiryDate = DateUtils.DateAddDatePeriod(date, "1y")
    volatilities = [volatility for i in range(7)]

    volSurface.AddSkew(strikes, volatilities, expiryDate)

    expiryDate = DateUtils.DateAddDatePeriod(date, "2y")
    volatilities = [volatility + 0.03 for i in range(7)]

    volSurface.AddSkew(strikes, volatilities, expiryDate)

    expiryDate = DateUtils.DateAddDatePeriod(date, "3y")
    volatilities = [volatility + 0.05 for i in range(7)]

    volSurface.AddSkew(strikes, volatilities, expiryDate)

    expiryDate = DateUtils.DateAddDatePeriod(date, "5y")
    volatilities = [volatility + 0.06 for i in range(7)]

    volSurface.AddSkew(strikes, volatilities, expiryDate)

    volSurface.SurfaceName(name)

    return volSurface

def createVolSurface(date, spotPrice, volatility, volPeriod, name, refDate):
    strikeInter = "Linear"
    expiryInter = "Linear in Volatility"
    volSurface = VolatilitySurface.VolatilitySurface( strikeInter, expiryInter, refDate )

    strikes = [ 70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0 ]
    strikes = [ 0.01 * spotPrice * strike for strike in strikes ]

    for i in range(len(volatility)):
        expiryDate = DateUtils.DateAddDatePeriod(date, volPeriod[i])
        volatilities = [volatility for i in range(7)]
        volSurface.AddSkew(strikes, volatilities, expiryDate)

    volSurface.SurfaceName(name)

    return volSurface