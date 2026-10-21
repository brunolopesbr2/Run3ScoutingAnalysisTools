import ROOT
ROOT.EnableImplicitMT()

ROOT.gInterpreter.Declare("""
template <typename T>
ROOT::VecOps::RVec<double> clampVec(const ROOT::VecOps::RVec<T>& v, double upper) {
    ROOT::VecOps::RVec<double> out(v.size());
    for (size_t i = 0; i < v.size(); i++) {
        out[i] = (v[i] > upper) ? upper : static_cast<double>(v[i]);
    }
    return out;
}
""")

from TMWeights_dsets import signalDict, dataDict, backgroundDict

upperdPVV = 2.2   #Values to crop the weight maps. This fixes the overflow bins.
upperdPVV3D = 5

HTcut = 400

## Create the histogram dict
dPVV2D3D = {}

#Signal -- regular tree maker
print("Processing the Signal trees")
for signal in signalDict.keys():
    print(f"Signal: {signal}")
    
    main_chain = ROOT.TChain("scoutingTree/tmTree")
    main_chain.Add(signalDict[signal])
    
    df = ROOT.RDataFrame(main_chain)

    df = df.Filter("genVert_dVV_TM > 0.036")
    #df = df.Filter("abs(genVert_dPhiVV_TM) > 0.5")
    df = df.Filter("All(genVert_deltaR_TM > 0.4)")
    df = df.Filter(f"hltHTProxy > {HTcut}")

    nEvts = df.Count().GetValue()
    print(f'Number of events after the cuts: {nEvts}')

    df = df.Define("dPVV_clamped", f"clampVec(genVert_dBV2D_TM, {upperdPVV - 1e-6})") #1e-6 just to fall within the last bin
    df = df.Define("dPVV3D_clamped",   f"clampVec(genVert_dBV3D_TM, {upperdPVV3D - 1e-6})")

    h = df.Histo2D(("dPVV2D3D", f"Reweighting Variables; dPVV 2D [cm]; dPVV 3D [cm]", 20, 0, upperdPVV, 20, 0, upperdPVV3D), "dPVV_clamped", "dPVV3D_clamped", "weight")
    dPVV2D3D[signal] = h.GetValue()
    if (dPVV2D3D[signal].Integral() > 0):
        dPVV2D3D[signal].Scale(1.0 / dPVV2D3D[signal].Integral())

#Data -- TM events
print("Processing Data TM trees")
for data in dataDict.keys():
    print(f"Data Era: {data}")
    main_chain = ROOT.TChain("vertexEffTree/objectTree")
    main_chain.Add(dataDict[data])
    df = ROOT.RDataFrame(main_chain)

    #df = df.Filter("nPreselJets > 2")
    df = df.Filter("jets_dR > 0.4")
    df = df.Filter(f"hltHTProxy > {HTcut}")
    df = df.Filter("LLP_PtSum > 0")
    df = df.Filter("nMovedTracks > 3")

    nEvts = df.Count().GetValue()
    print(f'Number of events after the cuts: {nEvts}')

    df = df.Define("dPVV_clamped", f"moveVertex_dPVV > {upperdPVV - 1e-6} ? {upperdPVV - 1e-6} : moveVertex_dPVV") #1e-6 value to make sure it falls within the last bin
    df = df.Define("dPVV3D_clamped",   f"moveVertex_dPVV3D > {upperdPVV3D - 1e-6} ? {upperdPVV3D - 1e-6} : moveVertex_dPVV3D")

    h = df.Histo2D(("dPVV2D3D", f"Reweighting Variables; dPVV 2D [cm]; dPVV 3D [cm]", 20, 0, upperdPVV, 20, 0, upperdPVV3D), f"dPVV_clamped", f"dPVV3D_clamped", "weight_noTrigger")
    dPVV2D3D[data] = h.GetValue()
    if dPVV2D3D[data].Integral() > 0:
        dPVV2D3D[data].Scale(1.0 / dPVV2D3D[data].Integral())


#For the full 2024 dataset
print("Now processing the full TM data combined")
main_chain = ROOT.TChain("vertexEffTree/objectTree")
for data in dataDict.keys():
    main_chain.Add(dataDict[data])
df = ROOT.RDataFrame(main_chain)

#df = df.Filter("nPreselJets > 2")
df = df.Filter("jets_dR > 0.4")
df = df.Filter(f"hltHTProxy > {HTcut}")
df = df.Filter("LLP_PtSum > 0")
df = df.Filter("nMovedTracks > 3")

nEvts = df.Count().GetValue()
print(f'Number of events after the cuts: {nEvts}')

df = df.Define("dPVV_clamped", f"moveVertex_dPVV > {upperdPVV - 1e-6} ? {upperdPVV - 1e-6} : moveVertex_dPVV") #1e-6 value to make sure it falls within the last bin
df = df.Define("dPVV3D_clamped",   f"moveVertex_dPVV3D > {upperdPVV3D - 1e-6} ? {upperdPVV3D - 1e-6} : moveVertex_dPVV3D")

h = df.Histo2D(("dPVV2D3D", f"Reweighting Variables; dPVV 2D [cm]; dPVV 3D [cm]", 20, 0, upperdPVV, 20, 0, upperdPVV3D), f"dPVV_clamped", f"dPVV3D_clamped", "weight_noTrigger")
dPVV2D3D['2024'] = h.GetValue()
if dPVV2D3D['2024'].Integral() > 0:
    dPVV2D3D['2024'].Scale(1.0 / dPVV2D3D['2024'].Integral())

#Background MC -- TM events. Add all backgrounds together with the corresponding weights
print("Processing the Background MC TM tree")

dPVV2D3D['MC'] = ROOT.TH2D("dPVV2D3D", "Reweighting Variables; dPVV 2D [cm]; dPVV 3D [cm]", 20, 0, upperdPVV, 20, 0, upperdPVV3D)
dPVV2D3D['MC'].SetDirectory(0)
dPVV2D3D['MC'].Sumw2()

for bg in backgroundDict.keys():
    print(f"Process: {bg}")
    f = ROOT.TFile.Open(backgroundDict[bg])
    h = f.Get("triggerFilter/genWeightsSkim")
    ibin = h.GetXaxis().FindBin("None")
    sum_gen_weights = h.GetBinContent(ibin)
    f.Close()
    print(f"Gen weight sum: {sum_gen_weights}")

    main_chain = ROOT.TChain("vertexEffTree/objectTree")
    main_chain.Add(backgroundDict[bg])
    df = ROOT.RDataFrame(main_chain)

    #df = df.Filter("nPreselJets > 2")
    df = df.Filter("jets_dR > 0.4")
    df = df.Filter(f"hltHTProxy > {HTcut}")
    df = df.Filter("LLP_PtSum > 0")
    df = df.Filter("nMovedTracks > 3")

    nEvts = df.Count().GetValue()
    print(f'Number of events after the cuts: {nEvts}')

    df = df.Define("normWeight", f"weight_noTrigger/{sum_gen_weights}")
    df = df.Define("dPVV_clamped", f"moveVertex_dPVV > {upperdPVV - 1e-6} ? {upperdPVV - 1e-6} : moveVertex_dPVV") #1e-6 value to make sure it falls within the last bin
    df = df.Define("dPVV3D_clamped",   f"moveVertex_dPVV3D > {upperdPVV3D - 1e-6} ? {upperdPVV3D - 1e-6} : moveVertex_dPVV3D")

    dPVV2D3D_tmp = df.Histo2D((f"dPVV2D3D_{bg}", f"Reweighting Variables; dPVV 2D [cm]; dPVV 3D [cm]", 20, 0, upperdPVV, 20, 0, upperdPVV3D), f"dPVV_clamped", f"dPVV3D_clamped", "normWeight")

    dPVV2D3D['MC'].Add(dPVV2D3D_tmp.GetPtr())

if(dPVV2D3D['MC'].Integral() > 0):
    dPVV2D3D['MC'].Scale(1.0 / dPVV2D3D['MC'].Integral())

## Write to ROOT file
print("Creating the output file...")
weightsFile = ROOT.TFile(f"TMLifetimeWeights.root", "RECREATE")
for era in list(dataDict.keys()) + ["2024", 'MC']:
    eraDir = weightsFile.mkdir(era)
    for signal in signalDict.keys():
        hist1 = dPVV2D3D[signal]
        hist2 = dPVV2D3D[era]

        weightMap = hist1.Clone(signal)
        weightMap.Divide(hist2)

        eraDir.cd()     
        weightMap.Write()

weightsFile.Close()

print(f'Created file TMLifetimeWeights.root')