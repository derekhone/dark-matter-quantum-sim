"""DM-004 Dark Photon Kinetic Mixing - IBM Quantum runner.

Trotterized circuit for H = omega_gamma(Z(x)I) + omega_dark(I(x)Z) + eps(X(x)X).
Initial state |10> (one visible photon). Measures P(|01>) = conversion probability.

HONEST SCOPE: toy Hamiltonian on 2 qubits; not detection of real dark photons.
"""

from __future__ import annotations

import json
import os
import hashlib
from datetime import datetime, timezone

import numpy as np

OMEGA_GAMMA = 1.0
OMEGA_DARK = 1.3
EPSILON = 0.5
T_EVOLVE = 2.693893  # pi / (2 Omega), first peak of conversion
TROTTER_STEPS = 6
SHOTS = 4096

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")


def build_circuit():
    """Trotterized exp(-i H t) for the dark photon kinetic mixing Hamiltonian.

    H = omega_gamma (Z(x)I) + omega_dark (I(x)Z) + epsilon (X(x)X)

    First-order Trotter decomposition:
      exp(-i H dt) ~ exp(-i omega_gamma Z(x)I dt)
                      exp(-i omega_dark I(x)Z dt)
                      exp(-i epsilon X(x)X dt)
    repeated `steps` times.

    Z rotation: exp(-i alpha Z) = RZ(2 alpha)
    XX interaction: CNOT-RZ-CNOT sandwich in Hadamard basis.
    """
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(2, 2)

    # State prep: |10> (qubit0 = 1, qubit1 = 0)
    qc.x(0)

    dt = T_EVOLVE / TROTTER_STEPS
    for _ in range(TROTTER_STEPS):
        # exp(-i omega_gamma dt Z(x)I): RZ on qubit 0
        qc.rz(2 * OMEGA_GAMMA * dt, 0)
        # exp(-i omega_dark dt I(x)Z): RZ on qubit 1
        qc.rz(2 * OMEGA_DARK * dt, 1)
        # exp(-i epsilon dt X(x)X): Hadamard-CNOT-RZ-CNOT-Hadamard
        qc.h(0)
        qc.h(1)
        qc.cx(0, 1)
        qc.rz(2 * EPSILON * dt, 1)
        qc.cx(0, 1)
        qc.h(0)
        qc.h(1)

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

    # Parse: P(|01>) = conversion probability
    total = sum(counts.values())
    n_01 = counts.get("01", 0)
    P_conv_hw = n_01 / total

    # Analytic prediction
    Delta = OMEGA_GAMMA - OMEGA_DARK
    Omega = np.sqrt(Delta**2 + EPSILON**2)
    P_max_analytic = EPSILON**2 / (Delta**2 + EPSILON**2)

    rel_err = abs(P_conv_hw - P_max_analytic) / P_max_analytic if P_max_analytic > 0 else 0
    passed = rel_err <= 0.10  # 10% threshold for hardware
    v = "PASS" if passed else "FAIL"

    print(f"P_conversion (hw): {P_conv_hw:.4f}")
    print(f"P_max (analytic) : {P_max_analytic:.4f}")
    print(f"Relative error   : {rel_err*100:.2f}%")
    print(f"VERDICT          : {v}")

    # Build ProofRecord
    os.makedirs(RESULTS_DIR, exist_ok=True)
    record = {
        "experiment_id": "DM-004-ibmq-v1",
        "series": "dark-matter-quantum-sim",
        "model": "dark_photon_kinetic_mixing",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parameters": {
            "omega_gamma": OMEGA_GAMMA,
            "omega_dark": OMEGA_DARK,
            "epsilon": EPSILON,
            "t_evolve": T_EVOLVE,
            "trotter_steps": TROTTER_STEPS,
            "shots": SHOTS,
            "backend": backend.name,
            "job_id": job.job_id(),
        },
        "observable": "gamma_to_dark_photon_conversion_probability",
        "result": {
            "P_conversion_hw": P_conv_hw,
            "P_max_analytic": P_max_analytic,
            "relative_error": rel_err,
            "raw_counts": counts,
        },
        "threshold": "hw conversion within 10% of analytic P_max",
        "verdict": v,
        "honest_scope": (
            "toy Hamiltonian on IBM Q hardware; not detection of real dark "
            "matter or dark photons"
        ),
    }
    payload = {k: v for k, v in record.items() if k != "record_hash"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    record["record_hash"] = hashlib.sha256(canonical.encode()).hexdigest()

    out_path = os.path.join(RESULTS_DIR, "DM-004-ibmq-v1.proofrecord.json")
    with open(out_path, "w") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    print(f"Saved: {out_path}")
    return record


if __name__ == "__main__":
    main()
