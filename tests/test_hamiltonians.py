"""Tests for the toy Hamiltonians."""

import numpy as np

from dm_sim.hamiltonians import (
    axion_hamiltonian,
    kron,
    sterile_neutrino_hamiltonian,
    wimp_hamiltonian,
    SX,
    SY,
    SZ,
    I2,
)


def test_pauli_algebra():
    # sigma_x^2 = I, and XY = iZ
    assert np.allclose(SX @ SX, I2)
    assert np.allclose(SX @ SY, 1j * SZ)


def test_kron_shape_and_value():
    op = kron(SZ, I2)
    assert op.shape == (4, 4)
    assert np.allclose(op, np.kron(SZ, I2))


def test_axion_hermitian():
    H = axion_hamiltonian(1.0, 0.3)
    assert H.shape == (4, 4)
    assert np.allclose(H, H.conj().T)


def test_axion_terms_present():
    H = axion_hamiltonian(omega_0=2.0, lam=0.5)
    expected = 2.0 * (kron(SZ, I2) + kron(I2, SZ)) + 0.5 * kron(SX, SX)
    assert np.allclose(H, expected)


def test_sterile_neutrino_hermitian_and_shape():
    H = sterile_neutrino_hamiltonian(1.0, 1.0, np.pi / 4)
    assert H.shape == (2, 2)
    assert np.allclose(H, H.conj().T)


def test_sterile_neutrino_maximal_mixing_is_pure_x():
    # at theta = pi/4, cos(2 theta) = 0 so H is proportional to X
    H = sterile_neutrino_hamiltonian(1.0, 1.0, np.pi / 4)
    assert abs(H[0, 0]) < 1e-12
    assert abs(H[1, 1]) < 1e-12
    assert abs(H[0, 1]) > 0


def test_wimp_hermitian_and_shape():
    H = wimp_hamiltonian(1.0)
    assert H.shape == (4, 4)
    assert np.allclose(H, H.conj().T)


def test_wimp_conserves_excitation_number():
    # XX+YY exchange preserves total excitation: no coupling to |00> or |11>
    H = wimp_hamiltonian(1.0)
    # |00> index 0, |11> index 3 should not couple to single-excitation block
    assert np.allclose(H[0, :], 0)
    assert np.allclose(H[3, :], 0)
