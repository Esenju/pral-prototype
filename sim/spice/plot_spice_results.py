"""
Post-processor for ngspice wrdata output.
ngspice wrdata format: each vector is preceded by its sweep variable,
so columns repeat as: [sweep, val1, sweep, val2, sweep, val3, ...]
"""

import numpy as np
import matplotlib.pyplot as plt
import os, sys

os.makedirs("analysis", exist_ok=True)

def load_wrdata(path, n_vectors):
    """
    Load ngspice wrdata file.
    n_vectors: number of data vectors (not counting the repeated sweep cols).
    Returns: (sweep, data) where data has shape (n_rows, n_vectors).
    """
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(('#', '*')):
                continue
            try:
                rows.append([float(x) for x in line.split()])
            except ValueError:
                continue
    arr = np.array(rows)
    # Columns: sweep, v0, sweep, v1, sweep, v2, ...
    sweep = arr[:, 0]
    data  = arr[:, 1::2]          # every 2nd col starting at index 1
    return sweep, data


# ─────────────────────────────────────────────────────────────────────────────
# BVD resonator results
# ─────────────────────────────────────────────────────────────────────────────
bvd_ok    = os.path.exists("sim/spice/out_bvd.dat")
energy_ok = os.path.exists("sim/spice/out_energy2.dat")

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle("PRAL SPICE Simulation Results", fontsize=14, fontweight='bold')

if bvd_ok:
    freq, d = load_wrdata("sim/spice/out_bvd.dat", 2)
    Zmag   = d[:, 0]
    Zphase = d[:, 1]
    freq_GHz = freq / 1e9

    i_min = np.argmin(Zmag)
    i_max = np.argmax(Zmag)
    fs_sim = freq[i_min]
    fp_sim = freq[i_max]
    Lm = 100e-9
    Q_analytical = 2 * np.pi * fs_sim * Lm / 0.5

    ax = axes[0, 0]
    ax.semilogy(freq_GHz, Zmag, color='royalblue', linewidth=2)
    ax.axvline(fs_sim / 1e9, color='firebrick', linestyle='--', linewidth=1.2,
               label=f'fs = {fs_sim/1e9:.4f} GHz')
    ax.axvline(fp_sim / 1e9, color='seagreen', linestyle='--', linewidth=1.2,
               label=f'fp = {fp_sim/1e9:.4f} GHz')
    ax.set_xlabel('Frequency [GHz]')
    ax.set_ylabel('|Z| [Ω]')
    ax.set_title(f'BVD AIN FBAR — Impedance  (Q={Q_analytical:.0f})')
    ax.legend(fontsize=9)
    ax.grid(True, which='both', alpha=0.3)

    ax2 = axes[0, 1]
    ax2.plot(freq_GHz, Zphase, color='darkorange', linewidth=2)
    ax2.axhline(0,  color='gray',     linestyle=':', linewidth=1)
    ax2.axvline(fs_sim / 1e9, color='firebrick', linestyle='--', linewidth=1.2,
                label=f'fs = {fs_sim/1e9:.4f} GHz')
    ax2.axvline(fp_sim / 1e9, color='seagreen',  linestyle='--', linewidth=1.2,
                label=f'fp = {fp_sim/1e9:.4f} GHz')
    ax2.set_xlabel('Frequency [GHz]')
    ax2.set_ylabel('Phase [°]')
    ax2.set_title('BVD AIN FBAR — Phase Response')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    print(f"\n=== BVD SPICE Results ===")
    print(f"  fs (min |Z|):   {fs_sim/1e9:.5f} GHz   (target 1.006 GHz)")
    print(f"  fp (max |Z|):   {fp_sim/1e9:.5f} GHz")
    print(f"  |Z| at fs:      {Zmag[i_min]:.4f} Ω     (designed Rm = 0.5 Ω)")
    print(f"  Q (analytical): {Q_analytical:.0f}")
else:
    for ax in axes[0]:
        ax.text(0.5, 0.5, 'Run bvd_resonator.cir first',
                ha='center', va='center', transform=ax.transAxes, color='gray')

# ─────────────────────────────────────────────────────────────────────────────
# Energy comparison results
# ─────────────────────────────────────────────────────────────────────────────
if energy_ok:
    t_us, d2 = load_wrdata("sim/spice/out_energy.dat", 3)
    t_us = t_us * 1e6      # s → µs
    vA   = d2[:, 0]
    vB   = d2[:, 1]

    te, de = load_wrdata("sim/spice/out_energy2.dat", 4)
    te_us   = te * 1e6
    E_capA  = de[:, 0] * 1e12    # J → pJ
    E_capB  = de[:, 1] * 1e12
    E_indB  = de[:, 2] * 1e12
    E_totB  = de[:, 3] * 1e12

    ax3 = axes[1, 0]
    ax3.plot(t_us, vA, color='firebrick', linewidth=1.8, label='Hard-switch RC  (τ=5ns)')
    ax3.plot(t_us, vB, color='royalblue', linewidth=1.4, label='LC resonant  (Q=1000)')
    ax3.set_xlabel('Time [µs]')
    ax3.set_ylabel('Capacitor voltage [V]')
    ax3.set_title('Voltage Waveforms')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, 5)         # zoom to first 5 µs to show both behaviours

    ax4 = axes[1, 1]
    ax4.plot(te_us, E_capA,  color='firebrick',  linewidth=1.8, label='Hard-switch (cap energy)')
    ax4.plot(te_us, E_totB,  color='royalblue',  linewidth=1.8, label='LC resonant (cap+ind)')
    ax4.plot(te_us, E_capB,  color='steelblue',  linewidth=1,   linestyle='--', label='LC cap only')
    ax4.set_xlabel('Time [µs]')
    ax4.set_ylabel('Stored energy [pJ]')
    ax4.set_title('Energy Retention vs. Time')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)

    E0 = 50.0   # pJ initial
    pct_B = E_totB[-1] / E0 * 100
    ax4.annotate(f'{pct_B:.1f}% retained\nafter 20 µs',
                 xy=(te_us[-1], E_totB[-1]),
                 xytext=(te_us[-1]*0.55, E_totB[-1]*0.88),
                 arrowprops=dict(arrowstyle='->', color='royalblue'),
                 color='royalblue', fontsize=9)

    print(f"\n=== Energy Comparison SPICE Results ===")
    print(f"  Initial energy (both):           {E0:.1f} pJ")
    print(f"  Case A (RC)  — final stored:     {E_capA[-1]:.4f} pJ  ({E_capA[-1]/E0*100:.2f}% remaining)")
    print(f"  Case B (LC)  — cap energy:       {E_capB[-1]:.2f} pJ")
    print(f"  Case B (LC)  — inductor energy:  {E_indB[-1]:.4f} pJ")
    print(f"  Case B (LC)  — TOTAL stored:     {E_totB[-1]:.2f} pJ  ({pct_B:.1f}% remaining)")
    E_lost_B = E0 - E_totB[-1]
    print(f"  Case B energy lost over 20 µs:   {E_lost_B:.2f} pJ  ({E_lost_B/20:.3f} pJ/cycle)")
    print(f"  Analytical target (CV²/Q):        {E0/1000:.3f} pJ/cycle")
    print(f"  Ratio A/B (total loss):          {E0/E_lost_B:.0f}× less energy lost with resonance")
else:
    for ax in axes[1]:
        ax.text(0.5, 0.5, 'Run energy_compare.cir first',
                ha='center', va='center', transform=ax.transAxes, color='gray')

plt.tight_layout()
plt.savefig('analysis/pral_spice_results.png', dpi=150, bbox_inches='tight')
print(f"\nPlot saved → analysis/pral_spice_results.png")
