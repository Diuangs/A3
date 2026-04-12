# tests/test_integration.py
"""
Integration test: verify all Member B functions are importable and work together.
"""
import sys
sys.path.insert(0, '.')

def test_all_imports():
    """Verify all functions are importable."""
    from analytic_pricer import geometric_asian_price
    from mc_pricer import arithmetic_asian_price, compute_95_ci
    from advanced_pricer import american_binomial_price
    print("All imports OK")

def test_smoke_all():
    """Smoke test all functions with S=100, K=100, T=0.25, r=0.05, sigma=0.3."""
    from analytic_pricer import geometric_asian_price
    from mc_pricer import arithmetic_asian_price, compute_95_ci
    from advanced_pricer import american_binomial_price

    # Geometric Asian
    g = geometric_asian_price(100, 100, 0.25, 0.05, 0.3, 'call')
    print(f"Geometric Asian call: {g:.4f}")
    assert isinstance(g, float)

    # Arithmetic Asian MC with CV
    a, lo, hi = arithmetic_asian_price(100, 100, 0.25, 0.05, 0.3, 'call', n_paths=10000, seed=42)
    print(f"Arithmetic Asian call: {a:.4f} [{lo:.4f}, {hi:.4f}]")
    assert lo < a < hi

    # American Binomial
    am = american_binomial_price(100, 100, 0.25, 0.05, 0.3, 'put', N=100)
    print(f"American Binomial put: {am:.4f}")
    assert isinstance(am, float)

def test_function_signatures():
    """Verify function signatures match Member A's GUI expectations."""
    import inspect
    from analytic_pricer import geometric_asian_price
    from mc_pricer import arithmetic_asian_price
    from advanced_pricer import american_binomial_price

    # Check geometric_asian_price params
    sig = inspect.signature(geometric_asian_price)
    params = list(sig.parameters.keys())
    assert 'S' in params and 'K' in params and 'T' in params
    assert 'r' in params and 'sigma' in params and 'option_type' in params

    # Check arithmetic_asian_price returns tuple
    from mc_pricer import arithmetic_asian_price
    result = arithmetic_asian_price(100, 100, 0.25, 0.05, 0.3, 'call', n_paths=1000, seed=42)
    assert isinstance(result, tuple) and len(result) == 3, f"Expected 3-tuple, got {type(result)}"

    # Check american_binomial_price params
    sig = inspect.signature(american_binomial_price)
    params = list(sig.parameters.keys())
    assert 'S' in params and 'K' in params and 'N' in params
    print("All signatures OK")