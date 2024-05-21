#!/usr/bin/env python3
# ***************************************
# usage: 
#    python3 scoutVSoffline.py
# ***************************************

import ROOT, array, random, copy
from ROOT import TCanvas, TFile, TH1, TH1F, TF1, gSystem
from ROOT import *
import ROOT, array, CMSGraphics, CMS_lumi, random, copy
from ROOT import RooCmdArg, RooArgSet, kFALSE, RooLinkedList, kBlue, kRed, kBlack, kOpenStar, kWhite, kGray
from ROOT import gStyle, TStyle, TGraph, TGraphErrors, TMath, TMultiGraph, TLine, gPad, TGaxis, TLegend, TText, TLatex, TColor, TPaveText
from ROOT import TAttFill, TLegend, TRatioPlot, TPad, THStack, TFileCollection
from ROOT import kBlue, kRed, kBlack, kWhite, kAzure, kOrange, kPink, kGreen, kYellow, kCyan
from array import array
import math
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import argparse
import sys

argparser = argparse.ArgumentParser(description='Parser used for non default arguments', formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=True)
argparser.add_argument('--outdir', dest='outdir', default='/eos/user/e/elfontan/www/CMS_SCOUTING/2024', help='Output directory')
args = argparser.parse_args()
outputdir = args.outdir

ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

lowmass = False
fullmass = True
#lowmass = True
#fullmass = False

######################################
# List of files and output directory #
######################################
def list_full_paths(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory)]
files = list_full_paths("/eos/user/e/elfontan/2024_SCOUTING/ScoutingPFMonitor/")
#files = files[:-5] 


########################
# Variables and histos #
########################
h_pt_res_zoom   = TH1F("h_pt_res_zoom", "h_pt_res_zoom", 200, -0.1, 0.1)
h_mass_res_zoom = TH1F("h_mass_res_zoom", "h_mass_res_zoom", 200, -0.1, 0.1)
h_pt_res        = TH1F("h_pt_res", "h_pt_res", 400, -0.4, 0.4) 
h_mass_res      = TH1F("h_mass_res", "h_mass_res", 400, -0.4, 0.4) 

if (fullmass):
    xbins = [0.215]
    #xbins = [0.295]
    while (xbins[-1]<250):
        xbins.append(1.01*xbins[-1])
    #print("xbins", xbins)
    xbins_rebin = [0.215]
    while (xbins_rebin[-1]<250):
        xbins_rebin.append(1.05*xbins_rebin[-1])
if (lowmass):
    xbins = [0.215]
    while (xbins[-1]<20):
        xbins.append(1.01*xbins[-1])
    print("xbins", xbins)
    print("len(xbins)", len(xbins))
    xbins_rebin = [0.215]
    while (xbins_rebin[-1]<20):
        xbins_rebin.append(1.05*xbins_rebin[-1])
    print("xbins_rebin", xbins_rebin)
    print("len(xbins_rebin)", len(xbins_rebin))

h_mass_offline = TH1F("h_mass_offline", "h_mass_offline", len(xbins)-1,array('f',xbins)) #LOG
h_mass_scout = TH1F("h_mass_scout", "h_mass_scout", len(xbins)-1,array('f',xbins)) #LOG
h_mass_offline_reb = TH1F("h_mass_offline_reb", "h_mass_offline_reb", len(xbins_rebin)-1,array('f',xbins_rebin))
h_mass_scout_reb = TH1F("h_mass_scout_reb", "h_mass_scout_reb", len(xbins_rebin)-1,array('f',xbins_rebin))

if (fullmass):
    frame = TH1F("frame","",1000,0.18,250.2)
    f_ratio = TH1F("f_ratio","",1000,0.18,250.2)
elif (lowmass):
    frame = TH1F("frame","",1000,0.18,20.2)
    f_ratio = TH1F("f_ratio","",1000,0.18,20.2)

# Loop over the files and fill the histo
print(">>>>>> READING...")
print(">>>>>> List of files:")
for filename in files:
    root_file = ROOT.TFile.Open(filename)
    print(filename)

    # Extract the TTree from the ROOT file
    t_scoutMuon = root_file.Get('scoutingTree/tree')

    # Check if the TTree was extracted successfully
    if not t_scoutMuon:
        print('Error: failed to extract TTree from {file_name}')
        root_file.Close()
        continue

    #t_scoutMuon.Draw("pt1>>h_pt_res")
    for ev in t_scoutMuon:
      #print("nScoutingMuons = ", ev.nScoutingMuons )
      if (not(ev.nScoutingMuons == 2)): continue
      #if (ev.pt1_scout == ev.pt2_scout): continue
      #if (ev.drmm < 0.2): continue 
      #if (ev.drmm < 0.2 or ev.drmm_scout < 0.2): continue 
      if (ev.dr_matching_1 > 0.2 or ev.dr_matching_2 > 0.2): continue

      if ((ev.l1Result[0]==1 or ev.l1Result[1]==1 or ev.l1Result[2]==1 or ev.l1Result[3]==1 or ev.l1Result[4]==1 or ev.l1Result[5]==1 or ev.l1Result[6]==1 or ev.l1Result[7]==1 or ev.l1Result[8]==1 or ev.l1Result[9]==1 or ev.l1Result[10]==1 or ev.l1Result[11]==1 or ev.l1Result[12]==1 or ev.l1Result[13]==1 or ev.l1Result[14]==1 or ev.l1Result[15]==1 or ev.l1Result[16]==1 or ev.l1Result[17]==1 or ev.l1Result[18]==1 or ev.l1Result[19]==1 or ev.l1Result[20]==1 or ev.l1Result[21]==1 or ev.l1Result[22]==1 or ev.l1Result[23]==1) and ev.ndvtx > 0 ):
      #if ((ev.l1Result[0]==1 or ev.l1Result[1]==1 or ev.l1Result[2]==1 or ev.l1Result[3]==1 or ev.l1Result[4]==1 or ev.l1Result[5]==1) and ev.lxy > 0.0):
          #if (ev.mu1_ID[0] and ev.mu2_ID[0] and ev.pfIso1 < 0.25 and ev.pfIso2 < 0.25):
          #print("pt1 = ", ev.pt1, " and pt1_scout = ", ev.pt1_scout)
          h_pt_res_zoom.Fill((ev.pt1_scout - ev.pt1)/ev.pt1)
          h_pt_res_zoom.Fill((ev.pt2_scout - ev.pt2)/ev.pt2)
          h_pt_res.Fill((ev.pt1_scout - ev.pt1)/ev.pt1)
          h_pt_res.Fill((ev.pt2_scout - ev.pt2)/ev.pt2)
          h_mass_res_zoom.Fill((ev.mass_scout - ev.mass)/ev.mass)
          h_mass_res.Fill((ev.mass_scout - ev.mass)/ev.mass)
          h_mass_offline.Fill(ev.mass)
          h_mass_scout.Fill(ev.mass_scout)
          h_mass_offline_reb.Fill(ev.mass)
          h_mass_scout_reb.Fill(ev.mass_scout)
      else:
          continue
    # Close the ROOT file
    root_file.Close()


legend = ROOT.TLegend (0.6, 0.6, 0.86, 0.86)
legend.SetTextSize (0.03)
legend.AddEntry (h_pt_res, "Uncorrected muons", "NDC")
legend.SetLineWidth (0)

CMS_lumi.writeExtraText = True                                                                                                             
CMS_lumi.extraText      = "Preliminary"
CMS_lumi.lumi_sqrtS      = "3.1 fb^{-1} (13.6 TeV, 2024)"                                                                                   
CMS_lumi.cmsTextSize    = 0.6
CMS_lumi.lumiTextSize   = 0.46
CMS_lumi.extraOverCmsTextSize = 0.75
CMS_lumi.relPosX = 0.12


# --------------------------------------------------------------------
#gr_text = ROOT.TPaveText(0.3, 0.78, 0.85, 0.83, "NDC")

gr_text1 = ROOT.TPaveText(0.12, 0.8, 0.7, 0.84, "NDC")
gr_text1.AddText("Events with two matched muons, #DeltaR_{#mu#mu} > 0.2 and p_{T}^{#mu} > 3 GeV")
#gr_text1.AddText("Events with two matched muons, #Delta#it{R}_{#it{#mu#mu}} > 0.2 and p_{T}^{#it{#mu}} > 3 GeV")
gr_text1.SetTextSize(0.032)
gr_text1.SetFillColor(0)

#leg_mass = ROOT.TLegend (0.15, 0.7, 0.45, 0.88)
leg_mass = ROOT.TLegend (0.735, 0.65, 0.88, 0.82)
leg_mass.SetTextSize(0.037)
leg_mass.AddEntry (h_mass_offline, "Offline", "F")
leg_mass.AddEntry (h_mass_scout, "Scouting", "F")
leg_mass.SetLineWidth (0)

labels = TLatex()
masses = {
    "#bf{#eta}": 0.546862,
    "#bf{#rho,#omega}": 0.780,
    "#bf{#phi}": 1.019,
    "#bf{J/#Psi}": 3.096,
    "#bf{#Psi'}": 3.686,
    "#bf{#Upsilon(nS)}": 9.460,
    "#bf{Z}": 91.1876,
}
labels.SetTextSize(0.04)
labels.SetTextAlign(21)

if (fullmass):
    c_mass = ROOT.TCanvas("c_mass", "c_mass", 1200, 1000)
    c_mass.cd()    
    c_mass.SetLeftMargin(0.11)
    c_mass.SetBottomMargin(0.17)
    
    pad_main = TPad("pad_main", "pad_main", 0.0, 0.3, 1.0, 1.0)
    pad_main.SetBottomMargin(0.02)
    pad_main.SetLogx()    
    pad_main.SetLogy()    
    pad_main.Draw()
    pad_main.cd()
    
    frame.SetMinimum(10)
    frame.SetMaximum(1000000)
    frame.GetXaxis().SetLabelOffset(0.2)
    frame.GetXaxis().SetTitleOffset(1.9)
    frame.GetYaxis().SetLabelSize(0.05)
    frame.GetYaxis().SetTitleOffset(0.9)
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
    frame.GetYaxis().SetTitle("Events / MeV")

    frame.Draw()

    h_mass_offline.SetLineWidth(2)
    h_mass_offline.SetLineColor(kBlue-3)
    #h_mass_offline.SetLineColor(kOrange-3)
    #h_mass_offline.SetFillColorAlpha(kAzure-9,0.35)
    h_mass_scout.SetLineWidth(3)
    h_mass_scout.SetFillColor(kMagenta-9)
    h_mass_scout.SetLineColor(kMagenta-9)
    #h_mass_scout.SetFillColorAlpha(kMagenta-9,0.65)
    h_mass_scout.SetFillStyle(3015)    
    #h_mass_scout.SetFillStyle(3004)
    h_mass_scout.Scale(1., "width")
    h_mass_offline.Scale(1., "width")
    h_mass_scout.Draw("same hist")
    h_mass_offline.Draw("same hist")
    frame.Draw("same axis")
    
    [ labels.DrawLatex(masses[m], 1.5*h_mass_offline.GetBinContent(h_mass_scout.FindBin(masses[m])), m) for m in masses ]
    labels.Draw("same")
    gr_text1.Draw("same")
    leg_mass.Draw ("same")
    CMS_lumi.CMS_lumi(pad_main, 0, 0)

    # Create ratio pad
    c_mass.cd()  # Go back to the main canvas
    pad_ratio = TPad("pad_ratio", "pad_ratio", 0.0, 0.0, 1.0, 0.3)
    pad_ratio.SetTopMargin(0.05)
    pad_ratio.SetBottomMargin(0.3)
    pad_ratio.SetTicks()    
    pad_ratio.SetLogx()    
    pad_ratio.Draw()
    pad_ratio.cd()
        
    # Compute and draw ratio histogram                     
    # --------------------------------
    h_mass_offline_reb.Scale(1., "width")
    h_mass_scout_reb.Scale(1., "width")
    h_ratio = h_mass_offline_reb.Clone()
    h_ratio.Divide(h_mass_scout_reb)                                                                                    
    
    h_ratio.SetFillColor(kGray)
    f_ratio.GetYaxis().SetRangeUser(0.6, 1.4)
    f_ratio.GetXaxis().SetLabelSize(0.12)
    f_ratio.GetYaxis().SetLabelSize(0.08)
    f_ratio.GetXaxis().SetTitleSize(0.12)
    f_ratio.GetYaxis().SetTitleSize(0.1)
    f_ratio.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
    f_ratio.GetXaxis().SetTitleOffset(1.1)
    f_ratio.GetYaxis().SetTitle("Offline / Scouting")
    f_ratio.GetYaxis().SetTitleOffset(0.45)
    h_ratio.SetBinContent(0, 0)

    f_ratio.GetYaxis().SetNdivisions(505)
    f_ratio.GetXaxis().SetTickSize(0.06)

    f_ratio.Draw("")
    h_ratio.Draw("E4 same")

    line_at_one = TLine(0.215, 1, 250.1, 1)
    line_at_one.SetLineStyle(2)
    line_at_one.Draw("same")
    
    # Update and save canvas
    c_mass.Update()
    c_mass.SaveAs(outputdir + "/mass_logXYwidth.png")
    c_mass.SaveAs(outputdir + "/mass_logXYwidth.pdf")
    
if (lowmass):
    c_lowmass = ROOT.TCanvas("c_lowmass", "c_lowmass", 1200, 1000)
    c_lowmass.cd()    
    #c_lowmass.SetLogx()    
    #c_lowmass.SetLogy()    
    c_lowmass.SetLeftMargin(0.13)
    c_lowmass.SetBottomMargin(0.1)

    # Create main pad
    pad_main = TPad("pad_main", "pad_main", 0.0, 0.3, 1.0, 1.0)
    pad_main.SetBottomMargin(0.02)
    pad_main.SetLogx()    
    pad_main.SetLogy()    
    pad_main.SetTicks()    
    pad_main.Draw()
    pad_main.cd()

    frame.SetMinimum(100)
    frame.SetMaximum(3000000)
    #frame.GetXaxis().SetRangeUser(0.3,20.)
    frame.GetXaxis().SetLabelOffset(0.2)
    frame.GetXaxis().SetTitleOffset(1.9)
    #frame.GetYaxis().SetLabelOffset(0.08)
    frame.GetYaxis().SetLabelSize(0.05)
    frame.GetYaxis().SetTitleOffset(0.9)
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
    #frame.GetXaxis().SetTitle("#it{m}_{#it{#mu#mu}} [GeV]")
    frame.GetYaxis().SetTitle("Events / MeV")
    #frame.GetYaxis().SetTickSize(0)
    #frame.GetYaxis().SetTickLength(0)
    #frame.GetXaxis().SetTickLength(0.05)  # Length of ticks
    #frame.GetYaxis().SetTickLength(0.05)  # Length of ticks

    frame.Draw()

    #h_mass_offline.GetYaxis().SetRangeUser(100, 10000000)
    #h_mass_scout.GetYaxis().SetRangeUser(100, 10000000)
    h_mass_offline.SetLineWidth(2)
    #h_mass_offline.SetLineStyle(2)
    #h_mass_offline.SetLineWidth(3)
    #h_mass_offline.SetLineStyle(8)
    h_mass_offline.SetLineColor(kBlue-3)
    #h_mass_offline.SetLineColor(kOrange-3)
    #h_mass_offline.SetFillColorAlpha(kAzure-9,0.35)
    h_mass_scout.SetLineWidth(3)
    h_mass_scout.SetFillColor(kMagenta-9)
    h_mass_scout.SetLineColor(kMagenta-9)
    #h_mass_scout.SetFillColorAlpha(kMagenta-9,0.65)
    h_mass_scout.SetFillStyle(3015)    
    #h_mass_scout.SetFillStyle(3004)
    h_mass_scout.Scale(1., "width")
    h_mass_offline.Scale(1., "width")
    h_mass_scout.Draw("same hist")
    h_mass_offline.Draw("same hist")
    frame.Draw("same axis")
    
    [ labels.DrawLatex(masses[m], 1.5*h_mass_offline.GetBinContent(h_mass_scout.FindBin(masses[m])), m) for m in masses ]
    labels.Draw("same")
    gr_text1.Draw("same")
    leg_mass.Draw ("same")
    CMS_lumi.CMS_lumi(pad_main, 0, 0)

    # Create ratio pad
    c_lowmass.cd()  # Go back to the main canvas
    pad_ratio = TPad("pad_ratio", "pad_ratio", 0.0, 0.0, 1.0, 0.3)
    pad_ratio.SetTopMargin(0.05)
    pad_ratio.SetBottomMargin(0.3)
    pad_ratio.SetTicks()    
    pad_ratio.SetLogx()    
    pad_ratio.Draw()
    pad_ratio.cd()
        
    # Compute and draw ratio histogram                     
    # --------------------------------
    h_mass_offline_reb.Scale(1., "width")
    h_mass_scout_reb.Scale(1., "width")
    h_ratio = h_mass_offline_reb.Clone()
    h_ratio.Divide(h_mass_scout_reb)                                                                                    
    
    h_ratio.SetFillColor(kGray)
    f_ratio.GetYaxis().SetRangeUser(0.6, 1.4)
    f_ratio.GetXaxis().SetLabelSize(0.12)
    f_ratio.GetYaxis().SetLabelSize(0.08)
    f_ratio.GetXaxis().SetTitleSize(0.12)
    f_ratio.GetYaxis().SetTitleSize(0.1)
    f_ratio.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
    f_ratio.GetXaxis().SetTitleOffset(1.1)
    f_ratio.GetYaxis().SetTitle("Offline / Scouting")
    f_ratio.GetYaxis().SetTitleOffset(0.45)
    h_ratio.SetBinContent(0, 0)

    f_ratio.GetYaxis().SetNdivisions(505)
    f_ratio.GetXaxis().SetTickSize(0.06)

    f_ratio.Draw("")
    h_ratio.Draw("E4 same")

    line_at_one = TLine(0.215, 1, 20.1, 1)
    line_at_one.SetLineStyle(2)
    line_at_one.Draw("same")
    
    c_lowmass.Update()
    c_lowmass.SaveAs(outputdir + "/dimuScouting_lowmass.png")
    c_lowmass.SaveAs(outputdir + "/dimuScouting_lowmass.pdf")
