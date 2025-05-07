from CRABClient.UserUtilities import config
config = config()

theTag = "ScoutingData_Summer24_2024D_InputToVertexer_1Mevts_v1"
config.General.requestName = theTag

config.JobType.pluginName = 'Analysis'
# Name of the CMSSW configuration file
config.JobType.psetName = 'HLTScoutingUnpackProducer.py'
#config.JobType.maxMemoryMB = 5000

config.Data.inputDBS = 'global'
config.Data.inputDataset = '/ScoutingPFRun3/Run2024D-v1/HLTSCOUT'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.totalUnits = 1000000
config.Data.unitsPerJob = 10000
config.Data.publication = True
# This string is used to construct the output dataset name
config.Data.outputDatasetTag = theTag

# These values only make sense for processing data
#    Select input data based on a lumi mask
#config.Data.lumiMask = 'Cert_190456-208686_8TeV_PromptReco_Collisions12_JSON.txt'
#    Select input data based on run-ranges
#config.Data.runRange = '190456-194076'

# Where the output files will be transmitted to
config.Site.storageSite = 'T2_BR_SPRACE'
