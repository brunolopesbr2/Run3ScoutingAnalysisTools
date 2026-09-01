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
    "scoutVert_mass": [0.3,0.7,11],
    "scoutVert_dBV": [0.01,2,11],
    "scoutVert_pt": [2,40,16],
    "scoutVert_eta": [-2.4,2.4,26],
    #"scoutVert_costh2": [0.8,1,21],
    #"scoutVert_ctau": [0.0,0.5,21],
    #"scoutVert_dBVErr": [0,0.1,101],
    #"scoutVert_nTracks": [0,10,11], "scoutVert_chi2": [0,7,50],
    #"scoutVert_dT": [0,0.5,101], "scoutVert_cosT": [-1,1,101],
    #"muon_phi": [-3.142,3.142,21]
    #"vertTrack_dxy": [0,0.3,51]
}

def process_root_file(args):
    rootFile, process = args
    print(f"Processing {rootFile}")

    output = {}
    genWeightSum = 0
    with uproot.open(rootFile) as file:
        isMC = True
        if("2024" in process):
            isMC = False
        output["genWeightSum"] = {}
        genWeightSum = file["K0Filter/genWeightsSkim"].values()[0]
        tree = file["K0Tree/objectTree"]

        # Select only necessary branches to load
        branches = list(plotDict.keys()) + ["vertTrack_iVtx", "scoutVert_dBV", "weight","scoutVert_nTracks","scoutVert_dBV","scoutVert_mass","scoutVert_costh2","scoutVert_ctau","scoutVert_chi2","scoutVert_pt","muon_phi","dimuon_mass"]
        if(isMC):
            branches = branches + ["uncorrectedWeight","weight_PU_BCDEFGHI_nominal", "weight_PU_BCDEFGHI_up", "weight_PU_BCDEFGHI_down"] 
        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        for batch in tree.iterate(branches, library="ak", step_size=40000):
            if(isMC):
                weights = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] #* (13.35/109.99)#(7.62/109.99)#* batch["weight_trigger_nominal"]
                weights_PU_up = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_up"] #* (13.35/109.99)#(7.62/109.99)#* batch["weight_trigger_nominal"]
                weights_PU_down = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_down"] #* (13.35/109.99)#(7.62/109.99)#* batch["weight_trigger_nominal"]
            else:
                weights = ak.ones_like(batch["weight"])
            '''
            if(process=="TTToLNu2Q"):
                weights = weights * 0.439
                weights_PU_up = weights_PU_up * 0.439
                weights_PU_down = weights_PU_down * 0.439
            if(process=="TTTo4Q"):
                weights = weights * 0.455
                weights_PU_up = weights_PU_up * 0.455
                weights_PU_down = weights_PU_down * 0.455
            if(process=="TTTo2L2Nu"):
                weights = weights * 0.106
                weights_PU_up = weights_PU_up * 0.106
                weights_PU_down = weights_PU_down * 0.106
            '''
            if(isMC): 
                weights = weights / genWeightSum
                weights_PU_up = weights_PU_up / genWeightSum
                weights_PU_down = weights_PU_down / genWeightSum
            for plot, binning in plotDict.items():
                bins = np.linspace(binning[0], binning[1], binning[2])
                data = batch[plot]
                
                # Apply displacement cut
                if "vertTrack" in plot:
                    mask = (batch["scoutVert_dBV"][batch["vertTrack_iVtx"]] >= 0.01) & (batch["scoutVert_dBV"][batch["vertTrack_iVtx"]] < 2.0) #& (batch["scoutVert_dBVErr"][batch["vertTrack_iVtx"]] < 0.005) & (batch["scoutVert_nTracks"][batch["vertTrack_iVtx"]] > 4)
                elif "scoutVert" in plot:
                    mask = (batch["scoutVert_dBV"] >= 0.01) & (batch["scoutVert_dBV"] < 2.0) & (batch["scoutVert_ctau"] >= 0.0268) & (batch["scoutVert_costh2"] > 0.9) & (batch["scoutVert_pt"]  > 2) & (batch["scoutVert_chi2"]  < 7)
                elif "scoutTrack" in plot:
                    mask = (batch["scoutTrack_dxySig"] > 4) & (batch["scoutTrack_pt"] > 1.0) & (batch["scoutTrack_nValidPixelHits"] > 2) & (batch["scoutTrack_nValidStripHits"] > 1) & (batch["scoutTrack_nTrackerLayersWithMeasurement"] > 5) & (abs(batch["scoutTrack_eta"])<2.4) #& (batch["scoutTrack_iJet"]!=-1)
                    #mask = (batch["scoutTrack_pt"] > 1.0) & (batch["scoutTrack_nValidPixelHits"] > 2) & (batch["scoutTrack_nValidStripHits"] > 1) & (batch["scoutTrack_nTrackerLayersWithMeasurement"] > 5) & (abs(batch["scoutTrack_eta"])<2.4)
                elif "muon" in plot:
                    mask = (ak.num(batch["muon_phi"],axis=1)==2)
                else:
                    mask = ak.ones_like(data, dtype=bool)
                data = data[mask]
                
                mask = (ak.num(batch["muon_phi"],axis=1)>=2) & (ak.any((batch["dimuon_mass"]>70) & (batch["dimuon_mass"]<110),axis=1))
                data = data[mask]
                #Test to see if requiring two muons helps data/MC
                weightsMasked=weights[mask]
                if(isMC):
                    weightsMasked_PU_up=weights_PU_up[mask]
                    weightsMasked_PU_down=weights_PU_down[mask]
                broadcastWeights, data = ak.broadcast_arrays(weightsMasked,data)
                if(isMC):
                    broadcastWeights_PU_up, data = ak.broadcast_arrays(weightsMasked_PU_up,data)
                    broadcastWeights_PU_down, data = ak.broadcast_arrays(weightsMasked_PU_down,data)
                
                # Apply mask and flatten data
                data = ak.flatten(data,axis=None)
                data = np.clip(data,bins[0],bins[-1])
                weights_filtered = ak.flatten(broadcastWeights,axis=None)
                if(isMC):
                    weights_filtered_PU_up = ak.flatten(broadcastWeights_PU_up,axis=None)
                    weights_filtered_PU_down = ak.flatten(broadcastWeights_PU_down,axis=None)
                # Compute histograms
                n, _ = np.histogram(data, weights=weights_filtered, bins=bins)
                n_2, _ = np.histogram(data, weights=weights_filtered**2, bins=bins)
                if(isMC):
                    n_PU_up, _ = np.histogram(data, weights=weights_filtered_PU_up, bins=bins)
                    n_PU_down, _ = np.histogram(data, weights=weights_filtered_PU_down, bins=bins)
                if plot not in output:
                    output[plot] = {process: n}
                    output[f"{plot}_squared"] = {process: n_2}
                    if(isMC):
                        output[f"{plot}_PU_up"] = {process: n_PU_up}
                        output[f"{plot}_PU_down"] = {process: n_PU_down}
                else:
                    output[plot][process] = output[plot][process] + n
                    output[f"{plot}_squared"][process] = output[f"{plot}_squared"][process] + n_2
                    if(isMC):
                        output[f"{plot}_PU_up"][process] = output[f"{plot}_PU_up"][process] + n_PU_up
                        output[f"{plot}_PU_down"][process] = output[f"{plot}_PU_down"][process] + n_PU_down
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
    signalDict, processDict = makeDict("v4-K0",["2024"],["QCD","DY","Wto","WW","WZ","ZZ","TTTo"])
    bgPlotWeights = parallel_processing(processDict)
    sigPlotWeights = parallel_processing(signalDict)

    legendStrings = ["Mu QCD","EM QCD","bcToE QCD","DY","WtoLNu","Diboson","TTbar"]
    #legendStrings = ["QCD","DY","WtoLNu","Diboson","TTbar"]
    #Combining Background Subprocesses and Reweighting Events
    for plot in plotDict.keys():
        processes = list(bgPlotWeights[plot].keys())
        firstFile = True
        for string in legendStrings:
            bgPlotWeights[plot][string] = ak.zeros_like(bgPlotWeights[plot]["TTTo4Q"])
            bgPlotWeights[f"{plot}_PU_up"][string] = ak.zeros_like(bgPlotWeights[plot]["TTTo4Q"])
            bgPlotWeights[f"{plot}_PU_down"][string] = ak.zeros_like(bgPlotWeights[plot]["TTTo4Q"])
            bgPlotWeights[f"{plot}_squared"][string] = ak.zeros_like(bgPlotWeights[plot]["TTTo4Q"])
        for process in bgPlotWeights["genWeightSum"].keys():
            bgPlotWeights[plot][process] = bgPlotWeights[plot][process] / bgPlotWeights["genWeightSum"][process]
            bgPlotWeights[f"{plot}_PU_up"][process] = bgPlotWeights[f"{plot}_PU_up"][process] / bgPlotWeights["genWeightSum"][process]
            bgPlotWeights[f"{plot}_PU_down"][process] = bgPlotWeights[f"{plot}_PU_down"][process] / bgPlotWeights["genWeightSum"][process]
            bgPlotWeights[f"{plot}_squared"][process] = bgPlotWeights[f"{plot}_squared"][process] / (bgPlotWeights["genWeightSum"][process]**2)
        for process in processes:
            if(firstFile):
                bgPlotWeights[plot]["MC"] = bgPlotWeights[plot][process]
                bgPlotWeights[f"{plot}_PU_up"]["MC"] = bgPlotWeights[f"{plot}_PU_up"][process]
                bgPlotWeights[f"{plot}_PU_down"]["MC"] = bgPlotWeights[f"{plot}_PU_down"][process]
                bgPlotWeights[f"{plot}_squared"]["MC"] = bgPlotWeights[f"{plot}_squared"][process]
                firstFile = False
            else:
                bgPlotWeights[plot]["MC"] = bgPlotWeights[plot]["MC"] + bgPlotWeights[plot][process]
                bgPlotWeights[f"{plot}_PU_up"]["MC"] = bgPlotWeights[f"{plot}_PU_up"]["MC"] + bgPlotWeights[f"{plot}_PU_up"][process]
                bgPlotWeights[f"{plot}_PU_down"]["MC"] = bgPlotWeights[f"{plot}_PU_down"]["MC"] + bgPlotWeights[f"{plot}_PU_down"][process]
                bgPlotWeights[f"{plot}_squared"]["MC"] = bgPlotWeights[f"{plot}_squared"]["MC"] + bgPlotWeights[f"{plot}_squared"][process]
    #         if("MuEnriched" in process) or ("EMEnriched" in process) or ("bcToE" in process):
    #             bgPlotWeights[plot]["QCD"] = bgPlotWeights[plot]["QCD"] + bgPlotWeights[plot][process]
    #             bgPlotWeights[f"{plot}_PU_up"]["QCD"] = bgPlotWeights[f"{plot}_PU_up"]["QCD"] + bgPlotWeights[f"{plot}_PU_up"][process]
    #             bgPlotWeights[f"{plot}_PU_down"]["QCD"] = bgPlotWeights[f"{plot}_PU_down"]["QCD"] + bgPlotWeights[f"{plot}_PU_down"][process]
    #             bgPlotWeights[f"{plot}_squared"]["QCD"] = bgPlotWeights[f"{plot}_squared"]["QCD"] + bgPlotWeights[f"{plot}_squared"][process]
            if("MuEnriched" in process):
                bgPlotWeights[plot]["Mu QCD"] = bgPlotWeights[plot]["Mu QCD"] + bgPlotWeights[plot][process]
                bgPlotWeights[f"{plot}_PU_up"]["Mu QCD"] = bgPlotWeights[f"{plot}_PU_up"]["Mu QCD"] + bgPlotWeights[f"{plot}_PU_up"][process]
                bgPlotWeights[f"{plot}_PU_down"]["Mu QCD"] = bgPlotWeights[f"{plot}_PU_down"]["Mu QCD"] + bgPlotWeights[f"{plot}_PU_down"][process]
                bgPlotWeights[f"{plot}_squared"]["Mu QCD"] = bgPlotWeights[f"{plot}_squared"]["Mu QCD"] + bgPlotWeights[f"{plot}_squared"][process]
            elif("EMEnriched" in process):
                bgPlotWeights[plot]["EM QCD"] = bgPlotWeights[plot]["EM QCD"] + bgPlotWeights[plot][process]
                bgPlotWeights[f"{plot}_PU_up"]["EM QCD"] = bgPlotWeights[f"{plot}_PU_up"]["EM QCD"] + bgPlotWeights[f"{plot}_PU_up"][process]
                bgPlotWeights[f"{plot}_PU_down"]["EM QCD"] = bgPlotWeights[f"{plot}_PU_down"]["EM QCD"] + bgPlotWeights[f"{plot}_PU_down"][process]
                bgPlotWeights[f"{plot}_squared"]["EM QCD"] = bgPlotWeights[f"{plot}_squared"]["EM QCD"] + bgPlotWeights[f"{plot}_squared"][process]
            elif("bcToE" in process):
                bgPlotWeights[plot]["bcToE QCD"] = bgPlotWeights[plot]["bcToE QCD"] + bgPlotWeights[plot][process]
                bgPlotWeights[f"{plot}_PU_up"]["bcToE QCD"] = bgPlotWeights[f"{plot}_PU_up"]["bcToE QCD"] + bgPlotWeights[f"{plot}_PU_up"][process]
                bgPlotWeights[f"{plot}_PU_down"]["bcToE QCD"] = bgPlotWeights[f"{plot}_PU_down"]["bcToE QCD"] + bgPlotWeights[f"{plot}_PU_down"][process]
                bgPlotWeights[f"{plot}_squared"]["bcToE QCD"] = bgPlotWeights[f"{plot}_squared"]["bcToE QCD"] + bgPlotWeights[f"{plot}_squared"][process]
            elif("DYto" in process):
                bgPlotWeights[plot]["DY"] = bgPlotWeights[plot]["DY"] + bgPlotWeights[plot][process]
                bgPlotWeights[f"{plot}_PU_up"]["DY"] = bgPlotWeights[f"{plot}_PU_up"]["DY"] + bgPlotWeights[f"{plot}_PU_up"][process]
                bgPlotWeights[f"{plot}_PU_down"]["DY"] = bgPlotWeights[f"{plot}_PU_down"]["DY"] + bgPlotWeights[f"{plot}_PU_down"][process]
                bgPlotWeights[f"{plot}_squared"]["DY"] = bgPlotWeights[f"{plot}_squared"]["DY"] + bgPlotWeights[f"{plot}_squared"][process]
            elif("WToLNu" in process):
                bgPlotWeights[plot]["WtoLNu"] = bgPlotWeights[plot]["WtoLNu"] + bgPlotWeights[plot][process]
                bgPlotWeights[f"{plot}_PU_up"]["WtoLNu"] = bgPlotWeights[f"{plot}_PU_up"]["WtoLNu"] + bgPlotWeights[f"{plot}_PU_up"][process]
                bgPlotWeights[f"{plot}_PU_down"]["WtoLNu"] = bgPlotWeights[f"{plot}_PU_down"]["WtoLNu"] + bgPlotWeights[f"{plot}_PU_down"][process]
                bgPlotWeights[f"{plot}_squared"]["WtoLNu"] = bgPlotWeights[f"{plot}_squared"]["WtoLNu"] + bgPlotWeights[f"{plot}_squared"][process]
            elif(("WW" in process) or ("WZ" in process) or ("ZZ" in process)):
                bgPlotWeights[plot]["Diboson"] = bgPlotWeights[plot]["Diboson"] + bgPlotWeights[plot][process]
                bgPlotWeights[f"{plot}_PU_up"]["Diboson"] = bgPlotWeights[f"{plot}_PU_up"]["Diboson"] + bgPlotWeights[f"{plot}_PU_up"][process]
                bgPlotWeights[f"{plot}_PU_down"]["Diboson"] = bgPlotWeights[f"{plot}_PU_down"]["Diboson"] + bgPlotWeights[f"{plot}_PU_down"][process]
                bgPlotWeights[f"{plot}_squared"]["Diboson"] = bgPlotWeights[f"{plot}_squared"]["Diboson"] + bgPlotWeights[f"{plot}_squared"][process]
            elif("TTTo" in process):
                bgPlotWeights[plot]["TTbar"] = bgPlotWeights[plot]["TTbar"] + bgPlotWeights[plot][process]
                bgPlotWeights[f"{plot}_PU_up"]["TTbar"] = bgPlotWeights[f"{plot}_PU_up"]["TTbar"] + bgPlotWeights[f"{plot}_PU_up"][process]
                bgPlotWeights[f"{plot}_PU_down"]["TTbar"] = bgPlotWeights[f"{plot}_PU_down"]["TTbar"] + bgPlotWeights[f"{plot}_PU_down"][process]
                bgPlotWeights[f"{plot}_squared"]["TTbar"] = bgPlotWeights[f"{plot}_squared"]["TTbar"] + bgPlotWeights[f"{plot}_squared"][process]

    #for sample, array in bgPlotWeights["scoutVert_mass"].items():
    #    print(sample,array[0])
    #FIX ME: commenting out other eras until they finish

    for plot in plotDict.keys():
        sigPlotWeights[plot]["2024"] = sigPlotWeights[plot]["2024C"]+sigPlotWeights[plot]["2024D"]+sigPlotWeights[plot]["2024E"]+sigPlotWeights[plot]["2024F"]+sigPlotWeights[plot]["2024G"]+sigPlotWeights[plot]["2024H"]+sigPlotWeights[plot]["2024I"]
        sigPlotWeights[f"{plot}_squared"]["2024"] = sigPlotWeights[f"{plot}_squared"]["2024C"]+sigPlotWeights[f"{plot}_squared"]["2024D"]+sigPlotWeights[f"{plot}_squared"]["2024E"]+sigPlotWeights[f"{plot}_squared"]["2024F"]+sigPlotWeights[f"{plot}_squared"]["2024G"]+sigPlotWeights[f"{plot}_squared"]["2024H"]+sigPlotWeights[f"{plot}_squared"]["2024I"]    
    # **Plotting**
    for plot, binning in plotDict.items():
        if plot not in bgPlotWeights:
            print(f"Skipping {plot} (no data).")
            continue
        bins = np.linspace(binning[0], binning[1], binning[2])
        bgIntegral = (bins[1] - bins[0]) * sum(bgPlotWeights[plot]["MC"])
        #bgIntegral = 1

        fig, (ax, rax) = plt.subplots(2, 1, figsize=[12,12], gridspec_kw={"height_ratios": [3,1]}, sharex=True)
        fig.subplots_adjust(hspace=0.06)
        #legendStringNoQCD = ["DY","WtoLNu","Diboson","TTbar"]
        ax.hist([(bins[:-1] + bins[1:]) / 2]*len(legendStrings),weights=[list(bgPlotWeights[plot][string]) for string in legendStrings], stacked=True, density=True, label=legendStrings, bins=bins)
        #ax.hist((bins[:-1] + bins[1:]) / 2,weights=bgPlotWeights[plot]["QCD"], stacked=False, density=True, label="QCD", bins=bins,histtype="step")
        # Background (MC) values and statistical uncertainties
        bgValues = (bgPlotWeights[plot]["MC"] / bgIntegral)
        bgErrors_stat = np.sqrt(bgPlotWeights[f"{plot}_squared"]["MC"] / (bgIntegral**2))

        ax.errorbar(((bins[:-1] + bins[1:]) / 2), bgValues, yerr=bgErrors_stat, linestyle="none", color="purple")

        # Compute PU systematic uncertainty (asymmetric)
        bg_PU_up = (bgPlotWeights[f"{plot}_PU_up"]["MC"] / bgIntegral)
        bg_PU_down = (bgPlotWeights[f"{plot}_PU_down"]["MC"] / bgIntegral)

        # Systematic deviations from nominal
        sys_PU_up = bg_PU_up - bgValues
        sys_PU_down = bg_PU_down - bgValues

        # Upper error: maximum positive deviation
        bgErrors_sys_PU_up = np.maximum.reduce([sys_PU_up, sys_PU_down, np.zeros_like(bgValues)])

        # Lower error: maximum negative deviation (take absolute value)
        bgErrors_sys_PU_down = np.abs(np.minimum.reduce([sys_PU_up, sys_PU_down, np.zeros_like(bgValues)]))

        # Total MC uncertainty (stat + sys), asymmetric
        bgErrors_total_up = np.sqrt(bgErrors_stat**2 + bgErrors_sys_PU_up**2)
        bgErrors_total_down = np.sqrt(bgErrors_stat**2 + bgErrors_sys_PU_down**2)

        colors = {"2024": "black"}
        for signal, color in colors.items():
            if plot not in sigPlotWeights or signal not in sigPlotWeights[plot]:
                print(f"Skipping {signal} in {plot} (no data).")
                continue

            integral = (bins[1] - bins[0]) * sum(sigPlotWeights[plot][signal])
            #integral = 1
            ax.hist(((bins[:-1] + bins[1:]) / 2), weights=list(sigPlotWeights[plot][signal]),
                    stacked=False, density=True, label=signal, bins=bins, histtype="step", color=color)

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
        rax.set_xlabel(plot)
        rax.legend(loc='best', fontsize=10,ncol=3)
        rax.set_ylim(0.7,1.3)

        ax.set_ylabel("A.U")
        ax.legend(fontsize=10)
        ax.set_yscale("log")

        plt.savefig(f"{plot}_datamc.pdf", bbox_inches='tight')
    
if __name__=="__main__":
    main()
