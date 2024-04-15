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
                                #
                                #"/store/data/Run2023C/ScoutingPFMonitor/MINIAOD/PromptReco-v4/000/368/823/00000/cccd7032-a259-4e60-a21b-1b88c041c769.root",
                                #
                                "/store/data/Run2024B/ScoutingPFMonitor/MINIAOD/PromptReco-v1/000/379/349/00000/873bebf4-3f0d-40f4-abf1-c765b914d2fb.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/MINIAOD/PromptReco-v1/000/379/349/00000/90dabf21-60f0-4375-a84c-6f20094a8487.root"
                            ),
                            secondaryFileNames=cms.untracked.vstring(
                                #
                                #"/store/data/Run2023C/ScoutingPFMonitor/RAW/v1/000/368/823/00000/388bf0bd-900f-410a-864c-b77b243d11ff.root",
                                #"/store/data/Run2023C/ScoutingPFMonitor/RAW/v1/000/368/823/00000/9da4e47e-8e12-4a7e-8c71-88458eef0563.root",
                                #"/store/data/Run2023C/ScoutingPFMonitor/RAW/v1/000/368/823/00000/66c984ff-6f83-4c2e-9c77-34b6714fe479.root"
                                #
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/a6d83181-92fb-4acb-8c5e-21dcd9ddfaeb.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/958dfea7-21d3-4096-91b0-c2c2a49dcd2d.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/7abcadd0-245f-4f5b-8cbe-1e088adc3c52.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/fa791d1b-0298-45f5-88f4-3c5ed3faddf1.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/b7ceb3c4-fa26-4b73-a49e-c0f05c4310e4.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/bbc11c95-c875-485f-8606-4c1e1d03b0a8.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/ad2e8e3b-d43f-4645-92e8-b08f5f5c471a.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/2b70d8f6-4b70-4287-861d-a13f5022c71f.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/8b2996d4-9681-4e9d-affa-81ac67ce3d05.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/88a849cf-8006-4a6b-9868-948bb58efeea.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/84fab1ba-6f4f-42e3-8e54-fab0e2f31bd2.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/4c47f057-5b4d-4388-aa77-af39f7a8c69f.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/c5e89878-3c49-4385-af06-1d0ce9ded0eb.root",
                                "/store/data/Run2024B/ScoutingPFMonitor/RAW/v1/000/379/349/00000/9dfd4a46-45ee-40e8-97c4-0ddd5be8269e.root"
                                ),
                            lumisToProcess = cms.untracked.VLuminosityBlockRange('368823:3-368823:35')
                            #lumisToProcess = cms.untracked.VLuminosityBlockRange('361971:2303-361971:2327','362167:87-362167:96')
)

#process.load("Run3ScoutingAnalysisTools.ScoutingFilter.ScoutingFilter_cff")

process.load("EventFilter.L1TRawToDigi.gtStage2Digis_cfi")
#process.gtStage2Digis.InputLabel = cms.InputTag( "hltFEDSelectorL1" )
process.gtStage2Digis.InputLabel = cms.InputTag( "rawDataCollector", "", "LHC" )

process.TFileService = cms.Service("TFileService", 
    fileName = cms.string("scoutMonitor.root")
)

#process.ScoutingFilterPath = cms.Path(process.scoutingFilter)

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag = GlobalTag(process.GlobalTag, '124X_dataRun3_Prompt_v4', '') # Run 3 2022
#process.GlobalTag = GlobalTag(process.GlobalTag, '132X_dataRun3_Prompt_v2', '') # Run 3 2023
process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_Prompt_v1', '') # Run 3 2024

#L1Seeds = ["L1_DoubleMu_12_5","L1_DoubleMu_15_7","L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4", "L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4", "L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18","L1_DoubleMu4_SQ_OS_dR_Max1p2","L1_DoubleMu4p5_SQ_OS_dR_Max1p2", "L1_DoubleMu8_SQ"]
#L1Seeds = ["L1_DoubleMu_12_5","L1_DoubleMu_15_7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18","L1_DoubleMu4_SQ_OS_dR_Max1p2","L1_DoubleMu4p5_SQ_OS_dR_Max1p2", "L1_SingleLooseIsoEG28er2p1", "L1_SingleLooseIsoEG28er1p5", "L1_SingleLooseIsoEG30er1p5", "L1_SingleIsoEG30er2p1", "L1_SingleIsoEG32er2p1", "L1_DoubleEG_LooseIso16_LooseIso12_er1p5", "L1_DoubleEG_LooseIso18_LooseIso12_er1p5", "L1_DoubleEG_LooseIso20_LooseIso12_er1p5", "L1_DoubleEG_LooseIso22_LooseIso12_er1p5", "L1_SingleJet180", "L1_SingleJet200", "L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5", "L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5", "L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5", "L1_HTT280er", "L1_HTT320er", "L1_HTT360er", "L1_ETT2000"]

L1Seeds = ["L1_DoubleMu_12_5","L1_DoubleMu_15_7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_Min7","L1_DoubleMu4p5er2p0_SQ_OS_Mass_7to18","L1_DoubleMu8_SQ","L1_DoubleMu0er1p4_SQ_OS_dEta_Max1p2","L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6","L1_DoubleMu5_SQ_OS_dR_Max1p6","L1_DoubleMu3er2p0_SQ_OS_dR_Max1p6","L1_DoubleMu0er1p5_SQ_OS_dEta_Max1p2","L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p6","L1_DoubleMu0er1p4_OQ_OS_dEta_Max1p6","L1_DoubleMu0er2p0_SQ_OS_dEta_Max1p5","L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4","L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4","L1_DoubleMu4p5_SQ_OS_dR_Max1p2","L1_DoubleMu4_SQ_OS_dR_Max1p2","L1_DoubleMu0_Upt15_Upt7","L1_DoubleMu0_Upt6_IP_Min1_Upt4","L1_DoubleMu6_Upt6_SQ_er2p0","L1_DoubleMu7_Upt7_SQ_er2p0","L1_DoubleMu8_Upt8_SQ_er2p0","L1_DoubleMu0er2p0_SQ_dEta_Max1p6","L1_DoubleMu0er2p0_SQ_dEta_Max1p5"]

L1MonitorSeeds = ["L1_SingleMu22","L1_SingleMu25","L1_HTT200er","L1_HTT255er","L1_HTT280er","L1_HTT320er","L1_HTT360er","L1_HTT400er","L1_HTT450er","L1_ETT2000", "L1_HTT280er_QuadJet_70_55_40_35_er2p5","L1_HTT320er_QuadJet_80_60_er2p1_45_40_er2p3", "L1_HTT320er_QuadJet_80_60_er2p1_50_45_er2p3","L1_SingleEG34er2p5", "L1_SingleEG36er2p5","L1_SingleEG38er2p5","L1_SingleEG40er2p5","L1_SingleJet160er2p5","L1_SingleJet180","L1_SingleJet200","L1_SingleTau120er2p1","L1_SingleTau130er2p1","L1_SingleEG42er2p5","L1_SingleEG45er2p5","L1_SingleEG60", "L1_DoubleEG_LooseIso18_LooseIso12_er1p5","L1_DoubleEG_LooseIso20_LooseIso12_er1p5","L1_DoubleEG_LooseIso22_LooseIso12_er1p5"]
#L1MonitorSeeds = ["L1_HTT200er","L1_HTT255er","L1_HTT280er","L1_HTT320er","L1_HTT360er","L1_HTT400er","L1_HTT450er","L1_ETT2000","L1_SingleJet180","L1_SingleJet200","L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5","L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5","L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5","L1_SingleLooseIsoEG28er2p1","L1_SingleLooseIsoEG28er1p5","L1_SingleLooseIsoEG30er1p5","L1_SingleIsoEG28er2p1","L1_SingleIsoEG30er2p1","L1_SingleIsoEG32er2p1","L1_DoubleEG_LooseIso16_LooseIso12_er1p5","L1_DoubleEG_LooseIso18_LooseIso12_er1p5","L1_DoubleEG_LooseIso20_LooseIso12_er1p5","L1_DoubleEG_LooseIso22_LooseIso12_er1p5"]

process.scoutingTree = cms.EDAnalyzer('ScoutingTreeMakerRun3Monitor',
                                      triggerresults   = cms.InputTag("TriggerResults", "", "HLT"),
                                      ReadPrescalesFromFile = cms.bool( False ),
                                      AlgInputTag       = cms.InputTag("gtStage2Digis"),
                                      l1tAlgBlkInputTag = cms.InputTag("gtStage2Digis"),
                                      l1tExtBlkInputTag = cms.InputTag("gtStage2Digis"),
                                      doL1 = cms.bool( True ),
                                      l1Seeds           = cms.vstring(L1Seeds),
                                      l1MonitorSeeds    = cms.vstring(L1MonitorSeeds),
                                      muons             = cms.InputTag("hltScoutingMuonPackerNoVtx","","HLT"),
                                      offlineMuons      = cms.untracked.InputTag("slimmedMuons"),
                                      electrons         = cms.InputTag("hltScoutingEgammaPacker"),
                                      offlinePhotons    = cms.untracked.InputTag("slimmedPhotons"),
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
