#Dataset name and cross section in fb dictionary
inputDatasets = {
                 "/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 762100*0.106,
                 "/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 762100*0.439,
                 "/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 762100*0.455,
                 "/WToLNu_0J_v1/brlopesd-WToLNu_0J_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 55760000,
                 "/WtoLNu-2Jets_Bin-1J-PTLNu-40to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v3/MINIAODSIM": 4211000,
                 "/WtoLNu-2Jets_Bin-1J-PTLNu-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v3/MINIAODSIM": 342300,
                 "/WtoLNu-2Jets_Bin-1J-PTLNu-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 21840,
                 "/WtoLNu-2Jets_Bin-1J-PTLNu-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 684.5,
                 "/WtoLNu-2Jets_Bin-1J-PTLNu-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 77.53,
                 "/WtoLNu-2Jets_Bin-2J-PTLNu-40to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v3/MINIAODSIM": 1581000,
                 "/WtoLNu-2Jets_Bin-2J-PTLNu-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v3/MINIAODSIM": 411100,
                 "/WtoLNu-2Jets_Bin-2J-PTLNu-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 53590,
                 "/WtoLNu-2Jets_Bin-2J-PTLNu-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 3099,
                 "/WtoLNu-2Jets_Bin-2J-PTLNu-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 525.9,
                 "/WZ_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 29100,
                 "/WW_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 80230,
                 "/ZZ_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 12750,
                 "/DYto2E_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 6744000,
                 "/DYto2E_Bin-MLL-50to120_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 2219000,
                 "/DYto2E_Bin-MLL-120to200_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 21650,
                 "/DYto2E_Bin-MLL-200to400_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 3058,
                 "/DYto2E_Bin-MLL-400to800_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 269.1,
                 "/DYto2E_Bin-MLL-800to1500_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 19.15,
                 "/DYto2E_Bin-MLL-1500to2500_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 1.111,
                 "/DYto2E_Bin-MLL-2500to4000_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 0.05949,
                 "/DYto2E_Bin-MLL-4000to6000_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 0.001558,
                 "/DYto2E_Bin-MLL-6000_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": .00003519,
                 "/DYto2Mu_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 6744000,
                 "/DYto2Mu_Bin-MLL-50to120_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 2219000,
                 "/DYto2Mu_Bin-MLL-120to200_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 21650,
                 "/DYto2Mu_Bin-MLL-200to400_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 3058,
                 "/DYto2Mu_Bin-MLL-400to800_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 269.1,
                 "/DYto2Mu_Bin-MLL-800to1500_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 19.15,
                 "/DYto2Mu_Bin-MLL-1500to2500_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 1.111,
                 "/DYto2Mu_Bin-MLL-2500to4000_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 0.05949,
                 "/DYto2Mu_Bin-MLL-4000to6000_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 0.001558,
                 "/DYto2Mu_Bin-MLL-6000_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": .00003519,
                 "/DYto2Tau_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 6744000,
                 "/DYto2Tau_Bin-MLL-50to120_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 2219000,
                 "/DYto2Tau_Bin-MLL-120to200_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 21650,
                 "/DYto2Tau_Bin-MLL-200to400_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 3058,
                 "/DYto2Tau_Bin-MLL-400to800_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 269.1,
                 "/DYto2Tau_Bin-MLL-800to1500_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 19.15,
                 "/DYto2Tau_Bin-MLL-1500to2500_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 1.111,
                 "/DYto2Tau_Bin-MLL-2500to4000_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 0.05949,
                 "/DYto2Tau_Bin-MLL-4000to6000_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 0.001558,
                 "/DYto2Tau_Bin-MLL-6000_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": .00003519,
                 "/QCD_Bin-PT-15to20_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 3018000000,
                 "/QCD_Bin-PT-20to30_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 2701000000,
                 "/QCD_Bin-PT-30to50_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 1461000000,
                 "/QCD_Bin-PT-50to80_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 407600000,
                 "/QCD_Bin-PT-80to120_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 96070000,
                 "/QCD_Bin-PT-120to170_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 23140000,
                 "/QCD_Bin-PT-170to300_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 7754000,
                 "/QCD_Bin-PT-300to470_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 699600,
                 "/QCD_Bin-PT-470to600_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 67670,
                 "/QCD_Bin-PT-600to800_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 21270,
                 "/QCD_Bin-PT-800to1000_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 3890,
                 "/QCD_Bin-PT-1000_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM": 1323,
                 "/QCD_Bin-PT-15to20_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-15to20_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 1444000000,
                 "/QCD_Bin-PT-20to30_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-20to30_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 5309000000,
                 "/QCD_Bin-PT-30to50_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-30to50_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 6849000000,
                 "/QCD_Bin-PT-50to80_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-50to80_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 2130000000,
                 "/QCD_Bin-PT-80to120_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-80to120_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 391400000,
                 "/QCD_Bin-PT-120to170_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-120to170_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 71630000,
                 "/QCD_Bin-PT-170to300_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-170to300_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 18010000,
                 "/QCD_Bin-PT-300to470_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-300to470_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 1116000,
                 "/QCD_Bin-PT-470to600_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-470to600_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 82760,
                 "/QCD_Bin-PT-600to800_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-600to800_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 21620,
                 "/QCD_Bin-PT-800to1000_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-800to1000_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 3361,
                 "/QCD_Bin-PT-1000_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-1000_Fil-EMEnriched_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 1020,
                 "/QCD_Bin-PT-15to20_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-15to20_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 2348000000,
                 "/QCD_Bin-PT-20to30_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-20to30_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 2037000000,
                 "/QCD_Bin-PT-30to50_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-30to50_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 1042000000,
                 "/QCD_Bin-PT-50to80_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-50to80_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 270800000,
                 "/QCD_Bin-PT-80to120_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-80to120_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 60250000,
                 "/QCD_Bin-PT-120to170_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-120to170_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 13830000,
                 "/QCD_Bin-PT-170to300_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-170to300_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 4416000,
                 "/QCD_Bin-PT-300to470_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-300to470_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 377100,
                 "/QCD_Bin-PT-470to600_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-470to600_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 35350,
                 "/QCD_Bin-PT-600to800_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-600to800_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 10850,
                 "/QCD_Bin-PT-800to1000_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-800to1000_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 1960,
                 "/QCD_Bin-PT-1000_Fil-bcToE_TuneCP5_13p6TeV_pythia8/brlopesd-QCD_Bin-PT-1000_Fil-bcToE_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER": 652.8,
                 "/ScoutingPFRun3/Run2024C-v1/HLTSCOUT": 1,
                 "/ScoutingPFRun3/Run2024D-v1/HLTSCOUT": 1,
                 "/ScoutingPFRun3/Run2024E-v1/HLTSCOUT": 1,
                 "/ScoutingPFRun3/Run2024F-v1/HLTSCOUT": 1,
                 "/ScoutingPFRun3/Run2024G-v1/HLTSCOUT": 1,
                 "/ScoutingPFRun3/Run2024H-v1/HLTSCOUT": 1,
                 "/ScoutingPFRun3/Run2024I-v1/HLTSCOUT": 1
                 }

tagSuffix = "v5-K0-Resubmit"
scouting = True

for dataset, crossSection in inputDatasets.items():
    if ("ScoutingPF" in dataset):
        PUFile = "empty.npy"
    else:
        PUFile = "PURatio_Full2024.npy"
    
    if "ScoutingPF" in dataset:
        tag = dataset[16:].split("-v1")[0] + "_Tree_" + tagSuffix
        dataBase = "global"
        #totalUnits = 900000000
        memory = 3000
        isMC = False
        hasReco = False
        unitsPerJob = 20
        splitting = 'LumiBased'
        if "2024C" in dataset:
            totalUnits = 24298
        elif "2024D" in dataset:
            totalUnits = 23251
        elif "2024E" in dataset:
            totalUnits = 31576
        elif "2024F" in dataset:
            totalUnits = 70035
        elif "2024G" in dataset:
            totalUnits = 92654
        elif "2024H" in dataset:
            totalUnits = 13078
        elif "2024I" in dataset:
            totalUnits = 27112
    elif "WToLNu_0J" in dataset:
        tag = dataset[1:].split("_v1")[0] + "_Tree_" + tagSuffix
        dataBase = "phys03"
        memory = 2500
        isMC = True
        hasReco = True
        unitsPerJob = 500000
        splitting = 'EventAwareLumiBased'
    else:
        tag = dataset[1:].split("_Tune")[0] + "_Tree_" + tagSuffix
        if ("bcToE" in dataset) or ("EMEnriched" in dataset):
            dataBase = "phys03"
        else:
            dataBase = "global"
        memory = 2500
        isMC = True
        hasReco = True
        unitsPerJob = 500000
        splitting = 'EventAwareLumiBased'
    string = f"""from CRABClient.UserUtilities import config \n
config = config() \n
theTag = '{tag}' \n
config.General.requestName = theTag \n
config.JobType.pluginName = 'Analysis' \n
config.JobType.psetName = '../K0NTupleMaker.py' \n
config.JobType.inputFiles = ['/afs/cern.ch/user/r/rmccarth/private/scouting/CMSSW_14_0_18_patch1/src/Run3ScoutingAnalysisTools/Summer24Prompt24_RunBCDEFGHI.root'] \n
config.JobType.maxMemoryMB = {3000} \n
config.Data.inputDBS = '{dataBase}' \n
config.Data.inputDataset = '{dataset}' \n
config.Data.splitting = '{splitting}' \n
config.Data.unitsPerJob = {unitsPerJob} \n
config.Data.allowNonValidInputDataset = True \n
config.Data.publication = False \n
config.JobType.pyCfgParams = ['isScouting={scouting}','lumi=109.99','crossSection={crossSection}','isMC={isMC}','hasReco={hasReco}','PUFile=/afs/cern.ch/user/r/rmccarth/private/scouting/CMSSW_14_0_18_patch1/src/Run3ScoutingAnalysisTools/{PUFile}','doJEC=True'] \n
config.Data.outputDatasetTag = theTag \n
config.Data.outLFNDirBase = '/store/group/phys_exotica/DVScouting' \n
config.Site.storageSite = 'T2_CH_CERN' \n
""" 
    # Write to a temporary file
    if "ScoutingPF" in dataset:
        string += f"""config.Data.totalUnits = {totalUnits} \n"""
        string += f"""config.Data.lumiMask = '../GoldenJSON/2024' + '{dataset[23]}' + '_Golden.json'"""
        with open("crabSubmitScripts/"+dataset[16:].split("-v1")[0]+"_crabConfigK0.py", "w") as f:
            f.write(string)
    elif "WToLNu_0J" in dataset:
        with open("crabSubmitScripts/"+dataset[1:].split("_v1")[0]+"_crabConfigK0.py", "w") as f:
            f.write(string)
    else:
        with open("crabSubmitScripts/"+dataset[1:].split("_Tune")[0]+"_crabConfigK0.py", "w") as f:
            f.write(string)
