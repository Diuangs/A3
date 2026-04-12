import sys
sys.path.insert(0, '.')
from mc_pricer import arithmetic_asian_price, compute_95_ci

def test_arithmetic_asian_call_with_cv():
    price, lo, hi = arithmetic_asian_price(
        S=100, K=100, T=0.25, r=0.05, sigma=0.3,
        option_type='call', n_paths=50000, seed=42
    )
    assert lo < price < hi, "price must be within CI"
    # CV shifts price toward geometric Asian (~3.877); actual ~3.94
    assert 3.5 < price < 4.5, f"Price {price} out of expected range"

def test_arithmetic_asian_put_with_cv():
    price, lo, hi = arithmetic_asian_price(
        S=100, K=100, T=0.25, r=0.05, sigma=0.3,
        option_type='put', n_paths=50000, seed=42
    )
    # CV shifts price toward geometric Asian (~3.009); actual ~2.89
    assert 2.5 < price < 3.5, f"Price {price} out of expected range"

def test_95_ci_width():
    _, lo, hi = arithmetic_asian_price(S=100, K=100, T=0.25, r=0.05, sigma=0.3, n_paths=100000, seed=42)
    width = hi - lo
    assert width < 1.0, f"CI width {width} too large for 100k paths"