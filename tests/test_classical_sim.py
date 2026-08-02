"""Tests for the classical simulations and their kill conditions."""

import numpy as np

from dm_sim.classical_sim import (
    evolve,
    expectation,
    neutrino_survival_analytic,
    simulate_axion,
    simulate_neutrino,
    simulate_wimp,
    wimp_flip_analytic,
)
from dm_sim.hamiltonians import SZ


def test_evolve_preserves_norm():
    H = np.array([[0, 1], [1, 0]], dtype=complex)
    psi0 = np.array([1, 0], dtype=complex)
    psi = evolve(H, psi0, 0.7)
    assert abs(np.linalg.norm(psi) - 1.0) < 1e-12


def test_expectation_of_z_ground():
    psi = np.array([1, 0], dtype=complex)
    assert abs(expectation(SZ, psi) - 1.0) < 1e-12


def test_axion_sim_matches_true_rabi_period():
    """The classical simulation is physically correct.

    For H = w0(ZI+IZ) + lam(XX) starting from |00>, the |00>-|11> two-level
    block oscillates at the Rabi gap 2*sqrt((2 w0)^2 + lam^2), so the true
    period of <sigma_z> is pi / sqrt((2 w0)^2 + lam^2). We assert the simulator
    reproduces THIS (not the naive preregistered target 2*pi/w0). The naive
    target legitimately FAILS the preregistered 5% threshold -- and per the
    publish-regardless covenant that FAIL is recorded honestly.
    """
    omega_0, lam = 1.0, 0.3
    sim = simulate_axion(omega_0=omega_0, lam=lam)
    true_period = np.pi / np.sqrt((2 * omega_0) ** 2 + lam ** 2)
    rel = abs(sim["measured_period"] - true_period) / true_period
    assert rel <= 0.05


def test_axion_naive_threshold_fails_as_preregistered():
    """Documents the honest FAIL: measured period is NOT within 5% of 2*pi/w0."""
    sim = simulate_axion(omega_0=1.0, lam=0.3)
    rel = abs(sim["measured_period"] - sim["target_period"]) / sim["target_period"]
    assert rel > 0.05  # the naive preregistered prediction does not hold


def test_neutrino_kill_condition_clear():
    # analytic and matrix exponentiation must agree within 1%
    sim = simulate_neutrino()
    assert sim["max_abs_diff"] <= 0.01


def test_neutrino_analytic_bounds():
    L = np.linspace(0, 5, 50)
    P = neutrino_survival_analytic(L, 1.0, 1.0, np.pi / 4)
    assert np.all(P >= -1e-9)
    assert np.all(P <= 1 + 1e-9)


def test_neutrino_maximal_mixing_reaches_zero():
    # maximal mixing means survival dips to 0 somewhere
    L = np.linspace(0, 5, 500)
    P = neutrino_survival_analytic(L, 1.0, 1.0, np.pi / 4)
    assert P.min() < 1e-3


def test_wimp_kill_condition_clear():
    sim = simulate_wimp(g=1.0)
    assert sim["max_abs_diff"] <= 0.01


def test_wimp_quarter_period_full_flip():
    sim = simulate_wimp(g=1.0)
    assert abs(sim["flip_at_quarter"] - 1.0) <= 0.05


def test_wimp_analytic_closed_form():
    t = np.linspace(0, np.pi, 20)
    P = wimp_flip_analytic(1.0, t)
    assert np.allclose(P, np.sin(2 * t) ** 2)
