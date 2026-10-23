from CRABClient.UserUtilities import config
config = config()

Era = 'I'

theTag = "TrackMover_ScoutingData_2024" + Era + "_v19"
config.General.requestName = theTag

config.JobType.pluginName = 'Analysis'
# Name of the CMSSW configuration file
config.JobType.psetName = 'TrackMoverTest.py'
#config.JobType.maxMemoryMB = 5000

config.Data.inputDBS = 'global'
config.Data.inputDataset = '/ScoutingPFRun3/Run2024' + Era + '-v1/HLTSCOUT'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.totalUnits = 600000000
config.Data.unitsPerJob = 100000
config.Data.outLFNDirBase = '/store/user/brlopesd/TrackMover_v19/Data'
config.Data.publication = False
# This string is used to construct the output dataset name
config.Data.outputDatasetTag = theTag

config.JobType.inputFiles = ['Summer24Prompt24_RunBCDEFGHI.root',
                             'ratio_uncertaintyCorrections_v33.npz',
                             'TriggerCorrections/weights_trigger_2024_nominal.npy',
                             'TriggerCorrections/weights_trigger_2024_up.npy',
                             'TriggerCorrections/weights_trigger_2024_down.npy',
                             'TriggerCorrections/weights_trigger_2024_xedge.npy',
                             'TrackEffCorrection.root',
                             'jetScouting_jerc.json.gz'
                             ]


# These values only make sense for processing data
#    Select input data based on a lumi mask
config.Data.lumiMask = 'GoldenJSON/2024' + Era + '_Golden.json'
#    Select input data based on run-ranges
#config.Data.runRange = '190456-194076'
config.Site.blacklist = ["T2_BE_IIHE"]

# Where the output files will be transmitted to
config.Site.storageSite = 'T3_CH_CERNBOX'
