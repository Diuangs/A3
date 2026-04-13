import numpy as np
import math
from scipy.stats import norm, qmc


def calc_american_binomial(S0, sigma, r, T, K, n_steps, option_type):
    """
    Cox-Ross-Rubinstein binomial tree for American options.

    Args:
        S0:         spot price
        sigma:      volatility
        r:          risk-free rate
        T:          time to maturity (years)
        K:          strike price
        n_steps:    number of binomial tree time steps
        option_type: 'call' or 'put'

    Returns:
        price: float
    """
    option_type = str(option_type).lower()
    dt = T / n_steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1.0 / u
    p = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    j = np.arange(n_steps + 1)
    ST = S0 * (u ** (n_steps - j)) * (d ** j)

    if option_type == 'call':
        V = np.maximum(ST - K, 0.0)
    else:
        V = np.maximum(K - ST, 0.0)

    for i in range(n_steps - 1, -1, -1):
        j = np.arange(i + 1)
        Si = S0 * (u ** (i - j)) * (d ** j)
        V = disc * (p * V[:-1] + (1 - p) * V[1:])
        if option_type == 'call':
            exercise = np.maximum(Si - K, 0.0)
        else:
            exercise = np.maximum(K - Si, 0.0)
        V = np.maximum(V, exercise)

    return float(V[0])


def calc_kiko_put_qmc(S0, sigma, r, T, K, L, U, n_obs, R, m_paths=100000):
    """
    使用擬蒙特卡洛 (QMC) 計算 KIKO Put 的價格、置信區間和 Delta
    """
    n_obs = int(n_obs)
    dt = T / n_obs
    
    # 為了消除 Sobol 序列警告，自動調整路徑數為 2 的冪
    m_power = math.ceil(math.log2(int(m_paths)))
    optimal_paths = 2 ** m_power 
    
    sampler = qmc.Sobol(d=n_obs, scramble=True, seed=42)
    uniform_samples = sampler.random_base2(m=m_power) 
    Z_matrix = norm.ppf(uniform_samples)
    
    def get_all_payoffs(start_price):
        """返回每一條路徑的收益數組"""
        payoffs = np.zeros(optimal_paths)
        S = np.full(optimal_paths, float(start_price))
        
        knocked_in = np.zeros(optimal_paths, dtype=bool) 
        active = np.ones(optimal_paths, dtype=bool)      
        
        drift = (r - 0.5 * sigma**2) * dt
        vol = sigma * np.sqrt(dt)
        
        for i in range(n_obs):
            S[active] = S[active] * np.exp(drift + vol * Z_matrix[active, i])
            
            # 檢查敲出 (Knock-out)
            ko_mask = active & (S >= U)
            payoffs[ko_mask] = R * np.exp(-r * (i + 1) * dt)
            active[ko_mask] = False 
            
            # 檢查敲入 (Knock-in)
            knocked_in = knocked_in | (active & (S <= L))
            
        # 到期處理：未被敲出且曾經敲入
        survived_and_ki = active & knocked_in
        payoffs[survived_and_ki] = np.maximum(K - S[survived_and_ki], 0) * np.exp(-r * T)
        
        return payoffs

    # 1. 計算基准價格和置信區間
    base_payoffs = get_all_payoffs(S0)
    price = np.mean(base_payoffs)
    
    # 計算 95% 置信區間 (1.96 * 標準誤)
    std_dev = np.std(base_payoffs, ddof=1)
    std_err = std_dev / np.sqrt(optimal_paths)
    ci_lower = price - 1.96 * std_err
    ci_upper = price + 1.96 * std_err
    
    # 2. 計算 Delta (中心差分)
    bump = S0 * 0.01
    p_up = np.mean(get_all_payoffs(S0 + bump))
    p_down = np.mean(get_all_payoffs(S0 - bump))
    delta = (p_up - p_down) / (2 * bump)
    
    return {
        "Price": price,
        "Delta": delta,
        "CI_Lower": ci_lower,
        "CI_Upper": ci_upper,
        "StdErr": std_err
    }