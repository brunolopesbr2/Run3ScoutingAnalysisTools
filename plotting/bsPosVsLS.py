from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")

x_axis = "runNumber"
y_axis = "beamspot_x"

def process_root_file(args):
    rootFile, process = args
    print(f"Processing {rootFile}")

    output = {}
    with uproot.open(rootFile) as file:
        tree = file["scoutingTree/objectTree"]
        # Select only necessary branches to load
        branches = [x_axis, y_axis,"runNumber"]
        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        for batch in tree.iterate(branches, library="ak", step_size=40000):  
            #runNumber = batch["runNumber"]
            x_data = batch[x_axis]
            y_data = batch[y_axis]

            #mask = (runNumber==384323)
            #x_data = x_data[mask]
            #y_data = y_data[mask]
            #print(x_data)
            # Apply mask and flatten data
            x_data = ak.flatten(x_data,axis=None)
            y_data = ak.flatten(y_data,axis=None)
            
            for i in range(len(x_data)):
                if x_data[i] not in output:
                    output[x_data[i]] = [y_data[i]]
                else:
                    output[x_data[i]] += [y_data[i]]
    return output

# **Parallel Processing Using ProcessPoolExecutor**
def parallel_processing(files_dict):
    results = {}
    with ProcessPoolExecutor(max_workers=16) as executor:  # Adjust max_workers based on CPU cores
        futures = {executor.submit(process_root_file, (f, p)): (f, p)
                   for p, files in files_dict.items() for f in files}

        for future in as_completed(futures):
            result = future.result()
            for LS in result:
                if LS not in results:
                    results[LS] = result[LS]
                else:
                    for process in result[LS]:
                        if process not in results[LS]:
                             results[LS][process] = result[LS][process]
                        else:
                            results[LS][process] = results[LS][process] + result[LS][process]

    return results

def main():
    limitDict = build_limits("../EXO-23-13-ExoHiggsBRLimitvsLifetime.root","../EXO-19-13-RPVSUSYSigmaBSquaredLimitsMassvsLifetime.root")
    signalDict, dataDict = makeDict("v24-3to4Dxy-OnlineBS",["Hto2Sto4D"],["2024"])
    dataPlotWeights = parallel_processing(dataDict)

    EraCStart = 379412
    EraDStart = 380253
    EraEv1Start = 380948
    EraEv2Start = 381384
    EraFStart = 381944
    EraGStart = 383780
    EraHStart = 385814
    EraIv1Start = 386409
    EraIv2Start = 386798
    EraIv2End = 387121
    # **Plotting**
    x = []
    y = []
    for key, values in dataPlotWeights.items():
        avg = sum(values) / len(values)
        x += [key]
        y += [avg]
        if(key==384323):
            print("run 384323 average",avg)
            y_run384323 = avg
        if(key==384322):
            print("run 384322 average",avg)
            y_run384322 = avg
    fig, ax = plt.subplots()
    plt.scatter(x,y)
    plt.xlabel(x_axis)
    plt.ylabel("Beamspot X [cm]")
    plt.scatter(384322,y_run384322,color="green",label="run 384322")
    plt.scatter(384323,y_run384323,color="red",label="run 384323")
    plt.ticklabel_format(axis='y', useOffset=False)
    plt.legend(fontsize=12)
    hep.cms.label("Preliminary", loc=0, ax=ax, com=13.6, fontsize=16,data=True)
    ybottom, ytop = ax.get_ylim()
    plt.vlines(EraCStart,ybottom,ytop,linestyle="--")
    plt.text(EraCStart,ybottom,'Era C Start',rotation=90,fontsize=12)
    plt.vlines(EraDStart,ybottom,ytop,linestyle="--")
    plt.text(EraDStart,ybottom,'Era D Start',rotation=90,fontsize=12)
    plt.vlines(EraEv1Start,ybottom,ytop,linestyle="--")
    plt.text(EraEv1Start,ybottom,'Era E v1 Start',rotation=90,fontsize=12)
    plt.vlines(EraEv2Start,ybottom,ytop,linestyle="--")
    plt.text(EraEv2Start,ybottom,'Era E v2 Start',rotation=90,fontsize=12)
    plt.vlines(EraFStart,ybottom,ytop,linestyle="--")
    plt.text(EraFStart,ybottom,'Era F Start',rotation=90,fontsize=12)
    plt.vlines(EraGStart,ybottom,ytop,linestyle="--")
    plt.text(EraGStart,ybottom,'Era G Start',rotation=90,fontsize=12)
    plt.vlines(EraHStart,ybottom,ytop,linestyle="--")
    plt.text(EraHStart,ybottom,'Era H Start',rotation=90,fontsize=12)
    plt.vlines(EraIv1Start,ybottom,ytop,linestyle="--")
    plt.text(EraIv1Start,ybottom,'Era I v1 Start',rotation=90,fontsize=12)
    plt.vlines(EraIv2Start,ybottom,ytop,linestyle="--")
    plt.text(EraIv2Start,ybottom,'Era I v2 Start',rotation=90,fontsize=12)
    plt.vlines(EraIv2End,ybottom,ytop,linestyle="--")
    plt.text(EraIv2End,ybottom,'Era I v2 End',rotation=90,fontsize=12)
    plt.savefig("OnlineBSXPosVsRunNumber.pdf")
    
if __name__=="__main__":
    main()
