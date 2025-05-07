from CRABClient.UserUtilities import config
config = config()

theTag = "ScoutingData_Summer24_2024D_Tree_1Mevts_v1"
config.General.requestName = theTag

config.JobType.pluginName = 'Analysis'
# Name of the CMSSW configuration file
config.JobType.psetName = 'tree.py'
#config.JobType.maxMemoryMB = 5000

config.Data.inputDBS = 'phys03'
config.Data.inputDataset = '/ScoutingPFRun3/brlopesd-ScoutingData_Summer24_2024D_WithVertex_1Mevts_v1-950c16096432821b8d64deb3468e7847/USER'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 100000
config.Data.publication = True
# This string is used to construct the output dataset name

config.Data.outputDatasetTag = theTag
config.Data.outLFNDirBase = '/store/user/brlopesd/data_tree_1M/'
config.Data.publication = False


# These values only make sense for processing data
#    Select input data based on a lumi mask
#config.Data.lumiMask = 'Cert_190456-208686_8TeV_PromptReco_Collisions12_JSON.txt'
#    Select input data based on run-ranges
#config.Data.runRange = '190456-194076'

# Where the output files will be transmitted to
config.Site.storageSite = 'T3_CH_CERNBOX'
