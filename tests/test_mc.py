import sys
sys.path.insert(0, '.')
from mc_pricer import calc_arithmetic_asian_mc

def test_arithmetic_asian_call_with_cv():
    res = calc_arithmetic_asian_mc(
        S0=100, sigma=0.3, r=0.05, T=0.25, K=100,
        n_obs=52, option_type='call', m_paths=50000, use_cv=True
    )
    price = res["Price"]
    lo = res["CI_Lower"]
    hi = res["CI_Upper"]
    assert lo < price < hi, "price must be within CI"
    assert 3.5 < price < 4.5, f"Price {price} out of expected range"

def test_arithmetic_asian_put_with_cv():
    res = calc_arithmetic_asian_mc(
        S0=100, sigma=0.3, r=0.05, T=0.25, K=100,
        n_obs=52, option_type='put', m_paths=50000, use_cv=True
    )
    price = res["Price"]
    lo = res["CI_Lower"]
    hi = res["CI_Upper"]
    assert 2.5 < price < 3.5, f"Price {price} out of expected range"

def test_95_ci_width():
    res = calc_arithmetic_asian_mc(
        S0=100, sigma=0.3, r=0.05, T=0.25, K=100,
        n_obs=52, option_type='call', m_paths=100000, use_cv=True
    )
    width = res["CI_Upper"] - res["CI_Lower"]
    assert width < 1.0, f"CI width {width} too large for 100k paths"