from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'monitorSkim_2024A-v1'

config.JobType.pluginName = 'Analysis'

# Name of the CMSSW configuration file
# ------------------------------------
config.JobType.psetName = 'monitorTree.py'

config.Data.inputDataset = '/ScoutingPFMonitor/Run2024B-PromptReco-v1/MINIAOD'
config.Data.secondaryInputDataset = '/ScoutingPFMonitor/Run2024B-v1/RAW'
config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 10
config.Data.publication = True
# This string is used to construct the output dataset name
# --------------------------------------------------------
config.Data.outputDatasetTag = 'monitorSkim_2024B-v1'

# These values only make sense for processing data: Select input data based on a lumi mask
# ----------------------------------------------------------------------------------------
# Golden JSON 2023: https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json
#config.Data.lumiMask = 'Cert_Collisions2023_366442_370790_Golden.json'
# Golden JSON Era C: https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions23/Cert_Collisions2023_eraC_367095_368823_Golden.json
#config.Data.lumiMask = 'Cert_Collisions2023_eraC_367095_368823_Golden.json'
# Golden JSON Era D: https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions23/Cert_Collisions2023_eraD_369803_370790_Golden.json
#config.Data.lumiMask = 'Cert_Collisions2023_eraD_369803_370790_Golden.json'
config.Data.lumiMask = 'Collisions24_13p6TeV_378981_379355_DCSOnly_TkPx.json' # Run 3 2024 (Preliminary)

#config.Site.whitelist = ['T2_US*','T2_CH*']
config.Site.storageSite = 'T3_CH_CERNBOX'
