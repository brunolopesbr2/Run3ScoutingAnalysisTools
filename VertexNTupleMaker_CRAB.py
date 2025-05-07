from CRABClient.UserUtilities import config
config = config()

theTag = "ScoutingData_Summer24_2024D_tree_1Mevts_v3"
config.General.requestName = theTag

config.JobType.pluginName = 'Analysis'
# Name of the CMSSW configuration file
config.JobType.psetName = 'VertexNTupleMaker.py'
#config.JobType.maxMemoryMB = 5000

config.Data.inputDBS = 'global'
config.Data.inputDataset = '/ScoutingPFRun3/Run2024D-v1/HLTSCOUT'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.totalUnits = 10000000
config.Data.unitsPerJob = 1000
config.Data.outLFNDirBase = '/store/user/brlopesd/data_tree_1M/'
config.Data.publication = False
# This string is used to construct the output dataset name
config.Data.outputDatasetTag = theTag


# These values only make sense for processing data
#    Select input data based on a lumi mask
config.Data.lumiMask = '2024D_Golden.json'
#    Select input data based on run-ranges
#config.Data.runRange = '190456-194076'

# Where the output files will be transmitted to
config.Site.storageSite = 'T3_CH_CERNBOX'
