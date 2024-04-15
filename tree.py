import FWCore.ParameterSet.Config as cms

process = cms.Process("SKIM")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)
process.MessageLogger.cerr.FwkSummary.reportEvery = 1000
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        '/store/data/Run2024B/ScoutingPFRun3/RAW/v1/000/379/349/00000/11875fc9-72ca-41d6-b97e-49afa43802e2.root',
        '/store/data/Run2024B/ScoutingPFRun3/RAW/v1/000/379/349/00000/3d9a4294-329c-4d65-8fc8-d14c82f3b261.root'
 )
)

#process.load("Run3ScoutingAnalysisTools.ScoutingFilter.ScoutingFilter_cff")

process.load("EventFilter.L1TRawToDigi.gtStage2Digis_cfi")
process.gtStage2Digis.InputLabel = cms.InputTag( "hltFEDSelectorL1" )

process.TFileService = cms.Service("TFileService", 
    fileName = cms.string("scout.root")
)

#process.ScoutingFilterPath = cms.Path(process.scoutingFilter)

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, '124X_dataRun3_Prompt_v4', '') # Run 3 2022
#process.GlobalTag = GlobalTag(process.GlobalTag, '132X_dataRun3_Prompt_v2', '') # Run 3 2023
process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_Prompt_v1', '') # Run 3 2024

#L1Info = ["L1_DoubleMu_12_5","L1_DoubleMu_15_7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18","L1_DoubleMu4_SQ_OS_dR_Max1p2","L1_DoubleMu4p5_SQ_OS_dR_Max1p2"]
#L1Info = ["L1_DoubleMu_12_5","L1_DoubleMu_15_7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18","L1_DoubleMu4_SQ_OS_dR_Max1p2","L1_DoubleMu4p5_SQ_OS_dR_Max1p2", "L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4", "L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4", "L1_DoubleMu8_SQ"]
L1Info = ["L1_DoubleMu_12_5","L1_DoubleMu_15_7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18","L1_DoubleMu8_SQ","L1_DoubleMu0er1p4_SQ_OS_dEta_Max1p2","L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6","L1_DoubleMu5_SQ_OS_dR_Max1p6","L1_DoubleMu3er2p0_SQ_OS_dR_Max1p6","L1_DoubleMu0er1p5_SQ_OS_dEta_Max1p2","L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6","L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6","L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5","L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4","L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4","L1_DoubleMu4p5_SQ_OS_dR_Max1p2","L1_DoubleMu4_SQ_OS_dR_Max1p2","L1_DoubleMu0_Upt15_Upt7","L1_DoubleMu0_Upt6_IP_Min1_Upt4","L1_DoubleMu6_Upt6_SQ_er2p0","L1_DoubleMu7_Upt7_SQ_er2p0","L1_DoubleMu8_Upt8_SQ_er2p0","L1_DoubleMu0er2p0_SQ_dEta_Max1p6","L1_DoubleMu0er2p0_SQ_dEta_Max1p5"]

process.scoutingTree = cms.EDAnalyzer('ScoutingTreeMakerRun3',
                                      triggerresults   = cms.InputTag("TriggerResults", "", "HLT"),
                                      ReadPrescalesFromFile = cms.bool( False ),
                                      AlgInputTag       = cms.InputTag("gtStage2Digis"),
                                      l1tAlgBlkInputTag = cms.InputTag("gtStage2Digis"),
                                      l1tExtBlkInputTag = cms.InputTag("gtStage2Digis"),
                                      doL1 = cms.bool( True ),
                                      l1Seeds           = cms.vstring(L1Info),
                                      muons             = cms.InputTag("hltScoutingMuonPackerNoVtx"),
                                      electrons         = cms.InputTag("hltScoutingEgammaPacker"),
                                      photons           = cms.InputTag("hltScoutingEgammaPacker"),
                                      pfcands           = cms.InputTag("hltScoutingPFPacker"),
                                      pfjets            = cms.InputTag("hltScoutingPFPacker"),
                                      tracks            = cms.InputTag("hltScoutingTrackPacker"),
                                      primaryVertices   = cms.InputTag("hltScoutingPrimaryVertexPacker","primaryVtx"),
                                      displacedVertices = cms.InputTag("hltScoutingMuonPackerNoVtx","displacedVtx"),
                                      pfMet             = cms.InputTag("hltScoutingPFPacker","pfMetPt"),
                                      pfMetPhi          = cms.InputTag("hltScoutingPFPacker","pfMetPhi"),
                                      rho               = cms.InputTag("hltScoutingPFPacker","rho"),
                                  )

process.p = cms.Path(process.gtStage2Digis+process.scoutingTree)
