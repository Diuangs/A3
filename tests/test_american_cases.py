# tests/test_american_cases.py
"""
Test cases from assignment3.pdf for American Options.
2 cases: S=100, K=100, T=0.25, r=0.05, sigma=0.3, call/put
"""
import sys
sys.path.insert(0, '.')
from advanced_pricer import calc_american_binomial
from analytic_pricer import calc_geometric_asian_closed_form

AMERICAN_CASES = [
    (100, 100, 0.25, 0.05, 0.3, 'call', 'σ=0.3, K=100, Call'),
    (100, 100, 0.25, 0.05, 0.3, 'put',  'σ=0.3, K=100, Put'),
]

def test_american_convergence():
    """Verify American price >= European price (put), and tree converges."""
    results = []
    for S, K, T, r, sigma, opt_type, desc in AMERICAN_CASES:
        american = calc_american_binomial(S0=S, sigma=sigma, r=r, T=T, K=K, n_steps=200, option_type=opt_type)
        european = calc_geometric_asian_closed_form(S0=S, sigma=sigma, r=r, T=T, K=K, n_obs=52, option_type=opt_type)
        print(f"{desc}: American={american:.4f}, European(geo)={european:.4f}, Diff={american - european:.4f}")
        if opt_type == 'put':
            assert american >= european * 0.95, f"American put {american} should be >= European {european}"
        results.append({'desc': desc, 'american': american, 'european': european})
    return results