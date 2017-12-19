"""First the Black-Scholes formula as a benchmark for Monte Carlo valuation of a european vanilla option.
The Black-Scholes formula"""

from random import normalvariate
from math import exp, sqrt, log


"""Approximation of the Normal Distribution"""

def N(x):

    y = abs(x)
    if y > 37:
        nd = 0
    else:
        e = exp(-y * y / 2.0)
        if y < 7.07106781186547:
            sumA = 0.0352624965998911 * y + 0.700383064443688
            sumA = sumA * y + 6.37396220353165
            sumA = sumA * y + 33.912866078383
            sumA = sumA * y + 112.079291497871
            sumA = sumA * y + 221.213596169931
            sumA = sumA * y + 220.206867912376
            sumB = 0.0883883476483184 * y + 1.75566716318264
            sumB = sumB * y + 16.064177579207
            sumB = sumB * y + 86.7807322029461
            sumB = sumB * y + 296.564248779674
            sumB = sumB * y + 637.333633378831
            sumB = sumB * y + 793.826512519948
            sumB = sumB * y + 440.413735824752
            nd = e * sumA / sumB
        else:
            sumA = y + 0.65
            sumA = y + 4.0 / sumA
            sumA = y + 3.0 / sumA
            sumA = y + 2.0 / sumA
            sumA = y + 1.0 / sumA
            nd = e / (sumA * 2.506628274631)
    if x > 0:
        nd = 1.0 - nd
    return nd


"""Black-Scholes formula"""
def BlackScholes(S0, K, T, r, d, sigma, isCall):
    # Parameter for switching between call and put: isCall = True => callPut = 1, isCall = False => callPut = -1
    callPut = 2 * isCall - 1
    # Forward value: Compounding
    forward = S0 * exp((r - d) * T)

    # Black-Scholes solution
    d1 = (log(forward / K) + 0.5 * sigma * sigma * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    result = callPut * exp(-r * T) * (forward * N(callPut * d1) - K * N(callPut * d2))

    return result


"""Testa olika värden på parametrarna."""
def TestBlackScholesFormula():
    """ The parameters here should return a value of 16.7341... """
    S0 = 100.0
    K = 100.0
    isCall = True
    r = 0.1
    d = 0.0
    sigma = 0.3
    T = 1.0

    analytical = BlackScholes(S0, K, T, r, d, sigma, isCall)
    print(analytical)

TestBlackScholesFormula()


"""Python function for generating a random walk"""
def MonteCarloPath(S0, sigma, r, d, timePoints, nt):
    # Path starts at time timePoints[0] = 0, for each time step we append the simulated index level
    St = S0
    path = [St]
    det = r - d - 0.5 * sigma * sigma
    for i in range(nt - 1):
        # Get time step dt and a standard normal random variable
        dt = timePoints[i + 1] - timePoints[i]
        rand = normalvariate(0.0, 1.0)

        # Solution to Black-Scholes SDE
        St = St * exp(det * dt + sigma * sqrt(dt) * rand)
        path.append(St)

    return path

"""A simple test
#Let us test the above function: We do a few iterations,
# that give different outcomes since we do not specify a seed for the random number generator at each iteration"""
def TestRandomWalk():
    S0 = 100.0
    sigma = 0.3
    r = 0.1
    d = 0.0
    timePoints = [0.0, 0.5, 1.0, 1.5, 2.0]
    nt = len(timePoints)

    path = MonteCarloPath(S0, sigma, r, d, timePoints, nt)

    print(path)


for i in range(5):
    TestRandomWalk()


"""Example payoff for a european vanilla option: Only one cashflow at expiry"""
def VanillaPayoff(path, parameters):
    # Extraxt contract parameters
    strikePrice = parameters[0]
    isCall = parameters[1]
    cfIndex = parameters[2]

    # Find index level at expiry/maturity: In this case at the only cash flow time indicated by cfIndex
    ST = path[cfIndex]
    callPut = 2 * isCall - 1

    # Payoff of a vanilla option: Return an array of cashflows and cashflow times (in this case one at expiry)
    cashFlows = [[max(callPut * (ST - strikePrice), 0.0), cfIndex]]
    result = {"CashFlows": cashFlows, "KO Index": cfIndex, "KO Pos": 0}

    return result


def NikkeiLinkedNotePayoff(path, parameters):
    nominal = parameters[0]  # The amount invested
    initial = parameters[1]  # The initial index level
    knockOut = parameters[2]  # knock out level: 105% = 1.05
    knockIn = parameters[3]  # knock in level :  65% = 0.65
    highRate = parameters[4]  # For example:       4% = 0.04
    lowRate = parameters[5]  # For example:     0.1% = 0.001
    strike = parameters[6]  # strike level:     85% = 0.85
    intervals = parameters[7]  # The lengths of the cash flow periods in years
    cfIndices = parameters[8]  # the indices of cashflow time points

    # Check if the contract has been knocked in: We simulate the path for all dates so we just take the minimum
    strike = strike * initial
    knockIn = knockIn * initial
    knockOut = knockOut * initial
    isKnockIn = (min(path) < knockIn)

    # Loop over the cash flow dates
    cashFlows = []
    isKnockOut = False
    index = 0
    koIndex = cfIndices[-1]
    koPos = len(cfIndices) - 1
    for cfIndex in cfIndices:
        St = path[cfIndex]
        if not isKnockOut:
            if St >= strike:
                cashFlows.append([nominal * intervals[index] * highRate, cfIndex])
            else:
                cashFlows.append([nominal * intervals[index] * lowRate, cfIndex])
            if St >= knockOut:
                """ We add the nominal cash flow to the position of 'index' """
                cashFlows[index][0] += nominal
                isKnockOut = True
                koIndex = cfIndex
                koPos = index
        else:
            cashFlows.append([0.0, cfIndex])

        index += 1

    if not isKnockOut:
        #  In this case the investment amount ha still not been repaid: cfIndex is the last of cfIndices (hence the -1)
        cfIndex = cfIndices[-1]
        ST = path[cfIndex]
        pos = len(cfIndices) - 1
        if isKnockIn:
            cashFlows[pos][0] += nominal * min(ST / initial, 1.0)
        else:
            cashFlows[pos][0] += nominal

    # print(S0, S0*1.05, S0*0.85, S0*0.65, min(path))
    # print([path[index] for index in cfIndices])
    # print(cashFlows)

    result = {"CashFlows": cashFlows, "KO Index": koIndex, "KO Pos": koPos}
    return result

"""Testing the payoff functions"""
def TestVanillaPayoff():
    S0 = 100.0
    K = 100.0
    isCall = True
    sigma = 0.3
    r = 0.1
    d = 0.0
    timePoints = [0.0, 0.5, 1.0, 1.5, 2.0]
    nt = len(timePoints)
    cfIndex = nt - 1  # A vanilla option only has one cash flow, the one at expiry = last index of the timePoints array.
    parameters = [K, isCall, cfIndex]
    path = MonteCarloPath(S0, sigma, r, d, timePoints, nt)

    print(path)

    payOff = VanillaPayoff(path, parameters)

    print(payOff)


for i in range(5):
    TestVanillaPayoff()


def TestStructurePayoff():
    nominal = 1e9
    initial = 17900.0
    S0 = 18000.0
    knockOut = 1.05
    knockIn = 0.65
    highRate = 0.04
    lowRate = 0.001
    strike = 0.85
    r = 0.01
    d = 0.00
    sigma = 0.15
    dt = 1.0 / 365
    timePoints = [i * dt for i in range(3 * 365 + 1)]
    nt = len(timePoints)
    cfIndices = [182, 365, 365 + 182, 2 * 365, 2 * 365 + 182, 3 * 365]
    intervals = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    parameters = [nominal, initial, knockOut, knockIn, highRate, lowRate, strike, intervals, cfIndices]

    path = MonteCarloPath(S0, sigma, r, d, timePoints, nt)

    # We do not really want to print the path in this case
    # print(path)

    payOff = NikkeiLinkedNotePayoff(path, parameters)

    print(payOff)


for i in range(5):
    TestStructurePayoff()

"""The monte Carlo function"""


def MonteCarlo(S0, sigma, r, d, timePoints, payOffFunction, parameters, nSim):
    theor = 0.0
    nt = len(timePoints)
    remainLife = 0.0
    for i in range(nSim):
        # Simulate path and calculate contract value: Payoff returns an array of cashflows
        path = MonteCarloPath(S0, sigma, r, d, timePoints, nt)
        result = payOffFunction(path, parameters)
        cashFlows = result["CashFlows"]
        koIndex = result["KO Index"]
        koPos = result["KO Pos"]
        remainLife += timePoints[koIndex]

        # Initilize array for knockout probabilities
        if i == 0:
            koProb = [0.0 for cf in cashFlows]
            cfs = [0.0 for cf in cashFlows]
            cfPVs = [0.0 for cf in cashFlows]

        koProb[koPos] += 1.0
        pv = 0.0
        index = 0
        for cashFlow in cashFlows:
            # For each cash flow we have the cash flow value and the index of when it occurs in the timePoints array
            cfValue = cashFlow[0]
            cfIndex = cashFlow[1]
            cfTime = timePoints[cfIndex]

            # Discount the cash flow and add to payoff: Assuming a constant discount rate
            cfPV = cfValue * exp(-r * cfTime)
            pv += cfPV

            # Accumulate the total cashflows and their PVs
            cfs[index] += cfValue
            cfPVs[index] += cfPV

            index += 1

        # Add to the result of previous simulations (cfs and cfs have an extra nominal cash flow which must be moved)
        theor += pv

    # Take the average
    result = {}
    result["Theoretical Value"] = theor / nSim
    result["Remaining Life"] = remainLife / nSim
    result["KO Probability"] = [prob / nSim for prob in koProb]
    result["Cash Flows"] = [cf / nSim for cf in cfs]
    result["Cash Flow PVs"] = [cfPV / nSim for cfPV in cfPVs]

    return result

"""Here is an example of how to use the Monte Carlo Function together with a vanilla option payoff"""


def VanillaOptionTest():
    S0 = 100.0
    K = 100.0
    isCall = True
    r = 0.1
    d = 0.0
    sigma = 0.3
    T = 1.0
    timePoints = [0.0, T]  # Only time now and at expiry
    cfIndex = len(timePoints) - 1  # This is the final point in the path
    parameters = [K, isCall, cfIndex]
    nSim = 1000000
    payOff = VanillaPayoff

    analytical = BlackScholes(S0, K, T, r, d, sigma, isCall)
    monteCarlo = MonteCarlo(S0, sigma, r, d, timePoints, payOff, parameters, nSim)

    print("Analytical  : ", analytical)
    print("Monte Carlo : ", monteCarlo)


VanillaOptionTest()

"""Here is an example of how to use the Monte Carlo function with a Nikkei linked note payoff.
Notice that the Cash Flows are the approximate expected cash flows and are close to weighting the
Theoretical Value with knock-out probabilities at different knock-out dates.
We assume that there are cash flows every 0.5 years and that the 0.5 years is 182 or 183 days (not accounting for leap years)"""


def StructuredNoteTest():
    nominal = 1e9
    initial = 17900.0
    S0 = 18000.0
    knockOut = 1.05
    knockIn = 0.65
    highRate = 0.04
    lowRate = 0.001
    strike = 0.85
    r = 0.01
    d = 0.00
    sigma = 0.15
    dt = 1.0 / 365
    timePoints = [i * dt for i in range(3 * 365 + 1)]
    cfIndices = [182, 365, 365 + 182, 2 * 365, 2 * 365 + 182,
                 3 * 365]  # Approximate indices of cash flows in the array timePoints
    intervals = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]  # Cash flows each 6 months
    parameters = [nominal, initial, knockOut, knockIn, highRate, lowRate, strike, intervals, cfIndices]

    payOff = NikkeiLinkedNotePayoff
    nSim = 10000

    monteCarlo = MonteCarlo(S0, sigma, r, d, timePoints, payOff, parameters, nSim)

    for key in monteCarlo.keys():
        print(key, monteCarlo[key])
        if key in ["Cash Flows", "Cash Flow PVs", "KO Probability"]:
            """ A simple check that the arrays sum up to the correct number """
            print("SUM(" + key + ") : ", sum(monteCarlo[key]))


StructuredNoteTest()

"""Interpolation Function"""


def FindPosition(point, points):
    """Determines the position of point in the vector points"""
    if point < points[0]:
        return -1

    for i in range(len(points) - 1):
        if point < points[i + 1]:
            return i

    return len(points)


def LinearInterpolation(point, points, values):
    """LinearInterpolation(point, points, values)"""
    n = len(points)
    i = FindPosition(point, points)
    if i == -1:
        return values[0]

    elif i == len(values):
        return values[len(values) - 1]

    coeff = (values[i + 1] - values[i]) / (points[i + 1] - points[i])
    value = values[i] + (point - points[i]) * coeff

    return value

"""Discount Factor and Forward Rate Calculation"""


def ForwardRate(timePoints, rates, timeStart, timeEnd):
    """ Interpolate rates """
    rateStart = LinearInterpolation(timeStart, timePoints, rates)
    rateEnd = LinearInterpolation(timeEnd, timePoints, rates)

    """ Calculate discount factors """
    discStart = exp(-rateStart * timeStart)
    discEnd = exp(-rateEnd * timeEnd)

    """ Forward discount factor and forward rate"""
    dForw = discEnd / discStart
    dt = timeEnd - timeStart
    forw = (1.0 - dForw) / (dt * dForw)

    return forw


class FloatingRateNote:
    def __init__(self, nominal, maturityTime, cashFlowTimes, spread):
        """ Assuming that cash flow times and maturity are with respect to today and today is the start date.
            A real FRN valuation would include start date, maturity date, cash flow period, business date adjustments
            and a day count method.
        """
        self.nominal = nominal
        self.maturityTime = maturityTime
        self.cashFlowTimes = cashFlowTimes
        self.spread = spread

    def PresentValue(self, timePoints, rates):
        pv = 0.0
        nCF = len(self.cashFlowTimes)

        for iCF in range(nCF):
            if iCF == 0:
                # Assuming today is time t = 0.0 and cashFlowTimes[0] is the time to the first cash flow
                t0 = 0.0
                t1 = self.cashFlowTimes[iCF]
            else:
                # A forward starting time period
                t0 = self.cashFlowTimes[iCF - 1]
                t1 = self.cashFlowTimes[iCF]

            dt = t1 - t0
            F = ForwardRate(timePoints, rates, t0, t1)

            rate = LinearInterpolation(t1, timePoints, rates)
            disc = exp(-rate * t1)

            """ Cash flow """
            pv += self.nominal * (F + self.spread) * dt * disc

        """ Final repayment of nominal: Note that after the loop above the discount factor will be the one for maturity
            as this is the last cash flow time.
        """
        pv += self.nominal * disc

        return pv

"""Testing FRN Valuation"""


def TestValuationFRN():
    timePoints = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    rates = [0.01, 0.015, 0.018, 0.2, 0.21, 0.215, 0.218, 2.20]
    nominal = 1e9
    maturityTime = 3.0
    cashFlowTimes = [0.25 * i for i in range(1, 13)]
    spread = -0.0040
    frn = FloatingRateNote(nominal, maturityTime, cashFlowTimes, spread)

    theor = frn.PresentValue(timePoints, rates)

    print(theor)


TestValuationFRN()

"""Testing Structured Swap Valuation"""


def StructuredSwapTest():
    """ We assume an interest rate curve even if it is not used in the valuation of the structured swap """
    rateTimes = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    ratesUSD = [0.01, 0.015, 0.018, 0.02, 0.021, 0.0215, 0.0218, 0.0220]
    ratesJPY = [0.00, 0.005, 0.008, 0.01, 0.015, 0.018, 0.02, 0.021]

    nominalJPY = 1e9
    nominalUSD = nominalJPY / 112.5
    fxRate = 112.5  # An approximate made up raate between JPY and USD
    initial = 18000.0
    S0 = 17200.0
    knockOut = 1.05
    knockIn = 0.65
    highRate = 0.04
    lowRate = 0.001
    strike = 0.85
    T = 3.0
    r = LinearInterpolation(T, rateTimes, ratesJPY)
    d = 0.00
    sigma = 0.15
    dt = 1.0 / 365
    timePoints = [i * dt for i in range(3 * 365 + 1)]
    cfIndices = [182, 365, 365 + 182, 2 * 365, 2 * 365 + 182,
                 3 * 365]  # Approximate indices of cash flows in the array timePoints
    intervals = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]  # Cash flows each 6 months
    parameters = [nominalJPY, initial, knockOut, knockIn, highRate, lowRate, strike, intervals, cfIndices]

    payOff = NikkeiLinkedNotePayoff
    nSim = 10000

    monteCarlo = MonteCarlo(S0, sigma, r, d, timePoints, payOff, parameters, nSim)
    structPV = monteCarlo["Theoretical Value"]

    """ At this point we will create one FRN for each knock-out time """
    floatPV = 0.0
    maturities = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    for i in range(len(maturities)):
        maturity = maturities[i]
        cashFlowTimes = [0.25 * j for j in range(1, int(maturity / 0.25) + 1)]
        spread = -0.0040
        frn = FloatingRateNote(nominalUSD, maturity, cashFlowTimes, spread)
        floatPV += monteCarlo["KO Probability"][i] * frn.PresentValue(rateTimes, ratesUSD)

    """ Print the leg PVs and the total PV """
    print("-" * 100)
    print("Struct Leg (JPY): ", structPV)
    print("Libor Leg  (USD): ", floatPV)
    print("Swap Value (USD): ", structPV / fxRate - floatPV)

    """ Print additional info of struct leg """
    print("-" * 100)
    for key in monteCarlo.keys():
        print(key, monteCarlo[key])
    print("-" * 100)


StructuredSwapTest()

"""Struct Leg (JPY):  980394145.5618186
Libor Leg  (USD):  8819712.721639313
Swap Value (USD):  -105098.09442314692
----------------------------------------------------------------------------------------------------
Remaining Life 1.9955400000000068
Theoretical Value 980394145.5618186
Cash Flows [212424050.0, 156953200.0, 102133200.0, 69439500.0, 52483400.0, 421286653.8808537]
Cash Flow PVs [210526001.9605835, 154153316.9439502, 99414949.65016069, 66984139.65931969, 50175235.420371205, 399140501.92743486]
KO Probability [0.195, 0.1448, 0.0935, 0.063, 0.0473, 0.4564]"""