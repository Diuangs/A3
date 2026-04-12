# tests/test_integration.py
"""
Integration test: verify all Member B functions are importable and work together.
"""
import sys
sys.path.insert(0, '.')

def test_all_imports():
    """Verify all functions are importable."""
    from analytic_pricer import calc_geometric_asian_closed_form
    from mc_pricer import calc_arithmetic_asian_mc
    from advanced_pricer import calc_american_binomial
    print("All imports OK")

def test_smoke_all():
    """Smoke test all functions with S=100, K=100, T=0.25, r=0.05, sigma=0.3."""
    from analytic_pricer import calc_geometric_asian_closed_form
    from mc_pricer import calc_arithmetic_asian_mc
    from advanced_pricer import calc_american_binomial

    # Geometric Asian
    g = calc_geometric_asian_closed_form(S0=100, sigma=0.3, r=0.05, T=0.25, K=100, n_obs=52, option_type='call')
    print(f"Geometric Asian call: {g:.4f}")
    assert isinstance(g, float)

    # Arithmetic Asian MC with CV (returns dict)
    res = calc_arithmetic_asian_mc(S0=100, sigma=0.3, r=0.05, T=0.25, K=100, n_obs=52, option_type='call', m_paths=10000, use_cv=True)
    print(f"Arithmetic Asian call: {res['Price']:.4f} [{res['CI_Lower']:.4f}, {res['CI_Upper']:.4f}]")
    assert res['CI_Lower'] < res['Price'] < res['CI_Upper']

    # American Binomial
    am = calc_american_binomial(S0=100, sigma=0.3, r=0.05, T=0.25, K=100, n_steps=100, option_type='put')
    print(f"American Binomial put: {am:.4f}")
    assert isinstance(am, float)

def test_function_signatures():
    """Verify function signatures match the required spec."""
    import inspect
    from analytic_pricer import calc_geometric_asian_closed_form
    from mc_pricer import calc_arithmetic_asian_mc
    from advanced_pricer import calc_american_binomial

    # Check calc_geometric_asian_closed_form params
    sig = inspect.signature(calc_geometric_asian_closed_form)
    params = list(sig.parameters.keys())
    assert params == ['S0', 'sigma', 'r', 'T', 'K', 'n_obs', 'option_type'], f"Got {params}"

    # Check calc_arithmetic_asian_mc returns dict
    res = calc_arithmetic_asian_mc(S0=100, sigma=0.3, r=0.05, T=0.25, K=100, n_obs=52, option_type='call', m_paths=1000, use_cv=True)
    assert isinstance(res, dict) and set(res.keys()) == {"Price", "CI_Lower", "CI_Upper", "StdError"}, \
        f"Expected dict with keys Price/CI_Lower/CI_Upper/StdError, got {type(res)}"

    # Check calc_american_binomial params
    sig = inspect.signature(calc_american_binomial)
    params = list(sig.parameters.keys())
    assert params == ['S0', 'sigma', 'r', 'T', 'K', 'n_steps', 'option_type'], f"Got {params}"
    print("All signatures OK")