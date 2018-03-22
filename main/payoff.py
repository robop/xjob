"""Here we have all the pay off functions"""

def ccs(fixRate,fixDiscount,fx,floatingDiscount,forwardRate,cfDatesFix,cfDatesFloating):

    # fix leg pv
    m = len(cfDatesFix) - 1
    pvFix = 0
    for i in range(m):
        pvFix += fixRate*fixDiscount[i]

    # floating leg pv
    n = len(cfDatesFloating) - 1
    pvFloating = 0
    for i in range(n):
        pvFloating += floatingDiscount[i]*forwardRate[i]*(cfDatesFloating[i+1]-cfDatesFloating[i])/360

    V = pvFix - fx*pvFloating

    return V