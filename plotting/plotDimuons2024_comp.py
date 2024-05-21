#!/usr/bin/env python3                                                                                                                                               
# ***************************************                                                                             
# usage:                                                                                                                                     
#    python3 plotDimuons2024.py                                                                                
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


print("2024 Scouting - Dimuon studies")

year="2024"
lumi2024=4.2
energy="13.6"

xbins = [0.215]
while (xbins[-1]<250):
  xbins.append(1.01*xbins[-1])

  
# List of ROOT files
# ------------------
f_18 = TFile.Open("/afs/cern.ch/work/e/elfontan/private/SCOUTING/CMSSW_14_0_4/src/Run3ScoutingAnalysisTools/plotting/HISTOS/histos_mll/massRun2.root")
f_22 = TFile.Open("/afs/cern.ch/work/e/elfontan/private/SCOUTING/CMSSW_14_0_4/src/Run3ScoutingAnalysisTools/plotting/HISTOS/histos_mll/massRun3.root")
f_23C = TFile.Open("/afs/cern.ch/work/e/elfontan/private/SCOUTING/CMSSW_14_0_4/src/Run3ScoutingAnalysisTools/plotting/HISTOS/histos_mll/hmll_2023C.root")
f_23D = TFile.Open("/afs/cern.ch/work/e/elfontan/private/SCOUTING/CMSSW_14_0_4/src/Run3ScoutingAnalysisTools/plotting/HISTOS/histos_mll/hmll_2023D.root")
f_24 = TFile.Open("/afs/cern.ch/work/e/elfontan/private/SCOUTING/CMSSW_14_0_4/src/Run3ScoutingAnalysisTools/plotting/HISTOS/histos_mll/hmll_2024.root")


h_18 = TH1F("h_18","h_18",len(xbins)-1,array('f',xbins))
h_22 = TH1F("h_22","h_22",len(xbins)-1,array('f',xbins))
h_23C = TH1F("h_23C","h_23C",len(xbins)-1,array('f',xbins))
h_23D = TH1F("h_23D","h_23D",len(xbins)-1,array('f',xbins))
h_24 = TH1F("h_24","h_24",len(xbins)-1,array('f',xbins))

h_18 = f_18.Get("h_mass")
h_22 = f_22.Get("h_mass")
h_23C = f_23C.Get("hmll")
h_23D = f_23D.Get("hmll")
h_24 = f_24.Get("hmll")


  
c1 = TCanvas("c1","c1",1000,800)
c1.SetLogy()
c1.SetLogx()
c1.SetBottomMargin(0.1)
c1.SetLeftMargin(0.12)
c1.SetRightMargin(0.05)

col_list = [kMagenta-7, kOrange-3, kAzure-4, kGreen-3, kCyan-3]

lumi24=4.2
h_18.Scale(h_24.Integral()/h_18.Integral())
h_22.Scale(h_24.Integral()/h_22.Integral())
h_23C.Scale(h_24.Integral()/h_23C.Integral())
h_23D.Scale(h_24.Integral()/h_23D.Integral())
h_24.Scale(1./lumi24, "width")
h_23C.Scale(1./lumi24, "width")
h_23D.Scale(1./lumi24, "width")
h_22.Scale(1./lumi24, "width")
h_18.Scale(1./lumi24, "width")
h_18.GetXaxis().SetRangeUser(0.2,150 )
h_22.GetXaxis().SetRangeUser(0.2,150 )
h_23C.GetXaxis().SetRangeUser(0.2,150 )
h_23D.GetXaxis().SetRangeUser(0.2,150 )
h_24.GetXaxis().SetRangeUser(0.2,150 )

h_18.SetLineWidth(1)
h_18.SetMarkerStyle(20)
h_18.SetMarkerSize(0.2)
h_18.SetLineColor(col_list[0])
h_18.SetMarkerColor(col_list[0])
h_18.GetXaxis().SetTitleOffset(1.2)
h_18.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
h_18.GetYaxis().SetTitle("Events / GeV / fb^{-1}")

h_22.SetLineWidth(1)
h_22.SetLineColor(col_list[1])
h_23C.SetLineWidth(1)
h_23C.SetLineColor(col_list[2])
h_23D.SetLineWidth(1)
h_23D.SetLineColor(col_list[3])
h_24.SetLineWidth(1)
h_24.SetLineColor(col_list[4])
h_18.Draw("ehist")
h_22.Draw("ehist SAME")
h_23C.Draw("ehist SAME")
h_23D.Draw("ehist SAME")
h_24.Draw("ehist SAME")


legend=TLegend(0.2,0.15,0.45,0.3)                                                                       
legend.SetLineColor(0)
legend.AddEntry(h_18,"2018D","l")
legend.AddEntry(h_22,"2022F","l")
legend.AddEntry(h_23C,"2023C","l")
legend.AddEntry(h_23D,"2023D","l")
legend.AddEntry(h_24,"2024BCpartD","l")
legend.Draw()

latex = TLatex();
latex.SetTextSize(0.05);
latex.SetTextAlign(13);
latex.SetTextFont(62)  
latex.DrawLatexNDC(.12,.95,"CMS");
latex.SetTextFont(52)  
latex.DrawLatexNDC(.20,.95, " Preliminary");
latex.SetTextFont(42)  
latex.SetTextSize(0.04);
latex.DrawLatexNDC(.7,.95,"#sqrt{s} = 13--13.6 TeV");
#latex.DrawLatexNDC(.5,.95,"Run2024BCpartD ("+ str(lumi2024)+" fb^{-1}), #sqrt{s} = "+energy+" TeV");

c1.SaveAs(outputdir+"/hmll_yearComparisons.png")
c1.SaveAs(outputdir+"/hmll_yearComparisons.pdf")
