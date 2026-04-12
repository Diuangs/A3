# advanced_pricer.py
"""
Advanced option pricers: binomial tree, barrier options, etc.
"""

import numpy as np


def american_binomial_price(S, K, T, r, sigma, option_type='call', N=100):
    """
    Price American option using Cox-Ross-Rubinstein binomial tree.

    Args:
        S: spot price
        K: strike price
        T: time to maturity (years)
        r: risk-free rate
        sigma: volatility
        option_type: 'call' or 'put'
        N: number of time steps

    Returns:
        price: float
    """
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))   # up factor
    d = 1.0 / u                        # down factor
    p = (np.exp(r * dt) - d) / (u - d)  # risk-neutral probability
    disc = np.exp(-r * dt)

    # Terminal stock prices (vectorized)
    j = np.arange(N + 1)        # 0, 1, ..., N
    ST = S * (u ** (N - j)) * (d ** j)

    # Terminal payoffs
    if option_type == 'call':
        V = np.maximum(ST - K, 0.0)
    else:
        V = np.maximum(K - ST, 0.0)

    # Backward induction with early exercise check
    for i in range(N - 1, -1, -1):
        j = np.arange(i + 1)
        Si = S * (u ** (i - j)) * (d ** j)
        # Continuation value
        V = disc * (p * V[:-1] + (1 - p) * V[1:])
        # Exercise value
        if option_type == 'call':
            exercise = np.maximum(Si - K, 0.0)
        else:
            exercise = np.maximum(K - Si, 0.0)
        # American: max of continuation and exercise
        V = np.maximum(V, exercise)

    return float(V[0])
