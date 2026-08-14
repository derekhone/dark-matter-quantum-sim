"""DM-005 Majorana Mass Seesaw - IBM Quantum runner.

Trotterized circuit for H = m_D(X(x)X) + (M_R/2)(I(x)Z).
Initial state |00>. Measures P(|11>) = lepton-number-violation probability.

HONEST SCOPE: toy Hamiltonian on 2 qubits; not detection of Majorana neutrinos.
"""

from __future__ import annotations

import json
import os
import hashlib
from datetime import datetime, timezone

import numpy as np

M_D = 0.5
M_R = 2.0
OMEGA = np.sqrt(M_D**2 + (M_R / 2.0) ** 2)
T_EVOLVE = np.pi / (2.0 * OMEGA)  # first peak of LNV probability
TROTTER_STEPS = 6
SHOTS = 4096

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")


def build_circuit():
    """Trotterized exp(-i H t) for the Majorana seesaw Hamiltonian.

    H = m_D (X(x)X) + (M_R/2) (I(x)Z)

    First-order Trotter:
      exp(-i H dt) ~ exp(-i m_D X(x)X dt) exp(-i (M_R/2) I(x)Z dt)

    XX interaction: Hadamard-CNOT-RZ-CNOT-Hadamard.
    I(x)Z: RZ on qubit 1.
    """
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(2, 2)

    # Initial state |00> (no state prep needed, this is the default)
    dt = T_EVOLVE / TROTTER_STEPS
    for _ in range(TROTTER_STEPS):
        # exp(-i m_D dt X(x)X): Hadamard-CNOT-RZ-CNOT-Hadamard
        qc.h(0)
        qc.h(1)
        qc.cx(0, 1)
        qc.rz(2 * M_D * dt, 1)
        qc.cx(0, 1)
        qc.h(0)
        qc.h(1)
        # exp(-i (M_R/2) dt I(x)Z): RZ on qubit 1
        qc.rz(2 * (M_R / 2.0) * dt, 1)

    qc.measure([0, 1], [0, 1])
    return qc


def main():
    """Submit the circuit to IBM Quantum and process results."""
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=2)
    print(f"Backend: {backend.name}")

    qc = build_circuit()
    sampler = SamplerV2(mode=backend)
    job = sampler.run([qc], shots=SHOTS)
    print(f"Job ID: {job.job_id()}")
    print("Waiting for results...")

    result = job.result()
    counts = result[0].data.meas.get_counts()
    print(f"Raw counts: {counts}")

    # Parse: P(|11>) = LNV probability
    total = sum(counts.values())
    n_11 = counts.get("11", 0)
    P_lnv_hw = n_11 / total

    # Analytic prediction
    P_max_analytic = (M_D / OMEGA) ** 2

    rel_err = abs(P_lnv_hw - P_max_analytic) / P_max_analytic if P_max_analytic > 0 else 0
    passed = rel_err <= 0.10  # 10% threshold for hardware
    v = "PASS" if passed else "FAIL"

    print(f"P_LNV (hw)      : {P_lnv_hw:.4f}")
    print(f"P_max (analytic) : {P_max_analytic:.4f}")
    print(f"Relative error   : {rel_err*100:.2f}%")
    print(f"VERDICT          : {v}")

    # Build ProofRecord
    os.makedirs(RESULTS_DIR, exist_ok=True)
    record = {
        "experiment_id": "DM-005-ibmq-v1",
        "series": "dark-matter-quantum-sim",
        "model": "majorana_seesaw_mixing",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parameters": {
            "m_D": M_D,
            "M_R": M_R,
            "Omega": OMEGA,
            "t_evolve": T_EVOLVE,
            "trotter_steps": TROTTER_STEPS,
            "shots": SHOTS,
            "backend": backend.name,
            "job_id": job.job_id(),
        },
        "observable": "lepton_number_violation_probability",
        "result": {
            "P_lnv_hw": P_lnv_hw,
            "P_max_analytic": P_max_analytic,
            "relative_error": rel_err,
            "raw_counts": counts,
        },
        "threshold": "hw LNV prob within 10% of analytic P_max",
        "verdict": v,
        "honest_scope": (
            "toy Hamiltonian on IBM Q hardware; not detection of real "
            "Majorana neutrinos or dark matter"
        ),
    }
    payload = {k: v for k, v in record.items() if k != "record_hash"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    record["record_hash"] = hashlib.sha256(canonical.encode()).hexdigest()

    out_path = os.path.join(RESULTS_DIR, "DM-005-ibmq-v1.proofrecord.json")
    with open(out_path, "w") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    print(f"Saved: {out_path}")
    return record


if __name__ == "__main__":
    main()
