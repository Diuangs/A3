import math
import numpy as np
from scipy.stats import norm
from math_utils import normal_cdf, normal_pdf, discount_factor, bs_d1_d2

def calc_geometric_basket_closed_form(S1, S2, sigma1, sigma2, r, T, K, rho, option_type):
    """
    计算双资产几何篮子期权的闭式解
    对应公式 (4), (5), (6), (7)
    """
    # 资产数量 n = 2
    n = 2

    # 计算 Bg(0)
    Bg_0 = math.sqrt(S1 * S2)

    # 计算组合波动率 sigma_Bg (公式 4)
    # 分子内部: sum(sigma_i * sigma_j * rho_ij)
    # = sigma1*sigma1*1 + sigma2*sigma2*1 + sigma1*sigma2*rho + sigma2*sigma1*rho
    variance_sum = sigma1**2 + sigma2**2 + 2 * sigma1 * sigma2 * rho
    sigma_Bg = math.sqrt(variance_sum) / n

    # 计算漂移项 mu_Bg (公式 5)
    mu_Bg = r - 0.5 * ((sigma1**2 + sigma2**2) / n) + 0.5 * (sigma_Bg**2)

    # 计算 d1 和 d2
    d1_numerator = math.log(Bg_0 / K) + (mu_Bg + 0.5 * sigma_Bg**2) * T
    d1_denominator = sigma_Bg * math.sqrt(T)
    d1 = d1_numerator / d1_denominator
    d2 = d1 - d1_denominator

    # 计算期权价格 (公式 6 和 7)
    discount = math.exp(-r * T)
    drift_term = math.exp(mu_Bg * T)

    if option_type.lower() == 'call':
        price = discount * (Bg_0 * drift_term * norm.cdf(d1) - K * norm.cdf(d2))
    elif option_type.lower() == 'put':
        price = discount * (K * norm.cdf(-d2) - Bg_0 * drift_term * norm.cdf(-d1))
    else:
        raise ValueError("Option type must be 'call' or 'put'")

    return price


def calc_european_bs(S0, sigma, r, q, T, K, option_type):
    """
    Black-Scholes formula for European options with continuous dividend yield.

    Args:
        S0:  spot price
        sigma: volatility
        r:    risk-free rate
        q:    continuous dividend yield
        T:    time to maturity (years)
        K:    strike price
        option_type: 'call' or 'put'

    Returns:
        price: float
    """
    option_type = str(option_type).lower()
    d1, d2 = bs_d1_d2(S0, sigma, r, q, T, K)
    disc = np.exp(-r * T)
    if option_type == 'call':
        price = disc * (S0 * np.exp((r - q) * T) * norm.cdf(d1) - K * norm.cdf(d2))
    else:
        price = disc * (K * norm.cdf(-d2) - S0 * np.exp((r - q) * T) * norm.cdf(-d1))
    return float(price)


def calc_implied_vol(S0, r, q, T, K, premium, option_type, tol=1e-6, max_iter=100):
    """
    Newton-Raphson iteration to find implied volatility from Black-Scholes.

    Args:
        S0, r, q, T, K, option_type: same as calc_european_bs
        premium: observed market price of the option
        tol:    convergence tolerance
        max_iter: maximum iterations

    Returns:
        sigma: implied volatility (float)
    """
    # sigma = 0.30  # initial guess
    # for _ in range(max_iter):
    #     d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    #     d2 = d1 - sigma * np.sqrt(T)
    #     disc = np.exp(-r * T)
    #     if option_type == 'call':
    #         price = disc * (S0 * np.exp((r - q) * T) * norm.cdf(d1) - K * norm.cdf(d2))
    #     else:
    #         price = disc * (K * norm.cdf(-d2) - S0 * np.exp((r - q) * T) * norm.cdf(-d1))
    #     vega = disc * S0 * np.exp((r - q) * T) * norm.pdf(d1) * np.sqrt(T)
    #     if vega < 1e-10:
    #         break
    #     diff = premium - price
    #     if abs(diff) < tol:
    #         return float(sigma)
    #     sigma = sigma + diff / vega
    # return float(sigma)

    low_sigma = 1e-6
    high_sigma = 5.0

    low_price = calc_european_bs(S0, low_sigma, r, q, T, K, option_type)
    high_price = calc_european_bs(S0, high_sigma, r, q, T, K, option_type)

    for _ in range(max_iter):
        mid_sigma = 0.5 * (low_sigma + high_sigma)
        mid_price = calc_european_bs(S0, mid_sigma, r, q, T, K, option_type)

        if abs(mid_price - premium) < tol:
            return mid_sigma

        if mid_price < premium:
            low_sigma = mid_sigma
        else:
            high_sigma = mid_sigma

    return 0.5 * (low_sigma + high_sigma)

def calc_geometric_asian_closed_form(S0, sigma, r, T, K, n_obs, option_type):
    """
    Thompson (2002) closed-form for geometric average Asian option.

    Args:
        S0:         spot price
        sigma:      volatility
        r:          risk-free rate
        T:          time to maturity (years)
        K:          strike price
        n_obs:      number of observation periods (e.g., 52 for weekly)
        option_type: 'call' or 'put'

    Returns:
        price: float
    """
    option_type = str(option_type).lower()
    n_obs = int(n_obs)

    if n_obs <= 0:
        raise ValueError("n_obs must be a positive integer")
    if option_type not in {'call', 'put'}:
        raise ValueError("option_type must be 'call' or 'put'")

    # Discrete monitoring at t_i = iT/n, i=1..n.
    mean_log_G = (
        np.log(S0)
        + (r - 0.5 * sigma**2) * T * (n_obs + 1) / (2 * n_obs)
    )
    var_log_G = (
        sigma**2 * T * (n_obs + 1) * (2 * n_obs + 1) / (6 * n_obs**2)
    )

    if var_log_G <= 0:
        deterministic_G = np.exp(mean_log_G)
        payoff = max(deterministic_G - K, 0.0) if option_type == 'call' else max(K - deterministic_G, 0.0)
        return float(np.exp(-r * T) * payoff)

    std_log_G = np.sqrt(var_log_G)
    d1 = (mean_log_G - np.log(K) + var_log_G) / std_log_G
    d2 = d1 - std_log_G
    discount = np.exp(-r * T)
    expected_G = np.exp(mean_log_G + 0.5 * var_log_G)

    if option_type == 'call':
        price = discount * (expected_G * norm.cdf(d1) - K * norm.cdf(d2))
    else:
        price = discount * (K * norm.cdf(-d2) - expected_G * norm.cdf(-d1))
    return float(price)
