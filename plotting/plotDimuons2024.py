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

t = TChain("scoutingTree/tree")
t.Add("/eos/user/e/elfontan/2024_SCOUTING/ScoutingPFRun3/data_2024B.root")
t.Add("/eos/user/e/elfontan/2024_SCOUTING/ScoutingPFRun3/data_2024C.root")
t.Add("/eos/user/e/elfontan/2024_SCOUTING/ScoutingPFRun3/data_2024D.root")

year="2024"
lumi=4.2
energy="13.6"

print(t.GetEntries())

xbins = [0.215]
while (xbins[-1]<250):
  xbins.append(1.01*xbins[-1])

hmll = TH1F("hmll","hmll",len(xbins)-1,array('f',xbins))

t.Draw("mass>>hmll","(l1Result[0]==1||l1Result[1]==1||l1Result[2]==1||l1Result[3]==1||l1Result[4]==1||l1Result[5]==1||l1Result[6]==1||l1Result[7]==1||l1Result[8]==1||l1Result[9]==1||l1Result[10]==1||l1Result[11]==1||l1Result[12]==1||l1Result[13]==1||l1Result[14]==1||l1Result[15]==1||l1Result[16]==1||l1Result[17]==1||l1Result[18]==1||l1Result[19]==1||l1Result[20]==1||l1Result[21]==1||l1Result[22]==1||l1Result[23]==1)","goff")
hmll.SaveAs("hmll_"+year+".root")

c1 = TCanvas("c1","c1",800,600)
c1.SetLogy()
c1.SetLogx()
c1.SetLeftMargin(0.12)
c1.SetRightMargin(0.05)
hmll.Scale(1.0/lumi,"width")
hmll.SetLineWidth(1)
hmll.SetMarkerStyle(20)
hmll.SetMarkerSize(0.2)
hmll.SetLineColor(kCyan-3)
hmll.SetMarkerColor(kCyan-3)
hmll.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
hmll.GetYaxis().SetTitle("Events / GeV / fb^{-1}")
hmll.Draw("ehist")

latex = TLatex();
latex.SetTextSize(0.05);
latex.SetTextAlign(13);
latex.SetTextFont(62)  
latex.DrawLatexNDC(.12,.95,"CMS");
latex.SetTextFont(52)  
latex.DrawLatexNDC(.20,.95,"Preliminary");
latex.SetTextFont(42)  
latex.SetTextSize(0.04);
latex.DrawLatexNDC(.5,.95,"Run2024B ("+ str(lumi)+" fb^{-1}), #sqrt{s} = "+energy+" TeV");

c1.SaveAs(outputdir+"/hmll_"+year+"_BCpartD.png")
c1.SaveAs(outputdir+"/hmll_"+year+"_BCpartD.pdf")

#L1Info = ["L1_DoubleMu_12_5","L1_DoubleMu_15_7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18","L1_DoubleMu4_SQ_OS_dR_Max1p2","L1_DoubleMu4p5_SQ_OS_dR_Max1p2"]
L1Info = ["L1_DoubleMu_12_5","L1_DoubleMu_15_7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18","L1_DoubleMu8_SQ","L1_DoubleMu0er1p4_SQ_OS_dEta_Max1p2","L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6","L1_DoubleMu5_SQ_OS_dR_Max1p6","L1_DoubleMu3er2p0_SQ_OS_dR_Max1p6","L1_DoubleMu0er1p5_SQ_OS_dEta_Max1p2","L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6","L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6","L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5","L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4","L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4","L1_DoubleMu4p5_SQ_OS_dR_Max1p2","L1_DoubleMu4_SQ_OS_dR_Max1p2","L1_DoubleMu0_Upt15_Upt7","L1_DoubleMu0_Upt6_IP_Min1_Upt4","L1_DoubleMu6_Upt6_SQ_er2p0","L1_DoubleMu7_Upt7_SQ_er2p0","L1_DoubleMu8_Upt8_SQ_er2p0","L1_DoubleMu0er2p0_SQ_dEta_Max1p6","L1_DoubleMu0er2p0_SQ_dEta_Max1p5"]

hl1={}
il1=0
maximums=[]
for l1 in L1Info:
  hl1[l1] = TH1F("hl1"+l1,"hl1"+l1,len(xbins)-1,array('f',xbins))
  t.Draw("mass>>hl1"+l1,"l1Result["+str(il1)+"]==1","goff")
  hl1[l1].Scale(1.0/lumi,"width")
  maximums.append(hl1[l1].GetMaximum())
  il1+=1


c1 = TCanvas("c1","c1",800,600)
c1.SetLogy()
c1.SetLogx()
c1.SetLeftMargin(0.12)
c1.SetRightMargin(0.05)
hmll.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
hmll.GetYaxis().SetTitle("Events / GeV / fb^{-1}")
hmll.GetYaxis().SetRangeUser(10,80000000)
hmll.Draw("ehist")

col = [ROOT.kPink-7,ROOT.kAzure-7,ROOT.kSpring-7,ROOT.kSpring-9,ROOT.kOrange-3,ROOT.kTeal-7,ROOT.kMagenta-9,ROOT.kCyan-7,ROOT.kYellow-7,ROOT.kViolet-7,ROOT.kViolet-9,ROOT.kGreen-7,ROOT.kGreen-9]
    
legend=TLegend(0.15,0.12,0.56,0.38)
legend.AddEntry(hmll,"Total","l")
legend.SetLineColor(0)
legend.SetFillColor(0)
i=0
for l1 in L1Info:
  if (l1=="L1_DoubleMu_12_5" or l1=="L1_DoubleMu4_SQ_OS_dR_Max1p2" or l1=="L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18" or l1=="L1_DoubleMu3er2p0_SQ_OS_dR_Max1p6" or l1=="L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4" or l1=="L1_DoubleMu5_SQ_OS_dR_Max1p6" or l1=="L1_DoubleMu0er1p5_SQ_OS_dEta_Max1p2" or l1=="L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6" or l1=="L1_DoubleMu0er1p4_SQ_OS_dEta_Max1p2" or l1=="L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6" or l1=="L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5" or l1=="L1_DoubleMu0er2p0_SQ_dEta_Max1p6" or l1=="L1_DoubleMu0er2p0_SQ_dEta_Max1p5" or l1=="L1_DoubleMu0_Upt6_IP_Min1_Upt4" or l1=="L1_DoubleMu6_Upt6_SQ_er2p0" or l1=="L1_DoubleMu7_Upt7_SQ_er2p0" or l1=="L1_DoubleMu8_Upt8_SQ_er2p0"): continue
  hl1[l1].SetLineWidth(1)
  hl1[l1].SetMarkerStyle(20)
  hl1[l1].SetMarkerSize(0.2)
  hl1[l1].SetLineColor(col[i])
  hl1[l1].SetMarkerColor(col[i])
  hl1[l1].GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
  hl1[l1].GetYaxis().SetTitle("Events / GeV / fb^{-1}")
  hl1[l1].Draw("ehistsame")
  legend.AddEntry(hl1[l1],l1,"l")
  i+=1
legend.Draw("same")

latex = TLatex();
latex.SetTextSize(0.05);
latex.SetTextAlign(13);
latex.SetTextFont(62)  
latex.DrawLatexNDC(.12,.95,"CMS");
latex.SetTextFont(52)  
latex.DrawLatexNDC(.20,.95,"Preliminary");
latex.SetTextFont(42)  
latex.SetTextSize(0.04);
latex.DrawLatexNDC(.5,.95,"2024 B+C+partD ("+ str(lumi)+" fb^{-1}), #sqrt{s} = "+energy+" TeV");

c1.SaveAs(outputdir+"/hmll_l1_"+year+"_BCpartD.png")
c1.SaveAs(outputdir+"/hmll_l1_"+year+"_BCpartD.pdf")



xbins = [2.7]
while (xbins[-1]<3.5):
  xbins.append(xbins[-1]+0.01)

hpsi = TH1F("hpsi","hpsi",len(xbins)-1,array('f',xbins))

t.Draw("mass>>hpsi","mass>2.7 && mass<3.5 && (l1Result[0]==1||l1Result[1]==1||l1Result[2]==1||l1Result[3]==1||l1Result[4]==1||l1Result[5]==1||l1Result[6]==1||l1Result[7]==1||l1Result[8]==1||l1Result[9]==1||l1Result[10]==1||l1Result[11]==1||l1Result[12]==1||l1Result[13]==1||l1Result[14]==1||l1Result[15]==1||l1Result[16]==1||l1Result[17]==1||l1Result[18]==1||l1Result[19]==1||l1Result[20]==1||l1Result[21]==1||l1Result[22]==1||l1Result[23]==1)","goff")
hpsi.SaveAs("hpsi_"+year+".root")
hpsi.Sumw2()

hpsi.Scale(1.0/lumi) # 1/Lumi

c2 = TCanvas("c2","c2",800,600)
#c2.SetLogy()
#c2.SetLogx()
c2.SetLeftMargin(0.12)
c2.SetRightMargin(0.05)
hpsi.SetLineWidth(2)
hpsi.SetMarkerStyle(20)
hpsi.SetMarkerSize(1)
hpsi.SetLineColor(kBlue+2)
hpsi.SetMarkerColor(kBlue+2)
hpsi.GetXaxis().SetRangeUser(2.7,3.5)
hpsi.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
hpsi.GetYaxis().SetTitle("Events / 0.01 GeV / fb^{-1}")

hpsi.Draw("ep")
fit = TF1("fit","crystalball(0)+gaus(5)+pol1(8)",2.7,3.5)
fit.SetParameter(0,100000./lumi)
fit.SetParameter(1,3.09)
fit.SetParameter(2,0.025)
fit.SetParameter(3,1.2)
fit.SetParameter(4,3.9)
fit.SetParameter(5,30000./lumi)
fit.SetParameter(6,3.08)
fit.SetParameter(7,0.04)
fit.SetParameter(8,14000./lumi)
fit.SetParameter(9,-3000./lumi)
hpsi.Fit(fit,"R")
fit.SetLineColor(kBlue+2)
fit.Draw("lsame")

latex = TLatex();
latex.SetTextSize(0.05);
latex.SetTextAlign(13);
latex.SetTextFont(62)  
latex.DrawLatexNDC(.12,.95,"CMS");
latex.SetTextFont(52)  
latex.DrawLatexNDC(.20,.95,"Preliminary");
latex.SetTextFont(42)  
latex.SetTextSize(0.04);
latex.DrawLatexNDC(.5,.95,"Run2024B ("+ str(lumi)+" fb^{-1}), #sqrt{s} = "+energy+" TeV");

print(hpsi.Integral())
print(fit.Integral(2.7,3.5)/hpsi.GetBinWidth(1))

sig = TF1("sig","crystalball(0)+gaus(5)",2.7,3.5)
p=0
while (p<=7):
  sig.SetParameter(p,fit.GetParameter(p))
  p+=1

print(sig.Integral(2.7,3.5)/hpsi.GetBinWidth(1))

c2.SaveAs(outputdir+"/hpsi_"+year+"_BCpartD.png")
c2.SaveAs(outputdir+"/hpsi_"+year+"_BCpartD.pdf")



xbins = [0.3]
while (xbins[-1]<0.8):
  xbins.append(xbins[-1]+0.001)

hpsi = TH1F("hpsi","hpsi",len(xbins)-1,array('f',xbins))

t.Draw("mass>>hpsi","mass>0.3 && mass<0.8 && (l1Result[0]==1||l1Result[1]==1||l1Result[2]==1||l1Result[3]==1||l1Result[4]==1||l1Result[5]==1||l1Result[6]==1||l1Result[7]==1||l1Result[8]==1||l1Result[9]==1||l1Result[10]==1||l1Result[11]==1||l1Result[12]==1||l1Result[13]==1||l1Result[14]==1||l1Result[15]==1||l1Result[16]==1||l1Result[17]==1||l1Result[18]==1||l1Result[19]==1||l1Result[20]==1||l1Result[21]==1||l1Result[22]==1||l1Result[23]==1)","goff")
hpsi.SaveAs("hpsi_"+year+".root")
hpsi.Sumw2()

hpsi.Scale(1.0/lumi) # 1/Lumi

c2 = TCanvas("c2","c2",800,600)
#c2.SetLogy()
#c2.SetLogx()
c2.SetLeftMargin(0.12)
c2.SetRightMargin(0.05)
hpsi.SetLineWidth(2)
hpsi.SetMarkerStyle(20)
hpsi.SetMarkerSize(1)
hpsi.SetLineColor(kBlue+2)
hpsi.SetMarkerColor(kBlue+2)
hpsi.GetXaxis().SetRangeUser(0.3,0.8)
hpsi.GetXaxis().SetTitle("m_{#mu#mu} [GeV]")
hpsi.GetYaxis().SetTitle("Events / 1 MeV / fb^{-1}")

hpsi.Draw("ep")
fit = TF1("fit","crystalball(0)+gaus(5)+pol1(8)",0.3,0.8)
fit.SetParameter(0,100000./lumi)
fit.SetParameter(1,3.09)
fit.SetParameter(2,0.025)
fit.SetParameter(3,1.2)
fit.SetParameter(4,3.9)
fit.SetParameter(5,30000./lumi)
fit.SetParameter(6,3.08)
fit.SetParameter(7,0.04)
fit.SetParameter(8,14000./lumi)
fit.SetParameter(9,-3000./lumi)
hpsi.Fit(fit,"R")
fit.SetLineColor(kBlue+2)
fit.Draw("lsame")

latex = TLatex();
latex.SetTextSize(0.05);
latex.SetTextAlign(13);
latex.SetTextFont(62)  
latex.DrawLatexNDC(.12,.95,"CMS");
latex.SetTextFont(52)  
latex.DrawLatexNDC(.20,.95,"Preliminary");
latex.SetTextFont(42)  
latex.SetTextSize(0.04);
latex.DrawLatexNDC(.5,.95,"Run2024B ("+ str(lumi)+" fb^{-1}), #sqrt{s} = "+energy+" TeV");

print(hpsi.Integral())
print(fit.Integral(0.3,0.8)/hpsi.GetBinWidth(1))

sig = TF1("sig","crystalball(0)+gaus(5)",0.3,0.8)
p=0
while (p<=7):
  sig.SetParameter(p,fit.GetParameter(p))
  p+=1

print(sig.Integral(0.3,0.8)/hpsi.GetBinWidth(1))

c2.SaveAs(outputdir+"/heta_"+year+"_BCpartD.png")
c2.SaveAs(outputdir+"/heta_"+year+"_BCpartD.pdf")
