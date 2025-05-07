import FWCore.ParameterSet.Config as cms
import os
import FWCore.ParameterSet.VarParsing as VarParsing

process = cms.Process("TREE")
options = VarParsing.VarParsing ('analysis')
options.register('isScouting',
                 True,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "If scouting or reco tracks should be used for vertexing"
    )
options.register('lumi',
                 108.96,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.float,
                 "Integrated luminosity for weighting"
    )
options.register('crossSection',
                 1,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.float,
                 "Cross Section for weighting"
    )

options.parseArguments()
process.load("FWCore.MessageService.MessageLogger_cfi")

process.MessageLogger.cerr.FwkSummary.reportEvery = 100
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring( 
        'file:scout_withRecoVertex.root'
    )
)

process.load("EventFilter.L1TRawToDigi.gtStage2Digis_cfi")
process.gtStage2Digis.InputLabel = cms.InputTag( "hltFEDSelectorL1" )

process.TFileService = cms.Service("TFileService", 
    fileName = cms.string("tree.root")
)

if(options.isScouting):
    pfjetsTag = cms.InputTag("hltScoutingPFPacker")
    patjetsTag = cms.InputTag("")
    pvTag = cms.InputTag("hltScoutingUnpackProducer","PrimaryVertex")
else:
    pfjetsTag = cms.InputTag("")
    patjetsTag = cms.InputTag("slimmedJets")
    pvTag = cms.InputTag("offlineSlimmedPrimaryVertices")
    

#process.ScoutingFilterPath = cms.Path(process.scoutingFilter)
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_Prompt_v4', '')  
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

#The L1 seeds used for JetHT
L1Info = ["L1_HTT200er", "L1_HTT255er", "L1_HTT280er", "L1_HTT320er", "L1_HTT360er", "L1_HTT400er", "L1_HTT450er", "L1_ETT2000", "L1_SingleJet180", "L1_SingleJet200", "L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5", "L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5", "L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5"]

#For CMSSW 13.3.0, the muon tag is hltScoutingMuonPacker, whilst for 14X it's hltScoutingMuonPackerNoVtx
process.scoutingTree = cms.EDAnalyzer('ScoutingTreeMakerRun3',
                                      required_ntk     = cms.int32(2),
                                      triggerresults   = cms.InputTag("TriggerResults", "", "HLT"),
                                      ReadPrescalesFromFile = cms.bool( False ),
                                      AlgInputTag       = cms.InputTag("gtStage2Digis"),
                                      l1tAlgBlkInputTag = cms.InputTag("gtStage2Digis"),
                                      l1tExtBlkInputTag = cms.InputTag("gtStage2Digis"),
                                      doTrigger = cms.bool( True ),
                                      isScouting = cms.bool(True),
                                      doPhiCorrection = cms.bool( False ),
                                      doGenMatching = cms.bool( False ),
                                      luminosity = cms.double(108.96), #2024 luminosity (fb-1)
                                      crossSection = cms.double(1), # cross section in fb
                                      l1Seeds           = cms.vstring(L1Info),
                                      muons             = cms.InputTag("hltScoutingMuonPacker"),
                                      electrons         = cms.InputTag("hltScoutingEgammaPacker"),
                                      photons           = cms.InputTag("hltScoutingEgammaPacker"),
                                      pfjets            = pfjetsTag,
                                      patjets           = patjetsTag,
                                      tracks            = cms.InputTag("hltScoutingUnpackProducer","Track"),
                                      trackRefs         = cms.InputTag("hltScoutingUnpackProducer", "Track-RefToOriginal"),
                                      primaryVertices   = cms.InputTag("hltScoutingPrimaryVertexPacker","primaryVtx"),
                                      displacedVertices = cms.InputTag("Vertexer"),
                                      pfMet             = cms.InputTag("hltScoutingPFPacker","pfMetPt"),
                                      pfMetPhi          = cms.InputTag("hltScoutingPFPacker","pfMetPhi"),
                                      rho               = cms.InputTag("hltScoutingPFPacker","rho"),
                                      beamspot_src = cms.InputTag('offlineBeamSpot'),
                                      #genParticle_src = cms.InputTag('genParticles',''),
                                      #generatorName = cms.InputTag('generator')
                                  )

process.p = cms.Path(process.gtStage2Digis+process.scoutingTree)
