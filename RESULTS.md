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

The `H = g(X⊗X + Y⊗Y)` exchange coupling reproduces `P_flip = sin²(2gt)` to floating-point
precision, and the quarter-period flip probability is exactly 1.0.

---

### Honest scope (unchanged)

These are toy Hamiltonian classical simulations, not detection of real dark matter. The IBM
Q circuit runs (`run_ibmq.py`) are provided but not part of this classical-layer result set.
A physics collaborator is needed to develop realistic Hamiltonians beyond these toy models.
