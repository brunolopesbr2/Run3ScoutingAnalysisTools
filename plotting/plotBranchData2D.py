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
    "scoutTrack_dxy": [-0.02,0.02,101], "scoutTrack_phi": [-3.142,3.142,101], "scoutVert_x": [-0.05,0.05,101], "scoutVert_y": [-0.05,0.05,101]
}

x_axis = "scoutVert_x"
y_axis = "scoutVert_y"

def process_root_file(args):
    rootFile, process = args
    print(f"Processing {rootFile}")
    output = {}
    weightSum = np.zeros((plotDict[x_axis][2]-1,plotDict[y_axis][2]-1))
    with uproot.open(rootFile) as file:
        tree = file["scoutingTree/objectTree"]
        # Select only necessary branches to load
        branches = list(plotDict.keys()) + ["weight", x_axis, y_axis,"runNumber","lumiBlock"]
        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        nbatches = 0
        for batch in tree.iterate(branches, library="ak", step_size=40000):  
            runNumber = batch["runNumber"]
            ls = batch["lumiBlock"]
            #mask = (runNumber!=384323)
            #if(ak.sum(mask)==0): continue
            #nbatches += 1
            #if(nbatches>10): break
            weights = ak.ones_like(batch["weight"])  # normalize event weights
            #print(runNumber)
            #print(ls)
            x_binning = plotDict[x_axis]
            x_bins = np.linspace(x_binning[0], x_binning[1], x_binning[2])
            x_data = batch[x_axis]

            y_binning = plotDict[y_axis]
            y_bins = np.linspace(y_binning[0], y_binning[1], y_binning[2])
            y_data = batch[y_axis]
            #print(x_data)
            # Apply displacement cut
            #x_data = x_data[mask]
            #print(x_data)
            # Apply displacement cut
            #mask = ak.ones_like(y_data, dtype=bool)
            #y_data = y_data[mask]
            #weights = weights[mask]

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
        output["2D"] = {process: weightSum}
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
    signalDict, dataDict = makeDict("offlineBeamspot",["Hto2Sto4D"],["2024"])
    dataPlotWeights = parallel_processing(dataDict)
    
    # **Plotting**
    x_binning = plotDict[x_axis]
    y_binning = plotDict[y_axis]
    x_bins = np.linspace(x_binning[0], x_binning[1], x_binning[2])
    y_bins = np.linspace(y_binning[0], y_binning[1], y_binning[2])
    data = np.array(dataPlotWeights["2D"]["2024G"]).T
    fig, ax = plt.subplots()
    plt.pcolormesh(x_bins, y_bins, data, shading='auto', cmap='viridis',norm=LogNorm())
    plt.colorbar()
    plt.xlabel("Vertex X [cm]")
    plt.ylabel("Vertex Y [cm]")
    hep.cms.label("Preliminary", loc=0, ax=ax, com=13.6, fontsize=16,data=True)
    plt.savefig("beamspot2d_run384323_offlineBeamspot.pdf")
    
if __name__=="__main__":
    main()
