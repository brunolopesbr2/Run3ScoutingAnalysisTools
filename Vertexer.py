import FWCore.ParameterSet.Config as cms

process = cms.Process("TESTVERTEX")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)

process.MessageLogger.cerr.FwkSummary.reportEvery = 100
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # Test file generated on CMSSW 13.3.0
    fileNames = cms.untracked.vstring( 
        'file:scout_test.root'
    )
)

#Choosing the GlobalTag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '133X_mcRun3_2024_realistic_v9', '')  
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

# Input tags to the EDProducer
process.Vertexer = cms.EDProducer('Vertexer',
  seed_tracks_src = cms.InputTag('hltScoutingUnpackProducer', 'Track')
)

# Save only the scouting collections on the output file
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('vertexer_test.root'),
    #outputCommands = cms.untracked.vstring('drop *', 'keep *_hltGtStage2ObjectMap_*_*', 'keep *_TriggerResults_*_*', 'keep *_hltScouting*_*_*')
)

# Usually it is better to put producers on a task instead of a path
# but paths also work.
process.p = cms.Path(process.Vertexer)
process.e = cms.EndPath(process.out)
