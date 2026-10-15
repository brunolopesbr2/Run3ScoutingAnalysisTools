import FWCore.ParameterSet.Config as cms
import os
import FWCore.ParameterSet.VarParsing as VarParsing

process = cms.Process("ScoutingToRecoJet")
options = VarParsing.VarParsing ('analysis')

options.register('lumi',
                 109.99,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.float,
                 "Integrated luminosity for weighting"
    )
options.register('crossSection',
                 762.1,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.float,
                 "Cross Section for weighting"
    )
options.register('isMC',
                 True,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "If using MC or data"
    )

options.register('doJECOffline',
                 True,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Online or offline JECs"
    ) 

options.register('doJECUnc',
                 True,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Do the JEC variations. Only available for the offline JECs"
    ) 

options.register('hasReco',
                 False,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "If the input has offline reconstruction (MC or ScoutingPFMonitor)"
    )

options.register('debugTree',
                 False,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Include extra track collections and PV information for debugging."
)

options.parseArguments()
process.load("FWCore.MessageService.MessageLogger_cfi")
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)
process.MessageLogger.cerr.FwkSummary.reportEvery = 100
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10000) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        #MC test file
        #'/store/mc/RunIII2024Summer24MiniAOD/QCD-4Jets_Bin-HT-1000to1200_TuneCP5_13p6TeV_madgraphMLM-pythia8/MINIAODSIM/140X_mcRun3_2024_realistic_v26-v2/100000/00f7403b-49bf-4efd-9b8f-0398bd61d910.root'
        #Data test file
        #'/store/data/Run2024D/ScoutingPFRun3/HLTSCOUT/v1/000/380/945/00000/cdf45723-07c4-4b41-9595-f368f2929369.root'
        #PF monitor file
        #'/store/data/Run2024D/ScoutingPFMonitor/MINIAOD/PromptReco-v1/000/380/306/00000/70ec6086-72c5-4562-82a8-1f043e645d59.root'
        #Higgs test file
        #'/store/mc/RunIII2024Summer24MiniAOD/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/MINIAODSIM/140X_mcRun3_2024_realistic_v26-v2/110000/03add799-043d-4b36-ae54-b114138eb7c8.root'
        #Stop test file
        #'/store/user/brlopesd/StopStopbarTo2Dbar2D_M-800_CTau-3mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-800_CTau-3mm_Summer24_100k_miniAOD_v2/250214_151828/0000/stop_dbar_miniAOD_1.root'
        #more displaced sample
        '/store/user/brlopesd/StopStopbarTo2Dbar2D_M-800_CTau-10mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-800_CTau-10mm_Summer24_100k_miniAOD_v2/250214_151643/0000/stop_dbar_miniAOD_1.root'
        #local test file
        #'file:testScoutMonitorFile.root'
        #ScoutingPFMonitor test file
        #'/store/data/Run2024D/ScoutingPFMonitor/MINIAOD/PromptReco-v1/000/380/306/00000/7236c128-bb6e-4a16-aeda-2091c9544adc.root'

    )
)


#Choosing the GlobalTag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag

if(options.isMC):
    process.GlobalTag = GlobalTag(process.GlobalTag, '140X_mcRun3_2024_realistic_v26', '')  
    truePileupTag = cms.InputTag("slimmedAddPileupInfo")
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_HLT_v3', '')
    truePileupTag = cms.InputTag("")

process.load("EventFilter.L1TRawToDigi.gtStage2Digis_cfi")
process.gtStage2Digis.InputLabel = cms.InputTag( "hltFEDSelectorL1" )

isDataBool = cms.bool(not options.isMC)
if(options.isMC):
    eraToJEC = cms.string("")
else:
    eraToJEC = cms.string("Era2024All")

#The L1 seeds used for JetHT
L1Info = ["L1_HTT200er", "L1_HTT255er", "L1_HTT280er", "L1_HTT320er", "L1_HTT360er", "L1_HTT400er", "L1_HTT450er", "L1_ETT2000", "L1_SingleJet180", "L1_SingleJet200", "L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5", "L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5", "L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5"]

#Part 0: make sure all events have a valid rho
process.rhoFilter = cms.EDFilter("RhoFilter",
    src = cms.InputTag("hltScoutingPFPacker", "rho")
)

#Part 1: create reco::PFJet
process.scoutingToRecoJets = cms.EDProducer('Run3ScoutingPFJetToRecoPFJetProducer',
                                     scoutingPFJet = cms.InputTag("hltScoutingPFPacker")
                                     )


#Part 2.1: online JEC
if(options.doJECOffline):
    pfjetsTag = cms.InputTag("jecAppliedJetProducer", "CorrectedAK4")
    if(options.doJECUnc):
        pfjetsTagUp = cms.InputTag("jecAppliedJetProducerJECup", "CorrectedAK4")
        pfjetsTagDown = cms.InputTag("jecAppliedJetProducerJECdown", "CorrectedAK4")
    else:
        pfjetsTagUp = cms.InputTag("")
        pfjetsTagDown = cms.InputTag("")
else:
    pfjetsTag = cms.InputTag("scoutingPFJetCorrected")
    pfjetsTagUp = cms.InputTag("")
    pfjetsTagDown = cms.InputTag("")

# update JEC
if(options.isMC):
    process.GlobalTag.toGet = cms.VPSet(
    cms.PSet( # hlt AK4PFHLT latest
        record = cms.string("JetCorrectionsRecord"),
        tag = cms.string("JetCorrectorParametersCollection_Run3Winter24Digi_AK4PFHLT"),
        label = cms.untracked.string("AK4PFHLT"),
        connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS")
    )
    )
else:
    process.GlobalTag.toGet = cms.VPSet(
    cms.PSet( # hlt AK4PFHLT latest
        record = cms.string("JetCorrectionsRecord"),
        tag = cms.string("JetCorrectorParametersCollection_AK4PFHLT_hlt_v1"),
        label = cms.untracked.string("AK4PFHLT"),
        connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS")
    )
    )

#Online JEC
process.hltAK4PFFastJetCorrector = cms.EDProducer("L1FastjetCorrectorProducer",
    algorithm = cms.string("AK4PFHLT"),
    level = cms.string("L1FastJet"),
    srcRho = cms.InputTag("hltScoutingPFPacker", "rho")
)

process.hltAK4PFRelativeCorrector = cms.EDProducer( "LXXXCorrectorProducer",
    algorithm = cms.string( "AK4PFHLT" ),
    level = cms.string( "L2Relative" )
)

process.hltAK4PFAbsoluteCorrector = cms.EDProducer( "LXXXCorrectorProducer",
    algorithm = cms.string( "AK4PFHLT" ),
    level = cms.string( "L3Absolute" )
)

process.hltAK4PFResidualCorrector = cms.EDProducer( "LXXXCorrectorProducer",
    algorithm = cms.string( "AK4PFHLT" ),
    level = cms.string( "L2L3Residual" )
)

process.hltAK4PFCorrector = cms.EDProducer("ChainedJetCorrectorProducer",
    correctors = cms.VInputTag(["hltAK4PFFastJetCorrector", "hltAK4PFRelativeCorrector", "hltAK4PFAbsoluteCorrector", "hltAK4PFResidualCorrector" ])
)
process.scoutingPFJetCorrected = cms.EDProducer("CorrectedPFJetProducer",
    correctors = cms.VInputTag(["hltAK4PFCorrector"]),
    src = cms.InputTag("scoutingToRecoJets"),
)

#Part 2.2: Correction from JSON
if(options.isMC):
    eraToJEC = cms.string("")
else:
    eraToJEC = cms.string("Era2024ScoutingAll")

process.jecAppliedJetProducer = cms.EDProducer(
    "JecAppliedJetProducer",
    isDebug = cms.bool(False),  # set True to dump [JERC DEBUG] logs

    Jets = cms.PSet(
        srcAK4 = cms.InputTag("scoutingToRecoJets"),          # pat::JetCollection
        rho    = cms.InputTag("hltScoutingPFPacker", "rho"),
        Year   = cms.string("2024Scouting"),
        IsData = isDataBool,

        # Optional era ("" => None)
        Era    = eraToJEC,

        # --- Choose one of: "Nominal", "JES", "JER"
        SystKind    = cms.string("Nominal"),

        # If SystKind == "JES"
        JesSystName = cms.string("AbsoluteStat"),  # correction set key
        JesSystVar  = cms.string("Up"),            # "Up" | "Down"

        # If SystKind == "JER"
        JerVar      = cms.string("nom"),           # "nom" | "up" | "down"
        JerRegion   = cms.PSet(                    # optional gate
            etaMin = cms.double(0.0),
            etaMax = cms.double(999.0),
            ptMin  = cms.double(0.0),
            ptMax  = cms.double(1.0e9),
        ),
        JecConfig = cms.FileInPath("Run3ScoutingAnalysisTools/OfflineJetCorrector/data/JecConfigAK4.json"),
        JerToolConfig = cms.FileInPath("Run3ScoutingAnalysisTools/OfflineJetCorrector/data/jer_smear.json.gz"),
    ),
)
if(options.doJECUnc and options.isMC):
    process.jecAppliedJetProducerJECup = process.jecAppliedJetProducer.clone(
        Jets = dict(
            SystKind    = cms.string("JES"),
            JesSystName = cms.string("CMS_scale_j_Total"),
            JesSystVar  = cms.string("Up"),
        )
    )
    process.jecAppliedJetProducerJECdown = process.jecAppliedJetProducer.clone(
        Jets = dict(
            SystKind    = cms.string("JES"),
            JesSystName = cms.string("CMS_scale_j_Total"),
            JesSystVar  = cms.string("Down"),
        )
    )


#Part 4: analyzer
process.triggerEffs = cms.EDAnalyzer('TriggerEffs',
                                     isMC = cms.bool(options.isMC),
                                     hasReco = cms.bool(options.hasReco),
                                     triggerresults   = cms.InputTag("TriggerResults", "", "HLT"),
                                     ReadPrescalesFromFile = cms.bool( False ),
                                     AlgInputTag       = cms.InputTag("gtStage2Digis"),
                                     l1tAlgBlkInputTag = cms.InputTag("gtStage2Digis"),
                                     l1tExtBlkInputTag = cms.InputTag("gtStage2Digis"),
                                     luminosity = cms.double(options.lumi), #2024 luminosity (fb-1)
                                     crossSection = cms.double(options.crossSection), # cross section in fb
                                     l1Seeds           = cms.vstring(L1Info),
                                     l1Et = cms.InputTag("gtStage2Digis", "EtSum"),
                                     pfjets            = pfjetsTag,
                                     jetIDMode = cms.int32(2), #0 = no ID, 1 = same as regualr analysis, 2 = no charged energy fraction
                                     generatorName = cms.InputTag('generator'),
                                     truePileup        = truePileupTag,
                                     scoutingMuon = cms.InputTag('hltScoutingMuonPackerNoVtx'), #remove the NoVtx if 2023 data
                                     scoutingParticle = cms.InputTag("hltScoutingPFPacker"),
                                     muon_pt = cms.double(20),
                                     muon_eta = cms.double(2.4),
                                     muon_chi2 = cms.double(10),
                                     muon_trackLayers = cms.int32(5),
                                     muon_pixelHits = cms.int32(0),
                                     muon_muonHits = cms.int32(0),
                                     muon_matchedStation = cms.int32(1),
                                     matchingTolerance = cms.double(0.1),
                                     muon_iso_max = cms.double(0.10),
                                     debugTree = cms.bool(options.debugTree)
)

if(options.doJECUnc and options.isMC):
    process.triggerEffsJECup = process.triggerEffs.clone(
        pfjets = pfjetsTagUp
    )
    process.triggerEffsJECdown = process.triggerEffs.clone(
        pfjets = pfjetsTagDown
    )

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("tree_corrected.root")
                                   )
# Usually it is better to put producers on a task instead of a path
# but paths also work.
if(options.doJECOffline):
    if(options.doJECUnc and options.isMC):
        process.p = cms.Path(
            process.rhoFilter *
            process.scoutingToRecoJets *
            process.jecAppliedJetProducer *
            process.jecAppliedJetProducerJECup *
            process.jecAppliedJetProducerJECdown *
            process.gtStage2Digis *
            process.triggerEffs *
            process.triggerEffsJECup *
            process.triggerEffsJECdown
        )
    else:
        process.p = cms.Path(
            process.rhoFilter *
            process.scoutingToRecoJets *
            process.jecAppliedJetProducer *
            process.gtStage2Digis *
            process.triggerEffs
        )

else:
    process.p = cms.Path(
        process.scoutingToRecoJets *
        process.hltAK4PFFastJetCorrector *
        process.hltAK4PFRelativeCorrector *
        process.hltAK4PFAbsoluteCorrector *
        process.hltAK4PFResidualCorrector *
        process.hltAK4PFCorrector *
        process.scoutingPFJetCorrected *
        process.gtStage2Digis *
        process.triggerEffs
    )
#process.e = cms.EndPath(process.out)