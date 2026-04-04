#! /usr/bin/env python3

import matplotlib.pyplot as plt

def plot_alias_panel_with_original(
    fL_khz: float,
    fH_khz: float,
    fs_list_khz: list[float],
    fc_khz: float | None = None,
    xlim_khz: tuple[float, float] = (-10.0, 10.0),
    K: int = 6,
    vertical_compress: float = 12.0,
    lane_gap: float = 0.22,
    label_dx_khz: float = 0.1,
    trapezoid_slant_frac: float = 0.25,
    alpha: float = 0.25,
    figsize: tuple[float, float] = (12.0, 5.2),
    title: str = "Bandpass sampling aliases",
):
    if fc_khz is None:
        fc_khz = 0.5 * (fL_khz + fH_khz)

    xmin, xmax = xlim_khz
    H = 1.0 / vertical_compress
    lane_height = H * 1.55

    cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    k_values = list(range(-K, K + 1))
    k_to_color = {k: cycle[(k + K) % len(cycle)] for k in k_values}
    k_to_color[0] = cycle[0]

    fig, ax = plt.subplots(figsize=figsize)

    def draw_trapezoid(x0, x1, y0, upper, color):
        w = (x1 - x0) * trapezoid_slant_frac
        if upper:
            xs = [x0, x1, x1 - w, x0]
        else:
            xs = [x0, x1, x1, x0 + w]
        ys = [y0, y0, y0 + H, y0 + H]
        ax.fill(xs, ys, alpha=alpha, color=color, linewidth=0)

    def draw_center(c, y0, color):
        if xmin <= c <= xmax:
            ax.plot([c, c], [y0, y0 + H], linestyle=":", color=color)
            ax.text(
                c + label_dx_khz,
                y0 + H * 1.25,
                f"{c:.2f}",
                rotation=90,
                ha="right",
                va="bottom",
                fontsize=8,
                color=color,
                clip_on=False,
            )

    n_lanes = 1 + len(fs_list_khz)
    total_height = n_lanes * lane_height + (n_lanes - 1) * lane_gap
    extra_top = H * 1.0

    def lane_base(idx_from_top):
        return (n_lanes - 1 - idx_from_top) * (lane_height + lane_gap)

    # --- Lane 0: original ---
    y0 = lane_base(0)
    ax.hlines(y0, xmin, xmax, linewidth=0.8, colors="black")

    col0 = k_to_color[0]
    pL, pH = fL_khz, fH_khz
    if pH >= xmin and pL <= xmax:
        draw_trapezoid(max(pL, xmin), min(pH, xmax), y0, True, col0)
    nL, nH = -fH_khz, -fL_khz
    if nH >= xmin and nL <= xmax:
        draw_trapezoid(max(nL, xmin), min(nH, xmax), y0, False, col0)

    draw_center(+fc_khz, y0, col0)
    draw_center(-fc_khz, y0, col0)

    # --- Sampled lanes ---
    for i, fs_khz in enumerate(fs_list_khz, start=1):
        yb = lane_base(i)
        ax.hlines(yb, xmin, xmax, linewidth=0.8, colors="black")

        # fs label on left of lane
        ax.text(
            xmin,
            yb + H * 0.5,
            f"fs = {fs_khz:g} kHz",
            ha="left",
            va="center",
            fontsize=9,
        )

        for k in range(-K, K + 1):
            col = k_to_color[k]

            c_pos = k * fs_khz + fc_khz
            c_neg = k * fs_khz - fc_khz
            draw_center(c_pos, yb, col)
            draw_center(c_neg, yb, col)

            pL = k * fs_khz + fL_khz
            pH = k * fs_khz + fH_khz
            nL = k * fs_khz - fH_khz
            nH = k * fs_khz - fL_khz

            if pH >= xmin and pL <= xmax:
                draw_trapezoid(max(pL, xmin), min(pH, xmax), yb, True, col)
            if nH >= xmin and nL <= xmax:
                draw_trapezoid(max(nL, xmin), min(nH, xmax), yb, False, col)

    # DC line
    ax.axvline(0.0, linewidth=1.0, color="black")

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0, total_height + extra_top)
    ax.set_xlabel("Frequency (kHz)")
    ax.set_ylabel("")
    ax.set_yticks([])
    ax.grid(False)
    ax.set_title(title)

    fig.tight_layout()
    return fig, ax


fs_values = [2.25, 2.33, 2.5, 3.0, 3.2, 3.5, 4.5, 5.0, 7.0, 9]
fig, ax = plot_alias_panel_with_original(
    fL_khz=3.5,
    fH_khz=4.5,
    fs_list_khz=fs_values,
    xlim_khz=(-8, 8),
    K=6,
    vertical_compress=5.0,
    figsize=(10, 7.2),
    title="Bandpass sampling for different sample rates",
)

svg_path = "alias_panel.svg"
png_path = "alias_panel.png"
fig.savefig(svg_path, format="svg")
fig.savefig(png_path, format="png", dpi=200)

plt.show()

(svg_path, png_path)

