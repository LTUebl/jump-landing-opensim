"""
step2_run_jump_kinetics.py
Streamlined Step 2 for single-cycle jump landings:
  - Takes identified landing windows from Step 1 (or user-specified time interval)
  - Evaluates Inverse Kinetics (Ground Reaction Forces, focusing on vertical GRF)
  - Evaluates muscle forces with focus on knee extensor muscles:
      * recfem (rectus femoris)
      * vasint (vastus intermedius)
      * vaslat (vastus lateralis)
      * vasmed (vastus medialis)
  - Supports both OpenSim BodyKinematics/Static Optimization and OpenSimAD simulation files.
  - Exports extracted landing phase kinetics and muscle forces to CSV and summary tables.

Usage:
  python step2_run_jump_kinetics.py [--session_dir <path>] [--out_dir <path>]
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEFAULT_SESSION_DIR = r"C:\Users\emeyer\Documents\Work\Teaching\OtherClasses\BiomechMovement\F2026\JumpLandingOpenCapExampleData_EGM\OpenCapData_aacdc355-04b6-4d74-97e8-0dcd8d28a628"

KNEE_EXTENSORS_R = ["recfem_r", "vasint_r", "vaslat_r", "vasmed_r"]
KNEE_EXTENSORS_L = ["recfem_l", "vasint_l", "vaslat_l", "vasmed_l"]
ALL_KNEE_EXTENSORS = KNEE_EXTENSORS_R + KNEE_EXTENSORS_L

def read_storage(path):
    with open(path, "r") as f:
        for idx, line in enumerate(f):
            if line.strip().lower() == "endheader":
                df = pd.read_csv(path, sep=r"\s+", skiprows=idx + 1)
                df.columns = [c.strip() for c in df.columns]
                return df
    raise ValueError(f"Could not parse storage file: {path}")

def load_or_compute_kinetics(session_dir, trial_name):
    """
    Loads dynamics results (GRF and muscle forces) for a given trial.
    Checks OpenSimData/Dynamics/{trial_name}/ for:
      - GRF_resultant_{trial_name}_0.mot (or GRF.mot)
      - forces_{trial_name}_0.mot (or muscle_forces.sto)
      - kinetics_{trial_name}_0.mot
    """
    dyn_dir = os.path.join(session_dir, "OpenSimData", "Dynamics", trial_name)
    if not os.path.isdir(dyn_dir):
        raise FileNotFoundError(f"Dynamics folder not found for {trial_name}: {dyn_dir}")

    # 1. GRF
    grf_file = None
    for candidate in [f"GRF_resultant_{trial_name}_0.mot", f"GRF_{trial_name}_0.mot", "GRF.mot", "GRF.sto"]:
        p = os.path.join(dyn_dir, candidate)
        if os.path.isfile(p):
            grf_file = p
            break
    if grf_file is None:
        raise FileNotFoundError(f"No GRF file found in {dyn_dir}")
    df_grf = read_storage(grf_file)

    # 2. Muscle Forces
    forces_file = None
    for candidate in [f"forces_{trial_name}_0.mot", "muscle_forces.sto", "forces.mot"]:
        p = os.path.join(dyn_dir, candidate)
        if os.path.isfile(p):
            forces_file = p
            break
    if forces_file is None:
        raise FileNotFoundError(f"No muscle forces file found in {dyn_dir}")
    df_forces = read_storage(forces_file)

    # 3. Kinetics / Joint Moments
    kinetics_file = None
    for candidate in [f"kinetics_{trial_name}_0.mot", "joint_moments.sto", "kinetics.mot"]:
        p = os.path.join(dyn_dir, candidate)
        if os.path.isfile(p):
            kinetics_file = p
            break
    df_kinetics = read_storage(kinetics_file) if kinetics_file else None

    return df_grf, df_forces, df_kinetics

def plot_trial_landing_results(df_grf, df_forces, trial_name, out_dir, mass=95.0):
    os.makedirs(out_dir, exist_ok=True)
    time = df_grf["time"].values
    bw = mass * 9.80665

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"Landing Phase Kinetics & Muscle Forces: {trial_name}", fontsize=14, fontweight="bold")

    # 1. Vertical Ground Reaction Forces (N)
    axs[0, 0].plot(time, df_grf["ground_force_right_vy"], color="blue", lw=2, label="Right vGRF")
    axs[0, 0].plot(time, df_grf["ground_force_left_vy"], color="red", lw=2, label="Left vGRF")
    total_vgrf = df_grf["ground_force_right_vy"] + df_grf["ground_force_left_vy"]
    axs[0, 0].plot(time, total_vgrf, color="black", lw=2.5, linestyle="--", label="Total vGRF")
    axs[0, 0].axhline(bw, color="gray", linestyle=":", label="1 Body Weight (BW)")
    axs[0, 0].set_ylabel("Vertical GRF (N)", fontsize=11, fontweight="bold")
    axs[0, 0].set_title("Ground Reaction Forces (Inverse Kinetics)", fontsize=12, fontweight="bold")
    axs[0, 0].grid(True, linestyle=":", alpha=0.6)
    axs[0, 0].legend(loc="upper right")

    # 2. Vertical GRF in Body Weights (BW)
    axs[0, 1].plot(time, total_vgrf / bw, color="black", lw=2.5, label="Total vGRF (BW)")
    axs[0, 1].plot(time, df_grf["ground_force_right_vy"] / bw, color="blue", lw=1.5, label="Right vGRF (BW)")
    axs[0, 1].plot(time, df_grf["ground_force_left_vy"] / bw, color="red", lw=1.5, label="Left vGRF (BW)")
    axs[0, 1].axhline(1.0, color="gray", linestyle=":")
    axs[0, 1].set_ylabel("Force (Body Weights)", fontsize=11, fontweight="bold")
    axs[0, 1].set_title(f"Normalized vGRF (Peak = {total_vgrf.max() / bw:.2f} BW)", fontsize=12, fontweight="bold")
    axs[0, 1].grid(True, linestyle=":", alpha=0.6)
    axs[0, 1].legend(loc="upper right")

    # 3. Knee Extensor Muscle Forces - Right Leg
    for m in KNEE_EXTENSORS_R:
        if m in df_forces.columns:
            axs[1, 0].plot(time, df_forces[m], lw=2, label=m.replace("_r", ""))
    total_quad_r = sum(df_forces[m] for m in KNEE_EXTENSORS_R if m in df_forces.columns)
    axs[1, 0].plot(time, total_quad_r, color="black", lw=2, linestyle="--", label="Total Quadriceps R")
    axs[1, 0].set_ylabel("Muscle Force (N)", fontsize=11, fontweight="bold")
    axs[1, 0].set_xlabel("Time (s)", fontsize=11, fontweight="bold")
    axs[1, 0].set_title("Right Knee Extensor Muscle Forces", fontsize=12, fontweight="bold")
    axs[1, 0].grid(True, linestyle=":", alpha=0.6)
    axs[1, 0].legend(loc="upper right")

    # 4. Knee Extensor Muscle Forces - Left Leg
    for m in KNEE_EXTENSORS_L:
        if m in df_forces.columns:
            axs[1, 1].plot(time, df_forces[m], lw=2, label=m.replace("_l", ""))
    total_quad_l = sum(df_forces[m] for m in KNEE_EXTENSORS_L if m in df_forces.columns)
    axs[1, 1].plot(time, total_quad_l, color="black", lw=2, linestyle="--", label="Total Quadriceps L")
    axs[1, 1].set_ylabel("Muscle Force (N)", fontsize=11, fontweight="bold")
    axs[1, 1].set_xlabel("Time (s)", fontsize=11, fontweight="bold")
    axs[1, 1].set_title("Left Knee Extensor Muscle Forces", fontsize=12, fontweight="bold")
    axs[1, 1].grid(True, linestyle=":", alpha=0.6)
    axs[1, 1].legend(loc="upper right")

    plt.tight_layout()
    out_path = os.path.join(out_dir, f"{trial_name}_Landing_Kinetics_Muscles.png")
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved kinetics/muscles plot: {out_path}")

def run_step2(session_dir=DEFAULT_SESSION_DIR, out_dir=None):
    if out_dir is None:
        out_dir = os.path.join(session_dir, "Analysis", "Dynamics")
    os.makedirs(out_dir, exist_ok=True)

    dyn_root = os.path.join(session_dir, "OpenSimData", "Dynamics")
    if not os.path.isdir(dyn_root):
        print(f"Dynamics folder does not exist: {dyn_root}")
        return

    trials = [d for d in os.listdir(dyn_root) if os.path.isdir(os.path.join(dyn_root, d))]
    print(f"Found {len(trials)} trials in Dynamics: {trials}")

    metrics_rows = []

    for trial in sorted(trials):
        df_grf, df_forces, df_kinetics = load_or_compute_kinetics(session_dir, trial)
        plot_trial_landing_results(df_grf, df_forces, trial, out_dir)

        time = df_grf["time"].values
        total_vgrf = df_grf["ground_force_right_vy"] + df_grf["ground_force_left_vy"]
        bw = 95.0 * 9.80665

        peak_vgrf_idx = np.argmax(total_vgrf)
        peak_vgrf_val = total_vgrf[peak_vgrf_idx]
        t_peak_vgrf = time[peak_vgrf_idx]

        row = {
            "Trial": trial,
            "Peak Total vGRF (N)": round(peak_vgrf_val, 1),
            "Peak Total vGRF (BW)": round(peak_vgrf_val / bw, 2),
            "Time to Peak vGRF (s)": round(t_peak_vgrf, 3),
            "Right Leg Peak vGRF (N)": round(df_grf["ground_force_right_vy"].max(), 1),
            "Left Leg Peak vGRF (N)": round(df_grf["ground_force_left_vy"].max(), 1),
        }

        # Knee extensor peaks
        for m in ALL_KNEE_EXTENSORS:
            if m in df_forces.columns:
                row[f"{m} Peak (N)"] = round(df_forces[m].max(), 1)

        total_quad_r = sum(df_forces[m] for m in KNEE_EXTENSORS_R if m in df_forces.columns)
        row["Total Quad R Peak (N)"] = round(total_quad_r.max(), 1)
        row["Total Quad R Peak (BW)"] = round(total_quad_r.max() / bw, 2)

        metrics_rows.append(row)

    df_metrics = pd.DataFrame(metrics_rows)
    out_csv = os.path.join(out_dir, "JumpLanding_Kinetics_Muscles_Summary.csv")
    df_metrics.to_csv(out_csv, index=False)
    print("\n=== Jump Landing Kinetics & Muscle Forces Summary ===")
    print(df_metrics[["Trial", "Peak Total vGRF (N)", "Peak Total vGRF (BW)", "vaslat_r Peak (N)", "vasmed_r Peak (N)", "recfem_r Peak (N)", "vasint_r Peak (N)"]].to_string(index=False))
    print(f"\nSaved metrics summary to: {out_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and evaluate single-cycle jump landing kinetics and muscle forces.")
    parser.add_argument("--session_dir", default=DEFAULT_SESSION_DIR, help="Path to OpenCapData session folder")
    parser.add_argument("--out_dir", default=None, help="Output directory")
    args = parser.parse_args()
    run_step2(args.session_dir, args.out_dir)
