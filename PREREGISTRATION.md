# PREREGISTRATION — dark-matter-quantum-sim

**Series:** `dark-matter-quantum-sim`
**Steward:** Remnant Fieldworks Inc.
**Preregistration date:** 2026-08-01
**Status:** LOCKED (hash recorded in `MANIFEST.sha256`)

---

## 0. Covenant

This document is written and locked **before** any results are computed. It follows the
Remnant Fieldworks preregistration covenant used across the prior 75 preregistered
quantum experiments (WITNESS, BELLWETHER, CHRONO, OMNI, TRINITY series):

1. **Questions and thresholds are stated first.** No result may retroactively change the
   question it was meant to answer.
2. **Every run emits a ProofRecord** bound by SHA-256 to its own contents.
3. **Verdicts are `PASS` / `FAIL` / `HOLD`** against thresholds fixed in this document.
4. **Publish regardless of verdict.** A `FAIL` is published with the same discipline as a
   `PASS`. Suppression of a negative result is a covenant violation.

Once the SHA-256 of this file is written to `MANIFEST.sha256`, the questions, Hamiltonians,
observables, and thresholds below are considered frozen for version `v1`.

---

## 1. HONEST SCOPE (binding)

These are **small-system toy Hamiltonian simulations** (2–4 qubits) that model the
*mathematical structure* of dark matter candidate interactions. They are:

- **NOT** detection experiments,
- **NOT** simulations of real dark matter,
- and they **do NOT** prove that any dark matter candidate particle is real.

The value of this work is **methodological**:

1. Applying preregistered IBM Q simulation methods to open physics questions.
2. Binding simulation results to ExecutionProof-style ProofRecords using the same
   framework as the Remnant Fieldworks quantum witness series.
3. Establishing prior art in *quantum-simulation-as-governed-research*.

A physics collaborator is required to develop more realistic Hamiltonians beyond these
toy models. Nothing in this repository should be read as a physical discovery claim.

---

## 2. Experiments

Three experiments are preregistered. For each we fix: the **question**, the **Hamiltonian**,
the **observable**, and the **pass/fail threshold**. Conventions:

- Pauli operators `σ_x, σ_y, σ_z`; identity `I`. Tensor order is `qubit0 ⊗ qubit1`.
- Natural units, `ħ = 1`. Time `t` is dimensionless in simulation units unless stated.
- Classical simulation uses exact matrix exponentiation `U(t) = exp(-i H t)`.

### EXPERIMENT DM-001 — Axion Dark Matter Toy Model

**Question.** Does a 2-qubit anharmonic-oscillator approximation of the Peccei–Quinn
double-well potential produce a coherent oscillation in `⟨σ_z⟩` with the expected period?

**Background.** The QCD axion (Peccei–Quinn, 1977) is a hypothetical particle proposed to
solve the strong CP problem. Its mass–coupling relationship yields a characteristic
oscillation signature. On a quantum computer the axion potential can be approximated as an
anharmonic oscillator.

**Hamiltonian.**
```
H = ω₀ (σ_z ⊗ I + I ⊗ σ_z) + λ (σ_x ⊗ σ_x)
```
with axion frequency parameter `ω₀ = 1.0` and coupling `λ = 0.3`.

**Observable.** Expectation value `⟨σ_z⟩` on qubit 0 as a function of time (oscillation
signature), initial state `|00⟩`.

**Classical method.** Matrix exponentiation.
**IBM Q circuit.** `Ry` rotations + `CNOT`, measured in the `Z` basis (Trotterized time
evolution).

**Preregistered threshold.**
- Classical: the dominant oscillation period `T` of `⟨σ_z⟩` satisfies `T = 2π/ω₀ ± 5%`.
- IBM Q: the hardware result matches the classical prediction within `2σ` (accounting for
  hardware noise).
- Verdict `PASS` iff the classical period is within ±5% of `2π/ω₀`.

### EXPERIMENT DM-002 — Sterile Neutrino Oscillation Toy Model

**Question.** Does a 2-qubit Trotterized evolution reproduce the analytic 2-flavor neutrino
survival probability for a maximal-mixing (sterile-neutrino-analogue) scenario?

**Background.** Sterile neutrinos are dark matter candidates that mix with active neutrinos.
Neutrino oscillation is already fully described by quantum mechanics (PMNS matrix), so a
2-qubit system naturally models 2-flavor oscillation. This is the **most faithfully
simulatable** of the three experiments.

**Hamiltonian.**
```
H = (Δm² / 4E) ( −cos(2θ) σ_z + sin(2θ) σ_x )
```
Initial state `|ν_μ⟩ = cos(θ)|0⟩ + sin(θ)|1⟩`.
Parameters: mixing angle `θ = π/4` (maximal mixing), `Δm² = 1 eV²`
(light sterile-neutrino candidate range, LSND/MiniBooNE anomaly band).

**Observable.** Survival probability
```
P(ν_μ → ν_μ) = 1 − sin²(2θ) · sin²(1.27 Δm² L / E)
```

**Classical method.** Exact analytic formula (and matrix-exponentiation cross-check).
**IBM Q circuit.** `Ry(2θ)` state prep + Trotterized time evolution.

**Preregistered threshold.**
- IBM Q survival probability matches the analytic prediction within **10%** (loose — deep
  circuits accumulate hardware noise).
- Verdict `PASS` iff the classical/analytic and matrix-exponentiation curves agree within
  1% at all sampled points (kill condition, §3) **and** the reported point matches analytic
  within 10%.

### EXPERIMENT DM-003 — WIMP Scattering Toy Model (Simplified)

**Question.** Does a 2-qubit XX+YY (exchange) coupling reproduce the expected
`sin²(gt)` spin-flip probability for a simplified WIMP–nucleon scattering analogue?

**Background.** WIMPs (Weakly Interacting Massive Particles) scatter off nucleons via the
weak force; the cross-section sets detection rates. A 2-qubit system models a simplified
WIMP–nucleon interaction as a spin–spin coupling.

**Hamiltonian.**
```
H = g (σ_x ⊗ σ_x + σ_y ⊗ σ_y)
```
qubit 0 = WIMP spin, qubit 1 = nucleon spin. Initial state `|↑↓⟩ = |01⟩`.
Coupling `g = 1.0` (scanned over a range for the rate-vs-coupling curve).

**Observable.** Probability of spin-flip to `|↓↑⟩ = |10⟩` as a function of `g` and `t`.

**Classical method.** Exact matrix exponentiation.
**IBM Q circuit.** Bell-state / exchange rotation circuit.

**Preregistered threshold.**
- Spin-flip probability matches `P = sin²(2gt)` for the XX+YY convention at the sampled
  times; specifically at `t = π/(4g)` (a quarter of the `2g` Rabi period) the flip
  probability equals `sin²(π/2) = 1` within **±5%**.
- Verdict `PASS` iff the simulated flip probability matches the closed form within ±5%.

> **Convention note (frozen here before results):** for `H = g(XX+YY)` acting on the
> single-excitation subspace `{|01⟩, |10⟩}`, the effective two-level gap is `2g`, giving
> `P_flip(t) = sin²(2gt)`. The quarter-period is therefore `t = π/(4g)`. This closed form
> is the reference used for the ±5% test.

---

## 3. Kill condition (applies to all experiments)

If the **classical matrix-exponentiation simulation disagrees with the closed-form /
analytic solution by more than 1%** at any sampled point, the classical layer itself is
untrustworthy. In that case:

- the run is marked `HOLD`,
- no `PASS`/`FAIL` verdict on the physics question is issued,
- the discrepancy is investigated before any IBM Q run is attempted.

This is a stop condition, not a failure of the physics question.

---

## 4. Publication rule

Results are published **regardless of `PASS` / `FAIL` / `HOLD`**, with the ProofRecord and
its SHA-256 hash, to the Remnant Fieldworks Zenodo record for this series. A negative or
null result is a valid, publishable outcome and is reported with identical prominence to a
positive one.

---

## 5. Freeze

Upon writing `sha256(PREREGISTRATION.md)` to `MANIFEST.sha256`, sections 1–4 above are
frozen for version `v1` of the `dark-matter-quantum-sim` series. Any change to a question,
Hamiltonian, observable, threshold, or kill condition requires a new preregistration
(`v2`) with a new hash and a new dated entry.
