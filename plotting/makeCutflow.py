from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")
import ROOT
from hist import intervals

#Cutflow table script 
doPercents = False
bin_namesCustom = ["7Tracks","8Tracks","9Tracks"]

def process_cutflows(args):
    """ Process a single ROOT file in chunks using uproot.iterate() """
    rootFile, process = args
    print(f"Processing {rootFile}")

    output = {}
    with uproot.open(rootFile) as file:
        output[process] = {}
        output[process+"_PU_up"] = {}
        output[process+"_PU_down"] = {}
        output[process+"_Trigger_up"] = {}
        output[process+"_Trigger_down"] = {}
        output[process+"_squared"] = {}
        output[process+"_PU_up_squared"] = {}
        output[process+"_PU_down_squared"] = {}
        output[process+"_nEvents"] = {}
        tree = file["scoutingTree/objectTree"]

        # Select only necessary branches to load
        branches = ["uncorrectedWeight","scoutVert_dBV","scoutVert_dBVErr", "scoutVert_nTracks","weight","scoutVert_cosT","scoutVert_chi2","weight_PU_BCDEFGHI_nominal","weight_PU_BCDEFGHI_up","weight_PU_BCDEFGHI_down","jet_pt","scoutVert_pMag","weight_trigger_nominal","weight_trigger_up","weight_trigger_down","ht_corrected"]

        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        weightSum = [0]*len(bin_namesCustom)
        weightSumSquared = [0] * len(bin_namesCustom)
        weightSum_PU_up = [0]*len(bin_namesCustom)
        weightSumSquared_PU_up = [0] * len(bin_namesCustom)
        weightSum_PU_down = [0]*len(bin_namesCustom)
        weightSumSquared_PU_down = [0] * len(bin_namesCustom)
        weightSum_Trigger_up = [0]*len(bin_namesCustom)
        weightSum_Trigger_down = [0]*len(bin_namesCustom)
        numEvents = [0] * len(bin_namesCustom)
        for batch in tree.iterate(branches, library="ak", step_size=100000):  
            #weights = batch["weight"]  # event weights
            weights = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] * batch["weight_trigger_nominal"] #* (114.44/108.96) #temp to correct for official 2024 lumi
            weights_PU_up = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_up"] * batch["weight_trigger_nominal"]#* (114.44/108.96)
            weights_PU_down = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_down"] * batch["weight_trigger_nominal"]#* (114.44/108.96)
            weights_Trigger_up = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] * batch["weight_trigger_up"]
            weights_Trigger_down = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] * batch["weight_trigger_down"]
            #if(process in signalDict):
                #if process in limitDict:
                    #currentLimit = limitDict[process]
                    #weights = weights * currentLimit #don't want this when doing combine limit calculation
            data = batch["scoutVert_dBV"]
            ntracks = batch["scoutVert_nTracks"]
            cosT = batch["scoutVert_cosT"]
            dBVErr = batch["scoutVert_dBVErr"] 
            chi2 = batch["scoutVert_chi2"]
            jetpt = batch["jet_pt"]
            ht = batch["ht_corrected"]
            #ht = ak.sum(jetpt,axis=-1)
            #jetMask = (jetpt>30)
            #nJetsAboveCut = ak.sum(jetMask,axis=1)
            mask = (data<2.0) & (cosT>0) & (dBVErr<0.005) & (chi2<2.5) 
            data = data[mask]
            ntracks = ntracks[mask]
            mask = (ak.sum(data>=0.01,axis=1)>0) #& (ht>400)
            #htMask = (ht>280) & (nJetsAboveCut>2)
            #mask = mask & htMask
            weights = weights[mask]
            weights_PU_up = weights_PU_up[mask]
            weights_PU_down = weights_PU_down[mask]
            weights_Trigger_up = weights_Trigger_up[mask]
            weights_Trigger_down = weights_Trigger_down[mask]
            data = data[mask]
            ntracks = ntracks[mask]
            #weightSum[0] += ak.sum(weights)
            #weightSumSquared[0] += ak.sum(weights**2)
            
            # Apply displacement error cut
            #mask = batch["scoutVert_dBVErr"][mask] < 999.9
            #data = data[mask]
            #ntracks = ntracks[mask]
            
            #mask = ak.sum(data>=0.01,axis=1)>0
            #weights = weights[mask]
            #data = data[mask]
            #ntracks = ntracks[mask]
            #weightSum[0] += ak.sum(weights)
            #weightSumSquared[0] += ak.sum(weights**2)
            #numEvents[0] += ak.num(weights,axis=0)
            
            mask_7trackBin = (ntracks==7)
            eventMask_7trackBin = ak.sum(data[mask_7trackBin]>=0.01,axis=1)>0
            weightSum[0] += ak.sum(weights[eventMask_7trackBin])
            weightSumSquared[0] += ak.sum(weights[eventMask_7trackBin]**2)
            weightSum_PU_up[0] += ak.sum(weights_PU_up[eventMask_7trackBin])
            weightSumSquared_PU_up[0] += ak.sum(weights_PU_up[eventMask_7trackBin]**2)
            weightSum_PU_down[0] += ak.sum(weights_PU_down[eventMask_7trackBin])
            weightSumSquared_PU_down[0] += ak.sum(weights_PU_down[eventMask_7trackBin]**2)
            weightSum_Trigger_up[0] += ak.sum(weights_Trigger_up[eventMask_7trackBin])
            weightSum_Trigger_down[0] += ak.sum(weights_Trigger_down[eventMask_7trackBin])
            numEvents[0] += ak.num(weights[eventMask_7trackBin],axis=0)
            
            mask_8trackBin = (ntracks==8)
            eventMask_8trackBin = ak.sum(data[mask_8trackBin]>=0.01,axis=1)>0
            weightSum[1] += ak.sum(weights[eventMask_8trackBin])
            weightSumSquared[1] += ak.sum(weights[eventMask_8trackBin]**2)
            weightSum_PU_up[1] += ak.sum(weights_PU_up[eventMask_8trackBin])
            weightSumSquared_PU_up[1] += ak.sum(weights_PU_up[eventMask_8trackBin]**2)
            weightSum_PU_down[1] += ak.sum(weights_PU_down[eventMask_8trackBin])
            weightSumSquared_PU_down[1] += ak.sum(weights_PU_down[eventMask_8trackBin]**2)
            weightSum_Trigger_up[1] += ak.sum(weights_Trigger_up[eventMask_8trackBin])
            weightSum_Trigger_down[1] += ak.sum(weights_Trigger_down[eventMask_8trackBin])
            numEvents[1] += ak.num(weights[eventMask_8trackBin],axis=0)
            
            mask = (ntracks > 8)
            data = data[mask]
            mask = ak.sum(data>=0.01,axis=1)>0
            weights = weights[mask]
            weights_PU_up = weights_PU_up[mask]
            weights_PU_down = weights_PU_down[mask]
            weights_Trigger_up = weights_Trigger_up[mask]
            weights_Trigger_down = weights_Trigger_down[mask]
            weightSum[2] += ak.sum(weights)
            weightSumSquared[2] += ak.sum(weights**2)
            weightSum_PU_up[2] += ak.sum(weights_PU_up)
            weightSumSquared_PU_up[2] += ak.sum(weights_PU_up**2)
            weightSum_PU_down[2] += ak.sum(weights_PU_down)
            weightSumSquared_PU_down[2] += ak.sum(weights_PU_down**2)
            weightSum_Trigger_up[2] += ak.sum(weights_Trigger_up)
            weightSum_Trigger_down[2] += ak.sum(weights_Trigger_down)
            numEvents[2] += ak.num(weights,axis=0)
            
        for i in range(len(bin_namesCustom)):
            output[process][bin_namesCustom[i]] = weightSum[i]
            output[process+"_squared"][bin_namesCustom[i]] = weightSumSquared[i]
            output[process+"_PU_up"][bin_namesCustom[i]] = weightSum_PU_up[i]
            output[process+"_PU_up_squared"][bin_namesCustom[i]] = weightSumSquared_PU_up[i]
            output[process+"_PU_down"][bin_namesCustom[i]] = weightSum_PU_down[i]
            output[process+"_PU_down_squared"][bin_namesCustom[i]] = weightSumSquared_PU_down[i]
            output[process+"_Trigger_up"][bin_namesCustom[i]] = weightSum_Trigger_up[i]
            output[process+"_Trigger_down"][bin_namesCustom[i]] = weightSum_Trigger_down[i]
            output[process+"_nEvents"][bin_namesCustom[i]] = numEvents[i]
        
    return output

# **Parallel Processing Using ProcessPoolExecutor**
def parallel_processing(files_dict):
    """ Process all ROOT files in parallel and aggregate results """
    results = {}
    with ProcessPoolExecutor(max_workers=16) as executor:  # Adjust max_workers based on CPU cores
        futures = {executor.submit(process_cutflows, (f, p)): (f, p)
                   for p, files in files_dict.items() for f in files}

        for future in as_completed(futures):
            result = future.result()
            for process in result:
                if process not in results:
                    results[process] = result[process]
                else:
                    for cut in result[process]:
                        results[process][cut] = results[process].get(cut, 0) + result[process][cut]

    return results

def main():
    limitDict = build_limits("../EXO-23-13-ExoHiggsBRLimitvsLifetime.root","../EXO-19-13-RPVSUSYSigmaBSquaredLimitsMassvsLifetime.root")
    signalDict, processDict = makeDict("v33-4DxyMin",["Stealth"],["QCD","TTTo"])
    bgPlotWeights = parallel_processing(processDict)
    sigPlotWeights = parallel_processing(signalDict)

    # Define LaTeX table header
    latex_table = "\\begin{table}[htbp]\n"
    latex_table += "\\centering\n" 

    dict = signalDict | processDict
    customWeights = parallel_processing(dict)

    firstProcess = True
    weightSumDict = {}
    weightSquaredSumDict = {}
    genWeightSumDict = {}
    for process, rootFiles in dict.items():
        firstFile = True
        weightSum = []
        weightSquaredSum = []
        genWeightSum = 0
        for rootFile in rootFiles:
            f = ROOT.TFile.Open(rootFile, "READ")
            #h_weightsSkim = f.Get("triggerFilter/weightsSkim")
            #h_weightsSquaredSkim = f.Get("triggerFilter/weightsSquaredSkim")
            h_weightsSkim = f.Get("triggerFilter/weightsSkimLUMCorrected")
            h_weightsSquaredSkim = f.Get("triggerFilter/weightsSquaredSkimLUMCorrected")
            h_genWeights = f.Get("triggerFilter/genWeightsSkim")
            #h_weights = f.Get("scoutingTree/weights")
            #h_weightsSquared = f.Get("scoutingTree/weightsSquared")
            h_weights = f.Get("scoutingTree/weightsLUMCorrected")
            h_weightsSquared = f.Get("scoutingTree/weightsSquaredLUMCorrected")

            # Extract content
            n_bins = 0 #temp while making simplified cutflow table
            #n_bins = h_weights.GetNbinsX()
            weights = np.array([h_weights.GetBinContent(i) for i in range(3, n_bins)]) #temp since there are redundant cuts in tree maker, normally would go from 1 to n_bins+1
            bin_names = np.array([h_weights.GetXaxis().GetLabels().At(i-1).GetName() for i in range(3, n_bins)])
            weightsSquared = np.array([h_weightsSquared.GetBinContent(i) for i in range(3, n_bins)])

            n_binsSkim = h_weightsSkim.GetNbinsX() 
            currentLimit = 1
            if(process in signalDict):
                if process in limitDict:
                    currentLimit = limitDict[process]
            weightsSkim = np.array([h_weightsSkim.GetBinContent(i) for i in range(1, n_binsSkim + 1)]) #* currentLimit #* (114.44/108.96)
            bin_namesSkim = np.array([h_weightsSkim.GetXaxis().GetLabels().At(i-1).GetName() for i in range(1, n_binsSkim + 1)]) 
            weightsSquaredSkim = np.array([h_weightsSquaredSkim.GetBinContent(i) for i in range(1, n_binsSkim + 1)]) #* (currentLimit**2) #* ((114.44/108.96)**2)
            genWeights = np.array([h_genWeights.GetBinContent(i) for i in range(1, n_binsSkim + 1)])

            if(firstFile and firstProcess):
                latex_table += "\\resizebox{\\textwidth}{!}{\\begin{tabular}{|l|"+(len(bin_names)+len(bin_namesSkim)+len(bin_namesCustom)+2)*"c|"+"}\n"
                latex_table += "\\hline\n"
                latex_table += "Process "
                for name in np.concatenate((bin_namesSkim,bin_names)):
                    latex_table += "& {} ".format(name)
                    weightSum.append(0)
                    weightSquaredSum.append(0)
                for name in bin_namesCustom:
                    latex_table += "& {} ".format(name)
                latex_table += "& {} & {} ".format("s/sqrt(s+b)","$\epsilon/(1+\sqrt{B})$")
                latex_table += "\\\\\n"
                latex_table += "\\hline\n"
                firstFile = False
            elif(firstFile):
                for name in np.concatenate((bin_namesSkim,bin_names)):
                    weightSum.append(0)
                    weightSquaredSum.append(0)
                firstFile = False

            genWeightSum += genWeights[0]
            for i in range(len(weightsSkim)):
                weightSum[i] += weightsSkim[i]
                weightSquaredSum[i] += weightsSquaredSkim[i]
            for i in range(len(weights)):
                weightSum[i+len(weightsSkim)] += weights[i]
                weightSquaredSum[i+len(weightsSkim)] += weightsSquared[i]
        firstProcess = False
        weightSumDict[process] = weightSum
        weightSquaredSumDict[process] = weightSquaredSum
        genWeightSumDict[process] = genWeightSum

    #Combining Background Subprocesses and Reweighting Events
    for process in dict.keys():
        for i in range(len(weightSumDict[process])):
            weightSumDict[process][i] = weightSumDict[process][i] / genWeightSumDict[process] 
            weightSquaredSumDict[process][i] = weightSquaredSumDict[process][i] / (genWeightSumDict[process]**2) 
        for cut in customWeights[process].keys():
            customWeights[process][cut] = customWeights[process][cut] / genWeightSumDict[process] 
            customWeights[process+"_squared"][cut] = customWeights[process+"_squared"][cut] / (genWeightSumDict[process]**2) 
            customWeights[process+"_PU_up"][cut] = customWeights[process+"_PU_up"][cut] / genWeightSumDict[process] 
            customWeights[process+"_PU_up_squared"][cut] = customWeights[process+"_PU_up_squared"][cut] / (genWeightSumDict[process]**2)
            customWeights[process+"_PU_down"][cut] = customWeights[process+"_PU_down"][cut] / genWeightSumDict[process] 
            customWeights[process+"_PU_down_squared"][cut] = customWeights[process+"_PU_down_squared"][cut] / (genWeightSumDict[process]**2) 
            customWeights[process+"_Trigger_up"][cut] = customWeights[process+"_Trigger_up"][cut] / genWeightSumDict[process] 
            customWeights[process+"_Trigger_down"][cut] = customWeights[process+"_Trigger_down"][cut] / genWeightSumDict[process] 
    weightSumDict["QCD"] = weightSumDict["QCD200to400"]
    weightSquaredSumDict["QCD"] = weightSquaredSumDict["QCD200to400"]
    weightSumDict["TTbar"] = weightSumDict["TTTo4Q"]
    weightSquaredSumDict["TTbar"] = weightSquaredSumDict["TTTo4Q"]
    for i in range(len(weightSumDict["QCD"])):
        weightSumDict["QCD"][i] = weightSumDict["QCD40to70"][i]+weightSumDict["QCD70to100"][i]+weightSumDict["QCD100to200"][i]+weightSumDict["QCD"][i]+weightSumDict["QCD400to600"][i]+weightSumDict["QCD600to800"][i]+weightSumDict["QCD800to1000"][i]+weightSumDict["QCD1000to1200"][i]+weightSumDict["QCD1200to1500"][i]+weightSumDict["QCD1500to2000"][i]+weightSumDict["QCD2000"][i]
        weightSquaredSumDict["QCD"][i] = weightSquaredSumDict["QCD40to70"][i]+weightSquaredSumDict["QCD70to100"][i]+weightSquaredSumDict["QCD100to200"][i]+weightSquaredSumDict["QCD"][i]+weightSquaredSumDict["QCD400to600"][i]+weightSquaredSumDict["QCD600to800"][i]+weightSquaredSumDict["QCD800to1000"][i]+weightSquaredSumDict["QCD1000to1200"][i]+weightSquaredSumDict["QCD1200to1500"][i]+weightSquaredSumDict["QCD1500to2000"][i]+weightSquaredSumDict["QCD2000"][i]
        weightSumDict["TTbar"][i] = weightSumDict["TTbar"][i]+weightSumDict["TTToLNu2Q"][i]
        weightSquaredSumDict["TTbar"][i] = weightSquaredSumDict["TTbar"][i]+weightSquaredSumDict["TTToLNu2Q"][i]
    customWeights["QCD"] = {}
    customWeights["QCD_PU_up"] = {}
    customWeights["QCD_PU_down"] = {}
    customWeights["QCD_Trigger_up"] = {}
    customWeights["QCD_Trigger_down"] = {}
    customWeights["TTbar"] = {}
    customWeights["TTbar_PU_up"] = {}
    customWeights["TTbar_PU_down"] = {}
    customWeights["TTbar_Trigger_up"] = {}
    customWeights["TTbar_Trigger_down"] = {}
    customWeights["QCD_squared"] = {}
    customWeights["TTbar_squared"] = {}
    customWeights["QCD_nEvents"] = {}
    customWeights["TTbar_nEvents"] = {}
    for i in range(len(bin_namesCustom)):
        cut = bin_namesCustom[i]
        customWeights["QCD"][cut] = customWeights["QCD40to70"][cut]+customWeights["QCD70to100"][cut]+customWeights["QCD100to200"][cut]+customWeights["QCD200to400"][cut]+customWeights["QCD400to600"][cut]+customWeights["QCD600to800"][cut]+customWeights["QCD800to1000"][cut]+customWeights["QCD1000to1200"][cut]+customWeights["QCD1200to1500"][cut]+customWeights["QCD1500to2000"][cut]+customWeights["QCD2000"][cut]
        customWeights["QCD_PU_up"][cut] = customWeights["QCD40to70_PU_up"][cut]+customWeights["QCD70to100_PU_up"][cut]+customWeights["QCD100to200_PU_up"][cut]+customWeights["QCD200to400_PU_up"][cut]+customWeights["QCD400to600_PU_up"][cut]+customWeights["QCD600to800_PU_up"][cut]+customWeights["QCD800to1000_PU_up"][cut]+customWeights["QCD1000to1200_PU_up"][cut]+customWeights["QCD1200to1500_PU_up"][cut]+customWeights["QCD1500to2000_PU_up"][cut]+customWeights["QCD2000_PU_up"][cut]
        customWeights["QCD_Trigger_up"][cut] = customWeights["QCD40to70_Trigger_up"][cut]+customWeights["QCD70to100_Trigger_up"][cut]+customWeights["QCD100to200_Trigger_up"][cut]+customWeights["QCD200to400_Trigger_up"][cut]+customWeights["QCD400to600_Trigger_up"][cut]+customWeights["QCD600to800_Trigger_up"][cut]+customWeights["QCD800to1000_Trigger_up"][cut]+customWeights["QCD1000to1200_Trigger_up"][cut]+customWeights["QCD1200to1500_Trigger_up"][cut]+customWeights["QCD1500to2000_Trigger_up"][cut]+customWeights["QCD2000_Trigger_up"][cut]
        customWeights["QCD_Trigger_down"][cut] = customWeights["QCD40to70_Trigger_down"][cut]+customWeights["QCD70to100_Trigger_down"][cut]+customWeights["QCD100to200_Trigger_down"][cut]+customWeights["QCD200to400_Trigger_down"][cut]+customWeights["QCD400to600_Trigger_down"][cut]+customWeights["QCD600to800_Trigger_down"][cut]+customWeights["QCD800to1000_Trigger_down"][cut]+customWeights["QCD1000to1200_Trigger_down"][cut]+customWeights["QCD1200to1500_Trigger_down"][cut]+customWeights["QCD1500to2000_Trigger_down"][cut]+customWeights["QCD2000_Trigger_down"][cut]
        customWeights["QCD_PU_down"][cut] = customWeights["QCD40to70_PU_down"][cut]+customWeights["QCD70to100_PU_down"][cut]+customWeights["QCD100to200_PU_down"][cut]+customWeights["QCD200to400_PU_down"][cut]+customWeights["QCD400to600_PU_down"][cut]+customWeights["QCD600to800_PU_down"][cut]+customWeights["QCD800to1000_PU_down"][cut]+customWeights["QCD1000to1200_PU_down"][cut]+customWeights["QCD1200to1500_PU_down"][cut]+customWeights["QCD1500to2000_PU_down"][cut]+customWeights["QCD2000_PU_down"][cut]
        customWeights["QCD_squared"][cut] = customWeights["QCD40to70_squared"][cut]+customWeights["QCD70to100_squared"][cut]+customWeights["QCD100to200_squared"][cut]+customWeights["QCD200to400_squared"][cut]+customWeights["QCD400to600_squared"][cut]+customWeights["QCD600to800_squared"][cut]+customWeights["QCD800to1000_squared"][cut]+customWeights["QCD1000to1200_squared"][cut]+customWeights["QCD1200to1500_squared"][cut]+customWeights["QCD1500to2000_squared"][cut]+customWeights["QCD2000_squared"][cut]
        customWeights["QCD_nEvents"][cut] = customWeights["QCD40to70_nEvents"][cut]+customWeights["QCD70to100_nEvents"][cut]+customWeights["QCD100to200_nEvents"][cut]+customWeights["QCD200to400_nEvents"][cut]+customWeights["QCD400to600_nEvents"][cut]+customWeights["QCD600to800_nEvents"][cut]+customWeights["QCD800to1000_nEvents"][cut]+customWeights["QCD1000to1200_nEvents"][cut]+customWeights["QCD1200to1500_nEvents"][cut]+customWeights["QCD1500to2000_nEvents"][cut]+customWeights["QCD2000_nEvents"][cut]
        customWeights["TTbar"][cut] = customWeights["TTTo4Q"][cut]+customWeights["TTToLNu2Q"][cut]
        customWeights["TTbar_PU_up"][cut] = customWeights["TTTo4Q_PU_up"][cut]+customWeights["TTToLNu2Q_PU_up"][cut]
        customWeights["TTbar_PU_down"][cut] = customWeights["TTTo4Q_PU_down"][cut]+customWeights["TTToLNu2Q_PU_down"][cut]
        customWeights["TTbar_Trigger_up"][cut] = customWeights["TTTo4Q_Trigger_up"][cut]+customWeights["TTToLNu2Q_Trigger_up"][cut]
        customWeights["TTbar_Trigger_down"][cut] = customWeights["TTTo4Q_Trigger_down"][cut]+customWeights["TTToLNu2Q_Trigger_down"][cut]
        customWeights["TTbar_squared"][cut] = customWeights["TTTo4Q_squared"][cut]+customWeights["TTToLNu2Q_squared"][cut]
        customWeights["TTbar_nEvents"][cut] = customWeights["TTTo4Q_nEvents"][cut]+customWeights["TTToLNu2Q_nEvents"][cut]
    '''
    stopMassArray = [200,400,600,800]
    stopLifetimeArray = ["0p1","0p3","0p7",1,3,10]
    #stopLifetimeArray = ["0p1","0p3","0p7"]
    stopRawEventsArray = []
    stopWeightedEventsArray = []
    stopWeightedEventsArray_PU_up = []
    stopWeightedEventsArray_PU_down = []
    stopWeightedEventsArray_Trigger_up = []
    stopWeightedEventsArray_Trigger_down = []
    for i in range(3):
        stopRawEventsArrayBin = []
        stopWeightedEventsArrayBin = []
        stopWeightedEventsArrayBin_PU_up = []
        stopWeightedEventsArrayBin_PU_down = []
        stopWeightedEventsArrayBin_Trigger_up = []
        stopWeightedEventsArrayBin_Trigger_down = []
        for mass in stopMassArray:
            singleMassRawEventsArray = []
            singleMassWeightedEventsArray = []
            singleMassWeightedEventsArray_PU_up = []
            singleMassWeightedEventsArray_PU_down = []
            singleMassWeightedEventsArray_Trigger_up = []
            singleMassWeightedEventsArray_Trigger_down = []
            for lifetime in stopLifetimeArray:
                singleMassRawEventsArray.append(customWeights[f'Stop-M{mass}-cT{lifetime}_nEvents'][bin_namesCustom[-1-i]])
                nominal = customWeights[f'Stop-M{mass}-cT{lifetime}'][bin_namesCustom[-1-i]]
                pu_up = customWeights[f'Stop-M{mass}-cT{lifetime}_PU_up'][bin_namesCustom[-1-i]]
                pu_down = customWeights[f'Stop-M{mass}-cT{lifetime}_PU_down'][bin_namesCustom[-1-i]]
                singleMassWeightedEventsArray.append(round(nominal,2))
                singleMassWeightedEventsArray_PU_up.append(round(1+((pu_up-nominal)/nominal),3))
                singleMassWeightedEventsArray_PU_down.append(round(1+((pu_down-nominal)/nominal),3))
                trigger_up = customWeights[f'Stop-M{mass}-cT{lifetime}_Trigger_up'][bin_namesCustom[-1-i]]
                trigger_down = customWeights[f'Stop-M{mass}-cT{lifetime}_Trigger_down'][bin_namesCustom[-1-i]]
                singleMassWeightedEventsArray_Trigger_up.append(round(1+((trigger_up-nominal)/nominal),3))
                singleMassWeightedEventsArray_Trigger_down.append(round(1+((trigger_down-nominal)/nominal),3))
            stopRawEventsArrayBin.append(singleMassRawEventsArray)
            stopWeightedEventsArrayBin.append(singleMassWeightedEventsArray)
            stopWeightedEventsArrayBin_PU_up.append(singleMassWeightedEventsArray_PU_up)
            stopWeightedEventsArrayBin_PU_down.append(singleMassWeightedEventsArray_PU_down)
            stopWeightedEventsArrayBin_Trigger_up.append(singleMassWeightedEventsArray_Trigger_up)
            stopWeightedEventsArrayBin_Trigger_down.append(singleMassWeightedEventsArray_Trigger_down)
        stopRawEventsArray.append(stopRawEventsArrayBin)
        stopWeightedEventsArray.append(stopWeightedEventsArrayBin)
        stopWeightedEventsArray_PU_up.append(stopWeightedEventsArrayBin_PU_up)
        stopWeightedEventsArray_PU_down.append(stopWeightedEventsArrayBin_PU_down)
        stopWeightedEventsArray_Trigger_up.append(stopWeightedEventsArrayBin_Trigger_up)
        stopWeightedEventsArray_Trigger_down.append(stopWeightedEventsArrayBin_Trigger_down)

    for i in range(3):
        print("bin:",bin_namesCustom[-1-i])
        print("stop raw array:",stopRawEventsArray[i])
        print("stop weighted array:",stopWeightedEventsArray[i])
        print("stop PU up uncertainty",stopWeightedEventsArray_PU_up[i])
        print("stop PU down uncertainty",stopWeightedEventsArray_PU_down[i])
        print("stop Trigger up uncertainty",stopWeightedEventsArray_Trigger_up[i])
        print("stop Trigger down uncertainty",stopWeightedEventsArray_Trigger_down[i])

    higgsMassArray = [15,23,30,40,55]
    higgsLifetimeArray = ["0p1","1","10"]
    higgsRawEventsArray = []
    higgsWeightedEventsArray = []
    higgsWeightedEventsArray_PU_up = []
    higgsWeightedEventsArray_PU_down = []
    higgsWeightedEventsArray_Trigger_up = []
    higgsWeightedEventsArray_Trigger_down = []
    for i in range(3):
        higgsRawEventsArrayBin = []
        higgsWeightedEventsArrayBin = []
        higgsWeightedEventsArrayBin_PU_up = []
        higgsWeightedEventsArrayBin_PU_down = []
        higgsWeightedEventsArrayBin_Trigger_up = []
        higgsWeightedEventsArrayBin_Trigger_down = []
        for mass in higgsMassArray:
            singleMassRawEventsArray = []
            singleMassWeightedEventsArray = []
            singleMassWeightedEventsArray_PU_up = []
            singleMassWeightedEventsArray_PU_down = []
            singleMassWeightedEventsArray_Trigger_up = []
            singleMassWeightedEventsArray_Trigger_down = []
            for lifetime in higgsLifetimeArray:
                singleMassRawEventsArray.append(customWeights[f'Hto2Sto4D-cT{lifetime}-MS{mass}_nEvents'][bin_namesCustom[-1-i]])
                nominal = customWeights[f'Hto2Sto4D-cT{lifetime}-MS{mass}'][bin_namesCustom[-1-i]] * (52.23/8)
                pu_up = customWeights[f'Hto2Sto4D-cT{lifetime}-MS{mass}_PU_up'][bin_namesCustom[-1-i]] * (52.23/8)
                pu_down = customWeights[f'Hto2Sto4D-cT{lifetime}-MS{mass}_PU_down'][bin_namesCustom[-1-i]] * (52.23/8)
                singleMassWeightedEventsArray.append(round(nominal,2))
                singleMassWeightedEventsArray_PU_up.append(round(1+((pu_up-nominal)/nominal),3))
                singleMassWeightedEventsArray_PU_down.append(round(1+((pu_down-nominal)/nominal),3))
                trigger_up = customWeights[f'Hto2Sto4D-cT{lifetime}-MS{mass}_Trigger_up'][bin_namesCustom[-1-i]] * (52.23/8)
                trigger_down = customWeights[f'Hto2Sto4D-cT{lifetime}-MS{mass}_Trigger_down'][bin_namesCustom[-1-i]] * (52.23/8)
                singleMassWeightedEventsArray_Trigger_up.append(round(1+((trigger_up-nominal)/nominal),3))
                singleMassWeightedEventsArray_Trigger_down.append(round(1+((trigger_down-nominal)/nominal),3))
            higgsRawEventsArrayBin.append(singleMassRawEventsArray)
            higgsWeightedEventsArrayBin.append(singleMassWeightedEventsArray)
            higgsWeightedEventsArrayBin_PU_up.append(singleMassWeightedEventsArray_PU_up)
            higgsWeightedEventsArrayBin_PU_down.append(singleMassWeightedEventsArray_PU_down)
            higgsWeightedEventsArrayBin_Trigger_up.append(singleMassWeightedEventsArray_Trigger_up)
            higgsWeightedEventsArrayBin_Trigger_down.append(singleMassWeightedEventsArray_Trigger_down)
        higgsRawEventsArray.append(higgsRawEventsArrayBin)
        higgsWeightedEventsArray.append(higgsWeightedEventsArrayBin)
        higgsWeightedEventsArray_PU_up.append(higgsWeightedEventsArrayBin_PU_up)
        higgsWeightedEventsArray_PU_down.append(higgsWeightedEventsArrayBin_PU_down)
        higgsWeightedEventsArray_Trigger_up.append(higgsWeightedEventsArrayBin_Trigger_up)
        higgsWeightedEventsArray_Trigger_down.append(higgsWeightedEventsArrayBin_Trigger_down)

    for i in range(3):
        print("bin:",bin_namesCustom[-1-i])
        print("higgs raw array:",higgsRawEventsArray[i])
        print("higgs weighted array:",higgsWeightedEventsArray[i])
        print("higgs PU up uncertainty",higgsWeightedEventsArray_PU_up[i])
        print("higgs PU down uncertainty",higgsWeightedEventsArray_PU_down[i])
        print("higgs Trigger up uncertainty",higgsWeightedEventsArray_Trigger_up[i])
        print("higgs Trigger down uncertainty",higgsWeightedEventsArray_Trigger_down[i])
    '''
    nevents = customWeights["QCD_nEvents"][bin_namesCustom[-1]] + customWeights["TTbar_nEvents"][bin_namesCustom[-1]]
    nominal = customWeights["QCD"][bin_namesCustom[-1]] + customWeights["TTbar"][bin_namesCustom[-1]]
    pu_up = customWeights["QCD_PU_up"][bin_namesCustom[-1]] + customWeights["TTbar_PU_up"][bin_namesCustom[-1]]
    pu_down = customWeights["QCD_PU_down"][bin_namesCustom[-1]] + customWeights["TTbar_PU_down"][bin_namesCustom[-1]]
    trigger_up = customWeights["QCD_Trigger_up"][bin_namesCustom[-1]] + customWeights["TTbar_Trigger_up"][bin_namesCustom[-1]]
    trigger_down = customWeights["QCD_Trigger_down"][bin_namesCustom[-1]] + customWeights["TTbar_Trigger_down"][bin_namesCustom[-1]]
    print("bkg raw events:",nevents)
    print("bkg weighted events:",round(nominal,2))
    print("bkg PU up uncertainty",round(1+((pu_up-nominal)/nominal),3))
    print("bkg PU down uncertainty",round(1+((pu_down-nominal)/nominal),3))
    print("bkg Trigger up uncertainty",round(1+((trigger_up-nominal)/nominal),3))
    print("bkg Trigger down uncertainty",round(1+((trigger_down-nominal)/nominal),3))

    for process in list(signalDict.keys())+["TTbar","QCD"]:
        print("events passing full selection for process",process,":",customWeights[process+'_nEvents'][bin_namesCustom[-1]])
        latex_table +=  f"{process}"
        for i in range(len(weightSumDict[process])):
            clop_unc = intervals.clopper_pearson_interval(weightSumDict[process][i],weightSumDict[process][0])
            stat_unc = np.sqrt(weightSquaredSumDict[process][i])
            efficiency = weightSumDict[process][i]
            formatString = ".1g"
            if(doPercents):
                efficiency = efficiency / weightSumDict[process][0]
                stat_unc = efficiency * np.sqrt(((stat_unc/weightSumDict[process][i])**2)+((np.sqrt(weightSquaredSumDict[process][0])/weightSumDict[process][0])**2))
            else:
                clop_unc = clop_unc * weightSumDict[process][0]
            if process in ["TTbar","QCD"]:
                formatString = ".2E"
            if(efficiency>0):
                latex_table +=  f" & {efficiency:.3g} $\pm$ {stat_unc:.1g}"
            else:
                latex_table +=  f" & {efficiency:.3g}$^{{+{clop_unc[1]-efficiency:{formatString}}}}_{{-{efficiency-clop_unc[0]:{formatString}}}}$"
        #Custom Cutflows
        for i in range(len(bin_namesCustom)):
            clop_unc = intervals.clopper_pearson_interval(customWeights[process][bin_namesCustom[i]],weightSumDict[process][0])
            stat_unc = np.sqrt(customWeights[process+'_squared'][bin_namesCustom[i]])
            efficiency = customWeights[process][bin_namesCustom[i]]
            formatString = ".1g"
            if(doPercents):
                efficiency = efficiency / weightSumDict[process][0]
                stat_unc = efficiency * np.sqrt(((stat_unc/customWeights[process][bin_namesCustom[i]])**2)+((np.sqrt(weightSquaredSumDict[process][0])/weightSumDict[process][0])**2))
            else:
                clop_unc = clop_unc * weightSumDict[process][0]
            if process in ["TTbar","QCD"] and doPercents:
                formatString = ".2E"
            if(efficiency>0):
                latex_table +=  f" & {efficiency:.3g} $\pm$ {stat_unc:.1g}"
            else:
                latex_table +=  f" & {efficiency:.3g}$^{{+{clop_unc[1]-efficiency:{formatString}}}}_{{-{efficiency-clop_unc[0]:{formatString}}}}$"
        latex_table += "\\\\\n"

    latex_table += "\\hline\n"
    latex_table += "\\end{tabular}}\n"
    latex_table += "\\caption{Cutflow table}\n"
    latex_table += "\\label{tab:cutflow}\n"
    latex_table += "\\end{table}"

    #Add sensitivity

    splitStrings = latex_table.split("\\hline\n")
    processString = splitStrings[2]
    substrings = processString.split("\\\\")
    final_table = splitStrings[0]+"\\hline\n"+splitStrings[1]+"\\hline\n"
    for string in substrings:
        process = string.split(' &')[0]
        process = process.replace('\n','')
        if(process in signalDict):
            if(len(bin_namesCustom)):
                string += f" & {customWeights[process][bin_namesCustom[-1]]/np.sqrt(customWeights[process][bin_namesCustom[-1]]+customWeights['QCD'][bin_namesCustom[-1]]+customWeights['TTbar'][bin_namesCustom[-1]]):.2f} & {(customWeights[process][bin_namesCustom[-1]]/weightSumDict[process][0])/(1+np.sqrt(customWeights['QCD'][bin_namesCustom[-1]]+customWeights['TTbar'][bin_namesCustom[-1]])):.3f}"
            else:
                string += f" & {weightSumDict[process][-1]/np.sqrt(weightSumDict[process][-1]+weightSumDict['QCD'][-1]+weightSumDict['TTbar'][-1]):.3f}" 
        elif(process in ["QCD","TTbar"]):
            string += f" & & "
        final_table += string + "\\\\"
    final_table = final_table[:-2]
    final_table += "\\hline\n" + splitStrings[3]

    print(final_table) 

    
if __name__=="__main__":
    main()
