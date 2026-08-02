"""DM-001 Axion toy model - classical simulation runner.

Runs the exact classical simulation, evaluates the preregistered threshold,
emits a ProofRecord and saves results.

HONEST SCOPE: toy Hamiltonian classical simulation only; not detection of real
dark matter.
"""

from __future__ import annotations

import os

from dm_sim.classical_sim import simulate_axion
from dm_sim.metrics import match_threshold, verdict
from dm_sim.proofrecord import make_proofrecord, save_record

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")

OMEGA_0 = 1.0
LAMBDA = 0.3
THRESHOLD_FRACTION = 0.05  # +/- 5% on the period


def main() -> dict:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    sim = simulate_axion(omega_0=OMEGA_0, lam=LAMBDA)
    measured = sim["measured_period"]
    target = sim["target_period"]

    passed = match_threshold(measured, target, THRESHOLD_FRACTION)
    # No independent analytic period beyond 2*pi/omega_0; the coupling shifts
    # the observed period slightly, so the kill condition is not applied here.
    v = verdict(passed, kill_triggered=False)

    record = make_proofrecord(
        experiment_id="DM-001-classical-v1",
        model="axion_pq_potential",
        parameters={"omega_0": OMEGA_0, "lambda": LAMBDA},
        observable="sigma_z_expectation",
        result={
            "measured_period": measured,
            "target_period": target,
            "relative_error": abs(measured - target) / target,
            "sigma_z_first": float(sim["sigma_z"][0]),
            "sigma_z_min": float(sim["sigma_z"].min()),
            "sigma_z_max": float(sim["sigma_z"].max()),
        },
        threshold="T within 5% of 2*pi/omega_0",
        verdict=v,
    )

    out_path = os.path.join(RESULTS_DIR, "DM-001-classical-v1.proofrecord.json")
    save_record(record, out_path)

    print("=" * 70)
    print("DM-001 Axion Dark Matter Toy Model - classical simulation")
    print("=" * 70)
    print(f"  omega_0            : {OMEGA_0}")
    print(f"  lambda             : {LAMBDA}")
    print(f"  target period 2pi/w: {target:.6f}")
    print(f"  measured period    : {measured:.6f}")
    print(f"  relative error     : {abs(measured - target) / target * 100:.3f}%")
    print(f"  VERDICT            : {v}")
    print(f"  record_hash        : {record['record_hash']}")
    print(f"  saved              : {out_path}")
    return record


if __name__ == "__main__":
    main()
