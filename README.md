> **Repository Role:** Research Prototype — Toy Dark Matter Hamiltonian Simulation (Honest Scope: No Real DM Detection) · Part of the [Remnant Fieldworks](https://remnantfieldworks.com) research and product ecosystem

**Where this fits:** This is an exploratory research prototype — toy Hamiltonian simulations governed by ProofRecord methodology. These simulations do not detect real dark matter or make claims about physical reality beyond what the toy models demonstrate. This repository showcases ProofRecord governance applied to a high-curiosity domain. For the commercial product, see [ExecutionProof](https://executionproof.io).

---

# dark-matter-quantum-sim

**Preregistered, ProofRecord-governed quantum simulation of toy dark matter candidate Hamiltonians.**
A [Remnant Fieldworks Inc.](https://executionproof.io) research repository.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)](#)

---

### Honest scope

> These simulations model the mathematical structure of dark matter candidate interactions using small (2-4 qubit) toy Hamiltonians. They do not detect dark matter, prove any candidate particle exists, or replace experimental searches. The value is methodological: applying preregistered, ProofRecord-governed experimental discipline to quantum simulation of open physics questions. A physics collaborator is needed to develop more realistic Hamiltonians beyond these toy models.

Read that paragraph twice. Nothing in this repository is a physics discovery claim. Every
result carries the same `honest_scope` line in its ProofRecord.

---

### Why this repository exists

Remnant Fieldworks has run **75 preregistered quantum experiments** (the WITNESS,
BELLWETHER, CHRONO, OMNI, and TRINITY series), each governed by the same discipline:

1. Write and **SHA-256-lock a preregistration** before any results exist.
2. Emit a **ProofRecord** for every run, bound to itself by a hash.
3. Issue a **PASS / FAIL / HOLD** verdict against thresholds fixed in advance.
4. **Publish regardless of outcome** (Zenodo), including negative results.

This repository applies that exact rigor to *quantum simulation of open physics questions* —
starting with three toy dark matter candidate models. It establishes the **methodology and
prior art** for quantum-simulation-as-governed-research, and is the on-ramp for a physics
collaborator to build more realistic Hamiltonians on top of a disciplined foundation.

---

### The three experiments

| ID | Model | Hamiltonian | Observable | Threshold |
|----|-------|-------------|------------|-----------|
| **DM-001** | Axion (Peccei-Quinn double-well) | `H = ω₀(Z⊗I + I⊗Z) + λ(X⊗X)` | `⟨σ_z⟩` oscillation period | `T = 2π/ω₀ ± 5%` |
| **DM-002** | Sterile neutrino (2-flavor) | `H = (Δm²/4E)(−cos2θ·Z + sin2θ·X)` | survival `P(ν_μ→ν_μ)` | analytic match ± 10% |
| **DM-003** | WIMP-nucleon (exchange) | `H = g(X⊗X + Y⊗Y)` | spin-flip `P(|01⟩→|10⟩)` | `sin²(2gt) ± 5%` |

Full statements, parameters, and kill conditions are locked in
[`PREREGISTRATION.md`](PREREGISTRATION.md), whose SHA-256 hash is recorded in
[`MANIFEST.sha256`](MANIFEST.sha256).

All three are **classically simulated exactly** first (matrix exponentiation, `scipy.linalg.expm`)
and cross-checked against closed-form / analytic solutions. IBM Q circuits are provided and
ready to run, but the classical layer is the one that must pass the kill condition first.

---

### Install

```bash
git clone https://github.com/derekhone/dark-matter-quantum-sim.git
cd dark-matter-quantum-sim
pip install -e .            # classical simulation only (numpy, scipy, matplotlib)
pip install -e ".[ibmq]"    # add Qiskit + IBM Q runtime for hardware runs
pip install -e ".[dev]"     # add pytest
```

Python 3.9+.

---

### Run the classical simulations

Each experiment has a `run_classical.py` that runs the exact simulation, checks the
preregistered threshold, and writes a ProofRecord to its `results/` folder.

```bash
cd experiments/DM-001_axion          && python run_classical.py
cd ../DM-002_sterile_neutrino        && python run_classical.py
cd ../DM-003_wimp                    && python run_classical.py
```

(Or from the repo root with `PYTHONPATH=src` — see below.)

Each run prints its verdict and the `record_hash`, e.g.:

```
DM-003 WIMP Scattering Toy Model - classical simulation
  g                        : 1.0
  max |sim - closed form|  : ...e-16
  kill condition (>1%)     : clear
  t_quarter = pi/(4g)      : 0.785398
  flip prob at quarter     : 1.000000 (target 1.0)
  VERDICT                  : PASS
  record_hash              : <sha256>
```

---

### Run on IBM Quantum hardware

Each experiment also has a `run_ibmq.py`. Provide your IBM Quantum token via the
`IBMQ_TOKEN` environment variable; the runner picks the least-busy real backend and falls
back to the local Aer simulator if no token / hardware is available.

```bash
export IBMQ_TOKEN="your_ibm_quantum_token"
cd experiments/DM-002_sterile_neutrino && python run_ibmq.py
```

> DM-002 (neutrino oscillation) is the most faithfully simulatable on real hardware, because
> 2-flavor oscillation *is* standard quantum mechanics. DM-001 and DM-003 are shallower toy
> circuits. Credentials and tokens are never committed (see `.gitignore`).

---

### ProofRecord schema

Every run emits a record with this structure (same schema as the RF quantum series):

```json
{
  "experiment_id": "DM-001-classical-v1",
  "series": "dark-matter-quantum-sim",
  "model": "axion_pq_potential",
  "timestamp_utc": "2026-08-01T00:00:00Z",
  "parameters": {"omega_0": 1.0, "lambda": 0.3},
  "observable": "sigma_z_expectation",
  "result": {"measured_period": 6.28, "target_period": 6.283},
  "threshold": "T within 5% of 2*pi/omega_0",
  "verdict": "PASS",
  "honest_scope": "toy Hamiltonian classical simulation only; not detection of real dark matter",
  "record_hash": "<sha256 of the record without the record_hash field>"
}
```

`record_hash` is SHA-256 over the canonical JSON of the record with the `record_hash`
field removed. `dm_sim.proofrecord.verify_record()` recomputes and confirms it, so any
tampering is detectable.

---

### Package layout

```
dark-matter-quantum-sim/
├── PREREGISTRATION.md      # locked questions, Hamiltonians, thresholds, kill conditions
├── MANIFEST.sha256         # SHA-256 of PREREGISTRATION.md (the lock)
├── src/dm_sim/
│   ├── hamiltonians.py     # H matrices for all three models
│   ├── classical_sim.py    # exact matrix exponentiation + analytic references
│   ├── circuits.py         # Qiskit circuit builders (IBM Q ready, optional import)
│   ├── proofrecord.py      # ProofRecord schema + SHA-256 binding
│   └── metrics.py          # fidelity, threshold matching, PASS/FAIL/HOLD verdicts
├── experiments/
│   ├── DM-001_axion/            {run_classical.py, run_ibmq.py, results/}
│   ├── DM-002_sterile_neutrino/ {run_classical.py, run_ibmq.py, results/}
│   └── DM-003_wimp/             {run_classical.py, run_ibmq.py, results/}
├── notebooks/
│   └── dark_matter_toy_models_overview.ipynb
└── tests/                  # pytest suite (hamiltonians, classical sim, proofrecord)
```

---

### Development

```bash
pip install -e ".[dev]"
PYTHONPATH=src pytest -q
```

Verify the preregistration lock:

```bash
sha256sum PREREGISTRATION.md          # must match MANIFEST.sha256
```

---

### Kill condition & publication rule

- **Kill condition.** If the exact classical simulation disagrees with the closed-form /
  analytic solution by more than **1%**, the classical layer is untrustworthy: the run is
  marked `HOLD`, no physics verdict is issued, and the discrepancy is investigated first.
- **Publication rule.** Results are published **regardless of PASS / FAIL / HOLD**, with the
  ProofRecord and hash. A negative result is reported with the same prominence as a positive
  one.

---

### License

MIT © 2026 Remnant Fieldworks Inc. See [LICENSE](LICENSE).

*Proof before power.*
