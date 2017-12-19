import math
import random

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

def CallOption(St, K, r, d, vol, t, T):

    tEff = T - t
    if tEff == 0:
        return max( St - K, 0.0 )

    F = St * math.exp( (r - d) * tEff )
    d1 = (math.log( F / K ) + vol * vol * tEff / 2.0) / (vol * math.sqrt( tEff ))
    d2 = d1 - vol * math.sqrt( tEff )

    V = math.exp( -r * tEff ) * (F * N( d1 ) - K * N( d2 ))

    return V


def MonteCarloPath(S0, r, d, vol, tVec):
    St = S0
    path = [ St ]
    nt = len( tVec )
    for i in range( nt - 1 ):
        dt = tVec[ i + 1 ] - tVec[ i ]
        rand = random.normalvariate( 0.0, 1.0 )
        St = St * math.exp( (r - d - 0.5 * vol * vol) * dt + vol * math.sqrt( dt ) * rand )
        path.append( St )
    return path


def TestValuation( ):

    S0 = 100.0
    K = 100.0
    r = 0.1
    d = 0.0
    vol = 0.3
    T = 1.0

    t = 1.0 / 12
    St = S0 * math.exp( (r - d) * t )

    V = CallOption( St, K, r, d, vol, t, T )

    print( V )


def TestEPE( ):

    S0 = 100.0
    K = 100.0
    r = 0.1
    d = 0.0
    vol = 0.3
    T = 1.0
    nt = 12
    dt = 1.0 / nt

    sim = 100000

    tVec = [ i * dt for i in range( nt + 1 ) ]
    EPE = [ 0.0 for t in tVec ]

    for i in range( sim ):
        """ For each sim, generate random walk """
        path = MonteCarloPath( S0, r, d, vol, tVec )
        for j in range( len( path ) ):
            """ For each time point, estimate value of contract """
            t = tVec[ j ]
            St = path[ j ]
            Vt = CallOption( St, K, r, d, vol, t, T )
            EPE[ j ] += max( Vt, 0.0 )

    EPE = [ E / sim for E in EPE ]  # Expected Positive Exposure (= EE Since Vt >= 0)
    print( EPE )

    """ Actually since EPE is just the Option Value discounted from T to t """
    V = CallOption( S0, K, r, d, vol, 0.0, T )
    print( [ math.exp( t * r ) * V for t in tVec ] )

TestEPE( )

#TestValuation()ion()ion()ion()ion()ion()ion()ion()ion()ion()ion()ion()ion()ion()ion()ion()
