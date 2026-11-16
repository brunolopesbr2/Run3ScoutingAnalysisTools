import os
import numpy as np
import ROOT
from IPython.display import Image, display

ROOT.EnableImplicitMT()
ROOT.gStyle.SetOptTitle(0)   # we draw our own title (see make_plot)

import matplotlib
import matplotlib.pyplot as plt

# =====================================================================
#  Configuration
# =====================================================================
# isSignal = False -> Data vs background MC   (muon-triggered selection)
# isSignal = True  -> Signal A / Signal B vs background MC (naive: no muon requirement)
isSignal = False

Fit = False

JECVar = ""  # "", "JECup" or "JECdown"  (applies to all MC trees)

ht_mode = "hltNeutralPlusChargedPFCands" #Use "hltNeutralPlusChargedPFCands" for the proxy
FileLabel = ht_mode
plotsPath = "plots_newJEC/"

#dataEras = ["2024C", "2024D", "2024E", "2024F", "2024G", "2024H", "2024I", "2024"]
dataEras = ['2024']


# Trigger menu: L1_HTT280er, L1_ETT2000, L1_SingleJet180, L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5
# passHTTrigger is the logical OR
Trigger = "passHTTrigger"

# Histogram binning
NBINS, XMIN, XMAX = 30, 0, 1500

HT_EXPR = ("hltPFCands_NeutralEnergy_JetMatch + "
           "(0.8 - 0.6*exp(-hltHT/300.0)) * hltPFCands_ChargedEnergy_JetMatch")

# Range of the lower (ratio) pad
RATIO_RANGE_DATA = (0.1, 1.2)    # Data / MC
RATIO_RANGE_SIGNAL = (0.0, 3.0)  # Signal / Background MC  (adjust to taste)


# =====================================================================
#  File lists
# =====================================================================
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


# ---- Background MC ----
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

# ---- Signal MC ----
def HiggsPath(ms, ctau):
    return (f"Signal/GluGluH-Hto2Sto4D_Par-ctauS-{ctau}-MH-125-MS-{ms}_TuneCP5_13p6TeV_powheg-pythia8/"
            f"ScoutingMC_2024_Higgs_{ms}_{ctau}_TriggerEffs_v6/")

def StopPathPrompt(ms, ctau):
    # NOTE: pattern inferred from your Higgs_55_10 path -- check the 0p1 folder names
    return (f"Signal/StopStopbarTo2Dbar2D_M-{ms}_ctau-{ctau}mm_100kEvts_v2/"
            f"ScoutingMC_2024_StopToD_{ms}_{ctau}_TriggerEffs_v6/")

def StopPathDisplaced(ms, ctau):
    # NOTE: pattern inferred from your Higgs_55_10 path -- check the 0p1 folder names
    return (f"Signal/StopStopbarTo2Dbar2D_M-{ms}_CTau-{ctau}mm_Summer24_100k_v2/"
            f"ScoutingMC_2024_StopToD_{ms}_{ctau}_TriggerEffs_v6/")

signalDict = {
    "Higgs_15_0p1": FileList(HiggsPath(55, "0p1")),
    "Higgs_15_10":  FileList(HiggsPath(55, "10")),
    "Higgs_55_0p1": FileList(HiggsPath(55, "0p1")),
    "Higgs_55_10":  FileList(HiggsPath(55, "10")),
    "Stop_200_0p1": FileList(StopPathPrompt(200, '0p1')),
    "Stop_200_10":  FileList(StopPathDisplaced(200, '10')),
    "Stop_800_0p1": FileList(StopPathPrompt(800, '0p1')),
    "Stop_800_10":  FileList(StopPathDisplaced(800, '10'))
}

# One plot per family: the two signals to overlay (the background MC is always the reference)
signalFamilies = {
    "Higgs_15": ["Higgs_15_0p1", "Higgs_15_10"],
    "Higgs_55": ["Higgs_55_0p1", "Higgs_55_10"],
    "Stop_200": ["Stop_200_0p1", "Stop_200_10"],
    "Stop_800": ["Stop_800_0p1", "Stop_800_10"]
}

# ---- Data ----
dataDict = {
    "2024C": FileList("TriggerEffs_Data/ScoutingMonitor_2024C_TriggerEffs_v6/"),
    "2024D": FileList("TriggerEffs_Data/ScoutingMonitor_2024D_TriggerEffs_v6/"),
    "2024E": FileList("TriggerEffs_Data/ScoutingMonitor_2024E_TriggerEffs_v6/"),
    "2024F": FileList("TriggerEffs_Data/ScoutingMonitor_2024F_TriggerEffs_v6/"),
    "2024G": FileList("TriggerEffs_Data/ScoutingMonitor_2024G_TriggerEffs_v6/"),
    "2024H": FileList("TriggerEffs_Data/ScoutingMonitor_2024H_TriggerEffs_v6/"),
    "2024I": FileList("TriggerEffs_Data/ScoutingMonitor_2024I_TriggerEffs_v6/"),
}

# =====================================================================
#  Colours
# =====================================================================
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

# =====================================================================
#  Selections
# =====================================================================
# Naive selection (no muon requirement): used for the signals
naive_num_filter = f"({Trigger} == 1)"
naive_den_filter = "1"

# Muon-triggered selection: used for data and for the background MC
muon_num_filter = f"({Trigger} == 1) && (passMuonTrigger == 1) && (mu1s_pt > 20)"
muon_den_filter = "(passMuonTrigger == 1) && (mu1s_pt > 20)"


# =====================================================================
#  Helpers
# =====================================================================
def new_hist_pair(tag):
    num = ROOT.TH1F(f"{tag}_num", f"{tag}_num", NBINS, XMIN, XMAX)
    den = ROOT.TH1F(f"{tag}_den", f"{tag}_den", NBINS, XMIN, XMAX)
    num.Sumw2()  # proper error tracking for weighted fills
    den.Sumw2()
    return num, den
 
 
def fill_data(files, tag):
    """Numerator/denominator histograms for data (weights = theWeight)."""
    num_h, den_h = new_hist_pair(tag)
    if not files:
        print(f"WARNING: no files for {tag}")
        return num_h, den_h
 
    df = ROOT.RDataFrame("triggerEffs/objectTree", files)
    df = df.Define("hltNeutralPlusChargedPFCands", HT_EXPR)
    d_num = df.Filter(muon_num_filter).Histo1D(("num", "num", NBINS, XMIN, XMAX), ht_mode, "theWeight")
    d_den = df.Filter(muon_den_filter).Histo1D(("den", "den", NBINS, XMIN, XMAX), ht_mode, "theWeight")
    num_h.Add(d_num.GetPtr())
    den_h.Add(d_den.GetPtr())
    return num_h, den_h
 
 
def fill_mc(procs, tag, num_filter, den_filter):
    """Numerator/denominator histograms for a dict {process: [files]}, using the given
    numerator/denominator selections. Each process is normalised by its own sum of genWeights before being merged."""
    num_h, den_h = new_hist_pair(tag)
 
    for key, files in procs.items():
        print(f"Processing {key} ...")
        if not files:
            print(f"WARNING: no files for {key}, skipping")
            continue
 
        df = ROOT.RDataFrame(f"triggerEffs{JECVar}/objectTree", files)
        df = df.Define("hltNeutralPlusChargedPFCands", HT_EXPR)
 
        sum_genweight = df.Sum("genWeight").GetValue()
        print("Total genWeight sum =", sum_genweight)
        df = df.Define("weight", f"theWeight / {sum_genweight}")
 
        d_num = df.Filter(num_filter).Histo1D(("mc_num", "mc_num", NBINS, XMIN, XMAX), ht_mode, "weight")
        d_den = df.Filter(den_filter).Histo1D(("mc_den", "mc_den", NBINS, XMIN, XMAX), ht_mode, "weight")
        num_h.Add(d_num.GetPtr())
        den_h.Add(d_den.GetPtr())
 
    print(f"finished processing {tag}")
    return num_h, den_h
 
 
def build_eff(name, num, den, weighted, color, marker=20):
    eff = ROOT.TEfficiency(name, "", NBINS, XMIN, XMAX)
    if weighted:
        eff.SetUseWeightedEvents()                           # tell ROOT the sample is weighted
        eff.SetStatisticOption(ROOT.TEfficiency.kBUniform)   # Bayesian for weighted MC
    else:
        eff.SetStatisticOption(ROOT.TEfficiency.kFCP)        # exact Clopper-Pearson for integer counts
    eff.SetTotalHistogram(den, "f")
    eff.SetPassedHistogram(num, "f")
    eff.SetConfidenceLevel(0.6827)                           # 1-sigma
 
    eff.SetTitle(";H_{T} proxy [GeV];Efficiency")
    eff.SetLineColor(color)
    eff.SetMarkerColor(color)
    eff.SetMarkerStyle(marker)
    return eff

def signal_label(key):
    # "Higgs_55_0p1" -> "Higgs, m_{S} = 55 GeV, c#tau = 0.1 mm"
    # "Stop_200_10"  -> "RPV SUSY, m_{#tilde{t}} = 200 GeV, c#tau = 10 mm"
    parts = key.split("_")
    ctau = parts[-1].replace("p", ".")
    mass = parts[1]
    if parts[0] == "Stop":
        return f"RPV SUSY, m_{{#tilde{{t}}}} = {mass} GeV, c#tau = {ctau} mm"
    return f"{parts[0]}, m_{{S}} = {mass} GeV, c#tau = {ctau} mm"
 
 
def make_ratio(g_num, g_ref, keep_placeholders):
    """Ratio g_num / g_ref with uncorrelated asymmetric error propagation.
 
    keep_placeholders=True reproduces the original behaviour: skipped bins stay
    as (0,0) points in the graph (this matters for the saved .npy arrays).
    keep_placeholders=False drops skipped bins entirely (cleaner for plotting).
    """
    n = g_num.GetN()
    # NB: don't write TGraphAsymmErrors(0): PyROOT treats the int 0 as a null pointer
    # and picks the TH1* constructor -> "Pointer to histogram is null" + segfault
    ratio = ROOT.TGraphAsymmErrors(n) if keep_placeholders else ROOT.TGraphAsymmErrors()
    j = 0
    for i in range(n):
        x     = g_num.GetX()[i]
        eff_n = g_num.GetY()[i]
        eff_r = g_ref.GetY()[i]
        if eff_r <= 0 or eff_n <= 0:
            continue
 
        r = eff_n / eff_r
        err_n_lo, err_n_hi = g_num.GetEYlow()[i], g_num.GetEYhigh()[i]
        err_r_lo, err_r_hi = g_ref.GetEYlow()[i],  g_ref.GetEYhigh()[i]
 
        # Low numerator error + high reference error -> lower ratio error (and vice versa)
        err_lo = r * np.sqrt((err_n_lo / eff_n)**2 + (err_r_hi / eff_r)**2)
        err_hi = r * np.sqrt((err_n_hi / eff_n)**2 + (err_r_lo / eff_r)**2)
 
        idx = i if keep_placeholders else j
        ratio.SetPoint(idx, x, r)
        ratio.SetPointError(idx, g_num.GetEXlow()[i], g_num.GetEXhigh()[i], err_lo, err_hi)
        j += 1
    return ratio
 
 
def save_ratio_npy(ratio_graph, out_base):
    n_pts = ratio_graph.GetN()
    x_upper   = np.array([ratio_graph.GetX()[i] + ratio_graph.GetEXhigh()[i] for i in range(n_pts)])
    ratio_nom = np.array([ratio_graph.GetY()[i] for i in range(n_pts)])
    ratio_up  = np.array([ratio_graph.GetY()[i] + ratio_graph.GetEYhigh()[i] for i in range(n_pts)])
    ratio_dn  = np.array([ratio_graph.GetY()[i] - ratio_graph.GetEYlow()[i]  for i in range(n_pts)])
 
    np.save(out_base + "_xedge.npy",   x_upper)
    np.save(out_base + "_nominal.npy", ratio_nom)
    np.save(out_base + "_up.npy",      ratio_up)
    np.save(out_base + "_down.npy",    ratio_dn)
 
 
def make_plot(tag, curves, ratio_ylabel, ratio_range, out_pdf, keep_placeholders):
    """
    curves: list of dicts {label, eff, color}. curves[0] is the REFERENCE
            (drawn first, denominator of every ratio); the others are drawn on top
            and divided by the reference in the lower pad.
    Returns (canvas, ratio_graphs, keep) -- keep these alive so PyROOT doesn't delete them.
    """
    keep = []
 
    c = ROOT.TCanvas(f"c_{tag}", "c", 800, 900)
    pad1 = ROOT.TPad(f"pad1_{tag}", "pad1", 0, 0.3, 1, 1.0)
    pad2 = ROOT.TPad(f"pad2_{tag}", "pad2", 0, 0.0, 1, 0.3)
    pad1.SetBottomMargin(0.02)
    pad2.SetTopMargin(0.02)
    pad2.SetBottomMargin(0.35)
    pad1.Draw()
    pad2.Draw()
 
    # ---------------- upper pad: efficiencies ----------------
    pad1.cd()
    for k, cv in enumerate(curves):
        cv["eff"].Draw("PE" if k == 0 else "PE SAME")
 
    c.Update()  # needed before accessing the painted graph
    g_axis = curves[0]["eff"].GetPaintedGraph()  # reference graph carries the axes
    g_axis.GetXaxis().SetLimits(XMIN, XMAX)
    c.Update()
    g_axis.GetXaxis().SetLabelSize(0)   # hide x labels on upper pad
    g_axis.GetXaxis().SetTitleSize(0)   # hide x title on upper pad
    g_axis.GetYaxis().SetTitleOffset(1.2)

    if(ht_mode == "hltNeutralPlusChargedPFCands"):
        vl = ROOT.TLine(400, 0, 400, 1.1)
        vl.SetLineStyle(2)
        vl.SetLineColor(ROOT.kGray + 2)
        vl.SetLineWidth(2)
        vl.Draw("SAME")
        keep.append(vl)
 
    # ---------------- optional error-function fits ----------------
    if Fit:
        for k, cv in enumerate(curves):
            graph = cv["eff"].CreateGraph()
            f = ROOT.TF1(f"fit_{tag}_{k}", "[0] + 0.5*[1]*(1 + TMath::Erf((x-[2])/[3]))", 0, 1500)
            f.SetParNames("A", "B", "#mu_{on}", "#sigma_{on}")
            f.SetParameters(0.0, 1.0, 500.0, 100.0)
            f.SetParLimits(0, 0.0, 0.5)   # baseline >= 0
            f.SetParLimits(1, 0.0, 1.0)   # plateau in [0, 1]
            f.SetParLimits(2, 0, 2000)    # mu within range
            f.SetParLimits(3, 1, 1000)    # sigma positive
            graph.Fit(f, "R W")
            cv["fit_params"] = [f.GetParameter(i) for i in range(4)]
            cv["fit_errors"] = [f.GetParError(i) for i in range(4)]
            f.SetLineColor(cv["color"])
            f.SetLineWidth(2)
            f.SetLineStyle(1 if k == 0 else 2)
            f.Draw("SAME")
            keep += [graph, f]
 
    # ---------------- lower pad: ratios to the reference ----------------
    pad2.cd()
    g_ref = curves[0]["eff"].CreateGraph()
    keep.append(g_ref)
 
    ratio_graphs = []
    single_ratio = (len(curves) == 2)
    for k, cv in enumerate(curves[1:]):
        g_num = cv["eff"].CreateGraph()
        rg = make_ratio(g_num, g_ref, keep_placeholders)
        col = ROOT.kBlack if single_ratio else cv["color"]
        rg.SetMarkerStyle(cv["eff"].GetMarkerStyle())
        rg.SetMarkerColor(col)
        rg.SetLineColor(col)
        rg.SetTitle("")
 
        if k == 0:  # first ratio graph carries the axes
            if(ht_mode == 'hltHT'):
                rg.GetXaxis().SetTitle("HLT H_{T} [GeV]")
            else:
                rg.GetXaxis().SetTitle("H_{T} proxy [GeV]")
            rg.GetYaxis().SetTitle(ratio_ylabel)
            rg.GetYaxis().SetRangeUser(*ratio_range)
            rg.GetYaxis().SetNdivisions(505)
            rg.GetXaxis().SetLimits(XMIN, XMAX)
            rg.GetXaxis().SetTitleSize(0.12)
            rg.GetXaxis().SetLabelSize(0.10)
            rg.GetYaxis().SetTitleSize(0.10)
            rg.GetYaxis().SetLabelSize(0.08)
            rg.GetYaxis().SetTitleOffset(0.5)
            rg.Draw("APE")
        else:
            rg.Draw("PE SAME")
 
        ratio_graphs.append(rg)
        keep += [g_num]
 
    # Reference line at 1 and the 400 GeV marker
    line = ROOT.TLine(XMIN, 1, XMAX, 1)
    line.SetLineStyle(2)
    line.SetLineColor(ROOT.kGray + 1)
    line.Draw("SAME")

    if (ht_mode == "hltNeutralPlusChargedPFCands"):
        vline = ROOT.TLine(400, ratio_range[0], 400, ratio_range[1])
        vline.SetLineStyle(2)
        vline.SetLineColor(ROOT.kGray + 2)
        vline.SetLineWidth(2)
        vline.Draw("SAME")
        keep += [line, vline]
 
    # ---------------- final touches on the upper pad ----------------
    pad1.cd()
    c.Update()
    g_axis.GetYaxis().SetRangeUser(0.0, 1.1)
    c.Update()
 
    # legend: wide enough for the long signal labels, with tight marker-to-text spacing
    # and taller rows so the subscript (m_{#tilde{t}}) isn't squeezed
    leg = ROOT.TLegend(0.40, 0.18, 0.88, 0.18 + 0.07 * len(curves))
    leg.SetMargin(0.08)        # fraction of the box width reserved for the marker (default 0.25)
    leg.SetTextFont(42)
    leg.SetTextSize(0.032)     # fixed size instead of auto-fill
    for cv in curves:
        leg.AddEntry(cv["eff"], cv["label"], "pe")
    leg.Draw("SAME")
    keep.append(leg)
 
    c.Draw()
    c.SaveAs(out_pdf)
    return c, ratio_graphs, keep

def extract_ratio(ratio_graph):
    """Pull plain numpy arrays out of a ratio TGraphAsymmErrors.
    Placeholder points (skipped bins, kept as (0,0) when keep_placeholders=True) are dropped,
    and the real bin centres/widths are used instead of reconstructing edges."""
    n = ratio_graph.GetN()
    x   = np.array([ratio_graph.GetX()[i]       for i in range(n)])
    y   = np.array([ratio_graph.GetY()[i]       for i in range(n)])
    exl = np.array([ratio_graph.GetEXlow()[i]   for i in range(n)])
    exh = np.array([ratio_graph.GetEXhigh()[i]  for i in range(n)])
    eyl = np.array([ratio_graph.GetEYlow()[i]   for i in range(n)])
    eyh = np.array([ratio_graph.GetEYhigh()[i]  for i in range(n)])
    ok = y > 0
    return dict(x=x[ok], y=y[ok], exl=exl[ok], exh=exh[ok], eyl=eyl[ok], eyh=eyh[ok])


def plot_era_ratios(ratios, out_path, ylim=(0.1, 1.5)):
    """ratios: dict {era: extract_ratio(...) dict}"""
    colors = plt.cm.tab10.colors
    fig, ax = plt.subplots(figsize=(10, 6))

    for (era, r), color in zip(ratios.items(), colors):
        ax.errorbar(
            r["x"], r["y"],
            xerr=[r["exl"], r["exh"]],
            yerr=[r["eyl"], r["eyh"]],
            fmt='o', color=color, markersize=4,
            label=era if era != "2024" else "2024 (all)",
        )

    ax.axhline(1.0, color='black', linestyle='--', linewidth=1)
    ax.set_xlabel(r'Proxy $H_T$ [GeV]', fontsize=13)
    ax.set_ylabel('Data / MC', fontsize=13)
    ax.set_title('HT Trigger Efficiency Ratio (Data / MC) - All Eras', fontsize=13)
    ax.set_xlim(XMIN, XMAX)
    ax.set_ylim(*ylim)
    ax.legend(fontsize=10, ncol=2)
    ax.grid(True, linestyle=':', alpha=0.5)

    plt.tight_layout()
    fig.savefig(out_path)
    plt.show()
    print(f"Saved to {out_path}")
 
 
# =====================================================================
#  Main
# =====================================================================
canvases = []  # keep everything alive (important in notebooks)
 
# Background MC (always with the muon requirement) is common to both modes -> fill once
bkg_num, bkg_den = fill_mc(processDict, "bkg", muon_num_filter, muon_den_filter)
eff_bkg = build_eff("eff_bkg", bkg_num, bkg_den, weighted=True, color=SPdblue)
 
if not isSignal:
    # ------------------ Data vs background MC ------------------
    era_ratios = {}   # <-- new

    for dataEra in dataEras:
        if dataEra == "2024":
            files = [f for k in dataDict for f in dataDict[k]]
        else:
            files = dataDict[dataEra]

        data_num, data_den = fill_data(files, f"data_{dataEra}")
        eff_data = build_eff(f"eff_data_{dataEra}", data_num, data_den, weighted=False, color=SPdred)

        curves = [
            {"label": f"Background MC {JECVar}", "eff": eff_bkg,  "color": SPdblue},
            {"label": f"{dataEra} Data",         "eff": eff_data, "color": SPdred},
        ]
        out_pdf = f"{plotsPath}HT_eff_{FileLabel}_{dataEra}_{JECVar}ExpFit_300Scale.pdf"

        out = make_plot(dataEra, curves, "Data / MC", RATIO_RANGE_DATA, out_pdf, keep_placeholders=True)
        canvases.append(out)

        out_base = f"{plotsPath}/weights_trigger_{dataEra}"
        save_ratio_npy(out[1][0], out_base)

        era_ratios[dataEra] = extract_ratio(out[1][0])   # <-- new

    # Per-era ratio comparison (uses the ratios computed above)
    plot_era_ratios(era_ratios, f"{plotsPath}/HT_ratio_check_{JECVar}.pdf")
 
else:
    # ------------------ Signal (2 per family) vs background MC ------------------
    sig_colors  = [SPred, SPgreen]
    sig_markers = [21, 22]
 
    for family, keys in signalFamilies.items():
        curves = [{"label": f"Bkg MC {JECVar} (#mu sel.)", "eff": eff_bkg, "color": SPdgrey}]
        eff_bkg.SetLineColor(SPdgrey)
        eff_bkg.SetMarkerColor(SPdgrey)
 
        for k, key in enumerate(keys):
            if key not in signalDict or not signalDict[key]:
                print(f"WARNING: no files for signal '{key}', skipping")
                continue
            s_num, s_den = fill_mc({key: signalDict[key]}, key, naive_num_filter, naive_den_filter)
            eff_s = build_eff(f"eff_{key}", s_num, s_den, weighted=True,
                              color=sig_colors[k], marker=sig_markers[k])
            curves.append({"label": signal_label(key), "eff": eff_s, "color": sig_colors[k]})
 
        if len(curves) < 2:
            print(f"WARNING: nothing to plot for family {family}")
            continue
 
        out_pdf = f"{plotsPath}HT_eff_signal_{family}_{FileLabel}_{JECVar}ExpFit_300Scale.pdf"
 
        out = make_plot(family, curves, "Signal / Bkg", RATIO_RANGE_SIGNAL, out_pdf, keep_placeholders=False)
        canvases.append(out)