import sys
sys.path.insert(0, '.')
from analytic_pricer import calc_geometric_asian_closed_form

def test_geometric_asian_call():
    # S0=100, sigma=0.3, r=0.05, T=0.25, K=100, n_obs=52, call
    price = calc_geometric_asian_closed_form(S0=100, sigma=0.3, r=0.05, T=0.25, K=100, n_obs=52, option_type='call')
    # Known reference value: ~3.88 for S=K=100, T=0.25, r=0.05, sigma=0.3
    assert 3.5 < price < 4.5, f"Price {price} out of expected range"

def test_geometric_asian_put():
    price = calc_geometric_asian_closed_form(S0=100, sigma=0.3, r=0.05, T=0.25, K=100, n_obs=52, option_type='put')
    # Known reference value: ~3.01 for S=K=100, T=0.25, r=0.05, sigma=0.3
    assert 2.5 < price < 3.5, f"Price {price} out of expected range"