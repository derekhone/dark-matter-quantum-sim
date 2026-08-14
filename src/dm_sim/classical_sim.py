"""Exact classical simulation of the toy Hamiltonians.

Uses exact matrix exponentiation ``U(t) = exp(-i H t)`` (scipy) to evolve
states, plus closed-form / analytic references for the kill-condition check.

HONEST SCOPE: classical simulation of toy Hamiltonians only. Not dark matter.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.linalg import expm

from .hamiltonians import (
    SZ,
    I2,
    axion_hamiltonian,
    dark_photon_hamiltonian,
    kron,
    majorana_hamiltonian,
    sterile_neutrino_hamiltonian,
    wimp_hamiltonian,
)


# ---------------------------------------------------------------------------
# Generic evolution helpers
# ---------------------------------------------------------------------------
def evolve(H: np.ndarray, psi0: np.ndarray, t: float) -> np.ndarray:
    """Return |psi(t)> = exp(-i H t) |psi0>."""
    U = expm(-1j * H * t)
    return U @ psi0


def expectation(op: np.ndarray, psi: np.ndarray) -> float:
    """Return the real expectation value <psi|op|psi>."""
    return float(np.real(np.conjugate(psi) @ (op @ psi)))


def _dominant_period(times: np.ndarray, signal: np.ndarray) -> float:
    """Estimate the dominant oscillation period of a real signal via FFT.

    Removes the DC component, finds the peak positive frequency, returns 1/f.
    """
    sig = np.asarray(signal, dtype=float)
    sig = sig - sig.mean()
    dt = float(times[1] - times[0])
    n = len(sig)
    # zero-pad for finer frequency resolution
    n_fft = 1 << int(np.ceil(np.log2(n * 8)))
    spectrum = np.abs(np.fft.rfft(sig, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=dt)
    # ignore the zero-frequency bin
    peak = 1 + int(np.argmax(spectrum[1:]))
    f_peak = freqs[peak]
    if f_peak <= 0:
        return float("inf")
    return 1.0 / f_peak


# ---------------------------------------------------------------------------
# DM-001 : Axion
# ---------------------------------------------------------------------------
def simulate_axion(
    omega_0: float = 1.0,
    lam: float = 0.3,
    t_max: float = 20.0,
    n_steps: int = 2000,
) -> dict:
    """Simulate <sigma_z> on qubit 0 vs time for the axion toy model.

    Returns a dict with times, sigma_z series, measured period and the target
    period 2*pi/omega_0.
    """
    H = axion_hamiltonian(omega_0, lam)
    psi0 = np.zeros(4, dtype=complex)
    psi0[0] = 1.0  # |00>
    sz_q0 = kron(SZ, I2)

    times = np.linspace(0.0, t_max, n_steps)
    sz = np.empty(n_steps)
    for i, t in enumerate(times):
        psi = evolve(H, psi0, t)
        sz[i] = expectation(sz_q0, psi)

    measured_period = _dominant_period(times, sz)
    target_period = 2.0 * np.pi / omega_0
    return {
        "times": times,
        "sigma_z": sz,
        "measured_period": measured_period,
        "target_period": target_period,
        "omega_0": omega_0,
        "lambda": lam,
    }


# ---------------------------------------------------------------------------
# DM-002 : Sterile neutrino oscillation
# ---------------------------------------------------------------------------
def neutrino_survival_analytic(
    L: float | np.ndarray,
    delta_m2: float = 1.0,
    energy: float = 1.0,
    theta: float = np.pi / 4,
) -> np.ndarray:
    """Analytic 2-flavor survival probability P(nu_mu -> nu_mu).

    P = 1 - sin^2(2 theta) * sin^2(1.27 * delta_m2 * L / E)
    (1.27 is the standard L[km], E[GeV], delta_m2[eV^2] conversion constant.)
    """
    L = np.asarray(L, dtype=float)
    return 1.0 - (np.sin(2 * theta) ** 2) * np.sin(1.27 * delta_m2 * L / energy) ** 2


def simulate_neutrino(
    delta_m2: float = 1.0,
    energy: float = 1.0,
    theta: float = np.pi / 4,
    L_max: float = 3.0,
    n_steps: int = 300,
) -> dict:
    """Simulate the survival probability both analytically and via matrix exp.

    The Hamiltonian phase and the 1.27 L/E phase are matched so the two curves
    can be compared for the kill condition (must agree within 1%).
    """
    H = sterile_neutrino_hamiltonian(delta_m2, energy, theta)
    psi0 = np.array([0.0, 1.0], dtype=complex)  # |nu_mu>

    L = np.linspace(0.0, L_max, n_steps)
    analytic = neutrino_survival_analytic(L, delta_m2, energy, theta)

    omega = delta_m2 / (4.0 * energy)
    survival_matrix = np.empty(n_steps)
    for i, Li in enumerate(L):
        phi = 1.27 * delta_m2 * Li / energy
        t = phi / omega if omega != 0 else 0.0
        psi = evolve(H, psi0, t)
        amp = np.conjugate(psi0) @ psi
        survival_matrix[i] = float(np.abs(amp) ** 2)

    max_abs_diff = float(np.max(np.abs(analytic - survival_matrix)))
    return {
        "L": L,
        "analytic": analytic,
        "matrix": survival_matrix,
        "max_abs_diff": max_abs_diff,
        "delta_m2": delta_m2,
        "energy": energy,
        "theta": theta,
    }


# ---------------------------------------------------------------------------
# DM-003 : WIMP scattering
# ---------------------------------------------------------------------------
def wimp_flip_analytic(g: float, t: float | np.ndarray) -> np.ndarray:
    """Closed form spin-flip probability for H = g(XX+YY): P = sin^2(2 g t)."""
    t = np.asarray(t, dtype=float)
    return np.sin(2.0 * g * t) ** 2


def simulate_wimp(
    g: float = 1.0,
    t_max: float | None = None,
    n_steps: int = 400,
) -> dict:
    """Simulate the |01> -> |10> spin-flip probability vs time.

    Also evaluates the flip probability at the quarter-period t = pi/(4g),
    which the closed form predicts to be 1.0.
    """
    if t_max is None:
        t_max = np.pi / g
    H = wimp_hamiltonian(g)
    psi0 = np.zeros(4, dtype=complex)
    psi0[1] = 1.0  # |01>

    times = np.linspace(0.0, t_max, n_steps)
    flip = np.empty(n_steps)
    for i, t in enumerate(times):
        psi = evolve(H, psi0, t)
        flip[i] = float(np.abs(psi[2]) ** 2)

    analytic = wimp_flip_analytic(g, times)
    max_abs_diff = float(np.max(np.abs(flip - analytic)))

    t_quarter = np.pi / (4.0 * g)
    psi_q = evolve(H, psi0, t_quarter)
    flip_quarter = float(np.abs(psi_q[2]) ** 2)

    return {
        "times": times,
        "flip": flip,
        "analytic": analytic,
        "max_abs_diff": max_abs_diff,
        "t_quarter": t_quarter,
        "flip_at_quarter": flip_quarter,
        "g": g,
    }


# ---------------------------------------------------------------------------
# DM-004 : Dark Photon Kinetic Mixing
# ---------------------------------------------------------------------------
def dark_photon_conversion_analytic(
    t: float | np.ndarray,
    omega_gamma: float = 1.0,
    omega_dark: float = 1.3,
    epsilon: float = 0.5,
) -> np.ndarray:
    """Analytic gamma -> dark photon conversion probability.

    P(gamma -> A', t) = [eps^2 / (Delta^2 + eps^2)] sin^2(Omega t)

    where Delta = omega_gamma - omega_dark, Omega = sqrt(Delta^2 + eps^2).
    """
    t = np.asarray(t, dtype=float)
    Delta = omega_gamma - omega_dark
    Omega = np.sqrt(Delta**2 + epsilon**2)
    P_max = epsilon**2 / (Delta**2 + epsilon**2)
    return P_max * np.sin(Omega * t) ** 2


def simulate_dark_photon(
    omega_gamma: float = 1.0,
    omega_dark: float = 1.3,
    epsilon: float = 0.5,
    t_max: float = 15.0,
    n_steps: int = 500,
) -> dict:
    """Simulate gamma -> dark photon conversion probability vs time.

    Compares exact matrix exponentiation with the analytic formula in the
    single-excitation subspace.  Initial state |10> (one visible photon).
    """
    H = dark_photon_hamiltonian(omega_gamma, omega_dark, epsilon)
    psi0 = np.zeros(4, dtype=complex)
    psi0[2] = 1.0  # |10>

    times = np.linspace(0.0, t_max, n_steps)
    analytic = dark_photon_conversion_analytic(
        times, omega_gamma, omega_dark, epsilon
    )

    conversion_matrix = np.empty(n_steps)
    for i, t in enumerate(times):
        psi = evolve(H, psi0, t)
        conversion_matrix[i] = float(np.abs(psi[1]) ** 2)

    max_abs_diff = float(np.max(np.abs(analytic - conversion_matrix)))

    Delta = omega_gamma - omega_dark
    Omega = np.sqrt(Delta**2 + epsilon**2)
    t_peak = np.pi / (2.0 * Omega)
    P_max_analytic = epsilon**2 / (Delta**2 + epsilon**2)

    psi_peak = evolve(H, psi0, t_peak)
    P_max_sim = float(np.abs(psi_peak[1]) ** 2)

    return {
        "times": times,
        "conversion_sim": conversion_matrix,
        "conversion_analytic": analytic,
        "max_abs_diff": max_abs_diff,
        "t_peak": t_peak,
        "P_max_sim": P_max_sim,
        "P_max_analytic": P_max_analytic,
        "omega_gamma": omega_gamma,
        "omega_dark": omega_dark,
        "epsilon": epsilon,
        "Delta": Delta,
        "Omega": Omega,
    }


# ---------------------------------------------------------------------------
# DM-005 : Majorana Mass Seesaw
# ---------------------------------------------------------------------------
def majorana_lnv_analytic(
    t: float | np.ndarray,
    m_D: float = 0.5,
    M_R: float = 2.0,
) -> np.ndarray:
    """Analytic lepton-number-violation probability for the seesaw toy model.

    P_LNV(t) = (m_D / Omega)^2 sin^2(Omega t)

    where Omega = sqrt(m_D^2 + (M_R/2)^2).
    """
    t = np.asarray(t, dtype=float)
    Omega = np.sqrt(m_D**2 + (M_R / 2.0) ** 2)
    amplitude = (m_D / Omega) ** 2
    return amplitude * np.sin(Omega * t) ** 2


def simulate_majorana(
    m_D: float = 0.5,
    M_R: float = 2.0,
    t_max: float = 15.0,
    n_steps: int = 500,
) -> dict:
    """Simulate lepton-number-violation probability vs time for the seesaw model.

    Initial state |00> (active neutrino, lepton number +1).
    Observable: P(|00> -> |11>) = P_LNV (lepton number violation).
    """
    H = majorana_hamiltonian(m_D, M_R)
    psi0 = np.zeros(4, dtype=complex)
    psi0[0] = 1.0  # |00>

    times = np.linspace(0.0, t_max, n_steps)
    analytic = majorana_lnv_analytic(times, m_D, M_R)

    lnv_matrix = np.empty(n_steps)
    for i, t in enumerate(times):
        psi = evolve(H, psi0, t)
        lnv_matrix[i] = float(np.abs(psi[3]) ** 2)

    max_abs_diff = float(np.max(np.abs(analytic - lnv_matrix)))

    Omega = np.sqrt(m_D**2 + (M_R / 2.0) ** 2)
    t_peak = np.pi / (2.0 * Omega)
    P_max_analytic = (m_D / Omega) ** 2

    psi_peak = evolve(H, psi0, t_peak)
    P_max_sim = float(np.abs(psi_peak[3]) ** 2)

    seesaw_approx = 4.0 * m_D**2 / M_R**2

    return {
        "times": times,
        "lnv_sim": lnv_matrix,
        "lnv_analytic": analytic,
        "max_abs_diff": max_abs_diff,
        "t_peak": t_peak,
        "P_max_sim": P_max_sim,
        "P_max_analytic": P_max_analytic,
        "seesaw_approx": seesaw_approx,
        "m_D": m_D,
        "M_R": M_R,
        "Omega": Omega,
    }


__all__ = [
    "evolve",
    "expectation",
    "simulate_axion",
    "neutrino_survival_analytic",
    "simulate_neutrino",
    "wimp_flip_analytic",
    "simulate_wimp",
    "dark_photon_conversion_analytic",
    "simulate_dark_photon",
    "majorana_lnv_analytic",
    "simulate_majorana",
]
