# Jump Landing Biomechanics: OpenSim Inverse Kinetics & Knee Extensor Muscle Forces

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/LTUebl/jump-landing-opensim/blob/main/JumpLanding_OpenSim_Analysis.ipynb)
[![Interactive Web Guide](https://img.shields.io/badge/Public_Site-Interactive_Dashboard-blue?logo=googlechrome&logoColor=white)](https://ltuebl.github.io/jump-landing-opensim/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github&logoColor=white)](https://github.com/LTUebl/jump-landing-opensim)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)

**Course:** BME 4903 Advanced Kinesiology / Biomechanics of Movement  
**Institution:** Lawrence Technological University · Department of Biomedical Engineering · Experimental Biomechanics Lab  
**Public Interactive Website:** [https://ltuebl.github.io/jump-landing-opensim/](https://ltuebl.github.io/jump-landing-opensim/)

---

## 1. Overview & Objectives

This repository provides an automated, student-friendly **Google Colab pipeline** and **interactive web dashboard** to analyze single-cycle jump landing kinematics, inverse kinetics (ground reaction forces), and knee extensor muscle forces using data collected from **OpenCap** and modeled in **OpenSim**.

### Key Learning Objectives:
1. **Automated Single-Cycle Event Detection:** Automatically identify landing events—**Jump Apex** ($t_{apex}$), **Initial Contact** ($t_{IC}$), and **Maximum Knee Flexion** ($t_{KM}$)—without requiring manual multi-cycle segmentation.
2. **Inverse Kinetics ($vGRF$):** Quantify total vertical Ground Reaction Forces in Newtons ($N$) and normalized to Body Weight ($BW$). Evaluate peak impact force, loading rate ($BW/s$), and vertical impulse ($J_y = \int vGRF\, dt$).
3. **Knee Extensor Muscle Forces:** Quantify individual quadriceps muscle forces across the absorption phase:
   - **Vastus Lateralis (`vaslat`)** — dominant extensor torque contributor.
   - **Vastus Medialis (`vasmed`)** — medial patellar stabilizer.
   - **Vastus Intermedius (`vasint`)** — deep uniarticular extensor.
   - **Rectus Femoris (`recfem`)** — biarticular hip flexor and knee extensor.
4. **Landing Posture Comparison:** Compare **Forward Trunk Lean** vs. **Upright Trunk** landing strategies.
5. **Injury Prevention (ACL Risk):** Understand how trunk posture, knee flexion angles, and quadriceps forces dictate anterior tibial shear and non-contact ACL injury risk.

---

## 2. Quick Links & Downloads

| Resource | Description | Link |
| :--- | :--- | :--- |
| **Google Colab Notebook** | Complete interactive pipeline ready to run in one click | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/LTUebl/jump-landing-opensim/blob/main/JumpLanding_OpenSim_Analysis.ipynb) |
| **Interactive Web Dashboard** | Interactive charts, data tables, and lab questions | [https://ltuebl.github.io/jump-landing-opensim/](https://ltuebl.github.io/jump-landing-opensim/) |
| **Example OpenCap Dataset** | Lightweight Subject EGM session dataset (1.39 MB) | [`data/JumpLanding_OpenCap_OpenSimData_EGM.zip`](data/JumpLanding_OpenCap_OpenSimData_EGM.zip) |
| **Excel Summary Spreadsheet** | Precomputed metrics and 101-point curves | [`data/JumpLanding_Posture_Comparison.xlsx`](data/JumpLanding_Posture_Comparison.xlsx) |
| **4-Panel Overlay Figure** | Publication-quality comparison plot | [`assets/JumpLanding_Posture_Comparison_Overlay.png`](assets/JumpLanding_Posture_Comparison_Overlay.png) |
| **Detailed Knee Extensors Plot** | Individual vasti and rectus femoris breakdown | [`assets/JumpLanding_KneeExtensors_Detailed.png`](assets/JumpLanding_KneeExtensors_Detailed.png) |

---

## 3. Reference Biomechanical Results (Subject EGM)

The example dataset evaluates Subject EGM (Mass = 95 kg, Height = 1.95 m) performing a **Forward Lean Landing** (`LeaningJump`) vs. an **Upright Landing** (`UprightJump`):

| Biomechanical Metric | Forward Lean Landing | Upright Landing | Difference | Biomechanical Significance |
| :--- | :---: | :---: | :---: | :--- |
| **Lumbar Angle at KM** | **-51.2°** (Deep Lean) | **-6.3°** (Erect) | -44.9° | Postural intervention check |
| **Peak Knee Flexion** | **78.9°** | **54.0°** | +24.9° | Compliant landing strategy; deeper flexion |
| **Absorption Duration** | **0.433 s** | **0.167 s** | +0.266 s (+160%) | Longer deceleration window attenuates impact |
| **Peak Total vGRF** | **4.10 BW** (3,820 N) | **4.45 BW** (4,143 N) | +0.35 BW (+8.5%) | Stiff upright landing increases peak impact force |
| **Impact Loading Rate** | **18.6 BW/s** | **55.0 BW/s** | +36.4 BW/s (nearly 3×) | High loading rates cause cartilage microdamage |
| **Vertical Impulse** | **0.79 BW·s** (740 N·s) | **0.40 BW·s** (368 N·s) | +0.39 BW·s | Total momentum dissipated over absorption window |
| **Peak `vaslat` Force** | **3,526 N** | **4,831 N** | +1,305 N (+37%) | Dominant vastus muscle; upright demands +37% force |
| **Peak `recfem` Force** | **749 N** | **1,270 N** | +521 N (+69.5%) | Biarticular muscle on stretch across extended hip |
| **Total Quadriceps Peak** | **7,042 N** (7.56 BW) | **7,872 N** (8.45 BW) | +830 N (+11.8%) | Upright posture dramatically increases knee demand |

---

## 4. How Students Run the Google Colab Notebook

### Zero-Restart Setup (Crash-Free)
Unlike older methods that required `condacolab` and triggered kernel crashes, this notebook runs natively using pre-installed Google Colab packages:
1. Open [`JumpLanding_OpenSim_Analysis.ipynb`](https://colab.research.google.com/github/LTUebl/jump-landing-opensim/blob/main/JumpLanding_OpenSim_Analysis.ipynb) in Google Colab.
2. Click **Runtime $\rightarrow$ Run All** (or run cell-by-cell).
3. **Data Input Options in Part 1:**
   - **Option A (Student Data):** Click the **"Choose Files"** button in Part 1.1 to upload an OpenCap session `.zip` file collected with smartphone cameras.
   - **Option B (Example Data):** If no file is uploaded, the notebook automatically downloads the Subject EGM reference dataset from GitHub!
4. **Automatic Download:** At the end of the notebook, it automatically triggers a browser download for:
   - `JumpLanding_Posture_Comparison_Overlay.png` (4-panel graph)
   - `JumpLanding_KneeExtensors_Detailed.png` (4 muscle breakdown)
   - `JumpLanding_Posture_Comparison.xlsx` (multi-sheet Excel summary)

---

## 5. Lab Report Discussion Questions & Solutions

### Question 1: Impact Attenuation & Impulse-Momentum Principles
* **Question:** Why does landing with forward trunk lean reduce peak vGRF and loading rate compared to upright landing?
* **Answer:** By the impulse-momentum theorem, $J = \Delta p = \int F\, dt = m \Delta v$. Since initial contact velocity is fixed by jump height, the required momentum change $\Delta p$ is nearly identical. Forward trunk lean facilitates greater knee flexion (78.9° vs 54.0°) and hip flexion, more than doubling the deceleration duration (0.433 s vs 0.167 s). Spreading the impulse over a longer time interval significantly reduces peak force (4.10 BW vs 4.45 BW) and slashes impact loading rate from 55.0 BW/s to 18.6 BW/s.

### Question 2: Biarticular Rectus Femoris Mechanics
* **Question:** Why does the rectus femoris experience nearly 70% higher peak force in the upright posture (1,270 N vs 749 N)?
* **Answer:** Rectus femoris is the only biarticular quadriceps muscle crossing both the anterior hip (flexor) and anterior knee (extensor). In an upright landing (extended hip), the muscle fibers of rectus femoris are stretched across the hip joint. Under the sliding filament force-length relationship, this places the muscle fibers in a lengthened, higher-tension region. In forward trunk lean, the flexed hip passively shortens rectus femoris, decreasing its active force generation.

### Question 3: Vasti Muscle Force Sharing
* **Question:** Which individual vastus muscle generates the largest force, and why?
* **Answer:** The vastus lateralis (`vaslat`) generates the highest force (4,831 N upright, 3,526 N leaning). Anatomically, vastus lateralis has the largest physiological cross-sectional area (PCSA) in the quadriceps group, making it the primary contributor to eccentric knee extension torque during impact.

### Question 4: ACL Injury Risk Implications
* **Question:** Which landing posture creates greater risk for Anterior Cruciate Ligament (ACL) strain?
* **Answer:** The upright landing posture poses a substantially higher risk for ACL tears. Landing with shallow knee flexion (< 60°) causes the patellar tendon to insert onto the tibial tuberosity at an acute angle, directing a substantial portion of the quadriceps force anteriorly. With upright peak quadriceps forces exceeding 7,870 N, this generates large anterior tibial shear force, the primary mechanism of non-contact ACL rupture. Coaching athletes to land with deep knee flexion and forward trunk lean reduces patellar tendon shear and protects the ACL.

### Question 5: Energy Dissipation Strategy (The Posterior Chain)
* **Question:** In forward-lean landing, knee extensor demand is reduced. What muscle groups absorb the remaining energy?
* **Answer:** Forward trunk flexion shifts the body center of mass forward, moving the ground reaction force vector closer to the knee joint center (reducing the external knee flexion moment arm) and farther from the hip joint center (increasing the external hip flexion moment arm). Consequently, mechanical energy dissipation is transferred from the anterior knee extensors to the powerful posterior chain hip extensors—the gluteus maximus and hamstrings—which safely absorb impact energy without loading the patellar tendon or ACL.

---

## 6. Repository Layout

```
jump-landing-opensim/
├── index.html                           # Interactive public web dashboard
├── app.js                               # Plotly.js chart rendering logic
├── JumpLanding_OpenSim_Analysis.ipynb   # Standalone Google Colab notebook
├── README.md                            # Complete lab and pipeline guide
├── LICENSE                              # MIT License
├── data/
│   ├── JumpLanding_OpenCap_OpenSimData_EGM.zip  # Example session dataset (1.39 MB)
│   ├── JumpLanding_Posture_Comparison.xlsx       # Multi-sheet Excel results
│   ├── JumpLanding_Posture_Comparison.csv        # Metrics summary table
│   ├── JumpLanding_Kinematic_Events_Summary.csv  # Kinematic timing table
│   └── precomputed_curves.json                  # 101-point curves for web app
├── python/
│   ├── step1_jump_landing_kinematics.py         # Automated single-cycle event detection
│   ├── step2_run_jump_kinetics.py               # Inverse kinetics & muscle forces
│   └── step3_compare_landing_postures.py        # Posture comparison & report generation
└── assets/
    ├── JumpLanding_Posture_Comparison_Overlay.png # 4-panel comparison figure
    ├── JumpLanding_KneeExtensors_Detailed.png     # Individual extensor profiles
    ├── KinematicsComparison_EGMexample.png        # Kinematic traces
    └── KineticsComparison_EGMexample.png          # Kinetics traces
```

---

## 7. Standalone Python Execution (Local Machine)

To run the pipeline locally without Google Colab:
```bash
# Clone the repository
git clone https://github.com/LTUebl/jump-landing-opensim.git
cd jump-landing-opensim

# Install requirements
pip install numpy pandas matplotlib scipy openpyxl

# Execute pipeline steps
python python/step1_jump_landing_kinematics.py
python python/step2_run_jump_kinetics.py
python python/step3_compare_landing_postures.py
```

---

## 8. License & Citation

Distributed under the MIT License. See [LICENSE](LICENSE) for details.  
Department of Biomedical Engineering, Lawrence Technological University.
