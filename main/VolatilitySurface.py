# -*- coding: utf-8 -*-
import math
import DateUtils
import Interpolation
import YieldCurve
# import OptimizationMethods

def FindPosition(point, points):
    """Determines the position of point in the vector points"""
    if point < points[0]:
        return -1

    for i in range(len(points) - 1):
        if point < points[i + 1]:
            return i

    return len(points)


class VolatilitySkew:
    def __init__(self,
                 strikes,
                 volatilities,
                 expiryDate):
        """ Just a vector of implied volatilities for a given expiry date """
        self.volatilities = volatilities
        self.strikes = strikes
        self.expiryDate = expiryDate

    def Volatility(self,
                   strike,
                   interpolation):
        if len(self.strikes) == 0:
            print("Error in interpolation, no points in skew at expiry : ", self.expiryDate)
        elif len(self.strikes) == 1:
            print("Warning: Only one point in skew, returning this value for skew at : ", self.expiryDate)
            return self.volatilities[0]
        elif len(self.strikes) == 2:
            print("Warning: Only two points in skew, using linear interpolation for skew at : ", self.expiryDate)
            return Interpolation.LinearInterpolation(strike, self.strikes, self.volatilities)

        return interpolation(strike, self.strikes, self.volatilities)

class ParametricVolatilitySkew:
    """ Implements an SVI parameterization of a volatility skew:  """
    def __init__(self,
                 strikes,
                 forward,
                 volatilities,
                 expiryDate,
                 refDate = DateUtils.DateToday()):
        self.strikes = strikes
        self.forward = forward
        self.volatilities = volatilities
        self.expiryDate = expiryDate
        self.expiryTime = DateUtils.DateDifferenceInYears(refDate, expiryDate)
        self.refDate = refDate
        self.parameters = None
        self.isCalibrated = False
        self.useArbitrageCondition = True
        self.arbitrageLimit = 0.001

        self.InitializeParameters()

    def InitializeParameters(self):
        """ Parameter order: a, b, rho, sigma, m"""
        self.parameters = [0.04, 0.04, 0.0, 0.10, 0.05]

    def GoalFunctionArbitrage(self, parameters):
        strike = parameters[0]
        a = parameters[1]
        b = parameters[2]
        rho = parameters[3]
        sigma = parameters[4]
        m = parameters[5]

        if strike <= 0.0:
            return 1e6

        k = math.log(strike / self.forward)
        h = 1.0e-4

        vol = self.VolatilityLM(strike, parameters)
        volUp = self.VolatilityLM(strike + h, parameters)
        volDw = self.VolatilityLM(strike - h, parameters)

        if vol <= 0.0:
            return 1.0

        dvdk = (volUp - volDw) / (2 * h)
        d2vdk2 = (volUp - 2 * vol + volDw) / (h * h)

        cond = (1 - k * dvdk / vol) ** 2 - 0.25 * vol * vol * dvdk * dvdk + vol * d2vdk2

        return cond

    def IsArbitrageFreeSkew(self, parameters):
        inputParams = [self.forward]
        inputParams.extend(parameters)
        index = 0
        tol = 1.0e-6
        iters = 100

        sol = OptimizationMethods.Minimize1D(self.GoalFunctionArbitrage, inputParams, index, tol, iters)

        if sol[1] > 0.0:
            return (True, sol)
        return (False, sol)

    def PenaltyFunction(self, strike, params):
        a = params[0]
        b = params[1]
        rho = params[2]
        sigma = params[3]
        m = params[4]
        k = math.log(strike / self.forward)

        km = k - m
        var = (a + b * (rho * km + math.sqrt(km * km + sigma * sigma)))

        if self.useArbitrageCondition:
            arbitrage = self.IsArbitrageFreeSkew(params)
            penalty = 0.0
            if not arbitrage[0]:
                penalty += 1000 * max(self.arbitrageLimit - arbitrage[1][1], 0.0)
        else:
            penalty = 0.0

            penalty += 1000 * (max(-var, 0.0) + max(1e-3 - sigma, 0.0) + max(-a, 0.0) + max(-b, 0.0))

        return penalty

    def GoalFunction(self, parameters):
        volatilities = []
        for index, strike in enumerate(self.strikes):
            volatility = self.VolatilityLM(strike, parameters)
            penalty = self.PenaltyFunction(strike, parameters)
            volatilities.append(volatility + penalty)

        return volatilities

    def Calibrate(self, logging = False):
        if len(self.volatilities) < 5:
            print("Error in calibration, need at least 5 points in skew. Error in skew at date : ", self.expiryDate)

        instance = OptimizationMethods.LevenbergMarquardt(self.GoalFunction, self.parameters, self.volatilities, "Central", logging)
        instance.Optimize()
        self.parameters = instance.optimum
        if logging:
            print("Calibrated skew : ", self.expiryDate, self.parameters)


    def VolatilityLM(self, strike, parameters):
        k = math.log(strike / self.forward)
        a = parameters[0]
        b = parameters[1]
        rho = parameters[2]
        sigma = parameters[3]
        m = parameters[4]
        km = k - m
        var = a + b*(rho*km + math.sqrt(km*km + sigma*sigma))

        if var < 0:
            return 0.0

        return math.sqrt(var)

    def Volatility(self, strike, logging = False):
        return self.VolatilityLM(strike, self.parameters)

class VolatilitySurface:
    def __init__(self,
                 strikeInterpolation,
                 expiryInterpolation,
                 refDate=DateUtils.DateToday()):
        self.skews = []
        self.expiryDates = []
        self.expiryTimes = []
        self.surfaceName = None

        if strikeInterpolation == "Linear":
            self.strikeInterpolation = Interpolation.LinearInterpolation
        elif strikeInterpolation == "Hermite":
            self.strikeInterpolation = Interpolation.HermiteInterpolation
        elif strikeInterpolation == "Cubic Spline":
            self.strikeInterpolation = Interpolation.CubicSplineInterpolation

        self.expiryInterpolation = expiryInterpolation
        self.refDate = refDate

    def SurfaceName(self, surfaceName=None):
        if surfaceName:
            self.surfaceName = surfaceName
        else:
            return self.surfaceName

    def AddSkew(self, strikes, volatilities, expiryDate, update=False):
        skewInSurface = False
        index = 0
        for skew in self.skews:
            if skew.expiryDate == expiryDate:
                """ In this case there is already a skew with the given expiryDate in the surface """
                skewInSurface = True
                if update:
                    volSkew = VolatilitySkew(strikes, volatilities, expiryDate)
                    expiryTime = DateUtils.DateDifferenceInYears(self.refDate, expiryDate)
                    self.skews[index] = volSkew
                    self.expiryDates[index] = expiryDate
                    self.expiryTimes[index] = expiryTime

            index += 1

        if not skewInSurface:
            volSkew = VolatilitySkew(strikes, volatilities, expiryDate)
            expiryTime = DateUtils.DateDifferenceInYears(self.refDate, expiryDate)
            self.skews.append(volSkew)
            self.expiryDates.append(expiryDate)
            self.expiryTimes.append(expiryTime)

        """ Now sort skews with respect to expiry """
        expiryTimes, expiryDates, skews = zip(*sorted(zip(self.expiryTimes, self.expiryDates, self.skews)))

        self.expiryTimes = [expiryTime for expiryTime in expiryTimes]
        self.expiryDates = [expiryDate for expiryDate in expiryDates]
        self.skews = [skew for skew in skews]

    def Volatility(self, strike, expiryDate):
        """ First find position of expiryDate, then interpolate along each skew and finally between skews """
        expiryTime = DateUtils.DateDifferenceInYears(self.refDate, expiryDate)
        index = FindPosition(expiryTime, self.expiryTimes)

        if index == -1:
            """ Interpolate along first skew """
            return self.skews[0].Volatility(strike, self.strikeInterpolation)

        elif index == len(self.skews):
            return self.skews[len(self.skews) - 1].Volatility(strike, self.strikeInterpolation)

        if self.expiryInterpolation == "Linear in Volatility":
            t1 = self.expiryTimes[index]
            t2 = self.expiryTimes[index + 1]
            vol1 = self.skews[index].Volatility(strike, self.strikeInterpolation)
            vol2 = self.skews[index + 1].Volatility(strike, self.strikeInterpolation)

            volatility = vol1 + (expiryTime - t1) * (vol2 - vol1) / (t2 - t1)

        elif self.expiryInterpolation == "Linear in Variance":
            t1 = self.expiryTimes[index]
            t2 = self.expiryTimes[index + 1]
            vol1 = self.skews[index].Volatility(strike, self.strikeInterpolation)
            vol2 = self.skews[index + 1].Volatility(strike, self.strikeInterpolation)

            variance = vol1 * vol1 * t1 + (expiryTime - t1) * (vol2 * vol2 * t2 - vol1 * vol1 * t1) / (t2 - t1)
            volatility = math.sqrt(variance / expiryTime)

        return volatility

    def VolatilityFromTime(self, strike, expiryTime):
        """ First find position of expiryDate, then interpolate along each skew and finally between skews """
        index = FindPosition(expiryTime, self.expiryTimes)

        if index == -1:
            """ Interpolate along first skew """
            return self.skews[0].Volatility(strike, self.strikeInterpolation)

        elif index == len(self.skews):
            return self.skews[len(self.skews) - 1].Volatility(strike, self.strikeInterpolation)

        if self.expiryInterpolation == "Linear in Volatility":
            t1 = self.expiryTimes[index]
            t2 = self.expiryTimes[index + 1]
            vol1 = self.skews[index].Volatility(strike, self.strikeInterpolation)
            vol2 = self.skews[index + 1].Volatility(strike, self.strikeInterpolation)

            volatility = vol1 + (expiryTime - t1) * (vol2 - vol1) / (t2 - t1)

        elif self.expiryInterpolation == "Linear in Variance":
            t1 = self.expiryTimes[index]
            t2 = self.expiryTimes[index + 1]
            vol1 = self.skews[index].Volatility(strike, self.strikeInterpolation)
            vol2 = self.skews[index + 1].Volatility(strike, self.strikeInterpolation)

            variance = vol1 * vol1 * t1 + (expiryTime - t1) * (vol2 * vol2 * t2 - vol1 * vol1 * t1) / (t2 - t1)
            volatility = math.sqrt(variance / expiryTime)

        return volatility

    def ForwardVolatility(self, strike, startDate, endDate):
        t1 = DateUtils.DateDifferenceInYears(self.refDate, startDate)
        t2 = DateUtils.DateDifferenceInYears(self.refDate, endDate)
        vol1 = self.Volatility(strike, startDate)
        vol2 = self.Volatility(strike, endDate)

        forwVol = math.sqrt((vol2 * vol2 * t2 - vol1 * vol1 * t1) / (t2 - t1))

        return forwVol

    def ForwardVolatilityFromTimes(self, strike, t1, t2):
        vol1 = self.VolatilityFromTime(strike, t1)
        vol2 = self.VolatilityFromTime(strike, t2)

        forwVol = math.sqrt((vol2 * vol2 * t2 - vol1 * vol1 * t1) / (t2 - t1))

        return forwVol


class ParametricVolatilitySurface:
    """ If used for FX: reference curve is domestic yield curve and dividend curve is foreign yield curve """
    def __init__(self,
                 spotValue,
                 expiryInterpolation,
                 referenceCurve,
                 dividendCurve,
                 refDate=DateUtils.DateToday()):
        self.skews = []
        self.expiryDates = []
        self.expiryTimes = []
        self.spotValue = spotValue
        self.expiryInterpolation = expiryInterpolation
        self.referenceCurve = referenceCurve
        self.dividendCurve = dividendCurve
        self.refDate = refDate

    def AddSkew(self, strikes, volatilities, expiryDate, update=False):
        skewInSurface = False
        expiryTime = DateUtils.DateDifferenceInYears(self.refDate, expiryDate)
        refRate = self.referenceCurve.RateFromTime(expiryTime)
        divRate = self.dividendCurve.RateFromTime(expiryTime)
        forward = self.spotValue*math.exp((refRate - divRate)*expiryTime)
        index = 0
        for skew in self.skews:
            if skew.expiryDate == expiryDate:
                """ In this case there is already a skew with the given expiryDate in the surface """
                skewInSurface = True
                if update:
                    volSkew = ParametricVolatilitySkew(strikes, forward, volatilities, expiryDate, self.refDate)
                    volSkew.Calibrate()

                    self.skews[index] = volSkew
                    self.expiryDates[index] = expiryDate
                    self.expiryTimes[index] = expiryTime

            index += 1

        if not skewInSurface:
            volSkew = ParametricVolatilitySkew(strikes, forward, volatilities, expiryDate, self.refDate)
            volSkew.Calibrate()

            self.skews.append(volSkew)
            self.expiryDates.append(expiryDate)
            self.expiryTimes.append(expiryTime)

        """ Now sort the skews with respect to expiry """
        expiryTimes, expiryDates, skews = zip(*sorted(zip(self.expiryTimes, self.expiryDates, self.skews)))

        self.expiryTimes = [expiryTime for expiryTime in expiryTimes]
        self.expiryDates = [expiryDate for expiryDate in expiryDates]
        self.skews = [skew for skew in skews]

    def Volatility(self, strike, expiryDate):
        """ First find position of expiryDate, then interpolate along each skew and finally between skews """
        expiryTime = DateUtils.DateDifferenceInYears(self.refDate, expiryDate)
        index = FindPosition(expiryTime, self.expiryTimes)

        if index == -1:
            if self.expiryInterpolation == "Linear in Volatility":
                """ Interpolate along first skew and use flat extrapolation """
                return self.skews[0].Volatility(strike)
            elif self.expiryInterpolation == "Linear in Variance":
                """ Interpolate along first skew and use flat extrapolation """
                vol1 = self.skews[0].Volatility(strike)
                return vol1*math.sqrt(self.expiryTimes[0]/expiryTime)

        elif index == len(self.skews):
            if self.expiryInterpolation == "Linear in Volatility":
                """ Interpolate along last skew and use flat extrapolation """
                return self.skews[-1].Volatility(strike)
            elif self.expiryInterpolation == "Linear in Variance":
                """ Interpolate along last skew and use flat extrapolation """
                volN = self.skews[-1].Volatility(strike)
                return volN * math.sqrt(self.expiryTimes[-1] / expiryTime)

        if self.expiryInterpolation == "Linear in Volatility":
            t1 = self.expiryTimes[index]
            t2 = self.expiryTimes[index + 1]
            vol1 = self.skews[index].Volatility(strike)
            vol2 = self.skews[index + 1].Volatility(strike)

            volatility = vol1 + (expiryTime - t1) * (vol2 - vol1) / (t2 - t1)

        elif self.expiryInterpolation == "Linear in Variance":
            t1 = self.expiryTimes[index]
            t2 = self.expiryTimes[index + 1]
            vol1 = self.skews[index].Volatility(strike)
            vol2 = self.skews[index + 1].Volatility(strike)

            variance = vol1 * vol1 * t1 + (expiryTime - t1) * (vol2 * vol2 * t2 - vol1 * vol1 * t1) / (t2 - t1)
            volatility = math.sqrt(variance / expiryTime)

        return volatility

    def Variance(self, strike, expiryTime):
        """ used for the local volatility function """
        index = FindPosition(expiryTime, self.expiryTimes)

        if index == -1:
            vol1 = self.skews[0].Volatility(strike)
            return vol1 * math.sqrt(self.expiryTimes[0] / expiryTime)

        elif index == len(self.skews):
            volN = self.skews[-1].Volatility(strike)
            return volN * math.sqrt(self.expiryTimes[-1] / expiryTime)

        t1 = self.expiryTimes[index]
        t2 = self.expiryTimes[index + 1]
        vol1 = self.skews[index].Volatility(strike)
        vol2 = self.skews[index + 1].Volatility(strike)

        variance = vol1 * vol1 * t1 + (expiryTime - t1) * (vol2 * vol2 * t2 - vol1 * vol1 * t1) / (t2 - t1)

        return variance

    def ForwardVolatility(self, strike, startDate, endDate):
        t1 = DateUtils.DateDifferenceInYears(self.refDate, startDate)
        t2 = DateUtils.DateDifferenceInYears(self.refDate, endDate)
        vol1 = self.Volatility(strike, startDate)
        vol2 = self.Volatility(strike, endDate)

        forwVol = math.sqrt((vol2 * vol2 * t2 - vol1 * vol1 * t1) / (t2 - t1))

        return forwVol

    def LocalVolatility(self, strike, expiryTime, h = 1.0e-5):
        """ TODO """
        return 0.0

def TestVolatilitySurface():
    """ Function designed to test whether the ordinary volatility surface works as well as an example """
    today = DateUtils.DateToday()
    strikeInterpolation = Interpolation.CubicSplineInterpolation
    expiryInterpolation = "Linear in Variance"
    volSurface = VolatilitySurface(strikeInterpolation, expiryInterpolation, today)

    strikes = [70.0, 80.0, 90.0, 100.0, 110.0, 120.0, 130.0]
    expiryDate = DateUtils.DateAddDatePeriod(today, "1y")
    volatilities = [0.01*(25 + (10 - 0.2 * i * i)) for i in range(7)]

    volSurface.AddSkew(strikes, volatilities, expiryDate)

    expiryDate = DateUtils.DateAddDatePeriod(today, "2y")
    volatilities = [0.01*(24 + (10 - 0.18 * i * i)) for i in range(7)]

    volSurface.AddSkew(strikes, volatilities, expiryDate)

    expiryDate = DateUtils.DateAddDatePeriod(today, "3y")
    volatilities = [0.01*(23 + (10 - 0.15 * i * i)) for i in range(7)]

    volSurface.AddSkew(strikes, volatilities, expiryDate)

    matrix = []
    for i in range(40):
        expiryDate = DateUtils.DateAddDatePeriod(today, str(i) + "m")
        row = []
        for j in range(13):
            strike = 70.0 + 5.0 * j
            volatility = volSurface.Volatility(strike, expiryDate)
            row.append(volatility)

        matrix.append(row)

    for row in matrix:
        for element in row:
            print(str(element).replace(".", ",") + "\t", end="")
        print("")

def TestParametricVolatilitySurface():
    """ Function designed to test whether the SVI surface with calibration works as well as an example """
    today = DateUtils.DateToday()
    spotValue = 100.0
    expiryInterpolation = "Linear in Variance"
    referenceRates = [0.01, 0.015, 0.018, 0.020, 0.021]
    dividendRates = [0.001, 0.003, 0.004, 0.005, 0.0055]
    referenceDates = [DateUtils.DateAddDatePeriod(today, str(i) + "y") for i in range(1, 6)]
    dividendDates = [DateUtils.DateAddDatePeriod(today, str(i) + "y") for i in range(1, 6)]
    referenceCurve = YieldCurve.Curve(referenceDates, referenceRates, "Act/365", "Cubic Spline", "Flat", today)
    dividendCurve = YieldCurve.Curve(dividendDates, dividendRates, "Act/365", "Cubic Spline", "Flat", today)
    volSurface = ParametricVolatilitySurface(spotValue, expiryInterpolation, referenceCurve, dividendCurve, today)

    """ Testing: Create volatilities with given values of SVI parameters, then calibrate to these to see if
        we recover the parameters. For robustness, try adding noise and then comparing. """
    import random
    def Volatility(forward, strike, parameters):
        k = math.log(strike / forward)
        a = parameters[0]
        b = parameters[1]
        rho = parameters[2]
        sigma = parameters[3]
        m = parameters[4]
        km = k - m
        var = a + b * (rho * km + math.sqrt(km * km + sigma * sigma))

        if var < 0:
            print("-" * 100)
            print("Negative Variance in SVI Volatility Skew :", var)
            print("Invalid Parameters in SVI volatility skew  :", parameters)
            print("Expiry Date :", expiryDate)
            print("Strike : ", strike)
            print("Returning 0.0")
            print("-"*100)

            return 0.0
        """ 2% potential deviation, positive volatilties in the examples below """
        return math.sqrt(var) + 0.02*random.uniform(-1, 1)

    strikes = [30.0 + 5.0*i for i in range(29)]
    volDict = {}

    expiryDate = DateUtils.DateAddDatePeriod(today, "1y")
    refRate = referenceCurve.RateFromDate(expiryDate)
    divRate = dividendCurve.RateFromDate(expiryDate)
    expiryTime = DateUtils.DateDifferenceInYears(today, expiryDate)
    forward = spotValue*math.exp((refRate - divRate)*expiryTime)
    parameters = [0.06, 0.05, -0.3, 0.12, 0.07]
    volatilities = [Volatility(forward, strike, parameters) for strike in strikes]
    volDict[expiryDate] = volatilities

    volSurface.AddSkew(strikes, volatilities, expiryDate)

    expiryDate = DateUtils.DateAddDatePeriod(today, "2y")
    refRate = referenceCurve.RateFromDate(expiryDate)
    divRate = dividendCurve.RateFromDate(expiryDate)
    expiryTime = DateUtils.DateDifferenceInYears(today, expiryDate)
    forward = spotValue * math.exp((refRate - divRate) * expiryTime)
    parameters = [0.07, 0.06, -0.33, 0.11, 0.06]
    volatilities = [Volatility(forward, strike, parameters) for strike in strikes]
    volDict[expiryDate] = volatilities

    volSurface.AddSkew(strikes, volatilities, expiryDate)

    expiryDate = DateUtils.DateAddDatePeriod(today, "10y")
    refRate = referenceCurve.RateFromDate(expiryDate)
    divRate = dividendCurve.RateFromDate(expiryDate)
    expiryTime = DateUtils.DateDifferenceInYears(today, expiryDate)
    forward = spotValue * math.exp((refRate - divRate) * expiryTime)
    parameters = [0.08, 0.07, -0.35, 0.10, 0.03]
    volatilities = [Volatility(forward, strike, parameters) for strike in strikes]
    volDict[expiryDate] = volatilities

    volSurface.AddSkew(strikes, volatilities, expiryDate)

    for skew in volSurface.skews:
        print("Expiry\ta\tb\trho\tsigma\tm")
        print(skew.expiryDate, "\t", end="")
        for p in skew.parameters:
            print(str(p).replace(".", ",") + "\t", end="")
        print("\n")
        print("Strike\tModel\tMarket\Diff")

        for index, strike in enumerate(strikes):
            sviVol = skew.Volatility(strike)
            vol = volDict[skew.expiryDate][index]
            strikeStr = str(strike).replace(".", ",")
            sviStr = str(sviVol).replace(".", ",")
            volStr = str(vol).replace(".", ",")
            diffStr = str(sviVol - vol).replace(".", ",")
            printStr = strikeStr + "\t" + sviStr + "\t" + volStr + "\t" + diffStr

            print(printStr)


#TestVolatilitySurface()
#TestParametricVolatilitySurface()






