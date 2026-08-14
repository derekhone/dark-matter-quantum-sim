"""DM-004 Dark Photon Kinetic Mixing - classical simulation runner.

Compares the simulated gamma -> dark photon conversion probability against the
analytic off-resonance oscillation formula (kill condition: agree within 1%),
checks the peak conversion probability against the analytic P_max within +/-5%,
emits a ProofRecord.

HONEST SCOPE: toy Hamiltonian classical simulation only; not detection of real
dark matter or dark photons.
"""

from __future__ import annotations

import os
import sys

import numpy as np
from scipy.linalg import expm

# ---------------------------------------------------------------------------
# Inline physics (self-contained runner — no package install required)
# ---------------------------------------------------------------------------
I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def kron(*ops):
    out = np.array([[1.0 + 0j]])
    for op in ops:
        out = np.kron(out, op)
    return out


def dark_photon_hamiltonian(omega_gamma, omega_dark, epsilon):
    return (omega_gamma * kron(SZ, I2)
            + omega_dark * kron(I2, SZ)
            + epsilon * kron(SX, SX))


def evolve(H, psi0, t):
    return expm(-1j * H * t) @ psi0


def dark_photon_conversion_analytic(t, omega_gamma, omega_dark, epsilon):
    t = np.asarray(t, dtype=float)
    Delta = omega_gamma - omega_dark
    Omega = np.sqrt(Delta**2 + epsilon**2)
    P_max = epsilon**2 / (Delta**2 + epsilon**2)
    return P_max * np.sin(Omega * t) ** 2


# ---------------------------------------------------------------------------
# ProofRecord helpers (inline to avoid import issues)
# ---------------------------------------------------------------------------
import hashlib
import json
from datetime import datetime, timezone

SERIES = "dark-matter-quantum-sim"
HONEST_SCOPE = (
    "toy Hamiltonian classical simulation only; not detection of real dark "
    "matter or dark photons"
)


def _canonical_json(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"),
                      default=_default)


def _default(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def compute_record_hash(record):
    payload = {k: v for k, v in record.items() if k != "record_hash"}
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def make_proofrecord(experiment_id, model, parameters, observable, result,
                     threshold, verdict, *, series=SERIES,
                     honest_scope=HONEST_SCOPE, timestamp_utc=None):
    record = {
        "experiment_id": experiment_id,
        "series": series,
        "model": model,
        "timestamp_utc": timestamp_utc or datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "parameters": parameters,
        "observable": observable,
        "result": result,
        "threshold": threshold,
        "verdict": verdict,
        "honest_scope": honest_scope,
    }
    record["record_hash"] = compute_record_hash(record)
    return record


def save_record(record, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, default=_default)
        fh.write("\n")

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
KILL_TOL = 0.01


def relative_error(measured, reference):
    if abs(reference) < 1e-12:
        return abs(measured - reference)
    return abs(measured - reference) / abs(reference)


def match_threshold(measured, reference, tol_fraction):
    return relative_error(measured, reference) <= tol_fraction


def kill_condition_triggered(max_abs_diff, tol=KILL_TOL):
    return max_abs_diff > tol


def verdict_fn(passed, kill_triggered=False):
    if kill_triggered:
        return "HOLD"
    return "PASS" if passed else "FAIL"


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")

OMEGA_GAMMA = 1.0
OMEGA_DARK = 1.3
EPSILON = 0.5
THRESHOLD_FRACTION = 0.05  # +/- 5%


def main() -> dict:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Build Hamiltonian and simulate
    H = dark_photon_hamiltonian(OMEGA_GAMMA, OMEGA_DARK, EPSILON)
    psi0 = np.zeros(4, dtype=complex)
    psi0[2] = 1.0  # |10> (one visible photon, no dark photon)

    n_steps = 500
    t_max = 15.0
    times = np.linspace(0.0, t_max, n_steps)
    analytic = dark_photon_conversion_analytic(
        times, OMEGA_GAMMA, OMEGA_DARK, EPSILON)

    conversion_sim = np.empty(n_steps)
    for i, t in enumerate(times):
        psi = evolve(H, psi0, t)
        conversion_sim[i] = float(np.abs(psi[1]) ** 2)  # P(|01>)

    max_abs_diff = float(np.max(np.abs(analytic - conversion_sim)))
    kill = kill_condition_triggered(max_abs_diff)

    # Evaluate at first peak
    Delta = OMEGA_GAMMA - OMEGA_DARK
    Omega = np.sqrt(Delta**2 + EPSILON**2)
    t_peak = np.pi / (2.0 * Omega)
    P_max_analytic = EPSILON**2 / (Delta**2 + EPSILON**2)

    psi_peak = evolve(H, psi0, t_peak)
    P_max_sim = float(np.abs(psi_peak[1]) ** 2)

    passed = match_threshold(P_max_sim, P_max_analytic, THRESHOLD_FRACTION)
    v = verdict_fn(passed, kill_triggered=kill)

    record = make_proofrecord(
        experiment_id="DM-004-classical-v1",
        model="dark_photon_kinetic_mixing",
        parameters={
            "omega_gamma": OMEGA_GAMMA,
            "omega_dark": OMEGA_DARK,
            "epsilon": EPSILON,
            "Delta": Delta,
            "Omega": Omega,
        },
        observable="gamma_to_dark_photon_conversion_probability",
        result={
            "max_abs_diff_sim_vs_analytic": max_abs_diff,
            "t_peak": t_peak,
            "P_max_sim": P_max_sim,
            "P_max_analytic": P_max_analytic,
            "relative_error": relative_error(P_max_sim, P_max_analytic),
        },
        threshold=(
            "P_max within 5% of eps^2/(Delta^2+eps^2); "
            "kill if sim vs analytic >1%"
        ),
        verdict=v,
    )

    out_path = os.path.join(RESULTS_DIR, "DM-004-classical-v1.proofrecord.json")
    save_record(record, out_path)

    print("=" * 70)
    print("DM-004 Dark Photon Kinetic Mixing - classical simulation")
    print("=" * 70)
    print(f"  omega_gamma          : {OMEGA_GAMMA}")
    print(f"  omega_dark           : {OMEGA_DARK}")
    print(f"  epsilon              : {EPSILON}")
    print(f"  Delta                : {Delta:.4f}")
    print(f"  Omega                : {Omega:.6f}")
    print(f"  max |sim - analytic| : {max_abs_diff:.3e}")
    print(f"  kill condition (>1%) : {'TRIGGERED' if kill else 'clear'}")
    print(f"  t_peak = pi/(2 Omega): {t_peak:.6f}")
    print(f"  P_max (sim)          : {P_max_sim:.6f}")
    print(f"  P_max (analytic)     : {P_max_analytic:.6f}")
    print(f"  relative error       : {relative_error(P_max_sim, P_max_analytic)*100:.4f}%")
    print(f"  VERDICT              : {v}")
    print(f"  record_hash          : {record['record_hash']}")
    print(f"  saved                : {out_path}")
    return record


if __name__ == "__main__":
    main()
