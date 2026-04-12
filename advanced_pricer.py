import numpy as np
from scipy.stats import norm, qmc

def calc_kiko_put_qmc(S0, sigma, r, T, K, L, U, n_obs, R, m_paths=100000):
    """
    使用拟蒙特卡洛(QMC - Sobol序列)计算 KIKO Put Option 的价格和 Delta
    """
    # 将观察次数转换为整数
    n_obs = int(n_obs)
    dt = T / n_obs
    
    # 1. 生成 Sobol 序列 (QMC 核心)
    # 强制将种子设为 42，保持模拟实验的基准一致性
    sampler = qmc.Sobol(d=n_obs, scramble=True, seed=42)
    # 取样并使用逆变换法(ppf)映射到标准正态分布 Z
    uniform_samples = sampler.random(n=int(m_paths))
    Z_matrix = norm.ppf(uniform_samples)
    
    # 定义一个内部闭包函数来评估给定初始价格的期望收益
    # 这样做是为了复用同一个 Z_matrix 来计算 Delta，消除随机噪声带来的误差
    def evaluate_expected_payoff(start_price):
        payoffs = np.zeros(m_paths)
        S = np.full(m_paths, float(start_price))
        
        # 状态标记
        knocked_in = np.zeros(m_paths, dtype=bool) # 是否曾经触碰过下限 L
        active = np.ones(m_paths, dtype=bool)      # 期权是否仍然存续（未被敲出）
        
        drift = (r - 0.5 * sigma**2) * dt
        vol = sigma * np.sqrt(dt)
        
        # 按时间步迭代
        for i in range(n_obs):
            # 仅对仍在存续的路径更新资产价格
            S[active] = S[active] * np.exp(drift + vol * Z_matrix[active, i])
            
            # 条件 1：检查是否敲出 (S >= U)
            knock_out_mask = active & (S >= U)
            # 敲出时立即获得返还金 R，并折现到 t=0
            payoffs[knock_out_mask] = R * np.exp(-r * (i + 1) * dt)
            active[knock_out_mask] = False # 这些路径终止
            
            # 条件 2：检查是否敲入 (S <= L)
            # 只要在此前或当前步触碰过 L，且尚未敲出，就标记为 True
            knocked_in = knocked_in | (active & (S <= L))
            
        # 到期日处理：未被敲出且曾经敲入的路径，获得普通 Put 收益
        survived = active & knocked_in
        payoffs[survived] = np.maximum(K - S[survived], 0) * np.exp(-r * T)
        
        return np.mean(payoffs)

    # 2. 计算基准期权价格
    base_price = evaluate_expected_payoff(S0)
    
    # 3. 计算 Delta (使用中心差分法)
    bump = S0 * 0.01  # 上下浮动 1%
    price_up = evaluate_expected_payoff(S0 + bump)
    price_down = evaluate_expected_payoff(S0 - bump)
    delta = (price_up - price_down) / (2 * bump)
    
    return {
        "Price": base_price,
        "Delta": delta
    }