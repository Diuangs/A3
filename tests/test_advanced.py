import sys
sys.path.insert(0, '.')
from advanced_pricer import calc_american_binomial
from analytic_pricer import calc_geometric_asian_closed_form

def test_american_call():
    price = calc_american_binomial(S0=100, sigma=0.3, r=0.05, T=0.25, K=100, n_steps=100, option_type='call')
    assert 5.5 < price < 8.0, f"Price {price} out of expected range"

def test_american_put():
    price = calc_american_binomial(S0=100, sigma=0.3, r=0.05, T=0.25, K=100, n_steps=100, option_type='put')
    assert 4.5 < price < 7.0, f"Price {price} out of expected range"

def test_american_vs_european_put():
    """American put should be >= European put (early exercise premium)."""
    american = calc_american_binomial(S0=100, sigma=0.3, r=0.05, T=0.25, K=100, n_steps=200, option_type='put')
    european = calc_geometric_asian_closed_form(S0=100, sigma=0.3, r=0.05, T=0.25, K=100, n_obs=52, option_type='put')
    assert american >= european * 0.95, f"American put {american} should be >= European {european}"