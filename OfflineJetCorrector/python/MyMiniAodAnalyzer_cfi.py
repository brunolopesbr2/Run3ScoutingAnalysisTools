import FWCore.ParameterSet.Config as cms

myMiniAodAnalyzer = cms.EDAnalyzer("MyMiniAodAnalyzer",
    jetAK4Src = cms.InputTag("slimmedJets"),
    jetAK8Src = cms.InputTag("slimmedJetsAK8"),   # set to "" to skip AK8
    metSrc    = cms.InputTag("slimmedMETs")       # or "slimmedMETsPuppi"
)

