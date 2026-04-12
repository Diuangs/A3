import numpy as np
from analytic_pricer import calc_geometric_basket_closed_form

def calc_arithmetic_basket_mc(S1, S2, sigma1, sigma2, r, T, K, rho, option_type, m_paths, use_cv):
    """
    使用蒙特卡洛模拟计算双资产算术篮子期权
    包含 95% 置信区间计算和控制变量法(Control Variate)
    """
    # 固定随机数种子以保证结果可复现 (作业要求)
    np.random.seed(42)
    
    # 生成独立标准正态分布随机数矩阵 (2行, m_paths列)
    Z_indep = np.random.standard_normal((2, int(m_paths)))
    
    # 乔列斯基分解构造相关性
    # Z1 = Z_indep[0]
    # Z2 = rho * Z_indep[0] + sqrt(1 - rho^2) * Z_indep[1]
    Z1 = Z_indep[0]
    Z2 = rho * Z_indep[0] + np.sqrt(1 - rho**2) * Z_indep[1]
    
    # 模拟到期日 T 的资产价格 (几何布朗运动)
    ST1 = S1 * np.exp((r - 0.5 * sigma1**2) * T + sigma1 * np.sqrt(T) * Z1)
    ST2 = S2 * np.exp((r - 0.5 * sigma2**2) * T + sigma2 * np.sqrt(T) * Z2)
    
    # 计算算术平均篮子和几何平均篮子
    Ba_T = 0.5 * (ST1 + ST2)
    Bg_T = np.sqrt(ST1 * ST2)
    
    # 计算到期支付 (Payoffs)
    if option_type.lower() == 'call':
        payoff_arithmetic = np.maximum(Ba_T - K, 0)
        payoff_geometric = np.maximum(Bg_T - K, 0)
    else: # put
        payoff_arithmetic = np.maximum(K - Ba_T, 0)
        payoff_geometric = np.maximum(K - Bg_T, 0)
        
    discount = np.exp(-r * T)
    Y = discount * payoff_arithmetic
    
    if use_cv:
        # 使用几何篮子期权作为控制变量
        X = discount * payoff_geometric
        
        # 计算最优参数 c* = Cov(X, Y) / Var(X)
        cov_matrix = np.cov(X, Y)
        cov_XY = cov_matrix[0, 1]
        var_X = cov_matrix[0, 0]
        c_star = cov_XY / var_X if var_X != 0 else 0
        
        # 获取几何篮子的精确期望值 E[X]
        E_X = calc_geometric_basket_closed_form(S1, S2, sigma1, sigma2, r, T, K, rho, option_type)
        
        # 调整后的 Payoff: Y_cv = Y - c*(X - E[X])
        Y_final = Y - c_star * (X - E_X)
    else:
        Y_final = Y
        
    # 计算均值和 95% 置信区间
    price_estimate = np.mean(Y_final)
    std_err = np.std(Y_final, ddof=1) / np.sqrt(m_paths)
    
    # 95% 置信区间 (1.96 * 标准误)
    ci_lower = price_estimate - 1.96 * std_err
    ci_upper = price_estimate + 1.96 * std_err
    
    return {
        "Price": price_estimate,
        "CI_Lower": ci_lower,
        "CI_Upper": ci_upper,
        "StdError": std_err
    }


def arithmetic_asian_price(S, K, T, r, sigma, option_type='call',
                            n_paths=100000, seed=42):
    """
    Price arithmetic average Asian option using MC with geometric Asian as control variate.

    Args:
        S, K, T, r, sigma, option_type: same as analytic
        n_paths: number of simulation paths
        seed: random seed for reproducibility

    Returns:
        (price, lower_ci, upper_ci): tuple of (price, 95% CI lower, 95% CI upper)
    """
    pass  # TODO

def compute_95_ci(samples):
    """
    Compute 95% confidence interval from MC sample prices.

    Args:
        samples: array of option payoffs across paths

    Returns:
        (mean, lower, upper)
    """
    pass  # TODO