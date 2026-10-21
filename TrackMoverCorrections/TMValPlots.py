import ROOT
#import cmsstyle as CMS

ROOT.EnableImplicitMT()

# --- Declare the C++ side: a map from a string key -> TH2D*, plus a lookup function ---
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

import os

doLifetimeReweighting = True
doTrackPlots = False
plotsFolder = 'plots_val1'
os.makedirs(plotsFolder, exist_ok=True)
test_signal = "Stop_400_10" #Take some entry of the TMWeights_dsets.py database

#eras = ['2024C', '2024D', '2024E', '2024F', '2024G', '2024H', '2024I', '2024', 'MC']
eras = ['2024', 'MC']
from TMWeights_dsets import signalDict, dataDict, backgroundDict
signals = list(signalDict.keys())

#Load kinematic weights
if "Higgs" in test_signal:
    weightsFile = ROOT.TFile.Open("TMWeights_Higgs.root")
    print("Loading Higgs kinematic weights...")
else:
    weightsFile = ROOT.TFile.Open("TMWeights_SUSY.root")
    print("Loading SUSY kinematic weights...")

for era in eras:
    eraDir = weightsFile.Get(era)
    for signal in signals:
        hist = eraDir.Get(signal)
        hist.SetDirectory(0)  # detach from file so it survives after closing
        key = f"{era}_{signal}"
        # push the pointer into the C++ map
        ROOT.tm_weight_map[key] = hist
weightsFile.Close()

#Load lifetime weights
if "Higgs" in test_signal:
    lifetimeWeightsFile = ROOT.TFile.Open("TMLifetimeWeights_Higgs.root")
    print("Loading Higgs lifetime weights...")
else:
    lifetimeWeightsFile = ROOT.TFile.Open("TMLifetimeWeights_SUSY.root")
    print("Loading SUSY lifetime weights...")

for era in eras:
    eraDir = lifetimeWeightsFile.Get(era)
    for signal in signals:
        hist = eraDir.Get(signal)
        hist.SetDirectory(0)  # detach from file so it survives after closing
        key = f"lifetime_{era}_{signal}"
        # push the pointer into the C++ map
        ROOT.tm_weight_map[key] = hist
lifetimeWeightsFile.Close()


base_sel = "jets_dR > 0.4 && hltHTProxy > 400 && LLP_PtSum > 0"

from plottingFunctions import *
import time
t0 = time.time()
# MC dataframe
dfsMC = {}
for bg in backgroundDict.keys():
    MCchain = ROOT.TChain("vertexEffTree/objectTree")
    MCchain.Add(backgroundDict[bg])
    dfMC = ROOT.RDataFrame(MCchain)
    dfMC = dfMC.Filter(base_sel)
    dfMC = dfMC.Filter("nMovedTracks > 3") #Guard against events with not enough tracks to move

    dfMC = dfMC.Define("Jet1_eta", "jets_eta[0]")
    dfMC = dfMC.Define("Jet2_eta", "jets_eta[1]")

    dfMC = dfMC.Define("moveVertex_R", "sqrt(moveVertex_x*moveVertex_x + moveVertex_y*moveVertex_y)")

    #vertex_sel = "(matchedVertex_cosT > 0) && (matchedVertex_chi2 < 2.5) && (matchedVertex_dBV > 0.01) && (matchedVertex_dBV < 2.0) && (matchedVertex_dBVerr < 0.005) && (matchedVertex_nTracks > 2)"
    vertex_sel = "(matchedVertex_dBV > 0.01) && (matchedVertex_dBV < 2.0) && (matchedVertex_dBVerr < 0.005) && (matchedVertex_nTracks > 2)"

    dfMC = dfMC.Define("vertex_pass", vertex_sel)
    #dfMC = dfMC.Define("totalTracks", "nCloseTracks + nSurvivedTracks")

    if "Higgs" in test_signal:
        upperNetP = 500   #Values to crop the weight maps. This fixes the overflow bins.
    else:
        upperNetP = 750
    upperDR   = 6

    dfMC = dfMC.Define("netP_clamped", f"LLP_netP > {upperNetP - 1e-6} ? {upperNetP - 1e-6} : LLP_netP") #1e-6 value to make sure it falls within the last bin
    dfMC = dfMC.Define("dR_clamped",   f"LLP_dR > {upperDR - 1e-6} ? {upperDR - 1e-6} : LLP_dR")

    upperdPVV = 2.2
    upperdPVV3D = 5
    dfMC = dfMC.Define("dPVV_clamped", f"moveVertex_dPVV > {upperdPVV - 1e-6} ? {upperdPVV - 1e-6} : moveVertex_dPVV") #1e-6 value to make sure it falls within the last bin
    dfMC = dfMC.Define("dPVV3D_clamped",   f"moveVertex_dPVV3D > {upperdPVV3D - 1e-6} ? {upperdPVV3D - 1e-6} : moveVertex_dPVV3D")

    upperEff = 2.0
    dfMC = dfMC.Define("dBV_eff",  f"std::min(moveVertex_dBV,  {upperEff - 1e-6})")
    dfMC = dfMC.Define("dPVV_eff", f"std::min(moveVertex_dPVV, {upperEff - 1e-6})")

    dfsMC[bg] = dfMC

loadHistogramsMC(dfsMC, backgroundDict, eras=['MC'], signals=[test_signal, "original"], debugPlots=doTrackPlots, doLifetimeReweighting=doLifetimeReweighting)

t1 = time.time()
print(f"It took {t1 - t0} seconds to run the MC histograms")

# 2024 data draframe
DATAchain = ROOT.TChain("vertexEffTree/objectTree")
for data in dataDict.keys():
    DATAchain.Add(dataDict[data])
dfDATA = ROOT.RDataFrame(DATAchain)
dfDATA = dfDATA.Filter(base_sel)
dfDATA = dfDATA.Filter("nMovedTracks > 3") #Guard against events with not enough tracks to move

dfDATA = dfDATA.Define("Jet1_eta", "jets_eta[0]")
dfDATA = dfDATA.Define("Jet2_eta", "jets_eta[1]")

dfDATA = dfDATA.Define("moveVertex_R", "sqrt(moveVertex_x*moveVertex_x + moveVertex_y*moveVertex_y)")
dfDATA = dfDATA.Define("vertex_pass", vertex_sel)

dfDATA = dfDATA.Define("netP_clamped", f"LLP_netP > {upperNetP - 1e-6} ? {upperNetP - 1e-6} : LLP_netP") #1e-6 value to make sure it falls within the last bin
dfDATA = dfDATA.Define("dR_clamped",   f"LLP_dR > {upperDR - 1e-6} ? {upperDR - 1e-6} : LLP_dR")
#dfDATA = dfDATA.Define("totalTracks", "nCloseTracks + nSurvivedTracks")

dfDATA = dfDATA.Define("dPVV_clamped", f"moveVertex_dPVV > {upperdPVV - 1e-6} ? {upperdPVV - 1e-6} : moveVertex_dPVV") #1e-6 value to make sure it falls within the last bin
dfDATA = dfDATA.Define("dPVV3D_clamped",   f"moveVertex_dPVV3D > {upperdPVV3D - 1e-6} ? {upperdPVV3D - 1e-6} : moveVertex_dPVV3D")

dfDATA = dfDATA.Define("dBV_eff",  f"std::min(moveVertex_dBV,  {upperEff - 1e-6})")
dfDATA = dfDATA.Define("dPVV_eff", f"std::min(moveVertex_dPVV, {upperEff - 1e-6})")

loadHistograms(dfDATA, eras=['2024'], signals=[test_signal, "original"], debugPlots=doTrackPlots, doLifetimeReweighting=doLifetimeReweighting)

t2 = time.time()
print(f"It took {t2 - t1} seconds to run the DATA histograms")

dfsSignal = {}
# signal histos
signals_test = [test_signal]
for signal in signals_test:
    SignalChain = ROOT.TChain("scoutingTree/tmTree")
    SignalChain.Add(signalDict[signal])
    dfSignal = ROOT.RDataFrame(SignalChain)

    dfSignal = dfSignal.Filter("genVert_dVV_TM > 0.036")
    dfSignal = dfSignal.Filter("abs(genVert_dPhiVV_TM) > 0.5")
    dfSignal = dfSignal.Filter("All(genVert_deltaR_TM > 0.4)")
    dfSignal = dfSignal.Filter("hltHTProxy > 400")

    dfsSignal[signal] = dfSignal

loadSignalHistograms(dfsSignal)

t3 = time.time()
print(f"It took {t3 - t2} seconds to run the signal histograms")

if doLifetimeReweighting:
    appendString = "_ctauReweighted"
else:
    appendString = ""

logscale = False
#Validation plots before reweighting
compare_plot(moveVertex_sumPt[f'2024'], moveVertex_sumPt[f'MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="pT sum [GeV]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/sumpT_noReweighting')
compare_plot(moveVertex_netPt[f'2024'], moveVertex_netPt[f'MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="Net pT [GeV]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/netpT_noReweighting')
compare_plot(moveVertex_netP[f'2024'], moveVertex_netP[f'MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="Net 3D momentum [GeV]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/netP_noReweighting')
compare_plot(moveVertex_deltaR[f'2024'], moveVertex_deltaR[f'MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="Vertex Tracks Delta R", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/deltaR_noReweighting')

logscale = True
compare_plot(moveVertexDBV[f'2024'], moveVertexDBV[f'MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dBV [cm]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/dBV_noReweighting')
compare_plot(moveVertexDBV3D[f'2024'], moveVertexDBV3D[f'MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dBV 3D [cm]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/dBV3D_noReweighting')
compare_plot(moveVertexDPVV['2024'], moveVertexDPVV['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/dPVV_noReweighting')
compare_plot(moveVertexDPVV3D['2024'], moveVertexDPVV3D['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV 3D [cm]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/dPVV3D_noReweighting')

logscale = False
compare_plot(nPV['2024'], nPV['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nPV", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nPV_noReweighting')

compare_plot(nMovedTracks['2024'], nMovedTracks['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nMovedTracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nMovedTracks_noReweighting')

compare_plot(nSurvivedTracks['2024'], nSurvivedTracks['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nSurvivedTracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nSurvivedTracks_noReweighting')
compare_plot(nCloseBGTracks['2024'], nCloseBGTracks['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nCloseBGTracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nCloseBGTracks_noReweighting')
compare_plot(nCloseTotalTracks['2024'], nCloseTotalTracks['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="Total Close Tracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nTotalCloseTracks_noReweighting')

compare_plot(nSurvivedSeedTracks['2024'], nSurvivedSeedTracks['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nSurvivedSeedTracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nSurvivedSeedTracks_noReweighting')
compare_plot(nCloseBGSeedTracks['2024'], nCloseBGSeedTracks['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nCloseBGSeedTracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nCloseBGSeedTracks_noReweighting')
compare_plot(nCloseTotalSeedTracks['2024'], nCloseTotalSeedTracks['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="Total Close Seed Tracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nTotalCloseSeedTracks_noReweighting')

compare_plot(nSurvivedTracksVsdPVV['2024'], nSurvivedTracksVsdPVV['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Survived Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nSurvivedTracksVsdPVV_noReweighting', is_profile=True)
compare_plot(nCloseBGTracksVsdPVV['2024'], nCloseBGTracksVsdPVV['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Close BG Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nCloseBGTracksVsdPVV_noReweighting', is_profile=True)
compare_plot(nCloseTotalTracksVsdPVV['2024'], nCloseTotalTracksVsdPVV['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Total Close Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nCloseTotalTracksVsdPVV_noReweighting', is_profile=True)

compare_plot(nSurvivedSeedTracksVsdPVV['2024'], nSurvivedSeedTracksVsdPVV['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Survived Seed Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nSurvivedSeedTracksVsdPVV_noReweighting', is_profile=True)
compare_plot(nCloseBGSeedTracksVsdPVV['2024'], nCloseBGSeedTracksVsdPVV['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Close BG Seed Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nCloseBGSeedTracksVsdPVV_noReweighting', is_profile=True)
compare_plot(nCloseTotalSeedTracksVsdPVV['2024'], nCloseTotalSeedTracksVsdPVV['MC'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Total Close Seed Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nCloseTotalSeedTracksVsdPVV_noReweighting', is_profile=True)

#Non-reweighted efficiency plots
logscale=False
for ntk in [3, 4, 5, 6, 7, 8, 9]:
    if(ntk == 9):
        ntk_string = ">= 9"
    else:
        ntk_string = str(ntk)
        
    compare_plot(vertexEffJet1Eta[f'2024_{str(ntk)}tks'], vertexEffJet1Eta[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="First jet eta", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffJet1Eta_{str(ntk)}Tracks", is_teff=True)
    compare_plot(vertexEffJet2Eta[f'2024_{str(ntk)}tks'], vertexEffJet2Eta[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="Second jet eta", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffJet2Eta_{str(ntk)}Tracks", is_teff=True)

    compare_plot(vertexEffSumPt[f'2024_{str(ntk)}tks'], vertexEffSumPt[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="pT sum [GeV]", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffSumPt_{str(ntk)}Tracks", is_teff=True)
    compare_plot(vertexEffNetPt[f'2024_{str(ntk)}tks'], vertexEffNetPt[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="Net pT [GeV]", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffNetPt_{str(ntk)}Tracks", is_teff=True)
    compare_plot(vertexEffNetP[f'2024_{str(ntk)}tks'], vertexEffNetP[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="Net 3D momentum [GeV]", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffNetP_{str(ntk)}Tracks", is_teff=True)
    compare_plot(vertexEffDeltaR[f'2024_{str(ntk)}tks'], vertexEffDeltaR[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="Vertex tracks delta R", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffDeltaR_{str(ntk)}Tracks", is_teff=True)
    
    logscale = True
    compare_plot(vertexEffdPVV[f'2024_{str(ntk)}tks'], vertexEffdPVV[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="dPVV [cm]", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffdPVV_{str(ntk)}Tracks", is_teff=True)
    compare_plot(vertexEffdPVV3D[f'2024_{str(ntk)}tks'], vertexEffdPVV3D[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="dPVV 3D [cm]", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffdPVV3D_{str(ntk)}Tracks", is_teff=True)
    compare_plot(vertexEffdBV[f'2024_{str(ntk)}tks'], vertexEffdBV[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="dBV [cm]", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffdBV_{str(ntk)}Tracks", is_teff=True)
    
    logscale = False
    compare_plot(vertexEffSurvTracks[f'2024_{str(ntk)}tks'], vertexEffSurvTracks[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="Survived Tracks", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffSurvTracks_{str(ntk)}Tracks", is_teff=True)
    compare_plot(vertexEffCloseBGTracks[f'2024_{str(ntk)}tks'], vertexEffCloseBGTracks[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="Close BG Tracks", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffCloseBGTracks_{str(ntk)}Tracks", is_teff=True)
    compare_plot(vertexEffTotalCloseTracks[f'2024_{str(ntk)}tks'], vertexEffTotalCloseTracks[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="Total Close Tracks", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffTotalCloseTracks_{str(ntk)}Tracks", is_teff=True)
    
    compare_plot(vertexEffSurvSeedTracks[f'2024_{str(ntk)}tks'], vertexEffSurvSeedTracks[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="Survived Seed Tracks", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffSurvSeedTracks_{str(ntk)}Tracks", is_teff=True)
    compare_plot(vertexEffCloseBGSeedTracks[f'2024_{str(ntk)}tks'], vertexEffCloseBGSeedTracks[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="Close BG Seed Tracks", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffCloseBGSeedTracks_{str(ntk)}Tracks", is_teff=True)
    compare_plot(vertexEffTotalCloseSeedTracks[f'2024_{str(ntk)}tks'], vertexEffTotalCloseSeedTracks[f'MC_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="Total Close Seed Tracks", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffTotalCloseSeedTracks_{str(ntk)}Tracks", is_teff=True)
        


#Validation plots reweighted to signals
signals = [test_signal]

for signal in signals:
    logscale = False
    compare_3plot(signal_sumPt[signal], moveVertex_sumPt[f'2024_{signal}'], moveVertex_sumPt[f'MC_{signal}'], legend1=f"Signal {signal}", legend2="2024 Data", legend3="Background MC", plot_title="", x_axis="pT sum [GeV]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/sumpT_{signal}{appendString}')
    compare_3plot(signal_netPt[signal], moveVertex_netPt[f'2024_{signal}'], moveVertex_netPt[f'MC_{signal}'], legend1=f"Signal {signal}", legend2="2024 Data", legend3="Background MC", plot_title="", x_axis="Net pT [GeV]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/netpT_{signal}{appendString}')
    compare_3plot(signal_netP[signal], moveVertex_netP[f'2024_{signal}'], moveVertex_netP[f'MC_{signal}'], legend1=f"Signal {signal}", legend2="2024 Data", legend3="Background MC", plot_title="", x_axis="Net 3D momentum [GeV]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/netP_{signal}{appendString}')
    compare_3plot(signal_deltaR[signal], moveVertex_deltaR[f'2024_{signal}'], moveVertex_deltaR[f'MC_{signal}'], legend1=f"Signal {signal}", legend2="2024 Data", legend3="Background MC", plot_title="", x_axis="Vertex Tracks Delta R", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/deltaR_{signal}{appendString}')
    
    logscale = True
    compare_3plot(signal_DBV[signal], moveVertexDPVV[f'2024_{signal}'], moveVertexDPVV[f'MC_{signal}'], legend1=f"Signal {signal}", legend2="2024 Data", legend3="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/dBV_{signal}{appendString}')
    compare_3plot(signal_DBV3D[signal], moveVertexDPVV3D[f'2024_{signal}'], moveVertexDPVV3D[f'MC_{signal}'], legend1=f"Signal {signal}", legend2="2024 Data", legend3="Background MC", plot_title="", x_axis="dPVV 3D [cm]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/dBV3D_{signal}{appendString}')

    #Also the number of tracks and PVs
    logscale = False
    compare_plot(nMovedTracks[f'2024_{signal}'], nMovedTracks[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nMovedTracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nMovedTracks_{signal}{appendString}')
    
    compare_plot(nSurvivedTracks[f'2024_{signal}'], nSurvivedTracks[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nSurvivedTracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nSurvivedTracks_{signal}{appendString}')
    compare_plot(nCloseBGTracks[f'2024_{signal}'], nCloseBGTracks[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nCloseBGTracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nCloseBGTracks_{signal}{appendString}')
    compare_plot(nCloseTotalTracks[f'2024_{signal}'], nCloseTotalTracks[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="Total Close Tracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nTotalCloseTracks_{signal}{appendString}')
    
    compare_plot(nSurvivedSeedTracks[f'2024_{signal}'], nSurvivedSeedTracks[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nSurvivedSeedTracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nSurvivedSeedTracks_{signal}{appendString}')
    compare_plot(nCloseBGSeedTracks[f'2024_{signal}'], nCloseBGSeedTracks[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nCloseBGSeedTracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nCloseBGSeedTracks_{signal}{appendString}')
    compare_plot(nCloseTotalSeedTracks[f'2024_{signal}'], nCloseTotalSeedTracks[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="Total Close Seed Tracks", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nTotalCloseSeedTracks_{signal}{appendString}')

    compare_plot(nSurvivedTracksVsdPVV[f'2024_{signal}'], nSurvivedTracksVsdPVV[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Survived Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nSurvivedTracksVsdPVV_{signal}{appendString}', is_profile=True)
    compare_plot(nCloseBGTracksVsdPVV[f'2024_{signal}'], nCloseBGTracksVsdPVV[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Close BG Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nCloseBGTracksVsdPVV_{signal}{appendString}', is_profile=True)
    compare_plot(nCloseTotalTracksVsdPVV[f'2024_{signal}'], nCloseTotalTracksVsdPVV[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Total Close Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nCloseTotalTracksVsdPVV_{signal}{appendString}', is_profile=True)
    
    compare_plot(nSurvivedSeedTracksVsdPVV[f'2024_{signal}'], nSurvivedSeedTracksVsdPVV[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Survived Seed Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nSurvivedSeedTracksVsdPVV_{signal}{appendString}', is_profile=True)
    compare_plot(nCloseBGSeedTracksVsdPVV[f'2024_{signal}'], nCloseBGSeedTracksVsdPVV[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Close BG Seed Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nCloseBGSeedTracksVsdPVV_{signal}{appendString}', is_profile=True)
    compare_plot(nCloseTotalSeedTracksVsdPVV[f'2024_{signal}'], nCloseTotalSeedTracksVsdPVV[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="Total Close Seed Tracks", logy=logscale, plotFileName=f'{plotsFolder}/nCloseTotalSeedTracksVsdPVV_{signal}{appendString}', is_profile=True)

    compare_plot(nPV[f'2024_{signal}'], nPV[f'MC_{signal}'], legend1="2024 Data", legend2="Background MC", plot_title="", x_axis="nPV", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/nPV_{signal}{appendString}')

    logscale = True
    compare_3plot(signal_DBV[signal], moveVertexDPVV[f'2024_{signal}'], moveVertexDPVV[f'MC_{signal}'], legend1=f"Signal {signal}", legend2="2024 Data", legend3="Background MC", plot_title="", x_axis="dPVV [cm]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/dPVV_{signal}{appendString}')
    compare_3plot(signal_DBV3D[signal], moveVertexDPVV3D[f'2024_{signal}'], moveVertexDPVV3D[f'MC_{signal}'], legend1=f"Signal {signal}", legend2="2024 Data", legend3="Background MC", plot_title="", x_axis="dPVV 3D [cm]", y_axis="A.U.", logy=logscale, plotFileName=f'{plotsFolder}/dPVV3D_{signal}{appendString}')

#Efficiency plots
signals = [test_signal]
for signal in signals:
    for ntk in [3, 4, 5, 6, 7, 8, 9]:
        if(ntk == 9):
            ntk_string = ">= 9"
        else:
            ntk_string = str(ntk)
        logscale=False
        compare_plot(vertexEffJet1Eta[f'2024_{signal}_{str(ntk)}tks'], vertexEffJet1Eta[f'MC_{signal}_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="First jet eta", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffJet1Eta_{str(ntk)}Tracks_{signal}{appendString}", is_teff=True)
        compare_plot(vertexEffJet2Eta[f'2024_{signal}_{str(ntk)}tks'], vertexEffJet2Eta[f'MC_{signal}_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="Second jet eta", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffJet2Eta_{str(ntk)}Tracks_{signal}{appendString}", is_teff=True)
        logscale=True
        compare_plot(vertexEffdBV[f'2024_{signal}_{str(ntk)}tks'], vertexEffdBV[f'MC_{signal}_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="dBV [cm]", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffdBV_{str(ntk)}Tracks_{signal}{appendString}", is_teff=True)
        compare_plot(vertexEffdPVV[f'2024_{signal}_{str(ntk)}tks'], vertexEffdPVV[f'MC_{signal}_{str(ntk)}tks'], legend1="Data", legend2="MC", plot_title=f"Vertex Efficiency for {ntk_string} tracks", x_axis="dPVV [cm]", y_axis="Efficiency", logy=logscale, plotFileName=f"{plotsFolder}/vertexEffdPVV_{str(ntk)}Tracks_{signal}{appendString}", is_teff=True)

logscale = True
#Track distributions
if(doTrackPlots):
    for signal in originalTrack_pt.keys():
        compare_plot(originalTrack_pt[signal], newTrack_pt[signal], legend1="Original Tracks", legend2="New Tracks", plot_title=f"Tracks pT for {signal}", x_axis="pT [GeV]", y_axis="A.U.", logy=logscale, plotFileName=f"{plotsFolder}/tracks_pt_{signal}", vline=[])
        compare_plot(originalTrack_eta[signal], newTrack_eta[signal], legend1="Original Tracks", legend2="New Tracks", plot_title=f"Tracks eta for {signal}", x_axis="eta", y_axis="A.U.", logy=logscale, plotFileName=f"{plotsFolder}/tracks_eta_{signal}", vline=[])
        compare_plot(originalTrack_phi[signal], newTrack_phi[signal], legend1="Original Tracks", legend2="New Tracks", plot_title=f"Tracks phi for {signal}", x_axis="phi", y_axis="A.U.", logy=logscale, plotFileName=f"{plotsFolder}/tracks_phi_{signal}", vline=[])
        compare_plot(originalTrack_dxy[signal], newTrack_dxy[signal], legend1="Original Tracks", legend2="New Tracks", plot_title=f"Tracks dxy for {signal}", x_axis="dxy [cm]", y_axis="A.U.", logy=logscale, plotFileName=f"{plotsFolder}/tracks_dxy_{signal}", vline=[])

        compare_plot(unmovedTrack_pt[signal], movedTrack_pt[signal], legend1="Unmoved Tracks", legend2="Moved Tracks", plot_title=f"Tracks pT for {signal}", x_axis="pT [GeV]", y_axis="A.U.", logy=logscale, plotFileName=f"{plotsFolder}/movedTracks_pt_{signal}", vline=[])
        compare_plot(unmovedTrack_eta[signal], movedTrack_eta[signal], legend1="Unmoved Tracks", legend2="Moved Tracks", plot_title=f"Tracks eta for {signal}", x_axis="eta", y_axis="A.U.", logy=logscale, plotFileName=f"{plotsFolder}/movedTracks_eta_{signal}", vline=[])
        compare_plot(unmovedTrack_phi[signal], movedTrack_phi[signal], legend1="Unmoved Tracks", legend2="Moved Tracks", plot_title=f"Tracks phi for {signal}", x_axis="phi", y_axis="A.U.", logy=logscale, plotFileName=f"{plotsFolder}/movedTracks_phi_{signal}", vline=[])
        compare_plot(unmovedTrack_dxy[signal], movedTrack_dxy[signal], legend1="Unmoved Tracks", legend2="Moved Tracks", plot_title=f"Tracks dxy for {signal}", x_axis="dxy [cm]", y_axis="A.U.", logy=logscale, plotFileName=f"{plotsFolder}/movedTracks_dxy_{signal}", vline=[])