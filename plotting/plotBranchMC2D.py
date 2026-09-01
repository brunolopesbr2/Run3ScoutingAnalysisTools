from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")
from matplotlib.colors import LogNorm

plotDict = {
    #"vertTrack_pt": [0,50,101], "vertTrack_eta": [-3,3,101], "vertTrack_phi": [-3.142,3.142,101],
    #"vertTrack_reducedChi2": [0,7,51], "vertTrack_dxy": [0,0.3,51], "vertTrack_dxySig": [0,50,101],
    #"vertTrack_nValidPixelHits": [0,13,14], "vertTrack_nTrackerLayersWithMeasurement": [0,21,22],
    #"vertTrack_nValidStripHits": [0,32,33], 
    "scoutVert_dBV": [0,1,101], "scoutVert_dBVErr": [0,0.1,101],
    #"vertTrack_nMissingInnerHits": [0,5,6], 
    "scoutVert_nTracks": [2,10,9], "scoutVert_chi2": [0,5,50],
    "scoutVert_dT": [0,0.5,101],
    "scoutVert_cosT": [-1,1,101],
    #"scoutTrack_eta": [-3,3,101], "scoutTrack_phi": [-3.142,3.142,101], "scoutTrack_dxy": [0,0.03,51],
    #"scoutTrack_dxySig": [0,50,101]
}

xvar = "scoutVert_nTracks"
yvar = "scoutVert_cosT"

def histogram_correlation(x_edges, y_edges, H):
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2
    X, Y = np.meshgrid(x_centers, y_centers, indexing='xy')
    x_vals = X.ravel()
    y_vals = Y.ravel()
    weights = H.ravel()
    mean_x = np.average(x_vals, weights=weights)
    mean_y = np.average(y_vals, weights=weights)
    cov_xy = np.average((x_vals - mean_x) * (y_vals - mean_y), weights=weights)
    var_x = np.average((x_vals - mean_x)**2, weights=weights)
    var_y = np.average((y_vals - mean_y)**2, weights=weights)
    return cov_xy / np.sqrt(var_x * var_y)

def process_root_file(args):
    rootFile, process = args
    print(f"Processing {rootFile}")

    output = {}
    genWeightSum = 0
    weightSum = np.zeros((plotDict[xvar][2]-1,plotDict[yvar][2]-1))
    with uproot.open(rootFile) as file:
        output["genWeightSum"] = {}
        genWeightSum = file["triggerFilter/genWeightsSkim"].values()[0]
        tree = file["scoutingTree/objectTree"]

        # Select only necessary branches to load
        branches = list(plotDict.keys()) + ["vertTrack_iVtx", "weight","scoutVert_cosT","uncorrectedWeight","weight_PU_BCDEFGHI_nominal","weight_trigger_nominal"]

        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        for batch in tree.iterate(branches, library="ak", step_size=100000):  
            weights = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] * batch["weight_trigger_nominal"]
            weights = weights / genWeightSum

            x_binning = plotDict[xvar]
            x_bins = np.linspace(x_binning[0], x_binning[1], x_binning[2])
            x_data = batch[xvar]

            y_binning = plotDict[yvar]
            y_bins = np.linspace(y_binning[0], y_binning[1], y_binning[2])
            y_data = batch[yvar]
            
            #Apply displacement cut
            mask = (batch["scoutVert_dBV"] >= 0.01) & (batch["scoutVert_dBV"] < 2)  & (batch["scoutVert_dBVErr"] < 0.005)  #& (batch["scoutVert_cosT"] > 0) 
            x_data = x_data[mask]
            y_data = y_data[mask]#*np.sqrt(x_data)
            broadcastWeights, x_data = ak.broadcast_arrays(weights,x_data)
            # Apply mask and flatten data
            x_data = ak.flatten(x_data,axis=None)
            x_data = np.clip(x_data,x_bins[0],x_bins[-1])
            y_data = ak.flatten(y_data,axis=None)
            y_data = np.clip(y_data,y_bins[0],y_bins[-1])
            weights_filtered = ak.flatten(broadcastWeights,axis=None)
            # Compute histograms
            n, xedges, yedges = np.histogram2d(x_data,y_data,weights=weights_filtered, bins=(x_bins,y_bins))
            weightSum = weightSum + n
    output["trkVert_eta_phi"] = {process: weightSum}
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
    signalDict, processDict = makeDict("v33-4DxyMin",["Stop-M","Hto2Sto4D"],["QCD","TTTo"])
    bgPlotWeights = parallel_processing(processDict)
    sigPlotWeights = parallel_processing(signalDict)

    #Combining Background Subprocesses and Reweighting Events
    for plot in ["trkVert_eta_phi"]:
        bgPlotWeights[plot]["QCD"] = bgPlotWeights[plot]["QCD40to70"]+bgPlotWeights[plot]["QCD70to100"]+bgPlotWeights[plot]["QCD100to200"]+bgPlotWeights[plot]["QCD200to400"]+bgPlotWeights[plot]["QCD400to600"]+bgPlotWeights[plot]["QCD600to800"]+bgPlotWeights[plot]["QCD800to1000"]+bgPlotWeights[plot]["QCD1000to1200"]+bgPlotWeights[plot]["QCD1200to1500"]+bgPlotWeights[plot]["QCD1500to2000"]+bgPlotWeights[plot]["QCD2000"]
        bgPlotWeights[plot]["TTbar"] = bgPlotWeights[plot]["TTTo4Q"]+bgPlotWeights[plot]["TTToLNu2Q"]
        bgPlotWeights[plot]["BG"] = bgPlotWeights[plot]["QCD"]+bgPlotWeights[plot]["TTbar"]

    # **Plotting**
    x_binning = plotDict[xvar]
    y_binning = plotDict[yvar]
    x_bins = np.linspace(x_binning[0], x_binning[1], x_binning[2])
    y_bins = np.linspace(y_binning[0], y_binning[1], y_binning[2])
    plt.pcolormesh(x_bins, y_bins, np.array(bgPlotWeights["trkVert_eta_phi"]["BG"]).T, shading='auto', cmap='viridis',norm=LogNorm())
    plt.colorbar()
    plt.xlabel(xvar)
    plt.ylabel(yvar)
    plt.savefig(f"{xvar}_{yvar}2D_BG.pdf", bbox_inches='tight')

    for signal in signalDict.keys():
        print(signal)
        plt.pcolormesh(x_bins, y_bins, np.array(sigPlotWeights["trkVert_eta_phi"][signal]).T, shading='auto', cmap='viridis',norm=LogNorm())
        plt.colorbar()
        plt.xlabel(xvar)
        plt.ylabel(yvar)
        plt.savefig(f"{xvar}_{yvar}2D_{signal}.pdf", bbox_inches='tight')
    print("TTbar", histogram_correlation(x_bins, y_bins, np.array(bgPlotWeights["trkVert_eta_phi"]["TTbar"])))
    print("QCD", histogram_correlation(x_bins, y_bins, np.array(bgPlotWeights["trkVert_eta_phi"]["QCD"])))
    print("Stop M200 cT1", histogram_correlation(x_bins, y_bins, np.array(sigPlotWeights["trkVert_eta_phi"]["Stop-M200-cT1"])))

if __name__=="__main__":
    main()
