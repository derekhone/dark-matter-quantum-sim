"""DM-002 Sterile neutrino oscillation toy model - IBM Q runner.

Builds the state-prep + Trotter circuit and measures the survival probability
P(nu_mu -> nu_mu) on IBM Quantum hardware (or Aer fallback), compares against
the analytic prediction (preregistered 10% threshold).

HONEST SCOPE: toy Hamiltonian on qubits; not detection of real dark matter.
"""

from __future__ import annotations

import os

import numpy as np

from dm_sim.circuits import sterile_neutrino_circuit
from dm_sim.classical_sim import neutrino_survival_analytic
from dm_sim.metrics import match_threshold, verdict
from dm_sim.proofrecord import make_proofrecord, save_record

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")

DELTA_M2 = 1.0
ENERGY = 1.0
THETA = np.pi / 4
L_REPORT = 1.0
SHOTS = 4096
THRESHOLD_FRACTION = 0.10


def get_backend(prefer_hardware: bool = True):
    token = os.environ.get("IBMQ_TOKEN")
    if prefer_hardware and token:
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService

            service = QiskitRuntimeService(channel="ibm_quantum", token=token)
            backend = service.least_busy(operational=True, simulator=False)
            print(f"[IBM Q] using hardware backend: {backend.name}")
            return backend, "hardware"
        except Exception as exc:  # pragma: no cover - network dependent
            print(f"[IBM Q] hardware unavailable ({exc}); falling back to Aer")
    from qiskit_aer import AerSimulator

    print("[IBM Q] using local Aer simulator")
    return AerSimulator(), "aer_simulator"


def main() -> dict:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    qc = sterile_neutrino_circuit(DELTA_M2, ENERGY, THETA, L=L_REPORT, steps=6)
    backend, backend_kind = get_backend()

    from qiskit import transpile

    tqc = transpile(qc, backend)
    job = backend.run(tqc, shots=SHOTS)
    counts = job.result().get_counts()
    total = sum(counts.values())
    # survival = probability of measuring '1' (|nu_mu> = |1> in the flavor basis)
    survival_hw = counts.get("1", 0) / total

    analytic_pt = float(neutrino_survival_analytic(L_REPORT, DELTA_M2, ENERGY, THETA))
    passed = match_threshold(survival_hw, analytic_pt, THRESHOLD_FRACTION)
    v = verdict(passed, kill_triggered=False)

    record = make_proofrecord(
        experiment_id="DM-002-ibmq-v1",
        model="sterile_neutrino_2flavor",
        parameters={"delta_m2": DELTA_M2, "energy": ENERGY, "theta": THETA,
                     "L": L_REPORT, "shots": SHOTS, "backend": backend_kind},
        observable="survival_probability_P_mu_mu",
        result={"counts": counts, "survival_hw": survival_hw,
                 "analytic": analytic_pt},
        threshold="IBM Q survival within 10% of analytic",
        verdict=v,
    )
    out_path = os.path.join(RESULTS_DIR, "DM-002-ibmq-v1.proofrecord.json")
    save_record(record, out_path)

    print("=" * 70)
    print("DM-002 Sterile Neutrino - IBM Q run")
    print("=" * 70)
    print(f"  backend            : {backend_kind}")
    print(f"  counts             : {counts}")
    print(f"  survival (hw)      : {survival_hw:.4f}")
    print(f"  survival (analytic): {analytic_pt:.4f}")
    print(f"  VERDICT            : {v}")
    print(f"  record_hash        : {record['record_hash']}")
    print(f"  saved              : {out_path}")
    return record


if __name__ == "__main__":
    main()
