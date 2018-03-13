from math import exp, log
import LinearAlgebra


def HermiteMi(t, ti, tiplus):
   """Spline coefficient in Hermite Interpolation"""
   return (t - ti) / (tiplus - ti)


def HermiteGi(ti, tiplus, riprime, ri, riplus):
   """Spline coefficient in Hermite Interpolation"""
   return (tiplus - ti) * riprime - (riplus - ri)


def HermiteCi(ri, riplus, ti, tiplus, riprime, riprimeplus):
   """Spline coefficient in Hermite Interpolation"""
   return 2 * (riplus - ri) - (tiplus - ti) * (riprime + riprimeplus)


def RiPrimeIntermediate(timinus, ti, tiplus, ri, riplus, riminus):
   """Gradient vector in Hermite Interpolation: General Case"""
   term1 = (ri - riminus) * (tiplus - ti) / (ti - timinus)
   term2 = (riplus - ri) * (ti - timinus) / (tiplus - ti)

   return (term1 + term2) / (tiplus - timinus)


def RiPrimeFirst(tVec, rVec):
   """Gradient vector in Hermite Interpolation: Special Case, first interval"""
   term1 = (rVec[1] - rVec[0]) * (tVec[2] + tVec[1] - 2 * tVec[0]) / (tVec[1] - tVec[0])
   term2 = (rVec[2] - rVec[1]) * (tVec[1] - tVec[0]) / (tVec[2] - tVec[1])

   return (term1 - term2) / (tVec[2] - tVec[0])


def RiPrimeLast(tVec, rVec):
   """Gradient vector in Hermite Interpolation: Special Case, last interval"""
   n = len(tVec)
   term1 = (rVec[n - 2] - rVec[n - 3]) * (tVec[n - 1] - tVec[n - 2]) / (tVec[n - 2] - tVec[n - 3])
   term2 = (rVec[n - 1] - rVec[n - 2]) * (2 * tVec[n - 1] - tVec[n - 2] - tVec[n - 3]) / (tVec[n - 1] - tVec[n - 2])

   return -(term1 - term2) / (tVec[n - 1] - tVec[n - 3])


def CubicA(t, ti, tiplus):
   """Spline coefficient in Cubic Spline Interpolation"""
   return (tiplus - t) / (tiplus - ti)


def CubicB(t, ti, tiplus):
   """Spline coefficient in Cubic Spline Interpolation"""
   return 1 - CubicA(t, ti, tiplus)


def CubicC(t, ti, tiplus):
   """Spline coefficient in Cubic Spline Interpolation"""
   return (CubicA(t, ti, tiplus) ** 3 - CubicA(t, ti, tiplus)) * (tiplus - ti) * (tiplus - ti) / 6.0


def CubicD(t, ti, tiplus):
   """Spline coefficient in Cubic Spline Interpolation"""
   return (CubicB(t, ti, tiplus) ** 3 - CubicB(t, ti, tiplus)) * (tiplus - ti) * (tiplus - ti) / 6.0


def RPrimePrime(points, values):
   """Second derivative vector in Cubic Spline Interpolation: Involves solving a tridiagonal system of equations"""
   n = len(points)

   a = [(points[i] - points[i - 1]) / 6 for i in range(1, n - 1)]
   b = [(points[i + 1] - points[i - 1]) / 3 for i in range(1, n - 1)]
   c = [(points[i + 1] - points[i]) / 6 for i in range(1, n - 1)]
   RHS = [(values[i + 1] - values[i]) / (points[i + 1] - points[i]) - (values[i] - values[i - 1]) / (
   points[i] - points[i - 1]) for i in range(1, n - 1)]

   result = [0.0 for i in range(n)]
   result[1:n - 1] = LinearAlgebra.SolveTriDiagonal(a, b, c, RHS)

   return result


def RTPrimePrime(points, values):
   """Second derivative vector in Cubic Spline Interpolation: Involves solving a Tri-Diagonal system of equations"""
   n = len(points)

   a = [(points[i] - points[i - 1]) / 6 for i in range(1, n - 1)]
   b = [(points[i + 1] - points[i - 1]) / 3 for i in range(1, n - 1)]
   c = [(points[i + 1] - points[i]) / 6 for i in range(1, n - 1)]
   RHS = [(values[i + 1] * points[i + 1] - values[i] * points[i]) / (points[i + 1] - points[i]) - (
   values[i] * points[i] - values[i - 1] * points[i - 1]) / (points[i] - points[i - 1]) for i in range(1, n - 1)]

   result = [0.0 for i in range(n)]
   result[1:n - 1] = LinearAlgebra.SolveTriDiagonal(a, b, c, RHS)

   return result


def FindPosition(point, points):
   """Determines the position of point in the vector points"""
   if point < points[0]:
       return -1

   for i in range(len(points) - 1):
       if point < points[i + 1]:
           return i

   return len(points)


def LinearInterpolation(point, points, values, extrapolationBack="Flat", extrapolationForw="Flat"):
   """ LinearInterpolation(point, points, values) """
   n = len(points)
   i = FindPosition(point, points)
   if i == -1:
       if extrapolationBack == "Flat":
           return values[0]

       elif extrapolationBack == "Linear":
           coeff = (values[1] - values[0]) / (points[1] - points[0])
           value = values[0] + (point - points[0]) * coeff
           return value

   elif i == len(values):
       if extrapolationForw == "Flat":
           return values[len(values) - 1]

       elif extrapolationForw == "Linear":
           n = len(values) - 1
           coeff = (values[n] - values[n - 1]) / (points[n] - points[n - 1])
           value = values[n] + (point - points[n]) * coeff
           return value

   coeff = (values[i + 1] - values[i]) / (points[i + 1] - points[i])
   value = values[i] + (point - points[i]) * coeff

   return value


def LogLinearInterpolation(point, points, values, extrapolationBack="Flat", extrapolationForw="Flat"):
   """LinearInterpolation(point, points, values)"""
   n = len(points)
   i = FindPosition(point, points)
   if i == -1:
       if extrapolationBack == "Flat":
           return values[0]

       elif extrapolationBack == "Linear":
           coeff = (values[1] - values[0]) / (points[1] - points[0])
           value = values[0] + (point - points[0]) * coeff
           return value

   elif i == len(values):
       if extrapolationForw == "Flat":
           return values[len(values) - 1]

       elif extrapolationForw == "Linear":
           n = len(values) - 1
           coeff = (values[n] - values[n - 1]) / (points[n] - points[n - 1])
           value = values[n] + (point - points[n]) * coeff
           return value

   coeff = (log(values[i + 1]) - log(values[i])) / (points[i + 1] - points[i])
   value = log(values[i]) + (point - points[i]) * coeff

   return exp(value)


def LogDiscountLinearInterpolation(point, points, values, extrapolationBack="Flat", extrapolationForw="Flat"):
   """LinearInterpolation(point, points, values)"""
   n = len(points)
   i = FindPosition(point, points)
   if i == -1:
       if extrapolationBack == "Flat":
           return values[0]

       elif extrapolationBack == "Linear":
           coeff = (values[1] - values[0]) / (points[1] - points[0])
           value = values[0] + (point - points[0]) * coeff
           return value

   elif i == len(values):
       if extrapolationForw == "Flat":
           return values[len(values) - 1]

       elif extrapolationForw == "Linear":
           n = len(values) - 1
           coeff = (values[n] - values[n - 1]) / (points[n] - points[n - 1])
           value = values[n] + (point - points[n]) * coeff
           return value

   coeff = (values[i + 1] * points[i + 1] - values[i] * points[i]) / (points[i + 1] - points[i])
   value = values[i] * points[i] + (point - points[i]) * coeff

   return value / point


def QuadraticInterpolation(point, points, values):
   """QuadraticInterpolation(point, points, values): For three points (x1,y1), (x2,y2), (x3,y3)"""
   b = ((values[1] - values[2]) / (points[1] ** 2 - points[2] ** 2) - (values[0] - values[2]) / (
   points[0] ** 2 - points[2] ** 2)) / (1 / (points[1] + points[2]) + 1 / (points[0] + points[2]))
   a = (values[0] - values[2]) / (points[0] ** 2 - points[2] ** 2) - b / (points[0] + points[2])
   c = values[2] - (points[2] ** 2) * a - points[2] * b

   value = a * point ** 2 + b * point + c

   return value


def LeastSquaresQuadraticInterpolation(point, points, values):
   """LeastSquaresQuadraticInterpolation(point, points, values): For n points {(xi,yi)}, i = 1,...,n"""
   n = len(points)
   A = [[1.0 * points[i] ** 2, 1.0 * points[i], 1.0] for i in range(n)]

   [a, b, c] = LinearAlgebra.LeastSquaresCholesky(A, values)
   value = a * point ** 2 + b * point + c

   return value


def LeastSquaresCubicInterpolation(point, points, values):
   """LeastSquaresCubicInterpolation(point, points, values): For n points {(xi,yi)}, i = 1,...,n"""
   n = len(points)
   A = [[1.0 * points[i] ** 3, 1.0 * points[i] ** 2, 1.0 * points[i], 1.0] for i in range(n)]

   [a, b, c, d] = LinearAlgebra.LeastSquaresCholesky(A, values)
   value = a * point ** 3 + b * point ** 2 + c * point + d

   return value


def LeastSquaresPolynomialInterpolation(point, points, values, order):
   """LeastSquaresPolynomialInterpolation(point, points, values, order): For n points {(xi,yi)}, i = 1,...,n, by a polynomial or order < n"""
   n = len(points)
   value = 0

   if order > n:
       print("Warning reducing order of approximating polynomial due to order => number of points")
       order = n - 1

   A = [[1.0 * points[i] ** j for j in range(order + 1)] for i in range(n)]
   coeff = LinearAlgebra.LeastSquaresCholesky(A, values)

   for i in range(order + 1):
       value += coeff[i] * point ** i

   return value


def HermiteInterpolation(point, points, values, extrapolationBack="Flat", extrapolationForw="Flat"):
   """HermiteInterpolation(point, points, values)"""
   n = len(points)
   i = FindPosition(point, points)
   if i == -1:
       if extrapolationBack == "Flat":
           return values[0]

       elif extrapolationBack == "Linear":
           coeff = (values[1] - values[0]) / (points[1] - points[0])
           value = values[0] + (point - points[0]) * coeff
           return value

   elif i == len(values):
       if extrapolationForw == "Flat":
           return values[len(values) - 1]

       elif extrapolationForw == "Linear":
           n = len(values) - 1
           coeff = (values[n] - values[n - 1]) / (points[n] - points[n - 1])
           value = values[n] + (point - points[n]) * coeff
           return value

   rPrime = [RiPrimeFirst(points, values)]

   for k in range(1, n - 1):
       rPrime.append(
           RiPrimeIntermediate(points[k - 1], points[k], points[k + 1], values[k], values[k + 1], values[k - 1]))

   rPrime.append(RiPrimeLast(points, values))

   m = HermiteMi(point, points[i], points[i + 1])
   g = HermiteGi(points[i], points[i + 1], rPrime[i], values[i], values[i + 1])
   c = HermiteCi(values[i], values[i + 1], points[i], points[i + 1], rPrime[i], rPrime[i + 1])

   value = values[i] + m * (values[i + 1] - values[i]) + m * (1 - m) * g + m * m * (1 - m) * c

   return value


def HermiteLogDiscountInterpolation(point, points, values, extrapolationBack="Flat", extrapolationForw="Flat"):
   """HermiteInterpolation(point, points, values)"""
   n = len(points)
   i = FindPosition(point, points)
   if i == -1:
       if extrapolationBack == "Flat":
           return values[0]

       elif extrapolationBack == "Linear":
           coeff = (values[1] - values[0]) / (points[1] - points[0])
           value = values[0] + (point - points[0]) * coeff
           return value

   elif i == len(values):
       if extrapolationForw == "Flat":
           return values[len(values) - 1]

       elif extrapolationForw == "Linear":
           n = len(values) - 1
           coeff = (values[n] - values[n - 1]) / (points[n] - points[n - 1])
           value = values[n] + (point - points[n]) * coeff
           return value

   rPrime = [RiPrimeFirst(points, values)]

   for k in range(1, n - 1):
       rPrime.append(
           RiPrimeIntermediate(points[k - 1], points[k], points[k + 1], values[k], values[k + 1], values[k - 1]))

   rPrime.append(RiPrimeLast(points, values))

   m = HermiteMi(point, points[i], points[i + 1])
   g = HermiteGi(points[i], points[i + 1], rPrime[i], values[i], values[i + 1])
   c = HermiteCi(values[i], values[i + 1], points[i], points[i + 1], rPrime[i], rPrime[i + 1])

   value = values[i] + m * (values[i + 1] - values[i]) + m * (1 - m) * g + m * m * (1 - m) * c

   return value


def CubicSplineInterpolation(point, points, values, extrapolationBack="Flat", extrapolationForw="Flat"):
   i = FindPosition(point, points)

   if i == -1:
       if extrapolationBack == "Flat":
           return values[0]

       elif extrapolationBack == "Linear":
           coeff = (values[1] - values[0]) / (points[1] - points[0])
           value = values[0] + (point - points[0]) * coeff
           return value

   elif i == len(values):
       if extrapolationForw == "Flat":
           return values[len(values) - 1]

       elif extrapolationForw == "Linear":
           n = len(values) - 1
           coeff = (values[n] - values[n - 1]) / (points[n] - points[n - 1])
           value = values[n] + (point - points[n]) * coeff
           return value

   valuesPrimePrime = RPrimePrime(points, values)

   A = CubicA(point, points[i], points[i + 1])
   B = CubicB(point, points[i], points[i + 1])
   C = CubicC(point, points[i], points[i + 1])
   D = CubicD(point, points[i], points[i + 1])

   value = A * values[i] + B * values[i + 1] + C * valuesPrimePrime[i] + D * valuesPrimePrime[i + 1]

   return value


def CubicSplineLogDiscountInterpolation(point, points, values, extrapolationBack="Flat", extrapolationForw="Flat"):
   i = FindPosition(point, points)

   if i == -1:
       if extrapolationBack == "Flat":
           return values[0]

       elif extrapolationBack == "Linear":
           coeff = (values[1] - values[0]) / (points[1] - points[0])
           value = values[0] + (point - points[0]) * coeff
           return value

   elif i == len(values):
       if extrapolationForw == "Flat":
           return values[len(values) - 1]

       elif extrapolationForw == "Linear":
           n = len(values) - 1
           coeff = (values[n] - values[n - 1]) / (points[n] - points[n - 1])
           value = values[n] + (point - points[n]) * coeff
           return value

   valuesPrimePrime = RTPrimePrime(points, values)

   A = CubicA(point, points[i], points[i + 1])
   B = CubicB(point, points[i], points[i + 1])
   C = CubicC(point, points[i], points[i + 1])
   D = CubicD(point, points[i], points[i + 1])

   value = A * values[i] * points[i] + B * values[i + 1] * points[i + 1] + C * valuesPrimePrime[i] + D * \
                                                                                                     valuesPrimePrime[
                                                                                                         i + 1]

   return value / point