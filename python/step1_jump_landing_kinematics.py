"""
step1_jump_landing_kinematics.py
Streamlined Step 1 for single-cycle jump landings:
  - Scans OpenCapData session folder
  - Reads .mot files for all landing conditions (e.g. LeaningJump, UprightJump)
  - Automatically identifies single-cycle jump events:
      * Apex of jump (maximum vertical height)
      * Initial contact (IC)
      * Maximum knee flexion (KM)
  - Generates labeled time-series kinematic plots
  - Saves event timing table for downstream kinetics/muscle force analysis

Usage:
  python step1_jump_landing_kinematics.py [--session_dir <path>] [--out_dir <path>]
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Default path points to JumpLandingOpenCapExampleData_EGM
DEFAULT_SESSION_DIR = r"C:\Users\emeyer\Documents\Work\Teaching\OtherClasses\BiomechMovement\F2026\JumpLandingOpenCapExampleData_EGM\OpenCapData_aacdc355-04b6-4d74-97e8-0dcd8d28a628"

def find_kinematics_dir(session_dir):
    candidates = [
        os.path.join(session_dir, "OpenSimData", "Kinematics"),
        os.path.join(session_dir, "Kinematics")
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    # scan subdirectories
    for root, dirs, files in os.walk(session_dir):
        if os.path.basename(root) == "Kinematics" and any(f.endswith(".mot") for f in files):
            return root
    raise FileNotFoundError(f"Could not locate Kinematics directory inside {session_dir}")

def read_mot(file_path):
    with open(file_path, "r") as f:
        for idx, line in enumerate(f):
            if line.strip().lower() == "endheader":
                df = pd.read_csv(file_path, sep=r"\s+", skiprows=idx + 1)
                df.columns = [c.strip() for c in df.columns]
                return df
    raise ValueError(f"Could not parse .mot file: {file_path}")

def detect_landing_events(df):
    """
    Detects single-cycle jump landing events:
      1. Apex: Maximum vertical pelvis height (pelvis_ty)
      2. Initial Contact (IC): First ground contact after apex, identified
         where knee flexion or ankle dorsiflexion begins rapid landing increase,
         or where vertical pelvis deceleration begins.
      3. Maximum Knee Flexion (KM): Peak knee angle during landing absorption.
    """
    time = df["time"].values
    pelvis_y = df["pelvis_ty"].values if "pelvis_ty" in df.columns else None
    knee_r = df["knee_angle_r"].values if "knee_angle_r" in df.columns else None
    knee_l = df["knee_angle_l"].values if "knee_angle_l" in df.columns else None
    ankle_r = df["ankle_angle_r"].values if "ankle_angle_r" in df.columns else None

    # Use average knee angle or right knee
    knee = knee_r if knee_r is not None else knee_l

    # 1. Apex
    if pelvis_y is not None:
        apex_idx = int(np.argmax(pelvis_y))
    else:
        # Fallback: minimum knee flexion during flight
        apex_idx = int(np.argmin(knee[len(knee)//4 : 3*len(knee)//4])) + len(knee)//4

    t_apex = time[apex_idx]

    # 2. Maximum Knee Flexion (KM) after apex
    post_apex_mask = np.arange(len(time)) >= apex_idx
    post_indices = np.where(post_apex_mask)[0]
    
    # Peak knee flexion in post-apex window
    km_local_idx = np.argmax(knee[post_indices])
    km_idx = post_indices[km_local_idx]
    t_km = time[km_idx]

    # 3. Initial Contact (IC) between Apex and KM
    # During flight, knees are extended. At IC, knees start rapidly flexing.
    between_indices = np.where((time >= t_apex) & (time <= t_km))[0]
    if len(between_indices) > 3:
        knee_between = knee[between_indices]
        # find where knee flexion exceeds 10 degrees or 15% of range
        thresh = knee_between[0] + 0.15 * (knee[km_idx] - knee_between[0])
        cross_idx = np.where(knee_between >= thresh)[0]
        if len(cross_idx) > 0:
            # step back 2 frames for exact contact initiation
            ic_idx = between_indices[max(0, cross_idx[0] - 2)]
        else:
            ic_idx = between_indices[len(between_indices)//2]
    else:
        ic_idx = apex_idx + (km_idx - apex_idx) // 2

    t_ic = time[ic_idx]

    return {
        "t_apex": t_apex,
        "t_ic": t_ic,
        "t_km": t_km,
        "apex_idx": apex_idx,
        "ic_idx": ic_idx,
        "km_idx": km_idx,
        "knee_max_deg": knee[km_idx],
        "absorption_duration": t_km - t_ic
    }

def plot_single_cycle_kinematics(df, trial_name, events, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    time = df["time"].values
    t_apex = events["t_apex"]
    t_ic = events["t_ic"]
    t_km = events["t_km"]

    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle(f"Jump Landing Kinematics: {trial_name} (Single-Cycle Analysis)", fontsize=14, fontweight="bold")

    # 1. Pelvis Vertical Position
    if "pelvis_ty" in df.columns:
        axs[0].plot(time, df["pelvis_ty"], color="#1f77b4", lw=2, label="Pelvis Vertical Position (m)")
        axs[0].axvline(t_apex, color="orange", linestyle="--", label=f"Apex ({t_apex:.2f}s)")
        axs[0].set_ylabel("Pelvis Y (m)", fontsize=11, fontweight="bold")
        axs[0].grid(True, linestyle=":", alpha=0.6)
        axs[0].legend(loc="upper right")

    # 2. Knee Angle
    if "knee_angle_r" in df.columns:
        axs[1].plot(time, df["knee_angle_r"], color="#d62728", lw=2, label="Knee Flexion Right (deg)")
    if "knee_angle_l" in df.columns:
        axs[1].plot(time, df["knee_angle_l"], color="#ff7f0e", lw=1.5, linestyle="--", label="Knee Flexion Left (deg)")
    axs[1].axvline(t_ic, color="green", linestyle="--", label=f"IC ({t_ic:.2f}s)")
    axs[1].axvline(t_km, color="purple", linestyle="--", label=f"KM ({t_km:.2f}s, {events['knee_max_deg']:.1f}°)")
    axs[1].axvspan(t_ic, t_km, color="green", alpha=0.15, label="Absorption Phase")
    axs[1].set_ylabel("Knee Angle (°)", fontsize=11, fontweight="bold")
    axs[1].grid(True, linestyle=":", alpha=0.6)
    axs[1].legend(loc="upper right")

    # 3. Trunk Posture (Lumbar Extension) & Ankle Angle
    if "lumbar_extension" in df.columns:
        axs[2].plot(time, df["lumbar_extension"], color="#2ca02c", lw=2, label="Lumbar Extension (deg; negative=flexion/lean)")
    if "ankle_angle_r" in df.columns:
        axs[2].plot(time, df["ankle_angle_r"], color="#7f7f7f", lw=1.5, linestyle=":", label="Ankle Dorsiflexion Right (deg)")
    axs[2].axvline(t_ic, color="green", linestyle="--")
    axs[2].axvline(t_km, color="purple", linestyle="--")
    axs[2].axvspan(t_ic, t_km, color="green", alpha=0.15)
    axs[2].set_ylabel("Angle (°)", fontsize=11, fontweight="bold")
    axs[2].set_xlabel("Time (s)", fontsize=11, fontweight="bold")
    axs[2].grid(True, linestyle=":", alpha=0.6)
    axs[2].legend(loc="upper right")

    plt.tight_layout()
    out_path = os.path.join(out_dir, f"{trial_name}_Kinematics_Labeled.png")
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved kinematic plot: {out_path}")

def run_analysis(session_dir=DEFAULT_SESSION_DIR, out_dir=None):
    if out_dir is None:
        out_dir = os.path.join(session_dir, "Analysis", "Kinematics")
    os.makedirs(out_dir, exist_ok=True)

    kin_dir = find_kinematics_dir(session_dir)
    mot_files = [f for f in os.listdir(kin_dir) if f.endswith(".mot") and not f.lower().startswith("neutral")]

    if not mot_files:
        print(f"No .mot files found in {kin_dir}")
        return

    print(f"Analyzing {len(mot_files)} trials from: {kin_dir}")
    summary_rows = []

    for f in sorted(mot_files):
        trial_name = os.path.splitext(f)[0]
        file_path = os.path.join(kin_dir, f)
        df = read_mot(file_path)

        events = detect_landing_events(df)
        plot_single_cycle_kinematics(df, trial_name, events, out_dir)

        # Trunk flexion at KM
        lumbar_km = df.loc[events["km_idx"], "lumbar_extension"] if "lumbar_extension" in df.columns else np.nan

        summary_rows.append({
            "Trial": trial_name,
            "Apex Time (s)": round(events["t_apex"], 3),
            "Initial Contact (IC) Time (s)": round(events["t_ic"], 3),
            "Knee Max (KM) Time (s)": round(events["t_km"], 3),
            "Absorption Duration (s)": round(events["absorption_duration"], 3),
            "Peak Knee Flexion (deg)": round(events["knee_max_deg"], 1),
            "Lumbar Angle at KM (deg)": round(lumbar_km, 1),
            "Posture Classification": "Forward Lean" if lumbar_km < -20 else "Upright"
        })

    df_summary = pd.DataFrame(summary_rows)
    summary_csv = os.path.join(out_dir, "JumpLanding_Kinematic_Events_Summary.csv")
    df_summary.to_csv(summary_csv, index=False)
    print("\n=== Jump Landing Kinematic Events Summary ===")
    print(df_summary.to_string(index=False))
    print(f"\nSummary table saved to: {summary_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze single-cycle jump landing kinematics.")
    parser.add_argument("--session_dir", default=DEFAULT_SESSION_DIR, help="Path to OpenCapData session folder")
    parser.add_argument("--out_dir", default=None, help="Output directory")
    args = parser.parse_args()
    run_analysis(args.session_dir, args.out_dir)
