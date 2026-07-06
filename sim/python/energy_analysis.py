"""
PRAL Energy Analysis: Compare energy dissipation across switching paradigms.
  - Standard CMOS:       E = 0.5 * C * V^2
  - RC Adiabatic:        E = (2*R*C/T) * C * V^2   [slow ramp, resistive loss]
  - Resonant (PRAL):     E_approx = C * V^2 / Q     [sinusoidal at resonance]
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

C   = 10e-15   # load capacitance [F]  (10 fF, typical gate)
V   = 1.0      # supply voltage [V]    (1.0 V)
f_s = 1e9      # switching frequency   (1 GHz)
T   = 1 / f_s  # period

Q_range = np.logspace(0, 6, 500)   # Q from 1 to 1e6

E_cmos      = 0.5 * C * V**2
E_pral      = (C * V**2) / Q_range
recovery_eff = (1 - E_pral / E_cmos) * 100

# RC adiabatic: sweep RC/T ratio
RC_T_range = np.logspace(-2, 1, 200)   # RC/T from 0.01 to 10
E_adiabatic = 2 * RC_T_range * C * V**2

fig = plt.figure(figsize=(14, 10))
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

# ── Plot 1: Energy vs Q-factor ──────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
ax1.loglog(Q_range, E_pral * 1e18, color='royalblue', linewidth=2, label='PRAL (resonant)')
ax1.axhline(E_cmos * 1e18, color='firebrick', linewidth=1.5, linestyle='--', label='CMOS baseline')
ax1.set_xlabel('Resonator Q-factor')
ax1.set_ylabel('Energy per transition [aJ]')
ax1.set_title('PRAL Energy vs. Q-factor')
ax1.legend()
ax1.grid(True, which='both', alpha=0.3)

# ── Plot 2: Recovery efficiency vs Q ────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
ax2.semilogx(Q_range, recovery_eff, color='seagreen', linewidth=2)
ax2.axhline(90, color='orange', linestyle=':', linewidth=1.5, label='90% target')
Q_90 = C * V**2 / (0.1 * E_cmos)   # Q needed for 90% recovery
ax2.axvline(Q_90, color='orange', linestyle=':', linewidth=1.5)
ax2.set_xlabel('Resonator Q-factor')
ax2.set_ylabel('Energy Recovery Efficiency [%]')
ax2.set_title('Recovery Efficiency vs. Q')
ax2.legend()
ax2.grid(True, which='both', alpha=0.3)
ax2.set_ylim(0, 100)

# ── Plot 3: Comparison — all three paradigms ────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
Q_compare = np.array([1e1, 1e2, 1e3, 1e4, 1e5])
E_pral_pts = (C * V**2) / Q_compare
ax3.bar(['CMOS'], [E_cmos * 1e18], color='firebrick', alpha=0.8, label='CMOS')
for i, (q, e) in enumerate(zip(Q_compare, E_pral_pts)):
    ax3.bar([f'PRAL\nQ={q:.0e}'], [e * 1e18],
            color=plt.cm.Blues(0.3 + 0.15 * i), alpha=0.9)
ax3.set_ylabel('Energy per transition [aJ]')
ax3.set_title('Energy Comparison (C=10fF, V=1V)')
ax3.set_yscale('log')
ax3.grid(axis='y', alpha=0.3)

# ── Plot 4: RC adiabatic vs PRAL trade-space ────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
ax4.loglog(RC_T_range, E_adiabatic * 1e18, color='darkorange', linewidth=2, label='RC Adiabatic')
Q_equiv = 1 / (2 * RC_T_range)
ax4.loglog(Q_equiv, E_adiabatic * 1e18, color='royalblue', linewidth=2,
           linestyle='--', label='PRAL equivalent Q')
ax4.set_xlabel('RC/T  (adiabatic)  /  1/(2·Q)  (PRAL)')
ax4.set_ylabel('Energy per transition [aJ]')
ax4.set_title('RC Adiabatic vs. PRAL Trade-Space')
ax4.legend(fontsize=8)
ax4.grid(True, which='both', alpha=0.3)

fig.suptitle('PRAL Energy Analysis  |  C=10fF, V=1V, f=1GHz', fontsize=13, fontweight='bold')
plt.savefig('analysis/pral_energy_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n=== Key Numbers ===")
print(f"CMOS baseline energy:       {E_cmos*1e18:.2f} aJ")
print(f"PRAL at Q=1000:             {(C*V**2/1e3)*1e18:.4f} aJ  ({(1-1/1e3)*100:.1f}% recovery)")
print(f"PRAL at Q=10000:            {(C*V**2/1e4)*1e18:.5f} aJ  ({(1-1/1e4)*100:.2f}% recovery)")
print(f"Q needed for 90% recovery:  Q = {int(C*V**2 / (0.1*E_cmos))}")
print(f"Power at 1GHz (CMOS):       {E_cmos * f_s * 1e3:.2f} mW per gate")
print(f"Power at 1GHz (PRAL Q=1e4): {(C*V**2/1e4) * f_s * 1e6:.4f} µW per gate")
