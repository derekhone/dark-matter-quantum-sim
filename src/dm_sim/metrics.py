"""Metrics and verdict logic for the dark-matter-quantum-sim series.

Provides fidelity/agreement helpers and the PASS / FAIL / HOLD verdict logic
that maps preregistered thresholds onto computed results.
"""

from __future__ import annotations

import numpy as np

PASS = "PASS"
FAIL = "FAIL"
HOLD = "HOLD"

# Kill condition tolerance from PREREGISTRATION.md section 3.
KILL_TOL = 0.01  # classical vs analytic must agree within 1%


def compute_fidelity(a: np.ndarray, b: np.ndarray) -> float:
    """State fidelity |<a|b>|^2 for two (normalized) state vectors."""
    a = np.asarray(a, dtype=complex)
    b = np.asarray(b, dtype=complex)
    overlap = np.vdot(a, b)
    return float(np.abs(overlap) ** 2)


def relative_error(measured: float, reference: float) -> float:
    """Absolute relative error |measured - reference| / |reference|.

    Falls back to absolute error when the reference is ~0.
    """
    if abs(reference) < 1e-12:
        return abs(measured - reference)
    return abs(measured - reference) / abs(reference)


def match_threshold(measured: float, reference: float, tol_fraction: float) -> bool:
    """True iff measured is within tol_fraction (e.g. 0.05 = 5%) of reference."""
    return relative_error(measured, reference) <= tol_fraction


def kill_condition_triggered(max_abs_diff: float, tol: float = KILL_TOL) -> bool:
    """True iff the classical vs analytic max abs difference exceeds tol."""
    return max_abs_diff > tol


def verdict(passed: bool, kill_triggered: bool = False) -> str:
    """Map (passed, kill) onto a PASS / FAIL / HOLD verdict.

    If the kill condition is triggered the classical layer is untrustworthy,
    so no physics verdict is issued and we return HOLD.
    """
    if kill_triggered:
        return HOLD
    return PASS if passed else FAIL


__all__ = [
    "PASS",
    "FAIL",
    "HOLD",
    "KILL_TOL",
    "compute_fidelity",
    "relative_error",
    "match_threshold",
    "kill_condition_triggered",
    "verdict",
]
