import FWCore.ParameterSet.Config as cms

process = cms.Process("SKIM")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)
process.MessageLogger.cerr.FwkSummary.reportEvery = 1000
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # Test file generated on CMSSW 13.3.0
    fileNames = cms.untracked.vstring( 
        '/store/user/brlopesd/StopStopbarTo2Dbar2D_M-200_CTau-10mm_v1/StopStopbarTo2Dbar2D_M-200_CTau-10mm_v1/240730_165552/0000/GENSIMRAW_3.root'
    )
)

#Choosing the GlobalTag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '133X_mcRun3_2024_realistic_v9', '')  

# Input tags to the EDProducer
process.hltScoutingUnpackProducer = cms.EDProducer('HLTScoutingUnpackProducer',
  scoutingTrack = cms.InputTag('hltScoutingTrackPacker'),
  scoutingPrimaryVertex = cms.InputTag("hltScoutingPrimaryVertexPacker","primaryVtx"),
  producePFCHSCandidate = cms.bool(False),
  mightGet = cms.optional.untracked.vstring
)

# Save only the scouting collections on the output file
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('scout_test.root'),
    outputCommands = cms.untracked.vstring('drop *', 'keep *_hltGtStage2ObjectMap_*_*', 'keep *_TriggerResults_*_*', 'keep *_hltScouting*_*_*')
)

# Usually it is better to put producers on a task instead of a path
# but paths also work.
process.p = cms.Path(process.hltScoutingUnpackProducer)
process.e = cms.EndPath(process.out)
