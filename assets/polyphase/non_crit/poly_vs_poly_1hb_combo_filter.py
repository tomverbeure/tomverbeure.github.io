#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

# r = transition width / final output sample rate, where final Fout = Fs/D.
# Ratio = combo cost / single-polyphase cost:
#
#   C_single = K/r
#   C_combo  = 2K/(1+r) + K/(2rD)
#
# Therefore:
#
#   ratio = C_combo / C_single
#         = 2r/(1+r) + 1/(2D)

r = np.linspace(0.01, 0.99, 400)
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

fig, ax = plt.subplots(figsize=(8, 5))

line_handles = []
for D in Ds:
    ratio = 2 * r / (1 + r) + 1 / (2 * D)
    line, = ax.plot(r, ratio, label=f"D={D}")
    line_handles.append(line)

break_even = ax.axhline(1.0, linestyle="--", linewidth=1, label="break-even")
line_handles.append(break_even)

ax.set_xlabel("Transition width / final output sample rate")
ax.set_ylabel("Combo cost / single polyphase cost")
ax.set_title("Decimation: Polyphase Filter vs Polyphase + Half-Band Combo")

ax.set_ylim(0, 1.25)
ax.set_xlim(0, 1.0)
ax.grid(True)

# Region labels, placed around 1/4th of the horizontal panel.
ax.text(0.25, 1.06, "Polyphase")
ax.text(0.20, 0.93, "Polyphase + Half-Band")

# Plot just one example point as a fat black X
D = example_point["decimation"]
rr = example_point["transition_hz"] / example_point["fout_hz"]
ratio = 2 * rr / (1 + rr) + 1 / (2 * D)

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

# Keep only the model-curves legend
ax.legend(handles=line_handles, title="Model curves", loc="lower right")

fig.tight_layout()

output_path = "poly_vs_poly_1hb_combo.png"
fig.savefig(output_path, dpi=160)
output_path = "poly_vs_poly_1hb_combo.svg"
fig.savefig(output_path, dpi=160)
plt.show()
