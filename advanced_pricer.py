import numpy as np
from scipy.stats import norm


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


def calc_kiko_qmc(S0, sigma, r, T, K, L, U, n_obs, rebate):
    """
    KIKO (Knock-In Knock-Out) barrier put option with rebate,
    priced using Quasi-Monte Carlo (Sobol sequence).

    The option:
    - Knock-out barrier at L (below initial spot)
    - Knock-in barrier at U (above initial spot)
    - Pays rebate if knocked out before knock-in
    - Pays max(K-S_T, 0) if knocked in then survives to expiry

    Args:
        S0:     spot price
        sigma:  volatility
        r:      risk-free rate
        T:      time to maturity (years)
        K:      strike price
        L:      lower knock-out barrier
        U:      upper knock-in barrier
        n_obs:  number of observation periods (monitoring dates)
        rebate: rebate paid if knocked out

    Returns:
        (price, delta): tuple
    """
    m_paths = 2 ** 17  # 131072 — power of 2 required by Sobol
    dt = T / n_obs
    disc = np.exp(-r * T)

    # Sobol QRNG for n_obs dimensions
    try:
        from scipy.stats import qmc
        sampler = qmc.Sobol(d=n_obs, scramble=True, seed=42)
        u_samples = sampler.random(n=m_paths)       # shape (m_paths, n_obs)
        Z = norm.ppf(u_samples)                      # shape (m_paths, n_obs)
    except Exception:
        rng = np.random.default_rng(42)
        Z = rng.standard_normal((m_paths, n_obs))

    # GBM: log returns at each observation date
    log_returns = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    price_paths = S0 * np.exp(np.cumsum(log_returns, axis=1))  # (m_paths, n_obs)

    # Barrier monitoring: any date at which KO (L) or KI (U) is hit
    ko_hit = np.any(price_paths <= L, axis=1)   # (m_paths,) bool
    ki_hit = np.any(price_paths >= U, axis=1)   # (m_paths,) bool

    # Terminal stock price (last observation)
    ST_final = price_paths[:, -1]               # (m_paths,)
    put_payoff = np.maximum(K - ST_final, 0.0)   # (m_paths,)

    # Payoff: KO → rebate, KI → put, neither → 0
    payoff = np.where(ko_hit, rebate, np.where(ki_hit, put_payoff, 0.0))

    price = float(disc * np.mean(payoff))
    n = len(payoff)
    se = float(disc * np.std(payoff, ddof=1) / np.sqrt(n))

    # Delta: bump-and-reprice (same Sobol draws shifted by eps)
    eps = 0.01 * S0
    try:
        from scipy.stats import qmc
        sampler2 = qmc.Sobol(d=n_obs, scramble=True, seed=43)
        u2 = sampler2.random(n=m_paths)
        Z2 = norm.ppf(u2)
    except Exception:
        rng2 = np.random.default_rng(43)
        Z2 = rng2.standard_normal((m_paths, n_obs))

    price_paths_up = (S0 + eps) * np.exp(np.cumsum((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z2, axis=1))
    ko_up = np.any(price_paths_up <= L, axis=1)
    ki_up = np.any(price_paths_up >= U, axis=1)
    payoff_up = np.where(ko_up, rebate, np.where(ki_up, np.maximum(K - price_paths_up[:, -1], 0.0), 0.0))
    price_up = float(disc * np.mean(payoff_up))

    delta = (price_up - price) / eps

    return price, delta
