from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple, Optional

import numpy as np
from scipy.signal import firwin


@dataclass(frozen=True)
class SigInfo:
    nr_samples: int
    sample_rate: float
    frequencies_hz: Sequence[float]
    amplitudes_db: Sequence[float]
    stopband_center_hz: float
    stopband_width_hz: float
    noise_floor_db: float
    oob_noise_db: float
    oob_filter_taps: int
    oob_kaiser_beta: float


def generate_signal(
    info: SigInfo,
    *,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    if len(info.frequencies_hz) != len(info.amplitudes_db):
        raise ValueError("frequencies_hz and amplitudes_db must have the same length.")

    if rng is None:
        rng = np.random.default_rng()

    t = np.arange(info.nr_samples) / info.sample_rate

    signal_pure = np.zeros(info.nr_samples)
    for idx, (freq_hz, ampl_db) in enumerate(zip(info.frequencies_hz, info.amplitudes_db)):
        ampl = 10 ** (ampl_db / 20.0)
        if idx % 2 == 0:
            signal_pure += ampl * np.sin(2 * np.pi * freq_hz * t)
        else:
            signal_pure += ampl * np.cos(2 * np.pi * freq_hz * t)

    floor_noise_rms = 10 ** (info.noise_floor_db / 20.0)
    floor_noise = rng.normal(0.0, floor_noise_rms, info.nr_samples)

    oob_noise_rms = 10 ** (info.oob_noise_db / 20.0)
    oob_noise = rng.normal(0.0, oob_noise_rms, info.nr_samples)

    oob_noise_filtered = oob_noise
    if info.stopband_width_hz > 0:
        nyq = info.sample_rate / 2.0
        half = info.stopband_width_hz / 2.0
        low = max(0.0, info.stopband_center_hz - half)
        high = min(nyq * 0.999999, info.stopband_center_hz + half)
        if low > 0.0 and high > low:
            cutoffs = [low / nyq, high / nyq]
            oob_noise_h = firwin(
                info.oob_filter_taps,
                cutoffs,
                window=("kaiser", info.oob_kaiser_beta),
                pass_zero="bandstop",
            )
            oob_noise_filtered = np.convolve(oob_noise, oob_noise_h, mode="same")

    signal = signal_pure + floor_noise + oob_noise_filtered
    return t, signal
