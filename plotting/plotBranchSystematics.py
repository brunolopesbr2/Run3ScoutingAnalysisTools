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
    #"vertTrack_pt": [0,25,26], "vertTrack_eta": [-3,3,26], "vertTrack_phi": [-3.142,3.142,26],
    #"vertTrack_reducedChi2": [0,7,51], 
    #"vertTrack_dxy": [0,0.3,51], "vertTrack_dxyErr": [0,0.05,51], "vertTrack_dxySig": [2.5,5,51],
    #"vertTrack_dz": [0,0.025,51], "vertTrack_dzErr": [0,0.05,51], "vertTrack_dzSig": [0,500,51],
    #"vertTrack_nValidPixelHits": [0,13,14], #"vertTrack_nTrackerLayersWithMeasurement": [0,21,22],
    #"vertTrack_nValidStripHits": [0,32,33], 
    #"vertTrack_shiftZErr": [0,0.05,51], "vertTrack_shiftZValue": [0,0.05,101],
    #"vertTrack_shift3DErr": [0,0.05,51], "vertTrack_shift3DValue": [0,0.1,101],
    #"scoutVert_dBV": [0,0.5,26],# "scoutVert_dBVErr": [0,0.1,101],
    #"vertTrack_nMissingInnerHits": [0,5,6], 
    "scoutVert_nTracks": [3,7,5], #"scoutVert_chi2": [0,5,26],
    #"scoutVert_dT": [0,0.5,101], "scoutVert_cosT": [-1,1,101], "scoutVert_pMag": [0,500,101],
    #"scoutTrack_dxy": [0,0.3,51], "scoutTrack_dxyErr": [0,0.05,51], 
    #"scoutTrack_dxySig": [2,5,26],
    #"scoutTrack_dz": [0,0.025,51], "scoutTrack_dzErr": [0,0.05,51], "scoutTrack_dzSig": [0,500,51],
    #"scoutTrack_phi": [-3.142,3.142,101], "scoutTrack_dxySig": [0,50,101], "scoutTrack_nTrackerLayersWithMeasurement": [0,21,22],
    #"scoutTrack_pt": [0,200,101],#, "scoutTrack_nValidPixelHits": [0,13,14]
    #"scoutTrack_pt": [0,25,26], "scoutTrack_eta": [-3,3,26], "scoutTrack_phi": [-3.142,3.142,26],
    #"jet_pt": [30,200,26], "jet_eta": [-3,3,26], "jet_phi": [-3.142,3.142,26],
    #"scoutTrack_pt": [7,100,94],
    #"vertTrack_pt": [4,14,11],
    #"jet_pt": [3,12,10]
    #"vertTrack_iJet": [-2,10,13]
    #"vertTrack_hasPFMatch" : [-2,2,5]
}

def process_root_file(args):
    rootFile, process = args
    print(f"Processing {rootFile}")

    output = {}
    with uproot.open(rootFile) as file:
        isMC = True
        if("2024" in process):
            isMC = False
        output["genWeightSum"] = {}
        genWeightSum = file["triggerFilter/genWeightsSkim"].values()[0]
        tree = file["scoutingTree/objectTree"]

        # Select only necessary branches to load
        branches = list(plotDict.keys()) + ["vertTrack_iVtx", "runNumber","scoutVert_dBV","scoutVert_dBVErr","weight","scoutVert_nTracks","scoutTrack_dxySig","scoutTrack_nValidPixelHits","scoutTrack_nValidStripHits","scoutTrack_nTrackerLayersWithMeasurement","scoutTrack_eta","scoutTrack_pt","vertTrack_iJet","scoutTrack_iJet"]
        if(isMC):
            branches = branches + ["uncorrectedWeight","weight_PU_BCDEFGHI_nominal", "weight_PU_BCDEFGHI_up", "weight_PU_BCDEFGHI_down","weight_trigger_nominal","weight_trigger_up","weight_trigger_down"] 
        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        for batch in tree.iterate(branches, library="ak", step_size=40000):
            if(isMC):
                weights = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] * batch["weight_trigger_nominal"]
                weights_PU_up = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_up"] * batch["weight_trigger_nominal"]
                weights_PU_down = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_down"] * batch["weight_trigger_nominal"]
                weights_Trigger_up = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] * batch["weight_trigger_up"]
                weights_Trigger_down = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] * batch["weight_trigger_down"]
            else:
                weights = ak.ones_like(batch["weight"])
                        
            '''
            dBV = batch["scoutVert_dBV"]
            dBV_masked = dBV[mask]
            mask = (dBV_masked >= 0.01) & (dBV_masked < 2.0) & (batch["scoutVert_nTracks"][mask] > 3)
            dBV_masked = dBV_masked[mask]
            eventMask = (ak.num(dBV_masked,axis=1)>0)
            weights=weights[eventMask]
            if(process in bkgDict):
                weights_PU_up=weights_PU_up[eventMask]
                weights_PU_down=weights_PU_down[eventMask]
            '''
            if(isMC): 
                weights = weights / genWeightSum
                weights_PU_up = weights_PU_up / genWeightSum
                weights_PU_down = weights_PU_down / genWeightSum
                weights_Trigger_up = weights_Trigger_up / genWeightSum
                weights_Trigger_down = weights_Trigger_down / genWeightSum
            for plot, binning in plotDict.items():
                bins = np.linspace(binning[0], binning[1], binning[2])
                data = batch[plot]
                
                # Apply displacement cut
                if "vertTrack" in plot:
                    mask = (batch["scoutVert_dBV"][batch["vertTrack_iVtx"]] >= 0.01) & (batch["scoutVert_dBV"][batch["vertTrack_iVtx"]] < 2.0) #& (batch["scoutVert_dBVErr"][batch["vertTrack_iVtx"]] < 0.005) & (batch["scoutVert_nTracks"][batch["vertTrack_iVtx"]] > 4)
                elif "scoutVert" in plot:
                    mask = (batch["scoutVert_dBV"] >= 0.01) & (batch["scoutVert_dBV"] < 2.0) & (batch["scoutVert_nTracks"] < 7)
                elif "scoutTrack" in plot:
                    mask = (batch["scoutTrack_dxySig"] > 4) & (batch["scoutTrack_pt"] > 1.0) & (batch["scoutTrack_nValidPixelHits"] > 2) & (batch["scoutTrack_nValidStripHits"] > 1) & (batch["scoutTrack_nTrackerLayersWithMeasurement"] > 5) & (abs(batch["scoutTrack_eta"])<2.4) #& (batch["scoutTrack_iJet"]!=-1)
                    #mask = (batch["scoutTrack_pt"] > 1.0) & (batch["scoutTrack_nValidPixelHits"] > 2) & (batch["scoutTrack_nValidStripHits"] > 1) & (batch["scoutTrack_nTrackerLayersWithMeasurement"] > 5) & (abs(batch["scoutTrack_eta"])<2.4)
                else:
                    mask = ak.ones_like(data, dtype=bool)
                data = data[mask]
                #data = ak.num(data,axis=1)
                #mask = (runNumber!=384323)
                #data = data[mask]
                #data = data[eventMask]
                #mask = ak.sum(mask,axis=1)>1
                #data = data[mask]
                #maskedWeights = weights[mask]
                broadcastWeights, data = ak.broadcast_arrays(weights,data)
                if(isMC):
                    broadcastWeights_PU_up, data = ak.broadcast_arrays(weights_PU_up,data)
                    broadcastWeights_PU_down, data = ak.broadcast_arrays(weights_PU_down,data)
                    broadcastWeights_Trigger_up, data = ak.broadcast_arrays(weights_Trigger_up,data)
                    broadcastWeights_Trigger_down, data = ak.broadcast_arrays(weights_Trigger_down,data)
                # Apply mask and flatten data
                data = ak.flatten(data,axis=None)
                data = np.clip(data,bins[0],bins[-1])
                weights_filtered = ak.flatten(broadcastWeights,axis=None)
                if(isMC):
                    weights_filtered_PU_up = ak.flatten(broadcastWeights_PU_up,axis=None)
                    weights_filtered_PU_down = ak.flatten(broadcastWeights_PU_down,axis=None)
                    weights_filtered_Trigger_up = ak.flatten(broadcastWeights_Trigger_up,axis=None)
                    weights_filtered_Trigger_down = ak.flatten(broadcastWeights_Trigger_down,axis=None)
                # Compute histograms
                n, _ = np.histogram(data, weights=weights_filtered, bins=bins)
                n_2, _ = np.histogram(data, weights=weights_filtered**2, bins=bins)
                if(isMC):
                    n_PU_up, _ = np.histogram(data, weights=weights_filtered_PU_up, bins=bins)
                    n_PU_down, _ = np.histogram(data, weights=weights_filtered_PU_down, bins=bins)
                    n_Trigger_up, _ = np.histogram(data, weights=weights_filtered_Trigger_up, bins=bins)
                    n_Trigger_down, _ = np.histogram(data, weights=weights_filtered_Trigger_down, bins=bins)
                if plot not in output:
                    output[plot] = {process: n}
                    output[f"{plot}_squared"] = {process: n_2}
                    if(isMC):
                        output[f"{plot}_PU_up"] = {process: n_PU_up}
                        output[f"{plot}_PU_down"] = {process: n_PU_down}
                        output[f"{plot}_Trigger_up"] = {process: n_Trigger_up}
                        output[f"{plot}_Trigger_down"] = {process: n_Trigger_down}
                else:
                    output[plot][process] = output[plot][process] + n
                    output[f"{plot}_squared"][process] = output[f"{plot}_squared"][process] + n_2
                    if(isMC):
                        output[f"{plot}_PU_up"][process] = output[f"{plot}_PU_up"][process] + n_PU_up
                        output[f"{plot}_PU_down"][process] = output[f"{plot}_PU_down"][process] + n_PU_down
                        output[f"{plot}_Trigger_up"][process] = output[f"{plot}_Trigger_up"][process] + n_Trigger_up
                        output[f"{plot}_Trigger_down"][process] = output[f"{plot}_Trigger_down"][process] + n_Trigger_down
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
    bkgDict, dataDict = makeDict("v33-4DxyMin",["QCD","TTTo"],["2024"])
    bgPlotWeights = parallel_processing(bkgDict)
    sigPlotWeights = parallel_processing(dataDict)

    #Combining Background Subprocesses and Reweighting Events
    for plot in plotDict.keys():
        bgPlotWeights[plot]["QCD"] = bgPlotWeights[plot]["QCD40to70"]+bgPlotWeights[plot]["QCD70to100"]+bgPlotWeights[plot]["QCD100to200"]+bgPlotWeights[plot]["QCD200to400"]+bgPlotWeights[plot]["QCD400to600"]+bgPlotWeights[plot]["QCD600to800"]+bgPlotWeights[plot]["QCD800to1000"]+bgPlotWeights[plot]["QCD1000to1200"]+bgPlotWeights[plot]["QCD1200to1500"]+bgPlotWeights[plot]["QCD1500to2000"]+bgPlotWeights[plot]["QCD2000"]
        bgPlotWeights[f"{plot}_squared"]["QCD"] = bgPlotWeights[f"{plot}_squared"]["QCD40to70"]+bgPlotWeights[f"{plot}_squared"]["QCD70to100"]+bgPlotWeights[f"{plot}_squared"]["QCD100to200"]+bgPlotWeights[f"{plot}_squared"]["QCD200to400"]+bgPlotWeights[f"{plot}_squared"]["QCD400to600"]+bgPlotWeights[f"{plot}_squared"]["QCD600to800"]+bgPlotWeights[f"{plot}_squared"]["QCD800to1000"]+bgPlotWeights[f"{plot}_squared"]["QCD1000to1200"]+bgPlotWeights[f"{plot}_squared"]["QCD1200to1500"]+bgPlotWeights[f"{plot}_squared"]["QCD1500to2000"]+bgPlotWeights[f"{plot}_squared"]["QCD2000"]
        bgPlotWeights[f"{plot}_PU_up"]["QCD"] = bgPlotWeights[f"{plot}_PU_up"]["QCD40to70"]+bgPlotWeights[f"{plot}_PU_up"]["QCD70to100"]+bgPlotWeights[f"{plot}_PU_up"]["QCD100to200"]+bgPlotWeights[f"{plot}_PU_up"]["QCD200to400"]+bgPlotWeights[f"{plot}_PU_up"]["QCD400to600"]+bgPlotWeights[f"{plot}_PU_up"]["QCD600to800"]+bgPlotWeights[f"{plot}_PU_up"]["QCD800to1000"]+bgPlotWeights[f"{plot}_PU_up"]["QCD1000to1200"]+bgPlotWeights[f"{plot}_PU_up"]["QCD1200to1500"]+bgPlotWeights[f"{plot}_PU_up"]["QCD1500to2000"]+bgPlotWeights[f"{plot}_PU_up"]["QCD2000"]
        bgPlotWeights[f"{plot}_PU_down"]["QCD"] = bgPlotWeights[f"{plot}_PU_down"]["QCD40to70"]+bgPlotWeights[f"{plot}_PU_down"]["QCD70to100"]+bgPlotWeights[f"{plot}_PU_down"]["QCD100to200"]+bgPlotWeights[f"{plot}_PU_down"]["QCD200to400"]+bgPlotWeights[f"{plot}_PU_down"]["QCD400to600"]+bgPlotWeights[f"{plot}_PU_down"]["QCD600to800"]+bgPlotWeights[f"{plot}_PU_down"]["QCD800to1000"]+bgPlotWeights[f"{plot}_PU_down"]["QCD1000to1200"]+bgPlotWeights[f"{plot}_PU_down"]["QCD1200to1500"]+bgPlotWeights[f"{plot}_PU_down"]["QCD1500to2000"]+bgPlotWeights[f"{plot}_PU_down"]["QCD2000"]
        bgPlotWeights[f"{plot}_Trigger_up"]["QCD"] = bgPlotWeights[f"{plot}_Trigger_up"]["QCD40to70"]+bgPlotWeights[f"{plot}_Trigger_up"]["QCD70to100"]+bgPlotWeights[f"{plot}_Trigger_up"]["QCD100to200"]+bgPlotWeights[f"{plot}_Trigger_up"]["QCD200to400"]+bgPlotWeights[f"{plot}_Trigger_up"]["QCD400to600"]+bgPlotWeights[f"{plot}_Trigger_up"]["QCD600to800"]+bgPlotWeights[f"{plot}_Trigger_up"]["QCD800to1000"]+bgPlotWeights[f"{plot}_Trigger_up"]["QCD1000to1200"]+bgPlotWeights[f"{plot}_Trigger_up"]["QCD1200to1500"]+bgPlotWeights[f"{plot}_Trigger_up"]["QCD1500to2000"]+bgPlotWeights[f"{plot}_Trigger_up"]["QCD2000"]
        bgPlotWeights[f"{plot}_Trigger_down"]["QCD"] = bgPlotWeights[f"{plot}_Trigger_down"]["QCD40to70"]+bgPlotWeights[f"{plot}_Trigger_down"]["QCD70to100"]+bgPlotWeights[f"{plot}_Trigger_down"]["QCD100to200"]+bgPlotWeights[f"{plot}_Trigger_down"]["QCD200to400"]+bgPlotWeights[f"{plot}_Trigger_down"]["QCD400to600"]+bgPlotWeights[f"{plot}_Trigger_down"]["QCD600to800"]+bgPlotWeights[f"{plot}_Trigger_down"]["QCD800to1000"]+bgPlotWeights[f"{plot}_Trigger_down"]["QCD1000to1200"]+bgPlotWeights[f"{plot}_Trigger_down"]["QCD1200to1500"]+bgPlotWeights[f"{plot}_Trigger_down"]["QCD1500to2000"]+bgPlotWeights[f"{plot}_Trigger_down"]["QCD2000"]
        bgPlotWeights[plot]["TTbar"] = bgPlotWeights[plot]["TTTo4Q"]+bgPlotWeights[plot]["TTToLNu2Q"]
        bgPlotWeights[f"{plot}_squared"]["TTbar"] = bgPlotWeights[f"{plot}_squared"]["TTTo4Q"]+bgPlotWeights[f"{plot}_squared"]["TTToLNu2Q"]
        bgPlotWeights[f"{plot}_PU_up"]["TTbar"] = bgPlotWeights[f"{plot}_PU_up"]["TTTo4Q"]+bgPlotWeights[f"{plot}_PU_up"]["TTToLNu2Q"]
        bgPlotWeights[f"{plot}_PU_down"]["TTbar"] = bgPlotWeights[f"{plot}_PU_down"]["TTTo4Q"]+bgPlotWeights[f"{plot}_PU_down"]["TTToLNu2Q"]
        bgPlotWeights[f"{plot}_Trigger_up"]["TTbar"] = bgPlotWeights[f"{plot}_Trigger_up"]["TTTo4Q"]+bgPlotWeights[f"{plot}_Trigger_up"]["TTToLNu2Q"]
        bgPlotWeights[f"{plot}_Trigger_down"]["TTbar"] = bgPlotWeights[f"{plot}_Trigger_down"]["TTTo4Q"]+bgPlotWeights[f"{plot}_Trigger_down"]["TTToLNu2Q"]

    for plot in plotDict.keys():
        sigPlotWeights[plot]["2024"] = sigPlotWeights[plot]["2024C"]+sigPlotWeights[plot]["2024D"]+sigPlotWeights[plot]["2024E"]+sigPlotWeights[plot]["2024F"]+sigPlotWeights[plot]["2024G"]+sigPlotWeights[plot]["2024H"]+sigPlotWeights[plot]["2024I"]
        sigPlotWeights[f"{plot}_squared"]["2024"] = sigPlotWeights[f"{plot}_squared"]["2024C"]+sigPlotWeights[f"{plot}_squared"]["2024D"]+sigPlotWeights[f"{plot}_squared"]["2024E"]+sigPlotWeights[f"{plot}_squared"]["2024F"]+sigPlotWeights[f"{plot}_squared"]["2024G"]+sigPlotWeights[f"{plot}_squared"]["2024H"]+sigPlotWeights[f"{plot}_squared"]["2024I"]
        sigPlotWeights[plot]["CDEFHI"] = sigPlotWeights[plot]["2024C"]+sigPlotWeights[plot]["2024D"]+sigPlotWeights[plot]["2024E"]+sigPlotWeights[plot]["2024F"]+sigPlotWeights[plot]["2024H"]+sigPlotWeights[plot]["2024I"]


    # **Plotting**
    for plot, binning in plotDict.items():
        if plot not in bgPlotWeights:
            print(f"Skipping {plot} (no data).")
            continue

        bins = np.linspace(binning[0], binning[1], binning[2])
        bgIntegral = (bins[1] - bins[0]) * sum(bgPlotWeights[plot]["QCD"] + bgPlotWeights[plot]["TTbar"])
        #bgIntegral = 1

        fig, (ax, rax) = plt.subplots(2, 1, figsize=[12,12], gridspec_kw={"height_ratios": [3,1]}, sharex=True)
        fig.subplots_adjust(hspace=0.06)
        ax.hist([(bins[:-1] + bins[1:]) / 2]*2,weights=[list(bgPlotWeights[plot]["TTbar"]),list(bgPlotWeights[plot]["QCD"])],
                stacked=True, density=True, label=[r"$t\bar{t}$","QCD"], bins=bins)

        # Background (MC) values and statistical uncertainties
        bgValues = (bgPlotWeights[plot]["QCD"] / bgIntegral) + (bgPlotWeights[plot]["TTbar"] / bgIntegral)
        bgErrors_stat = np.sqrt(bgPlotWeights[f"{plot}_squared"]["QCD"] / (bgIntegral**2) + \
                                bgPlotWeights[f"{plot}_squared"]["TTbar"] / (bgIntegral**2))

        ax.errorbar(((bins[:-1] + bins[1:]) / 2), bgValues, yerr=bgErrors_stat, linestyle="none", color="purple")

        # Compute PU systematic uncertainty (asymmetric)
        bg_PU_up = (bgPlotWeights[f"{plot}_PU_up"]["QCD"] / bgIntegral) + (bgPlotWeights[f"{plot}_PU_up"]["TTbar"] / bgIntegral)
        bg_PU_down = (bgPlotWeights[f"{plot}_PU_down"]["QCD"] / bgIntegral) + (bgPlotWeights[f"{plot}_PU_down"]["TTbar"] / bgIntegral)

        bg_Trigger_up = (bgPlotWeights[f"{plot}_Trigger_up"]["QCD"] / bgIntegral) + (bgPlotWeights[f"{plot}_Trigger_up"]["TTbar"] / bgIntegral)
        bg_Trigger_down = (bgPlotWeights[f"{plot}_Trigger_down"]["QCD"] / bgIntegral) + (bgPlotWeights[f"{plot}_Trigger_down"]["TTbar"] / bgIntegral)

        # Systematic deviations from nominal
        sys_PU_up = bg_PU_up - bgValues
        sys_PU_down = bg_PU_down - bgValues

        sys_Trigger_up = bg_Trigger_up - bgValues
        sys_Trigger_down = bg_Trigger_down - bgValues

        # Upper error: maximum positive deviation
        bgErrors_sys_PU_up = np.maximum.reduce([sys_PU_up, sys_PU_down, np.zeros_like(bgValues)])
        bgErrors_sys_Trigger_up = np.maximum.reduce([sys_Trigger_up, sys_Trigger_down, np.zeros_like(bgValues)])

        # Lower error: maximum negative deviation (take absolute value)
        bgErrors_sys_PU_down = np.abs(np.minimum.reduce([sys_PU_up, sys_PU_down, np.zeros_like(bgValues)]))
        bgErrors_sys_Trigger_down = np.abs(np.minimum.reduce([sys_Trigger_up, sys_Trigger_down, np.zeros_like(bgValues)]))

        # Total MC uncertainty (stat + sys), asymmetric
        bgErrors_total_up = np.sqrt(bgErrors_stat**2 + bgErrors_sys_PU_up**2 + bgErrors_sys_Trigger_up**2)
        bgErrors_total_down = np.sqrt(bgErrors_stat**2 + bgErrors_sys_PU_down**2 + bgErrors_sys_Trigger_down**2)

        colors = {"2024": "black"}
        for signal, color in colors.items():
            if plot not in sigPlotWeights or signal not in sigPlotWeights[plot]:
                print(f"Skipping {signal} in {plot} (no data).")
                continue

            integral = (bins[1] - bins[0]) * sum(sigPlotWeights[plot][signal])
            #integral = 1
            ax.hist(((bins[:-1] + bins[1:]) / 2), weights=list(sigPlotWeights[plot][signal]),
                    stacked=False, density=True, label="Data", bins=bins, histtype="step", color=color)

            # Signal (Data) values and statistical uncertainties
            sigValues = sigPlotWeights[plot][signal] / integral
            sigErrors = np.sqrt(sigPlotWeights[f"{plot}_squared"][signal] / (integral**2))

            ax.errorbar(((bins[:-1] + bins[1:]) / 2), sigValues, yerr=sigErrors, linestyle="none", color=color)

            # Ratio with DATA statistical uncertainty only (assuming zero MC uncertainty)
            ratioValues = sigValues / bgValues
            ratioErrors_data = sigErrors / bgValues  # Only data stat uncertainty

            # MC relative uncertainties for bands (asymmetric)
            mc_stat_rel = bgErrors_stat / bgValues
            mc_total_rel_up = bgErrors_total_up / bgValues
            mc_total_rel_down = bgErrors_total_down / bgValues

            # Create step arrays for proper bin alignment
            bin_edges_step = np.repeat(bins, 2)[1:-1]
            mc_stat_rel_step = np.repeat(mc_stat_rel, 2)
            mc_total_rel_up_step = np.repeat(mc_total_rel_up, 2)
            mc_total_rel_down_step = np.repeat(mc_total_rel_down, 2)

            # Plot data points with data stat only
            rax.errorbar(((bins[:-1] + bins[1:]) / 2), ratioValues, yerr=ratioErrors_data, 
                        linestyle="none", color=color, marker=".", label="Data", zorder=3)

            # Inner band: MC stat only (hatched, symmetric)
            rax.fill_between(bin_edges_step, 1 - mc_stat_rel_step, 1 + mc_stat_rel_step, 
                            alpha=0.5, color='gray', hatch='///', 
                            edgecolor='gray', label='MC stat', linewidth=0, zorder=1)

            # Outer band: MC stat + sys (asymmetric)
            rax.fill_between(bin_edges_step, 1 - mc_total_rel_down_step, 1 + mc_total_rel_up_step,
                            alpha=0.3, color='blue', label='MC stat $\\oplus$ sys', linewidth=0, zorder=2)

        # Calculate maximum value for y-limit
        #max_ratio_data = np.nanmax(ratioValues + ratioErrors_data)
        #max_ratio_band = np.nanmax(1 + mc_total_rel_up)
        #max_ratio = max(max_ratio_data, max_ratio_band)

        rax.hlines(1, bins[0], bins[-1], linestyle="dashed", color='black', linewidth=1)
        rax.set_ylabel("Data/MC")
        #rax.set_xlabel(plot)
        if "scoutVert_nTracks" in plot:
            rax.set_xlabel("Vertex Track Multiplicity")
        else:
            rax.set_xlabel(plot)
        rax.legend(fontsize=16,labelspacing=0.25,ncol=3)
        rax.set_ylim(0,2)
        hep.cms.label("Work in progress", loc=0, ax=ax, com=13.6, fontsize=16,data=True)
        ax.set_ylabel("A.U")
        ax.legend(fontsize=16,labelspacing=0.25)
        ax.set_yscale("log")

        plt.savefig(f"{plot}_datamc.pdf", bbox_inches='tight')
    
if __name__=="__main__":
    main()
