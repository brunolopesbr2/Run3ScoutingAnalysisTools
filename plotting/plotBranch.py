from currentLimits import build_limits
from sampleDict import makeDict
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak

filterName = "K0Filter"
treeName = "K0Tree"
sysList = ["trigger","PU"] #options are trigger and PU

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
    with uproot.open(rootFile) as file:
        genWeightSum = file[filterName+"/genWeightsSkim"].values()[0]
        tree = file[treeName+"/objectTree"]
        isMC = True
        if("2024" in process):
            isMC = False
        # Select only necessary branches to load
        branches = list(plotDict.keys()) + ["vertTrack_iVtx", "scoutVert_dBV", "weight","scoutVert_nTracks","scoutVert_dBV","scoutVert_mass","scoutVert_costh2","scoutVert_ctau","scoutVert_chi2","scoutVert_pt","muon_phi","dimuon_mass","uncorrectedWeight"]
        if(isMC):
            if("PU" in sysList):
                branches = branches + ["weight_PU_BCDEFGHI_nominal", "weight_PU_BCDEFGHI_up", "weight_PU_BCDEFGHI_down"]
            if("trigger" in sysList):
                branches = branches + ["weight_trigger_nominal","weight_trigger_up","weight_trigger_down"]
        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        for batch in tree.iterate(branches, library="ak", step_size=40000):
            if(process in processDict):
                weights = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] #* (13.35/109.99)#(7.62/109.99)#* batch["weight_trigger_nominal"]
                weights_PU_up = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_up"] #* (13.35/109.99)#(7.62/109.99)#* batch["weight_trigger_nominal"]
                weights_PU_down = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_down"] #* (13.35/109.99)#(7.62/109.99)#* batch["weight_trigger_nominal"]
            else:
                weights = ak.ones_like(batch["weight"])
            if((process in processDict) and (not doWeightSum)): 
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
                if(process in processDict):
                    weightsMasked_PU_up=weights_PU_up[mask]
                    weightsMasked_PU_down=weights_PU_down[mask]
                broadcastWeights, data = ak.broadcast_arrays(weightsMasked,data)
                if(process in processDict):
                    broadcastWeights_PU_up, data = ak.broadcast_arrays(weightsMasked_PU_up,data)
                    broadcastWeights_PU_down, data = ak.broadcast_arrays(weightsMasked_PU_down,data)
                
                # Apply mask and flatten data
                data = ak.flatten(data,axis=None)
                data = np.clip(data,bins[0],bins[-1])
                weights_filtered = ak.flatten(broadcastWeights,axis=None)
                if(process in processDict):
                    weights_filtered_PU_up = ak.flatten(broadcastWeights_PU_up,axis=None)
                    weights_filtered_PU_down = ak.flatten(broadcastWeights_PU_down,axis=None)
                # Compute histograms
                n, _ = np.histogram(data, weights=weights_filtered, bins=bins)
                n_2, _ = np.histogram(data, weights=weights_filtered**2, bins=bins)
                if(process in processDict):
                    n_PU_up, _ = np.histogram(data, weights=weights_filtered_PU_up, bins=bins)
                    n_PU_down, _ = np.histogram(data, weights=weights_filtered_PU_down, bins=bins)
                if plot not in output:
                    output[plot] = {process: n}
                    output[f"{plot}_squared"] = {process: n_2}
                    if(process in processDict):
                        output[f"{plot}_PU_up"] = {process: n_PU_up}
                        output[f"{plot}_PU_down"] = {process: n_PU_down}
                else:
                    output[plot][process] = output[plot][process] + n
                    output[f"{plot}_squared"][process] = output[f"{plot}_squared"][process] + n_2
                    if(process in processDict):
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
    signalDict, bkgDict = makeDict("v33-4DxyMin",["Stop","Hto2Sto4D"],["QCD","TTto"])
    
    
if __name__=="__main__":
    main()
