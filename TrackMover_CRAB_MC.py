from CRABClient.UserUtilities import config
config = config()

Sample = 'QCD_HT-2000'

sampleDict = {}

QCD_bins = ['40to70', '70to100', '100to200', '200to400', '400to600', '600to800', '800to1000', '1000to1200', '1200to1500', '1500to2000', '2000']
for QCD_bin in QCD_bins:
    sampleDict[f'QCD_HT-{QCD_bin}'] = f'/QCD-4Jets_Bin-HT-{QCD_bin}_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM'

sampleDict['TTBar_SemiLeptonic'] = '/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM'
sampleDict['TTBar_FullyHadronic'] = '/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM'

theTag = f"TrackMover_ScoutingBG2024_{Sample}_v19"
config.General.requestName = theTag

config.JobType.pluginName = 'Analysis'
# Name of the CMSSW configuration file
config.JobType.psetName = 'TrackMoverTest.py'
#config.JobType.maxMemoryMB = 5000

config.Data.inputDBS = 'global'
config.Data.inputDataset = sampleDict[Sample]
config.Data.splitting = 'EventAwareLumiBased'
config.Data.totalUnits = 1000000000
config.Data.unitsPerJob = 500000
config.Data.outLFNDirBase = '/store/user/brlopesd/TrackMover_v19/Background'
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
#config.Data.lumiMask = 'GoldenJSON/2024' + Era + '_Golden.json'
#    Select input data based on run-ranges
#config.Data.runRange = '190456-194076'

config.Site.blacklist = ["T2_BE_IIHE"]

# Where the output files will be transmitted to
config.Site.storageSite = 'T3_CH_CERNBOX'
