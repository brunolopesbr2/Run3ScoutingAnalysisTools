from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")

errCuts = np.linspace(0.005,0.02,4)[::-1]
errCuts = np.append(errCuts,[0.004,0.003,0.002,0.001])
nTrackCuts = np.linspace(3,12,10)
shiftCuts = np.linspace(999.9,999.9,1)

def fast_count_vertices_numpy(ivtxMasked, dBV):
    # Get the number of vertices per event (length of each dBV event)
    n_vertices = ak.num(dBV)
    
    # Create flat indices for all events
    # This creates [0,1,2,...,n_vertices[0]-1, 0,1,2,...,n_vertices[1]-1, ...]
    flat_indices = ak.local_index(dBV, axis=1)
    
    # Flatten the ivtxMasked to work with all events at once
    flat_ivtx = ak.flatten(ivtxMasked)
    
    # Create event indices for each element in flat_ivtx
    event_idx = np.repeat(np.arange(len(ivtxMasked)), ak.num(ivtxMasked))
    
    # Calculate cumulative offsets for each event
    offsets = np.concatenate([[0], np.cumsum(n_vertices[:-1])])
    
    # Adjust indices to global flat array
    global_indices = flat_ivtx + offsets[event_idx]
    
    # Count using bincount
    total_vertices = np.sum(n_vertices)
    counts_flat = np.bincount(global_indices, minlength=total_vertices)
    
    # Unflatten back to jagged structure
    return ak.unflatten(counts_flat, n_vertices)

def process_root_file(args):
    rootFile, process = args
    print(f"Processing {rootFile}")

    output = {}
    with uproot.open(rootFile) as file:
        output["genWeightSum"] = {process: file["triggerFilter/genWeightsSkim"].values()[0]}
        output["weightSkimSum"] = {process: file["triggerFilter/weightsSkim"].values()[0]}
        tree = file["scoutingTree/objectTree"]
        # Select only necessary branches to load
        branches = ["weight","scoutVert_dBV","scoutVert_dBVErr","scoutVert_cosT","vertTrack_iVtx","vertTrack_shift3DValue"]
        weightSum = np.zeros((len(shiftCuts),len(errCuts),len(nTrackCuts)))
        weightSumSquared = np.zeros((len(shiftCuts),len(errCuts),len(nTrackCuts)))
        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        for batch in tree.iterate(branches, library="ak", step_size=100000):
            weights = batch["weight"]  # event weights   
            mask = (batch["scoutVert_dBV"][batch["vertTrack_iVtx"]] >= 0.01) & (batch["scoutVert_dBV"][batch["vertTrack_iVtx"]] < 2) & (batch["scoutVert_cosT"][batch["vertTrack_iVtx"]] > 0)
            shift = batch["vertTrack_shift3DValue"][mask]
            ivtx = batch["vertTrack_iVtx"][mask]
            
            shiftMasks = [(shift < shiftCuts[b]) for b in range(len(shiftCuts))]
            
            dBV = batch["scoutVert_dBV"]
            dBVErr = batch["scoutVert_dBVErr"]
            cosT = batch["scoutVert_cosT"]
            dBVMask = (dBV >= 0.01) & (dBV < 2) & (cosT>0)
            dBVErrMask = [(dBVErr < errCuts[m]) for m in range(len(errCuts))]
            
            for b in range(len(shiftCuts)):
                mask = shiftMasks[b]
                ivtxMasked = ivtx[mask]
                ntracks = fast_count_vertices_numpy(ivtxMasked, dBV)
                ntrackMasks = [(ntracks > nTrackCuts[n]) for n in range(len(nTrackCuts))]
                for m in range(len(errCuts)):
                    for n in range(len(nTrackCuts)):
                        mask = dBVMask & dBVErrMask[m] & ntrackMasks[n]
                        dBVMasked = dBV[mask]
                        mask = ak.num(dBVMasked,axis=1)>0
                        weightsMasked = weights[mask]
                        weightSum[b][m][n] += ak.sum(weightsMasked)
                        weightSumSquared[b][m][n] += ak.sum(weightsMasked**2)
        output["weightSum"] = {process: weightSum}
        output["weightSumSquared"] = {process: weightSumSquared}
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
                        if process not in results[plot]:
                             results[plot][process] = result[plot][process]
                        else:
                            results[plot][process] = results[plot][process] + result[plot][process]

    return results

def main():
    limitDict = build_limits("../EXO-23-13-ExoHiggsBRLimitvsLifetime.root","../EXO-19-13-RPVSUSYSigmaBSquaredLimitsMassvsLifetime.root")
    signalDict, processDict = makeDict("v22-Optimized",["Stop-M","Hto2Sto4D"],["QCD","TTTo"])
    bgPlotWeights = parallel_processing(processDict)
    sigPlotWeights = parallel_processing(signalDict)
    bestEfficiencySensitivity = {"Stop-M200-cT1": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M400-cT1": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M600-cT1": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M800-cT1": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M200-cT3": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M400-cT3": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M600-cT3": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M800-cT3": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M200-cT10": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M400-cT10": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M600-cT10": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M800-cT10": [0,0,0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS1": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS7": [0,0,0,0,0,0,0,0,0,0],"Hto2Sto4D-cT1-MS15": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS23": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS30": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS40": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS55": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS1": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS7": [0,0,0,0,0,0,0,0,0,0],"Hto2Sto4D-cT0p1-MS15": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS23": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS30": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS40": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS55": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS1": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS7": [0,0,0,0,0,0,0,0,0,0],"Hto2Sto4D-cT10-MS15": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS23": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS30": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS40": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS55": [0,0,0,0,0,0,0,0,0,0]}
    bestTraditionalSensitivity = {"Stop-M200-cT1": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M400-cT1": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M600-cT1": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M800-cT1": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M200-cT3": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M400-cT3": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M600-cT3": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M800-cT3": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M200-cT10": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M400-cT10": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M600-cT10": [0,0,0,0,0,0,0,0,0,0,0,0], "Stop-M800-cT10": [0,0,0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS1": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS7": [0,0,0,0,0,0,0,0,0,0],"Hto2Sto4D-cT1-MS15": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS23": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS30": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS40": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT1-MS55": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS1": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS7": [0,0,0,0,0,0,0,0,0,0],"Hto2Sto4D-cT0p1-MS15": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS23": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS30": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS40": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT0p1-MS55": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS1": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS7": [0,0,0,0,0,0,0,0,0,0],"Hto2Sto4D-cT10-MS15": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS23": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS30": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS40": [0,0,0,0,0,0,0,0,0,0], "Hto2Sto4D-cT10-MS55": [0,0,0,0,0,0,0,0,0,0]}

    #Combining Background Subprocesses and Reweighting Events
    for process in bgPlotWeights["genWeightSum"].keys():
        bgPlotWeights["weightSum"][process] = bgPlotWeights["weightSum"][process] / bgPlotWeights["genWeightSum"][process]
        bgPlotWeights["weightSkimSum"][process] = bgPlotWeights["weightSkimSum"][process] / bgPlotWeights["genWeightSum"][process]
        bgPlotWeights["weightSumSquared"][process] = bgPlotWeights["weightSumSquared"][process] / (bgPlotWeights["genWeightSum"][process]**2)
    bgPlotWeights["weightSum"]["QCD"] = bgPlotWeights["weightSum"]["QCD40to70"]+bgPlotWeights["weightSum"]["QCD70to100"]+bgPlotWeights["weightSum"]["QCD100to200"]+bgPlotWeights["weightSum"]["QCD200to400"]+bgPlotWeights["weightSum"]["QCD400to600"]+bgPlotWeights["weightSum"]["QCD600to800"]+bgPlotWeights["weightSum"]["QCD800to1000"]+bgPlotWeights["weightSum"]["QCD1000to1200"]+bgPlotWeights["weightSum"]["QCD1200to1500"]+bgPlotWeights["weightSum"]["QCD1500to2000"]+bgPlotWeights["weightSum"]["QCD2000"]
    bgPlotWeights["weightSkimSum"]["QCD"] = bgPlotWeights["weightSkimSum"]["QCD40to70"]+bgPlotWeights["weightSkimSum"]["QCD70to100"]+bgPlotWeights["weightSkimSum"]["QCD100to200"]+bgPlotWeights["weightSkimSum"]["QCD200to400"]+bgPlotWeights["weightSkimSum"]["QCD400to600"]+bgPlotWeights["weightSkimSum"]["QCD600to800"]+bgPlotWeights["weightSkimSum"]["QCD800to1000"]+bgPlotWeights["weightSkimSum"]["QCD1000to1200"]+bgPlotWeights["weightSkimSum"]["QCD1200to1500"]+bgPlotWeights["weightSkimSum"]["QCD1500to2000"]+bgPlotWeights["weightSkimSum"]["QCD2000"]
    bgPlotWeights["weightSumSquared"]["QCD"] = bgPlotWeights["weightSumSquared"]["QCD40to70"]+bgPlotWeights["weightSumSquared"]["QCD70to100"]+bgPlotWeights["weightSumSquared"]["QCD100to200"]+bgPlotWeights["weightSumSquared"]["QCD200to400"]+bgPlotWeights["weightSumSquared"]["QCD400to600"]+bgPlotWeights["weightSumSquared"]["QCD600to800"]+bgPlotWeights["weightSumSquared"]["QCD800to1000"]+bgPlotWeights["weightSumSquared"]["QCD1000to1200"]+bgPlotWeights["weightSumSquared"]["QCD1200to1500"]+bgPlotWeights["weightSumSquared"]["QCD1500to2000"]+bgPlotWeights["weightSumSquared"]["QCD2000"]
    bgPlotWeights["weightSum"]["TTbar"] = bgPlotWeights["weightSum"]["TTTo4Q"]+bgPlotWeights["weightSum"]["TTToLNu2Q"]
    bgPlotWeights["weightSkimSum"]["TTbar"] = bgPlotWeights["weightSkimSum"]["TTTo4Q"]+bgPlotWeights["weightSkimSum"]["TTToLNu2Q"]
    bgPlotWeights["weightSumSquared"]["TTbar"] = bgPlotWeights["weightSumSquared"]["TTTo4Q"]+bgPlotWeights["weightSumSquared"]["TTToLNu2Q"]
    for process in sigPlotWeights["genWeightSum"].keys():
        sigPlotWeights["weightSum"][process] = sigPlotWeights["weightSum"][process] / sigPlotWeights["genWeightSum"][process]
        sigPlotWeights["weightSkimSum"][process] = sigPlotWeights["weightSkimSum"][process] / sigPlotWeights["genWeightSum"][process]
        sigPlotWeights["weightSumSquared"][process] = sigPlotWeights["weightSumSquared"][process] / (sigPlotWeights["genWeightSum"][process]**2)

    optimalCuts = {}
    sensitivityMatrices = {}
    # **Plotting**
    for lifetime in ["1","3","10"]:
        fig, ax = plt.subplots()
        colors = {"Stop-M200-cT"+lifetime: "black", "Stop-M400-cT"+lifetime: "red", "Stop-M600-cT"+lifetime: "blue", "Stop-M800-cT"+lifetime: "green"}
        for signal, color in colors.items():
            sensitivity = sigPlotWeights["weightSum"][signal] / np.sqrt(sigPlotWeights["weightSum"][signal]+bgPlotWeights["weightSum"]["QCD"]+bgPlotWeights["weightSum"]["TTbar"])
            sensitivity = np.nan_to_num(sensitivity)
            efficiency = sigPlotWeights["weightSum"][signal] / sigPlotWeights["weightSkimSum"][signal]
            fpr = (bgPlotWeights["weightSum"]["QCD"]+bgPlotWeights["weightSum"]["TTbar"]) / (bgPlotWeights["weightSkimSum"]["QCD"]+bgPlotWeights["weightSkimSum"]["TTbar"])
            if(np.max(sensitivity)>bestTraditionalSensitivity[signal][0]): 
                ind = np.unravel_index(np.argmax(sensitivity, axis=None), sensitivity.shape)
                bestTraditionalSensitivity[signal] = [np.max(sensitivity),efficiency[ind],fpr[ind],shiftCuts[ind[0]],errCuts[ind[1]],nTrackCuts[ind[2]]]
                optimalCuts[signal] = ind
                sensitivityMatrices[signal] = sensitivity
            sensitivity = efficiency / (1+np.sqrt(bgPlotWeights["weightSum"]["QCD"]+bgPlotWeights["weightSum"]["TTbar"]))
            if(np.max(sensitivity)>bestEfficiencySensitivity[signal][0]): 
                ind = np.unravel_index(np.argmax(sensitivity, axis=None), sensitivity.shape)
                bestEfficiencySensitivity[signal] = [np.max(sensitivity),efficiency[ind],fpr[ind],shiftCuts[ind[0]],errCuts[ind[1]],nTrackCuts[ind[2]]]
            ax.scatter(fpr,efficiency,label=signal,color=color,zorder=1)
            ax.scatter(fpr[ind],efficiency[ind],marker="s",color=color,zorder=2,edgecolor="yellow")
            plt.xscale("symlog",linthresh=10**-11)
        ax.set_ylabel("TPR")
        #ax.set_ylim(0.0,0.7)
        plt.xlabel("FPR")
        plt.legend()
        plt.savefig("15FPRStopEff"+lifetime+"_Merge3SigmaMinTV2.pdf")
        plt.clf()
        #plt.show()

    for lifetime in ["0p1","1","10"]:
        fig, ax = plt.subplots()
        colors = {"Hto2Sto4D-cT"+lifetime+"-MS1": "black", "Hto2Sto4D-cT"+lifetime+"-MS7": "purple", "Hto2Sto4D-cT"+lifetime+"-MS15": "red", "Hto2Sto4D-cT"+lifetime+"-MS23": "orange", "Hto2Sto4D-cT"+lifetime+"-MS30": "blue", "Hto2Sto4D-cT"+lifetime+"-MS40": "pink", "Hto2Sto4D-cT"+lifetime+"-MS55": "green"}
        for signal, color in colors.items():
            sensitivity = sigPlotWeights["weightSum"][signal] / np.sqrt(sigPlotWeights["weightSum"][signal]+bgPlotWeights["weightSum"]["QCD"]+bgPlotWeights["weightSum"]["TTbar"])
            sensitivity = np.nan_to_num(sensitivity)
            efficiency = sigPlotWeights["weightSum"][signal] / sigPlotWeights["weightSkimSum"][signal]
            fpr = (bgPlotWeights["weightSum"]["QCD"]+bgPlotWeights["weightSum"]["TTbar"]) / (bgPlotWeights["weightSkimSum"]["QCD"]+bgPlotWeights["weightSkimSum"]["TTbar"])
            if(np.max(sensitivity)>bestTraditionalSensitivity[signal][0]): 
                ind = np.unravel_index(np.argmax(sensitivity, axis=None), sensitivity.shape)
                bestTraditionalSensitivity[signal] = [np.max(sensitivity),efficiency[ind],fpr[ind],shiftCuts[ind[0]],errCuts[ind[1]],nTrackCuts[ind[2]]]
                optimalCuts[signal] = ind
                sensitivityMatrices[signal] = sensitivity
            sensitivity = efficiency / (1+np.sqrt(bgPlotWeights["weightSum"]["QCD"]+bgPlotWeights["weightSum"]["TTbar"]))
            if(np.max(sensitivity)>bestEfficiencySensitivity[signal][0]): 
                ind = np.unravel_index(np.argmax(sensitivity, axis=None), sensitivity.shape)
                bestEfficiencySensitivity[signal] = [np.max(sensitivity),efficiency[ind],fpr[ind],shiftCuts[ind[0]],errCuts[ind[1]],nTrackCuts[ind[2]]]
            ax.scatter(fpr,efficiency,label=signal,color=color,zorder=1)
            ax.scatter(fpr[ind],efficiency[ind],marker="s",color=color,zorder=2,edgecolor="yellow")
            plt.xscale("symlog",linthresh=10**-11)
        ax.set_ylabel("TPR")
        #ax.set_ylim(0.0,0.7)
        plt.xlabel("FPR")
        plt.legend()
        plt.savefig("15FPRHiggsEff"+lifetime+"_Merge3SigmaMinTV2.pdf")
        plt.clf()
        #plt.show()

    markers = ["o","^","v","<",">","+","x","*",]
    indexList = []
    signalList = []
    i_marker = 0
    for signal, indices in optimalCuts.items():
        indexList.append(indices)
        signalList.append(signal)
    for i_index in range(len(indexList)):
        if(signalList[i_index] not in {"Stop-M200-cT1","Stop-M200-cT3","Hto2Sto4D-cT0p1-MS7","Hto2Sto4D-cT0p1-MS15","Hto2Sto4D-cT1-MS7","Hto2Sto4D-cT1-MS15","Hto2Sto4D-cT10-MS7","Hto2Sto4D-cT10-MS15"}): continue
        sensitivityList = []
        for j in range(len(signalList)):
            sensitivity = sensitivityMatrices[signalList[j]][indexList[i_index]]
            sensitivityList.append(sensitivity)
        plt.scatter(signalList,sensitivityList,label=signalList[i_index],marker=markers[i_marker])
        i_marker += 1
    plt.xlabel("15 FPR") 
    plt.ylabel("Sensitivity S/Sqrt(S+B)")
    plt.xticks(rotation=90,fontsize=10)
    plt.legend(fontsize=10)
    plt.savefig("15FPROptimization_Merge3SigmaMinTV2.pdf")
    plt.clf()
    #plt.show()
    
    print("total background:",bgPlotWeights["weightSkimSum"]["QCD"]+bgPlotWeights["weightSkimSum"]["TTbar"])
    for signal, cuts in bestTraditionalSensitivity.items():
        print("best traditional sensitivity for signal",signal,"is",cuts[0],"sig eff:",cuts[1],"fpr:",cuts[2],"requiring >",cuts[5],"tracks and <",f"{cuts[4]:3f}","uncertainty with shift <",cuts[3])
    for signal, cuts in bestEfficiencySensitivity.items():
        print("best efficiency sensitivity for signal",signal,"is",cuts[0],"sig eff:",cuts[1],"fpr:",cuts[2],"requiring >",cuts[5],"tracks and <",f"{cuts[4]:3f}","uncertainty with shift <",cuts[3])

    
if __name__=="__main__":
    main()
