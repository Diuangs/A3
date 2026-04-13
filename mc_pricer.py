import numpy as np
from analytic_pricer import calc_geometric_basket_closed_form, calc_geometric_asian_closed_form


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
    else:  # put
        payoff_arithmetic = np.maximum(K - Ba_T, 0)
        payoff_geometric = np.maximum(K - Bg_T, 0)

    discount = np.exp(-r * T)
    Y = discount * payoff_arithmetic

    if use_cv:
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


def calc_arithmetic_asian_mc(S0, sigma, r, T, K, n_obs, option_type, m_paths, use_cv):
    """
    Price arithmetic average Asian option using MC with geometric Asian as control variate.

    Args:
        S0:         spot price
        sigma:      volatility
        r:          risk-free rate
        T:          time to maturity (years)
        K:          strike price
        n_obs:      number of observation periods
        option_type: 'call' or 'put'
        m_paths:    number of simulation paths
        use_cv:     whether to use control variate (bool)

    Returns:
        dict with keys: Price, CI_Lower, CI_Upper, StdError
    """
    option_type = str(option_type).lower()
    rng = np.random.default_rng(42)
    n_steps = max(1, n_obs)

    dt = T / n_steps
    drift = (r - 0.5 * sigma**2) * dt
    vol = sigma * np.sqrt(dt)

    Z = rng.standard_normal((int(m_paths), n_steps))
    log_returns = drift + vol * Z
    price_paths = S0 * np.exp(np.cumsum(log_returns, axis=1))

    arith_avg = np.mean(price_paths, axis=1)
    log_prices = np.log(price_paths)
    geo_avg = np.exp(np.mean(log_prices, axis=1))

    if option_type == 'call':
        arith_payoff = np.maximum(arith_avg - K, 0.0)
        geo_payoff = np.maximum(geo_avg - K, 0.0)
    else:
        arith_payoff = np.maximum(K - arith_avg, 0.0)
        geo_payoff = np.maximum(K - geo_avg, 0.0)

    discount = np.exp(-r * T)
    discounted_arith = discount * arith_payoff
    discounted_geo = discount * geo_payoff

    if use_cv:
        beta = np.cov(discounted_arith, discounted_geo, ddof=1)[0, 1] / np.var(discounted_geo, ddof=1)
        geo_price = calc_geometric_asian_closed_form(S0=S0, sigma=sigma, r=r, T=T, K=K, n_obs=n_obs, option_type=option_type)
        adjusted_discounted = discounted_arith - beta * (discounted_geo - geo_price)
    else:
        adjusted_discounted = discounted_arith

    price_estimate = float(np.mean(adjusted_discounted))
    std_err = float(np.std(adjusted_discounted, ddof=1) / np.sqrt(len(adjusted_discounted)))
    ci_lower = price_estimate - 1.96 * std_err
    ci_upper = price_estimate + 1.96 * std_err

    return {
        "Price": price_estimate,
        "CI_Lower": ci_lower,
        "CI_Upper": ci_upper,
        "StdError": std_err
    }
