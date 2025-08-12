#! /usr/bin/env python3

# Nonlinear Class-C settling via a discrete per-cycle map
# y_{k+1} = α e^{jθ} y_k + Δv(y_k),  with conduction set by a thresholded current.
# Plots: |y| (envelope), per-cycle charge Qp, conduction angle γ.

import numpy as np
import matplotlib.pyplot as plt

# Tank
L, C, Q = 1e-6, 100e-12, 50.0
f0 = 1/(2*np.pi*np.sqrt(L*C)); w0 = 2*np.pi*f0; tau = 2*Q/w0

# Drive & map constants
df = 0.02*f0; fd = f0 + df; Td = 1/fd; wd = 2*np.pi*fd
alpha = np.exp(-Td/tau)              # decay per cycle
theta = 2*np.pi*f0/fd                # rotation per cycle (≈ 2π − 2π Δf/fd)

# Device: thresholded Class-C current i = Gm*(Vd sin θ − Vth_eff), clipped at 0
Vd, Vth, Gm, kappa = 1.8, 1.2, 1.0, 0.002   # kappa couples tank v into threshold (toy feedback)

def cycle_Qp_and_gamma(y_real):
    # Effective threshold increases with tank amplitude (compression)
    Veff = Vth + kappa*y_real
    if Veff >= Vd:                      # no conduction
        return 0.0, 0.0
    xi = Veff / Vd                      # must be in (−1, 1)
    xi = np.clip(xi, -0.999999, 0.999999)
    th1 = np.arcsin(xi)                 # conduction starts at θ=th1, ends at θ=π−th1
    # ∫(Vd sinθ − Veff) dθ over [th1, π−th1]
    Qp = (2*Gm/wd) * ( Vd*np.sqrt(1-xi*xi) + Veff*(th1 - np.pi/2) )
    gamma = np.pi - 2*th1               # conduction angle (rad)
    return Qp, gamma

# Iterate map
N = 400
y = np.zeros(N, dtype=complex)
Qp = np.zeros(N); gamma = np.zeros(N)
for k in range(N-1):
    Qp_k, gk = cycle_Qp_and_gamma(y[k].real)
    y[k+1] = alpha*np.exp(1j*theta)*y[k] + (Qp_k/C)
    Qp[k] = Qp_k; gamma[k] = gk

t = np.arange(N)*Td
A = np.abs(y)

plt.figure(); plt.plot(t*1e6, A); plt.xlabel("Time (µs)"); plt.ylabel("|y| [V]")
plt.title("Nonlinear settling (Class-C): AM-AM compression"); plt.tight_layout()

plt.figure(); plt.plot(t*1e6, Qp); plt.xlabel("Time (µs)"); plt.ylabel("Qp per cycle [C]")
plt.title("Per-cycle injected charge falls as amplitude grows"); plt.tight_layout()

plt.figure(); plt.plot(t*1e6, gamma); plt.xlabel("Time (µs)"); plt.ylabel("Conduction angle γ [rad]")
plt.title("Conduction angle adapts to a fixed point"); plt.tight_layout(); plt.show()

