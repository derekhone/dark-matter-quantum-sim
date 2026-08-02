"""DM-002 Sterile neutrino oscillation toy model - classical simulation runner.

Compares the analytic 2-flavor survival probability against an exact
matrix-exponentiation cross-check (kill condition: must agree within 1%),
evaluates the preregistered threshold, emits a ProofRecord.

HONEST SCOPE: toy Hamiltonian classical simulation only; not detection of real
dark matter.
"""

from __future__ import annotations

import os

import numpy as np

from dm_sim.classical_sim import neutrino_survival_analytic, simulate_neutrino
from dm_sim.metrics import kill_condition_triggered, match_threshold, verdict
from dm_sim.proofrecord import make_proofrecord, save_record

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")

DELTA_M2 = 1.0          # eV^2 (light sterile neutrino candidate range)
ENERGY = 1.0            # GeV (analogue units)
THETA = np.pi / 4       # maximal mixing
THRESHOLD_FRACTION = 0.10  # 10% (loose; accounts for hardware noise)
L_REPORT = 1.0          # baseline at which the point verdict is reported


def main() -> dict:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    sim = simulate_neutrino(delta_m2=DELTA_M2, energy=ENERGY, theta=THETA)
    max_abs_diff = sim["max_abs_diff"]
    kill = kill_condition_triggered(max_abs_diff)

    # reported point
    analytic_pt = float(neutrino_survival_analytic(L_REPORT, DELTA_M2, ENERGY, THETA))
    # nearest matrix sample to L_REPORT
    idx = int(np.argmin(np.abs(sim["L"] - L_REPORT)))
    matrix_pt = float(sim["matrix"][idx])

    passed = match_threshold(matrix_pt, analytic_pt, THRESHOLD_FRACTION)
    v = verdict(passed, kill_triggered=kill)

    record = make_proofrecord(
        experiment_id="DM-002-classical-v1",
        model="sterile_neutrino_2flavor",
        parameters={
            "delta_m2": DELTA_M2,
            "energy": ENERGY,
            "theta": THETA,
            "mixing": "maximal (pi/4)",
        },
        observable="survival_probability_P_mu_mu",
        result={
            "max_abs_diff_analytic_vs_matrix": max_abs_diff,
            "L_report": L_REPORT,
            "analytic_at_L": analytic_pt,
            "matrix_at_L": matrix_pt,
            "min_survival": float(sim["analytic"].min()),
            "max_survival": float(sim["analytic"].max()),
        },
        threshold="matrix vs analytic within 10%; kill if >1% classical-vs-analytic",
        verdict=v,
    )

    out_path = os.path.join(RESULTS_DIR, "DM-002-classical-v1.proofrecord.json")
    save_record(record, out_path)

    print("=" * 70)
    print("DM-002 Sterile Neutrino Oscillation Toy Model - classical simulation")
    print("=" * 70)
    print(f"  delta_m2 (eV^2)          : {DELTA_M2}")
    print(f"  energy                   : {ENERGY}")
    print(f"  theta                    : pi/4 (maximal mixing)")
    print(f"  max |analytic - matrix|  : {max_abs_diff:.3e}")
    print(f"  kill condition (>1%)     : {'TRIGGERED' if kill else 'clear'}")
    print(f"  analytic P(mu->mu) @L=1  : {analytic_pt:.6f}")
    print(f"  matrix   P(mu->mu) @L=1  : {matrix_pt:.6f}")
    print(f"  VERDICT                  : {v}")
    print(f"  record_hash              : {record['record_hash']}")
    print(f"  saved                    : {out_path}")
    return record


if __name__ == "__main__":
    main()
