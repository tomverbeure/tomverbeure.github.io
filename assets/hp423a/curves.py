#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

v = np.arange(-10.5, 2, 0.01)
i = 0.05*(np.exp(5*v)-1)
mask = v<=-10.05
i[mask] = v[mask]*10

q_mask = v<0.6
q = 1.7*v[q_mask]*v[q_mask]+0.015

q_mask = v<0.6
q2 = 1.99*v[q_mask]*v[q_mask]

i_q_delta = np.abs(q-i[q_mask])

fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax.plot(v,i)
ax.set_title("Diode I/V Curve")
ax.set_xlabel('Vd')
ax.set_ylabel('I(Vd)')
ax.grid(True, which='both')
ax.spines['left'].set_position('zero')
ax.spines['bottom'].set_position('zero')
ax.xaxis.tick_bottom()
ax.set_ylim(-2.1, 3.1)
ax.set_xlim(-11, 1.5)
ax.legend(["Diode I/V curve"], loc="upper left")
fig.tight_layout()
fig.savefig("diode_iv_curve.png")
#plt.show()

fig = plt.figure(figsize=(10,6))
ax = fig.add_subplot(111)
ax.plot(v,i)
ax.plot(v[q_mask],q)
#ax.plot(v[q_mask],i_q_delta)
ax.set_title("Diode I/V Curve - Subthreshold")
ax.set_xlabel('Vd')
ax.set_ylabel('I(Vd)')
ax.grid(True, which='both')
ax.spines['left'].set_position('zero')
ax.spines['bottom'].set_position('zero')
ax.xaxis.tick_bottom()
ax.set_ylim(-0.5, 1.0)
ax.set_xlim(-0.5, 1)
ax.legend(["Exponential I/V curve", "Quadratic approximation"], loc="upper right")
fig.tight_layout()
fig.savefig("diode_iv_curve_subthreshold.png")
#plt.show()

fig = plt.figure(figsize=(10,6))
ax = fig.add_subplot(111)
ax.plot(v,i)
ax.plot(v[q_mask],q2)
#ax.plot(v[q_mask],i_q_delta)
ax.set_title("Diode I/V Curve - Subthreshold")
ax.set_xlabel('Vd')
ax.set_ylabel('I(Vd)')
ax.grid(True, which='both')
ax.spines['left'].set_position('zero')
ax.spines['bottom'].set_position('zero')
ax.xaxis.tick_bottom()
ax.set_ylim(-0.5, 1.0)
ax.set_xlim(-0.5, 1)
ax.legend(["Exponential I/V curve", "Quadratic approximation"], loc="upper right")
fig.tight_layout()
fig.savefig("diode_iv_curve_subthreshold2.png")
plt.show()

