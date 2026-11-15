"""Log-mean Divisia index (LMDI) helper.

If X is a product of factors, X = f_1 * f_2 * ... * f_n, then the change in X between
two dates splits exactly into one term per factor:

    X1 - X0 = sum_k  L(X1, X0) * ln(f_k1 / f_k0)

where L(a, b) = (a - b) / (ln a - ln b) is the logarithmic mean.
The terms add up to the total change with no residual. That is why the budget bridge
ties to the published balance to the last decimal.
"""
import math


def logmean(a, b):
    """Logarithmic mean of two positive numbers. Equals a when a == b."""
    if abs(a - b) > 1e-12:
        return (a - b) / (math.log(a) - math.log(b))
    return a


def lmdi(x0, x1, f0, f1):
    """Contribution of each factor to x1 - x0.

    x0, x1: the product of the factors at the start and the end (both positive).
    f0, f1: dicts of factor name -> value at the start and the end (all positive).
    Returns a dict of factor name -> contribution, in the units of x.
    """
    w = logmean(x1, x0)
    return {k: w * math.log(f1[k] / f0[k]) for k in f0}
