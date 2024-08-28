import FWCore.ParameterSet.Config as cms

process = cms.Process("SKIM")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        '/store/user/brlopesd/StopStopbarTo2Dbar2D_M-200_CTau-10mm_v1/StopStopbarTo2Dbar2D_M-200_CTau-10mm_v1/240730_165552/0000/GENSIMRAW_3.root'
    )
)



process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '133X_mcRun3_2024_realistic_v9', '')  

# Note that the next part is often separated into a separate python file with the suffix _cfi.py
process.hltScoutingUnpackProducer = cms.EDProducer('HLTScoutingUnpackProducer',
  scoutingPFJet = cms.InputTag('hltScoutingPFPacker'),
  scoutingPFCandidate = cms.InputTag('hltScoutingPFPacker'),
  scoutingTrack = cms.InputTag('hltScoutingTrackPacker'),
  scoutingPrimaryVertex = cms.InputTag("hltScoutingPrimaryVertexPacker","primaryVtx"),
  producePFCandidate = cms.bool(True),
  producePFCandidateMatchTrack = cms.bool(False),
  producePFCHSCandidate = cms.bool(False),
  mightGet = cms.optional.untracked.vstring
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('scout_test.root'),
    #outputCommands = cms.untracked.vstring('keep *')
)

# Usually it is better to put producers on a task instead of a path
# but paths also work.
process.p = cms.Path(process.hltScoutingUnpackProducer)

process.e = cms.EndPath(process.out)
