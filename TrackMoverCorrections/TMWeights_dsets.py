SignalVersion = '19'
TMVersion = '19'

## Signal datasets ##
signalDict = {}

#Higgs signal
masses = ['15', '23', '30', '40', '55']
lifetimes = ['10']

for mass in masses:
    for ctau in lifetimes:
        signalDict[f'Higgs_{mass}_{ctau}'] = f'Signal/GluGluH-Hto2Sto4D_Par-ctauS-{ctau}-MH-125-MS-{mass}_TuneCP5_13p6TeV_powheg-pythia8/Higgs_mS-{mass}_ctau-{ctau}_v{SignalVersion}/Signal.root'

#RPV SUSY Signal
masses = ['200', '400', '600', '800']
lifetimes = ['10']

for mass in masses:
    for ctau in lifetimes:
        signalDict[f'Stop_{mass}_{ctau}'] = f'Signal/StopStopbarTo2Dbar2D_M-{mass}_CTau-{ctau}mm_Summer24_100k_v2/Stop_mStop-{mass}_ctau-{ctau}_v{SignalVersion}/Signal.root'
        signalDict[f'StopToB_{mass}_{ctau}'] = f'Signal/StopStopbarTo2Bbar2B_M-{mass}_ctau-{ctau}mm_100kEvts_v1/StopToB_mStop-{mass}_ctau-{ctau}_v19/Signal.root'

#Stealth SUSY boosted signal
masses = ['300', '500', '700', '900']
lifetimes = ['10']
models = ['SYY', 'SHH']
#
for mass in masses:
    for ctau in lifetimes:
        for model in models:
            signalDict[f'Stealth{model}_{mass}_100_{ctau}'] = f'Signal/Stealth{model}_mStop-{mass}_mSo-100_ctau-{ctau}mm100kEvts_v2/Stealth{model}_mStop-{mass}_mSo-100_ctau-{ctau}Resubmit_v19/Signal.root'

#Stealth SUSY resolved signal
masses = [325, 500, 700, 900]
lifetimes = ['10']
models = ['SYY', 'SHH']
#
for mass in masses:
    mSo = str(mass - 225)
    massString = str(mass)
    for ctau in lifetimes:
        for model in models:
            signalDict[f'Stealth{model}_{massString}_{mSo}_{ctau}'] = f'Signal/Stealth{model}_mStop-{massString}_mSo-{mSo}_ctau-{ctau}mm100kEvts_v2/Stealth{model}_mStop-{mass}_mSo-{mSo}_ctau-{ctau}Resubmit_v19/Signal.root'


## Data ##
dataDict = {}

Eras = ['2024C', '2024D', '2024E', '2024F','2024G', '2024H', '2024I']
for Era in Eras:
    dataDict[Era] = f'TMData/TrackMover_ScoutingData_{Era}_v{TMVersion}/TMData.root'

## Background MC ##
backgroundDict = {}

QCD_bins = ['100to200', '200to400', '400to600', '600to800', '800to1000', '1000to1200', '1200to1500', '1500to2000', '2000']
for QCD_bin in QCD_bins:
    backgroundDict[f'QCD-{QCD_bin}'] = f'TMBackground/QCD-4Jets_Bin-HT-{QCD_bin}_TuneCP5_13p6TeV_madgraphMLM-pythia8/TrackMover_ScoutingBG2024_QCD_HT-{QCD_bin}_v{TMVersion}/TMBackground.root'

backgroundDict[f'TTBar_Hadronic'] = f'TMBackground/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8/TrackMover_ScoutingBG2024_TTBar_FullyHadronic_v{TMVersion}/TMBackground.root'
backgroundDict[f'TTBar_SemiLeptonic'] = f'TMBackground/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/TrackMover_ScoutingBG2024_TTBar_SemiLeptonic_v{TMVersion}/TMBackground.root'