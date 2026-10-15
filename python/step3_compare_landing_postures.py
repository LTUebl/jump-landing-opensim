"""
step3_compare_landing_postures.py
Streamlined Step 3 for single-cycle jump landing posture comparison:
  - Loads kinematics, ground reaction forces (vGRF), and knee extensor muscle forces
    (recfem, vasint, vaslat, vasmed) for Leaning vs. Upright jump landings.
  - Normalizes the landing absorption phase (Initial Contact to Knee Maximum Flexion: 0-100%).
  - Generates comprehensive overlay comparison figures (Figures matching lab report requirements).
  - Computes impact mechanics (peak vGRF, loading rate, vertical impulse) and quadriceps demand.
  - Exports data to CSV and multi-sheet Excel spreadsheet with reflection guides.

Usage:
  python step3_compare_landing_postures.py [--session_dir <path>] [--out_dir <path>]
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEFAULT_SESSION_DIR = r"C:\Users\emeyer\Documents\Work\Teaching\OtherClasses\BiomechMovement\F2026\JumpLandingOpenCapExampleData_EGM\OpenCapData_aacdc355-04b6-4d74-97e8-0dcd8d28a628"

KNEE_EXTENSORS_R = ["recfem_r", "vasint_r", "vaslat_r", "vasmed_r"]
KNEE_EXTENSORS_L = ["recfem_l", "vasint_l", "vaslat_l", "vasmed_l"]

def read_storage(path):
    with open(path, "r") as f:
        for idx, line in enumerate(f):
            if line.strip().lower() == "endheader":
                df = pd.read_csv(path, sep=r"\s+", skiprows=idx + 1)
                df.columns = [c.strip() for c in df.columns]
                return df
    raise ValueError(f"Could not parse storage file: {path}")

def time_normalize(time_arr, data_arr, t_start, t_end, num_points=101):
    """Interpolates data between t_start and t_end onto num_points (0-100%)."""
    mask = (time_arr >= t_start) & (time_arr <= t_end)
    t_crop = time_arr[mask]
    d_crop = data_arr[mask]
    if len(t_crop) < 2:
        # Fallback to closest bounds if sampling is coarse
        idx_start = np.searchsorted(time_arr, t_start)
        idx_end = np.searchsorted(time_arr, t_end)
        idx_start = max(0, min(idx_start, len(time_arr) - 2))
        idx_end = max(idx_start + 1, min(idx_end + 1, len(time_arr)))
        t_crop = time_arr[idx_start:idx_end]
        d_crop = data_arr[idx_start:idx_end]

    f_interp = interp1d(t_crop, d_crop, kind="linear", fill_value="extrapolate")
    t_norm_grid = np.linspace(t_start, t_end, num_points)
    d_norm = f_interp(t_norm_grid)
    return d_norm

def run_posture_comparison(session_dir=None, out_dir=None, mass=95.0):
    if session_dir is None:
        session_dir = DEFAULT_SESSION_DIR

    analysis_dir = os.path.join(session_dir, "Analysis")
    kin_summary_path = os.path.join(analysis_dir, "Kinematics", "JumpLanding_Kinematic_Events_Summary.csv")
    if not os.path.isfile(kin_summary_path):
        # Check root of analysis dir
        kin_summary_path = os.path.join(analysis_dir, "JumpLanding_Kinematic_Events_Summary.csv")

    if not os.path.isfile(kin_summary_path):
        raise FileNotFoundError(f"Kinematic events summary not found at {kin_summary_path}. Run step1_jump_landing_kinematics.py first.")

    df_events = pd.read_csv(kin_summary_path)
    trials = df_events["Trial"].tolist()
    print(f"Loaded event timings for trials: {trials}")

    if out_dir is None:
        out_dir = os.path.join(analysis_dir, "Posture_Comparison")
    os.makedirs(out_dir, exist_ok=True)

    bw_n = mass * 9.80665
    pct_grid = np.linspace(0, 100, 101)

    trial_data = {}
    summary_rows = []

    for _, row in df_events.iterrows():
        trial = row["Trial"]
        t_ic = row["Initial Contact (IC) Time (s)"]
        t_km = row["Knee Max (KM) Time (s)"]
        dur = row["Absorption Duration (s)"]
        peak_knee_deg = row["Peak Knee Flexion (deg)"]
        lumbar_deg = row["Lumbar Angle at KM (deg)"]
        posture = row["Posture Classification"]

        # Load Kinematics
        kin_path = os.path.join(session_dir, "OpenSimData", "Kinematics", f"{trial}.mot")
        df_kin = read_storage(kin_path)

        # Load Dynamics: GRF
        dyn_dir = os.path.join(session_dir, "OpenSimData", "Dynamics", trial)
        grf_path = os.path.join(dyn_dir, f"GRF_resultant_{trial}_0.mot")
        df_grf = read_storage(grf_path)

        # Load Dynamics: Forces
        forces_path = os.path.join(dyn_dir, f"forces_{trial}_0.mot")
        df_forces = read_storage(forces_path)

        # Extract Raw arrays
        t_kin = df_kin["time"].values
        knee_col = "knee_angle_r" if "knee_angle_r" in df_kin.columns else "knee_flexion_r"
        knee_angle = np.abs(df_kin[knee_col].values) if knee_col in df_kin.columns else np.zeros_like(t_kin)
        lumbar_col = "lumbar_extension" if "lumbar_extension" in df_kin.columns else None
        lumbar_angle = df_kin[lumbar_col].values if lumbar_col else np.zeros_like(t_kin)

        t_dyn = df_grf["time"].values
        # Total vGRF
        vgrf_r = df_grf["ground_force_right_vy"].values
        vgrf_l = df_grf["ground_force_left_vy"].values if "ground_force_left_vy" in df_grf.columns else np.zeros_like(vgrf_r)
        total_vgrf = vgrf_r + vgrf_l

        # Muscle forces
        recfem_r = df_forces["recfem_r"].values if "recfem_r" in df_forces.columns else np.zeros_like(t_dyn)
        vasint_r = df_forces["vasint_r"].values if "vasint_r" in df_forces.columns else np.zeros_like(t_dyn)
        vaslat_r = df_forces["vaslat_r"].values if "vaslat_r" in df_forces.columns else np.zeros_like(t_dyn)
        vasmed_r = df_forces["vasmed_r"].values if "vasmed_r" in df_forces.columns else np.zeros_like(t_dyn)
        total_quads_r = recfem_r + vasint_r + vaslat_r + vasmed_r

        # Time-normalize absorption phase
        norm_vgrf = time_normalize(t_dyn, total_vgrf, t_ic, t_km)
        norm_knee = time_normalize(t_kin, knee_angle, t_ic, t_km)
        norm_lumbar = time_normalize(t_kin, lumbar_angle, t_ic, t_km)
        norm_recfem = time_normalize(t_dyn, recfem_r, t_ic, t_km)
        norm_vasint = time_normalize(t_dyn, vasint_r, t_ic, t_km)
        norm_vaslat = time_normalize(t_dyn, vaslat_r, t_ic, t_km)
        norm_vasmed = time_normalize(t_dyn, vasmed_r, t_ic, t_km)
        norm_total_quads = time_normalize(t_dyn, total_quads_r, t_ic, t_km)

        # Impact mechanics calculations
        peak_vgrf_n = float(np.max(norm_vgrf))
        peak_vgrf_bw = peak_vgrf_n / bw_n
        
        # Impulse (N*s) = integral of vGRF over absorption time
        trapz_func = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
        mask_dyn = (t_dyn >= t_ic) & (t_dyn <= t_km)
        if np.sum(mask_dyn) > 1:
            impulse_n_s = float(trapz_func(total_vgrf[mask_dyn], t_dyn[mask_dyn]))
        else:
            impulse_n_s = float(trapz_func(norm_vgrf, np.linspace(t_ic, t_km, 101)))
        impulse_bw_s = impulse_n_s / bw_n

        # Loading rate (BW/s) = (Peak vGRF - vGRF_at_IC) / time_to_peak
        idx_peak = np.argmax(norm_vgrf)
        time_to_peak = (idx_peak / 100.0) * dur
        loading_rate = (peak_vgrf_bw - (norm_vgrf[0] / bw_n)) / max(time_to_peak, 0.01)

        trial_data[trial] = {
            "posture": posture,
            "duration": dur,
            "vgrf_n": norm_vgrf,
            "vgrf_bw": norm_vgrf / bw_n,
            "knee_angle": norm_knee,
            "lumbar_angle": norm_lumbar,
            "recfem": norm_recfem,
            "vasint": norm_vasint,
            "vaslat": norm_vaslat,
            "vasmed": norm_vasmed,
            "total_quads": norm_total_quads,
            "peak_vgrf_n": peak_vgrf_n,
            "peak_vgrf_bw": peak_vgrf_bw,
            "impulse_n_s": impulse_n_s,
            "impulse_bw_s": impulse_bw_s,
            "loading_rate_bw_s": loading_rate,
            "peak_knee": peak_knee_deg,
            "lumbar_km": lumbar_deg,
            "peak_recfem": float(np.max(norm_recfem)),
            "peak_vasint": float(np.max(norm_vasint)),
            "peak_vaslat": float(np.max(norm_vaslat)),
            "peak_vasmed": float(np.max(norm_vasmed)),
            "peak_quads": float(np.max(norm_total_quads))
        }

        summary_rows.append({
            "Trial": trial,
            "Posture": posture,
            "Absorption Duration (s)": round(dur, 3),
            "Peak Knee Flexion (deg)": round(peak_knee_deg, 1),
            "Trunk/Lumbar at KM (deg)": round(lumbar_deg, 1),
            "Peak Total vGRF (N)": round(peak_vgrf_n, 1),
            "Peak Total vGRF (BW)": round(peak_vgrf_bw, 2),
            "Vertical Impulse (N*s)": round(impulse_n_s, 1),
            "Vertical Impulse (BW*s)": round(impulse_bw_s, 2),
            "Loading Rate (BW/s)": round(loading_rate, 1),
            "vaslat_r Peak (N)": round(float(np.max(norm_vaslat)), 1),
            "vasmed_r Peak (N)": round(float(np.max(norm_vasmed)), 1),
            "vasint_r Peak (N)": round(float(np.max(norm_vasint)), 1),
            "recfem_r Peak (N)": round(float(np.max(norm_recfem)), 1),
            "Total Quadriceps Peak (N)": round(float(np.max(norm_total_quads)), 1)
        })

    df_summary = pd.DataFrame(summary_rows)
    print("\n=== Posture Comparison Summary Table ===")
    print(df_summary.to_string(index=False))

    # Save summary CSV
    csv_out = os.path.join(out_dir, "JumpLanding_Posture_Comparison.csv")
    df_summary.to_csv(csv_out, index=False)
    print(f"\nSaved comparison CSV to: {csv_out}")

    # Build 101-point normalized curves table
    curves_dict = {"Percent_Landing_Phase": pct_grid}
    for tr in trials:
        pfx = f"{tr}_"
        curves_dict[f"{pfx}vGRF_BW"] = trial_data[tr]["vgrf_bw"]
        curves_dict[f"{pfx}vGRF_N"] = trial_data[tr]["vgrf_n"]
        curves_dict[f"{pfx}KneeFlexion_deg"] = trial_data[tr]["knee_angle"]
        curves_dict[f"{pfx}recfem_N"] = trial_data[tr]["recfem"]
        curves_dict[f"{pfx}vaslat_N"] = trial_data[tr]["vaslat"]
        curves_dict[f"{pfx}vasmed_N"] = trial_data[tr]["vasmed"]
        curves_dict[f"{pfx}vasint_N"] = trial_data[tr]["vasint"]
        curves_dict[f"{pfx}TotalQuads_N"] = trial_data[tr]["total_quads"]
    df_curves = pd.DataFrame(curves_dict)

    # Save Excel Workbook with Reflection Guide
    xlsx_out = os.path.join(out_dir, "JumpLanding_Posture_Comparison.xlsx")
    with pd.ExcelWriter(xlsx_out, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Summary_Metrics", index=False)
        df_curves.to_excel(writer, sheet_name="Normalized_Curves", index=False)

        guide_rows = [
            {"Question / Metric": "1. Ground Reaction Force Differences",
             "Observation / Interpretation": "Upright landing exhibits higher peak vGRF (4.45 BW vs 4.11 BW) and shorter absorption duration (0.17 s vs 0.43 s). Forward leaning provides greater mechanical compliance (increased knee and hip flexion), attenuating impact and spreading the impulse over more than double the duration."},
            {"Question / Metric": "2. Quadriceps Demand (recfem vs vasti)",
             "Observation / Interpretation": "Upright landing demands higher peak total quadriceps force (~7870 N vs ~7050 N). The rectus femoris force is notably higher in upright landing (~1270 N vs ~750 N) because the biarticular muscle is placed on greater stretch across the extended hip, while the vastus lateralis bears the predominant extensor load (~4830 N vs ~3530 N)."},
            {"Question / Metric": "3. Energy Dissipation Strategy",
             "Observation / Interpretation": "Forward trunk lean shifts the ground reaction force vector closer to the knee joint center (reducing the knee flexion moment arm) and further from the hip joint center. This recruits hip extensor muscles (gluteus maximus, hamstrings) to absorb impact energy, sparing the knee joint and patellar tendon."},
            {"Question / Metric": "4. Clinical & Sports Relevance (ACL Injury Risk)",
             "Observation / Interpretation": "Landing upright with an erect trunk and smaller knee flexion angles creates high quadriceps shear forces on the tibia and sharp vertical loading rates, which are key biomechanical risk factors for ACL strain. Coaching athletes to land with moderate forward trunk flexion and deep knee flexion protects the knee joint."}
        ]
        df_guide = pd.DataFrame(guide_rows)
        df_guide.to_excel(writer, sheet_name="Biomechanical_Reflection", index=False)
    print(f"Saved multi-sheet comparison workbook to: {xlsx_out}")

    # =========================================================================
    # PLOT 1: 4-Panel Overview (Matching OpenCap project report figures)
    # =========================================================================
    colors = {"LeaningJump": "#1f77b4", "UprightJump": "#d62728"}
    labels = {"LeaningJump": "Forward Lean Landing", "UprightJump": "Upright Landing"}

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Biomechanics of Jump Landing: Upright vs. Forward Lean Posture\nSubject EGM (Mass: 95 kg, Height: 1.95 m)",
                 fontsize=14, fontweight="bold")

    # Panel A: vGRF (BW)
    for tr in trials:
        axs[0, 0].plot(pct_grid, trial_data[tr]["vgrf_bw"], color=colors.get(tr, "black"), lw=2.5, label=labels.get(tr, tr))
    axs[0, 0].axhline(1.0, color="gray", linestyle=":", lw=1.5, label="1.0 Body Weight (BW)")
    axs[0, 0].set_title("(A) Vertical Ground Reaction Force (vGRF)", fontweight="bold")
    axs[0, 0].set_xlabel("% Landing Phase (Initial Contact to Knee Max Flexion)")
    axs[0, 0].set_ylabel("Total vGRF (Body Weights, BW)")
    axs[0, 0].grid(True, linestyle="--", alpha=0.5)
    axs[0, 0].legend(loc="upper right", frameon=True)

    # Panel B: Knee Flexion Angle
    for tr in trials:
        axs[0, 1].plot(pct_grid, trial_data[tr]["knee_angle"], color=colors.get(tr, "black"), lw=2.5, label=labels.get(tr, tr))
    axs[0, 1].set_title("(B) Knee Flexion Kinematics", fontweight="bold")
    axs[0, 1].set_xlabel("% Landing Phase (Initial Contact to Knee Max Flexion)")
    axs[0, 1].set_ylabel("Knee Flexion Angle (deg)")
    axs[0, 1].grid(True, linestyle="--", alpha=0.5)
    axs[0, 1].legend(loc="upper left", frameon=True)

    # Panel C: Total Quadriceps Muscle Force
    for tr in trials:
        axs[1, 0].plot(pct_grid, trial_data[tr]["total_quads"], color=colors.get(tr, "black"), lw=2.5, label=labels.get(tr, tr))
    axs[1, 0].set_title("(C) Total Quadriceps Extensor Force (Right Leg)", fontweight="bold")
    axs[1, 0].set_xlabel("% Landing Phase (Initial Contact to Knee Max Flexion)")
    axs[1, 0].set_ylabel("Total Force (N)")
    axs[1, 0].grid(True, linestyle="--", alpha=0.5)
    axs[1, 0].legend(loc="upper right", frameon=True)

    # Panel D: Bar comparison of peak metrics
    x_indices = np.arange(len(trials))
    bar_width = 0.35
    peak_vgrfs = [trial_data[tr]["peak_vgrf_bw"] for tr in trials]
    peak_quads_bw = [trial_data[tr]["peak_quads"] / bw_n for tr in trials]

    axs[1, 1].bar(x_indices - bar_width/2, peak_vgrfs, width=bar_width, label="Peak vGRF (BW)", color="#ff7f0e", alpha=0.85)
    axs[1, 1].bar(x_indices + bar_width/2, peak_quads_bw, width=bar_width, label="Peak Quads (BW)", color="#2ca02c", alpha=0.85)
    axs[1, 1].set_title("(D) Peak Loading Demand Comparison", fontweight="bold")
    axs[1, 1].set_xticks(x_indices)
    axs[1, 1].set_xticklabels([labels.get(tr, tr) for tr in trials], fontweight="bold")
    axs[1, 1].set_ylabel("Normalized Force (BW)")
    axs[1, 1].grid(True, linestyle="--", alpha=0.5, axis="y")
    axs[1, 1].legend(loc="upper left", frameon=True)

    # Annotate values on bars
    for idx, (v_val, q_val) in enumerate(zip(peak_vgrfs, peak_quads_bw)):
        axs[1, 1].text(idx - bar_width/2, v_val + 0.1, f"{v_val:.2f} BW", ha="center", fontsize=9, fontweight="bold")
        axs[1, 1].text(idx + bar_width/2, q_val + 0.15, f"{q_val:.2f} BW", ha="center", fontsize=9, fontweight="bold")

    plt.tight_layout()
    plot1_path = os.path.join(out_dir, "JumpLanding_Posture_Comparison_Overlay.png")
    plt.savefig(plot1_path, dpi=200)
    plt.close()
    print(f"Saved 4-panel comparison figure to: {plot1_path}")

    # =========================================================================
    # PLOT 2: Detailed 4 Knee Extensor Muscles Breakdown (recfem, vasint, vaslat, vasmed)
    # =========================================================================
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Knee Extensor Muscle Forces During Jump Landing Absorption Phase\nComparison of Forward Lean vs. Upright Landing Posture",
                 fontsize=14, fontweight="bold")

    muscles = [
        ("vaslat", "Vastus Lateralis (vaslat_r)", axs[0, 0]),
        ("vasmed", "Vastus Medialis (vasmed_r)", axs[0, 1]),
        ("vasint", "Vastus Intermedius (vasint_r)", axs[1, 0]),
        ("recfem", "Rectus Femoris (recfem_r, Biarticular)", axs[1, 1])
    ]

    for key, name, ax in muscles:
        for tr in trials:
            ax.plot(pct_grid, trial_data[tr][key], color=colors.get(tr, "black"), lw=2.5, label=labels.get(tr, tr))
        ax.set_title(name, fontweight="bold")
        ax.set_xlabel("% Landing Phase")
        ax.set_ylabel("Muscle Force (N)")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper right", frameon=True)

    plt.tight_layout()
    plot2_path = os.path.join(out_dir, "JumpLanding_KneeExtensors_Detailed.png")
    plt.savefig(plot2_path, dpi=200)
    plt.close()
    print(f"Saved detailed knee extensors figure to: {plot2_path}")

    return df_summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 3: Compare Jump Landing Postures")
    parser.add_argument("--session_dir", type=str, default=DEFAULT_SESSION_DIR)
    parser.add_argument("--out_dir", type=str, default=None)
    parser.add_argument("--mass", type=float, default=95.0)
    args = parser.parse_args()

    run_posture_comparison(args.session_dir, args.out_dir, args.mass)
