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


# ---------------------------------------------------------------------------
# DM-004 : Dark Photon Kinetic Mixing (off-resonance gamma-A' oscillation)
# ---------------------------------------------------------------------------
def dark_photon_hamiltonian(
    omega_gamma: float = 1.0,
    omega_dark: float = 1.3,
    epsilon: float = 0.5,
) -> np.ndarray:
    r"""H = omega_gamma (Z (x) I) + omega_dark (I (x) Z) + epsilon (X (x) X).

    qubit0 = visible photon mode, qubit1 = dark photon mode.
    omega_gamma and omega_dark are the mode frequencies; epsilon is the kinetic
    mixing parameter.  In the single-excitation subspace {|10>, |01>} the
    effective 2-level system exhibits off-resonance Rabi oscillation with
    conversion probability

        P(gamma -> A', t) = [eps^2 / (Delta^2 + eps^2)] sin^2(Omega t)

    where Delta = omega_gamma - omega_dark and Omega = sqrt(Delta^2 + eps^2).

    Parameters
    ----------
    omega_gamma : visible photon mode frequency.
    omega_dark  : dark photon mode frequency.
    epsilon     : kinetic mixing coupling constant.
    """
    H = (omega_gamma * kron(SZ, I2)
         + omega_dark * kron(I2, SZ)
         + epsilon * kron(SX, SX))
    return H


# ---------------------------------------------------------------------------
# DM-005 : Majorana Mass (seesaw mechanism toy model)
# ---------------------------------------------------------------------------
def majorana_hamiltonian(
    m_D: float = 0.5,
    M_R: float = 2.0,
) -> np.ndarray:
    r"""H = m_D (X (x) X) + (M_R / 2) (I (x) Z).

    qubit0 = left-handed neutrino, qubit1 = right-handed neutrino.
    m_D is the Dirac mass coupling, M_R is the Majorana mass.

    The Hamiltonian block-diagonalizes:
      - Block {|00>, |11>}: (M_R/2) sigma_z + m_D sigma_x
      - Block {|01>, |10>}: -(M_R/2) sigma_z + m_D sigma_x

    Starting from |00>, the lepton-number-violation probability is

        P_LNV(t) = (m_D / Omega)^2  sin^2(Omega t)

    where Omega = sqrt(m_D^2 + (M_R/2)^2).  In the seesaw limit M_R >> m_D
    this amplitude is suppressed as ~4 m_D^2 / M_R^2, reproducing the
    qualitative behavior of the type-I seesaw mechanism.

    Parameters
    ----------
    m_D : Dirac mass coupling constant.
    M_R : Majorana mass.
    """
    H = m_D * kron(SX, SX) + (M_R / 2.0) * kron(I2, SZ)
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
    "dark_photon_hamiltonian",
    "majorana_hamiltonian",
]
