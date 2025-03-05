import FWCore.ParameterSet.Config as cms

process = cms.Process("Repacker")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)
process.MessageLogger.cerr.FwkSummary.reportEvery = 100
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) ) #100 events for offline testing

process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring('file:scout_withRecoVertex.root',
                            )
)

#Choosing the GlobalTag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_Prompt_v4', '')  #GT for data

# Input tags to the EDProducer
process.hltScoutingRepackProducer = cms.EDProducer('HLTScoutingRepackProducer',
                                                   displacedVertices = cms.InputTag("Vertexer"),
)

# Save only the scouting collections on the output file
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('scout_repacked.root'),
    #keep everything for data
)

# Usually it is better to put producers on a task instead of a path
# but paths also work.
process.p = cms.Path(process.hltScoutingRepackProducer)
process.e = cms.EndPath(process.out)
