from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")
from collections import Counter
import glob
import os

def parse_lumi_files(file_pattern, lumi_dir):
    """
    Parse luminosity CSV files and build a dictionary of {run: recorded_lumi}.
    Assumes files have two header lines starting with '#', then data lines like:
    379416:9517,04/14/24 17:34:18,195,195,0.042302619,0.039739297
    """
    lumi_by_run = {}
    files = sorted(glob.glob(os.path.join(lumi_dir, file_pattern)))

    if not files:
        print(f"No files found matching '{file_pattern}' in '{lumi_dir}'")
        return lumi_by_run

    for f in files:
        print(f"Processing {f}")
        with open(f, "r") as infile:
            for line in infile:
                line = line.strip().strip("\r")
                if not line or line.startswith("#"):
                    continue
                cols = line.split(",")
                run = int(cols[0].split(":")[0])
                recorded = float(cols[-1])
                lumi_by_run[run] = lumi_by_run.get(run, 0.0) + recorded

    print(f"\nParsed {len(lumi_by_run)} unique runs from {len(files)} files")
    return lumi_by_run

def process_cutflows(args):
    rootFile, process = args
    print(f"Processing {rootFile}")

    output = {}
    with uproot.open(rootFile) as file:
        output[process+"_runNumbersB"] = Counter()  # Track run numbers for region B
        tree = file["scoutingTree/objectTree"]

        branches = ["scoutVert_dBV","scoutVert_dBVErr", "scoutVert_nTracks","weight","scoutVert_chi2","scoutVert_cosT","runNumber","lumiBlock"]
        runNumberCountsB = Counter()  # Local counter for this file
        
        for batch in tree.iterate(branches, library="ak", step_size=100000):  
            weights = batch["weight"]
            weights = ak.ones_like(weights)
            dBV = batch["scoutVert_dBV"]
            dBVErr = batch["scoutVert_dBVErr"]
            ntracks = batch["scoutVert_nTracks"]
            chi2 = batch["scoutVert_chi2"]
            cosT = batch["scoutVert_cosT"]
            runNumber = batch["runNumber"]
            lumisection = batch["lumiBlock"]
            
            mask = (dBV>0.01) & (dBV<2.0) & (ntracks>4) & (cosT>0) & (dBVErr<0.005) 
            dBV = dBV[mask]
            ntracks = ntracks[mask]
            chi2 = chi2[mask]
            mask = (ak.num(dBV,axis=1)>0) & (runNumber!=384323) #& (runNumber!=384322)
            weights = weights[mask]
            ntracks = ntracks[mask]
            chi2 = chi2[mask]
            runNumber = runNumber[mask]
            lumisection = lumisection[mask]
            
            ntrackMask = (ntracks>7)
            ntrackMinMask = (ntracks>5)
            chi2Mask = (chi2<3)
            
            #Signal region B
            mask = ntrackMask & chi2Mask
            mask = ak.num(ntracks[mask])>0
            runNumberB = runNumber[mask]
            lumisectionB = lumisection[mask]
            weightsB = weights[mask]
            
            # Count run numbers for events passing region B
            runNumberB_flat = ak.to_numpy(runNumberB)
            runNumberCountsB.update(runNumberB_flat)
            
        output[process+"_runNumbersB"] = runNumberCountsB        
    return output

def parallel_processing(files_dict):
    results = {}
    with ProcessPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(process_cutflows, (f, p)): (f, p)
                   for p, files in files_dict.items() for f in files}

        for future in as_completed(futures):
            result = future.result()
            for key in result:
                # Merge Counter objects
                if key not in results:
                    results[key] = Counter()
                results[key].update(result[key])

    return results

def main():
    limitDict = build_limits("../EXO-23-13-ExoHiggsBRLimitvsLifetime.root","../EXO-19-13-RPVSUSYSigmaBSquaredLimitsMassvsLifetime.root")
    signalDict, processDict = makeDict("v24-3to4Dxy",["Hto2Sto4D"],["2024"])
    dict = signalDict | processDict
    customWeights = parallel_processing(dict)
    lumi_by_run = parse_lumi_files(file_pattern="2024*_Brilcalc.csv", lumi_dir="/afs/cern.ch/user/r/rmccarth/private/scouting/CMSSW_14_0_18_patch1/src/Run3ScoutingAnalysisTools/GoldenJSON")

    customWeights["2024_runNumbersB"] = customWeights["2024C_runNumbersB"]+customWeights["2024D_runNumbersB"]+customWeights["2024E_runNumbersB"]+customWeights["2024F_runNumbersB"]+customWeights["2024G_runNumbersB"]+customWeights["2024H_runNumbersB"]+customWeights["2024I_runNumbersB"]
    # Build arrays of run number and effective cross section (counts / lumi)
    runs = []
    xsec = []

    for run, lumi in lumi_by_run.items():
        runs.append(run)
        if run in customWeights["2024_runNumbersB"]:
            xsec.append(customWeights["2024_runNumbersB"][run] / lumi)
        else:
            xsec.append(0)

    runs = np.array(runs)
    xsec = np.array(xsec)

    # Sort by run number for cleaner plotting
    order = np.argsort(runs)
    runs = runs[order]
    xsec = xsec[order]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.scatter(runs, xsec, s=5, alpha=0.7)
    ax.set_xlabel("Run Number")
    ax.set_ylabel("Counts / Recorded Luminosity [1/fb]")
    ax.set_title("Effective Cross Section per Run (Region B, 2024)")
    ax.ticklabel_format(axis="x", style="plain")
    plt.savefig("crossSectionVsRun.pdf")
    
if __name__=="__main__":
    main()
