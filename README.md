# dark-matter-quantum-sim

**Preregistered quantum simulations of toy dark-matter-candidate Hamiltonians.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21926912.svg)](https://doi.org/10.5281/zenodo.21926912)

**Series:** `dark-matter-quantum-sim`
**Steward:** [Remnant Fieldworks Inc.](https://remnantfieldworks.com)

## HONEST SCOPE

These are **small-system toy Hamiltonian simulations** (2 qubits) that model the
*mathematical structure* of dark matter candidate interactions. They are **NOT**
detection experiments, **NOT** simulations of real dark matter, and they do **NOT**
prove that any dark matter candidate particle is real.

## Experiments

| ID | Candidate | Hamiltonian | Classical | IBM Q | Notes |
|----|-----------|-------------|-----------|-------|-------|
| DM-001 | Axion (Peccei–Quinn) | `ω₀(ZI+IZ) + λ(XX)` | **FAIL** | **HOLD** | Honest FAIL: Rabi period ≠ 2π/ω₀ |
| DM-002 | Sterile neutrino | `(Δm²/4E)(−cos2θ Z + sin2θ X)` | **PASS** | **PASS** | 4.6% error on hardware |
| DM-003 | WIMP (exchange) | `g(XX+YY)` | **PASS** | **~~FAIL~~→PASS** | [Erratum](ERRATUM_DM-003.md): bitstring extraction defect; hardware was 98.0% (2.0% error) |
| DM-004 | Dark Photon (kinetic mixing) | `ω_γ(ZI) + ω_{A'}(IZ) + ε(XX)` | **PASS** | *pending* | Off-resonance oscillation exact |
| DM-005 | Majorana Mass (seesaw) | `m_D(XX) + (M_R/2)(IZ)` | **PASS** | *pending* | Seesaw suppression P_max=0.20 |

### Preregistration

All experiments were preregistered with questions, Hamiltonians, observables, and
pass/fail thresholds **locked before any results were computed**. See
[PREREGISTRATION.md](PREREGISTRATION.md) (v1: DM-001–003; v2: DM-004–005).

### Results

Full results with ProofRecords (SHA-256 self-binding): [RESULTS.md](RESULTS.md).

## Structure

```
experiments/
  DM-001_axion/          run_classical.py, run_ibmq.py, results/
  DM-002_sterile_neutrino/
  DM-003_wimp/
  DM-004_dark_photon/
  DM-005_majorana_mass/
src/dm_sim/
  hamiltonians.py        All 5 toy Hamiltonians
  classical_sim.py       Exact matrix-exponentiation simulations
  circuits.py            Qiskit circuit builders (IBM Q)
  proofrecord.py         SHA-256 self-binding ProofRecord format
  metrics.py             Verdict logic (PASS/FAIL/HOLD)
tests/
  test_classical_sim.py  Unit tests for all classical simulations
```

## Running

```bash
# Classical simulations (numpy + scipy only)
python -m experiments.DM-004_dark_photon.run_classical
python -m experiments.DM-005_majorana_mass.run_classical

# IBM Q (requires qiskit + IBM Quantum account)
python -m experiments.DM-004_dark_photon.run_ibmq
python -m experiments.DM-005_majorana_mass.run_ibmq
```

## License

MIT. Part of the [ExecutionProof](https://executionproof.io) governed-research program.
