import calendar
from datetime import date

from dateutil.relativedelta import relativedelta


def IsString(dateIn):
    return type(dateIn) == str


def YearFromString(dateString):
    return int(dateString[0:4])


def MonthFromString(dateString):
    return int(dateString[5:7])


def DayFromString(dateString):
    return int(dateString[8:10])


def Year(dateObj):
    return dateObj.year


def Month(dateObj):
    return dateObj.month


def Day(dateObj):
    return dateObj.day


def DateObjectFromString(dateString):
    year = YearFromString(dateString)
    month = MonthFromString(dateString)
    day = DayFromString(dateString)

    dateObj = date(year, month, day)

    return dateObj


def DateStringFromDateObject(dateIn):
    return str(dateIn)


def DateToday():
    return date.today()


def DateAddDelta(refDate, y, m, d):
    if IsString(refDate):
        refDate = DateObjectFromString(refDate)
    return refDate + relativedelta(years=+y, months=+m, days=+d)


def DateAddDatePeriod(refDate, datePeriod):
    if IsString(refDate):
        refDate = DateObjectFromString(refDate)
    n = len(datePeriod)
    unit = datePeriod[n - 1]
    value = datePeriod[0:n - 1]

    if unit in ["d", "D"]:
        newDate = DateAddDelta(refDate, 0, 0, int(value))
    if unit in ["w", "W"]:
        newDate = DateAddDelta(refDate, 0, 0, 7 * int(value))
    if unit in ["m", "M"]:
        newDate = DateAddDelta(refDate, 0, int(value), 0)
    if unit in ["y", "Y"]:
        newDate = DateAddDelta(refDate, int(value), 0, 0)

    return newDate


def DateSubtractDatePeriod(refDate, datePeriod):
    if IsString(refDate):
        refDate = DateObjectFromString(refDate)
    n = len(datePeriod)
    unit = datePeriod[n - 1]
    value = datePeriod[0:n - 1]

    if unit in ["d", "D"]:
        newDate = DateAddDelta(refDate, 0, 0, -int(value))
    if unit in ["w", "W"]:
        newDate = DateAddDelta(refDate, 0, 0, -7 * int(value))
    if unit in ["m", "M"]:
        newDate = DateAddDelta(refDate, 0, -int(value), 0)
    if unit in ["y", "Y"]:
        newDate = DateAddDelta(refDate, -int(value), 0, 0)

    return newDate


def DateDifferenceInDays(startDate, endDate):
    if IsString(startDate):
        startDate = DateObjectFromString(startDate)
    if IsString(endDate):
        endDate = DateObjectFromString(endDate)

    [startYear, startMonth, startDay] = map(int, str(startDate).split('-'))
    [endYear, endMonth, endDay] = map(int, str(endDate).split('-'))

    ds = date(startYear, startMonth, startDay)
    de = date(endYear, endMonth, endDay)
    delta = de - ds

    return delta.days


def DateDifferenceInYears(startDate, endDate):
    if IsString(startDate):
        startDate = DateObjectFromString(startDate)
    if IsString(endDate):
        endDate = DateObjectFromString(endDate)

    return DateDifferenceInDays(startDate, endDate) / 365.0


def WeekDayFromDate(refDate):
    if IsString(refDate):
        refDate = DateObjectFromString(refDate)

    return calendar.day_name[refDate.weekday()]

def IsBusinessDay(refDate, holidayArray):
    if IsString(refDate):
        refDate = DateObjectFromString(refDate)

    day = WeekDayFromDate(refDate)

    if (day == "Saturday" or day == "Sunday"):
        return False

    if str(refDate) in holidayArray:
        return False

    return True

def DateAddBusinessDays(refDate, days, holidayArray):
    """ We need to add days one by one, not counting the days that are non-business days """
    if IsString(refDate):
        refDate = DateObjectFromString(refDate)

    tmpDays = 0
    newDate = refDate
    while tmpDays < days:
        newDate = DateAddDelta(newDate, 0, 0, 1)
        if IsBusinessDay(newDate, holidayArray):
            tmpDays += 1

    return newDate


def DateSubtractBusinessDays(refDate, days, holidayArray):
    """ We need to subtract days one by one, not counting the days that are non-business days """
    if IsString(refDate):
        refDate = DateObjectFromString(refDate)

    tmpDays = 0
    newDate = refDate
    while tmpDays < days:
        newDate = DateAddDelta(newDate, 0, 0, -1)
        if IsBusinessDay(newDate, holidayArray):
            tmpDays += 1

    return newDate


def AdjustToBusinessDay(refDate, adjMethod, holidayArray):
    if IsString(refDate):
        refDate = DateObjectFromString(refDate)

    tmpDate = refDate
    if adjMethod == "Following":
        while not IsBusinessDay(tmpDate, holidayArray):
            tmpDate = DateAddDelta(tmpDate, 0, 0, 1)

    elif adjMethod == "Mod. Following":
        origMonth = Month(tmpDate)
        origDate = tmpDate

        while not IsBusinessDay(tmpDate, holidayArray):
            tmpDate = DateAddDelta(tmpDate, 0, 0, 1)

        if Month(tmpDate) != origMonth:
            tmpDate = origDate
            while not IsBusinessDay(tmpDate, holidayArray):
                tmpDate = DateAddDelta(tmpDate, 0, 0, -1)


    elif adjMethod == "Previous":
        while not IsBusinessDay(tmpDate, holidayArray):
            tmpDate = DateAddDelta(date, 0, 0, -1)

    elif adjMethod == "Mod. Previous":
        origMonth = Month(tmpDate)
        origDate = tmpDate
        while not IsBusinessDay(tmpDate, holidayArray):
            tmpDate = DateAddDelta(tmpDate, 0, 0, -1)

        if Month(date) != origMonth:
            tmpDate = origDate
            while not IsBusinessDay(tmpDate, holidayArray):
                tmpDate = DateAddDelta(tmpDate, 0, 0, 1)

    return tmpDate


def IsLeapYear(lyDate):
    if IsString(lyDate):
        lyDate = DateObjectFromString(lyDate)

    year = date.year
    if ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0):
        return True
    return False

def IsLeapYearOnlyYear(year):
    if ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0):
        return True
    return False

def GetNumberOfLeapYearDays(startDate, endDate):
    if IsString(startDate):
        startDate = DateObjectFromString(startDate)

    if IsString(endDate):
        endDate = DateObjectFromString(endDate)

    n = 0
    if IsLeapYear(startDate):
        if Month(startDate) <= 2 and Day(startDate) < 29:
            if Month(endDate) > 2 or Year(endDate) > Year(startDate):
                n += 1

    years = int(DateDifferenceInYears(startDate, endDate))
    startYear = Year(startDate)
    startMonth = Month(startDate)
    startDay = Day(startDate)

    for year in range(1, years):
        """ This goes to the year before endDate """
        if IsLeapYear(str(date(startYear + year, startMonth, startDay))):
            n += 1

    """ Handle end date """
    if IsLeapYear(str(date(startYear + years, startMonth, startDay))):
        if Month(endDate) > 2 and Year(endDate) > startYear:
            n += 1

    return n

def GetPeriodLength(startDate, endDate, dayCount):
    if IsString(startDate):
        startDate = DateObjectFromString(startDate)

    if IsString(endDate):
        endDate = DateObjectFromString(endDate)

    if dayCount == "Act/365":
        days = DateDifferenceInDays(startDate, endDate)
        return (days, days / 365.0)

    elif dayCount == "Act/360":
        days = DateDifferenceInDays(startDate, endDate)
        return (days, days / 360.0)

    elif dayCount == "30/360":
        d1 = Day(startDate)
        d2 = Day(endDate)
        m1 = Month(startDate)
        m2 = Month(endDate)
        y1 = Year(startDate)
        y2 = Year(endDate)

        if (d1 == 31):
            d1 = 30
        if (d2 == 31) and (d1 == 30):
            d2 = 30

        days = (d2 - d1) + 30 * (m2 - m1) + 360 * (y2 - y1)

        return (days, days / 360.0)

    elif dayCount == "Act/365 Fix":
        days = DateDifferenceInDays(startDate, endDate)
        days -= GetNumberOfLeapYearDays(startDate, endDate)

        return (days, days / 365.0)

def RemoveDuplicates(array):
    newArray = []
    for a in array:
        if a not in newArray:
            newArray.append(a)

    return newArray


def GenerateCashFlowDates(startDate, endDate, term, period, adjustMethod="Mod. Following", isStub=True, holidayArray=[]):
    if IsString(startDate):
        startDate = DateObjectFromString(startDate)

    startDate = AdjustToBusinessDay(startDate, adjustMethod, holidayArray)

    if endDate == None:
        endDate = DateAddDatePeriod(startDate, term)
    else:
        if IsString(endDate):
            endDate = DateObjectFromString(endDate)

    tmpDate = endDate
    endDates = [tmpDate]

    while DateDifferenceInDays(startDate, DateSubtractDatePeriod(tmpDate, period)) > 0:
        tmpDate = DateSubtractDatePeriod(tmpDate, period)
        endDates.append(AdjustToBusinessDay(tmpDate, adjustMethod, holidayArray))

    """ Remove Duplicates: Typically there are duplicates if the period is 1d as saturday, sunday and monday all end up
        adjusted to monday.
    """
    endDates = RemoveDuplicates(endDates)

    endDates[0] = AdjustToBusinessDay(endDates[0], adjustMethod, holidayArray)
    endDates.sort()

    startDates = [startDate]
    startDates.extend(endDates[0:len(endDates) - 1])

    if not isStub:
        """ Check if the first period is less than a cash flow period and if so remove first cash flow end date """
        if DateDifferenceInDays(startDates[0], DateSubtractDatePeriod(endDates[0], period)) < 0:
            endDates = endDates[1:len(endDates)]
            startTemp = [startDates[0]]
            startTemp.extend(startDates[2:len(startDates)])
            startDates = startTemp

    return (startDates, endDates)


def IsDate(dateCandidate):
    if not IsString(dateCandidate):
        dateCandidate = DateStringFromDateObject(dateCandidate)

    inputType = type(dateCandidate)
    if str(inputType) != "<class 'str'>":
        return False

    inputSize = len(dateCandidate)
    if inputSize != 10:
        return False

    if dateCandidate[4] != "-" or dateCandidate[7] != "-":
        return False

    year = dateCandidate[0:4]
    month = dateCandidate[5:7]
    day = dateCandidate[8:10]
    numbers = [str(i) for i in range(10)]

    for number in [year, month, day]:
        for chr in number:
            if chr not in numbers:
                return False

    if int(month) > 12 or int(month) == 0:
        return False

    if int(day) == 0 or int(day) > 31:
        return False

    if int(month) in [4, 6, 9, 11]:
        if int(day) > 30:
            return False

    if IsLeapYearOnlyYear(int(year)):
        if int(month) == 2:
            if int(day) > 29:
                return False
            if int(day) <= 29:
                return True

    if int(month) == 2:
        if int(day) > 28:
            return False

    return True


def IsDatePeriod(datePeriodCandidate):
    today = DateToday()
    try:
        newDate = DateAddDatePeriod(today, datePeriodCandidate)
        return IsDate(newDate)
    except:
        return False



