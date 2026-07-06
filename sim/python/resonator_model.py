"""
Butterworth-Van Dyke (BVD) equivalent circuit model for AIN piezoelectric resonator.

Motional arm:  Lm (series) -- Rm (series) -- Cm (series)
Parallel arm:  C0

Series resonance:  fs  = 1 / (2*pi*sqrt(Lm*Cm))
Parallel resonance: fp = fs * sqrt(1 + Cm/C0)
Q-factor:          Q   = 2*pi*fs*Lm / Rm  =  1 / (2*pi*fs*Cm*Rm)

Typical AIN FBAR (1 GHz):
  Lm ~ 100 nH,  Cm ~ 250 aF,  Rm ~ 0.5 Ω,  C0 ~ 2 pF
  -> Q ~ 1000–3000
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field


@dataclass
class BVDResonator:
    Lm: float   # motional inductance [H]
    Cm: float   # motional capacitance [F]
    Rm: float   # motional resistance [Ω]
    C0: float   # parallel capacitance [F]
    name: str = "BVD"

    @property
    def fs(self):
        return 1 / (2 * np.pi * np.sqrt(self.Lm * self.Cm))

    @property
    def fp(self):
        return self.fs * np.sqrt(1 + self.Cm / self.C0)

    @property
    def Q(self):
        return 2 * np.pi * self.fs * self.Lm / self.Rm

    def impedance(self, f: np.ndarray) -> np.ndarray:
        w = 2 * np.pi * f
        Z_motional = 1j * w * self.Lm + self.Rm + 1 / (1j * w * self.Cm)
        Z_C0       = 1 / (1j * w * self.C0)
        return (Z_motional * Z_C0) / (Z_motional + Z_C0)


# ── Typical AIN FBAR parameters at ~1 GHz ───────────────────────────────────
ain_fbar = BVDResonator(
    Lm = 100e-9,    # 100 nH
    Cm = 250e-18,   # 250 aF
    Rm = 0.5,       # 0.5 Ω
    C0 = 2e-12,     # 2 pF
    name = "AIN FBAR (1 GHz)"
)

# Low-frequency crystal (for PCB Tier-3 demo)
watch_crystal = BVDResonator(
    Lm = 4.4e-3,    # 4.4 mH  (typical 32.768 kHz watch crystal)
    Cm = 5.4e-15,   # 5.4 fF
    Rm = 35e3,      # 35 kΩ
    C0 = 1.8e-12,   # 1.8 pF
    name = "32.768 kHz Watch Crystal"
)

quartz_1mhz = BVDResonator(
    Lm = 10e-3,     # 10 mH
    Cm = 2.5e-15,   # 2.5 fF
    Rm = 10,        # 10 Ω
    C0 = 5e-12,     # 5 pF
    name = "1 MHz Quartz Crystal"
)

resonators = [ain_fbar, watch_crystal, quartz_1mhz]

fig, axes = plt.subplots(len(resonators), 2, figsize=(13, 4 * len(resonators)))
fig.suptitle('BVD Resonator Models — Impedance & Phase', fontsize=13, fontweight='bold')

for row, res in enumerate(resonators):
    fs = res.fs
    f  = np.linspace(fs * 0.95, fs * 1.05, 5000)
    Z  = res.impedance(f)

    ax_mag = axes[row, 0]
    ax_ph  = axes[row, 1]

    ax_mag.semilogy(f / 1e6, np.abs(Z), color='royalblue', linewidth=1.5)
    ax_mag.axvline(res.fs / 1e6, color='firebrick', linestyle='--', linewidth=1,
                   label=f'fs={res.fs/1e6:.4f} MHz')
    ax_mag.axvline(res.fp / 1e6, color='seagreen', linestyle='--', linewidth=1,
                   label=f'fp={res.fp/1e6:.4f} MHz')
    ax_mag.set_ylabel('|Z| [Ω]')
    ax_mag.set_title(f'{res.name}  (Q={res.Q:.0f})')
    ax_mag.legend(fontsize=8)
    ax_mag.grid(True, which='both', alpha=0.3)

    ax_ph.plot(f / 1e6, np.angle(Z, deg=True), color='darkorange', linewidth=1.5)
    ax_ph.axvline(res.fs / 1e6, color='firebrick', linestyle='--', linewidth=1)
    ax_ph.axvline(res.fp / 1e6, color='seagreen', linestyle='--', linewidth=1)
    ax_ph.set_ylabel('Phase [°]')
    ax_ph.set_xlabel('Frequency [MHz]')
    ax_ph.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('analysis/bvd_resonator_models.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n=== Resonator Summary ===")
for res in resonators:
    print(f"\n{res.name}")
    print(f"  fs = {res.fs/1e6:.6f} MHz")
    print(f"  fp = {res.fp/1e6:.6f} MHz")
    print(f"  Q  = {res.Q:.1f}")
    print(f"  Bandwidth = {res.fs / res.Q / 1e3:.2f} kHz")
