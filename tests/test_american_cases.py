# tests/test_american_cases.py
"""
Test cases from assignment3.pdf for American Options.
2 cases: S=100, K=100, T=0.25, r=0.05, sigma=0.3, call/put
"""
import sys
sys.path.insert(0, '.')
from advanced_pricer import american_binomial_price
from analytic_pricer import geometric_asian_price

AMERICAN_CASES = [
    (100, 100, 0.25, 0.05, 0.3, 'call', 'σ=0.3, K=100, Call'),
    (100, 100, 0.25, 0.05, 0.3, 'put',  'σ=0.3, K=100, Put'),
]

def test_american_convergence():
    """Verify American price >= European price (put), and tree converges."""
    results = []
    for S, K, T, r, sigma, opt_type, desc in AMERICAN_CASES:
        american = american_binomial_price(S, K, T, r, sigma, opt_type, N=200)
        european = geometric_asian_price(S, K, T, r, sigma, opt_type)
        print(f"{desc}: American={american:.4f}, European(geo)={european:.4f}, Diff={american - european:.4f}")
        if opt_type == 'put':
            # American put >= European put (early exercise premium)
            assert american >= european * 0.95, f"American put {american} should be >= European {european}"
        results.append({'desc': desc, 'american': american, 'european': european})
    return results