import ROOT
import numpy as np

ROOT.gStyle.SetOptStat(0)


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


def _make_canvas(plotFileName):
    canvas_name = f"c_{plotFileName.replace('/', '_').replace('.', '_')}"
    c = ROOT.TCanvas(canvas_name, canvas_name, 800, 900)
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
    pad2 = ROOT.TPad("pad2", "pad2", 0, 0.0, 1, 0.3)
    for p in (pad1, pad2):
        p.SetLeftMargin(0.15)    # identical horizontal margins -> identical pixel width
        p.SetRightMargin(0.05)
    pad1.SetBottomMargin(0.02)
    pad2.SetTopMargin(0.02)
    pad2.SetBottomMargin(0.35)
    pad1.Draw()
    pad2.Draw()
    return c, pad1, pad2


def _y_range(hists, logy, is_teff):
    """Automatic y range for the upper pad."""
    vals = []
    for h in hists:
        if is_teff:
            n = h.GetTotalHistogram().GetNbinsX()
            vals += [h.GetEfficiency(i) for i in range(1, n + 1)]
        else:
            vals += [h.GetBinContent(i) for i in range(1, h.GetNbinsX() + 1)]
    pos = [v for v in vals if v > 0]
    top = max(pos) if pos else 1.0
    if logy:
        bottom = min(pos) / 3.0 if pos else 1e-4
        return bottom, top * 5.0
    return 0.0, (1.3 if is_teff else top * 1.3)


def _draw_frames(pad1, pad2, x_min, x_max, y_lo, y_hi, title, x_axis, y_axis,
                 logy, ratio_range=(0.5, 1.5)):
    """Draw identical-x frames in both pads. All data is drawn on top with SAME."""
    pad1.cd()
    pad1.SetLogy(1 if logy else 0)           # set BEFORE drawing the frame
    f1 = pad1.DrawFrame(x_min, y_lo, x_max, y_hi, f"{title};;{y_axis}")
    f1.GetXaxis().SetLabelSize(0)
    f1.GetXaxis().SetTitleSize(0)
    f1.GetYaxis().SetTitleOffset(1.4)

    pad2.cd()
    f2 = pad2.DrawFrame(x_min, ratio_range[0], x_max, ratio_range[1], f";{x_axis};Ratio")
    f2.GetXaxis().SetTitleSize(0.12)
    f2.GetXaxis().SetLabelSize(0.10)
    f2.GetXaxis().SetTitleOffset(1.0)
    f2.GetYaxis().SetTitleSize(0.10)
    f2.GetYaxis().SetLabelSize(0.08)
    f2.GetYaxis().SetTitleOffset(0.5)
    f2.GetYaxis().SetNdivisions(505)
    pad1.cd()
    return f1, f2


def _ratio_graph(a, b, is_teff):
    """a/b as a TGraphAsymmErrors, using each bin's own center and half-width."""
    ref = a.GetTotalHistogram() if is_teff else a
    g = ROOT.TGraphAsymmErrors()
    k = 0
    for i in range(1, ref.GetNbinsX() + 1):
        x, ex = ref.GetBinCenter(i), ref.GetBinWidth(i) / 2.0
        if is_teff:
            ya, yb = a.GetEfficiency(i), b.GetEfficiency(i)
            ea_lo, ea_hi = a.GetEfficiencyErrorLow(i), a.GetEfficiencyErrorUp(i)
            eb_lo, eb_hi = b.GetEfficiencyErrorLow(i), b.GetEfficiencyErrorUp(i)
        else:
            ya, yb = a.GetBinContent(i), b.GetBinContent(i)
            ea_lo = ea_hi = a.GetBinError(i)
            eb_lo = eb_hi = b.GetBinError(i)
        if yb <= 0:
            continue
        r = ya / yb
        if ya > 0:
            err_lo = r * np.sqrt((ea_lo / ya)**2 + (eb_hi / yb)**2)
            err_hi = r * np.sqrt((ea_hi / ya)**2 + (eb_lo / yb)**2)
        else:
            err_lo, err_hi = 0, ea_hi / yb
        g.SetPoint(k, x, r)
        g.SetPointError(k, ex, ex, err_lo, err_hi)
        k += 1
    return g   # only filled points exist, so no stray (0,0) points


def _style_ratio(g, color):
    g.SetMarkerStyle(20)
    g.SetMarkerColor(color)
    g.SetLineColor(color)


def _style_inputs(hists, colors, line_styles, is_teff):
    for h, col, ls in zip(hists, colors, line_styles):
        h.SetLineColor(col)
        h.SetMarkerColor(col)
        h.SetMarkerStyle(20)
        h.SetLineWidth(2)
        if not is_teff:
            h.SetLineStyle(ls)


def _x_range(histo1, is_teff):
    ax = (histo1.GetTotalHistogram() if is_teff else histo1).GetXaxis()
    return ax.GetXmin(), ax.GetXmax()


def _draw_vlines(vline, y_lo, y_hi):
    lines = []
    for vl_x in vline:
        if vl_x is not None:
            vl = ROOT.TLine(vl_x, y_lo, vl_x, y_hi)
            vl.SetLineStyle(2)
            vl.SetLineColor(ROOT.kGray + 2)
            vl.SetLineWidth(2)
            vl.Draw("SAME")
            lines.append(vl)
    return lines   # keep alive until SaveAs


def compare_plot(histo1, histo2, legend1="legend1", legend2="legend2", plot_title="generic title",
                 x_axis="generic X", y_axis="Events", logy=False, plotFileName="plots/ForgotToChange.pdf",
                 vline=[None], is_teff=False, is_profile=False, ratio_range=(0.5, 1.5)):
    c, pad1, pad2 = _make_canvas(plotFileName)
    hists = [histo1, histo2]
    _style_inputs(hists, [SPdblue, SPdred], [1, 2], is_teff)

    if not is_teff and not is_profile:
        if histo1.Integral() > 0: histo1.Scale(1.0 / histo1.Integral())
        if histo2.Integral() > 0: histo2.Scale(1.0 / histo2.Integral())

    x_min, x_max = _x_range(histo1, is_teff)
    y_lo, y_hi = _y_range(hists, logy, is_teff)
    f1, f2 = _draw_frames(pad1, pad2, x_min, x_max, y_lo, y_hi, plot_title, x_axis, y_axis, logy, ratio_range)

    # upper pad
    pad1.cd()
    if is_teff:
        draw_opt = "P SAME"
    elif is_profile:
        draw_opt = "PE SAME"
    else:
        draw_opt = "HIST SAME"
    histo1.Draw(draw_opt)
    histo2.Draw(draw_opt)
    vlines = _draw_vlines(vline, y_lo, y_hi)

    leg = ROOT.TLegend(0.65, 0.75, 0.9, 0.9)
    opt = "lp" if is_teff else "l"
    leg.AddEntry(histo1.GetPtr() if hasattr(histo1, "GetPtr") else histo1, legend1, opt)
    leg.AddEntry(histo2.GetPtr() if hasattr(histo2, "GetPtr") else histo2, legend2, opt)
    leg.Draw("SAME")

    # lower pad
    pad2.cd()
    ratio_graph = _ratio_graph(histo1, histo2, is_teff)
    _style_ratio(ratio_graph, ROOT.kBlack)
    ratio_graph.Draw("PE")
    ref_line = ROOT.TLine(x_min, 1, x_max, 1)
    ref_line.SetLineStyle(2)
    ref_line.SetLineColor(ROOT.kBlack)
    ref_line.Draw("SAME")

    plotFileName += "_LogY.pdf" if logy else ".pdf"
    c.cd()
    c.Update()
    c.SaveAs(plotFileName)


def compare_3plot(histo1, histo2, histo3, legend1="legend1", legend2="legend2", legend3="legend3",
                  plot_title="generic title", x_axis="generic X", y_axis="Events", logy=False,
                  plotFileName="plots/ForgotToChange.pdf", vline=[None], is_teff=False,
                  ratio_range=(0.5, 1.5)):
    c, pad1, pad2 = _make_canvas(plotFileName)
    hists = [histo1, histo2, histo3]
    _style_inputs(hists, [SPdblue, SPdred, SPdyellow], [1, 2, 3], is_teff)

    if not is_teff:
        for h in hists:
            if h.Integral() > 0: h.Scale(1.0 / h.Integral())

    x_min, x_max = _x_range(histo1, is_teff)
    y_lo, y_hi = _y_range(hists, logy, is_teff)
    f1, f2 = _draw_frames(pad1, pad2, x_min, x_max, y_lo, y_hi, plot_title, x_axis, y_axis, logy, ratio_range)

    pad1.cd()
    draw_opt = "P SAME" if is_teff else "HIST SAME"
    for h in hists:
        h.Draw(draw_opt)
    vlines = _draw_vlines(vline, y_lo, y_hi)

    leg = ROOT.TLegend(0.65, 0.75, 0.9, 0.9)
    opt = "lp" if is_teff else "l"
    for h, name in zip(hists, [legend1, legend2, legend3]):
        leg.AddEntry(h.GetPtr() if hasattr(h, "GetPtr") else h, name, opt)
    leg.Draw("SAME")

    pad2.cd()
    ratio1 = _ratio_graph(histo2, histo1, is_teff)   # histo2 / histo1
    ratio2 = _ratio_graph(histo3, histo1, is_teff)   # histo3 / histo1
    _style_ratio(ratio1, SPdred)
    _style_ratio(ratio2, SPdyellow)
    ratio1.Draw("PE")
    ratio2.Draw("PE")
    ref_line = ROOT.TLine(x_min, 1, x_max, 1)
    ref_line.SetLineStyle(2)
    ref_line.SetLineColor(SPdblue)
    ref_line.Draw("SAME")

    plotFileName += "_LogY.pdf" if logy else ".pdf"
    c.cd()
    c.Update()
    c.SaveAs(plotFileName)
#Create the histo dicts
originalTrack_pt = {}
originalTrack_eta = {}
originalTrack_phi = {}
originalTrack_dxy = {}
newTrack_pt = {}
newTrack_eta = {}
newTrack_phi = {}
newTrack_dxy = {}
unmovedTrack_pt = {}
unmovedTrack_eta = {}
unmovedTrack_phi = {}
unmovedTrack_dxy = {}
movedTrack_pt = {}
movedTrack_eta = {}
movedTrack_phi = {}
movedTrack_dxy = {}

nMovedTracks = {}
nSurvivedTracks = {}
nCloseBGTracks = {}
nCloseTotalTracks = {}

nSurvivedTracksVsdPVV = {}
nCloseBGTracksVsdPVV = {}
nCloseTotalTracksVsdPVV = {}

nSurvivedSeedTracks = {}
nCloseBGSeedTracks = {}
nCloseTotalSeedTracks = {}

nSurvivedSeedTracksVsdPVV = {}
nCloseBGSeedTracksVsdPVV = {}
nCloseTotalSeedTracksVsdPVV = {}

moveVertexXY = {}
moveVertexZ = {}

nPV = {}
pvXY = {}
pvZ = {}

matchVertexDBV = {}
matchVertexDBV3D = {}
matchVertexDBVerr = {}
matchVertexCosT = {}
matchVertexChi2 = {}
matchVertexNtk = {}

moveVertexDPVV = {}
moveVertexDPVV3D = {}
moveVertexDBV = {}
moveVertexDBV3D = {}

matchVertex_sumPt = {}
matchVertex_netPt = {}
matchVertex_netP = {}
matchVertex_deltaR = {}

moveVertex_sumPt = {}
moveVertex_netPt = {}
moveVertex_netP = {}
moveVertex_deltaR = {}

signal_sumPt = {}
signal_netPt = {}
signal_netP = {}
signal_deltaR = {}
signal_DBV = {}
signal_DBV3D = {}

matchVertexWeightVariables = {}

#Efficiency vs. Jet 1 and 2 eta
vertexEffJet1Eta_num = {}
vertexEffJet1Eta_den = {}
vertexEffJet1Eta = {}

vertexEffJet2Eta_num = {}
vertexEffJet2Eta_den = {}
vertexEffJet2Eta = {}

#Efficiency vs reweighting variables (to be done before reweighting)
vertexEffSumPt_num = {}
vertexEffSumPt_den = {}
vertexEffSumPt = {}

vertexEffNetPt_num = {}
vertexEffNetPt_den = {}
vertexEffNetPt = {}

vertexEffNetP_num = {}
vertexEffNetP_den = {}
vertexEffNetP = {}

vertexEffDeltaR_num = {}
vertexEffDeltaR_den = {}
vertexEffDeltaR = {}

vertexEffdPVV_num = {}
vertexEffdPVV_den = {}
vertexEffdPVV = {}

vertexEffdPVV3D_num = {}
vertexEffdPVV3D_den = {}
vertexEffdPVV3D = {}

#Efficiency vs number of moved / close tracks
vertexEffSurvTracks_num = {}
vertexEffSurvTracks_den = {}
vertexEffSurvTracks = {}

vertexEffCloseBGTracks_num = {}
vertexEffCloseBGTracks_den = {}
vertexEffCloseBGTracks = {}

vertexEffTotalCloseTracks_num = {}
vertexEffTotalCloseTracks_den = {}
vertexEffTotalCloseTracks = {}

vertexEffSurvSeedTracks_num = {}
vertexEffSurvSeedTracks_den = {}
vertexEffSurvSeedTracks = {}

vertexEffCloseBGSeedTracks_num = {}
vertexEffCloseBGSeedTracks_den = {}
vertexEffCloseBGSeedTracks = {}

vertexEffTotalCloseSeedTracks_num = {}
vertexEffTotalCloseSeedTracks_den = {}
vertexEffTotalCloseSeedTracks = {}

#Final efficiency plot
vertexEffdBV_num = {}
vertexEffdBV_den = {}
vertexEffdBV = {}

dBV_edges  = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.4, 2.0], dtype=np.float64)

def model(name, title, edges):
    """RDataFrame model with variable binning."""
    return ROOT.RDF.TH1DModel(name, title, len(edges) - 1, edges)

def loadHistograms(df, eras=["2024"], signals=["Stop_800_1"], debugPlots=False, doLifetimeReweighting=True):
    #Book histos
    for era in eras:
        for signal in signals:
            if (signal == "original"):
                dataKey = era
                weightKey = "weight_noTrigger"
            else:
                dataKey = f'{era}_{signal}'
                weightKey = f"finalWeight_{signal}"

            print(f"Running for {dataKey}...")
            print("Performing TM reweighting...")

            if (signal != "original"):
                df = df.Define(f"tmWeight_{signal}", f'getTMWeight("{era}_{signal}", netP_clamped, dR_clamped)')
                if(doLifetimeReweighting):
                    print("Doing lifetime reweighting...")
                    df = df.Define(f"tmLifetimeWeight_{signal}", f'getTMWeight("lifetime_{era}_{signal}", dPVV_clamped, dPVV3D_clamped)')
                    df = df.Define(f"finalWeight_{signal}", f"weight_noTrigger * tmWeight_{signal} * tmLifetimeWeight_{signal}")
                else:
                    df = df.Define(f"finalWeight_{signal}", f"weight_noTrigger * tmWeight_{signal}")

            dfGood = df.Define("badWeight", f"!std::isfinite({weightKey}) || {weightKey} < 0")
            dfGood = dfGood.Filter("!badWeight")


            print("Booking histograms...")
            if(debugPlots):
                #Track-level plots
                originalTrack_pt[dataKey] = dfGood.Histo1D(("origTrack_pt", "pT of original tracks", 100, 0, 100), "originalTracks_pt", weightKey)
                originalTrack_eta[dataKey] = dfGood.Histo1D(("origTrack_eta", "eta of original tracks", 100, -2.5, 2.5), "originalTracks_eta", weightKey)
                originalTrack_phi[dataKey] = dfGood.Histo1D(("origTrack_phi", "phi of original tracks", 100, -3.5, 3.5), "originalTracks_phi", weightKey)
                originalTrack_dxy[dataKey] = dfGood.Histo1D(("origTrack_dxy", "dxy of original tracks", 100, -2, 2), "originalTracks_dxy", weightKey)

                newTrack_pt[dataKey] = dfGood.Histo1D(("newTrack_pt", "pT of new tracks", 100, 0, 100), "tracks_pt", weightKey)
                newTrack_eta[dataKey] = dfGood.Histo1D(("newTrack_eta", "eta of new tracks", 100, -2.5, 2.5), "tracks_eta", weightKey)
                newTrack_phi[dataKey] = dfGood.Histo1D(("newTrack_phi", "phi of new tracks", 100, -3.5, 3.5), "tracks_phi", weightKey)
                newTrack_dxy[dataKey] = dfGood.Histo1D(("newTrack_dxy", "dxy of new tracks", 100, -2, 2), "tracks_dxy", weightKey)

                movedTrack_pt[dataKey] = dfGood.Histo1D(("movedTrack_pt", "pT of moved tracks", 100, 0, 100), "movedTracks_pt", weightKey)
                movedTrack_eta[dataKey] = dfGood.Histo1D(("movedTrack_eta", "eta of moved tracks", 100, -2.5, 2.5), "movedTracks_eta", weightKey)
                movedTrack_phi[dataKey] = dfGood.Histo1D(("movedTrack_phi", "phi of moved tracks", 100, -3.5, 3.5), "movedTracks_phi", weightKey)
                movedTrack_dxy[dataKey] = dfGood.Histo1D(("movedTrack_dxy", "dxy of moved tracks", 100, -2, 2), "movedTracks_dxy", weightKey)

                pvXY[dataKey] = dfGood.Histo2D(("pvXY", f"Leading PV Position for {dataKey}", 50, -5, 5, 50, -5, 5), "primaryVertex_x", "primaryVertex_y", weightKey)
                pvZ[dataKey] = dfGood.Histo1D(("primaryVertex_z", f"Z of Leading PV for {dataKey}", 100, -12, 12), "primaryVertex_z", weightKey)

            #Track plots
            nMovedTracks[dataKey] = dfGood.Histo1D(("nMovedTracks", "Number of moved tracks", 40, 0, 40), "nMovedTracks", weightKey)
            nSurvivedTracks[dataKey] = dfGood.Histo1D(("nSurvivedTracks", "Number of survived tracks", 40, 0, 40), "nSurvivedTracks", weightKey)
            nCloseBGTracks[dataKey] = dfGood.Histo1D(("nCloseBGTracks", "Number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks", weightKey)
            nCloseTotalTracks[dataKey] = dfGood.Histo1D(("nCloseTotalTracks", "Total of close tracks", 40, 0, 40), "nCloseTotalTracks", weightKey)

            nSurvivedTracksVsdPVV[dataKey] = dfGood.Profile1D(("survivedTracksVsDPVV", "nSurvivedTrakcs vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nSurvivedTracks", weightKey)
            nCloseBGTracksVsdPVV[dataKey] = dfGood.Profile1D(("closeTracksVsDPVV", "nCloseTrakcs vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nCloseBGTracks", weightKey)
            nCloseTotalTracksVsdPVV[dataKey] = dfGood.Profile1D(("totalTracksVsDPVV", "totalTrakcs vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nCloseTotalTracks", weightKey) 

            nSurvivedSeedTracks[dataKey] = dfGood.Histo1D(("nSurvivedTracks", "Number of survived tracks", 40, 0, 40), "nSurvivedTracks_IPsig", weightKey)
            nCloseBGSeedTracks[dataKey] = dfGood.Histo1D(("nCloseBGTracks", "Number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks_IPsig", weightKey)
            nCloseTotalSeedTracks[dataKey] = dfGood.Histo1D(("nCloseTotalTracks", "Total of close tracks", 40, 0, 40), "nCloseTotalTracks_IPsig", weightKey)

            nSurvivedSeedTracksVsdPVV[dataKey] = dfGood.Profile1D(("survivedTracksVsDPVV", "nSurvivedTrakcs vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nSurvivedTracks_IPsig", weightKey)
            nCloseBGSeedTracksVsdPVV[dataKey] = dfGood.Profile1D(("closeTracksVsDPVV", "nCloseTrakcs vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nCloseBGTracks_IPsig", weightKey)
            nCloseTotalSeedTracksVsdPVV[dataKey] = dfGood.Profile1D(("totalTracksVsDPVV", "totalTrakcs vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nCloseTotalTracks_IPsig", weightKey) 

            #Vertex-level plots
            matchVertexDBV[dataKey] = dfGood.Histo1D(("matchedVertex_dBV", f"dBV of matched vertex for {dataKey}", 30, 0, 2), "matchedVertex_dBV", weightKey)

            moveVertexDBV[dataKey] = dfGood.Histo1D(("moveVertex_dBV", f"dBV of matched vertex for {dataKey}", 30, 0, 2), "moveVertex_dBV", weightKey)
            moveVertexDBV3D[dataKey] = dfGood.Histo1D(("moveVertex_dBV3D", f"dBV  3D of matched vertex for {dataKey}", 30, 0, 5), "moveVertex_dBV3D", weightKey)
            moveVertexDPVV[dataKey] = dfGood.Histo1D(("moveVertex_dPVV", f"dPVV of matched vertex for {dataKey}", 30, 0, 2), "moveVertex_dPVV", weightKey)
            moveVertexDPVV3D[dataKey] = dfGood.Histo1D(("moveVertex_dPVV3D", f"dPVV  3D of matched vertex for {dataKey}", 30, 0, 5), "moveVertex_dPVV3D", weightKey)

            moveVertex_sumPt[dataKey] = dfGood.Histo1D(("moveVertex_sumPt", f"pT sum for {dataKey}", 30, 0, 1500), "LLP_PtSum", weightKey)
            moveVertex_netPt[dataKey] = dfGood.Histo1D(("moveVertex_netPt", f"Net pT for {dataKey}", 30, 0, 1500), "LLP_netPt", weightKey)
            moveVertex_netP[dataKey] = dfGood.Histo1D(("moveVertex_netP", f"Net P for {dataKey}", 30, 0, 1500), "LLP_netP", weightKey)
            moveVertex_deltaR[dataKey] = dfGood.Histo1D(("moveVertex_deltaR", f"Vertex delta R for {dataKey}", 30, 0, 6), "LLP_dR", weightKey)

            nPV[dataKey] = dfGood.Histo1D(("nPV", f"Number of PVs for {dataKey}", 50, 0, 50), "nPV", weightKey)

            #Efficiency denominators
            #Jets Eta
            vertexEffJet1Eta_den[dataKey] = dfGood.Histo1D((f"vertexJet1Eta_den_{dataKey}", "Jet 1 eta", 25, -2.5, 2.5), "Jet1_eta", weightKey)
            vertexEffJet2Eta_den[dataKey] = dfGood.Histo1D((f"vertexJet2Eta_den_{dataKey}", "Jet 2 eta", 25, -2.5, 2.5), "Jet2_eta", weightKey)

            #Reweighting Variables
            if(signal=="original"):
                vertexEffSumPt_den[dataKey] = dfGood.Histo1D(("vertexSumPt_den", "pT sum of moved tracks", 25, 0, 1000), "LLP_PtSum", weightKey)
                vertexEffNetPt_den[dataKey] = dfGood.Histo1D(("vertexNetPt_den", "Net pT of moved tracks", 25, 0, 1000), "LLP_netPt", weightKey)
                vertexEffNetP_den[dataKey] = dfGood.Histo1D(("vertexNetP_den", "Net 3D momentum of moved tracks", 25, 0, 1000), "LLP_netP", weightKey)
                vertexEffDeltaR_den[dataKey] = dfGood.Histo1D(("vertexDeltaR_den", "delta R of moved tracks", 25, 0, 6), "LLP_dR", weightKey)
                vertexEffdPVV3D_den[dataKey] = dfGood.Histo1D(("vertexdPVV3D_den", "dPVV 3D of move vertex", 25, 0, 5), "moveVertex_dPVV3D", weightKey)

            #Number of tracks
            vertexEffSurvTracks_den[dataKey] = dfGood.Histo1D((f"vertexSurvTracks_den_{dataKey}", "number of survived moved tracks", 40, 0, 40), "nSurvivedTracks", weightKey)
            vertexEffCloseBGTracks_den[dataKey] = dfGood.Histo1D((f"vertexCloseTracks_den_{dataKey}", "number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks", weightKey)
            vertexEffTotalCloseTracks_den[dataKey] = dfGood.Histo1D((f"vertexTotalTracks_den_{dataKey}", "total of close tracks", 40, 0, 40),  "nCloseTotalTracks", weightKey)

            vertexEffSurvSeedTracks_den[dataKey] = dfGood.Histo1D((f"vertexSurvTracks_den_{dataKey}", "number of survived moved tracks", 40, 0, 40), "nSurvivedTracks_IPsig", weightKey)
            vertexEffCloseBGSeedTracks_den[dataKey] = dfGood.Histo1D((f"vertexCloseTracks_den_{dataKey}", "number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks_IPsig", weightKey)
            vertexEffTotalCloseSeedTracks_den[dataKey] = dfGood.Histo1D((f"vertexTotalTracks_den_{dataKey}", "total of close tracks", 40, 0, 40),  "nCloseTotalTracks_IPsig", weightKey)
            
            #Final efficiency
            vertexEffdBV_den[dataKey] = dfGood.Histo1D((f"vertexEffdBV_den_{dataKey}", f"Move Vertex 2D displacement for {dataKey}", len(dBV_edges)-1, dBV_edges), "dBV_eff", weightKey)
            vertexEffdPVV_den[dataKey] = dfGood.Histo1D((f"vertexdPVV_den_{dataKey}", "dPVV of move vertex", len(dBV_edges)-1, dBV_edges), "dPVV_eff", weightKey)

            print("Booking numerator plots for TEffs...")
            for ntk in [3, 4, 5, 6, 7, 8, 9]:
                if (ntk == 9):
                    dfFiltered = dfGood.Filter(f"vertex_pass && (matchedVertex_nTracks >= {str(ntk)})")
                else:
                    dfFiltered = dfGood.Filter(f"vertex_pass && (matchedVertex_nTracks == {str(ntk)})")

                vertexEffJet1Eta_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexJet1Eta_num", "Jet 1 eta", 25, -2.5, 2.5), "Jet1_eta", weightKey)
                vertexEffJet2Eta_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexJet2Eta_num", "Jet 2 eta", 25, -2.5, 2.5), "Jet2_eta", weightKey)

                if(signal=="original"):
                    vertexEffSumPt_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexSumPt_num", "pT sum of moved tracks", 25, 0, 1000), "LLP_PtSum", weightKey)
                    vertexEffNetPt_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexNetPt_num", "Net pT of moved tracks", 25, 0, 1000), "LLP_netPt", weightKey)
                    vertexEffNetP_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexNetP_num", "Net 3D momentum of moved tracks", 25, 0, 1000), "LLP_netP", weightKey)
                    vertexEffDeltaR_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexDeltaR_num", "delta R of moved tracks", 25, 0, 6), "LLP_dR", weightKey)
                    vertexEffdPVV3D_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexdPVV3D_num", "dPVV 3D of move vertex", 25, 0, 5), "moveVertex_dPVV3D", weightKey)

                vertexEffSurvTracks_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexSurvTracks_num", "Efficiency vs number of survived moved tracks", 40, 0, 40), "nSurvivedTracks", weightKey)
                vertexEffCloseBGTracks_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexCloseTracks_num", "Efficiency vs number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks", weightKey)
                vertexEffTotalCloseTracks_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexTotalTracks_num", "Efficiency vs total of close tracks", 40, 0, 40),  "nCloseTotalTracks", weightKey)

                vertexEffSurvSeedTracks_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexSurvTracks_num", "Efficiency vs number of survived moved tracks", 40, 0, 40), "nSurvivedTracks_IPsig", weightKey)
                vertexEffCloseBGSeedTracks_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexCloseTracks_num", "Efficiency vs number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks_IPsig", weightKey)
                vertexEffTotalCloseSeedTracks_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(("vertexTotalTracks_num", "Efficiency vs total of close tracks", 40, 0, 40),  "nCloseTotalTracks_IPsig", weightKey)

                vertexEffdBV_num[f'{dataKey}_{str(ntk)}tks']  = dfFiltered.Histo1D(model("vertexEffR_num", f"Vertex Reconstruction Efficiency for {signal}", dBV_edges), "dBV_eff", weightKey)
                vertexEffdPVV_num[f'{dataKey}_{str(ntk)}tks'] = dfFiltered.Histo1D(model("vertexdPVV_num", "dPVV of move vertex", dBV_edges), "dPVV_eff", weightKey)
    
    #Calculate the TEfficiency
    print("Making efficiency histograms (also triggers lazy actions)...")
    for era in eras:
        for signal in signals:
            if (signal == "original"):
                dataKey = era
            else:
                dataKey = f'{era}_{signal}'

            for ntk in [3, 4, 5, 6, 7, 8, 9]:

                vertexEffJet1Eta[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffJet1Eta_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffJet1Eta_den[dataKey].GetPtr())
                vertexEffJet2Eta[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffJet2Eta_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffJet2Eta_den[dataKey].GetPtr())

                if(signal == "original"):
                    vertexEffSumPt[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffSumPt_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffSumPt_den[dataKey].GetPtr())
                    vertexEffNetPt[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffNetPt_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffNetPt_den[dataKey].GetPtr())
                    vertexEffNetP[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffNetP_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffNetP_den[dataKey].GetPtr())
                    vertexEffDeltaR[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffDeltaR_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffDeltaR_den[dataKey].GetPtr())
                    vertexEffdPVV3D[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffdPVV3D_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffdPVV3D_den[dataKey].GetPtr())

                vertexEffSurvTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffSurvTracks_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffSurvTracks_den[dataKey].GetPtr())
                vertexEffCloseBGTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffCloseBGTracks_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffCloseBGTracks_den[dataKey].GetPtr())
                vertexEffTotalCloseTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffTotalCloseTracks_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffTotalCloseTracks_den[dataKey].GetPtr())

                vertexEffSurvSeedTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffSurvSeedTracks_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffSurvSeedTracks_den[dataKey].GetPtr())
                vertexEffCloseBGSeedTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffCloseBGSeedTracks_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffCloseBGSeedTracks_den[dataKey].GetPtr())
                vertexEffTotalCloseSeedTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffTotalCloseSeedTracks_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffTotalCloseSeedTracks_den[dataKey].GetPtr())

                vertexEffdBV[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffdBV_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffdBV_den[dataKey].GetPtr())
                vertexEffdPVV[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffdPVV_num[f'{dataKey}_{str(ntk)}tks'].GetPtr(), vertexEffdPVV_den[dataKey].GetPtr())


def loadHistogramsMC(dfs, backgroundDict, eras=["2024"], signals=["Stop_800_1"], debugPlots=False, doLifetimeReweighting=True):
    #Create the empty histograms
    print("Creating MC histograms...")
    for era in eras:
        for signal in signals:
            if (signal == "original"):
                dataKey = era
            else:
                dataKey = f'{era}_{signal}'

            if(debugPlots):
                #Track-level plots
                originalTrack_pt[dataKey] = ROOT.TH1D(f"origTrack_pt_{dataKey}", "pT of original tracks", 100, 0, 100)
                originalTrack_eta[dataKey] = ROOT.TH1D(f"origTrack_eta_{dataKey}", "eta of original tracks", 100, -2.5, 2.5)
                originalTrack_phi[dataKey] = ROOT.TH1D(f"origTrack_phi_{dataKey}", "phi of original tracks", 100, -3.5, 3.5)
                originalTrack_dxy[dataKey] = ROOT.TH1D(f"origTrack_dxy_{dataKey}", "dxy of original tracks", 100, -2, 2)

                newTrack_pt[dataKey] = ROOT.TH1D(f"newTrack_pt_{dataKey}", "pT of new tracks", 100, 0, 100) 
                newTrack_eta[dataKey] = ROOT.TH1D(f"newTrack_eta_{dataKey}", "eta of new tracks", 100, -2.5, 2.5)
                newTrack_phi[dataKey] = ROOT.TH1D(f"newTrack_phi_{dataKey}", "phi of new tracks", 100, -3.5, 3.5)
                newTrack_dxy[dataKey] = ROOT.TH1D(f"newTrack_dxy_{dataKey}", "dxy of new tracks", 100, -2, 2)

                movedTrack_pt[dataKey] = ROOT.TH1D(f"movedTrack_pt_{dataKey}", "pT of moved tracks", 100, 0, 100)
                movedTrack_eta[dataKey] = ROOT.TH1D(f"movedTrack_eta_{dataKey}", "eta of moved tracks", 100, -2.5, 2.5)
                movedTrack_phi[dataKey] = ROOT.TH1D(f"movedTrack_phi_{dataKey}", "phi of moved tracks", 100, -3.5, 3.5)
                movedTrack_dxy[dataKey] = ROOT.TH1D(f"movedTrack_dxy_{dataKey}", "dxy of moved tracks", 100, -2, 2)

                pvXY[dataKey] = ROOT.TH2D(f"pvXY_{dataKey}", f"Leading PV Position for {dataKey}", 50, -5, 5, 50, -5, 5)
                pvZ[dataKey] = ROOT.TH1D(f"primaryVertex_z_{dataKey}", f"Z of Leading PV for {dataKey}", 100, -12, 12)

            #Track plots
            nMovedTracks[dataKey] = ROOT.TH1D(f"nMovedTracks_{dataKey}", "Number of moved tracks", 40, 0, 40)
            nSurvivedTracks[dataKey] = ROOT.TH1D(f"nSurvivedTracks_{dataKey}", "Number of survived tracks", 40, 0, 40)
            nCloseBGTracks[dataKey] = ROOT.TH1D(f"nCloseBGTracks_{dataKey}", "Number of close unmoved tracks", 40, 0, 40)
            nCloseTotalTracks[dataKey] = ROOT.TH1D(f"nTotalTracks_{dataKey}", "Total of close tracks", 40, 0, 40)

            nSurvivedTracksVsdPVV[dataKey] = ROOT.TProfile(f"survivedTracksVsDPVV_{dataKey}", "nSurvivedTrakcs vs dPVV", 30, 0, 2)
            nCloseBGTracksVsdPVV[dataKey] = ROOT.TProfile(f"closeTracksVsDPVV_{dataKey}", "nCloseTrakcs vs dPVV", 30, 0, 2)
            nCloseTotalTracksVsdPVV[dataKey] = ROOT.TProfile(f"totalTracksVsDPVV_{dataKey}", "totalTrakcs vs dPVV", 30, 0, 2)

            nSurvivedSeedTracks[dataKey] = ROOT.TH1D(f"nSurvivedTracks_{dataKey}_IPsig", "Number of survived tracks", 40, 0, 40)
            nCloseBGSeedTracks[dataKey] = ROOT.TH1D(f"nCloseBGTracks_{dataKey}_IPsig", "Number of close unmoved tracks", 40, 0, 40)
            nCloseTotalSeedTracks[dataKey] = ROOT.TH1D(f"nTotalTracks_{dataKey}_IPsig", "Total of close tracks", 40, 0, 40)

            nSurvivedSeedTracksVsdPVV[dataKey] = ROOT.TProfile(f"survivedTracksVsDPVV_{dataKey}_IPsig", "nSurvivedTrakcs vs dPVV", 30, 0, 2)
            nCloseBGSeedTracksVsdPVV[dataKey] = ROOT.TProfile(f"closeTracksVsDPVV_{dataKey}_IPsig", "nCloseTrakcs vs dPVV", 30, 0, 2)
            nCloseTotalSeedTracksVsdPVV[dataKey] = ROOT.TProfile(f"totalTracksVsDPVV_{dataKey}_IPsig", "totalTrakcs vs dPVV", 30, 0, 2)

            #Vertex-level plots
            matchVertexDBV[dataKey] = ROOT.TH1D(f"matchedVertex_dBV_{dataKey}", f"dBV of matched vertex for {dataKey}", 30, 0, 2)

            moveVertexDBV[dataKey] = ROOT.TH1D(f"moveVertex_dBV_{dataKey}", f"dBV of matched vertex for {dataKey}", 30, 0, 2)
            moveVertexDBV3D[dataKey] = ROOT.TH1D(f"moveVertex_dBV3D_{dataKey}", f"dBV  3D of matched vertex for {dataKey}", 30, 0, 5)
            moveVertex_sumPt[dataKey] = ROOT.TH1D(f"moveVertex_sumPt_{dataKey}", f"pT sum for {dataKey}", 30, 0, 1500)
            moveVertex_netPt[dataKey] = ROOT.TH1D(f"moveVertex_netPt_{dataKey}", f"Net pT for {dataKey}", 30, 0, 1500)
            moveVertex_netP[dataKey] = ROOT.TH1D(f"moveVertex_netP_{dataKey}", f"Net P for {dataKey}", 30, 0, 1500)
            moveVertex_deltaR[dataKey] = ROOT.TH1D(f"moveVertex_deltaR_{dataKey}", f"Vertex delta R for {dataKey}", 30, 0, 6)

            moveVertexDPVV[dataKey] = ROOT.TH1D(f"moveVertex_dPVV_{dataKey}", f"dPVV of matched vertex for {dataKey}", 30, 0, 2)
            moveVertexDPVV3D[dataKey] = ROOT.TH1D(f"moveVertex_dPVV3D_{dataKey}", f"dPVV  3D of matched vertex for {dataKey}", 30, 0, 5)

            nPV[dataKey] = ROOT.TH1D(f"nPV_{dataKey}", f"Number of PVs for {dataKey}", 50, 0, 50)

            #Efficiency denominators
            #Jet eta
            vertexEffJet1Eta_den[dataKey] = ROOT.TH1D("vertexJet1Eta_den", "Jet 1 eta", 25, -2.5, 2.5)
            vertexEffJet2Eta_den[dataKey] = ROOT.TH1D("vertexJet2Eta_den", "Jet 2 eta", 25, -2.5, 2.5)

            #Reweighting Variables
            if(signal=="original"):
                vertexEffSumPt_den[dataKey] = ROOT.TH1D("vertexSumPt_den", "pT sum of moved tracks", 25, 0, 1000)
                vertexEffNetPt_den[dataKey] = ROOT.TH1D("vertexNetPt_den", "Net pT of moved tracks", 25, 0, 1000)
                vertexEffNetP_den[dataKey] = ROOT.TH1D("vertexNetP_den", "Net 3D momentum of moved tracks", 25, 0, 1000)
                vertexEffDeltaR_den[dataKey] = ROOT.TH1D("vertexDeltaR_den", "delta R of moved tracks", 25, 0, 6)
                vertexEffdPVV3D_den[dataKey] = ROOT.TH1D("vertexdPVV3D_den", "dPVV 3D of move vertex", 25, 0, 5)

            #Number of tracks
            vertexEffSurvTracks_den[dataKey] = ROOT.TH1D(f"vertexSurvTracks_den_{dataKey}", "number of survived moved tracks", 40, 0, 40)
            vertexEffCloseBGTracks_den[dataKey] = ROOT.TH1D(f"vertexCloseTracks_den_{dataKey}", "number of close unmoved tracks", 40, 0, 40)
            vertexEffTotalCloseTracks_den[dataKey] = ROOT.TH1D(f"vertexTotalTracks_den_{dataKey}", "total of close tracks", 40, 0, 40)

            vertexEffSurvSeedTracks_den[dataKey] = ROOT.TH1D(f"vertexSurvTracks_den_IPsig_{dataKey}", "number of survived moved tracks", 40, 0, 40)
            vertexEffCloseBGSeedTracks_den[dataKey] = ROOT.TH1D(f"vertexCloseTracks_den_IPsig_{dataKey}", "number of close unmoved tracks", 40, 0, 40)
            vertexEffTotalCloseSeedTracks_den[dataKey] = ROOT.TH1D(f"vertexTotalTracks_den_IPsig_{dataKey}", "total of close tracks", 40, 0, 40)

            #Total Efficiency
            vertexEffdBV_den[dataKey]  = ROOT.TH1D(f"moveVertexdBV_den_{dataKey}", f"dBV of move vertex ({dataKey})", len(dBV_edges)-1, dBV_edges)
            vertexEffdPVV_den[dataKey] = ROOT.TH1D(f"moveVertexdPVV_den_{dataKey}", f"dPVV of move vertex ({dataKey})", len(dBV_edges)-1, dBV_edges)

            #Efficiency numerators
            for ntk in [3, 4, 5, 6, 7, 8, 9]:
                vertexEffJet1Eta_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexJet1Eta_num_{dataKey}_{str(ntk)}tks", "Jet 1 eta", 25, -2.5, 2.5)
                vertexEffJet2Eta_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexJet2Eta_num_{dataKey}_{str(ntk)}tks", "Jet 2 eta", 25, -2.5, 2.5)
                #Reweighting Variables
                if(signal=="original"):
                    vertexEffSumPt_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexSumPt_num_{dataKey}_{str(ntk)}tks", "pT sum of moved tracks", 25, 0, 1000)
                    vertexEffNetPt_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexNetPt_num_{dataKey}_{str(ntk)}tks", "Net pT of moved tracks", 25, 0, 1000)
                    vertexEffNetP_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexNetP_num_{dataKey}_{str(ntk)}tks", "Net 3D momentum of moved tracks", 25, 0, 1000)
                    vertexEffDeltaR_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexDeltaR_num_{dataKey}_{str(ntk)}tks", "delta R of moved tracks", 25, 0, 6)
                    vertexEffdPVV3D_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexdPVV3D_num_{dataKey}_{str(ntk)}tks", "dPVV 3D of move vertex", 25, 0, 5)
                #Number of tracks
                vertexEffSurvTracks_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexSurvTracks_num_{dataKey}_{str(ntk)}tks", "number of survived moved tracks", 40, 0, 40)
                vertexEffCloseBGTracks_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexCloseTracks_num_{dataKey}_{str(ntk)}tks", "number of close unmoved tracks", 40, 0, 40)
                vertexEffTotalCloseTracks_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexTotalTracks_num_{dataKey}_{str(ntk)}tks", "total of close tracks", 40, 0, 40)

                vertexEffSurvSeedTracks_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexSurvTracks_num_{dataKey}_{str(ntk)}tks_IPsig", "number of survived moved tracks", 40, 0, 40)
                vertexEffCloseBGSeedTracks_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexCloseTracks_num_{dataKey}_{str(ntk)}tks_IPsig", "number of close unmoved tracks", 40, 0, 40)
                vertexEffTotalCloseSeedTracks_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexTotalTracks_num_{dataKey}_{str(ntk)}tks_IPsig", "total of close tracks", 40, 0, 40)
                
                #Total efficiency
                vertexEffdBV_num[f'{dataKey}_{str(ntk)}tks']  = ROOT.TH1D(f"vertexEffdBV_num_{dataKey}_{str(ntk)}tks", f"Vertex Reconstruction Efficiency for {signal}", len(dBV_edges)-1, dBV_edges)
                vertexEffdPVV_num[f'{dataKey}_{str(ntk)}tks'] = ROOT.TH1D(f"vertexEffdPVV_num_{dataKey}_{str(ntk)}tks", f"Vertex Reconstruction Efficiency for {signal}", len(dBV_edges)-1, dBV_edges)

    #Get gen weight sum
    sum_gen_weights = {}
    for bg in backgroundDict.keys():
        print(f"Processing background {bg}...")
        f = ROOT.TFile.Open(backgroundDict[bg])
        h = f.Get("triggerFilter/genWeightsSkim")
        ibin = h.GetXaxis().FindBin("None")
        sum_gen_weights[bg] = h.GetBinContent(ibin)
        f.Close()
        print(f"Gen weight sum: {sum_gen_weights[bg]}")

    for era in eras:
        for signal in signals:
            if (signal == "original"):
                dataKey = era
                weightKey = "weight_noTrigger"
            else:
                dataKey = f'{era}_{signal}'
                weightKey = f"finalWeight_{signal}"


            print(f"Running for {dataKey}...")

            for bg in dfs.keys():
                print(f"Processing background {bg}...")
                df = dfs[bg]
            
                if (signal != "original"):
                    df = df.Define(f"tmWeight_{signal}", f'getTMWeight("{era}_{signal}", netP_clamped, dR_clamped)')
                    if(doLifetimeReweighting):
                        print("Doing lifetime reweighting...")
                        df = df.Define(f"tmLifetimeWeight_{signal}", f'getTMWeight("lifetime_{era}_{signal}", dPVV_clamped, dPVV3D_clamped)')
                        df = df.Define(f"finalWeight_{signal}", f"weight_noTrigger * tmWeight_{signal} * tmLifetimeWeight_{signal}")
                    else:
                        df = df.Define(f"finalWeight_{signal}", f"weight_noTrigger * tmWeight_{signal}")

                df = df.Define(f"{weightKey}_normalized", f"{weightKey}/{sum_gen_weights[bg]}")
                dfGood = df.Define("badWeight", f"!std::isfinite({weightKey}_normalized) || {weightKey}_normalized < 0")
                dfGood = dfGood.Filter("!badWeight")


                print("Booking histograms...")
                if(debugPlots):
                    #Track-level plots
                    originalTrack_pt_tmp = dfGood.Histo1D((f"origTrack_pt_{bg}", "pT of original tracks", 100, 0, 100), "originalTracks_pt", f"{weightKey}_normalized")
                    originalTrack_eta_tmp = dfGood.Histo1D((f"origTrack_eta_{bg}", "eta of original tracks", 100, -2.5, 2.5), "originalTracks_eta", f"{weightKey}_normalized")
                    originalTrack_phi_tmp = dfGood.Histo1D((f"origTrack_phi_{bg}", "phi of original tracks", 100, -3.5, 3.5), "originalTracks_phi", f"{weightKey}_normalized")
                    originalTrack_dxy_tmp = dfGood.Histo1D((f"origTrack_dxy_{bg}", "dxy of original tracks", 100, -2, 2), "originalTracks_dxy", f"{weightKey}_normalized")

                    newTrack_pt_tmp = dfGood.Histo1D((f"newTrack_pt_{bg}", "pT of new tracks", 100, 0, 100), "tracks_pt", f"{weightKey}_normalized")
                    newTrack_eta_tmp = dfGood.Histo1D((f"newTrack_eta_{bg}", "eta of new tracks", 100, -2.5, 2.5), "tracks_eta", f"{weightKey}_normalized")
                    newTrack_phi_tmp = dfGood.Histo1D((f"newTrack_phi_{bg}", "phi of new tracks", 100, -3.5, 3.5), "tracks_phi", f"{weightKey}_normalized")
                    newTrack_dxy_tmp = dfGood.Histo1D((f"newTrack_dxy_{bg}", "dxy of new tracks", 100, -2, 2), "tracks_dxy", f"{weightKey}_normalized")
                    
                    movedTrack_pt_tmp = dfGood.Histo1D((f"movedTrack_pt_{bg}", "pT of moved tracks", 100, 0, 100), "movedTracks_pt", f"{weightKey}_normalized")
                    movedTrack_eta_tmp = dfGood.Histo1D((f"movedTrack_eta_{bg}", "eta of moved tracks", 100, -2.5, 2.5), "movedTracks_eta", f"{weightKey}_normalized")
                    movedTrack_phi_tmp = dfGood.Histo1D((f"movedTrack_phi_{bg}", "phi of moved tracks", 100, -3.5, 3.5), "movedTracks_phi", f"{weightKey}_normalized")
                    movedTrack_dxy_tmp = dfGood.Histo1D((f"movedTrack_dxy_{bg}", "dxy of moved tracks", 100, -2, 2), "movedTracks_dxy", f"{weightKey}_normalized")
                    
                    pvXY_tmp = dfGood.Histo2D((f"pvXY_{bg}", f"Leading PV Position for {dataKey}", 50, -5, 5, 50, -5, 5), "primaryVertex_x", "primaryVertex_y", f"{weightKey}_normalized")
                    pvZ_tmp = dfGood.Histo1D((f"primaryVertex_z_{bg}", f"Z of Leading PV for {dataKey}", 100, -12, 12), "primaryVertex_z", f"{weightKey}_normalized")

                #Track plots
                nMovedTracks_tmp = dfGood.Histo1D((f"nMovedTracks_{bg}", "Number of moved tracks", 40, 0, 40), "nMovedTracks", f"{weightKey}_normalized")
                nSurvivedTracks_tmp = dfGood.Histo1D((f"nSurvivedTracks_{bg}", "Number of survived tracks", 40, 0, 40), "nSurvivedTracks", f"{weightKey}_normalized")
                nCloseBGTracks_tmp = dfGood.Histo1D((f"nCloseBGTracks_{bg}", "Number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks", f"{weightKey}_normalized")
                nCloseTotalTracks_tmp = dfGood.Histo1D((f"nTotalTracks_{bg}", "Total of close tracks", 40, 0, 40), "nCloseTotalTracks", f"{weightKey}_normalized")

                nSurvivedTracksVsdPVV_tmp = dfGood.Profile1D((f"survivedTracksVsDPVV_{bg}", "nSurvivedTrakcs vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nSurvivedTracks", f"{weightKey}_normalized")
                nCloseBGTracksVsdPVV_tmp = dfGood.Profile1D((f"closeTracksVsDPVV_{bg}", "nCloseTrakcs vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nCloseBGTracks", f"{weightKey}_normalized")
                nCloseTotalTracksVsdPVV_tmp = dfGood.Profile1D((f"nCloseTotalTracksVsdPVV_{bg}", "mCloseTotalTracks vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nCloseTotalTracks", f"{weightKey}_normalized")

                nSurvivedSeedTracks_tmp = dfGood.Histo1D((f"nSurvivedTracks_{bg}_IPsig", "Number of survived tracks", 40, 0, 40), "nSurvivedTracks_IPsig", f"{weightKey}_normalized")
                nCloseBGSeedTracks_tmp = dfGood.Histo1D((f"nCloseBGTracks_{bg}_IPsig", "Number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks_IPsig", f"{weightKey}_normalized")
                nCloseTotalSeedTracks_tmp = dfGood.Histo1D((f"nTotalTracks_{bg}_IPsig", "Total of close tracks", 40, 0, 40), "nCloseTotalTracks_IPsig", f"{weightKey}_normalized")

                nSurvivedSeedTracksVsdPVV_tmp = dfGood.Profile1D((f"survivedTracksVsDPVV_{bg}_IPsig", "nSurvivedTrakcs vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nSurvivedTracks_IPsig", f"{weightKey}_normalized")
                nCloseBGSeedTracksVsdPVV_tmp = dfGood.Profile1D((f"closeTracksVsDPVV_{bg}_IPsig", "nCloseTrakcs vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nCloseBGTracks_IPsig", f"{weightKey}_normalized")
                nCloseTotalSeedTracksVsdPVV_tmp = dfGood.Profile1D((f"nCloseTotalSeedTracksVsdPVV_{bg}_IPsig", "nCloseTotalTracks vs dPVV", 30, 0, 2), "moveVertex_dPVV", "nCloseTotalTracks_IPsig", f"{weightKey}_normalized")

                #Vertex-level plots
                matchVertexDBV_tmp = dfGood.Histo1D((f"matchedVertex_dBV_{bg}", f"dBV of matched vertex for {dataKey}", 30, 0, 2), "matchedVertex_dBV", f"{weightKey}_normalized")
                moveVertexDBV_tmp = dfGood.Histo1D((f"matchedVertex_dBV_{bg}", f"dBV of matched vertex for {dataKey}", 30, 0, 2), "moveVertex_dBV", f"{weightKey}_normalized")
                moveVertexDBV3D_tmp = dfGood.Histo1D((f"matchedVertex_dBV3D_{bg}", f"dBV  3D of matched vertex for {dataKey}", 30, 0, 5), "moveVertex_dBV3D", f"{weightKey}_normalized")
                
                moveVertex_sumPt_tmp = dfGood.Histo1D((f"moveVertex_sumPt_{bg}", f"pT sum for {dataKey}", 30, 0, 1500), "LLP_PtSum", f"{weightKey}_normalized")
                moveVertex_netPt_tmp = dfGood.Histo1D((f"moveVertex_netPt_{bg}", f"Net pT for {dataKey}", 30, 0, 1500), "LLP_netPt", f"{weightKey}_normalized")
                moveVertex_netP_tmp = dfGood.Histo1D((f"moveVertex_netP_{bg}", f"Net P for {dataKey}", 30, 0, 1500), "LLP_netP", f"{weightKey}_normalized")
                moveVertex_deltaR_tmp = dfGood.Histo1D((f"moveVertex_deltaR_{bg}", f"Vertex delta R for {dataKey}", 30, 0, 6), "LLP_dR", f"{weightKey}_normalized")
                moveVertexDPVV_tmp = dfGood.Histo1D((f"moveVertex_dPVV_{bg}", f"dPVV of matched vertex for {dataKey}", 30, 0, 2), "moveVertex_dPVV", f"{weightKey}_normalized")
                moveVertexDPVV3D_tmp = dfGood.Histo1D((f"moveVertex_dPVV3D_{bg}", f"dPVV  3D of matched vertex for {dataKey}", 30, 0, 5), "moveVertex_dPVV3D", f"{weightKey}_normalized")

                nPV_tmp = dfGood.Histo1D((f"nPV_{bg}", f"Number of PVs for {dataKey}", 50, 0, 50), "nPV", f"{weightKey}_normalized")

                #Efficiency denominators
                #Jet eta
                vertexEffJet1Eta_den_tmp = dfGood.Histo1D(("vertexJet1_eta_den", "Jet 1 eta", 25, -2.5, 2.5), "Jet1_eta", f"{weightKey}_normalized")
                vertexEffJet2Eta_den_tmp = dfGood.Histo1D(("vertexJet2_eta_den", "Jet 2 eta", 25, -2.5, 2.5), "Jet2_eta", f"{weightKey}_normalized")
                #Reweighting Variables
                if(signal=="original"):
                    vertexEffSumPt_den_tmp = dfGood.Histo1D(("vertexSumPt_den", "pT sum of moved tracks", 25, 0, 1000), "LLP_PtSum", f"{weightKey}_normalized")
                    vertexEffNetPt_den_tmp = dfGood.Histo1D(("vertexNetPt_den", "Net pT of moved tracks", 25, 0, 1000), "LLP_netPt", f"{weightKey}_normalized")
                    vertexEffNetP_den_tmp = dfGood.Histo1D(("vertexNetP_den", "Net 3D momentum of moved tracks", 25, 0, 1000), "LLP_netP", f"{weightKey}_normalized")
                    vertexEffDeltaR_den_tmp = dfGood.Histo1D(("vertexDeltaR_den", "delta R of moved tracks", 25, 0, 6), "LLP_dR", f"{weightKey}_normalized")
                    vertexEffdPVV3D_den_tmp = dfGood.Histo1D(("vertexdPVV3D_den", "dPVV 3D of move vertex", 25, 0, 5), "moveVertex_dPVV3D", f"{weightKey}_normalized")

                #Number of tracks
                vertexEffSurvTracks_den_tmp = dfGood.Histo1D(("vertexSurvTracks_den", "number of survived moved tracks", 40, 0, 40), "nSurvivedTracks", f"{weightKey}_normalized")
                vertexEffCloseBGTracks_den_tmp = dfGood.Histo1D(("vertexCloseTracks_den", "number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks", f"{weightKey}_normalized")
                vertexEffTotalCloseTracks_den_tmp = dfGood.Histo1D(("vertexTotalTracks_den", "total of close tracks", 40, 0, 40),  "nCloseTotalTracks", f"{weightKey}_normalized")
                
                vertexEffSurvSeedTracks_den_tmp = dfGood.Histo1D(("vertexSurvTracks_den_IPsig", "number of survived moved tracks", 40, 0, 40), "nSurvivedTracks_IPsig", f"{weightKey}_normalized")
                vertexEffCloseBGSeedTracks_den_tmp = dfGood.Histo1D(("vertexCloseTracks_den_IPsig", "number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks_IPsig", f"{weightKey}_normalized")
                vertexEffTotalCloseSeedTracks_den_tmp = dfGood.Histo1D(("vertexTotalTracks_den_IPsig", "total of close tracks", 40, 0, 40),  "nCloseTotalTracks_IPsig", f"{weightKey}_normalized")

                #Final efficiency
                vertexEffdBV_den_tmp  = dfGood.Histo1D(model(f"moveVertexdBV_{bg}", f"dBV of move vertex", dBV_edges), "dBV_eff", f"{weightKey}_normalized")
                vertexEffdPVV_den_tmp = dfGood.Histo1D(model(f"moveVertexdPVV_{bg}", "dPVV of move vertex", dBV_edges), "dPVV_eff", f"{weightKey}_normalized")

                #Numerators
                if(signal=="original"):
                    vertexEffSumPt_num_tmp = {}
                    vertexEffNetPt_num_tmp = {}
                    vertexEffNetP_num_tmp = {}
                    vertexEffDeltaR_num_tmp = {}
                    vertexEffdPVV3D_num_tmp = {}

                vertexEffJet1Eta_num_tmp = {}
                vertexEffJet2Eta_num_tmp = {}

                vertexEffSurvTracks_num_tmp = {}
                vertexEffCloseBGTracks_num_tmp = {}
                vertexEffTotalCloseTracks_num_tmp = {}

                vertexEffSurvSeedTracks_num_tmp = {}
                vertexEffCloseBGSeedTracks_num_tmp = {}
                vertexEffTotalCloseSeedTracks_num_tmp = {}

                vertexEffdBV_num_tmp = {}
                vertexEffdPVV_num_tmp = {}

                for ntk in [3, 4, 5, 6, 7, 8, 9]:
                    if (ntk == 9):
                        dfFiltered = dfGood.Filter(f"vertex_pass && (matchedVertex_nTracks >= {str(ntk)})")
                    else:
                        dfFiltered = dfGood.Filter(f"vertex_pass && (matchedVertex_nTracks == {str(ntk)})")

                    vertexEffJet1Eta_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexJet1_eta_num_{bg}", "Jet 1 eta", 25, -2.5, 2.5), "Jet1_eta", f"{weightKey}_normalized")
                    vertexEffJet2Eta_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexJet2_eta_num_{bg}", "Jet 2 eta", 25, -2.5, 2.5), "Jet2_eta", f"{weightKey}_normalized")

                    if(signal=="original"):
                        vertexEffSumPt_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexSumPt_num_{bg}", "pT sum of moved tracks", 25, 0, 1000), "LLP_PtSum", f"{weightKey}_normalized")
                        vertexEffNetPt_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexNetPt_num_{bg}", "Net pT of moved tracks", 25, 0, 1000), "LLP_netPt", f"{weightKey}_normalized")
                        vertexEffNetP_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexNetP_num_{bg}", "Net 3D momentum of moved tracks", 25, 0, 1000), "LLP_netP", f"{weightKey}_normalized")
                        vertexEffDeltaR_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexDeltaR_num_{bg}", "delta R of moved tracks", 25, 0, 6), "LLP_dR", f"{weightKey}_normalized")
                        vertexEffdPVV3D_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexdPVV3D_num_{bg}", "dPVV 3D of move vertex", 25, 0, 5), "moveVertex_dPVV3D", f"{weightKey}_normalized")

                    vertexEffSurvTracks_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexSurvTracks_num_{bg}", "Efficiency vs number of survived moved tracks", 40, 0, 40), "nSurvivedTracks", f"{weightKey}_normalized")
                    vertexEffCloseBGTracks_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexCloseTracks_num_{bg}", "Efficiency vs number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks", f"{weightKey}_normalized")
                    vertexEffTotalCloseTracks_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexTotalTracks_num_{bg}", "Efficiency vs total of close tracks", 40, 0, 40),  "nCloseTotalTracks", f"{weightKey}_normalized")

                    vertexEffSurvSeedTracks_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexSurvTracks_num_{bg}_IPsig", "Efficiency vs number of survived moved tracks", 40, 0, 40), "nSurvivedTracks_IPsig", f"{weightKey}_normalized")
                    vertexEffCloseBGSeedTracks_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexCloseTracks_num_{bg}_IPsig", "Efficiency vs number of close unmoved tracks", 40, 0, 40), "nCloseBGTracks_IPsig", f"{weightKey}_normalized")
                    vertexEffTotalCloseSeedTracks_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D((f"vertexTotalTracks_num_{bg}_IPsig", "Efficiency vs total of close tracks", 40, 0, 40),  "nCloseTotalTracks_IPsig", f"{weightKey}_normalized")

                    vertexEffdBV_num_tmp[f'{str(ntk)}tks']  = dfFiltered.Histo1D(model(f"vertexEffR_num_{bg}", f"Vertex Reconstruction Efficiency for {signal}", dBV_edges), "dBV_eff", f"{weightKey}_normalized")
                    vertexEffdPVV_num_tmp[f'{str(ntk)}tks'] = dfFiltered.Histo1D(model(f"vertexdPVV_num_{bg}", f"Vertex Reconstruction Efficiency for {signal}", dBV_edges), "dPVV_eff", f"{weightKey}_normalized")

                print("Adding histograms (triggers lazy action)")
                if(debugPlots):
                    originalTrack_pt[dataKey].Add(originalTrack_pt_tmp.GetValue())
                    originalTrack_eta[dataKey].Add(originalTrack_eta_tmp.GetValue())
                    originalTrack_phi[dataKey].Add(originalTrack_phi_tmp.GetValue())
                    originalTrack_dxy[dataKey].Add(originalTrack_dxy_tmp.GetValue())

                    newTrack_pt[dataKey].Add(newTrack_pt_tmp.GetValue())
                    newTrack_eta[dataKey].Add(newTrack_eta_tmp.GetValue())
                    newTrack_phi[dataKey].Add(newTrack_phi_tmp.GetValue())
                    newTrack_dxy[dataKey].Add(newTrack_dxy_tmp.GetValue())

                    movedTrack_pt[dataKey].Add(movedTrack_pt_tmp.GetValue())
                    movedTrack_eta[dataKey].Add(movedTrack_eta_tmp.GetValue())
                    movedTrack_phi[dataKey].Add(movedTrack_phi_tmp.GetValue())
                    movedTrack_dxy[dataKey].Add(movedTrack_dxy_tmp.GetValue())

                    pvXY[dataKey].Add(pvXY_tmp.GetValue())
                    pvZ[dataKey].Add(pvZ_tmp.GetValue())

                moveVertexDPVV[dataKey].Add(moveVertexDPVV_tmp.GetValue())
                moveVertexDPVV3D[dataKey].Add(moveVertexDPVV3D_tmp.GetValue())

                nMovedTracks[dataKey].Add(nMovedTracks_tmp.GetValue())
                nSurvivedTracks[dataKey].Add(nSurvivedTracks_tmp.GetValue())
                nCloseBGTracks[dataKey].Add(nCloseBGTracks_tmp.GetValue())
                nCloseTotalTracks[dataKey].Add(nCloseTotalTracks_tmp.GetValue())

                nSurvivedTracksVsdPVV[dataKey].Add(nSurvivedTracksVsdPVV_tmp.GetValue())
                nCloseBGTracksVsdPVV[dataKey].Add(nCloseBGTracksVsdPVV_tmp.GetValue())
                nCloseTotalTracksVsdPVV[dataKey].Add(nCloseTotalTracksVsdPVV_tmp.GetValue())

                nSurvivedSeedTracks[dataKey].Add(nSurvivedSeedTracks_tmp.GetValue())
                nCloseBGSeedTracks[dataKey].Add(nCloseBGSeedTracks_tmp.GetValue())
                nCloseTotalSeedTracks[dataKey].Add(nCloseTotalSeedTracks_tmp.GetValue())
                
                nSurvivedSeedTracksVsdPVV[dataKey].Add(nSurvivedSeedTracksVsdPVV_tmp.GetValue())
                nCloseBGSeedTracksVsdPVV[dataKey].Add(nCloseBGSeedTracksVsdPVV_tmp.GetValue())
                nCloseTotalSeedTracksVsdPVV[dataKey].Add(nCloseTotalSeedTracksVsdPVV_tmp.GetValue())

                nPV[dataKey].Add(nPV_tmp.GetValue())

                matchVertexDBV[dataKey].Add(matchVertexDBV_tmp.GetValue())
                moveVertexDBV[dataKey].Add(moveVertexDBV_tmp.GetValue())
                moveVertexDBV3D[dataKey].Add(moveVertexDBV3D_tmp.GetValue())
                moveVertex_sumPt[dataKey].Add(moveVertex_sumPt_tmp.GetValue())
                moveVertex_netPt[dataKey].Add(moveVertex_netPt_tmp.GetValue())
                moveVertex_netP[dataKey].Add(moveVertex_netP_tmp.GetValue())
                moveVertex_deltaR[dataKey].Add(moveVertex_deltaR_tmp.GetValue())

                #Efficiency denominators
                if(signal=="original"):
                    vertexEffSumPt_den[dataKey].Add(vertexEffSumPt_den_tmp.GetValue())
                    vertexEffNetPt_den[dataKey].Add(vertexEffNetPt_den_tmp.GetValue())
                    vertexEffNetP_den[dataKey].Add(vertexEffNetP_den_tmp.GetValue())
                    vertexEffDeltaR_den[dataKey].Add(vertexEffDeltaR_den_tmp.GetValue())
                    vertexEffdPVV3D_den[dataKey].Add(vertexEffdPVV3D_den_tmp.GetValue())

                vertexEffJet1Eta_den[dataKey].Add(vertexEffJet1Eta_den_tmp.GetValue())
                vertexEffJet2Eta_den[dataKey].Add(vertexEffJet2Eta_den_tmp.GetValue())

                vertexEffSurvTracks_den[dataKey].Add(vertexEffSurvTracks_den_tmp.GetValue())
                vertexEffCloseBGTracks_den[dataKey].Add(vertexEffCloseBGTracks_den_tmp.GetValue())
                vertexEffTotalCloseTracks_den[dataKey].Add(vertexEffTotalCloseTracks_den_tmp.GetValue())

                vertexEffSurvSeedTracks_den[dataKey].Add(vertexEffSurvSeedTracks_den_tmp.GetValue())
                vertexEffCloseBGSeedTracks_den[dataKey].Add(vertexEffCloseBGSeedTracks_den_tmp.GetValue())
                vertexEffTotalCloseSeedTracks_den[dataKey].Add(vertexEffTotalCloseSeedTracks_den_tmp.GetValue())

                vertexEffdBV_den[dataKey].Add(vertexEffdBV_den_tmp.GetValue())
                vertexEffdPVV_den[dataKey].Add(vertexEffdPVV_den_tmp.GetValue())


                for ntk in [3, 4, 5, 6, 7, 8, 9]:
                    if(signal=="original"):
                        vertexEffSumPt_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffSumPt_num_tmp[f'{str(ntk)}tks'].GetValue())
                        vertexEffNetPt_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffNetPt_num_tmp[f'{str(ntk)}tks'].GetValue())
                        vertexEffNetP_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffNetP_num_tmp[f'{str(ntk)}tks'].GetValue())
                        vertexEffDeltaR_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffDeltaR_num_tmp[f'{str(ntk)}tks'].GetValue())
                        vertexEffdPVV3D_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffdPVV3D_num_tmp[f'{str(ntk)}tks'].GetValue())

                    vertexEffJet1Eta_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffJet1Eta_num_tmp[f'{str(ntk)}tks'].GetValue())
                    vertexEffJet2Eta_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffJet2Eta_num_tmp[f'{str(ntk)}tks'].GetValue())

                    vertexEffSurvTracks_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffSurvTracks_num_tmp[f'{str(ntk)}tks'].GetValue())
                    vertexEffCloseBGTracks_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffCloseBGTracks_num_tmp[f'{str(ntk)}tks'].GetValue())
                    vertexEffTotalCloseTracks_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffTotalCloseTracks_num_tmp[f'{str(ntk)}tks'].GetValue())

                    vertexEffSurvSeedTracks_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffSurvSeedTracks_num_tmp[f'{str(ntk)}tks'].GetValue())
                    vertexEffCloseBGSeedTracks_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffCloseBGSeedTracks_num_tmp[f'{str(ntk)}tks'].GetValue())
                    vertexEffTotalCloseSeedTracks_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffTotalCloseSeedTracks_num_tmp[f'{str(ntk)}tks'].GetValue())

                    vertexEffdBV_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffdBV_num_tmp[f'{str(ntk)}tks'].GetValue())
                    vertexEffdPVV_num[f'{dataKey}_{str(ntk)}tks'].Add(vertexEffdPVV_num_tmp[f'{str(ntk)}tks'].GetValue())

            #Calculate the TEfficiency
            print("Evaulating TEfficiency...")
            for ntk in [3, 4, 5, 6, 7, 8, 9]:
                if(signal=="original"):
                    vertexEffSumPt[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffSumPt_num[f'{dataKey}_{str(ntk)}tks'], vertexEffSumPt_den[dataKey])
                    vertexEffNetPt[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffNetPt_num[f'{dataKey}_{str(ntk)}tks'], vertexEffNetPt_den[dataKey])
                    vertexEffNetP[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffNetP_num[f'{dataKey}_{str(ntk)}tks'], vertexEffNetP_den[dataKey])
                    vertexEffDeltaR[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffDeltaR_num[f'{dataKey}_{str(ntk)}tks'], vertexEffDeltaR_den[dataKey])
                    vertexEffdPVV3D[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffdPVV3D_num[f'{dataKey}_{str(ntk)}tks'], vertexEffdPVV3D_den[dataKey])

                vertexEffJet1Eta[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffJet1Eta_num[f'{dataKey}_{str(ntk)}tks'], vertexEffJet1Eta_den[dataKey])
                vertexEffJet2Eta[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffJet2Eta_num[f'{dataKey}_{str(ntk)}tks'], vertexEffJet2Eta_den[dataKey])

                vertexEffSurvTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffSurvTracks_num[f'{dataKey}_{str(ntk)}tks'], vertexEffSurvTracks_den[dataKey])
                vertexEffCloseBGTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffCloseBGTracks_num[f'{dataKey}_{str(ntk)}tks'], vertexEffCloseBGTracks_den[dataKey])
                vertexEffTotalCloseTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffTotalCloseTracks_num[f'{dataKey}_{str(ntk)}tks'], vertexEffTotalCloseTracks_den[dataKey])
                
                vertexEffSurvSeedTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffSurvSeedTracks_num[f'{dataKey}_{str(ntk)}tks'], vertexEffSurvSeedTracks_den[dataKey])
                vertexEffCloseBGSeedTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffCloseBGSeedTracks_num[f'{dataKey}_{str(ntk)}tks'], vertexEffCloseBGSeedTracks_den[dataKey])
                vertexEffTotalCloseSeedTracks[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffTotalCloseSeedTracks_num[f'{dataKey}_{str(ntk)}tks'], vertexEffTotalCloseSeedTracks_den[dataKey])
              
                vertexEffdBV[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffdBV_num[f'{dataKey}_{str(ntk)}tks'], vertexEffdBV_den[dataKey])
                vertexEffdPVV[f'{dataKey}_{str(ntk)}tks'] = ROOT.TEfficiency(vertexEffdPVV_num[f'{dataKey}_{str(ntk)}tks'], vertexEffdPVV_den[dataKey])


def loadSignalHistograms(dfs):
    print("Loading signal histograms...")
    for signal in dfs.keys():
        df = dfs[signal]

        signal_sumPt[signal] = df.Histo1D((f"sumPt_{signal}", f"LLP pT sum for {signal}", 30, 0, 1500), "genVert_sumPt_TM", "weight")
        signal_netPt[signal] = df.Histo1D((f"netPt_{signal}", f"LLP net pT for {signal}", 30, 0, 1500), "genVert_netPt_TM", "weight")
        signal_netP[signal] = df.Histo1D((f"netP_{signal}", f"LLP net momentum for {signal}", 30, 0, 1500), "genVert_netP_TM", "weight")
        signal_deltaR[signal] = df.Histo1D((f"deltaR_{signal}", f"Daughters delta R for {signal}", 30, 0, 6), "genVert_deltaR_TM", "weight")
        signal_DBV[signal] = df.Histo1D((f"dBV_{signal}", f"LLP dBV for {signal}", 30, 0, 2), "genVert_dBV2D_TM", "weight")
        signal_DBV3D[signal] = df.Histo1D((f"dBV3D_{signal}", f"LLP dBV 3D for {signal}", 30, 0, 5), "genVert_dBV3D_TM", "weight")

def make_ratio_hist(eff_data, eff_mc, name, title="", default=1.0):
    """Data/MC efficiency ratio as a TH1D (same binning as the TEfficiency)."""
    tot = eff_data.GetTotalHistogram()
    h = tot.Clone(name)
    h.Reset()
    h.SetDirectory(0)
    h.SetTitle(title)

    for i in range(1, tot.GetNbinsX() + 1):
        y1 = eff_data.GetEfficiency(i)
        y2 = eff_mc.GetEfficiency(i)

        if y1 <= 0 or y2 <= 0:
            # no usable ratio in this bin -> neutral correction, no error
            h.SetBinContent(i, default)
            h.SetBinError(i, 0.0)
            continue

        ratio = y1 / y2
        # same error propagation as in compare_plot, then symmetrised
        err_lo = ratio * np.sqrt((eff_data.GetEfficiencyErrorLow(i) / y1)**2 +
                                 (eff_mc.GetEfficiencyErrorUp(i)   / y2)**2)
        err_hi = ratio * np.sqrt((eff_data.GetEfficiencyErrorUp(i)  / y1)**2 +
                                 (eff_mc.GetEfficiencyErrorLow(i)   / y2)**2)
        h.SetBinContent(i, ratio)
        h.SetBinError(i, 0.5 * (err_lo + err_hi))

    return h
