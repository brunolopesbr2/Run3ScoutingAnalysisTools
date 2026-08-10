import FWCore.ParameterSet.Config as cms
import os
import FWCore.ParameterSet.VarParsing as VarParsing
import numpy as np

process = cms.Process("TrackMover")
options = VarParsing.VarParsing ('analysis')
options.register('isScouting',
                 True,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "If scouting or reco tracks should be used for vertexing"
    )
options.register('hasReco',
                 False,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "If there are reco tracks to compare with the scouting"
    )
#Will use the reco derived from the scouting if hasReco is turned to false, so deviation plots entries should all be 0
options.register('lumi',
                 109.99,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.float,
                 "Integrated luminosity for weighting"
    )
options.register('crossSection',
                 26.49,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.float,
                 "Cross Section for weighting"
    )
options.register('isMC',
                 False,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "If using MC or data"
    )
options.register('PUFile',
                 'PURatio_Full2024.npy',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Name of pileup correction file to use"
    )

options.register('useLooseJets',
                 False,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Whether to select loose or tight jets on the EventSkim"
)

options.register('validation',
                 False,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Validation mode. Disables the event veto."
)


## Trigger corrections to use
options.register('TriggerCorrectionsNominal',
                 'TriggerCorrections/weights_trigger_2024_nominal.npy',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Nominal value of the trigger efficiency corrections"
    )
options.register('TriggerCorrectionsUp',
                 'TriggerCorrections/weights_trigger_2024_up.npy',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Upper bound of the trigger efficiency corrections"
    )
options.register('TriggerCorrectionsDown',
                 'TriggerCorrections/weights_trigger_2024_down.npy',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Lower bound of the trigger efficiency corrections"
    )
options.register('TriggerCorrectionsBinEdge',
                 'TriggerCorrections/weights_trigger_2024_xedge.npy',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Upper bin edges in HT of the trigger corrections"
    )
# ------

options.register('doJEC',
                 True,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "If HLT jet corrections are applied"
)

options.parseArguments()
process.load("FWCore.MessageService.MessageLogger_cfi")
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)

#process.options.numberOfThreads=cms.untracked.uint32(2)
#process.options.numberOfStreams=cms.untracked.uint32(0)
process.MessageLogger.cerr.FwkSummary.reportEvery = 100
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(30000) )
PUCorrectionData = np.load(options.PUFile)

TriggerCorrectionNominal = np.load(options.TriggerCorrectionsNominal)
TriggerCorrectionUp = np.load(options.TriggerCorrectionsUp)
TriggerCorrectionDown = np.load(options.TriggerCorrectionsDown)
TriggerCorrectionBinEdge = np.load(options.TriggerCorrectionsBinEdge)

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        #MC test file
        #'/store/mc/RunIII2024Summer24MiniAOD/QCD-4Jets_Bin-HT-1000to1200_TuneCP5_13p6TeV_madgraphMLM-pythia8/MINIAODSIM/140X_mcRun3_2024_realistic_v26-v2/100000/00f7403b-49bf-4efd-9b8f-0398bd61d910.root'
        #'/store/user/brlopesd/StopStopbarTo2Dbar2D_M-200_CTau-1mm_Summer24_100k_v2/StopStopbarTo2Dbar2D_M-200_CTau-1mm_Summer24_100k_miniAOD_v2/250214_150834/0000/stop_dbar_miniAOD_1.root'
        #Data test file
        #'/store/data/Run2024D/ScoutingPFRun3/HLTSCOUT/v1/000/380/945/00000/cdf45723-07c4-4b41-9595-f368f2929369.root'
        #PF monitor file
        #'/store/data/Run2024D/ScoutingPFMonitor/MINIAOD/PromptReco-v1/000/380/306/00000/70ec6086-72c5-4562-82a8-1f043e645d59.root'
        #Run 384323 LS 8
        #'/store/data/Run2024G/ScoutingPFRun3/HLTSCOUT/v1/000/384/323/00000/8504e079-a736-4dc9-b4c1-913502212b99.root'
        #Run 385986 Era H
        #'/store/data/Run2024H/ScoutingPFRun3/HLTSCOUT/v1/000/385/986/00000/e1aeb0a8-0ec4-4202-9705-873887cbf8ac.root'
        #Run 381053 LS 74
        #'/store/data/Run2024E/ScoutingPFRun3/HLTSCOUT/v1/000/381/053/00000/c0ba031e-c25b-426a-975b-aa058276df6c.root'
        #Run 382255 LS 79
        #'/store/data/Run2024F/ScoutingPFRun3/HLTSCOUT/v1/000/382/255/00000/ac42dc85-581c-438a-b536-3abbfe4eef90.root'
        #Era E Run 381544 LS 1096
        '/store/data/Run2024E/ScoutingPFRun3/HLTSCOUT/v1/000/381/544/00000/410771c4-3829-4638-8b0a-5126be4cacc9.root'
        #New lifetime stop sample
        #'/StopStopbarTo2Dbar2D_M-400_ctau-0p1mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-400_ctau-0p1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER'
        #offline test
        #'file:testDataFile.root'
    )
)

process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")

#Choosing the GlobalTag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag

if(options.isMC):
    process.GlobalTag = GlobalTag(process.GlobalTag, '140X_mcRun3_2024_realistic_v26', '')  
    truePileupTag = cms.InputTag("slimmedAddPileupInfo")
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_HLT_v3', '')
    truePileupTag = cms.InputTag("")
    
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

process.load("RecoVertex.BeamSpotProducer.BeamSpot_cfi")
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

#from RecoVertex.BeamSpotProducer.BeamSpotOnline_cfi import onlineBeamSpotProducer
#process.onlineBeamSpot = onlineBeamSpotProducer.clone(
#    useTransientRecord = cms.bool(True)
#)

process.load("EventFilter.L1TRawToDigi.gtStage2Digis_cfi")
process.gtStage2Digis.InputLabel = cms.InputTag( "hltFEDSelectorL1" )



process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("tree_trackMover.root")
                                   )

if(options.isScouting):
    #unpacker
    scoutingTrackTag = cms.InputTag('hltScoutingTrackPacker')
    scoutingPVTag = cms.InputTag("hltScoutingPrimaryVertexPacker","primaryVtx")
    scoutingPFTag = cms.InputTag("hltScoutingPFPacker")
    pfCandTag = cms.InputTag("")
    lostTrackTag = cms.InputTag("")

    #skim
    if(options.doJEC):
        pfjetsTag = cms.InputTag("scoutingPFJetCorrected")
        patjetsTag = cms.InputTag("")
    else:
        pfjetsTag = cms.InputTag("scoutingToRecoJets")
        patjetsTag = cms.InputTag("")

    #tree maker
    skimPFJetsTag = cms.InputTag("triggerFilter","pfjets")
    skimPatJetsTag = cms.InputTag("")
    pvTag = cms.InputTag("hltScoutingUnpackProducer","PrimaryVertex")
else:
    #unpacker
    scoutingTrackTag = cms.InputTag("")
    scoutingPVTag = cms.InputTag("")
    scoutingPFTag = cms.InputTag("")
    pfCandTag = cms.InputTag("packedPFCandidates")
    lostTrackTag = cms.InputTag("lostTracks")

    #skim
    pfjetsTag = cms.InputTag("")
    patjetsTag = cms.InputTag("slimmedJets")

    #tree maker
    skimPFJetsTag = cms.InputTag("")
    skimPatJetsTag = cms.InputTag("triggerFilter","patjets")
    pvTag = cms.InputTag("offlineSlimmedPrimaryVertices")

if(options.hasReco):
    recoTrackTag = cms.InputTag("displacedTracks")
else:
    recoTrackTag = cms.InputTag("hltScoutingUnpackProducer","Track")

#The L1 seeds used for JetHT
L1Info = ["L1_HTT200er", "L1_HTT255er", "L1_HTT280er", "L1_HTT320er", "L1_HTT360er", "L1_HTT400er", "L1_HTT450er", "L1_ETT2000", "L1_SingleJet180", "L1_SingleJet200", "L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5", "L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5", "L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5"]

    
# Input tags to the EDProducers

#create reco::PFJet
process.scoutingToRecoJets = cms.EDProducer('Run3ScoutingPFJetToRecoPFJetProducer',
                                     scoutingPFJet = cms.InputTag("hltScoutingPFPacker")
                                     )

#Jet corrector
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


process.hltScoutingUnpackProducer = cms.EDProducer('HLTScoutingUnpackProducer',
                                                   scoutingTrack = scoutingTrackTag,
                                                   scoutingPrimaryVertex = scoutingPVTag,
                                                   scoutingParticle = scoutingPFTag,
                                                   pfCand = pfCandTag,
                                                   lostTrack = lostTrackTag,
                                                   isScouting = cms.bool(options.isScouting),
                                                   producePFCHSCandidate = cms.bool(False),
                                                   mightGet = cms.optional.untracked.vstring
                                                   )


process.triggerFilter = cms.EDFilter('TriggerFilter',
                                     isMC = cms.bool(options.isMC),
                                     triggerresults   = cms.InputTag("TriggerResults", "", "HLT"),
                                     AlgInputTag       = cms.InputTag("gtStage2Digis"),
                                     l1tExtBlkInputTag = cms.InputTag("gtStage2Digis"),
                                     isScouting = cms.bool(options.isScouting),
                                     luminosity = cms.double(options.lumi), #2024 luminosity (fb-1)
                                     crossSection = cms.double(options.crossSection), # cross section in fb
                                     truePileup        = truePileupTag,
                                     PUCorrectionArray = cms.vdouble(*PUCorrectionData.flatten().tolist()),
                                     L1et = cms.InputTag("gtStage2Digis", "EtSum"),
                                     L1HTThreshold = cms.double(0.0),
                                     l1Seeds           = cms.vstring(L1Info),
                                     pfjets            = pfjetsTag,
                                     patjets           = patjetsTag,
                                     generatorName = cms.InputTag('generator'),
                                     genJet_src = cms.InputTag('slimmedGenJets',''),
                                     storeGenJets = cms.bool(False),
                                     scoutingParticle = scoutingPFTag,
                                     muons = cms.InputTag("hltScoutingMuonPackerNoVtx"),
                                     triggerNominal = cms.vdouble(*TriggerCorrectionNominal.flatten().tolist()),
                                     triggerUp = cms.vdouble(*TriggerCorrectionUp.flatten().tolist()),
                                     triggerDown = cms.vdouble(*TriggerCorrectionDown.flatten().tolist()),
                                     triggerEdge = cms.vdouble(*TriggerCorrectionBinEdge.flatten().tolist()),
                                     useLooseJets = cms.bool(options.useLooseJets),
                                     val = cms.bool(options.validation)
                                     )

process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
    trackMover = cms.PSet(
        initialSeed = cms.untracked.uint32(1234),
        engineName = cms.untracked.string("TRandom3")
    )
)

process.trackMover = cms.EDProducer('TrackMover',
                                    tracks_src = cms.InputTag("hltScoutingUnpackProducer", "Track"),
                                    primary_vertices_src = cms.InputTag("hltScoutingUnpackProducer", "PrimaryVertex"),
                                    jets_src = cms.InputTag("triggerFilter", "pfjets"),
                                    muons_src = cms.InputTag("hltScoutingMuonPackerNoVtx"),
                                    isMC = cms.bool(options.isMC),
                                    min_jet_pt = cms.double(30.),
                                    min_jet_ntracks = cms.int32(2),
                                    max_jet_track_dR = cms.double(0.4),
                                    njets = cms.int32(2),
                                    tau = cms.double(1.0),
                                    track_keep_prob = cms.double(1.),
                                    sig_theta = cms.double(0.2),
                                    sig_phi = cms.double(0.2),
                                    trackEffVariation = cms.string("ratio") #ratio, ratio_plus1sigma, ratio_minus1sigma
)

process.Vertexer = cms.EDProducer('Vertexer',
                                  generatorName = cms.InputTag('generator'),
                                  luminosity = cms.double(options.lumi), #2024 luminosity (fb-1)
                                  crossSection = cms.double(options.crossSection), # cross section in fb
                                  truePileup        = truePileupTag,
                                  PUCorrectionArray = cms.vdouble(*PUCorrectionData.flatten().tolist()),
                                  isMC = cms.bool(options.isMC),
                                  seed_tracks_src = cms.InputTag('trackMover', 'outputTracks'),
                                  pfjets = skimPFJetsTag,
                                  pt_min_cut = cms.double(1.0),
                                  dxySig_min_cut = cms.double(4.0),
                                  dxySig_max_cut = cms.double(-1), #dxySig between 2.5 and 4.0 for a control region, dxySig>4 with no max for signal region
                                  npixelHits_min_cut = cms.int32(2),
                                  nstripHits_min_cut = cms.int32(1),
                                  ntrackerLayers_min_cut = cms.int32(5),
                                  #kvr_params = kvr_params,
                                  #do_track_refinement = cms.bool(False), # remove tracks + trim out tracks with IP significance larger than trackrefine_sigmacut and trackrefine_trimmax, respectively
                                  resolve_split_vertices_loose = cms.bool(False), # an alternative merging routine with `loose` criteria, to merge any nearby vertices within a given dist or significance
                                  resolve_split_vertices_tight = cms.bool(True), # merging routine, based on vtx dphi and dVV
                                  investigate_merged_vertices = cms.bool(False), # investigate quality cuts on merged vertices from tight merging
                                  #resolve_shared_jets = cms.bool(True),       # shared-jet mitigation
                                  #resolve_shared_jets_src = cms.InputTag('selectedPatJets'),
                                  beamspot_src = cms.InputTag('offlineBeamSpot'),
                                  n_tracks_per_seed_vertex = cms.int32(2),
                                  max_seed_vertex_chi2 = cms.double(5),
                                  use_2d_vertex_dist = cms.bool(False),
                                  use_2d_track_dist = cms.bool(False),
                                  merge_anyway_dist = cms.double(-1),
                                  merge_anyway_sig = cms.double(4), # merging criteria for loose merging (*only* if resolve_split_vertices_loose is True)
                                  merge_shared_dist = cms.double(-1),
                                  merge_shared_sig = cms.double(3), # default merging shared-track vertices
                                  max_track_vertex_dist = cms.double(-1),
                                  max_track_vertex_sig = cms.double(5), # default track arbitration
                                  min_track_vertex_sig_to_remove = cms.double(2.0), # default track arbitration
                                  remove_one_track_at_a_time = cms.bool(True),
                                  max_nm1_refit_dist3 = cms.double(0.003),
                                  max_nm1_refit_distz = cms.double(-1),
                                  max_nm1_refit_count = cms.int32(-1),
                                  #trackrefine_sigmacut = cms.double(5), # track refinement criteria (*only* if do_track_refinement = True)
                                  #trackrefine_trimmax = cms.double(5), # track refinement criteria (*only* if do_track_refinement = True)
                                  verbose = cms.bool(False),
                                  weightMap = cms.InputTag("triggerFilter", "weightMap")
                                  )

process.vertexEffTree = cms.EDAnalyzer('VertexEffAnalyzer',
                                        primary_vertices = cms.InputTag("hltScoutingUnpackProducer", "PrimaryVertex"),
                                        original_tracks = cms.InputTag("hltScoutingUnpackProducer", "Track"),
                                        tracks = cms.InputTag('trackMover', 'outputTracks'),
                                        moved_tracks = cms.InputTag('trackMover', 'movedTracks'),
                                        move_vertex = cms.InputTag('trackMover', 'moveVertex'),
                                        vertices = cms.InputTag("Vertexer"),
                                        n_presel_jets = cms.InputTag('trackMover', 'npreseljets'),
                                        moved_jets = cms.InputTag('trackMover', 'jetsUsed'),
                                        flight_axis = cms.InputTag('trackMover', 'flightAxis'),
                                        matchVertexDistance = cms.double(0.01),
                                        isMC = cms.bool(options.isMC),
                                        weightMap = cms.InputTag("triggerFilter", "weightMap")
                                      )



# Usually it is better to put producers on a task instead of a path
# but paths also work.
if(options.doJEC):
    process.p = cms.Path(
        process.scoutingToRecoJets *
        process.hltAK4PFFastJetCorrector *
        process.hltAK4PFRelativeCorrector *
        process.hltAK4PFAbsoluteCorrector *
        process.hltAK4PFResidualCorrector *
        process.hltAK4PFCorrector *
        process.scoutingPFJetCorrected *
        process.gtStage2Digis *
        process.triggerFilter *
        process.hltScoutingUnpackProducer *
        process.trackMover *
        process.offlineBeamSpot *
        process.Vertexer *
        process.vertexEffTree
    )
else:
    process.p = cms.Path(
        process.scoutingToRecoJets *
        process.gtStage2Digis *
        process.triggerFilter *
        process.hltScoutingUnpackProducer *
        process.trackMover *
        process.offlineBeamSpot *
        process.Vertexer *
        process.vertexEffTree
    )

#process.out = cms.OutputModule("PoolOutputModule",
#    fileName = cms.untracked.string("output_edm.root"),
#    outputCommands = cms.untracked.vstring("keep *")
#)

#process.outpath = cms.EndPath(process.out)
