import ROOT
from IPython.display import Image, display
import numpy as np

ROOT.EnableImplicitMT()

SPred    = ROOT.TColor.GetColor(177,  4, 14)
SPdred   = ROOT.TColor.GetColor(140, 21, 21)
SPgreen  = ROOT.TColor.GetColor(  0,155,118)
SPdgreen = ROOT.TColor.GetColor( 23, 94, 84)
SPblue   = ROOT.TColor.GetColor(  0,152,219)
SPdblue  = ROOT.TColor.GetColor(  0,124,146)
SPyellow = ROOT.TColor.GetColor(234,171,  0)
SPdyellow= ROOT.TColor.GetColor(178,111, 22)
SPbeige  = ROOT.TColor.GetColor(210,194,149)
SPdbeige = ROOT.TColor.GetColor(179,153, 93)
SPbrown  = ROOT.TColor.GetColor(141, 60, 30)
SPdbrown = ROOT.TColor.GetColor( 94, 48, 50)
SPgrey   = ROOT.TColor.GetColor(182,177,179)
SPdgrey  = ROOT.TColor.GetColor( 77, 79, 83)
SPpurple = ROOT.TColor.GetColor( 83, 40, 79)

ht_proxy = "hltNeutralPlusChargedPFCands"
gen_var = "genHT"
signals = ['Higgs_15', 'Higgs_55', 'Stop_200', 'Stop_800']
JECvar = "" #leave empty for nominal
appendString = ""
treeName = "triggerEffs"
if(JECvar == "up" or JECvar == "down"):
    appendString = f"_JEC{JECvar}"
    treeName = f"{treeName}JEC{JECvar}"

c = ROOT.TCanvas("c", "c", 800, 900)
pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
pad2 = ROOT.TPad("pad2", "pad2", 0, 0.0, 1, 0.3)
pad1.SetBottomMargin(0.02)
pad2.SetTopMargin(0.02)
pad2.SetBottomMargin(0.35)
pad1.Draw()
pad2.Draw()


signalDict = {
    "Higgs_15_0p1": "Signal/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/ScoutingMC_2024_Higgs_15_0p1_TriggerEffs_v7/Signal.root",
    "Higgs_15_10": "Signal/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/ScoutingMC_2024_Higgs_15_10_TriggerEffs_v7/Signal.root",
    "Higgs_55_0p1": "Signal/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/ScoutingMC_2024_Higgs_55_0p1_TriggerEffs_v7/Signal.root",
    "Higgs_55_10": "Signal/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/ScoutingMC_2024_Higgs_55_10_TriggerEffs_v7/Signal.root",
    "Stop_200_0p1": "Signal/StopStopbarTo2Dbar2D_M-200_ctau-0p1mm_100kEvts_v2/ScoutingMC_2024_StopToD_200_0p1_TriggerEffs_v7/Signal.root",
    "Stop_200_10": "Signal/StopStopbarTo2Dbar2D_M-200_CTau-10mm_Summer24_100k_v2/ScoutingMC_2024_StopToD_200_10_TriggerEffs_v7/Signal.root",
    "Stop_800_0p1": "Signal/StopStopbarTo2Dbar2D_M-800_ctau-0p1mm_100kEvts_v2/ScoutingMC_2024_StopToD_800_0p1_TriggerEffs_v7/Signal.root",
    "Stop_800_10": "Signal/StopStopbarTo2Dbar2D_M-800_CTau-10mm_Summer24_100k_v2/ScoutingMC_2024_StopToD_800_10_TriggerEffs_v7/Signal.root"
}

ROOT.gStyle.SetOptStat(0)
pad1.Clear()
pad2.Clear()

colors = [SPblue, SPred, SPdgreen, SPpurple]

for signal in signals:
    print(f"Signal: {signal}")
    dfsSignal = {}
    chains = []   # keep TChains alive
    histos = {}   # keep histogram results alive
    genHistos = {}
    # Default legend position (top right)
    leg_coords = (0.55, 0.62, 0.9, 0.9)

    # Stop_800: the histogram peaks in the top right, so move the legend to the top left of the pad
    if signal == "Stop_800":
        leg_coords = (0.15, 0.62, 0.5, 0.9)


    leg = ROOT.TLegend(*leg_coords)
    signals_to_process = [f'{signal}_0p1', f'{signal}_10']
    for s in signals_to_process:
        signal_chain = ROOT.TChain(f'{treeName}/objectTree')
        signal_chain.Add(signalDict[s])
        chains.append(signal_chain)

        dfsSignal[s] = ROOT.RDataFrame(signal_chain)
        dfsSignal[s] = dfsSignal[s].Define("hltNeutralPlusChargedPFCands", "hltPFCands_NeutralEnergy_JetMatch + (0.8 - 0.6*exp(-hltHT/300.0)) * hltPFCands_ChargedEnergy_JetMatch")

        histoHT = dfsSignal[s].Histo1D((f"{ht_proxy}_{s}", ht_proxy, 50, 0, 2100), ht_proxy, "theWeight")
        if(ht_proxy == "hltHT"):
            histoHT.SetTitle(f"; HLT $H_T$ [GeV]; Weight Sum")
        else:
            histoHT.SetTitle(f"; $H_T$ proxy [GeV]; Weight Sum")
        histos[s] = histoHT

        histoGen = dfsSignal[s].Histo1D((f"{gen_var}_{s}", gen_var, 50, 0, 2100), gen_var, "theWeight")
        genHistos[s] = histoGen

    # --- Find global max (this triggers the event loop via GetMaximum()) ---
    global_max = max(h.GetMaximum() for h in histos.values())
    global_max = max(global_max, max(h.GetMaximum() for h in genHistos.values()))

    # --- Reference histograms for the ratio (first entry in the dict) ---
    ref_key = signals_to_process[0]
    ref_histo = histos[ref_key].GetValue().Clone(f"{ref_key}_ref")
    ref_histo.SetDirectory(0)
    ref_gen = genHistos[ref_key].GetValue().Clone(f"{ref_key}_gen_ref")
    ref_gen.SetDirectory(0)

    # --- Second pass: style + draw with shared y-axis max (top pad) ---
    pad1.cd()
    t = 0
    for sig, histoHT in histos.items():
        histoHT.SetLineColor(colors[t])
        histoHT.SetMaximum(global_max * 1.1)  # 10% headroom above the tallest histo
        histoHT.GetXaxis().SetLabelSize(0)    # hide x labels on upper pad
        histoHT.GetXaxis().SetTitleSize(0)    # hide x title on upper pad

        if t == 0:
            histoHT.Draw("HIST")
        else:
            histoHT.Draw("HIST SAME")

        leg.AddEntry(histoHT.GetPtr(), f"{sig} (proxy)", 'l')
        t += 1

    # --- genHT overlay: same colors, dashed ---
    t = 0
    for sig, histoGen in genHistos.items():
        histoGen.SetLineColor(colors[t])
        histoGen.SetLineStyle(2)
        histoGen.Draw("HIST SAME")
        leg.AddEntry(histoGen.GetPtr(), f"{sig} (gen)", 'l')
        t += 1

    leg.Draw("SAME")

    # --- Lower pad: ratio to the reference signal ---
    pad2.cd()

    disp_key = signals_to_process[1]  # displaced

    h_ratio = histos[disp_key].GetValue().Clone(f"ratio_{disp_key}")
    h_ratio.SetDirectory(0)
    h_ratio.Sumw2()
    h_ratio.Divide(ref_histo)

    h_ratio.SetLineColor(ROOT.kBlack)
    h_ratio.SetMarkerColor(ROOT.kBlack)
    h_ratio.SetMarkerStyle(20)
    h_ratio.SetTitle("")

    if(ht_proxy == "hltHT"):
        h_ratio.GetXaxis().SetTitle("HLT H_{T} [GeV]")
    else:
        h_ratio.GetXaxis().SetTitle("H_{T} proxy [GeV]")
        
    h_ratio.GetYaxis().SetTitle("Disp / Prompt")
    h_ratio.GetYaxis().SetNdivisions(505)
    h_ratio.GetXaxis().SetTitleSize(0.12)
    h_ratio.GetXaxis().SetLabelSize(0.10)
    h_ratio.GetYaxis().SetTitleSize(0.10)
    h_ratio.GetYaxis().SetLabelSize(0.08)
    h_ratio.GetYaxis().SetTitleOffset(0.5)
    h_ratio.GetYaxis().SetRangeUser(0.0, 2.0)

    h_ratio.Draw("PE")

    # genHT ratio: open gray markers on top of the proxy ratio
    h_ratio_gen = genHistos[disp_key].GetValue().Clone(f"ratio_gen_{disp_key}")
    h_ratio_gen.SetDirectory(0)
    h_ratio_gen.Sumw2()
    h_ratio_gen.Divide(ref_gen)
    h_ratio_gen.SetLineColor(ROOT.kGray + 2)
    h_ratio_gen.SetMarkerColor(ROOT.kGray + 2)
    h_ratio_gen.SetMarkerStyle(24)
    h_ratio_gen.Draw("PE SAME")

    # Reference line at 1
    line = ROOT.TLine(0, 1, 2100, 1)
    line.SetLineStyle(2)
    line.SetLineColor(ROOT.kGray + 1)
    line.Draw("SAME")

    pad1.cd()
    c.SetLogy(0)
    c.Draw()
    print(f"Saving plot: {signal}_{ht_proxy}.pdf")
    c.SaveAs(f'plotsHT/{signal}_{ht_proxy}{appendString}.pdf')

###### 2D plots
print("Making the 2D validation plots...")
import os

def FileList(folder_path):
    try:
        return [folder_path + f for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f))]
    except FileNotFoundError:
        print(f"Error: The folder '{folder_path}' was not found.")
        return []
    except NotADirectoryError:
        print(f"Error: The path '{folder_path}' is not a directory.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []



dataDict = {
    "2024C": FileList("TriggerEffs_Data/ScoutingMonitor_2024C_TriggerEffs_v6/"),
    "2024D": FileList("TriggerEffs_Data/ScoutingMonitor_2024D_TriggerEffs_v6/"),
    "2024E": FileList("TriggerEffs_Data/ScoutingMonitor_2024E_TriggerEffs_v6/"),
    "2024F": FileList("TriggerEffs_Data/ScoutingMonitor_2024F_TriggerEffs_v6/"),
    "2024G": FileList("TriggerEffs_Data/ScoutingMonitor_2024G_TriggerEffs_v6/"),
    "2024H": FileList("TriggerEffs_Data/ScoutingMonitor_2024H_TriggerEffs_v6/"),
    "2024I": FileList("TriggerEffs_Data/ScoutingMonitor_2024I_TriggerEffs_v6/"),
}
processDict = {
    "TTTo4Q":        FileList("TriggerEffs_BG/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8/ScoutingMC_2024_TTBar_FullyHadronic_TriggerEffs_v6/"),
    "TTToLNu2Q":     FileList("TriggerEffs_BG/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/ScoutingMC_2024_TTBar_SemiLeptonic_TriggerEffs_v6/"),
    "QCD100to200":   FileList("TriggerEffs_BG/QCD-4Jets_Bin-HT-100to200_TuneCP5_13p6TeV_madgraphMLM-pythia8/ScoutingMC_2024_QCD_100to200_TriggerEffs_v6/"),
    "QCD200to400":   FileList("TriggerEffs_BG/QCD-4Jets_Bin-HT-200to400_TuneCP5_13p6TeV_madgraphMLM-pythia8/ScoutingMC_2024_QCD_200to400_TriggerEffs_v6/"),
    "QCD400to600":   FileList("TriggerEffs_BG/QCD-4Jets_Bin-HT-400to600_TuneCP5_13p6TeV_madgraphMLM-pythia8/ScoutingMC_2024_QCD_400to600_TriggerEffs_v6/"),
    "QCD600to800":   FileList("TriggerEffs_BG/QCD-4Jets_Bin-HT-600to800_TuneCP5_13p6TeV_madgraphMLM-pythia8/ScoutingMC_2024_QCD_600to800_TriggerEffs_v6/"),
    "QCD800to1000":  FileList("TriggerEffs_BG/QCD-4Jets_Bin-HT-800to1000_TuneCP5_13p6TeV_madgraphMLM-pythia8/ScoutingMC_2024_QCD_800to1000_TriggerEffs_v6/"),
    "QCD1000to1200": FileList("TriggerEffs_BG/QCD-4Jets_Bin-HT-1000to1200_TuneCP5_13p6TeV_madgraphMLM-pythia8/ScoutingMC_2024_QCD_1000to1200_TriggerEffs_v6/"),
    "QCD1200to1500": FileList("TriggerEffs_BG/QCD-4Jets_Bin-HT-1200to1500_TuneCP5_13p6TeV_madgraphMLM-pythia8/ScoutingMC_2024_QCD_1200to1500_TriggerEffs_v6/"),
    "QCD1500to2000": FileList("TriggerEffs_BG/QCD-4Jets_Bin-HT-1500to2000_TuneCP5_13p6TeV_madgraphMLM-pythia8/ScoutingMC_2024_QCD_1500to2000_TriggerEffs_v6/"),
    "QCD2000":       FileList("TriggerEffs_BG/QCD-4Jets_Bin-HT-2000_TuneCP5_13p6TeV_madgraphMLM-pythia8/ScoutingMC_2024_QCD_2000_TriggerEffs_v6/"),
}

proxyGenHT = {}
proxyL1HT = {}
proxyHLTHT = {}
l1HLTHT = {}

## Data histo:
print("Processing the 2024 data...")
dataChain = ROOT.TChain("triggerEffs/objectTree")
for data in dataDict.keys():
    for file in dataDict[data]:
        dataChain.Add(file)

dfData = ROOT.RDataFrame(dataChain)
dfData = dfData.Define("proxyHT", "hltPFCands_NeutralEnergy_JetMatch + (0.8 - 0.6*exp(-hltHT/300.0)) * hltPFCands_ChargedEnergy_JetMatch")

proxyL1HT_data = dfData.Histo2D(("proxyL1HT_data", "Proxy vs L1 HT (data); proxy HT [GeV]; L1 HT [GeV]", 50, 0, 2000, 50, 0, 2000), "proxyHT", "l1HT", "theWeight")
proxyHLTHT_data = dfData.Histo2D(("proxyHLTHT_data", "Proxy vs HLT HT (data); proxy HT [GeV]; HLT HT [GeV]", 50, 0, 2000, 50, 0, 2000), "proxyHT", "hltHT", "theWeight")
l1HLTHT_data = dfData.Histo2D(("l1HLTHT_data", "L1 vs HLT HT (data); L1 HT [GeV]; HLT HT [GeV]", 50, 0, 2000, 50, 0, 2000), "l1HT", "hltHT", "theWeight")

proxyL1HT['2024'] = proxyL1HT_data.GetValue()
proxyHLTHT['2024'] = proxyHLTHT_data.GetValue()
l1HLTHT['2024'] = l1HLTHT_data.GetValue()


#Background histo
print("Processing background MC")
proxyL1HT['MC'] = ROOT.TH2D("proxyL1HT_bg", "Proxy vs L1 HT (BG MC); proxy HT [GeV]; L1 HT [GeV]", 50, 0, 2000, 50, 0, 2000)
proxyHLTHT['MC'] = ROOT.TH2D("proxyHLTHT_bg", "Proxy vs HLT HT (BG MC); proxy HT [GeV]; HLT HT [GeV]", 50, 0, 2000, 50, 0, 2000)
l1HLTHT['MC'] = ROOT.TH2D("l1HLTHT_bg", "L1 vs HLT HT (BG MC); L1 HT [GeV]; HLT HT [GeV]", 50, 0, 2000, 50, 0, 2000)

proxyL1HT_bg = {}
proxyHLTHT_bg = {}
l1HLTHT_bg = {}
for bg in processDict.keys():
    print(f"Process: {bg}")
    mcChain = ROOT.TChain("triggerEffs/objectTree")
    for file in processDict[bg]:
        mcChain.Add(file)

    dfMC = ROOT.RDataFrame(mcChain)
    genWeightSum = dfMC.Sum("genWeight").GetValue()
    print(f"Gen weight sum: {genWeightSum}")

    dfMC = dfMC.Define("normWeight", f"theWeight/{genWeightSum}")
    dfMC = dfMC.Define("proxyHT", "hltPFCands_NeutralEnergy_JetMatch + (0.8 - 0.6*exp(-hltHT/300.0)) * hltPFCands_ChargedEnergy_JetMatch")

    proxyL1HT_bg[bg] = dfMC.Histo2D(("proxyL1HT_data", "Proxy vs L1 HT (bg); proxy HT [GeV]; L1 HT [GeV]", 50, 0, 2000, 50, 0, 2000), "proxyHT", "l1HT", "normWeight")
    proxyHLTHT_bg[bg] = dfMC.Histo2D(("proxyHLTHT_data", "Proxy vs HLT HT (bg); proxy HT [GeV]; HLT HT [GeV]", 50, 0, 2000, 50, 0, 2000), "proxyHT", "hltHT", "normWeight")
    l1HLTHT_bg[bg] = dfMC.Histo2D(("l1HLTHT_data", "L1 vs HLT HT (bg); L1 HT [GeV]; HLT HT [GeV]", 50, 0, 2000, 50, 0, 2000), "l1HT", "hltHT", "normWeight")

    proxyL1HT['MC'].Add(proxyL1HT_bg[bg].GetValue())
    proxyHLTHT['MC'].Add(proxyHLTHT_bg[bg].GetValue())
    l1HLTHT['MC'].Add(l1HLTHT_bg[bg].GetValue())

#Signal histos
print("Processing the signal")
for signal in signalDict.keys():
    print(f"Added signal {signal}")
    signalChain = ROOT.TChain("triggerEffs/objectTree")
    signalChain.Add(signalDict[signal])

    dfSignal = ROOT.RDataFrame(signalChain)

    dfSignal = dfSignal.Define("proxyHT", "hltPFCands_NeutralEnergy_JetMatch + (0.8 - 0.6*exp(-hltHT/300.0)) * hltPFCands_ChargedEnergy_JetMatch")

    proxyGenHT_signal = dfSignal.Histo2D((f"proxyGenHT_{signal}", f"Proxy vs Gen HT ({signal}); proxy HT [GeV]; Gen HT [GeV]", 50, 0, 2000, 50, 0, 2000), "proxyHT", "genHT", "theWeight") 
    proxyL1HT_signal = dfSignal.Histo2D((f"proxyL1HT_{signal}", f"Proxy vs L1 HT ({signal}); proxy HT [GeV]; L1 HT [GeV]", 50, 0, 2000, 50, 0, 2000), "proxyHT", "l1HT", "theWeight") 
    proxyHLTHT_signal = dfSignal.Histo2D((f"proxyHLTHT_{signal}", f"Proxy vs HLT HT ({signal}); proxy HT [GeV]; HLT HT [GeV]", 50, 0, 2000, 50, 0, 2000), "proxyHT", "hltHT", "theWeight") 
    l1HLTHT_signal = dfSignal.Histo2D((f"l1HLTHT_{signal}", f"L1 vs HLT HT ({signal}); L1 HT [GeV]; HLT HT [GeV]", 50, 0, 2000, 50, 0, 2000), "l1HT", "hltHT", "theWeight")

    proxyGenHT[signal] = proxyGenHT_signal.GetValue()
    proxyL1HT[signal] = proxyL1HT_signal.GetValue()
    proxyHLTHT[signal] = proxyHLTHT_signal.GetValue()
    l1HLTHT[signal] = l1HLTHT_signal.GetValue()


# Normalise the histos
for key in proxyL1HT.keys():
    toNormalize = [proxyL1HT, proxyHLTHT, l1HLTHT]
    for histo in toNormalize:
        if (histo[key].Integral() > 0):
            histo[key].Scale (1.0/histo[key].Integral())

for key in signalDict.keys():
    if (proxyGenHT[key].Integral() > 0):
        proxyGenHT[key].Scale(1.0/proxyGenHT[key].Integral())


# Plotting
def SetSPPalette(nContours=100):
    """Sequential palette from the SP colors: white -> blue -> dark green -> purple."""
    def rgb(col):
        c = ROOT.gROOT.GetColor(col)
        return c.GetRed(), c.GetGreen(), c.GetBlue()

    stops = [0.0, 0.35, 0.70, 1.0]
    cols = [(1.0, 1.0, 1.0), rgb(SPblue), rgb(SPdgreen), rgb(SPpurple)]

    stopsArr = np.array(stops, dtype=np.float64)
    red   = np.array([c[0] for c in cols], dtype=np.float64)
    green = np.array([c[1] for c in cols], dtype=np.float64)
    blue  = np.array([c[2] for c in cols], dtype=np.float64)

    ROOT.TColor.CreateGradientColorTable(len(stops), stopsArr, red, green, blue, nContours)
    ROOT.gStyle.SetNumberContours(nContours)

def Draw2D(histo, outName, zTitle="Normalised fraction of events", dynamicRange=1e5):
    zmax = histo.GetMaximum()
    zmin = histo.GetMinimum(0)               # smallest strictly positive bin content
    zmin = max(zmin, zmax / dynamicRange)    # cap the dynamic range to 5 decades

    histo.SetMinimum(zmin)
    histo.SetMaximum(zmax * 1.5)
    histo.GetZaxis().SetTitle(zTitle)
    histo.GetZaxis().SetTitleOffset(1.2)
    histo.Draw("COLZ")
    c2d.Update()
    c2d.SaveAs(outName)

SetSPPalette()

c2d = ROOT.TCanvas("c2d", "c2d", 800, 700)
c2d.SetRightMargin(0.16)   # room for the color bar
c2d.SetLeftMargin(0.12)
c2d.SetBottomMargin(0.12)
c2d.SetLogz(1)

for key in proxyL1HT.keys():
    toPlot = {
        "proxyVsL1HT": proxyL1HT,
        "proxyVsHLTHT": proxyHLTHT,
        "l1VsHLTHT": l1HLTHT
    }
    for plotName, plot in toPlot.items():
        Draw2D(plot[key], f"plotsHT/{plotName}_{key}.pdf")

for key in signalDict.keys():
    Draw2D(proxyGenHT[key], f"plotsHT/proxyVsGenHT_{key}.pdf")

# ---------------------------------------------------------------
# Correlation factor summary (plotted as 1 - rho on a log axis)
# ---------------------------------------------------------------
categories = {
    "Proxy vs L1 HT":  (proxyL1HT,  SPblue,   20),
    "Proxy vs HLT HT": (proxyHLTHT, SPred,    21),
    "L1 vs HLT HT":    (l1HLTHT,    SPdgreen, 22),
    "Proxy vs Gen HT": (proxyGenHT, SPpurple, 23),   # signal only
}

samples = ["2024", "MC"] + list(signalDict.keys())
nS = len(samples)
nC = len(categories)
step = 0.16   # horizontal spacing between categories inside a sample slot

# Collect the points first so the y range can be set from the data
points = {}   # catName -> list of (x, 1-rho)
allVals = []
print(f"\n{'category':18s}" + "".join(f"{s:>14s}" for s in samples))
for i, (catName, (histDict, color, marker)) in enumerate(categories.items()):
    pts = []
    row = f"{catName:18s}"
    for b, s in enumerate(samples):
        if s in histDict:
            r = histDict[s].GetCorrelationFactor()
            row += f"{r:14.4f}"
            d = 1.0 - r
            if d > 0:
                x = b + 0.5 + (i - (nC - 1) / 2.0) * step
                pts.append((x, d))
                allVals.append(d)
            else:
                print(f"  (skipping {catName}/{s}: 1-rho = {d:.2e} <= 0)")
        else:
            row += f"{'-':>14s}"
    print(row)
    points[catName] = pts

ymin = 10 ** np.floor(np.log10(min(allVals))) if allVals else 1e-4
ymax = 10 ** np.ceil(np.log10(max(allVals))) if allVals else 1.0

cCorr = ROOT.TCanvas("cCorr", "cCorr", 1100, 700)
cCorr.SetTopMargin(0.14)      # reserved strip for the legend
cCorr.SetBottomMargin(0.22)
cCorr.SetLeftMargin(0.10)
cCorr.SetLogy(1)
cCorr.SetGridy(1)

# Frame histogram: provides axes and sample labels
frame = ROOT.TH1D("corrFrame", "", nS, 0, nS)
for b, s in enumerate(samples, start=1):
    frame.GetXaxis().SetBinLabel(b, s)
frame.SetMinimum(ymin)
frame.SetMaximum(ymax)
frame.GetYaxis().SetTitle("1 - #rho")
frame.GetYaxis().SetTitleOffset(1.0)
frame.GetXaxis().SetLabelSize(0.04)
frame.GetXaxis().LabelsOption("v")
frame.Draw("AXIS")

# Legend sits in the top margin, above the plotting area
legCorr = ROOT.TLegend(0.10, 0.865, 0.90, 0.97)
legCorr.SetNColumns(2)
legCorr.SetBorderSize(0)
legCorr.SetFillStyle(0)

graphs = []   # keep alive
for catName, (histDict, color, marker) in categories.items():
    pts = points[catName]
    if not pts:
        continue
    g = ROOT.TGraph(len(pts))
    for k, (x, y) in enumerate(pts):
        g.SetPoint(k, x, y)
    g.SetMarkerStyle(marker)
    g.SetMarkerSize(1.4)
    g.SetMarkerColor(color)
    g.SetLineColor(color)
    g.Draw("P SAME")
    legCorr.AddEntry(g, catName, "p")
    graphs.append(g)

legCorr.Draw("SAME")

# Light vertical separators between samples
seps = []
for b in range(1, nS):
    l = ROOT.TLine(b, ymin, b, ymax)
    l.SetLineStyle(3)
    l.SetLineColor(ROOT.kGray + 1)
    l.Draw("SAME")
    seps.append(l)

cCorr.Update()
cCorr.SaveAs("plotsHT/correlationSummary.pdf")