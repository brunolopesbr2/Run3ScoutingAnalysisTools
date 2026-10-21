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

includeRandomCrossing = False

if (includeRandomCrossing):
    appendString = "_withCloseTracks"
else:
    appendString = ""

upperNetP = 750   #Values to crop the weight maps. This fixes the overflow bins.
upperDR   = 6

HTcut = 400

## Create the histogram dict
dRvsSumPt = {}

#Signal -- regular tree maker
print("Processing the Signal trees")
for signal in signalDict.keys():
    print(f"Signal: {signal}")
    
    main_chain = ROOT.TChain("scoutingTree/tmTree")
    main_chain.Add(signalDict[signal])
    
    df = ROOT.RDataFrame(main_chain)

    df = df.Filter("genVert_dVV_TM > 0.036")
    df = df.Filter("abs(genVert_dPhiVV_TM) > 0.5")
    df = df.Filter("All(genVert_deltaR_TM > 0.4)")
    df = df.Filter(f"hltHTProxy > {HTcut}")

    nEvts = df.Count().GetValue()
    print(f'Number of events after the cuts: {nEvts}')

    df = df.Define("netP_clamped", f"clampVec(genVert_netP_TM, {upperNetP - 1e-6})") #1e-6 just to fall within the last bin
    df = df.Define("dR_clamped",   f"clampVec(genVert_deltaR_TM, {upperDR - 1e-6})")

    h = df.Histo2D((f"dRvsSumPt", "Reweighting Variables; Vertex net momentum [GeV]; Vertex delta R", 15, 0, upperNetP, 30, 0, upperDR), f"netP_clamped", f"dR_clamped", "weight")
    dRvsSumPt[signal] = h.GetValue()
    if dRvsSumPt[signal].Integral() > 0:
        dRvsSumPt[signal].Scale(1.0 / dRvsSumPt[signal].Integral())


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

    df = df.Define("netP_clamped", f"LLP_netP{appendString} > {upperNetP - 1e-6} ? {upperNetP - 1e-6} : LLP_netP{appendString}") #1e-6 value to make sure it falls within the last bin
    df = df.Define("dR_clamped",   f"LLP_dR{appendString} > {upperDR - 1e-6} ? {upperDR - 1e-6} : LLP_dR{appendString}")

    h =  df.Histo2D((f"dRvsSumPt", "Reweighting Variables; Vertex net momentum [GeV]; Vertex delta R", 15, 0, upperNetP, 30, 0, upperDR), "netP_clamped", "dR_clamped", "weight_noTrigger")
    dRvsSumPt[data] = h.GetValue()
    if dRvsSumPt[data].Integral() > 0:
        dRvsSumPt[data].Scale(1.0 / dRvsSumPt[data].Integral())

#For the full 2024 dataset
print("Now processing the full TM data combined")
main_chain = ROOT.TChain("vertexEffTree/objectTree")
for data in dataDict.keys():
    main_chain.Add(dataDict[data])
df = ROOT.RDataFrame(main_chain)

df = df.Filter("jets_dR > 0.4")
df = df.Filter(f"hltHTProxy > {HTcut}")
df = df.Filter("nMovedTracks > 3")
df = df.Filter("LLP_PtSum > 0")

nEvts = df.Count().GetValue()
print(f'Number of events after the cuts: {nEvts}')

df = df.Define("netP_clamped", f"LLP_netP{appendString} > {upperNetP - 1e-6} ? {upperNetP - 1e-6} : LLP_netP{appendString}") #1e-6 value to make sure it falls within the last bin
df = df.Define("dR_clamped",   f"LLP_dR{appendString} > {upperDR - 1e-6} ? {upperDR - 1e-6} : LLP_dR{appendString}")

h = df.Histo2D((f"dRvsSumPt", "Reweighting Variables; Vertex net momentum [GeV]; Vertex delta R", 15, 0, upperNetP, 30, 0, upperDR),"netP_clamped", "dR_clamped", "weight_noTrigger")
dRvsSumPt['2024'] = h.GetValue()
if dRvsSumPt['2024'].Integral() > 0:
    dRvsSumPt['2024'].Scale(1.0 / dRvsSumPt['2024'].Integral())

#Background MC -- TM events. Add all backgrounds together with the corresponding weights
print("Processing the Background MC TM tree")

dRvsSumPt['MC'] = ROOT.TH2D(f"dRvsSumPt_total", "Reweighting Variables; Vertex net momentum [GeV]; Vertex delta R", 15, 0, upperNetP, 30, 0, upperDR)
dRvsSumPt['MC'].SetDirectory(0)
dRvsSumPt['MC'].Sumw2()

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

    df = df.Filter("jets_dR > 0.4")
    df = df.Filter(f"hltHTProxy > {HTcut}")
    df = df.Filter("nMovedTracks > 3")
    df = df.Filter("LLP_PtSum > 0")

    nEvts = df.Count().GetValue()
    print(f'Number of events after the cuts: {nEvts}')

    df = df.Define("normWeight", f"weight_noTrigger/{sum_gen_weights}")
    df = df.Define("netP_clamped", f"LLP_netP{appendString} > {upperNetP - 1e-6} ? {upperNetP - 1e-6} : LLP_netP{appendString}") #1e-6 value to make sure it falls within the last bin
    df = df.Define("dR_clamped",   f"LLP_dR{appendString} > {upperDR - 1e-6} ? {upperDR - 1e-6} : LLP_dR{appendString}")

    dRvsSumPt_tmp = df.Histo2D(
        (f"dRvsSumPt_{bg}", "Reweighting Variables; Vertex net momentum [GeV]; Vertex delta R", 15, 0, upperNetP, 30, 0, upperDR),
        "netP_clamped", "dR_clamped", "normWeight")

    dRvsSumPt['MC'].Add(dRvsSumPt_tmp.GetPtr())
    if dRvsSumPt['MC'].Integral() > 0: 
        dRvsSumPt['MC'].Scale(1.0 / dRvsSumPt['MC'].Integral())

## Write to ROOT file
print("Creating the output file...")
weightsFile = ROOT.TFile(f"TMWeights{appendString}.root", "RECREATE")

for era in list(dataDict.keys()) + ["2024", 'MC']:
    eraDir = weightsFile.mkdir(era)
    for signal in signalDict.keys():
        hist1 = dRvsSumPt[signal]
        hist2 = dRvsSumPt[era]

        weightMap = hist1.Clone(signal)
        weightMap.Divide(hist2)

        eraDir.cd()     
        weightMap.Write()


weightsFile.Close()

print(f'Created file TMWeights{appendString}.root')