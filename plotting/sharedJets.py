from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")

plotDict = {"nSharedJet": [0,5,6]}

def count_multivertex_jets(jet_indices, vertex_indices):
    """
    Count jets associated with multiple vertices via their tracks.
    """
    counts = []
    
    for event_jets, event_verts in zip(jet_indices, vertex_indices):
        if len(event_jets) == 0:
            counts.append(0)
            continue
            
        # Convert to numpy for this event
        jets = ak.to_numpy(event_jets)
        verts = ak.to_numpy(event_verts)
        
        # Get unique jets
        unique_jets = np.unique(jets)
        
        # Count jets with multiple vertices
        multi_vertex_count = 0
        for jet in unique_jets:
            jet_vertices = verts[jets == jet]
            if len(np.unique(jet_vertices)) > 1:
                multi_vertex_count += 1
                
        counts.append(multi_vertex_count)
    
    return ak.Array(counts)

def process_root_file(args):
    rootFile, process = args
    print(f"Processing {rootFile}")

    output = {}
    genWeightSum = 0
    with uproot.open(rootFile) as file:
        output["genWeightSum"] = {}
        genWeightSum = file["triggerFilter/genWeightsSkim"].values()[0]
        tree = file["scoutingTree/objectTree"]

        # Select only necessary branches to load
        branches = ["vertTrack_iVtx", "weight","scoutVert_dBV","scoutVert_cosT","vertTrack_iJet","jet_eta","scoutVert_nTracks","uncorrectedWeight","weight_PU_BCDEFGHI_nominal","weight_trigger_nominal"]
        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        for batch in tree.iterate(branches, library="ak", step_size=10000):  
            weights = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] * batch["weight_trigger_nominal"]
            weights = weights / genWeightSum

            for plot, binning in plotDict.items():
                bins = np.linspace(binning[0], binning[1], binning[2])
                iVtx = batch["vertTrack_iVtx"]
                iJet = batch["vertTrack_iJet"]
                mask = (batch["scoutVert_dBV"][iVtx] >= 0.01) & (batch["scoutVert_dBV"][iVtx] < 2.0) & (batch["scoutVert_nTracks"][iVtx] > 6) & (batch["scoutVert_cosT"][iVtx] > 0)
                iVtx = iVtx[mask]
                iJet = iJet[mask]
                mask = (abs(batch["jet_eta"][iJet]) < 2.5)
                iVtx = iVtx[mask]
                iJet = iJet[mask]
                data = count_multivertex_jets(iJet,iVtx)
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

def main():
    limitDict = build_limits("../EXO-23-13-ExoHiggsBRLimitvsLifetime.root","../EXO-19-13-RPVSUSYSigmaBSquaredLimitsMassvsLifetime.root")
    signalDict, processDict = makeDict("v33-4DxyMin",["Stop-M"],["QCD","TTTo"])
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

        fig, (ax, rax) = plt.subplots(2, 1, figsize=[12,12], gridspec_kw={"height_ratios": [3,1]}, sharex=True)
        fig.subplots_adjust(hspace=0.06)
        ax.hist([(bins[:-1] + bins[1:]) / 2]*2,weights=[list(bgPlotWeights[plot]["TTbar"]),list(bgPlotWeights[plot]["QCD"])],
                stacked=True, density=True, label=["TTbar","QCD"], bins=bins)

        bgValues = (bgPlotWeights[plot]["QCD"] / bgIntegral) + (bgPlotWeights[plot]["TTbar"] / bgIntegral)
        bgErrors = np.sqrt(bgPlotWeights[f"{plot}_squared"]["QCD"] / (bgIntegral**2) + \
                   bgPlotWeights[f"{plot}_squared"]["TTbar"] / (bgIntegral**2))
        #bgValues = np.nan_to_num(bgValues)
        #bgErrors = np.nan_to_num(bgErrors)
        ax.errorbar(((bins[:-1] + bins[1:]) / 2), bgValues, yerr=bgErrors, linestyle="none", color="purple")

        colors = {"Stop-M200-cT10": "black", "Stop-M400-cT10": "red", "Stop-M600-cT10": "blue", "Stop-M800-cT10": "green"}
        #colors = {"Hto2Sto4D-cT10-MS1": "black", "Hto2Sto4D-cT10-MS15": "red", "Hto2Sto4D-cT10-MS30": "blue", "Hto2Sto4D-cT10-MS55": "green"}
        for signal, color in colors.items():
            if plot not in sigPlotWeights or signal not in sigPlotWeights[plot]:
                print(f"Skipping {signal} in {plot} (no data).")
                continue

            integral = (bins[1] - bins[0]) * sum(sigPlotWeights[plot][signal])
            ax.hist(((bins[:-1] + bins[1:]) / 2), weights=list(sigPlotWeights[plot][signal]),
                    stacked=False, density=True, label=signal, bins=bins, histtype="step", color=color)

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
        plt.xlabel(plot)
        ax.legend()
        ax.set_yscale("log")
        rax.set_yscale("log")
        plt.savefig(f"sharedJets.pdf", bbox_inches='tight')
    
if __name__=="__main__":
    main()
