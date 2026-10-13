import uproot
import matplotlib.pyplot as plt
import ROOT
import numpy as np
import awkward as ak
from concurrent.futures import ProcessPoolExecutor, as_completed

signalDict = {"Stop-M200-cT1": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-200_CTau-1mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-200_CTau-1mm_Tree_v35-4DxyMin/260925_191151/StopStopbarTo2Dbar2D_M-200_CTau-1mm.root"],
              "Stop-M400-cT1": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-400_CTau-1mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-400_CTau-1mm_Tree_v35-4DxyMin/260925_191247/StopStopbarTo2Dbar2D_M-400_CTau-1mm.root"],
              "Stop-M600-cT1": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-600_CTau-1mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-600_CTau-1mm_Tree_v35-4DxyMin/260925_191346/StopStopbarTo2Dbar2D_M-600_CTau-1mm.root"],
              "Stop-M800-cT1": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-800_CTau-1mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-800_CTau-1mm_Tree_v35-4DxyMin/260925_191446/StopStopbarTo2Dbar2D_M-800_CTau-1mm.root"],
              "Stop-M200-cT3": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-200_CTau-3mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-200_CTau-3mm_Tree_v35-4DxyMin/260925_191202/StopStopbarTo2Dbar2D_M-200_CTau-3mm.root"],
              "Stop-M400-cT3": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-400_CTau-3mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-400_CTau-3mm_Tree_v35-4DxyMin/260925_191258/StopStopbarTo2Dbar2D_M-400_CTau-3mm.root"],
              "Stop-M600-cT3": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-600_CTau-3mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-600_CTau-3mm_Tree_v35-4DxyMin/260925_191356/StopStopbarTo2Dbar2D_M-600_CTau-3mm.root"],
              "Stop-M800-cT3": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-800_CTau-3mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-800_CTau-3mm_Tree_v35-4DxyMin/260925_191456/StopStopbarTo2Dbar2D_M-800_CTau-3mm.root"],
              "Stop-M200-cT10": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-200_CTau-10mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-200_CTau-10mm_Tree_v35-4DxyMin/260925_191143/StopStopbarTo2Dbar2D_M-200_CTau-10mm.root"],
              "Stop-M400-cT10": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-400_CTau-10mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-400_CTau-10mm_Tree_v35-4DxyMin/260925_191237/StopStopbarTo2Dbar2D_M-400_CTau-10mm.root"],
              "Stop-M600-cT10": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-600_CTau-10mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-600_CTau-10mm_Tree_v35-4DxyMin/260925_191335/StopStopbarTo2Dbar2D_M-600_CTau-10mm.root"],
              "Stop-M800-cT10": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-800_CTau-10mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-800_CTau-10mm_Tree_v35-4DxyMin/260925_191433/StopStopbarTo2Dbar2D_M-800_CTau-10mm.root"],
              "Stop-M200-cT0p1": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-200_ctau-0p1mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-200_ctau-0p1mm_Tree_v35-4DxyMin/260925_191210/StopStopbarTo2Dbar2D_M-200_ctau-0p1mm_100kEvts_v2.root"],
              "Stop-M400-cT0p1": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-400_ctau-0p1mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-400_ctau-0p1mm_Tree_v35-4DxyMin/260925_191308/StopStopbarTo2Dbar2D_M-400_ctau-0p1mm_100kEvts_v2.root"],
              "Stop-M600-cT0p1": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-600_ctau-0p1mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-600_ctau-0p1mm_Tree_v35-4DxyMin/260925_191405/StopStopbarTo2Dbar2D_M-600_ctau-0p1mm_100kEvts_v2.root"],
              "Stop-M800-cT0p1": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-800_ctau-0p1mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-800_ctau-0p1mm_Tree_v35-4DxyMin/260925_191506/StopStopbarTo2Dbar2D_M-800_ctau-0p1mm_100kEvts_v2.root"],
              "Stop-M200-cT0p3": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-200_ctau-0p3mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-200_ctau-0p3mm_Tree_v35-4DxyMin/260925_191218/StopStopbarTo2Dbar2D_M-200_ctau-0p3mm_100kEvts_v2.root"],
              "Stop-M400-cT0p3": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-400_ctau-0p3mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-400_ctau-0p3mm_Tree_v35-4DxyMin/260925_191316/StopStopbarTo2Dbar2D_M-400_ctau-0p3mm_100kEvts_v2.root"],
              "Stop-M600-cT0p3": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-600_ctau-0p3mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-600_ctau-0p3mm_Tree_v35-4DxyMin/260925_191413/StopStopbarTo2Dbar2D_M-600_ctau-0p3mm_100kEvts_v2.root"],
              "Stop-M800-cT0p3": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-800_ctau-0p3mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-800_ctau-0p3mm_Tree_v35-4DxyMin/260925_191514/StopStopbarTo2Dbar2D_M-800_ctau-0p3mm_100kEvts_v2.root"],
              "Stop-M200-cT0p7": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-200_ctau-0p7mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-200_ctau-0p7mm_Tree_v35-4DxyMin/260925_191226/StopStopbarTo2Dbar2D_M-200_ctau-0p7mm_100kEvts_v2.root"],
              "Stop-M400-cT0p7": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-400_ctau-0p7mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-400_ctau-0p7mm_Tree_v35-4DxyMin/260925_191325/StopStopbarTo2Dbar2D_M-400_ctau-0p7mm_100kEvts_v2.root"],
              "Stop-M600-cT0p7": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-600_ctau-0p7mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-600_ctau-0p7mm_Tree_v35-4DxyMin/260925_191422/StopStopbarTo2Dbar2D_M-600_ctau-0p7mm_100kEvts_v2.root"],
              "Stop-M800-cT0p7": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Dbar2D_M-800_ctau-0p7mm_100kEvts_v2/StopStopbarTo2Dbar2D_M-800_ctau-0p7mm_Tree_v35-4DxyMin/260925_191522/StopStopbarTo2Dbar2D_M-800_ctau-0p7mm_100kEvts_v2.root"],
              "Hto2Sto4D-cT0p1-MS15": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-15_Tree_v35-4DxyMin/260925_185239/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-15.root"],
              "Hto2Sto4D-cT0p1-MS23": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-23_Tree_v35-4DxyMin/260925_185301/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-23.root"],
              "Hto2Sto4D-cT0p1-MS30": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-30_Tree_v35-4DxyMin/260925_185311/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-30.root"],
              "Hto2Sto4D-cT0p1-MS40": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-40_Tree_v35-4DxyMin/260925_185321/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-40.root"],
              "Hto2Sto4D-cT0p1-MS55": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-55_Tree_v35-4DxyMin/260925_185331/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-55.root"],
              "Hto2Sto4D-cT1-MS15": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-15_Tree_v35-4DxyMin/260925_185352/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-15.root"],
              "Hto2Sto4D-cT1-MS23": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-23_Tree_v35-4DxyMin/260925_185414/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-23.root"],
              "Hto2Sto4D-cT1-MS30": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-30_Tree_v35-4DxyMin/260925_185423/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-30.root"],
              "Hto2Sto4D-cT1-MS40": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-40_Tree_v35-4DxyMin/260925_185434/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-40.root"],
              "Hto2Sto4D-cT1-MS55": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-55_Tree_v35-4DxyMin/260925_185444/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-55.root"],
              "Hto2Sto4D-cT10-MS15": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-15_Tree_v35-4DxyMin/260925_185506/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-15.root"],
              "Hto2Sto4D-cT10-MS23": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-23_Tree_v35-4DxyMin/260925_185525/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-23.root"],
              "Hto2Sto4D-cT10-MS30": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-30_Tree_v35-4DxyMin/260925_185536/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-30.root"],
              "Hto2Sto4D-cT10-MS40": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-40_Tree_v35-4DxyMin/260925_185547/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-40.root"],
              "Hto2Sto4D-cT10-MS55": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-55_Tree_v35-4DxyMin/260925_185558/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-55.root"],
             }

'''

signalDict = {
              "Hto2Sto4B-cT0p1-MS55": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-55_Tree_v35-4DxyMin/260925_185659/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-55.root"],
              "Hto2Sto4B-cT1-MS55": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-55_Tree_v35-4DxyMin/260925_185800/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-55.root"],
              "Hto2Sto4B-cT10-MS55": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-55_Tree_v35-4DxyMin/260925_185900/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-55.root"]
}

'''
'''
signalDict = {"Hto2Sto4B-cT0p1-MS15": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-15_Tree_v34-4DxyMin/260901_192335/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-15.root"],
              "Hto2Sto4B-cT0p1-MS23": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-23_Tree_v34-4DxyMin/260901_192357/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-23.root"],
              "Hto2Sto4B-cT0p1-MS30": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-30_Tree_v34-4DxyMin/260901_192407/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-30.root"],
              "Hto2Sto4B-cT0p1-MS40": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-40_Tree_v34-4DxyMin/260901_192424/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-40.root"],
              "Hto2Sto4B-cT0p1-MS55": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-55_Tree_v34-4DxyMin/260901_192434/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-55.root"],
              "Hto2Sto4B-cT1-MS15": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-15_Tree_v34-4DxyMin/260901_192455/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-15.root"],
              "Hto2Sto4B-cT1-MS23": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-23_Tree_v34-4DxyMin/260901_192519/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-23.root"],
              "Hto2Sto4B-cT1-MS30": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-30_Tree_v34-4DxyMin/260901_192529/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-30.root"],
              "Hto2Sto4B-cT1-MS40": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-40_Tree_v34-4DxyMin/260901_192539/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-40.root"],
              "Hto2Sto4B-cT1-MS55": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-55_Tree_v34-4DxyMin/260901_192549/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-55.root"],
              "Hto2Sto4B-cT10-MS15": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-15_Tree_v34-4DxyMin/260901_192611/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-15.root"],
              "Hto2Sto4B-cT10-MS23": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-23_Tree_v34-4DxyMin/260901_192631/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-23.root"],
              "Hto2Sto4B-cT10-MS30": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-30_Tree_v34-4DxyMin/260901_192641/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-30.root"],
              "Hto2Sto4B-cT10-MS40": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-40_Tree_v34-4DxyMin/260901_192651/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-40.root"],
              "Hto2Sto4B-cT10-MS55": ["/eos/cms/store/group/phys_exotica/DVScouting/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-55_Tree_v34-4DxyMin/260901_192701/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-55.root"],
              "StopB-M200-cT1": ["/afs/cern.ch/work/r/rmccarth/private/StopStopbarTo2Bbar2B_M-200_ctau-1mm.root"],
              "StopB-M200-cT3": ["/afs/cern.ch/work/r/rmccarth/private/StopStopbarTo2Bbar2B_M-200_ctau-3mm.root"],
              "StopB-M200-cT10": ["/afs/cern.ch/work/r/rmccarth/private/StopStopbarTo2Bbar2B_M-200_ctau-10mm.root"],
              "StopB-M400-cT1": ["/afs/cern.ch/work/r/rmccarth/private/StopStopbarTo2Bbar2B_M-400_ctau-1mm.root"],
              "StopB-M400-cT3": ["/afs/cern.ch/work/r/rmccarth/private/StopStopbarTo2Bbar2B_M-400_ctau-3mm.root"],
              "StopB-M400-cT10": ["/afs/cern.ch/work/r/rmccarth/private/StopStopbarTo2Bbar2B_M-400_ctau-10mm.root"],
              "StopB-M200-cT0p1": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Bbar2B_M-200_ctau-0p1mm_100kEvts_v1/StopStopbarTo2Bbar2B_M-200_ctau-0p1mm_Tree_v34-4DxyMin/260901_194730/StopStopbarTo2Bbar2B_M-200_ctau-0p1mm_100kEvts_v1.root"],
              "StopB-M200-cT0p3": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Bbar2B_M-200_ctau-0p3mm_100kEvts_v1/StopStopbarTo2Bbar2B_M-200_ctau-0p3mm_Tree_v34-4DxyMin/260901_194740/StopStopbarTo2Bbar2B_M-200_ctau-0p3mm_100kEvts_v1.root"],
              "StopB-M200-cT0p7": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Bbar2B_M-200_ctau-0p7mm_100kEvts_v1/StopStopbarTo2Bbar2B_M-200_ctau-0p7mm_Tree_v34-4DxyMin/260901_194750/StopStopbarTo2Bbar2B_M-200_ctau-0p7mm_100kEvts_v1.root"],
              "StopB-M400-cT0p1": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Bbar2B_M-400_ctau-0p1mm_100kEvts_v1/StopStopbarTo2Bbar2B_M-400_ctau-0p1mm_Tree_v34-4DxyMin/260901_194810/StopStopbarTo2Bbar2B_M-400_ctau-0p1mm_100kEvts_v1.root"],
              "StopB-M400-cT0p3": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Bbar2B_M-400_ctau-0p3mm_100kEvts_v1/StopStopbarTo2Bbar2B_M-400_ctau-0p3mm_Tree_v34-4DxyMin/260901_194820/StopStopbarTo2Bbar2B_M-400_ctau-0p3mm_100kEvts_v1.root"],
              "StopB-M400-cT0p7": ["/eos/cms/store/group/phys_exotica/DVScouting/StopStopbarTo2Bbar2B_M-400_ctau-0p7mm_100kEvts_v1/StopStopbarTo2Bbar2B_M-400_ctau-0p7mm_Tree_v34-4DxyMin/260901_194830/StopStopbarTo2Bbar2B_M-400_ctau-0p7mm_100kEvts_v1.root"],
}
'''
#Cutflow table script 
bin_namesCustom = ["7Tracks","8Tracks","9Tracks"]
VTX_X, VTX_Y, VTX_Z = "scoutVert_x", "scoutVert_y", "scoutVert_z"
BS_X,  BS_Y,  BS_Z  = "beamspot_x", "beamspot_y", "beamspot_z"
TRK_PT, TRK_ETA, TRK_PHI = "vertTrack_pt", "vertTrack_eta", "vertTrack_phi"
TRK_VTXIDX = "vertTrack_iVtx"  # per-track index into scoutVert_* (-1 if unassociated)

# Trees to process: nominal plus JEC variations (key = suffix appended to output keys)
NOMINAL_TREE = "scoutingTree/objectTree"
JEC_TREES = {"_JEC_up":   "scoutingTreeJECup/objectTree",
             "_JEC_down": "scoutingTreeJECdown/objectTree"}

def compute_cosT(batch):
    """cos of the 3D angle between (vertex - beamspot) and the summed momentum
    of the tracks associated to the vertex. Returns a jagged array aligned with scoutVert_*."""
    # Displacement from beamspot (beamspot is per-event, broadcasts over vertices)
    dx = batch[VTX_X]
    dy = batch[VTX_Y]
    nvtx = ak.num(dx, axis=1)

    # Track momenta
    pt, eta, phi = batch[TRK_PT], batch[TRK_ETA], batch[TRK_PHI]
    px, py = pt * np.cos(phi), pt * np.sin(phi)

    # Map each track to a global vertex index (flattened over events), then sum per vertex
    vidx = ak.values_astype(batch[TRK_VTXIDX], np.int64)
    good = (vidx >= 0) & (vidx < nvtx)
    nvtx_np = ak.to_numpy(nvtx)
    offsets = ak.Array(np.cumsum(nvtx_np) - nvtx_np)  # first global vertex index per event
    gidx = ak.to_numpy(ak.flatten((vidx + offsets)[good]))
    ntot = int(nvtx_np.sum())

    def sum_per_vertex(p):
        flat = np.bincount(gidx, weights=ak.to_numpy(ak.flatten(p[good])), minlength=ntot)
        return ak.unflatten(flat, nvtx)

    Px, Py = sum_per_vertex(px), sum_per_vertex(py)

    dot = dx * Px + dy * Py
    norm = np.sqrt(dx**2 + dy**2) * np.sqrt(Px**2 + Py**2)
    # Sentinel -2 for degenerate vertices (no associated tracks / zero displacement)
    return ak.where(norm > 0, dot / ak.where(norm > 0, norm, 1.0), -2.0)

def process_cutflows(args):
    """ Process a single tree of a ROOT file in chunks using uproot.iterate() """
    rootFile, sample, treeName, suffix = args
    process = sample + suffix  # output keys tagged by tree variation ("" for nominal)
    print(f"Processing {rootFile} [{treeName}]")

    output = {}
    with uproot.open(rootFile) as file:
        output[process] = {}
        output[process+"_PU_up"] = {}
        output[process+"_PU_down"] = {}
        output[process+"_Trigger_up"] = {}
        output[process+"_Trigger_down"] = {}
        output[process+"_squared"] = {}
        output[process+"_PU_up_squared"] = {}
        output[process+"_PU_down_squared"] = {}
        output[process+"_nEvents"] = {}
        tree = file[treeName]
        
        # Select only necessary branches to load
        #branches = ["uncorrectedWeight","scoutVert_dBV","scoutVert_dBVErr", "scoutVert_nTracks","weight","scoutVert_cosT","scoutVert_chi2","weight_PU_BCDEFGHI_nominal","weight_PU_BCDEFGHI_up","weight_PU_BCDEFGHI_down","jet_pt","scoutVert_pMag","weight_trigger_nominal","weight_trigger_up","weight_trigger_down","hltHTProxy"]
        branches = ["uncorrectedWeight","scoutVert_dBV","scoutVert_dBVErr", "scoutVert_nTracks","weight","scoutVert_cosT","scoutVert_chi2","weight_PU_BCDEFGHI_nominal","weight_PU_BCDEFGHI_up","weight_PU_BCDEFGHI_down","jet_pt","scoutVert_pMag","weight_trigger_nominal","weight_trigger_up","weight_trigger_down","hltHTProxy", VTX_X, VTX_Y, VTX_Z, BS_X, BS_Y, BS_Z, TRK_PT, TRK_ETA, TRK_PHI, TRK_VTXIDX]

        # Iterate over the tree in chunks (adjust step_size to control memory usage)
        '''
        weightSum = [[0,0,0,0]]*len(bin_namesCustom)
        weightSumSquared = [[0,0,0,0]] * len(bin_namesCustom)
        weightSum_PU_up = [[0,0,0,0]]*len(bin_namesCustom)
        weightSumSquared_PU_up = [[0,0,0,0]] * len(bin_namesCustom)
        weightSum_PU_down = [[0,0,0,0]]*len(bin_namesCustom)
        weightSumSquared_PU_down = [[0,0,0,0]] * len(bin_namesCustom)
        weightSum_Trigger_up = [[0,0,0,0]]*len(bin_namesCustom)
        weightSum_Trigger_down = [[0,0,0,0]]*len(bin_namesCustom)
        numEvents = [[0,0,0,0]] * len(bin_namesCustom)
        '''
        weightSum              = [[0,0,0,0] for _ in range(len(bin_namesCustom))]
        weightSumSquared       = [[0,0,0,0] for _ in range(len(bin_namesCustom))]
        weightSum_PU_up        = [[0,0,0,0] for _ in range(len(bin_namesCustom))]
        weightSumSquared_PU_up = [[0,0,0,0] for _ in range(len(bin_namesCustom))]
        weightSum_PU_down      = [[0,0,0,0] for _ in range(len(bin_namesCustom))]
        weightSumSquared_PU_down = [[0,0,0,0] for _ in range(len(bin_namesCustom))]
        weightSum_Trigger_up   = [[0,0,0,0] for _ in range(len(bin_namesCustom))]
        weightSum_Trigger_down = [[0,0,0,0] for _ in range(len(bin_namesCustom))]
        numEvents              = [[0,0,0,0] for _ in range(len(bin_namesCustom))]
        for batch in tree.iterate(branches, library="ak", step_size=100000):  
            #weights = batch["weight"]  # event weights
            weights = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] #* batch["weight_trigger_nominal"] #* (114.44/108.96) #temp to correct for official 2024 lumi
            weights_PU_up = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_up"] #* batch["weight_trigger_nominal"]#* (114.44/108.96)
            weights_PU_down = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_down"] #* batch["weight_trigger_nominal"]#* (114.44/108.96)
            weights_Trigger_up = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] #* batch["weight_trigger_up"]
            weights_Trigger_down = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] #* batch["weight_trigger_down"]
            data = batch["scoutVert_dBV"]
            ntracks = batch["scoutVert_nTracks"]
            #cosT = batch["scoutVert_cosT"]
            cosT = compute_cosT(batch)
            dBVErr = batch["scoutVert_dBVErr"] 
            chi2 = batch["scoutVert_chi2"]
            jetpt = batch["jet_pt"]
            njet = ak.num(jetpt,axis=1)
            ht = batch["hltHTProxy"]
            #ht = ak.sum(jetpt,axis=-1)
            #jetMask = (jetpt>30)
            #nJetsAboveCut = ak.sum(jetMask,axis=1)
            mask_D = (data<2.0) & (cosT>0) & (dBVErr<0.005) & (chi2<2.5)
            mask_A = (data<2.0) & (cosT<0) & (dBVErr<0.005) & (chi2>2.5)
            mask_B = (data<2.0) & (cosT<0) & (dBVErr<0.005) & (chi2<2.5)
            mask_C = (data<2.0) & (cosT>0) & (dBVErr<0.005) & (chi2>2.5)
            regionMasks = {"A": mask_A, "B": mask_B, "C": mask_C, "D": mask_D}
            regionIndex = {"A": 0, "B": 1, "C": 2, "D": 3}  # column order in the weightSum arrays
            priority = ["D", "C", "B", "A"]
            eventSel = (ht > 400) & (njet > 2)
            displaced = (data >= 0.01)
            trackBinMasks = [(ntracks == 7), (ntracks == 8), (ntracks > 8)]

            # (sum array, sum-of-squares array or None, per-event weights)
            weightVariants = [
                (weightSum,              weightSumSquared,         weights),
                (weightSum_PU_up,        weightSumSquared_PU_up,   weights_PU_up),
                (weightSum_PU_down,      weightSumSquared_PU_down, weights_PU_down),
                (weightSum_Trigger_up,   None,                     weights_Trigger_up),
                (weightSum_Trigger_down, None,                     weights_Trigger_down),
            ]

            for k, trackMask in enumerate(trackBinMasks):
                taken = np.zeros(len(eventSel), dtype=bool)  # events already assigned in this track bin
                for region in priority:
                    vtxPass = regionMasks[region] & trackMask & displaced
                    inRegion = ak.to_numpy(ak.any(vtxPass, axis=1) & eventSel) & ~taken
                    taken |= inRegion

                    l = regionIndex[region]
                    for sumArr, sumSqArr, w in weightVariants:
                        wSel = w[inRegion]
                        sumArr[k][l] += ak.sum(wSel)
                        if sumSqArr is not None:
                            sumSqArr[k][l] += ak.sum(wSel**2)
                    numEvents[k][l] += int(np.sum(inRegion))
        for i in range(len(bin_namesCustom)):
            output[process][bin_namesCustom[i]] = weightSum[i]
            output[process+"_squared"][bin_namesCustom[i]] = weightSumSquared[i]
            output[process+"_PU_up"][bin_namesCustom[i]] = weightSum_PU_up[i]
            output[process+"_PU_up_squared"][bin_namesCustom[i]] = weightSumSquared_PU_up[i]
            output[process+"_PU_down"][bin_namesCustom[i]] = weightSum_PU_down[i]
            output[process+"_PU_down_squared"][bin_namesCustom[i]] = weightSumSquared_PU_down[i]
            output[process+"_Trigger_up"][bin_namesCustom[i]] = weightSum_Trigger_up[i]
            output[process+"_Trigger_down"][bin_namesCustom[i]] = weightSum_Trigger_down[i]
            output[process+"_nEvents"][bin_namesCustom[i]] = numEvents[i]
        
    return output

# **Parallel Processing Using ProcessPoolExecutor**
def parallel_processing(files_dict):
    """ Process all ROOT files (nominal + JEC trees) in parallel and aggregate results """
    results = {}
    trees = [("", NOMINAL_TREE)] + list(JEC_TREES.items())
    with ProcessPoolExecutor(max_workers=16) as executor:  # Adjust max_workers based on CPU cores
        futures = {executor.submit(process_cutflows, (f, p, t, s)): (f, p, t, s)
                   for p, files in files_dict.items() for f in files for s, t in trees}

        for future in as_completed(futures):
            result = future.result()
            for process in result:
                if process not in results:
                    results[process] = result[process]
                else:
                    for cut in result[process]:
                        results[process][cut] = results[process].get(cut, 0) + result[process][cut]

    return results

dict = signalDict
customWeights = parallel_processing(dict)

firstProcess = True
weightSumDict = {}
weightSquaredSumDict = {}
genWeightSumDict = {}
for process, rootFiles in dict.items():
    firstFile = True
    weightSum = []
    weightSquaredSum = []
    genWeightSum = 0
    for rootFile in rootFiles:
        f = ROOT.TFile.Open(rootFile, "READ")
        h_weightsSkim = f.Get("triggerFilter/weightsSkimLUMCorrected")
        h_weightsSquaredSkim = f.Get("triggerFilter/weightsSquaredSkimLUMCorrected")
        h_genWeights = f.Get("triggerFilter/genWeightsSkim")
        h_weights = f.Get("scoutingTree/weightsLUMCorrected")
        h_weightsSquared = f.Get("scoutingTree/weightsSquaredLUMCorrected")
        
        # Extract content
        n_bins = 0 #temp while making simplified cutflow table
        #n_bins = h_weights.GetNbinsX()
        weights = np.array([h_weights.GetBinContent(i) for i in range(3, n_bins)]) #temp since there are redundant cuts in tree maker, normally would go from 1 to n_bins+1
        bin_names = np.array([h_weights.GetXaxis().GetLabels().At(i-1).GetName() for i in range(3, n_bins)])
        weightsSquared = np.array([h_weightsSquared.GetBinContent(i) for i in range(3, n_bins)])
        
        n_binsSkim = h_weightsSkim.GetNbinsX() 
        weightsSkim = np.array([h_weightsSkim.GetBinContent(i) for i in range(1, n_binsSkim + 1)]) #* currentLimit #* (114.44/108.96)
        bin_namesSkim = np.array([h_weightsSkim.GetXaxis().GetLabels().At(i-1).GetName() for i in range(1, n_binsSkim + 1)]) 
        weightsSquaredSkim = np.array([h_weightsSquaredSkim.GetBinContent(i) for i in range(1, n_binsSkim + 1)]) #* (currentLimit**2) #* ((114.44/108.96)**2)
        genWeights = np.array([h_genWeights.GetBinContent(i) for i in range(1, n_binsSkim + 1)])
        
        if(firstFile and firstProcess):
            for name in np.concatenate((bin_namesSkim,bin_names)):
                weightSum.append(0)
                weightSquaredSum.append(0)
            firstFile = False
        elif(firstFile):
            for name in np.concatenate((bin_namesSkim,bin_names)):
                weightSum.append(0)
                weightSquaredSum.append(0)
            firstFile = False

        genWeightSum += genWeights[0]
        for i in range(len(weightsSkim)):
            weightSum[i] += weightsSkim[i]
            weightSquaredSum[i] += weightsSquaredSkim[i]
        for i in range(len(weights)):
            weightSum[i+len(weightsSkim)] += weights[i]
            weightSquaredSum[i+len(weightsSkim)] += weightsSquared[i]
    firstProcess = False
    weightSumDict[process] = weightSum
    weightSquaredSumDict[process] = weightSquaredSum
    genWeightSumDict[process] = genWeightSum
      
#Combining Background Subprocesses and Reweighting Events
for process in dict.keys():
    for i in range(len(weightSumDict[process])):
        weightSumDict[process][i] = weightSumDict[process][i] / genWeightSumDict[process] 
        weightSquaredSumDict[process][i] = weightSquaredSumDict[process][i] / (genWeightSumDict[process]**2) 
    for cut in customWeights[process].keys():
        customWeights[process][cut] = customWeights[process][cut] / genWeightSumDict[process] 
        customWeights[process+"_squared"][cut] = customWeights[process+"_squared"][cut] / (genWeightSumDict[process]**2) 
        customWeights[process+"_PU_up"][cut] = customWeights[process+"_PU_up"][cut] / genWeightSumDict[process] 
        customWeights[process+"_PU_up_squared"][cut] = customWeights[process+"_PU_up_squared"][cut] / (genWeightSumDict[process]**2)
        customWeights[process+"_PU_down"][cut] = customWeights[process+"_PU_down"][cut] / genWeightSumDict[process] 
        customWeights[process+"_PU_down_squared"][cut] = customWeights[process+"_PU_down_squared"][cut] / (genWeightSumDict[process]**2) 
        customWeights[process+"_Trigger_up"][cut] = customWeights[process+"_Trigger_up"][cut] / genWeightSumDict[process] 
        customWeights[process+"_Trigger_down"][cut] = customWeights[process+"_Trigger_down"][cut] / genWeightSumDict[process] 
        for s in JEC_TREES:
            customWeights[process+s][cut] = customWeights[process+s][cut] / genWeightSumDict[process]

stealthRawEventsDict = {}
stealthWeightedEventsDict = {}
stealthWeightedEventsDict_PU_up = {}
stealthWeightedEventsDict_PU_down = {}
stealthWeightedEventsDict_Trigger_up = {}
stealthWeightedEventsDict_Trigger_down = {}
stealthWeightedEventsDict_JEC_up = {}
stealthWeightedEventsDict_JEC_down = {}
for process in dict.keys():
    stealthRawEventsArray = []
    stealthWeightedEventsArray = []
    stealthWeightedEventsArray_PU_up = []
    stealthWeightedEventsArray_PU_down = []
    stealthWeightedEventsArray_Trigger_up = []
    stealthWeightedEventsArray_Trigger_down = []
    stealthWeightedEventsArray_JEC_up = []
    stealthWeightedEventsArray_JEC_down = []
    for i in range(3):
        stealthRawEventsArray.append(customWeights[process+'_nEvents'][bin_namesCustom[i]])
        nominal = customWeights[process][bin_namesCustom[i]]
        pu_up = customWeights[process+'_PU_up'][bin_namesCustom[i]]
        pu_down = customWeights[process+'_PU_down'][bin_namesCustom[i]]
        print(nominal)
        if("Hto2S" in process):
            stealthWeightedEventsArray.append(ak.round(nominal*(52.23/8),4))
            #stealthWeightedEventsArray.append(ak.round(nominal*(1/8),4))
        else:
            stealthWeightedEventsArray.append(ak.round(nominal,4))
        stealthWeightedEventsArray_PU_up.append(ak.round(1+((pu_up-nominal)/nominal),4))
        stealthWeightedEventsArray_PU_down.append(ak.round(1+((pu_down-nominal)/nominal),4))
        trigger_up = customWeights[process+'_Trigger_up'][bin_namesCustom[i]]
        trigger_down = customWeights[process+'_Trigger_down'][bin_namesCustom[i]]
        stealthWeightedEventsArray_Trigger_up.append(ak.round(1+((trigger_up-nominal)/nominal),4))
        stealthWeightedEventsArray_Trigger_down.append(ak.round(1+((trigger_down-nominal)/nominal),4))
        jec_up = customWeights[process+'_JEC_up'][bin_namesCustom[i]]
        jec_down = customWeights[process+'_JEC_down'][bin_namesCustom[i]]
        stealthWeightedEventsArray_JEC_up.append(ak.round(1+((jec_up-nominal)/nominal),4))
        stealthWeightedEventsArray_JEC_down.append(ak.round(1+((jec_down-nominal)/nominal),4))
    stealthRawEventsDict[process] = stealthRawEventsArray
    stealthWeightedEventsDict[process] = stealthWeightedEventsArray
    stealthWeightedEventsDict_PU_up[process] = stealthWeightedEventsArray_PU_up
    stealthWeightedEventsDict_PU_down[process] = stealthWeightedEventsArray_PU_down
    stealthWeightedEventsDict_Trigger_up[process] = stealthWeightedEventsArray_Trigger_up
    stealthWeightedEventsDict_Trigger_down[process] = stealthWeightedEventsArray_Trigger_down
    stealthWeightedEventsDict_JEC_up[process] = stealthWeightedEventsArray_JEC_up
    stealthWeightedEventsDict_JEC_down[process] = stealthWeightedEventsArray_JEC_down

#Backgrounds without HT cut
#bkgEvents_A = 11.0
#bkgEvents_B = 55.0
#bkgEvents_C = 12.0
#bkgEvents_A_8 = 34.0
#bkgEvents_B_8 = 98.0
#bkgEvents_C_8 = 48.0
#bkgEvents_A_7 =  224.0
#bkgEvents_B_7 =  325.0
#bkgEvents_C_7 =  226.0

# 400 L1 HT cut backgrounds
#bkgEvents_A = 9.0
#bkgEvents_B = 40.0
#bkgEvents_C = 7.0
#bkgEvents_A_8 = 17.0
#bkgEvents_B_8 = 61.0
#bkgEvents_C_8 = 29.0
#bkgEvents_A_7 = 152.0
#bkgEvents_B_7 = 210.0
#bkgEvents_C_7 = 147.0

# 600 L1 HT cut backgrounds
#bkgEvents_A = 5
#bkgEvents_B = 24
#bkgEvents_C = 6
#bkgEvents_A_8 =11 
#bkgEvents_B_8 = 33
#bkgEvents_C_8 = 21
#bkgEvents_A_7 = 85
#bkgEvents_B_7 = 112
#bkgEvents_C_7 = 77

# 400 Proxy HT cut backgrounds
#bkgEvents_A = 8
#bkgEvents_B = 30
#bkgEvents_C = 6
#bkgEvents_A_8 = 16 
#bkgEvents_B_8 = 43
#bkgEvents_C_8 = 24
#bkgEvents_A_7 = 129
#bkgEvents_B_7 = 166
#bkgEvents_C_7 = 120

# v35 Updated JEC 400 Proxy HT cut backgrounds
bkgEvents_A = 8
bkgEvents_A_Range = round(5*np.sqrt(bkgEvents_A))
bkgEvents_A_Min = 0 if (bkgEvents_A_Range>bkgEvents_A) else (bkgEvents_A-bkgEvents_A_Range)
bkgEvents_A_Max = bkgEvents_A+bkgEvents_A_Range
bkgEvents_B = 30
bkgEvents_B_Range = round(5*np.sqrt(bkgEvents_B))
bkgEvents_B_Min = 0 if (bkgEvents_B_Range>bkgEvents_B) else (bkgEvents_B-bkgEvents_B_Range)
bkgEvents_B_Max = bkgEvents_B+bkgEvents_B_Range
bkgEvents_C = 7
bkgEvents_C_Range = round(5*np.sqrt(bkgEvents_C))
bkgEvents_C_Min = 0 if (bkgEvents_C_Range>bkgEvents_C) else (bkgEvents_C-bkgEvents_C_Range)
bkgEvents_C_Max = bkgEvents_C+bkgEvents_C_Range
bkgEvents_A_8 = 16
bkgEvents_A_8_Range = round(5*np.sqrt(bkgEvents_A_8))
bkgEvents_A_8_Min = 0 if (bkgEvents_A_8_Range>bkgEvents_A_8) else (bkgEvents_A_8-bkgEvents_A_8_Range)
bkgEvents_A_8_Max = bkgEvents_A_8+bkgEvents_A_8_Range
bkgEvents_B_8 = 44
bkgEvents_B_8_Range = round(5*np.sqrt(bkgEvents_B_8))
bkgEvents_B_8_Min = 0 if (bkgEvents_B_8_Range>bkgEvents_B_8) else (bkgEvents_B_8-bkgEvents_B_8_Range)
bkgEvents_B_8_Max = bkgEvents_B_8+bkgEvents_B_8_Range
bkgEvents_C_8 = 23
bkgEvents_C_8_Range = round(5*np.sqrt(bkgEvents_C_8))
bkgEvents_C_8_Min = 0 if (bkgEvents_C_8_Range>bkgEvents_C_8) else (bkgEvents_C_8-bkgEvents_C_8_Range)
bkgEvents_C_8_Max = bkgEvents_C_8+bkgEvents_C_8_Range
bkgEvents_A_7 = 131
bkgEvents_A_7_Range = round(5*np.sqrt(bkgEvents_A_7))
bkgEvents_A_7_Min = 0 if (bkgEvents_A_7_Range>bkgEvents_A_7) else (bkgEvents_A_7-bkgEvents_A_7_Range)
bkgEvents_A_7_Max = bkgEvents_A_7+bkgEvents_A_7_Range
bkgEvents_B_7 = 167
bkgEvents_B_7_Range = round(5*np.sqrt(bkgEvents_B_7))
bkgEvents_B_7_Min = 0 if (bkgEvents_B_7_Range>bkgEvents_B_7) else (bkgEvents_B_7-bkgEvents_B_7_Range)
bkgEvents_B_7_Max = bkgEvents_B_7+bkgEvents_B_7_Range
bkgEvents_C_7 = 120
bkgEvents_C_7_Range = round(5*np.sqrt(bkgEvents_C_7))
bkgEvents_C_7_Min = 0 if (bkgEvents_C_7_Range>bkgEvents_C_7) else (bkgEvents_C_7-bkgEvents_C_7_Range)
bkgEvents_C_7_Max = bkgEvents_C_7+bkgEvents_C_7_Range

for process in dict.keys():
    print("in datacard loop")
    w = [ [0]*4 for index in range(3)]
    rawEventsArray = [ [0]*4 for index in range(3)]
    pu = [ [0]*4 for index in range(3)] #pileup up array
    pd = [ [0]*4 for index in range(3)] #pileup down array
    tu = [ [0]*4 for index in range(3)] #trigger up array
    td = [ [0]*4 for index in range(3)] #trigger down array
    ju = [ [0]*4 for index in range(3)] #JEC up array
    jd = [ [0]*4 for index in range(3)] #JEC down array
    rateArray = [ [0]*4 for index in range(3)]
    for k in range(3): #track multiplicity bin
        for l in range(4): #ABCD region
            w[k][l] = stealthWeightedEventsDict[process][k][l] # weighted events array
            rawEventsArray[k][l] = stealthRawEventsDict[process][k][l]
            pu[k][l] = stealthWeightedEventsDict_PU_up[process][k][l]
            pd[k][l] = stealthWeightedEventsDict_PU_down[process][k][l]
            tu[k][l] = 1#stealthWeightedEventsDict_Trigger_up[process][k][l]
            td[k][l] = 1#stealthWeightedEventsDict_Trigger_down[process][k][l]
            ju[k][l] = stealthWeightedEventsDict_JEC_up[process][k][l]
            jd[k][l] = stealthWeightedEventsDict_JEC_down[process][k][l]
            
            if(pu[k][l]==0):
                pu[k][l] = 0.01
            if(pd[k][l]==0):
                pd[k][l] = 0.01
            if(ju[k][l]==0):
                ju[k][l] = 0.01
            if(jd[k][l]==0):
                jd[k][l] = 0.01
            
            if(rawEventsArray[k][l]!=0):
                rateArray[k][l] = round(w[k][l]/rawEventsArray[k][l],7)
            else:
                rateArray[k][l] = 0

    fileString = f'''\
imax    12 number of bins \n
jmax    * number of processes minus 1 \n
kmax    * number of nuisance parameters \n
-------------------------------------------------------------------------------- \n
-------------------------------------------------------------------------------- \n
bin          CR_A7 CR_B7 CR_C7 SR7 CR_A8 CR_B8 CR_C8 SR8 CR_A9 CR_B9 CR_C9 SR9 \n
observation  {bkgEvents_A_7} {bkgEvents_B_7} {bkgEvents_C_7} 0 {bkgEvents_A_8} {bkgEvents_B_8} {bkgEvents_C_8} 0 {bkgEvents_A} {bkgEvents_B} {bkgEvents_C} 0 \n            
-------------------------------------------------------------------------------- \n
bin          CR_A7 CR_B7 CR_C7 SR7 CR_A8 CR_B8 CR_C8 SR8 CR_A9 CR_B9 CR_C9 SR9 CR_A7 CR_B7 CR_C7 SR7 CR_A8 CR_B8 CR_C8 SR8 CR_A9 CR_B9 CR_C9 SR9 \n
process      bkg bkg bkg bkg bkg bkg bkg bkg bkg bkg bkg bkg sig sig sig sig sig sig sig sig sig sig sig sig \n
process      1   1   1   1   1   1   1   1   1   1   1   1   0   0   0   0   0   0   0   0   0   0   0   0 \n
rate         1   1   1   1   1   1   1   1   1   1   1   1   {w[0][0]} {w[0][1]} {w[0][2]} {w[0][3]} {w[1][0]} {w[1][1]} {w[1][2]} {w[1][3]} {w[2][0]} {w[2][1]} {w[2][2]} {w[2][3]}\n        
-------------------------------------------------------------------------------- \n
CMS_PU_2024 lnN - - - - - - - - - - - - {pd[0][0]}/{pu[0][0]} {pd[0][1]}/{pu[0][1]} {pd[0][2]}/{pu[0][2]} {pd[0][3]}/{pu[0][3]} {pd[1][0]}/{pu[1][0]} {pd[1][1]}/{pu[1][1]} {pd[1][2]}/{pu[1][2]} {pd[1][3]}/{pu[1][3]} {pd[2][0]}/{pu[2][0]} {pd[2][1]}/{pu[2][1]} {pd[2][2]}/{pu[2][2]} {pd[2][3]}/{pu[2][3]} \n
lumi_2024 lnN - - - - - - - - - - - - 1.016 1.016 1.016 1.016 1.016 1.016 1.016 1.016 1.016 1.016 1.016 1.016 \n     
CMS_JEC_2024 lnN - - - - - - - - - - - - {jd[0][0]}/{ju[0][0]} {jd[0][1]}/{ju[0][1]} {jd[0][2]}/{ju[0][2]} {jd[0][3]}/{ju[0][3]} {jd[1][0]}/{ju[1][0]} {jd[1][1]}/{ju[1][1]} {jd[1][2]}/{ju[1][2]} {jd[1][3]}/{ju[1][3]} {jd[2][0]}/{ju[2][0]} {jd[2][1]}/{ju[2][1]} {jd[2][2]}/{ju[2][2]} {jd[2][3]}/{ju[2][3]} \n
bkg_ABCD_closure lnN - - - 1.10 - - - 1.10 - - - 1.10 - - - - - - - - - - - - \n
sig_stat_A_7       gmN {rawEventsArray[0][0]} - - - - - - - - - - - - {rateArray[0][0]} - - - - - - - - - - - \n
sig_stat_B_7       gmN {rawEventsArray[0][1]} - - - - - - - - - - - - - {rateArray[0][1]} - - - - - - - - - - \n
sig_stat_C_7       gmN {rawEventsArray[0][2]} - - - - - - - - - - - - - - {rateArray[0][2]} - - - - - - - - - \n
sig_stat_D_7       gmN {rawEventsArray[0][3]} - - - - - - - - - - - - - - - {rateArray[0][3]} - - - - - - - - \n
sig_stat_A_8       gmN {rawEventsArray[1][0]} - - - - - - - - - - - - - - - - {rateArray[1][0]} - - - - - - - \n
sig_stat_B_8       gmN {rawEventsArray[1][1]} - - - - - - - - - - - - - - - - - {rateArray[1][1]} - - - - - - \n
sig_stat_C_8       gmN {rawEventsArray[1][2]} - - - - - - - - - - - - - - - - - - {rateArray[1][2]} - - - - - \n
sig_stat_D_8       gmN {rawEventsArray[1][3]} - - - - - - - - - - - - - - - - - - - {rateArray[1][3]} - - - - \n
sig_stat_A_9       gmN {rawEventsArray[2][0]} - - - - - - - - - - - - - - - - - - - - {rateArray[2][0]} - - - \n
sig_stat_B_9       gmN {rawEventsArray[2][1]} - - - - - - - - - - - - - - - - - - - - - {rateArray[2][1]} - - \n
sig_stat_C_9       gmN {rawEventsArray[2][2]} - - - - - - - - - - - - - - - - - - - - - - {rateArray[2][2]} - \n
sig_stat_D_9       gmN {rawEventsArray[2][3]} - - - - - - - - - - - - - - - - - - - - - - - {rateArray[2][3]} \n
alpha rateParam CR_A9 bkg {bkgEvents_A} [{bkgEvents_A_Min},{bkgEvents_A_Max}] 
beta rateParam CR_B9 bkg {bkgEvents_B} [{bkgEvents_B_Min},{bkgEvents_B_Max}] 
gamma rateParam CR_C9 bkg {bkgEvents_C} [{bkgEvents_C_Min},{bkgEvents_C_Max}] 
pred_D rateParam SR9 bkg @0*@1/@2 beta,gamma,alpha
alpha7 rateParam CR_A7 bkg {bkgEvents_A_7} [{bkgEvents_A_7_Min},{bkgEvents_A_7_Max}] 
beta7 rateParam CR_B7 bkg {bkgEvents_B_7} [{bkgEvents_B_7_Min},{bkgEvents_B_7_Max}] 
gamma7 rateParam CR_C7 bkg {bkgEvents_C_7} [{bkgEvents_C_7_Min},{bkgEvents_C_7_Max}] 
pred_D7 rateParam SR7 bkg @0*@1/@2 beta7,gamma7,alpha7
alpha8 rateParam CR_A8 bkg {bkgEvents_A_8} [{bkgEvents_A_8_Min},{bkgEvents_A_8_Max}] 
beta8 rateParam CR_B8 bkg {bkgEvents_B_8} [{bkgEvents_B_8_Min},{bkgEvents_B_8_Max}] 
gamma8 rateParam CR_C8 bkg {bkgEvents_C_8} [{bkgEvents_C_8_Min},{bkgEvents_C_8_Max}] 
pred_D8 rateParam SR8 bkg @0*@1/@2 beta8,gamma8,alpha8
'''
    with open(f'datacard_{process}.txt', 'w') as output:
        fileString = fileString.replace("nan/nan","-")
        output.write(fileString)
