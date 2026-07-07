# PRAL: Piezo-Resonant Adiabatic Logic - Prototype & Experiment Repo

**Based on**: *"PRAL: A Piezo-Resonant Adiabatic Logic Framework for Beyond-CMOS Energy Efficiency"*
**Author**: Peter E. Mbua et al.

---

## Concept Summary

Standard CMOS dissipates **½CV²** per switching transition — charge is dumped to ground on every falling edge, unrecoverable. PRAL proposes:

1. Replace square-wave clock trees with a **high-Q monolithic piezoelectric resonant network** (AIN thin-film resonators in the BEOL stack).
2. The resonator forms an **acoustic-electric tank circuit** — logic transitions driven sinusoidally at the AIN mechanical resonant frequency.
3. The **converse piezoelectric effect** recovers charge from logic gates and stores it as mechanical strain energy in the crystal lattice.
4. Energy dissipation is governed by resonator Q-factor: `E_adiabatic ≈ E_CMOS / Q`.
5. With Q = 10³–10⁵, analytical models predict **>90% energy recovery** at GHz frequencies.

---

## Prototype Strategy (Tiered)

```
Tier 1 — Pure Simulation  (start here, zero cost)
Tier 2 — FPGA / HDL Demo  (demonstrates adiabatic principle on real silicon)
Tier 3 — PCB Hardware     (crystal-driven adiabatic logic, measurable at low freq)
Tier 4 — MEMS/BEOL        (requires fab access: AIN deposition, BEOL integration)
```

---

## Tier 1: Analytical + SPICE Simulation

### 1a. Energy Model (Python)
- Sweep Q-factor (10–10⁵), plot energy recovery vs. Q
- Compare: CMOS ½CV² vs. adiabatic 2RC/T·CV² vs. resonant CV²/Q
- Key insight: at what Q does PRAL beat conventional adiabatic logic?
- Files: `sim/python/energy_analysis.py`, `sim/python/resonator_model.py`

### 1b. Butterworth-Van Dyke (BVD) Resonator Model (SPICE)
The standard equivalent circuit for a piezoelectric resonator:
```
        Lm       Rm       Cm
  o---[====]---[===]---||---o
  |                         |
  +----------||  C0---------+
```
- Series arm (motional): Lm, Cm, Rm → models mechanical resonance
- Parallel arm: C0 → electrode/package capacitance
- Series resonance: fs = 1/(2π√(Lm·Cm))
- Q = 2π·fs·Lm / Rm

Experiment: extract impedance-frequency curve, confirm resonant peak, measure Q.
Files: `sim/spice/bvd_resonator.cir`

### 1c. Adiabatic Inverter SPICE
- Implement standard inverter driven by: (a) square-wave, (b) sinusoidal clock at fs
- Instrument supply current, integrate to get energy per cycle
- Expected result: sinusoidal drive at resonance dramatically reduces dissipation
- Files: `sim/spice/adiabatic_inverter.cir`, `sim/spice/energy_comparison.cir`

---

## Tier 2: RTL / FPGA Demo

### 2a. Adiabatic Gates in SystemVerilog
- Model ECRL (Efficient Charge Recovery Logic) or PAL (Pass-transistor Adiabatic Logic) gates
- Testbench measures switching activity and estimates energy with `$power` annotations
- Compare: standard logic vs. adiabatic logic, same function
- Files: `rtl/adiabatic_gates/`, `rtl/tb/`

### 2b. FPGA Power Measurement
- Implement a compute-intensive kernel (MAC array, shift register chain)
- Clock it with: (a) standard PLL square-wave, (b) sinusoidal approximation via Sigma-Delta/PWM
- Measure on-chip power via Xilinx Power Estimator or on-board INA226
- **Key limitation**: FPGA fabric is CMOS hard-switches — can't recover charge — but demonstrates
  the *switching frequency* and *slew rate* sensitivity to energy dissipation.
- Target board: Nexys A7 / Basys3 / Arty A7

---

## Tier 3: PCB Hardware Prototype

### 3a. Low-Frequency CPAL Demo (Crystal Adiabatic Logic)
The core PRAL principle can be demonstrated at audio/low-MHz frequencies using off-shelf components:

**Clock source**: 32.768 kHz watch crystal or 1–10 MHz quartz MEMS resonator
- Drives load capacitance sinusoidally
- Recovers energy each half-cycle through LC tank

**Circuit**: 
```
Crystal osc (resonant) → LC matching network → CPAL buffer chain → Load cap
                                  ↑
                        Energy recovery path (inductor)
```

**Measurement**: INA219/INA226 precision power monitor on supply rail
- Compare: crystal-resonant clock vs. buffered square-wave clock, same load

**BOM**: see `hardware/pcb_bom/tier3_bom.md`

### 3b. MEMS Resonator Evaluation Board
- Source a commercial AIN MEMS resonator (Akoustis, pSemi, Qorvo BAW filters)
- Characterize Q-factor with network analyzer (or NanoVNA)
- Use as clock source for adiabatic logic PCB
- Target Q: 1000+ at 1–5 GHz

---

## Tier 4: MEMS/BEOL Integration (Research-Grade)

Requires:
1. **AIN deposition**: PECVD or sputtering tool + c-axis texture optimization
2. **BEOL-compatible process**: post-metal dielectric, <400°C thermal budget
3. **Patterning**: wet etch or ICP-RIE of AIN resonator geometry
4. **Electrode metal**: Mo or W bottom/top electrodes
5. **Characterization**: S-parameter (VNA), X-ray diffraction (XRD for texture quality)

**Feasibility path without full fab**:
- Collaborate with a MEMS foundry (Silex, IMT, IMEC) for test chip
- Use open MPW (e.g., Sky130 + custom BEOL AIN stack at research partner)
- Alternatively: validate with FBAR (Film Bulk Acoustic Resonator) eval boards from telecom industry

---

## Key Equations

| Quantity | Expression |
|----------|------------|
| CMOS energy/cycle | `E_cmos = ½·C·V²` |
| Adiabatic (RC) energy | `E_ad = (2RC/T)·C·V²` |
| Resonant (PRAL) energy | `E_pral ≈ C·V²/Q` |
| Q-factor | `Q = 2π·f_s·L_m / R_m` |
| Series resonance | `f_s = 1/(2π√(L_m·C_m))` |
| Energy recovery efficiency | `η = 1 - 1/Q` |

At Q = 1000: η = 99.9% (theoretical)

---

## Repository Structure

```
pral-prototype/
├── README.md
├── docs/
│   └── theory.md              # Mathematical derivations
├── sim/
│   ├── python/
│   │   ├── energy_analysis.py # Energy sweep: CMOS vs adiabatic vs PRAL
│   │   ├── resonator_model.py # BVD model: impedance, Q, resonant freq
│   │   └── requirements.txt
│   ├── spice/
│   │   ├── bvd_resonator.cir  # Butterworth-Van Dyke BVD model
│   │   ├── adiabatic_inv.cir  # Inverter: square vs sinusoidal clock
│   │   └── energy_compare.cir # Energy comparison testbench
│   └── fem/
│       └── README.md          # COMSOL/FEniCS AIN resonator FEM notes
├── rtl/
│   ├── adiabatic_gates/
│   │   ├── ecrl_inv.sv        # ECRL adiabatic inverter model
│   │   └── ecrl_nand.sv       # ECRL NAND gate
│   └── tb/
│       └── tb_ecrl.sv         # Testbench with power annotation
├── notebooks/
│   └── 01_pral_exploration.ipynb
├── hardware/
│   └── pcb_bom/
│       └── tier3_bom.md       # Bill of materials for PCB demo
└── analysis/
    └── q_factor_sweep.py      # Standalone Q-factor analysis script
```

---

## Getting Started

```bash
# Install Python deps
pip install -r sim/python/requirements.txt

# Run energy analysis
python sim/python/energy_analysis.py

# Open exploration notebook
jupyter notebook notebooks/01_pral_exploration.ipynb

# Run SPICE simulation (requires ngspice)
ngspice sim/spice/bvd_resonator.cir
```

---

## References

- Athas et al., "Low-Power Digital Systems Based on Adiabatic-Switching Principles," IEEE TVLSI 1994
- Butterworth-Van Dyke equivalent circuit model (IEEE standard for piezoelectric resonators)
- Hashimoto, "RF Bulk Acoustic Wave Filters for Communications," Artech House 2009
- Piazza et al., "Piezoelectric Aluminum Nitride Vibrating Contour-Mode MEMS Resonators," JMEMS 2006
