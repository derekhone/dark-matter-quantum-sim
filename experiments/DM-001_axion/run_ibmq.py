"""DM-001 Axion toy model - IBM Q runner.

Builds the Trotterized axion circuit and runs it on IBM Quantum hardware (or
the Aer simulator as a fallback). Requires Qiskit and IBM Q credentials.

Set your token via the environment variable IBMQ_TOKEN, or configure the
Qiskit Runtime account beforehand.

HONEST SCOPE: toy Hamiltonian on 2 qubits; not detection of real dark matter.
"""

from __future__ import annotations

import os

from dm_sim.circuits import axion_circuit
from dm_sim.metrics import verdict
from dm_sim.proofrecord import make_proofrecord, save_record

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")

OMEGA_0 = 1.0
LAMBDA = 0.3
SHOTS = 4096


def get_backend(prefer_hardware: bool = True):
    """Return an execution backend: IBM Q hardware if available else Aer."""
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

    qc = axion_circuit(omega_0=OMEGA_0, lam=LAMBDA, t=1.0, steps=4)
    backend, backend_kind = get_backend()

    from qiskit import transpile

    tqc = transpile(qc, backend)
    job = backend.run(tqc, shots=SHOTS)
    counts = job.result().get_counts()
    total = sum(counts.values())
    # <sigma_z> on qubit 0 from the measured bitstrings
    exp_sz = 0.0
    for bitstring, c in counts.items():
        q0 = int(bitstring[-1])  # little-endian: rightmost is qubit 0
        exp_sz += (1 if q0 == 0 else -1) * c
    exp_sz /= total

    # A single Trotter snapshot cannot verify the full period on hardware; the
    # verdict here is HOLD pending a full time-sweep run (documented in prereg).
    v = verdict(False, kill_triggered=True)  # HOLD

    record = make_proofrecord(
        experiment_id="DM-001-ibmq-v1",
        model="axion_pq_potential",
        parameters={"omega_0": OMEGA_0, "lambda": LAMBDA, "shots": SHOTS,
                     "backend": backend_kind},
        observable="sigma_z_expectation",
        result={"counts": counts, "sigma_z_expectation": exp_sz},
        threshold="IBM Q matches classical within 2 sigma (full time-sweep)",
        verdict=v,
    )
    out_path = os.path.join(RESULTS_DIR, "DM-001-ibmq-v1.proofrecord.json")
    save_record(record, out_path)

    print("=" * 70)
    print("DM-001 Axion - IBM Q run")
    print("=" * 70)
    print(f"  backend            : {backend_kind}")
    print(f"  counts             : {counts}")
    print(f"  <sigma_z> (qubit0) : {exp_sz:.4f}")
    print(f"  VERDICT            : {v} (single snapshot; full sweep pending)")
    print(f"  record_hash        : {record['record_hash']}")
    print(f"  saved              : {out_path}")
    return record


if __name__ == "__main__":
    main()
