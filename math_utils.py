# math_utils.py
import numpy as np
from scipy.stats import norm
import math

def normal_cdf(x):
    """Cumulative distribution function of standard normal."""
    return norm.cdf(x)

def normal_inv_cdf(p):
    """Inverse CDF (ppf) of standard normal."""
    return norm.ppf(p)

def normal_sample(size, seed=42):
    """Generate normal samples with fixed seed."""
    rng = np.random.default_rng(seed)
    return rng.standard_normal(size)

def sample_mean(arr):
    """Arithmetic mean of sample array."""
    return np.mean(arr)

def sample_std(arr):
    """Standard deviation of sample array."""
    return np.std(arr, ddof=1)

def covariance(arr1, arr2):
    """Sample covariance between two arrays."""
    return np.cov(arr1, arr2, ddof=1)[0, 1]
    
def normal_pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)

def discount_factor(r, T):
    return math.exp(-r * T)

def bs_d1_d2(S0, sigma, r, q, T, K):
    d1 = (math.log(S0 / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return d1, d2
