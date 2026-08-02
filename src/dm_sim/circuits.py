"""Qiskit circuit builders (IBM Q ready) for the three toy experiments.

Qiskit is an OPTIONAL dependency. These builders are only needed for the
``run_ibmq.py`` runners; the classical simulations do not require Qiskit.
Import errors are raised lazily with a clear message so that the classical
path works in a numpy/scipy-only environment.

HONEST SCOPE: these circuits implement toy Hamiltonians on 2 qubits. They do
not detect dark matter.
"""

from __future__ import annotations

import numpy as np


def _require_qiskit():
    try:
        import qiskit  # noqa: F401
        from qiskit import QuantumCircuit

        return QuantumCircuit
    except Exception as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "Qiskit is required to build IBM Q circuits. Install with "
            "`pip install 'dark-matter-quantum-sim[ibmq]'` or `pip install qiskit`."
        ) from exc


# ---------------------------------------------------------------------------
# DM-001 : Axion  -  Trotterized exp(-i H t), H = w0(ZI+IZ) + lam(XX)
# ---------------------------------------------------------------------------
def axion_circuit(omega_0: float = 1.0, lam: float = 0.3, t: float = 1.0, steps: int = 4):
    """Trotterized time-evolution circuit for the axion toy Hamiltonian.

    Uses first-order Trotter: (exp(-i Hz dt) exp(-i Hxx dt))^steps.
    Measures both qubits in the Z basis.
    """
    QuantumCircuit = _require_qiskit()
    qc = QuantumCircuit(2, 2)
    dt = t / steps
    for _ in range(steps):
        # Z rotations: exp(-i w0 dt Z) on each qubit  ->  RZ(2 w0 dt)
        qc.rz(2 * omega_0 * dt, 0)
        qc.rz(2 * omega_0 * dt, 1)
        # XX interaction: exp(-i lam dt XX)  ->  standard CNOT-RZ-CNOT sandwich
        qc.h(0)
        qc.h(1)
        qc.cx(0, 1)
        qc.rz(2 * lam * dt, 1)
        qc.cx(0, 1)
        qc.h(0)
        qc.h(1)
    qc.measure([0, 1], [0, 1])
    return qc


# ---------------------------------------------------------------------------
# DM-002 : Sterile neutrino  -  state prep Ry(2 theta) + Trotter evolution
# ---------------------------------------------------------------------------
def sterile_neutrino_circuit(
    delta_m2: float = 1.0,
    energy: float = 1.0,
    theta: float = np.pi / 4,
    L: float = 1.0,
    steps: int = 4,
):
    """Circuit for 2-flavor neutrino oscillation on a single active qubit.

    In the flavor basis the mixing lives inside H, so the initial pure flavor
    state |nu_mu> is the computational basis state |1> (prepared with an X
    gate). We evolve under H = (dm2/4E)(-cos2th Z + sin2th X) via Trotterization
    and measure directly in the Z basis: the survival probability
    P(nu_mu -> nu_mu) is the probability of measuring outcome '1'.
    """
    QuantumCircuit = _require_qiskit()
    qc = QuantumCircuit(1, 1)
    # state prep: |nu_mu> = |1>
    qc.x(0)

    omega = delta_m2 / (4.0 * energy)
    phi = 1.27 * delta_m2 * L / energy
    t = phi / omega if omega != 0 else 0.0
    dt = t / steps
    for _ in range(steps):
        # exp(-i omega dt (-cos2th) Z) -> RZ(2 omega (-cos2th) dt)
        qc.rz(2 * omega * (-np.cos(2 * theta)) * dt, 0)
        # exp(-i omega dt ( sin2th) X) -> RX(2 omega ( sin2th) dt)
        qc.rx(2 * omega * (np.sin(2 * theta)) * dt, 0)
    qc.measure(0, 0)
    return qc


# ---------------------------------------------------------------------------
# DM-003 : WIMP  -  exchange interaction exp(-i g t (XX+YY))
# ---------------------------------------------------------------------------
def wimp_circuit(g: float = 1.0, t: float = np.pi / 4, steps: int = 4):
    """Trotterized circuit for the WIMP exchange coupling H = g(XX+YY).

    Prepares |01> then applies the XX+YY evolution and measures both qubits.
    """
    QuantumCircuit = _require_qiskit()
    qc = QuantumCircuit(2, 2)
    # initial state |01> (qubit0 = 0, qubit1 = 1)
    qc.x(1)
    dt = t / steps
    for _ in range(steps):
        # exp(-i g dt XX)
        qc.h(0)
        qc.h(1)
        qc.cx(0, 1)
        qc.rz(2 * g * dt, 1)
        qc.cx(0, 1)
        qc.h(0)
        qc.h(1)
        # exp(-i g dt YY)
        qc.rx(np.pi / 2, 0)
        qc.rx(np.pi / 2, 1)
        qc.cx(0, 1)
        qc.rz(2 * g * dt, 1)
        qc.cx(0, 1)
        qc.rx(-np.pi / 2, 0)
        qc.rx(-np.pi / 2, 1)
    qc.measure([0, 1], [0, 1])
    return qc


__all__ = [
    "axion_circuit",
    "sterile_neutrino_circuit",
    "wimp_circuit",
]
