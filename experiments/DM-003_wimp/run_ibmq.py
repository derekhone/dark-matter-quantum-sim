"""DM-003 WIMP scattering toy model - IBM Q runner (CORRECTED).

CORRECTION (2026-08-14): The original runner extracted the spin-flip probability
from Qiskit bitstring "10", which corresponds to the INITIAL state |01> in the
math convention, not the target state |10>. The correct bitstring is "01".
See ERRATUM_DM-003.md for details.

Builds the XX+YY exchange circuit at the quarter period t = pi/(4g), measures
the |01> -> |10> spin-flip probability on IBM Quantum hardware (or Aer
fallback), compares against the closed form (preregistered 5% threshold).

HONEST SCOPE: toy Hamiltonian on 2 qubits; not detection of real dark matter.
"""

from __future__ import annotations

import os

import numpy as np

from dm_sim.circuits import wimp_circuit
from dm_sim.metrics import match_threshold, verdict
from dm_sim.proofrecord import make_proofrecord, save_record

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")

G = 1.0
SHOTS = 4096
THRESHOLD_FRACTION = 0.05


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

    t_quarter = np.pi / (4.0 * G)
    qc = wimp_circuit(g=G, t=t_quarter, steps=6)
    backend, backend_kind = get_backend()

    from qiskit import transpile

    tqc = transpile(qc, backend)
    job = backend.run(tqc, shots=SHOTS)
    counts = job.result().get_counts()
    total = sum(counts.values())

    # CORRECTED: |10> in math convention (q0=1, q1=0) maps to Qiskit bitstring
    # "01" (Qiskit uses big-endian qubit ordering: bitstring "ab" = q1=a, q0=b).
    # The original runner incorrectly read bitstring "10" (= initial state |01>).
    flip_hw = counts.get("01", 0) / total

    passed = match_threshold(flip_hw, 1.0, THRESHOLD_FRACTION)
    v = verdict(passed, kill_triggered=False)

    record = make_proofrecord(
        experiment_id="DM-003-ibmq-v1",
        model="wimp_nucleon_exchange",
        parameters={"g": G, "t_quarter": t_quarter, "shots": SHOTS,
                     "backend": backend_kind},
        observable="spin_flip_probability_01_to_10",
        result={"counts": counts, "flip_hw": flip_hw, "closed_form": 1.0,
                "relative_error": abs(1.0 - flip_hw) / 1.0},
        threshold="IBM Q flip prob within 5% of sin^2(2 g t) at t=pi/(4g)",
        verdict=v,
    )
    out_path = os.path.join(RESULTS_DIR, "DM-003-ibmq-v1.proofrecord.json")
    save_record(record, out_path)

    print("=" * 70)
    print("DM-003 WIMP - IBM Q run (CORRECTED)")
    print("=" * 70)
    print(f"  backend            : {backend_kind}")
    print(f"  counts             : {counts}")
    print(f"  flip prob (hw)     : {flip_hw:.4f} (target 1.0)")
    print(f"  VERDICT            : {v}")
    print(f"  record_hash        : {record['record_hash']}")
    print(f"  saved              : {out_path}")
    return record


if __name__ == "__main__":
    main()
