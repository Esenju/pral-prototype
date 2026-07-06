# Tier 3 PCB Prototype — Bill of Materials

## Goal
Demonstrate energy recovery from resonant clocking at low frequency (32.768 kHz or 1–4 MHz) using off-shelf discrete components. Measure supply energy with vs. without resonant power-clock.

## Core Idea
Replace the hard-switch digital clock buffer with a crystal-resonant LC tank that drives the load capacitance sinusoidally. Measure current integral on INA226 power monitor.

---

## Component List

| # | Component | Part Number / Source | Qty | Est. Cost | Purpose |
|---|-----------|---------------------|-----|-----------|---------|
| 1 | 32.768 kHz watch crystal | ECS-.327-12.5-34B (DigiKey) | 2 | $0.50ea | Low-freq resonant clock source |
| 2 | 1 MHz quartz crystal | ECS-10-18-4X (DigiKey) | 2 | $0.80ea | Mid-freq experiment |
| 3 | INA226 breakout board | Adafruit #4226 or SparkFun | 1 | $10 | Precision power measurement |
| 4 | CMOS inverter (74LVC1G04) | SN74LVC1G04DBVR | 4 | $0.30ea | Standard CMOS baseline |
| 5 | CD4069UB (unbuffered) | CD4069UBPWR | 2 | $0.60ea | CMOS for adiabatic load |
| 6 | 100 µH inductor (low DCR) | SRR1210-101Y (Bourns) | 2 | $0.70ea | LC tank resonance matching |
| 7 | 100 pF C0G/NP0 caps | GRM1555C1H101FA01 (Murata) | 10 | $0.10ea | Tank caps, load caps |
| 8 | 10 nF C0G caps | GRM21BR71H103KA01 | 4 | $0.15ea | Bypass / timing |
| 9 | STM32 Nucleo-F446RE | Already owned | 1 | — | MCU for data logging, PWM approx |
| 10| NanoVNA V2 (optional) | NanoVNA-F V2 | 1 | $60 | Crystal Q-factor characterization |
| 11| 2N7002 N-MOSFET | 2N7002K-7-F | 4 | $0.20ea | Switching load |
| 12| BSS84 P-MOSFET | BSS84-7-F | 4 | $0.25ea | Adiabatic PMOS recovery |
| 13| 10Ω 1% resistor | ERJ-6ENF10R0V | 4 | $0.05ea | Current sense |
| 14| PCB (2-layer, OSH Park) | — | 1 | ~$15 | 4-layer optional for GND plane |

**Estimated Total**: ~$100 (excluding NanoVNA)

---

## Experiments to Run

### Exp-A: Crystal Q-factor Measurement
1. Connect crystal in π-network with 2× 22 pF series caps
2. Sweep impedance with NanoVNA across fs ± 5%
3. Fit BVD model parameters (Lm, Cm, Rm, C0)
4. Compute Q = 2π·fs·Lm / Rm
5. **Expected**: Q ~ 50,000–100,000 for 32.768 kHz crystal

### Exp-B: Hard-Switch vs. Resonant Clock Energy
1. **Reference (hard-switch)**: 74LVC1G04 driving 100 pF load at 32.768 kHz
   - Measure energy with INA226: E_ref = ∫(V·I)dt per cycle
2. **Resonant**: crystal oscillator driving same 100 pF load through LC matching
   - Crystal + 100 µH inductor forms series resonant tank
   - Measure E_resonant
3. Compute recovery ratio = (E_ref - E_resonant) / E_ref

### Exp-C: Adiabatic Inverter Ring
1. Build 3-stage ring with CD4069UB (unbuffered CMOS)
2. Power-clock: sinusoidal from crystal osc via transformer coupling
3. Compare oscillation energy: capacitor-only load vs. LC recovery path
4. **Caveats**: CD4069 has hard switches internally — demo only shows interconnect energy recovery, not gate switching energy. True adiabatic needs custom IC.

---

## Measurement Setup

```
Crystal OSC → LC matching → Load (100pF) → Return inductor path
                  |
               INA226 (Vbus, Iin monitor)
                  |
            STM32 I2C readout → energy_log.csv
```

STM32 firmware: sample INA226 at 1 kHz, log V, I, timestamp → post-process in Python.

---

## Scaling to GHz

The PCB demo operates at 32.768 kHz–1 MHz to make energy differences measurable.
At these frequencies:
- Crystal Q ~ 50,000–100,000 (much higher than GHz FBAR Q ~ 1000–3000)
- Energy savings will be dramatic (>99%) — sets upper bound
- The fundamental physics is identical to the GHz BEOL case
- Gap to fill: at GHz, FBAR Q is lower but frequencies are 30,000× higher → total power savings still enormous

```
Power = E_per_cycle × f
P_cmos  = ½CV² × 1GHz  = 5 µW/gate
P_pral  = CV²/Q × 1GHz = 5 nW/gate  (Q=1000)
```
