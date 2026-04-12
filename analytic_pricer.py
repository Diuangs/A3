import math
from scipy.stats import norm

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


def geometric_asian_price(S, K, T, r, sigma, option_type='call'):
    """
    Price geometric average Asian option using Thompson (2002) formula.

    Args:
        S: spot price
        K: strike price
        T: time to maturity (years)
        r: risk-free rate
        sigma: volatility
        option_type: 'call' or 'put'

    Returns:
        price: float
    """
    pass  # TODO