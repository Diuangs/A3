import sys
sys.path.insert(0, '.')
from advanced_pricer import american_binomial_price
from analytic_pricer import geometric_asian_price

def test_american_call():
    price = american_binomial_price(S=100, K=100, T=0.25, r=0.05, sigma=0.3, option_type='call', N=100)
    assert 5.5 < price < 8.0, f"Price {price} out of expected range"

def test_american_put():
    price = american_binomial_price(S=100, K=100, T=0.25, r=0.05, sigma=0.3, option_type='put', N=100)
    assert 4.5 < price < 7.0, f"Price {price} out of expected range"

def test_american_vs_european_put():
    """American put should be >= European put (early exercise premium)."""
    american = american_binomial_price(S=100, K=100, T=0.25, r=0.05, sigma=0.3, option_type='put', N=200)
    european = geometric_asian_price(S=100, K=100, T=0.25, r=0.05, sigma=0.3, option_type='put')
    assert american >= european * 0.95, f"American put {american} should be >= European {european}"