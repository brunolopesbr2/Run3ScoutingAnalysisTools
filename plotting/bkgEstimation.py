from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")

# ABCD regions in (cosT, chi2):
#   A: cosT <= 0, chi2 >= 3  (fail both)
#   B: cosT <= 0, chi2 < 3   (pass chi2 only)
#   C: cosT > 0,  chi2 >= 3  (pass cosT only)
#   D: cosT > 0,  chi2 < 3   (signal region)
#
# Transfer factor: TF = B/A
# Prediction: D_pred = C * (B/A)

NTRACK_BINS = [3, 4, 5, 6, 7, 8, "9+"]
ABCD_REGIONS = ["A", "B", "C", "D"]
BLINDED_BINS = [7,8,"9+"]  # Bins where D region is blinded

def process_abcd_per_ntrack(args):
    rootFile, process = args
    print(f"Processing {rootFile}")

    # Initialize counts: {ntrk: {region: (sum_w, sum_w2)}}
    counts = {nt: {r: [0.0, 0.0] for r in ABCD_REGIONS} for nt in NTRACK_BINS}

    with uproot.open(rootFile) as file:
        tree = file["scoutingTree/objectTree"]
        branches = [
            "scoutVert_dBV", "scoutVert_dBVErr", "scoutVert_nTracks",
            "weight", "scoutVert_chi2", "scoutVert_cosT", "jet_pt", "l1HT"
        ]

        for batch in tree.iterate(branches, library="ak", step_size=100000):
            weights = ak.ones_like(batch["weight"])
            dBV = batch["scoutVert_dBV"]
            dBVErr = batch["scoutVert_dBVErr"]
            ntracks = batch["scoutVert_nTracks"]
            chi2 = batch["scoutVert_chi2"]
            cosT = batch["scoutVert_cosT"]
            ht = batch["l1HT"]
            #jet_pt = batch["jet_pt"]
            #njet = ak.num(jet_pt,axis=1)
            #jet_mask = (njet>3)
            #dBV = dBV[jet_mask]
            #dBVErr = dBVErr[jet_mask]
            #ntracks = ntracks[jet_mask]
            #chi2 = chi2[jet_mask]
            #cosT = cosT[jet_mask]
            # Baseline vertex selection
            vtx_mask = (dBV > 0.01) & (dBV < 2.0) & (ntracks > 2) & (dBVErr < 0.005) #& (ntracks < 8)
            dBV = dBV[vtx_mask]
            ntracks = ntracks[vtx_mask]
            chi2 = chi2[vtx_mask]
            cosT = cosT[vtx_mask]

            # Keep events with at least one vertex passing baseline
            evt_mask = (ak.num(dBV, axis=1) > 0) & (ht>600)
            weights = weights[evt_mask]
            ntracks = ntracks[evt_mask]
            chi2 = chi2[evt_mask]
            cosT = cosT[evt_mask]

            for nt in NTRACK_BINS:
                # Select vertices with exactly this track multiplicity
                # (or >= 8 for the inclusive bin)
                if nt == "9+":
                    nt_mask = ntracks >= 9
                else:
                    nt_mask = ntracks == nt

                nt_chi2 = chi2[nt_mask]
                nt_cosT = cosT[nt_mask]

                # ABCD masks (per vertex)
                pass_cosT = nt_cosT > 0
                pass_chi2 = nt_chi2 < 2.5

                region_masks = {
                    "A": ~pass_cosT & ~pass_chi2,
                    "B": ~pass_cosT & pass_chi2,
                    "C": pass_cosT & ~pass_chi2,
                    "D": pass_cosT & pass_chi2,
                }

                duplicateMask = ak.ones_like(weights, dtype=bool)
                for region in ["D","C","B","A"]:
                    rmask = region_masks[region]
                    # Event has at least one vertex in this region
                    evt_in_region = (ak.num(nt_cosT[rmask]) > 0) & duplicateMask
                    duplicateMask = duplicateMask & (~evt_in_region)
                    
                    # Skip filling observed D for blinded bins
                    if region == "D" and nt in BLINDED_BINS:
                        continue
                    
                    w = weights[evt_in_region]
                    counts[nt][region][0] += float(ak.sum(w))
                    counts[nt][region][1] += float(ak.sum(w**2))
                    
                    
    return process, counts

def merge_counts(all_counts):
    """Merge counts across files for the same process."""
    merged = {}
    for process, counts in all_counts:
        if process not in merged:
            merged[process] = {nt: {r: [0.0, 0.0] for r in ABCD_REGIONS} for nt in NTRACK_BINS}
        for nt in NTRACK_BINS:
            for r in ABCD_REGIONS:
                merged[process][nt][r][0] += counts[nt][r][0]
                merged[process][nt][r][1] += counts[nt][r][1]
    return merged

def compute_transfer_factors(counts):
    """Compute TF = B/A and its uncertainty for each ntrack bin."""
    ntracks = []
    tfs = []
    tf_errs = []
    region_yields = {r: ([], []) for r in ABCD_REGIONS}

    for nt in NTRACK_BINS:
        A, A2 = counts[nt]["A"]
        B, B2 = counts[nt]["B"]
        C, C2 = counts[nt]["C"]
        D, D2 = counts[nt]["D"]

        A_err = np.sqrt(A2)
        B_err = np.sqrt(B2)
        C_err = np.sqrt(C2)
        D_err = np.sqrt(D2)

        for r in ABCD_REGIONS:
            val, val2 = counts[nt][r]
            region_yields[r][0].append(val)
            region_yields[r][1].append(np.sqrt(val2))

        if A > 0 and B > 0:
            tf = B / A
            tf_err = tf * np.sqrt((A_err / A)**2 + (B_err / B)**2)
        elif A == 0:
            tf = 0
            tf_err = 0
        else:
            tf = 0
            tf_err = 0

        # Use numeric position for plotting
        nt_label = nt if isinstance(nt, int) else 9
        ntracks.append(nt_label)
        tfs.append(tf)
        tf_errs.append(tf_err)

        # Predicted vs observed
        if A > 0:
            D_pred = C * B / A
            D_pred_err = D_pred * np.sqrt(
                (A_err / A)**2 + (B_err / B)**2 + (C_err / C)**2
            ) if C > 0 else 0
        else:
            D_pred = 0
            D_pred_err = 0

        if nt in BLINDED_BINS:
            print(f"ntrk={nt}: A={A:.1f}+-{A_err:.1f}  B={B:.1f}+-{B_err:.1f}  "
                  f"C={C:.1f}+-{C_err:.1f}  D=BLINDED")
            print(f"TF(B/A)={tf:.4f}+-{tf_err:.4f}  "
                  f"D_pred={D_pred:.2f}+-{D_pred_err:.2f}  D_obs=BLINDED")
        else:
            print(f"ntrk={nt}: A={A:.1f}+-{A_err:.1f}  B={B:.1f}+-{B_err:.1f}  "
                  f"C={C:.1f}+-{C_err:.1f}  D={D:.1f}+-{D_err:.1f}")
            print(f"  TF(B/A)={tf:.4f}+-{tf_err:.4f}  "
                  f"D_pred={D_pred:.2f}+-{D_pred_err:.2f}  D_obs={D:.1f}+-{D_err:.1f}")

    return np.array(ntracks), np.array(tfs), np.array(tf_errs), region_yields

def plot_transfer_factor(ntracks, tfs, tf_errs, process_label="2024 Data"):
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.errorbar(
        ntracks, tfs, yerr=tf_errs,
        fmt='o', color='black', markersize=6, capsize=4, linewidth=1.5,
        label=f"TF = B/A"
    )

    ax.set_xlabel("Vertex Track Multiplicity", fontsize=16)
    ax.set_ylabel("Transfer Factor (B/A)", fontsize=16)
    tick_labels = [str(nt) for nt in NTRACK_BINS]
    ax.set_xticks(ntracks)
    ax.set_xticklabels(tick_labels)
    ax.legend(fontsize=14)

    hep.cms.label("Work in progress", loc=0, ax=ax, com=13.6, fontsize=16,data=True)

    plt.tight_layout()
    plt.savefig("transfer_factor_vs_ntrack.pdf")
    plt.savefig("transfer_factor_vs_ntrack.png", dpi=150)
    
    print("Saved transfer_factor_vs_ntrack.pdf/png")

def plot_closure(ntracks, region_yields, process_label="2024 Data"):
    """Plot predicted vs observed D region yields."""
    A_vals, A_errs = np.array(region_yields["A"][0]), np.array(region_yields["A"][1])
    B_vals, B_errs = np.array(region_yields["B"][0]), np.array(region_yields["B"][1])
    C_vals, C_errs = np.array(region_yields["C"][0]), np.array(region_yields["C"][1])
    D_vals, D_errs = np.array(region_yields["D"][0]), np.array(region_yields["D"][1])

    safe_A = np.where(A_vals > 0, A_vals, 1.0)
    D_pred = np.where(A_vals > 0, C_vals * B_vals / safe_A, 0)
    D_pred_err = np.where(
        (A_vals > 0) & (B_vals > 0) & (C_vals > 0),
        D_pred * np.sqrt((A_errs/safe_A)**2 + (B_errs/np.where(B_vals>0,B_vals,1.0))**2 + (C_errs/np.where(C_vals>0,C_vals,1.0))**2),
        0
    )

    # Build masks for blinded vs unblinded bins
    blinded_mask = np.array([nt in BLINDED_BINS for nt in NTRACK_BINS])
    unblinded_mask = ~blinded_mask

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), height_ratios=[3, 1],
                                    sharex=True, gridspec_kw={'hspace': 0.05})

    # Plot prediction for all bins
    ax1.errorbar(ntracks - 0.05, D_pred, yerr=D_pred_err,
                 fmt='s', color='red', markersize=6, capsize=4, label="Predicted (C*B/A)")

    # Plot observed only for unblinded bins
    if np.any(unblinded_mask):
        ax1.errorbar(ntracks[unblinded_mask] + 0.05, D_vals[unblinded_mask],
                     yerr=D_errs[unblinded_mask],
                     fmt='o', color='black', markersize=6, capsize=4, label="Observed (D)")

    # Mark blinded bins with gray bands
    if np.any(blinded_mask):
        for x in ntracks[blinded_mask]:
            ax1.axvspan(x - 0.4, x + 0.4, color='gray', alpha=0.15, zorder=0)

    ax1.set_ylabel("Events", fontsize=16)
    ax1.legend(fontsize=18)
    ax1.set_yscale("log")

    # Place blinded labels after log scale is set so ylim is sensible
    if np.any(blinded_mask):
        for x in ntracks[blinded_mask]:
            ax1.text(x, ax1.get_ylim()[0] * 2, "BLINDED", ha='center', va='bottom',
                     fontsize=10, color='gray', fontstyle='italic')

    hep.cms.label("Work in progress", loc=0, ax=ax1, com=13.6, fontsize=16,data=True)
    # Ratio panel: only for unblinded bins
    safe_D = np.where(D_vals > 0, D_vals, 1.0)  # avoid division by zero
    ratio = np.where((D_vals > 0) & unblinded_mask, D_pred / safe_D, np.nan)
    ratio_err = np.where((D_vals > 0) & unblinded_mask, D_pred_err / safe_D, np.nan)

    if np.any(unblinded_mask):
        valid = unblinded_mask & np.isfinite(ratio)
        ax2.errorbar(ntracks[valid], ratio[valid], yerr=ratio_err[valid],
                     fmt='o', color='black', markersize=6, capsize=4)

    ax2.axhline(1, color='red', linestyle='--', linewidth=1)
    ax2.set_xlabel("Vertex Track Multiplicity", fontsize=16)
    ax2.set_ylabel("Pred / Obs", fontsize=16)
    ax2.set_ylim(0.5, 1.5)
    tick_labels = [str(nt) for nt in NTRACK_BINS]
    ax2.set_xticks(ntracks)
    ax2.set_xticklabels(tick_labels)

    # Gray bands on ratio panel too
    if np.any(blinded_mask):
        for x in ntracks[blinded_mask]:
            ax2.axvspan(x - 0.4, x + 0.4, color='gray', alpha=0.15, zorder=0)

    plt.savefig("abcd_closure_vs_ntrack.pdf")
    plt.savefig("abcd_closure_vs_ntrack.png", dpi=150)
    print("Saved abcd_closure_vs_ntrack.pdf/png")
    
def main():
    limitDict = build_limits("../EXO-23-13-ExoHiggsBRLimitvsLifetime.root","../EXO-19-13-RPVSUSYSigmaBSquaredLimitsMassvsLifetime.root")
    signalDict, dataDict = makeDict("v33-4DxyMin",["Hto2Sto4D"],["2024"])
    run_dict = dataDict

    # Parallel processing
    all_results = []
    with ProcessPoolExecutor(max_workers=16) as executor:
        futures = {
            executor.submit(process_abcd_per_ntrack, (f, p)): (f, p)
            for p, files in run_dict.items() for f in files
        }
        for future in as_completed(futures):
            all_results.append(future.result())

    merged = merge_counts(all_results)

    # Combine data eras
    combined = {nt: {r: [0.0, 0.0] for r in ABCD_REGIONS} for nt in NTRACK_BINS}
    data_eras = [k for k in merged if k.startswith("2024")]
    for era in data_eras:
        for nt in NTRACK_BINS:
            for r in ABCD_REGIONS:
                combined[nt][r][0] += merged[era][nt][r][0]
                combined[nt][r][1] += merged[era][nt][r][1]

    print("\n=== 2024 Data Combined ===")
    ntracks, tfs, tf_errs, region_yields = compute_transfer_factors(combined)

    plot_transfer_factor(ntracks, tfs, tf_errs, process_label="2024 Data")
    plot_closure(ntracks, region_yields, process_label="2024 Data")
    
if __name__=="__main__":
    main()
