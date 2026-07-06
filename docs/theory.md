# PRAL Theoretical Framework

## 1. The Power Wall Problem

Standard CMOS energy per switching transition:

```
E_cmos = ½ · C · V²
```

At each 0→1→0 cycle, the charge Q = CV is sourced from VDD, then dumped to GND. The energy stored in C (½CV²) is dissipated in the pull-down NMOS — not recoverable.

At 1 GHz, 1 billion gates, 10 fF each, α=0.2 switching activity:
```
P = α · f · C · V² · N
  = 0.2 × 1e9 × 10e-15 × 1.0² × 1e9
  = 2 W  (just from CV² charging)
```

Dennard scaling (constant field) assumed V shrinks with L — but V stopped scaling ~2005. Now: more transistors but same (or worse) power density.

---

## 2. Adiabatic Logic Principle

**Adiabatic** = thermodynamically reversible → zero theoretical entropy production.

Practical adiabatic logic uses a **slow ramp** (RC << T) to charge/discharge load capacitance. Energy dissipated in the resistance R over period T:

```
E_adiabatic = (2RC/T) · C · V²
```

As T → ∞ (infinitely slow transition), E → 0. But T is bounded by clock frequency.

**Problem with RC adiabatic**: requires external inductor or power supply to generate the ramp. On-chip inductors at GHz have very low Q (~10–30 in standard CMOS metal stack).

---

## 3. PRAL: Piezoelectric Resonance as the "Engine"

PRAL substitutes the low-Q on-chip inductor with a **high-Q AIN piezoelectric resonator** (FBAR or MEMS).

### Resonant Energy Recovery

In an LC tank circuit driven at resonance (ω = ω₀ = 1/√LC):
- Energy alternates between magnetic (inductor) and electric (capacitor) storage
- Only dissipation path: resistance R in motional arm
- Energy loss per cycle: `ΔE = E_stored / Q = C·V²/Q`

Therefore PRAL energy per gate transition:
```
E_pral ≈ C · V² / Q
```

For Q = 1000: `E_pral = E_cmos / 500` (0.2% of conventional CMOS)

### AIN Resonator as Mechanical Energy Buffer

AIN (aluminum nitride) has strong piezoelectric coupling (k_t² ~ 6–7%). In the FBAR structure:
- Electrical signal ↔ mechanical (acoustic) vibration via piezoelectric coupling
- Acoustic wave in AIN lattice stores energy as mechanical strain
- **Converse piezoelectric effect**: AC electric field → mechanical stress → strain energy storage
- **Direct piezoelectric effect**: strain → voltage → energy returned to circuit

This is exactly what PRAL exploits: the AIN resonator acts as a lossless (high-Q) energy shuttle between the electrical domain (logic gates) and the mechanical domain (acoustic wave in the crystal lattice).

---

## 4. Butterworth-Van Dyke Model

The standard equivalent circuit for a piezoelectric resonator:

```
         Lm        Rm        Cm
Port1 ---OOOO---/\/\/\---||---+--- Port2
         |                    |
         +--------- C0 -------+
```

| Parameter | Physical meaning | Typical AIN FBAR (1 GHz) |
|-----------|-----------------|--------------------------|
| Lm        | Motional mass (inductance ↔ inertia) | 100 nH |
| Cm        | Elastic compliance (capacitance ↔ spring) | 250 aF |
| Rm        | Acoustic loss (viscous damping + electrode) | 0.5 Ω |
| C0        | Static electrode capacitance | 2 pF |

Series resonance (minimum |Z|, maximum current):
```
fs = 1 / (2π√(Lm·Cm))
```

Q-factor:
```
Q = 2π·fs·Lm / Rm = 1 / (2π·fs·Cm·Rm)
```

---

## 5. Integration Path (BEOL-AIN)

AIN deposition is BEOL-compatible (< 400°C, sputtered):
1. Deposit W or Mo bottom electrode after last metal layer
2. Sputter AIN (~c-axis texture required for strong piezoelectric coupling)
3. Deposit top electrode (W/Mo)
4. Pattern resonator geometry (ICP-RIE, wet KOH etch for cavity release)
5. Connect to metal routing of standard CMOS logic layer below

Key metric: **electromechanical coupling coefficient** kt² = Cm / (Cm + C0) × π²/4

For AIN: kt² ~ 6–7% → sufficient coupling for GHz FBAR operation.

---

## 6. Key Experimental Metrics

| Metric | Target | Measurement method |
|--------|--------|--------------------|
| Resonator Q | > 1000 at 1 GHz | S11/S21 on VNA, BVD fit |
| kt² | > 5% | Admittance circle fit |
| fs accuracy | ± 0.1% of design | Resonance peak in impedance |
| Energy recovery | > 90% | Integrate supply current, compare |
| Thermal throttle relief | ΔT < 5°C at full load | IR camera on test chip |

---

## 7. Literature Anchors

- **Adiabatic switching limit**: Athas et al., IEEE TVLSI 1994
- **ECRL (Efficient Charge Recovery Logic)**: Moon & Jeong, IEEE JSSC 1996  
- **AIN FBAR for BEOL**: Piazza et al., JMEMS 2006; Akoustis Tech whitepaper
- **Mechanical Q in AIN**: Ruby, IEEE UFFC 2015 (Q > 3000 demonstrated)
- **Power density crisis**: Esmaeilzadeh et al., "Dark Silicon" ISCA 2011
