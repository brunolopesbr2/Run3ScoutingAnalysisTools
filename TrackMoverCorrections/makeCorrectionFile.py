#!/usr/bin/env python3
"""
Standalone script: produces ONLY the vertex-efficiency correction file.

For each label ("original" = no reweighting, plus every signal in signalDict) it stores
  <label>/ratio_dBV_<N>tks          Data/MC vertex efficiency vs dBV
  <label>/ratio_nCloseSeed_<N>tks   Data/MC vertex efficiency vs total number of close seed tracks
  <label>/raw/{Data,MC}/            weighted den_<var>, num2D_<var> (x = variable, y = nTracks clamped at 9)
                                    and num_<var>_<N>tks (weighted numerator per nTracks bin)
with N = 3..8 (exactly N tracks in the matched vertex) and N = 9 (>= 9 tracks).

Flow of the script:
  1. settings
  2. load the weight maps (SUSY or Higgs files, depending on the signal label)
  3. build the dataframes (one per background, one for data)
  4. book all histograms (lazy), then run ALL event loops at once with RunGraphs
  5. sum the backgrounds, project the 2D numerators into nTracks bins
  6. write the ratios and the raw histograms to the output file

Usage:
    python make_vertex_eff_corrections.py
"""
import time

import numpy as np
import ROOT

from TMWeights_dsets import signalDict, dataDict, backgroundDict

ROOT.gROOT.SetBatch(True)

# =============================================================================
# 1. Settings
# =============================================================================
outputFile = "VertexEffCorrections.root"
nThreads = 0                       #implicit MT threads (0 = all cores)
doLifetimeReweighting = True

eraData = "2024"
eraMC = "MC"
eras = [eraData, eraMC]
labels = ["original"] + list(signalDict.keys())    #"original" = no reweighting

#Selections
baseSel = "jets_dR > 0.4 && hltHTProxy > 400 && LLP_PtSum > 0"
movedSel = "nMovedTracks > 3"      #guard against events without enough tracks to move
vertexSel = "(matchedVertex_dBV > 0.01) && (matchedVertex_dBV < 2.0) && (matchedVertex_dBVerr < 0.005) && (matchedVertex_nTracks > 2)"

#nTracks bins: exactly N tracks, the last entry (9) means >= 9
ntkList = [3, 4, 5, 6, 7, 8, 9]
#nTracks axis of the 2D numerators: one bin per entry of ntkList (bin centres are integers).
#matchedVertex_nTracks is clamped to ntkList[-1] in the dataframe ("nTracks_eff"), so the
#last row of the 2D numerator already holds ">= ntkList[-1] tracks" (no overflow bin is used).
ntkEdges = np.linspace(ntkList[0] - 0.5, ntkList[-1] + 0.5, len(ntkList) + 1, dtype=np.float64)

#Variables the efficiency is measured vs
dBVEdges = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.4, 2.0], dtype=np.float64)
seedEdges = np.linspace(0, 40, 41, dtype=np.float64)
variables = {
    "dBV":        {"column": "dBV_eff",                 "edges": dBVEdges,  "title": "dBV [cm]"},
    "nCloseSeed": {"column": "nCloseTotalTracks_IPsig", "edges": seedEdges, "title": "Total close seed tracks"},
}

#Values to crop the weight maps (fixes the overflow bins), per signal family
upperDR = 6
upperNetP = {"SUSY": 750, "Higgs": 500}
upperdPVV = {"SUSY": 2.2, "Higgs": 2.2}
upperdPVV3D = {"SUSY": 5, "Higgs": 5}
upperEff = 2.0                     #dBV is clamped here (overflow goes into the last bin)

#Weight map files, per signal family
weightFiles = {"SUSY": "TMWeights_SUSY.root", "Higgs": "TMWeights_Higgs.root"}
lifetimeWeightFiles = {"SUSY": "TMLifetimeWeights_SUSY.root", "Higgs": "TMLifetimeWeights_Higgs.root"}

ROOT.EnableImplicitMT(nThreads)


# =============================================================================
# Functions
# =============================================================================
def getFamily(label):
    """'Higgs' if the signal label contains 'Higgs', else 'SUSY'."""
    if "Higgs" in label:
        return "Higgs"
    return "SUSY"


def loadWeightMaps(fileName, prefix, eras, signals):
    """Read the weight maps <era>/<signal> from fileName and push them into the C++ map."""
    print(f"Loading weight maps from {fileName}...")
    weightsFile = ROOT.TFile.Open(fileName)
    for era in eras:
        eraDir = weightsFile.Get(era)
        for signal in signals:
            hist = eraDir.Get(signal)
            hist.SetDirectory(0)  #detach from file so it survives after closing
            keepAlive.append(hist)
            key = f"{prefix}{era}_{signal}"
            ROOT.tm_weight_map[key] = hist
    weightsFile.Close()


def prepareDataframe(df):
    """Selections and the clamped columns used for the weight lookups and the efficiency axes."""
    df = df.Filter(baseSel)
    df = df.Filter(movedSel)

    #netP is clamped differently for each signal family
    for family in upperNetP:
        up = upperNetP[family]
        df = df.Define(f"netP_clamped_{family}", f"LLP_netP > {up - 1e-6} ? {up - 1e-6} : LLP_netP") #1e-6 to make sure it falls within the last bin
    df = df.Define("dR_clamped", f"LLP_dR > {upperDR - 1e-6} ? {upperDR - 1e-6} : LLP_dR")

    #dPVV and dPVV3D (lifetime weights), per signal family
    for family in upperdPVV:
        up = upperdPVV[family]
        up3D = upperdPVV3D[family]
        df = df.Define(f"dPVV_clamped_{family}", f"moveVertex_dPVV > {up - 1e-6} ? {up - 1e-6} : moveVertex_dPVV")
        df = df.Define(f"dPVV3D_clamped_{family}", f"moveVertex_dPVV3D > {up3D - 1e-6} ? {up3D - 1e-6} : moveVertex_dPVV3D")

    #Axes of the efficiency
    df = df.Define("dBV_eff", f"std::min(moveVertex_dBV, {upperEff - 1e-6})")
    df = df.Define("nTracks_eff", f"std::min<int>(matchedVertex_nTracks, {ntkList[-1]})")
    return df


def addWeights(df, era, label):
    """Define the weight column for this label. Returns (df, name of the weight column)."""
    if label == "original":
        return df, "weight_noTrigger"

    family = getFamily(label)
    df = df.Define(f"tmWeight_{label}", f'getTMWeight("{era}_{label}", netP_clamped_{family}, dR_clamped)')
    if doLifetimeReweighting:
        df = df.Define(f"tmLifetimeWeight_{label}", f'getTMWeight("lifetime_{era}_{label}", dPVV_clamped_{family}, dPVV3D_clamped_{family})')
        df = df.Define(f"finalWeight_{label}", f"weight_noTrigger * tmWeight_{label} * tmLifetimeWeight_{label}")
    else:
        df = df.Define(f"finalWeight_{label}", f"weight_noTrigger * tmWeight_{label}")
    return df, f"finalWeight_{label}"


def bookHistograms(df, tag, weightKey):
    """Lazily book, for each variable, one denominator and one 2D (variable, nTracks) numerator.
    Returns two dicts keyed by variable name: dens and nums."""
    dfGood = df.Define("badWeight", f"!std::isfinite({weightKey}) || {weightKey} < 0")
    dfGood = dfGood.Filter("!badWeight")
    dfVertex = dfGood.Filter(vertexSel, "vertex_sel")

    dens = {}
    nums = {}
    for var in variables:
        column = variables[var]["column"]
        edges = variables[var]["edges"]
        nBins = len(edges) - 1

        denModel = ROOT.RDF.TH1DModel(f"den_{var}_{tag}", "", nBins, edges)
        dens[var] = dfGood.Histo1D(denModel, column, weightKey)

        numModel = ROOT.RDF.TH2DModel(f"num_{var}_{tag}", "", nBins, edges, len(ntkEdges) - 1, ntkEdges)
        nums[var] = dfVertex.Histo2D(numModel, column, "nTracks_eff", weightKey)
    return dens, nums


def collectHandles(handleList, dens, nums):
    """Append the booked results to handleList (needed for RunGraphs)."""
    for var in dens:
        handleList.append(dens[var])
        handleList.append(nums[var])


def projectNtk(hist2D, ntk, name):
    """Numerator for matchedVertex_nTracks == ntk (>= ntk for the last entry of ntkList)."""
    ntkBin = hist2D.GetYaxis().FindBin(ntk)
    proj = hist2D.ProjectionX(name, ntkBin, ntkBin)
    proj.SetDirectory(0)
    return proj


def ntkString(ntk):
    if ntk == ntkList[-1]:
        return f">= {ntk}"
    return f"{ntk}"


def make_ratio_hist(eff_data, eff_mc, name, title="", default=1.0):
    """Data/MC efficiency ratio as a TH1D. Bins with no usable ratio get `default` +- 0."""
    tot = eff_data.GetTotalHistogram()
    h = tot.Clone(name)
    h.Reset()
    h.SetDirectory(0)
    h.SetTitle(title)

    for i in range(1, tot.GetNbinsX() + 1):
        y1 = eff_data.GetEfficiency(i)
        y2 = eff_mc.GetEfficiency(i)

        if y1 <= 0 or y2 <= 0:
            #no usable ratio in this bin -> neutral correction, no error
            h.SetBinContent(i, default)
            h.SetBinError(i, 0.0)
            continue

        ratio = y1 / y2
        err_lo = ratio * np.sqrt((eff_data.GetEfficiencyErrorLow(i) / y1)**2 + (eff_mc.GetEfficiencyErrorUp(i) / y2)**2)
        err_hi = ratio * np.sqrt((eff_data.GetEfficiencyErrorUp(i) / y1)**2 + (eff_mc.GetEfficiencyErrorLow(i) / y2)**2)
        h.SetBinContent(i, ratio)
        h.SetBinError(i, 0.5 * (err_lo + err_hi))
    return h


def writeWeighted(hist, name):
    """Write a copy of hist to the current directory.

    Bin contents (sum of weights) and errors (sqrt of sum of squared weights) are untouched.
    The fill counter, shown by ROOT as "Entries" and returned by GetEntries(), is replaced by
    the effective number of entries (sum w)^2 / sum w^2, so it is weight-aware.
    """
    copy = hist.Clone(name)
    copy.SetDirectory(0)
    copy.SetEntries(copy.GetEffectiveEntries())
    copy.Write()


# =============================================================================
# 2. Weight maps
# =============================================================================
#C++ side: a map from a string key -> TH2D*, plus a lookup function
ROOT.gInterpreter.Declare("""
#include <map>
#include <string>
#include "TH2D.h"

static std::map<std::string, TH2D*> tm_weight_map;

double getTMWeight(const std::string& key, double x, double y) {
    auto it = tm_weight_map.find(key);
    if (it == tm_weight_map.end() || it->second == nullptr) {
        return 1.0; // fallback if key not found
    }
    TH2D* h = it->second;
    int binx = h->GetXaxis()->FindBin(x);
    int biny = h->GetYaxis()->FindBin(y);
    double w = h->GetBinContent(binx, biny);
    return w;
}
""")

keepAlive = []   #python references to the weight histograms, so they are not garbage-collected

signalsReweighted = []
for label in labels:
    if label != "original":
        signalsReweighted.append(label)

for family in weightFiles:
    #Only the signals of this family are read from this family's files
    familySignals = []
    for signal in signalsReweighted:
        if getFamily(signal) == family:
            familySignals.append(signal)
    if len(familySignals) == 0:
        continue

    loadWeightMaps(weightFiles[family], "", eras, familySignals)
    if doLifetimeReweighting:
        loadWeightMaps(lifetimeWeightFiles[family], "lifetime_", eras, familySignals)


# =============================================================================
# 3. Dataframes
# =============================================================================
t0 = time.time()
chains = []   #keep the chains alive for the whole run

#MC dataframes (one per background)
dfsMC = {}
for bg in backgroundDict:
    print(f"Building dataframe for {bg}...")
    MCchain = ROOT.TChain("vertexEffTree/objectTree")
    MCchain.Add(backgroundDict[bg])
    chains.append(MCchain)
    dfsMC[bg] = prepareDataframe(ROOT.RDataFrame(MCchain))

#Data dataframe
print("Building dataframe for data...")
DATAchain = ROOT.TChain("vertexEffTree/objectTree")
for data in dataDict:
    DATAchain.Add(dataDict[data])
chains.append(DATAchain)
dfData = prepareDataframe(ROOT.RDataFrame(DATAchain))

#Generator weight sums, used to normalise each MC sample
sumGenWeights = {}
for bg in backgroundDict:
    f = ROOT.TFile.Open(backgroundDict[bg])
    h = f.Get("triggerFilter/genWeightsSkim")
    ibin = h.GetXaxis().FindBin("None")
    sumGenWeights[bg] = h.GetBinContent(ibin)
    f.Close()
    print(f"{bg}: gen weight sum = {sumGenWeights[bg]}")


# =============================================================================
# 4. Book all histograms, then run all the event loops at once
# =============================================================================
denMC = {}     #key: f"{label}_{bg}"  ->  {variable: histogram}
numMC = {}
denData = {}   #key: label            ->  {variable: histogram}
numData = {}
allHandles = []

for label in labels:
    print(f"Booking histograms for {label}...")

    #MC: one booking per background sample
    for bg in dfsMC:
        key = f"{label}_{bg}"
        df, weightKey = addWeights(dfsMC[bg], eraMC, label)
        df = df.Define("w_norm", f"{weightKey}/{sumGenWeights[bg]}")
        dens, nums = bookHistograms(df, f"MC_{key}", "w_norm")
        denMC[key] = dens
        numMC[key] = nums
        collectHandles(allHandles, dens, nums)

    #Data
    df, weightKey = addWeights(dfData, eraData, label)
    dens, nums = bookHistograms(df, f"Data_{label}", weightKey)
    denData[label] = dens
    numData[label] = nums
    collectHandles(allHandles, dens, nums)

print(f"Booking done in {time.time() - t0:.1f} s")

#ONE call runs all the event loops (all backgrounds, data, all labels) together
print("Running the event loops...")
ROOT.RDF.RunGraphs(allHandles)
print(f"Event loops done in {time.time() - t0:.1f} s")


# =============================================================================
# 5. Sum the backgrounds
# =============================================================================
denSummed = {}   #key: f"{sample}_{label}_{variable}", sample = "Data" or "MC"
numSummed = {}

for label in labels:
    for var in variables:
        #MC: add up all the backgrounds
        keyMC = f"MC_{label}_{var}"
        for bg in backgroundDict:
            denBg = denMC[f"{label}_{bg}"][var].GetValue()
            numBg = numMC[f"{label}_{bg}"][var].GetValue()

            if keyMC not in denSummed:
                #first background: start from a copy
                denSummed[keyMC] = denBg.Clone(f"den_{keyMC}")
                denSummed[keyMC].SetDirectory(0)
                numSummed[keyMC] = numBg.Clone(f"num_{keyMC}")
                numSummed[keyMC].SetDirectory(0)
            else:
                denSummed[keyMC].Add(denBg)
                numSummed[keyMC].Add(numBg)

        #Data: a single dataframe, just copy
        keyData = f"Data_{label}_{var}"
        denSummed[keyData] = denData[label][var].GetValue().Clone(f"den_{keyData}")
        denSummed[keyData].SetDirectory(0)
        numSummed[keyData] = numData[label][var].GetValue().Clone(f"num_{keyData}")
        numSummed[keyData].SetDirectory(0)


# =============================================================================
# 6. Write the output file
# =============================================================================
outFile = ROOT.TFile(outputFile, "RECREATE")

for label in labels:
    print(f"Writing {label}...")
    labelDir = outFile.mkdir(label)
    rawDir = labelDir.mkdir("raw")

    #Weighted numerator for each nTracks bin (projection of the 2D numerator)
    numProj = {}
    for sample in ["Data", "MC"]:
        for var in variables:
            for ntk in ntkList:
                numHist2D = numSummed[f"{sample}_{label}_{var}"]
                numProj[f"{sample}_{var}_{ntk}tks"] = projectNtk(numHist2D, ntk, f"num_{sample}_{label}_{var}_{ntk}tks")

    #Raw histograms: weighted denominators, 2D numerators and numerators per nTracks bin
    for sample in ["Data", "MC"]:
        sampleDir = rawDir.mkdir(sample)
        sampleDir.cd()
        for var in variables:
            writeWeighted(denSummed[f"{sample}_{label}_{var}"], f"den_{var}")
            writeWeighted(numSummed[f"{sample}_{label}_{var}"], f"num2D_{var}")
            for ntk in ntkList:
                writeWeighted(numProj[f"{sample}_{var}_{ntk}tks"], f"num_{var}_{ntk}tks")

    #Data/MC ratios
    labelDir.cd()
    for var in variables:
        xTitle = variables[var]["title"]
        for ntk in ntkList:
            effData = ROOT.TEfficiency(numProj[f"Data_{var}_{ntk}tks"], denSummed[f"Data_{label}_{var}"])
            effMC = ROOT.TEfficiency(numProj[f"MC_{var}_{ntk}tks"], denSummed[f"MC_{label}_{var}"])

            title = f"Data/MC vertex efficiency, {ntkString(ntk)} tracks;{xTitle};Data/MC"
            ratio = make_ratio_hist(effData, effMC, f"ratio_{var}_{ntk}tks", title)
            ratio.Write()

    outFile.cd()

outFile.Close()
print(f"Wrote {outputFile} (total {time.time() - t0:.1f} s)")