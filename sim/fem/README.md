# FEM Simulation of AIN Piezoelectric Resonator

## Tools
- **COMSOL Multiphysics** (Structural Mechanics + Electrostatics modules): gold standard, expensive license
- **FEniCS/FEniCSx** (open source): requires implementing piezoelectric constitutive equations manually
- **OpenFOAM** (not ideal): no piezoelectric module
- **ANSYS Mechanical** (university licenses common): has piezoelectric module

## Goal
Simulate a bulk AIN FBAR resonator to:
1. Confirm mechanical resonant frequency matches BVD analytical model
2. Extract Q-factor from damping model
3. Study geometry sensitivity (thickness → fs, electrode area → kt²)
4. Validate BEOL thermal budget constraints

## AIN Material Parameters

| Property | Value | Units |
|----------|-------|-------|
| Density ρ | 3260 | kg/m³ |
| c₃₃ (stiffness, along c-axis) | 395 | GPa |
| e₃₃ (piezo coefficient) | 1.55 | C/m² |
| ε₃₃ (permittivity, along c-axis) | 9.5 · ε₀ | F/m |
| Sound velocity (longitudinal) | ~11,300 | m/s |

## Resonant Frequency vs. Thickness

For a FBAR resonating in thickness-extensional mode:
```
fs = v_AIN / (2 · t_AIN)
   = 11300 / (2 · t)
```

| Target fs | Required t_AIN |
|-----------|----------------|
| 1 GHz | 5.65 µm |
| 2 GHz | 2.83 µm |
| 5 GHz | 1.13 µm |

These are BEOL-compatible thicknesses (standard Cu damascene is 2–5 µm per layer).

## COMSOL Model Setup (Sketch)

1. **Geometry**: Rectangular FBAR stack
   - Bottom electrode: Mo, 200 nm
   - AIN piezo layer: t_AIN (sweep from 1–10 µm)
   - Top electrode: Mo, 200 nm
   - Air gap below (FBAR) or Bragg reflector (SMR-FBAR)

2. **Physics**:
   - Solid Mechanics: linear elastic + piezoelectric coupling
   - Electrostatics: V applied top/bottom electrode
   - Boundary: fixed bottom (SMR) or free (FBAR cavity)

3. **Study**:
   - Eigenfrequency study → find fs, fp
   - Frequency domain study → extract admittance Y(f), fit BVD
   - Extract kt² = (fp² - fs²) / fp²

4. **Meshing**: λ/20 maximum element size in AIN layer
   - At 1 GHz, λ_AIN = 11.3 µm → max element 0.56 µm
   - ~50,000 DOF for 2D cross-section

## FEniCS Skeleton (open-source path)

See `fem/ain_fbar_fenics.py` (to be implemented).
Requires: `dolfinx`, `petsc4py`, `mpi4py`.

Constitutive equations for piezoelectric AIN:
```
σ_ij = c_ijkl · ε_kl - e_kij · E_k    (stress)
D_i  = e_ikl · ε_kl + ε_ij · E_j      (electric displacement)
```

## References
- Piazza et al., JMEMS 2006: FBAR geometry optimization
- Dubois & Muralt, J. Appl. Phys. 2001: AIN material constants
- COMSOL Piezoelectric Devices Module User Guide
