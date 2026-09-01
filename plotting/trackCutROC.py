from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")

ptTrackCuts = np.linspace(1,1,1)
dxySigCuts = np.linspace(2.0,8,13)
pixelHitsCuts = np.linspace(1,3,3)
nTrackerLayersCuts = np.linspace(3,9,7)
stripHitsCuts = np.linspace(0,8,9)

def process_root_file(args):
    rootFile, process = args
    print(f"Processing {rootFile}")

    output = {}
    with uproot.open(rootFile) as file:
        output["genWeightSum"] = {process: file["triggerFilter/genWeightsSkim"].values()[0]}
        tree = file["scoutingTree/objectTree"]
        # Select only necessary branches to load
        branches = ["weight","vertTrack_iVtx","scoutVert_dBV","vertTrack_pt","vertTrack_dxySig","vertTrack_nValidPixelHits", "vertTrack_nTrackerLayersWithMeasurement","vertTrack_nValidStripHits"]
        weightSum = np.zeros((len(ptTrackCuts),len(dxySigCuts),len(pixelHitsCuts),len(nTrackerLayersCuts),len(stripHitsCuts)))
        weightSkimSum = 0
        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        nbatch = 0;
        for batch in tree.iterate(branches, library="ak", step_size=100000):
            nbatch += 1
            if(nbatch>10):
                break
            weights = batch["weight"]  # event weights
            iVtx = batch["vertTrack_iVtx"]
            mask = (batch["scoutVert_dBV"][iVtx] >= 0.01) & (batch["scoutVert_dBV"][iVtx] < 2.0)
            pt = batch["vertTrack_pt"][mask]
            dxySig = batch["vertTrack_dxySig"][mask]
            npixel = batch["vertTrack_nValidPixelHits"][mask]
            ntracker = batch["vertTrack_nTrackerLayersWithMeasurement"][mask]
            nstrip = batch["vertTrack_nValidStripHits"][mask]
            nTracks = ak.num(pt,axis=1)
            weightSkimSum += ak.sum(nTracks*weights)
            ptMasks = [(pt > ptTrackCuts[i]) for i in range(len(ptTrackCuts))]
            dxyMasks = [(dxySig > dxySigCuts[j]) for j in range(len(dxySigCuts))]
            pixelMasks = [(npixel > pixelHitsCuts[k]) for k in range(len(pixelHitsCuts))]
            trackerMasks = [(ntracker > nTrackerLayersCuts[l]) for l in range(len(nTrackerLayersCuts))]
            stripMasks = [(nstrip > stripHitsCuts[k]) for k in range(len(stripHitsCuts))]
            for i in range(len(ptTrackCuts)):
                for j in range(len(dxySigCuts)):
                    for k in range(len(pixelHitsCuts)):
                        for l in range(len(nTrackerLayersCuts)):
                            for m in range(len(stripHitsCuts)):
                                mask = ptMasks[i] & dxyMasks[j] & pixelMasks[k] & trackerMasks[l] & stripMasks[m]
                                ptMasked = pt[mask]
                                nTracks = ak.num(ptMasked,axis=1)
                                weightSum[i][j][k][l][m] += ak.sum(nTracks*weights)
        output["weightSum"] = {process: weightSum}
        output["weightSkimSum"] = {process: weightSkimSum}
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
    signalDict, processDict = makeDict("v22-LooseTrackCuts",["Stop-M","Hto2Sto4D"],["QCD","TTTo"])
    bgPlotWeights = parallel_processing(processDict)
    sigPlotWeights = parallel_processing(signalDict)
    
    #Combining Background Subprocesses and Reweighting Events
    for process in bgPlotWeights["genWeightSum"].keys():
        bgPlotWeights["weightSum"][process] = bgPlotWeights["weightSum"][process] / bgPlotWeights["genWeightSum"][process]
        bgPlotWeights["weightSkimSum"][process] = bgPlotWeights["weightSkimSum"][process] / bgPlotWeights["genWeightSum"][process]
    bgPlotWeights["weightSum"]["QCD"] = bgPlotWeights["weightSum"]["QCD40to70"]+bgPlotWeights["weightSum"]["QCD70to100"]+bgPlotWeights["weightSum"]["QCD100to200"]+bgPlotWeights["weightSum"]["QCD200to400"]+bgPlotWeights["weightSum"]["QCD400to600"]+bgPlotWeights["weightSum"]["QCD600to800"]+bgPlotWeights["weightSum"]["QCD800to1000"]+bgPlotWeights["weightSum"]["QCD1000to1200"]+bgPlotWeights["weightSum"]["QCD1200to1500"]+bgPlotWeights["weightSum"]["QCD1500to2000"]+bgPlotWeights["weightSum"]["QCD2000"]
    bgPlotWeights["weightSkimSum"]["QCD"] = bgPlotWeights["weightSkimSum"]["QCD40to70"]+bgPlotWeights["weightSkimSum"]["QCD70to100"]+bgPlotWeights["weightSkimSum"]["QCD100to200"]+bgPlotWeights["weightSkimSum"]["QCD200to400"]+bgPlotWeights["weightSkimSum"]["QCD400to600"]+bgPlotWeights["weightSkimSum"]["QCD600to800"]+bgPlotWeights["weightSkimSum"]["QCD800to1000"]+bgPlotWeights["weightSkimSum"]["QCD1000to1200"]+bgPlotWeights["weightSkimSum"]["QCD1200to1500"]+bgPlotWeights["weightSkimSum"]["QCD1500to2000"]+bgPlotWeights["weightSkimSum"]["QCD2000"]
    bgPlotWeights["weightSum"]["TTbar"] = bgPlotWeights["weightSum"]["TTTo4Q"]+bgPlotWeights["weightSum"]["TTToLNu2Q"]
    bgPlotWeights["weightSkimSum"]["TTbar"] = bgPlotWeights["weightSkimSum"]["TTTo4Q"]+bgPlotWeights["weightSkimSum"]["TTToLNu2Q"]
    for process in sigPlotWeights["genWeightSum"].keys():
        sigPlotWeights["weightSum"][process] = sigPlotWeights["weightSum"][process] / sigPlotWeights["genWeightSum"][process]
        sigPlotWeights["weightSkimSum"][process] = sigPlotWeights["weightSkimSum"][process] / sigPlotWeights["genWeightSum"][process]

    thresh_val = [0.01,0.05,0.1,0.15,0.2,0.25,0.45,0.46,0.47,0.48,0.49,0.50]
    optimalCuts = {}
    effMatrices = {}
    # **Plotting**
    for lifetime in ["1","3","10"]:
        fig, ax = plt.subplots()
        colors = {"Stop-M200-cT"+lifetime: "black", "Stop-M400-cT"+lifetime: "red", "Stop-M600-cT"+lifetime: "blue", "Stop-M800-cT"+lifetime: "green"}
        for signal, color in colors.items():
            efficiency = sigPlotWeights["weightSum"][signal] / sigPlotWeights["weightSkimSum"][signal]
            efficiency = np.round(efficiency,2)
            fpr = (bgPlotWeights["weightSum"]["QCD"]+bgPlotWeights["weightSum"]["TTbar"]) / (bgPlotWeights["weightSkimSum"]["QCD"]+bgPlotWeights["weightSkimSum"]["TTbar"])
            fpr = np.round(fpr,2)
            unique_fpr = np.unique(fpr)
            max_effs = np.array([])
            thresh = [True]*len(thresh_val)
            indices = []
            thresh_eff = []
            for ux in unique_fpr:
                unique_eff = np.where(fpr == ux, efficiency, -1)
                max_eff = np.max(unique_eff)
                ind = np.unravel_index(np.argmax(unique_eff, axis=None), unique_eff.shape)
                for i in range(len(thresh_val)):
                    if(ux>=thresh_val[i] and thresh[i]): 
                        indices.append(ind)
                        thresh_eff.append(max_eff)
                        thresh[i] = False
                '''
                if(ux>=thresh_val[0] and thresh[0]): 
                    indices.append(ind)
                    thresh[0] = False
                if(ux>=thresh_val[1] and thresh[1]): 
                    indices.append(ind)
                    thresh[1] = False
                if(ux>=thresh_val[2] and thresh[2]): 
                    indices.append(ind)
                    thresh[2] = False
                if(ux>=thresh_val[3] and thresh[3]): 
                    indices.append(ind)
                    thresh[3] = False
                if(ux>=thresh_val[4] and thresh[4]): 
                    indices.append(ind)
                    thresh[4] = False
                if(ux>=thresh_val[5] and thresh[5]): 
                    indices.append(ind)
                    thresh[5] = False
                if(ux>=thresh_val[6] and thresh[6]): 
                    indices.append(ind)
                    thresh[6] = False
                '''
                max_effs = np.append(max_effs,max_eff)
            for i in range(len(thresh_val)):
                print(signal," fpr: ",thresh_val[i]," eff: ",thresh_eff[i]," best cuts are pt > ",ptTrackCuts[indices[i][0]]," dxy sig > ",dxySigCuts[indices[i][1]]," pixel hits > ",pixelHitsCuts[indices[i][2]]," tracker layers > ",nTrackerLayersCuts[indices[i][3]]," strip hits > ",stripHitsCuts[indices[i][4]])
            ax.scatter(unique_fpr,max_effs,label=signal,color=color,zorder=1)
            optimalCuts[signal] = indices
            effMatrices[signal] = efficiency
        ax.set_ylabel("TPR")
        plt.xlabel("FPR")
        #plt.yscale("log")
        plt.legend()
        plt.savefig(f"trackROC_stop_{lifetime}.pdf", bbox_inches='tight')

    for lifetime in ["0p1","1","10"]:
        fig, ax = plt.subplots()
        colors = {"Hto2Sto4D-cT"+lifetime+"-MS1": "black", "Hto2Sto4D-cT"+lifetime+"-MS7": "purple", "Hto2Sto4D-cT"+lifetime+"-MS15": "red", "Hto2Sto4D-cT"+lifetime+"-MS23": "orange", "Hto2Sto4D-cT"+lifetime+"-MS30": "blue", "Hto2Sto4D-cT"+lifetime+"-MS40": "pink", "Hto2Sto4D-cT"+lifetime+"-MS55": "green"}
        for signal, color in colors.items():
            efficiency = sigPlotWeights["weightSum"][signal] / sigPlotWeights["weightSkimSum"][signal]
            efficiency = np.round(efficiency,2)
            fpr = (bgPlotWeights["weightSum"]["QCD"]+bgPlotWeights["weightSum"]["TTbar"]) / (bgPlotWeights["weightSkimSum"]["QCD"]+bgPlotWeights["weightSkimSum"]["TTbar"])
            fpr = np.round(fpr,2)
            unique_fpr = np.unique(fpr)
            max_effs = np.array([])
            #thresh = [True,True,True,True,True,True,True]
            thresh = [True]*len(thresh_val)
            indices = []
            thresh_eff = []
            for ux in unique_fpr:
                unique_eff = np.where(fpr == ux, efficiency, -1)
                max_eff = np.max(unique_eff)
                ind = np.unravel_index(np.argmax(unique_eff, axis=None), unique_eff.shape)
                for i in range(len(thresh_val)):
                    if(ux>=thresh_val[i] and thresh[i]):
                        indices.append(ind)
                        thresh_eff.append(max_eff)
                        thresh[i] = False
                '''
                if(ux>=thresh_val[0] and thresh[0]): 
                    indices.append(ind)
                    thresh[0] = False
                if(ux>=thresh_val[1] and thresh[1]): 
                    indices.append(ind)
                    thresh[1] = False
                if(ux>=thresh_val[2] and thresh[2]): 
                    indices.append(ind)
                    thresh[2] = False
                if(ux>=thresh_val[3] and thresh[3]): 
                    indices.append(ind)
                    thresh[3] = False
                if(ux>=thresh_val[4] and thresh[4]): 
                    indices.append(ind)
                    thresh[4] = False
                if(ux>=thresh_val[5] and thresh[5]): 
                    indices.append(ind)
                    thresh[5] = False
                if(ux>=thresh_val[6] and thresh[6]): 
                    indices.append(ind)
                    thresh[6] = False
                '''
                max_effs = np.append(max_effs,max_eff)
            for i in range(len(thresh_val)):
                print(signal," fpr: ",thresh_val[i]," best cuts are pt > ",ptTrackCuts[indices[i][0]]," dxy sig > ",dxySigCuts[indices[i][1]]," pixel hits > ",pixelHitsCuts[indices[i][2]]," tracker layers > ",nTrackerLayersCuts[indices[i][3]]," strip hits > ",stripHitsCuts[indices[i][4]])
            ax.scatter(unique_fpr,max_effs,label=signal,color=color,zorder=1)
            optimalCuts[signal] = indices
            effMatrices[signal] = efficiency
        ax.set_ylabel("TPR")
        plt.xlabel("FPR")
        #plt.yscale("log")
        plt.legend()
        plt.savefig(f"trackROC_exoHiggs_{lifetime}.pdf", bbox_inches='tight')


    markers = ["o","^","v","<",">","+","x","*",]
    for i in range(len(thresh_val)):
        indexList = []
        signalList = []
        i_marker = 0
        for signal, indices in optimalCuts.items():
            indexList.append(indices[i])
            signalList.append(signal)
        for i_index in range(len(indexList)):
            if(signalList[i_index] not in {"Stop-M200-cT1","Stop-M200-cT3","Hto2Sto4D-cT0p1-MS7","Hto2Sto4D-cT0p1-MS15","Hto2Sto4D-cT1-MS7","Hto2Sto4D-cT1-MS15","Hto2Sto4D-cT10-MS7","Hto2Sto4D-cT10-MS15"}): continue
            effList = []
            for j in range(len(signalList)):
                eff = effMatrices[signalList[j]][indexList[i_index]]
                effList.append(eff)
            plt.scatter(signalList,effList,label=signalList[i_index],marker=markers[i_marker])
            i_marker += 1
        plt.xlabel(f"{thresh_val[i]} FPR") 
        plt.xticks(rotation=90,fontsize=10)
        plt.legend(fontsize=10)
        plt.savefig(f"signalEffComparison.pdf", bbox_inches='tight')
    
if __name__=="__main__":
    main()
