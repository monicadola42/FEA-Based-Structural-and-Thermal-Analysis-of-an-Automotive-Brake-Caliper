# FEA-Based Structural and Thermal Analysis of an Automotive Brake Caliper using ANSYS

## Project Overview

This project presents a Finite Element Analysis (FEA) study of an automotive disc brake caliper using ANSYS Workbench. The study evaluates structural response under a simplified braking load and thermal response under a simplified braking heat-transfer condition.

The workflow covers CAD preparation, material definition, finite element meshing, static structural analysis, steady-state thermal analysis, and mesh convergence.

## Objectives

- Evaluate equivalent (von-Mises) stress under a braking load.
- Evaluate total deformation of the caliper.
- Calculate the factor of safety using the selected material yield strength.
- Evaluate the temperature distribution through the caliper.
- Perform a basic mesh convergence check.
- Present the simulation workflow and results in a reproducible project format.

## Software and Tools

- ANSYS Workbench 2026 R1 Student
- ANSYS Mechanical
- CadQuery 2.x
- Python
- STEP CAD format

## Model

The brake caliper geometry was generated parametrically using CadQuery and exported as a STEP file for ANSYS Workbench.

![Brake Caliper Geometry](images/01_cad_geometry.png)

## Analysis Workflow

```text
Parametric CAD Model
        ↓
STEP Import into ANSYS
        ↓
Material Definition
        ↓
Finite Element Mesh
        ↓
Static Structural Analysis
        ↓
Stress + Deformation + Factor of Safety
        ↓
Steady-State Thermal Analysis
        ↓
Temperature Distribution
        ↓
Mesh Convergence
        ↓
Results and Engineering Interpretation
```

## 1. Static Structural Analysis

A simplified braking force of **1000 N** was applied to the brake-pad contact region. The mounting-hole regions were constrained using fixed supports.

### Results

| Parameter | Result |
|---|---:|
| Maximum Equivalent Stress | **5.859 MPa** |
| Maximum Total Deformation | **0.00412 mm** |
| Material Yield Strength | **250 MPa** |
| Factor of Safety | **42.67** |

### Equivalent Stress

![Equivalent Stress](images/02_static_equivalent_stress.png)

The maximum equivalent stress obtained from the simulation was approximately **5.859 MPa**.

### Total Deformation

![Total Deformation](images/03_static_total_deformation.png)

The maximum total deformation was approximately **0.00412 mm**, indicating very small displacement under the applied simplified load.

## 2. Steady-State Thermal Analysis

A simplified thermal loading and convection condition were used to study heat distribution through the caliper.

### 5 mm Mesh Result

| Parameter | Result |
|---|---:|
| Maximum Temperature | **456.87 °C** |
| Minimum Temperature | **316.25 °C** |

![Thermal Temperature Distribution](images/04_thermal_temperature_5mm.png)

The result shows the temperature gradient across the caliper, with the highest temperature concentrated around the brake-pad/contact region and lower temperatures toward the outer/mounting regions.

## 3. Mesh Convergence

Two mesh sizes were compared for the thermal solution.

| Mesh Size | Maximum Temperature |
|---|---:|
| 10 mm | 466.39 °C |
| 5 mm | 456.87 °C |

Percentage change:

**2.04%**

This indicates that refining the mesh from 10 mm to 5 mm changed the maximum temperature by only about 2.04%, providing a basic mesh-convergence check.

## Key Findings

- The calculated maximum equivalent stress was **5.859 MPa**.
- The calculated maximum deformation was **0.00412 mm**.
- The calculated factor of safety was **42.67** based on a 250 MPa yield strength.
- The maximum temperature from the refined 5 mm thermal mesh was **456.87 °C**.
- The thermal mesh refinement changed the maximum temperature by only **2.04%**.

## Project Structure

FEA_Brake_Caliper_ANSYS/
│
├── README.md
├── .gitignore
│
├── cad/
│   └── brake_caliper_parametric.py
│
├── images/
│   ├── 01_cad_geometry.png
│   ├── 02_static_equivalent_stress.png
│   ├── 03_static_total_deformation.png
│   ├── 04_thermal_temperature_5mm.png
│   └── 05_thermal_temperature_10mm.png
│
└── results/
    └── results_summary.md

## Engineering Note

This is an academic/project-level FEA study using simplified loading and thermal assumptions. The results should therefore be interpreted as simulation-study results rather than certified production-design values.

## Author

**Monica Dola**
