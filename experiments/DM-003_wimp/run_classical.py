"""DM-003 WIMP scattering toy model - classical simulation runner.

Compares the simulated |01> -> |10> spin-flip probability against the closed
form P = sin^2(2 g t) (kill condition: agree within 1%), checks the quarter
period flip probability against 1.0 within +/-5%, emits a ProofRecord.

HONEST SCOPE: toy Hamiltonian classical simulation only; not detection of real
dark matter.
"""

from __future__ import annotations

import os

from dm_sim.classical_sim import simulate_wimp
from dm_sim.metrics import kill_condition_triggered, match_threshold, verdict
from dm_sim.proofrecord import make_proofrecord, save_record

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")

G = 1.0
THRESHOLD_FRACTION = 0.05  # +/- 5% at the quarter period


def main() -> dict:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    sim = simulate_wimp(g=G)
    max_abs_diff = sim["max_abs_diff"]
    kill = kill_condition_triggered(max_abs_diff)

    flip_quarter = sim["flip_at_quarter"]
    passed = match_threshold(flip_quarter, 1.0, THRESHOLD_FRACTION)
    v = verdict(passed, kill_triggered=kill)

    record = make_proofrecord(
        experiment_id="DM-003-classical-v1",
        model="wimp_nucleon_exchange",
        parameters={"g": G, "coupling": "XX+YY exchange"},
        observable="spin_flip_probability_01_to_10",
        result={
            "max_abs_diff_sim_vs_closed_form": max_abs_diff,
            "t_quarter": sim["t_quarter"],
            "flip_at_quarter": flip_quarter,
            "closed_form_at_quarter": 1.0,
        },
        threshold="P = sin^2(2 g t) +/- 5% at t = pi/(4g); kill if >1% sim-vs-closed",
        verdict=v,
    )

    out_path = os.path.join(RESULTS_DIR, "DM-003-classical-v1.proofrecord.json")
    save_record(record, out_path)

    print("=" * 70)
    print("DM-003 WIMP Scattering Toy Model - classical simulation")
    print("=" * 70)
    print(f"  g                        : {G}")
    print(f"  max |sim - closed form|  : {max_abs_diff:.3e}")
    print(f"  kill condition (>1%)     : {'TRIGGERED' if kill else 'clear'}")
    print(f"  t_quarter = pi/(4g)      : {sim['t_quarter']:.6f}")
    print(f"  flip prob at quarter     : {flip_quarter:.6f} (target 1.0)")
    print(f"  VERDICT                  : {v}")
    print(f"  record_hash              : {record['record_hash']}")
    print(f"  saved                    : {out_path}")
    return record


if __name__ == "__main__":
    main()
