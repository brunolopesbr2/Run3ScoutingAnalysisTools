inputDatasets = [
                 "/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/WToLNu_0J_v1/brlopesd-WToLNu_0J_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/WtoLNu-2Jets_Bin-1J-PTLNu-40to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v3/MINIAODSIM",
                 "/WtoLNu-2Jets_Bin-1J-PTLNu-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v3/MINIAODSIM",
                 "/WtoLNu-2Jets_Bin-1J-PTLNu-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/WtoLNu-2Jets_Bin-1J-PTLNu-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/WtoLNu-2Jets_Bin-1J-PTLNu-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/WtoLNu-2Jets_Bin-2J-PTLNu-40to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v3/MINIAODSIM",
                 "/WtoLNu-2Jets_Bin-2J-PTLNu-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v3/MINIAODSIM",
                 "/WtoLNu-2Jets_Bin-2J-PTLNu-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/WtoLNu-2Jets_Bin-2J-PTLNu-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/WtoLNu-2Jets_Bin-2J-PTLNu-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/WZ_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/WW_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/ZZ_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/DYto2L-2Jets_Bin-MLL-50-PTLL-100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v3/MINIAODSIM",
                 "/QCD_Bin-PT-15to20_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-20to30_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-30to50_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-50to80_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-80to120_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-120to170_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-170to300_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-300to470_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-470to600_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-600to800_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-800to1000_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-1000_Fil-MuEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD_Bin-PT-15to20_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-20to30_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-30to50_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-50to80_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-80to120_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-120to170_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-170to300_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-300to470_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-470to600_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-600to800_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-800to1000_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-1000_Fil-EMEnriched_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-15to20_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-20to30_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-30to50_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-50to80_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-80to120_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-120to170_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-170to300_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-300to470_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-470to600_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-600to800_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-800to1000_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/QCD_Bin-PT-1000_Fil-bcToE_TuneCP5_13p6TeV_pythia8/RunIII2024Summer24MiniAODv6-150X_mcRun3_2024_realistic_v2-v2/MINIAODSIM",
                 "/ScoutingPFRun3/Run2024C-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024D-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024E-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024F-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024G-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024H-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024I-v1/HLTSCOUT",
                 ]

crossSections = [762100, 762100, 762100, 55760000, 4211000, 342300, 21840, 684.5, 77.53, 1581000, 411100, 53590, 3099, 525.9, 29100, 80230, 12750, 106600, 3018000000, 2701000000, 1461000000, 407600000, 96070000, 23140000, 7754000, 699600, 67670, 21270, 3890, 1323, 1444000000, 5309000000, 6849000000, 2130000000, 391400000, 71630000, 18010000, 1116000, 82760, 21620, 3361, 1020, 2348000000, 2037000000, 1042000000, 270800000, 60250000, 13830000, 4416000, 377100, 35350, 10850, 1960, 652.8] #Backgrounds should go first in dataset list with corresponding cross sections listed here
tagSuffix = "v1-K0"
scouting = True

for i in range(len(inputDatasets)):
    dataset = inputDatasets[i]
    if ("ScoutingPF" in dataset):
        crossSection = 1
        PUFile = "empty.npy"
    else:
        crossSection = crossSections[i]
        PUFile = "PURatio_Full2024.npy"
    
    if "ScoutingPF" in dataset:
        tag = dataset[16:].split("-v1")[0] + "_Tree_" + tagSuffix
        dataBase = "global"
        #totalUnits = 900000000
        isMC = False
        hasReco = False
        unitsPerJob = 10
        splitting = 'LumiBased'
        if "2024C" in dataset:
            totalUnits = int(24298 / 2)
        elif "2024D" in dataset:
            totalUnits = int(23251 / 2)
        elif "2024E" in dataset:
            totalUnits = int(31576 / 2)
        elif "2024F" in dataset:
            totalUnits = int(70035 / 2)
        elif "2024G" in dataset:
            totalUnits = int(92654 / 2)
        elif "2024H" in dataset:
            totalUnits = int(13078 / 2)
        elif "2024I" in dataset:
            totalUnits = int(27112 / 2)
    elif "WToLNu_0J" in dataset:
        tag = dataset[1:].split("_v1")[0] + "_Tree_" + tagSuffix
        dataBase = "phys03"
        isMC = True
        hasReco = True
        unitsPerJob = 500000
        splitting = 'EventAwareLumiBased'
    else:
        tag = dataset[1:].split("_Tune")[0] + "_Tree_" + tagSuffix
        dataBase = "global"
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
config.JobType.maxMemoryMB = 2500 \n
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
config.Data.ignoreLocality = True \n
config.Site.whitelist = ['T2_*', 'T1_*'] \n
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
