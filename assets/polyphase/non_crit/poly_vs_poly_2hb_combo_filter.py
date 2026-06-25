#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

# This plot compares:
#
#   1. A single polyphase decimator by D
#   2. A cascade:
#
#          polyphase decimator by D/4
#          half-band decimator by 2
#          half-band decimator by 2
#
#      for the same final decimation factor D.
#
# Let:
#
#   Fout = Fs / D
#   r    = transition_bw / Fout
#
# Single polyphase decimator:
#
#   C_single = K/r
#
# Polyphase + two half-band stages:
#
#   C_polyphase = 4K / (3 + r)
#
#   C_hb1 = 2K / (D(1 + r))
#   C_hb2 =  K / (2rD)
#
# Therefore:
#
#   C_combo = 4K/(3+r) + 2K/(D(1+r)) + K/(2rD)
#
# and:
#
#   ratio = C_combo / C_single
#         = 4r/(3+r) + 2r/(D(1+r)) + 1/(2D)

r = np.linspace(0.01, 0.99, 400)

# D must be at least 4 for a cascade of two decimate-by-2 half-band filters.
# The first polyphase stage provides the remaining D/4 decimation.
Ds = [4, 8, 16, 32, 64, 100]

# Single example point:
# 100 MHz input BW, D=8, transition BW = 2 MHz
example_point = {
    "label": "100 MHz input, D=8, transition=2 MHz",
    "fs_hz": 100e6,
    "decimation": 8,
    "fout_hz": 100e6 / 8,
    "transition_hz": 2e6,
}


def combo_ratio_2hb(r, D):
    return 4 * r / (3 + r) + 2 * r / (D * (1 + r)) + 1 / (2 * D)


fig, ax = plt.subplots(figsize=(8, 5))

line_handles = []
for D in Ds:
    ratio = combo_ratio_2hb(r, D)
    line, = ax.plot(r, ratio, label=f"D={D}")
    line_handles.append(line)

break_even = ax.axhline(1.0, linestyle="--", linewidth=1, label="break-even")
line_handles.append(break_even)

ax.set_xlabel("Transition width / final output sample rate")
ax.set_ylabel("Combo cost / single polyphase cost")
ax.set_title("Decimation: Polyphase Filter vs Polyphase + 2 Half-Band Combo")

ax.set_ylim(0, 1.25)
ax.set_xlim(0, 1.0)
ax.grid(True)

# Region labels, placed around 1/4th of the horizontal panel.
ax.text(0.25, 1.06, "Polyphase")
ax.text(0.20, 0.93, "Polyphase + 2 Half-Bands")

# Plot just one example point as a fat black X.
D = example_point["decimation"]
rr = example_point["transition_hz"] / example_point["fout_hz"]
ratio = combo_ratio_2hb(rr, D)

ax.plot(
    rr,
    ratio,
    marker="x",
    linestyle="None",
    markersize=14,
    markeredgewidth=3,
    color="black",
)

# Label placed relative to the X marker: lower-right of the marker.
ax.annotate(
    example_point["label"],
    xy=(rr, ratio),
    xytext=(12, -10),
    textcoords="offset points",
    ha="left",
    va="top",
)

ax.legend(handles=line_handles, title="Model curves", loc="lower right")

fig.tight_layout()

output_path = "poly_vs_poly_2hb_combo_filter.png"
fig.savefig(output_path, dpi=160)
output_path = "poly_vs_poly_2hb_combo_filter.svg"
fig.savefig(output_path, dpi=160)
plt.show()
