# math_utils.py
import numpy as np
from scipy.stats import norm

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
