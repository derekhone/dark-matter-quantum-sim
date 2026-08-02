"""dark-matter-quantum-sim
============================

Preregistered quantum simulation of toy dark matter candidate Hamiltonians,
governed by ExecutionProof-style ProofRecords, from Remnant Fieldworks Inc.

HONEST SCOPE
------------
These simulations model the mathematical structure of dark matter candidate
interactions using small (2-4 qubit) toy Hamiltonians. They do not detect dark
matter, prove any candidate particle exists, or replace experimental searches.
The value is methodological: applying preregistered, ProofRecord-governed
experimental discipline to quantum simulation of open physics questions.

Experiments
-----------
- DM-001  Axion dark matter toy model (Peccei-Quinn double-well)
- DM-002  Sterile neutrino oscillation toy model
- DM-003  WIMP scattering toy model (simplified exchange coupling)
"""

from __future__ import annotations

from .hamiltonians import (
    axion_hamiltonian,
    sterile_neutrino_hamiltonian,
    wimp_hamiltonian,
    SX,
    SY,
    SZ,
    I2,
    kron,
)
from .classical_sim import (
    evolve,
    expectation,
    simulate_axion,
    simulate_neutrino,
    simulate_wimp,
    neutrino_survival_analytic,
    wimp_flip_analytic,
)
from .metrics import (
    PASS,
    FAIL,
    HOLD,
    compute_fidelity,
    relative_error,
    match_threshold,
    kill_condition_triggered,
    verdict,
)
from .proofrecord import (
    make_proofrecord,
    compute_record_hash,
    verify_record,
    save_record,
    load_record,
    utc_now,
    SERIES,
    HONEST_SCOPE,
)

__version__ = "0.1.0a1"

__all__ = [
    "__version__",
    # hamiltonians
    "axion_hamiltonian",
    "sterile_neutrino_hamiltonian",
    "wimp_hamiltonian",
    "SX",
    "SY",
    "SZ",
    "I2",
    "kron",
    # classical sim
    "evolve",
    "expectation",
    "simulate_axion",
    "simulate_neutrino",
    "simulate_wimp",
    "neutrino_survival_analytic",
    "wimp_flip_analytic",
    # metrics
    "PASS",
    "FAIL",
    "HOLD",
    "compute_fidelity",
    "relative_error",
    "match_threshold",
    "kill_condition_triggered",
    "verdict",
    # proofrecord
    "make_proofrecord",
    "compute_record_hash",
    "verify_record",
    "save_record",
    "load_record",
    "utc_now",
    "SERIES",
    "HONEST_SCOPE",
]
