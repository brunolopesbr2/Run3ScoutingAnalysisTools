from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")
import matplotlib.ticker as ticker
import ROOT
#Binned ABCD Signal Contamination Plot

# ABCD regions in (cosT, chi2):
#   A: cosT <= 0, chi2 >= 2.5  (fail both)
#   B: cosT <= 0, chi2 < 2.5   (pass chi2 only)
#   C: cosT > 0,  chi2 >= 2.5  (pass cosT only)
#   D: cosT > 0,  chi2 < 2.5   (signal region)
#
# Transfer factor: TF = B/A
# Prediction: D_pred = C * (B/A)
NTRACK_BINS = [3, 4, 5, 6]
ABCD_REGIONS = ["A", "B", "C", "D"]

def process_abcd_per_ntrack(args):
    rootFile, process = args
    print(f"Processing {rootFile}")

    # Initialize counts: {ntrk: {region: (sum_w, sum_w2)}}
    counts = {nt: {r: [0.0, 0.0] for r in ABCD_REGIONS} for nt in NTRACK_BINS}

    with uproot.open(rootFile) as file:
        tree = file["scoutingTree/objectTree"]
        branches = [
            "scoutVert_dBV", "scoutVert_dBVErr", "scoutVert_nTracks",
            "scoutVert_chi2", "scoutVert_cosT", "jet_pt", "uncorrectedWeight", "weight_PU_BCDEFGHI_nominal", "weight_trigger_nominal"
        ]

        for batch in tree.iterate(branches, library="ak", step_size=100000):
            weights = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] * batch["weight_trigger_nominal"] #* (1/2) # event weights for half of 2024
            if("2024" in process):
                weights = ak.ones_like(weights)
            dBV = batch["scoutVert_dBV"]
            dBVErr = batch["scoutVert_dBVErr"]
            ntracks = batch["scoutVert_nTracks"]
            chi2 = batch["scoutVert_chi2"]
            cosT = batch["scoutVert_cosT"]
            # Baseline vertex selection
            vtx_mask = (dBV > 0.01) & (dBV < 2.0) & (ntracks > 2) & (dBVErr < 0.005) & (ntracks < 7)
            dBV = dBV[vtx_mask]
            ntracks = ntracks[vtx_mask]
            chi2 = chi2[vtx_mask]
            cosT = cosT[vtx_mask]

            # Keep events with at least one vertex passing baseline
            evt_mask = ak.num(dBV, axis=1) > 0
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

def main():
    limitDict = build_limits("../EXO-23-13-ExoHiggsBRLimitvsLifetime.root","../EXO-19-13-RPVSUSYSigmaBSquaredLimitsMassvsLifetime.root")
    signalDict, dataDict = makeDict("v33-4DxyMin",["Hto2Sto4D-cT0p1-MS15","Hto2Sto4D-cT0p1-MS55","Hto2Sto4D-cT1-MS15","Hto2Sto4D-cT1-MS55","Hto2Sto4D-cT10-MS15","Hto2Sto4D-cT10-MS55"],["2024"])
    run_dict = signalDict | dataDict

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

    genWeightSumDict = {}
    for process, rootFiles in signalDict.items():
        genWeightSum = 0
        for rootFile in rootFiles:
            f = ROOT.TFile.Open(rootFile, "READ")
            h_genWeights = f.Get("triggerFilter/genWeightsSkim")
            n_binsSkim = h_genWeights.GetNbinsX() 
            genWeights = np.array([h_genWeights.GetBinContent(i) for i in range(1, n_binsSkim + 1)])
            genWeightSum += genWeights[0]
        genWeightSumDict[process] = genWeightSum

    #Reweighting Signal Events
    for process in signalDict.keys():
        if process in limitDict:
            currentLimit = limitDict[process]
        else:
            currentLimit = 1
        for nt in NTRACK_BINS:
            for r in ABCD_REGIONS:
                merged[process][nt][r][0] = merged[process][nt][r][0] / genWeightSumDict[process]
                merged[process][nt][r][0] = merged[process][nt][r][0] * currentLimit
                merged[process][nt][r][1] = merged[process][nt][r][1] / (genWeightSumDict[process]**2)
                merged[process][nt][r][1] = merged[process][nt][r][1] * (currentLimit**2)
    
    plt.style.use(hep.style.CMS)

    fig, ax = plt.subplots(figsize=(14, 6))

    # Build x-axis bin labels: "Region_Ntrk"
    bin_labels = []
    for nt in NTRACK_BINS:
        for r in ABCD_REGIONS:
            bin_labels.append(f"{r}, ntrk={nt}")

    x = np.arange(len(bin_labels))

    # Color cycle for signals
    colors = plt.cm.tab20.colors

    for i_sig, process in enumerate(sorted(signalDict.keys())):
        ratios = []
        ratio_errs = []

        for nt in NTRACK_BINS:
            for r in ABCD_REGIONS:
                s_w, s_w2 = merged[process][nt][r]
                d_w, d_w2 = combined[nt][r]
                #print(process,"nt",nt,"r",r,"s_w",s_w,"s_w2",s_w2,"d_w",d_w,"d_w2",d_w2)
                if d_w > 0 and s_w != 0:
                    ratio = s_w / d_w
                    # Error propagation: delta(S/D) = |S/D| * sqrt((deltaS/S)^2 + (deltaD/D)^2)
                    sig_s = np.sqrt(s_w2) if s_w2 > 0 else 0.0
                    sig_d = np.sqrt(d_w2) if d_w2 > 0 else 0.0
                    rel_s = (sig_s / abs(s_w)) if s_w != 0 else 0.0
                    rel_d = (sig_d / d_w) if d_w > 0 else 0.0
                    ratio_err = abs(ratio) * np.sqrt(rel_s**2 + rel_d**2)
                else:
                    ratio = 0.0
                    ratio_err = 0.0

                ratios.append(ratio)
                ratio_errs.append(ratio_err)

        ratios = np.array(ratios)
        ratio_errs = np.array(ratio_errs)

        # Small horizontal offset so overlapping points are visible
        offset = (i_sig - len(signalDict) / 2) * 0.075
        ax.errorbar(
            x + offset, ratios, yerr=ratio_errs,
            fmt='o', markersize=4, capsize=3,
            color=colors[i_sig % len(colors)],
            label=process
        )

    # Draw vertical lines to separate ntrack groups
    for i in range(1, len(NTRACK_BINS)):
        ax.axvline(x=i * len(ABCD_REGIONS) - 0.5, color='gray', ls='--', lw=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(bin_labels, rotation=45, ha='right', fontsize=10)
    ax.set_ylabel("Signal / Data")
    ax.set_xlabel("ABCD Region, Track Multiplicity Bin")
    ax.set_yscale('log')
    ax.legend(fontsize=9, ncol=2, loc='best')
    ax.set_title("Signal Contamination")
    hep.cms.label("Preliminary", loc=0, ax=ax, com=13.6, fontsize=16,data=True)
    #fig.tight_layout()
    ax.yaxis.set_major_locator(ticker.LogLocator(numticks=999))
    ax.yaxis.set_minor_locator(ticker.LogLocator(numticks=999, subs="auto"))
    #fig.savefig("signal_contamination_abcd_higgs_3to4dxy.pdf")
    #fig.savefig("signal_contamination_abcd_higgs_3to4dxy.png", dpi=200)
    plt.savefig("signal_contamination_exoHiggs.pdf")
    

if __name__=="__main__":
    main()
