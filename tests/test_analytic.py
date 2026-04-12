import sys
sys.path.insert(0, '.')
from analytic_pricer import geometric_asian_price

def test_geometric_asian_call():
    # S=100, K=100, T=0.25, r=0.05, sigma=0.3, call
    price = geometric_asian_price(S=100, K=100, T=0.25, r=0.05, sigma=0.3, option_type='call')
    # Known reference value: ~3.88 for S=K=100, T=0.25, r=0.05, sigma=0.3
    assert 3.5 < price < 4.5, f"Price {price} out of expected range"

def test_geometric_asian_put():
    price = geometric_asian_price(S=100, K=100, T=0.25, r=0.05, sigma=0.3, option_type='put')
    # Known reference value: ~3.01 for S=K=100, T=0.25, r=0.05, sigma=0.3
    assert 2.5 < price < 3.5, f"Price {price} out of expected range"