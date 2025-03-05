import FWCore.ParameterSet.Config as cms

process = cms.Process("VertexProducer")

process.load("FWCore.MessageService.MessageLogger_cfi")
#process.options = cms.untracked.PSet(
#    wantSummary = cms.untracked.bool(True)
#)

process.MessageLogger.cerr.FwkSummary.reportEvery = 100
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring( 
        'file:scout_unpacked.root'
    )
)


process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')


#Choosing the GlobalTag  
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_Prompt_v4', '')  #GT for data

process.load("RecoVertex.BeamSpotProducer.BeamSpot_cfi")
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

# Input tags to the EDProducer
process.Vertexer = cms.EDProducer('Vertexer',
                                  seed_tracks_src = cms.InputTag('hltScoutingUnpackProducer', 'Track'),
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
                                  merge_shared_sig = cms.double(4), # default merging shared-track vertices  
                                  max_track_vertex_dist = cms.double(-1),
                                  max_track_vertex_sig = cms.double(5), # default track arbitration
                                  min_track_vertex_sig_to_remove = cms.double(1.5), # default track arbitration
                                  remove_one_track_at_a_time = cms.bool(True),
                                  max_nm1_refit_dist3 = cms.double(-1),
                                  max_nm1_refit_distz = cms.double(0.005),
                                  max_nm1_refit_count = cms.int32(-1),
                                  #trackrefine_sigmacut = cms.double(5), # track refinement criteria (*only* if do_track_refinement = True)
                                  #trackrefine_trimmax = cms.double(5), # track refinement criteria (*only* if do_track_refinement = True)
                                  verbose = cms.bool(False),
                                  )

# Save only the scouting collections on the output file
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('scout_withRecoVertex.root'),
)

# Usually it is better to put producers on a task instead of a path
# but paths also work.
process.p = cms.Path(process.offlineBeamSpot+process.Vertexer)
process.e = cms.EndPath(process.out)
