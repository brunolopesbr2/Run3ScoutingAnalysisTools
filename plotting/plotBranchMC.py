from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")

plotDict = {
    #"vertTrack_pt": [0,5,101],# "vertTrack_eta": [-3,3,101], "vertTrack_phi": [-3.142,3.142,101],
    #"vertTrack_reducedChi2": [0,7,51], "vertTrack_dxy": [0,0.3,51], "vertTrack_dxyErr": [0,0.05,101], 
    #"vertTrack_dxySig": [0,50,101],
    #"vertTrack_nValidPixelHits": [0,13,14], "vertTrack_nTrackerLayersWithMeasurement": [0,21,22],
    #"vertTrack_nValidStripHits": [0,32,33], 
    #"vertTrack_shiftZErr": [0,0.05,51], "vertTrack_shiftZValue": [0,0.05,101],
    #"vertTrack_shift3DErr": [0,0.05,51], "vertTrack_shift3DValue": [0,0.1,101],
    #"scoutVert_dBV": [0,2,51],
    #"scoutVert_dBVErr": [0,0.1,51],
    #"vertTrack_nMissingInnerHits": [0,5,6], 
    "scoutVert_nTracks": [0,25,26]#, "scoutVert_chi2": [0,5,50],
    #"scoutVert_dT": [0,0.5,101], "scoutVert_cosT": [-1,1,41], 
    #"scoutVert_pMag": [0,500,26],
    #"scoutTrack_phi": [-3.142,3.142,101], "scoutTrack_dxySig": [0,50,101], "scoutTrack_nTrackerLayersWithMeasurement": [0,21,22],
    #"scoutTrack_pt": [0,50,101], "scoutTrack_nValidPixelHits": [0,13,14]
    #"truePU": [0,100,101]
    #"vertTrack_iJet": [-2,10,13]
}

def process_root_file(args):
    rootFile, process = args
    print(f"Processing {rootFile}")

    output = {}
    genWeightSum = 0
    with uproot.open(rootFile) as file:
        genWeightSum = file["triggerFilter/genWeightsSkim"].values()[0]
        tree = file["scoutingTree/objectTree"]

        # Select only necessary branches to load
        branches = list(plotDict.keys()) + ["weight_trigger_nominal","uncorrectedWeight","weight_PU_BCDEFGHI_nominal","vertTrack_iVtx", "weight","scoutVert_dBV","scoutVert_chi2","scoutVert_dBVErr","scoutVert_cosT","scoutVert_nTracks"]
        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        for batch in tree.iterate(branches, library="ak", step_size=100000):  
            weights = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] * batch["weight_trigger_nominal"]
            weights = weights / genWeightSum

            for plot, binning in plotDict.items():
                bins = np.linspace(binning[0], binning[1], binning[2])
                data = batch[plot]
                # Apply displacement cut
                #if "vertTrack_shift" in plot:
                #   mask = (batch["scoutVert_dBV"][batch["vertTrack_iVtx"]] >= 0.1) & (batch["vertTrack_shiftZValue"] > -900)
                if "vertTrack" in plot:
                    #mask = (batch["scoutVert_dBV"][batch["vertTrack_iVtx"]] >= 0.1)  & (batch["vertTrack_dxySig"] > 5) & (batch["vertTrack_pt"] > 1.0) & (batch["vertTrack_nValidPixelHits"] > 1)
                    mask = (batch["scoutVert_dBV"][batch["vertTrack_iVtx"]] >= 0.01) & (batch["scoutVert_dBV"][batch["vertTrack_iVtx"]] < 2) #& (batch["scoutVert_dBVErr"][batch["vertTrack_iVtx"]] < 0.005) & (batch["scoutVert_nTracks"][batch["vertTrack_iVtx"]] > 4)
                elif "scoutVert" in plot:
                    mask = (batch["scoutVert_dBV"] >= 0.01) & (batch["scoutVert_dBV"] < 2) & (batch["scoutVert_cosT"] > 0) & (batch["scoutVert_chi2"] < 2.5) & (batch["scoutVert_dBVErr"] < 0.005) #& (batch["scoutVert_nTracks"] > 7)
                elif "scoutTrack" in plot:
                    mask = (batch["scoutTrack_dxySig"] > 5) & (batch["scoutTrack_pt"] > 1.0) & (batch["scoutTrack_nValidPixelHits"] > 1) & (batch["scoutTrack_nTrackerLayersWithMeasurement"] > 5)
                else:
                    mask = ak.ones_like(data, dtype=bool)
                data = data[mask]
                #mask = ak.sum(mask,axis=1)>1
                #data = data[mask]
                #maskedWeights = weights[mask]
                broadcastWeights, data = ak.broadcast_arrays(weights,data)
                # Apply mask and flatten data
                data = ak.flatten(data,axis=None)
                data = np.clip(data,bins[0],bins[-1])
                weights_filtered = ak.flatten(broadcastWeights,axis=None)
                # Compute histograms
                n, _ = np.histogram(data, weights=weights_filtered, bins=bins)
                n_2, _ = np.histogram(data, weights=weights_filtered**2, bins=bins)
                if plot not in output:
                    output[plot] = {process: n}
                    output[f"{plot}_squared"] = {process: n_2}
                else:
                    output[plot][process] = output[plot][process] + n
                    output[f"{plot}_squared"][process] = output[f"{plot}_squared"][process] + n_2
    return output

# **Parallel Processing Using ProcessPoolExecutor**
def parallel_processing(files_dict):
    results = {}
    with ProcessPoolExecutor(max_workers=16) as executor:  # Adjust max_workers based on CPU cores
        futures = {executor.submit(process_root_file, (f, p)): (f, p)
                   for p, files in files_dict.items() for f in files}

        for future in as_completed(futures):
            result = future.result()
            for plot in result:
                if plot not in results:
                    results[plot] = result[plot]
                else:
                    for process in result[plot]:
                        results[plot][process] = results[plot].get(process, 0) + result[plot][process]

    return results

# **Parallel Processing Using ProcessPoolExecutor**
def parallel_processing(files_dict):
    results = {}
    with ProcessPoolExecutor(max_workers=16) as executor:  # Adjust max_workers based on CPU cores
        futures = {executor.submit(process_root_file, (f, p)): (f, p)
                   for p, files in files_dict.items() for f in files}

        for future in as_completed(futures):
            result = future.result()
            for plot in result:
                if plot not in results:
                    results[plot] = result[plot]
                else:
                    for process in result[plot]:
                        results[plot][process] = results[plot].get(process, 0) + result[plot][process]

    return results

def main():
    limitDict = build_limits("../EXO-23-13-ExoHiggsBRLimitvsLifetime.root","../EXO-19-13-RPVSUSYSigmaBSquaredLimitsMassvsLifetime.root")
    signalDict, processDict = makeDict("v33-4DxyMin",["Hto2Sto4B","Hto2Sto4D"],["QCD","TTTo"])
    bgPlotWeights = parallel_processing(processDict)
    sigPlotWeights = parallel_processing(signalDict)

    #Combining Background Subprocesses and Reweighting Events
    for plot in plotDict.keys():
        bgPlotWeights[plot]["QCD"] = bgPlotWeights[plot]["QCD40to70"]+bgPlotWeights[plot]["QCD70to100"]+bgPlotWeights[plot]["QCD100to200"]+bgPlotWeights[plot]["QCD200to400"]+bgPlotWeights[plot]["QCD400to600"]+bgPlotWeights[plot]["QCD600to800"]+bgPlotWeights[plot]["QCD800to1000"]+bgPlotWeights[plot]["QCD1000to1200"]+bgPlotWeights[plot]["QCD1200to1500"]+bgPlotWeights[plot]["QCD1500to2000"]+bgPlotWeights[plot]["QCD2000"]
        bgPlotWeights[f"{plot}_squared"]["QCD"] = bgPlotWeights[f"{plot}_squared"]["QCD40to70"]+bgPlotWeights[f"{plot}_squared"]["QCD70to100"]+bgPlotWeights[f"{plot}_squared"]["QCD100to200"]+bgPlotWeights[f"{plot}_squared"]["QCD200to400"]+bgPlotWeights[f"{plot}_squared"]["QCD400to600"]+bgPlotWeights[f"{plot}_squared"]["QCD600to800"]+bgPlotWeights[f"{plot}_squared"]["QCD800to1000"]+bgPlotWeights[f"{plot}_squared"]["QCD1000to1200"]+bgPlotWeights[f"{plot}_squared"]["QCD1200to1500"]+bgPlotWeights[f"{plot}_squared"]["QCD1500to2000"]+bgPlotWeights[f"{plot}_squared"]["QCD2000"]
        bgPlotWeights[plot]["TTbar"] = bgPlotWeights[plot]["TTTo4Q"]+bgPlotWeights[plot]["TTToLNu2Q"]
        bgPlotWeights[f"{plot}_squared"]["TTbar"] = bgPlotWeights[f"{plot}_squared"]["TTTo4Q"]+bgPlotWeights[f"{plot}_squared"]["TTToLNu2Q"]

    # **Plotting**
    for plot, binning in plotDict.items():
        if plot not in bgPlotWeights:
            print(f"Skipping {plot} (no data).")
            continue

        bins = np.linspace(binning[0], binning[1], binning[2])
        bgIntegral = (bins[1] - bins[0]) * sum(bgPlotWeights[plot]["QCD"] + bgPlotWeights[plot]["TTbar"])
        bgIntegral = 1
        fig, (ax, rax) = plt.subplots(2, 1, figsize=[12,12], gridspec_kw={"height_ratios": [3,1]}, sharex=True)
        fig.subplots_adjust(hspace=0.06)
        ax.hist([(bins[:-1] + bins[1:]) / 2]*2,weights=[list(bgPlotWeights[plot]["TTbar"]),list(bgPlotWeights[plot]["QCD"])],
                stacked=True, density=False, label=[r"$t\bar{t}$","QCD"], bins=bins)
        
        bgValues = (bgPlotWeights[plot]["QCD"] / bgIntegral) + (bgPlotWeights[plot]["TTbar"] / bgIntegral)
        bgErrors = np.sqrt(bgPlotWeights[f"{plot}_squared"]["QCD"] / (bgIntegral**2) + \
                           bgPlotWeights[f"{plot}_squared"]["TTbar"] / (bgIntegral**2))
        #bgValues = np.nan_to_num(bgValues)
        #bgErrors = np.nan_to_num(bgErrors)
        ax.errorbar(((bins[:-1] + bins[1:]) / 2), bgValues, yerr=bgErrors, linestyle="none", color="purple")
        
        #colors = {"Stop-M200-cT0p3": "black", "Stop-M200-cT1": "red", "Stop-M800-cT0p3": "blue", "Stop-M800-cT1": "green"}
        colors = {"Hto2Sto4D-cT1-MS15": "black", "Hto2Sto4D-cT1-MS55": "blue", "Hto2Sto4B-cT1-MS15": "red", "Hto2Sto4B-cT1-MS55": "green"}
        for signal, color in colors.items():
            if plot not in sigPlotWeights or signal not in sigPlotWeights[plot]:
                print(f"Skipping {signal} in {plot} (no data).")
                continue

            legendLabel = signal
            if "Stop" in signal:
                string = signal.split("-")
                mass = string[1][1:]
                lifetime = string[2][2:]
                lifetime = lifetime.replace("p",".")
                legendLabel = rf'$\tilde{{t}}\rightarrow \bar{{d}}\bar{{d}}$ m={mass} GeV c$\tau$={lifetime} mm'
            if "Hto2Sto4B" in signal:
                string = signal.split("-")
                mass = string[2][2:]
                lifetime = string[1][2:]
                lifetime = lifetime.replace("p",".")
                legendLabel = rf'$H\rightarrow SS \rightarrow b\bar{{b}}b\bar{{b}}$ m={mass} GeV c$\tau$={lifetime} mm'
            if "Hto2Sto4D" in signal:
                string = signal.split("-")
                mass = string[2][2:]
                lifetime = string[1][2:]
                lifetime = lifetime.replace("p",".")
                legendLabel = rf'$H\rightarrow SS \rightarrow d\bar{{d}}d\bar{{d}}$ m={mass} GeV c$\tau$={lifetime} mm'
            
            integral = (bins[1] - bins[0]) * sum(sigPlotWeights[plot][signal])
            integral = 1
            ax.hist(((bins[:-1] + bins[1:]) / 2), weights=list(sigPlotWeights[plot][signal]),
                    stacked=False, density=False, label=legendLabel, bins=bins, histtype="step", color=color)
            
            sigValues = sigPlotWeights[plot][signal] / integral
            sigErrors = np.sqrt(sigPlotWeights[f"{plot}_squared"][signal] / (integral**2))
            
            ax.errorbar(((bins[:-1] + bins[1:]) / 2), sigValues, yerr=sigErrors, linestyle="none", color=color)
            ratioValues = sigValues / bgValues
            ratioErrors = ratioValues * np.sqrt((sigErrors / sigValues)**2 + (bgErrors / bgValues)**2)
            #ratioValues = np.nan_to_num(ratioValues)
            #ratioErrors = np.nan_to_num(ratioErrors)
            rax.errorbar(((bins[:-1] + bins[1:]) / 2), ratioValues, yerr=ratioErrors, linestyle="none", color=color, marker=".")

        rax.hlines(1, bins[0], bins[-1], linestyle="dashed")
        rax.set_ylabel("s/b ratio")
        ax.set_ylabel("A.U")
        #plt.xlabel(plot)
        if "scoutVert_nTracks" in plot:
            plt.xlabel("Vertex Track Multiplicity")
        else:
            plt.xlabel(plot)
        ax.legend(fontsize=16,labelspacing=0.25)
        ax.set_yscale("log")
        rax.set_yscale("log")
        hep.cms.label("Work in progress", loc=0, ax=ax, com=13.6, fontsize=16,data=True)
        plt.savefig(f"{plot}_sigbkg_stop.pdf", bbox_inches='tight')
    
    
if __name__=="__main__":
    main()
