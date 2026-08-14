# ERRATUM — DM-003-ibmq-v1: Bit-Ordering Defect in Observable Extraction

**Date:** 2026-08-14
**Affects:** `DM-003-ibmq-v1.proofrecord.json` (published in dark-matter-quantum-sim
v1, DOI 10.5281/zenodo.21926912)
**Severity:** Verdict reversal (published FAIL → corrected PASS)
**Root cause:** Qiskit bitstring convention applied backwards in the IBM Q runner

---

## Summary

The DM-003 IBM Quantum runner (`experiments/DM-003_wimp/run_ibmq.py`) extracted
the spin-flip probability from the wrong Qiskit bitstring. The published verdict
of **FAIL** (relative error 99.6%) is incorrect. The hardware actually produced
a result consistent with **PASS** (relative error ~2.0%).

## Details

The WIMP exchange Hamiltonian H = g(XX + YY) evolves the initial state |01⟩
toward |10⟩. At the quarter period t = π/(4g), the analytic flip probability
P(|01⟩ → |10⟩) = 1.0.

In the computational basis with the tensor convention |q0 q1⟩:
- |01⟩ (initial) = index 1 in the state vector
- |10⟩ (target)  = index 2 in the state vector

Qiskit represents measurement outcomes as bitstrings in **big-endian qubit
order**: bitstring `"ab"` means q1 = a, q0 = b. Therefore:
- |01⟩ (q0=0, q1=1) → Qiskit bitstring `"10"`
- |10⟩ (q0=1, q1=0) → Qiskit bitstring `"01"`

The runner contained:
```python
# |10> in little-endian qiskit bitstring order is "10" -> q1=1,q0=0
flip_hw = counts.get("10", 0) / total
```

The comment's mapping is incorrect. Qiskit bitstring `"10"` corresponds to the
**initial** state |01⟩, not the target state |10⟩. The runner measured the
probability of *not* flipping.

## Hardware counts (unchanged)

```
{"00": 40, "01": 4016, "10": 16, "11": 24}
```

| extraction | bitstring | counts | probability | relative error | verdict |
|---|---|---|---|---|---|
| Published (wrong) | `"10"` | 16 | 0.003906 | 99.61% | FAIL |
| Corrected | `"01"` | 4016 | 0.980469 | 1.95% | **PASS** |

The hardware result (98.0% flip probability vs analytic 100%) is well within the
preregistered 5% relative error threshold.

## Cross-check against other runners

- **DM-001** (axion, 2-qubit): Uses `int(bitstring[-1])` to extract q0 from
  Qiskit's big-endian string. Correct convention. ✓
- **DM-002** (sterile neutrino, 1-qubit): Uses `counts.get("1", 0)`. Unambiguous
  for a single qubit. ✓
- **DM-003** was the only 2-qubit IBM Q runner that extracted a specific
  2-qubit bitstring by name, and the mapping was reversed.

## What changes

1. `run_ibmq.py` is corrected: the extraction line now reads
   `counts.get("01", 0)` and the comment is fixed.
2. A new ProofRecord `DM-003-ibmq-v1-corrected.proofrecord.json` is published
   alongside the original. The original `DM-003-ibmq-v1.proofrecord.json` is
   **preserved unchanged** — it is not silently replaced.
3. The corrected record contains a `correction_note` field referencing this
   erratum and the original record hash.
4. `RESULTS.md` and `README.md` are updated to reflect the corrected verdict.

## What does not change

- The original ProofRecord file is not deleted or modified.
- The original hardware job ID and counts are preserved verbatim in the
  corrected record.
- The classical simulation (`DM-003-classical-v1`) is unaffected (PASS,
  agreement to floating-point precision).
- No circuit, Hamiltonian, or threshold is changed.

## Implications for QG-004

The QG-004 experiment ("Mitigation Cannot Manufacture Truth") was originally
conceived using DM-003's FAIL as a substrate. Since the FAIL was an extraction
defect rather than a physics failure, QG-004 has been redesigned to use a
**deliberately falsified analytic target** instead. This is documented in the
QG series preregistration.
