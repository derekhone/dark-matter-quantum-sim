# RESULTS — classical simulation layer (v1)

**Series:** `dark-matter-quantum-sim` · **Run date:** 2026-08-01
**Preregistration:** locked, SHA-256 in [`MANIFEST.sha256`](MANIFEST.sha256).

Per the RF covenant, results are published **regardless of PASS / FAIL / HOLD**. The full
ProofRecords (with self-binding `record_hash`) are in each experiment's `results/` folder.

| Experiment | Model | Preregistered threshold | Result | Verdict |
|------------|-------|-------------------------|--------|---------|
| **DM-001** | Axion (Peccei-Quinn double-well) | period `T = 2π/ω₀ ± 5%` | measured period **1.546** vs target **6.283** (75.4% off) | **FAIL** |
| **DM-002** | Sterile neutrino (2-flavor) | matrix vs analytic within 10%; kill if >1% | analytic/matrix agree to **7.8e-16**; `P@L=1 ≈ 0.085` | **PASS** |
| **DM-003** | WIMP-nucleon (exchange) | `sin²(2gt) ± 5%` at `t=π/(4g)` | flip prob **1.000** vs target **1.0**; sim vs closed form **1.1e-15** | **PASS** |

---

### DM-001 is an honest FAIL — and that is the point

The preregistration fixed the naive prediction that `⟨σ_z⟩` would oscillate with period
`T = 2π/ω₀`. The exact classical simulation shows it does not: with the coupling `λ` and the
two-qubit `|00⟩–|11⟩` structure, the true oscillation is a **Rabi oscillation** at the gap
`2√((2ω₀)² + λ²)`, giving a period `π/√((2ω₀)² + λ²) ≈ 1.55` — a 75% deviation from the
preregistered target.

Because the threshold was **locked before the result existed**, we cannot retroactively
"fix" the prediction to manufacture a PASS. We record the **FAIL** and publish it. This is
exactly the discipline the RF preregistration covenant exists to enforce: preregistration
prevents goalpost-moving; a wrong prior is reported as wrong.

The simulation code itself is verified correct — `tests/test_classical_sim.py` confirms the
simulator reproduces the true Rabi period to within 0.5%.

### DM-002 demonstrates the kill condition working

An initial (buggy) flavor-basis convention made the matrix-exponentiation cross-check
disagree with the analytic survival formula by ~1.0 (a complete mismatch). The
preregistered **kill condition (>1% ⇒ HOLD)** correctly caught it before any physics verdict
was issued. After correcting the convention (initial pure flavor state `|ν_μ⟩ = |1⟩`), the
analytic and matrix curves agree to **7.8e-16** and the experiment reports **PASS**.

### DM-003 passes cleanly

The `H = g(XX+YY)` exchange coupling reproduces `P_flip = sin²(2gt)` to floating-point
precision, and the quarter-period flip probability is exactly 1.0.

---

# RESULTS — IBM Quantum hardware layer (v1)

**Hardware:** `ibm_marrakesh` (156-qubit Heron r2) · **Run date:** 2026-08-13
**Jobs queued:** 2026-08-13 00:18–00:26 UTC · **Jobs completed:** 2026-08-13 ~22:18–22:19 UTC
**Shots:** 4096 per experiment · **QPU time:** ~3 s each

The same toy Hamiltonians preregistered and tested classically above were run on IBM
Quantum hardware via the Trotterized circuits in each experiment's `run_ibmq.py`. Results
are published regardless of verdict per the RF covenant.

| Experiment | Model | Preregistered threshold | Hardware result | Verdict |
|------------|-------|-------------------------|-----------------|---------|
| **DM-001** | Axion (2-qubit Trotter) | classical ± 2σ (full time-sweep) | `⟨σ_z⟩ = 0.9453`; single snapshot only | **HOLD** |
| **DM-002** | Sterile neutrino (1-qubit) | hw survival within 10% of analytic | `P_hw = 0.0837` vs analytic `0.0878` (4.6% error) | **PASS** |
| **DM-003** | WIMP exchange (2-qubit) | hw flip prob within 5% of sin²(2gt) | `P_flip = 0.9805` vs target `1.0` (2.0% error) | **~~FAIL~~→PASS** ([erratum](ERRATUM_DM-003.md)) |

### DM-001 is HOLD — by design

The `run_ibmq.py` script for DM-001 hardcodes `verdict(False, kill_triggered=True)` → HOLD
because a single Trotter time-step cannot verify the full oscillation period. The hardware
result `⟨σ_z⟩ = 0.9453` represents a single snapshot at `t = 1.0` with 4 Trotter steps.
A full time-sweep is needed to measure the period and compare against the classical result.
The hardware did produce a clean signal: 96.8% of shots in `|00⟩`, consistent with the
initial state `|00⟩` and the small coupling `λ = 0.3`.

Raw counts: `{00: 3962, 01: 9, 10: 22, 11: 103}` (total 4096).

### DM-002 PASSES on hardware — neutrino survival matches analytic

The sterile neutrino circuit (1-qubit Ry rotation with 6 Trotter steps) measured a survival
probability of **8.37%** against an analytic prediction of **8.78%**, giving a relative error
of **4.6%** — well within the preregistered 10% threshold.

This is noteworthy: despite hardware noise (decoherence, gate errors), the `ibm_marrakesh`
processor reproduced the analytic 2-flavor oscillation probability to within 5%. The circuit
is shallow (single qubit + 6 Trotter steps), which helps explain the good agreement.

Raw counts: `{0: 3753, 1: 343}` (total 4096).

### DM-003 erratum: FAIL→PASS (bitstring extraction defect)

**Erratum (2026-08-14):** The original DM-003 IBM Q runner extracted the
spin-flip probability from the wrong Qiskit bitstring. The runner read bitstring
`"10"` (= initial state |01⟩ in the math convention) instead of `"01"` (= target
state |10⟩). The hardware counts were:

```
{"00": 40, "01": 4016, "10": 16, "11": 24}
```

- **Published (wrong):** `counts["10"] = 16/4096 = 0.0039` → 99.6% error → FAIL
- **Corrected:** `counts["01"] = 4016/4096 = 0.9805` → 2.0% error → **PASS**

The original ProofRecord (`DM-003-ibmq-v1.proofrecord.json`) is **preserved
unchanged**. The corrected analysis is published alongside it as
`DM-003-ibmq-v1-corrected.proofrecord.json`. The circuit, hardware job, and
threshold are unchanged; only the observable extraction was fixed.

See [ERRATUM_DM-003.md](ERRATUM_DM-003.md) for full details and cross-checks
against the DM-001 and DM-002 runners.


### Honest scope (updated for hardware layer)

The classical layer simulates toy Hamiltonians — not detection of real dark matter. The
hardware layer runs the same toy models on IBM Quantum processors. Neither layer claims to
detect, model, or constrain actual dark matter. A physics collaborator is needed to develop
realistic Hamiltonians beyond these toy models.

### Hardware ProofRecords

Self-binding SHA-256 ProofRecords for all three hardware runs are stored alongside their
classical counterparts:

- `experiments/DM-001_axion/results/DM-001-ibmq-v1.proofrecord.json`
- `experiments/DM-002_sterile_neutrino/results/DM-002-ibmq-v1.proofrecord.json`
- `experiments/DM-003_wimp/results/DM-003-ibmq-v1.proofrecord.json` (original, preserved)
- `experiments/DM-003_wimp/results/DM-003-ibmq-v1-corrected.proofrecord.json` (corrected)

---

# RESULTS — classical simulation layer (v2: DM-004 + DM-005)

**Series:** `dark-matter-quantum-sim` · **Run date:** 2026-08-13
**Preregistration:** v2 amendment locked, SHA-256 in `MANIFEST.sha256`.

Two new experiments added by preregistration v2. Published regardless of verdict.

| Experiment | Model | Preregistered threshold | Result | Verdict |
|------------|-------|-------------------------|--------|---------|
| **DM-004** | Dark Photon (kinetic mixing) | `P_max` within 5% of `ε²/(Δ²+ε²)`; kill if >1% | sim vs analytic **2.1e-15**; `P_max = 0.7353` (exact match) | **PASS** |
| **DM-005** | Majorana Mass (seesaw) | `P_max` within 5% of `(m_D/Ω)²`; kill if >1% | sim vs analytic **7.2e-16**; `P_max = 0.2000` (exact match) | **PASS** |

---

### DM-004 passes cleanly — off-resonance dark photon conversion

The 2-qubit toy Hamiltonian `H = ω_γ(Z⊗I) + ω_{A'}(I⊗Z) + ε(X⊗X)` models
kinetic mixing between a visible photon mode (qubit 0) and a dark photon mode
(qubit 1). With `ω_γ = 1.0`, `ω_{A'} = 1.3`, `ε = 0.5`, the detuning
`Δ = −0.3` suppresses the maximum conversion probability from 1.0 (resonant
case) to `P_max = ε²/(Δ²+ε²) = 0.7353`.

The matrix exponentiation reproduces the analytic off-resonance oscillation
formula to **2.1×10⁻¹⁵** — floating-point precision. At the first peak
`t = π/(2Ω) = 2.694`, the simulated `P_max = 0.735294` matches the analytic
prediction exactly.

### DM-005 passes — seesaw suppression verified

The Majorana seesaw toy Hamiltonian `H = m_D(X⊗X) + (M_R/2)(I⊗Z)` models the
Dirac–Majorana mass matrix. Starting from `|00⟩` (left-handed active neutrino),
the lepton-number-violation probability is

    P_LNV(t) = (m_D/Ω)² sin²(Ωt),    Ω = √(m_D² + (M_R/2)²)

With `m_D = 0.5`, `M_R = 2.0` (seesaw ratio 4:1), the maximum LNV probability
is `P_max = (m_D/Ω)² = 0.20` — suppressed from unity by the heavy Majorana
mass. The seesaw approximation `4 m_D²/M_R² = 0.25` overestimates by 25%
because the ratio is not yet deep seesaw. Both values are recorded honestly.

The simulation reproduces the analytic curve to **7.2×10⁻¹⁶**.

### Classical ProofRecords (v2)

- `experiments/DM-004_dark_photon/results/DM-004-classical-v1.proofrecord.json`
- `experiments/DM-005_majorana_mass/results/DM-005-classical-v1.proofrecord.json`
