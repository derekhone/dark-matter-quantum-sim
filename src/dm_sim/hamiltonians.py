"""Toy Hamiltonians for the dark-matter-quantum-sim series.

HONEST SCOPE: these are small (2-qubit) toy Hamiltonians that model the
*mathematical structure* of dark matter candidate interactions. They are not
simulations of real dark matter and do not detect or prove any candidate.

All operators use the tensor convention ``qubit0 (x) qubit1`` (NumPy ``np.kron``).
Natural units, hbar = 1.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Single-qubit Pauli operators
# ---------------------------------------------------------------------------
I2 = np.eye(2, dtype=complex)
SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def kron(*ops: np.ndarray) -> np.ndarray:
    """Tensor product of a sequence of operators (qubit0 (x) qubit1 (x) ...)."""
    out = np.array([[1.0 + 0j]])
    for op in ops:
        out = np.kron(out, op)
    return out


# ---------------------------------------------------------------------------
# DM-001 : Axion (Peccei-Quinn double-well toy) Hamiltonian
# ---------------------------------------------------------------------------
def axion_hamiltonian(omega_0: float = 1.0, lam: float = 0.3) -> np.ndarray:
    """H = omega_0 (Z(x)I + I(x)Z) + lambda (X(x)X).

    Parameters
    ----------
    omega_0 : axion frequency parameter.
    lam     : coupling constant lambda.
    """
    H = omega_0 * (kron(SZ, I2) + kron(I2, SZ)) + lam * kron(SX, SX)
    return H


# ---------------------------------------------------------------------------
# DM-002 : Sterile neutrino 2-flavor oscillation toy Hamiltonian
# ---------------------------------------------------------------------------
def sterile_neutrino_hamiltonian(
    delta_m2: float = 1.0, energy: float = 1.0, theta: float = np.pi / 4
) -> np.ndarray:
    """Single-qubit 2-flavor oscillation Hamiltonian.

    H = (delta_m2 / 4E) ( -cos(2 theta) Z + sin(2 theta) X )

    Returns a 2x2 (single-qubit) matrix; the second qubit in the IBM Q design
    is an ancilla/register and does not change the analytic oscillation.

    Parameters
    ----------
    delta_m2 : mass-squared difference (eV^2 in the physics analogue).
    energy   : neutrino energy E.
    theta    : mixing angle (pi/4 = maximal mixing).
    """
    prefactor = delta_m2 / (4.0 * energy)
    H = prefactor * (-np.cos(2 * theta) * SZ + np.sin(2 * theta) * SX)
    return H


# ---------------------------------------------------------------------------
# DM-003 : WIMP-nucleon scattering (exchange coupling) toy Hamiltonian
# ---------------------------------------------------------------------------
def wimp_hamiltonian(g: float = 1.0) -> np.ndarray:
    """H = g (X(x)X + Y(x)Y).

    qubit0 = WIMP spin, qubit1 = nucleon spin.

    Parameters
    ----------
    g : coupling constant.
    """
    H = g * (kron(SX, SX) + kron(SY, SY))
    return H


__all__ = [
    "I2",
    "SX",
    "SY",
    "SZ",
    "kron",
    "axion_hamiltonian",
    "sterile_neutrino_hamiltonian",
    "wimp_hamiltonian",
]
