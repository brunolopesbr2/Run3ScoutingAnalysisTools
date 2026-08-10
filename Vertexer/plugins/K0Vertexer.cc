// -*- C++ -*-
//
// Package:    Run3ScoutingAnalysisTools/K0Vertexer
// Class:      K0Vertexer
//
/**\class K0Vertexer K0Vertexer.cc Run3ScoutingAnalysisTools/Vertexer/plugins/K0Vertexer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Bruno Lopes
//         Created:  Wed, 04 Sep 2024 12:37:22 GMT
//
//

// system include files
#include <memory>

#include "CondFormats/DataRecord/interface/BeamSpotOnlineHLTObjectsRcd.h"
#include "CondFormats/BeamSpotObjects/interface/BeamSpotObjects.h"
#include "CondFormats/BeamSpotObjects/interface/BeamSpotOnlineObjects.h"

#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "MagneticField/Engine/interface/MagneticField.h"

#include "TLorentzVector.h"
#include "TVector3.h"
// user include files
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/Utilities/interface/ESGetToken.h"
#include "DataFormats/Common/interface/ValueMap.h"

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/JetReco/interface/PFJet.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
//Scouting data formats
#include "DataFormats/Scouting/interface/Run3ScoutingElectron.h"
#include "DataFormats/Scouting/interface/Run3ScoutingPhoton.h"
#include "DataFormats/Scouting/interface/Run3ScoutingPFJet.h"
#include "DataFormats/Scouting/interface/Run3ScoutingVertex.h"
#include "DataFormats/Scouting/interface/Run3ScoutingTrack.h"
#include "DataFormats/Scouting/interface/Run3ScoutingMuon.h"
#include "DataFormats/Scouting/interface/Run3ScoutingParticle.h"

//Vertex tools
#include "RecoVertex/KalmanVertexFit/interface/KalmanVertexFitter.h"
#include "RecoVertex/VertexTools/interface/VertexDistance3D.h"
#include "RecoVertex/VertexTools/interface/VertexDistanceXY.h"
#include "TrackingTools/IPTools/interface/IPTools.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "TH1.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"
using namespace edm;

//
// class declaration
//

class K0Vertexer : public edm::stream::EDProducer<> {
public:
  ~K0Vertexer() override;

  explicit K0Vertexer(edm::ParameterSet const& params);

  

private:
  typedef std::set<reco::TrackRef> track_set;
  typedef std::vector<reco::TrackRef> track_vec;

  void beginStream(edm::StreamID) override;
  void endStream() override;
  void produce(edm::Event&, const edm::EventSetup&) override;

  //const edm::EDGetTokenT<GenEventInfoProduct> GeneratorToken_;
  double luminosity;
  double crossSection;
  //const edm::EDGetTokenT<std::vector<PileupSummaryInfo>> truePileupToken;
  int truePU;
  //std::vector<double> PUCorrectionArray;
  bool isMC;

  TH1D* h_dxyErr_weighted_sum_barrel;
  TH1D* h_dszErr_weighted_sum_barrel;
  TH1D* h_dszdxyCov_weighted_sum_barrel;
  TH1D* h_dxyErr_weighted_sq_sum_barrel;
  TH1D* h_dszErr_weighted_sq_sum_barrel;
  TH1D* h_dszdxyCov_weighted_sq_sum_barrel;
  TH1D* h_weight_sum_barrel;
  TH1D* h_weight_sq_sum_barrel;

  TH1D* h_dxyErr_weighted_sum_disk;
  TH1D* h_dszErr_weighted_sum_disk;
  TH1D* h_dszdxyCov_weighted_sum_disk;
  TH1D* h_dxyErr_weighted_sq_sum_disk;
  TH1D* h_dszErr_weighted_sq_sum_disk;
  TH1D* h_dszdxyCov_weighted_sq_sum_disk;
  TH1D* h_weight_sum_disk;
  TH1D* h_weight_sq_sum_disk;

  TH1D* h_dxyErr_weighted_sum_barrel_jetMatched;
  TH1D* h_dszErr_weighted_sum_barrel_jetMatched;
  TH1D* h_dszdxyCov_weighted_sum_barrel_jetMatched;
  TH1D* h_dxyErr_weighted_sq_sum_barrel_jetMatched;
  TH1D* h_dszErr_weighted_sq_sum_barrel_jetMatched;
  TH1D* h_dszdxyCov_weighted_sq_sum_barrel_jetMatched;
  TH1D* h_weight_sum_barrel_jetMatched;
  TH1D* h_weight_sq_sum_barrel_jetMatched;

  TH1D* h_dxyErr_weighted_sum_disk_jetMatched;
  TH1D* h_dszErr_weighted_sum_disk_jetMatched;
  TH1D* h_dszdxyCov_weighted_sum_disk_jetMatched;
  TH1D* h_dxyErr_weighted_sq_sum_disk_jetMatched;
  TH1D* h_dszErr_weighted_sq_sum_disk_jetMatched;
  TH1D* h_dszdxyCov_weighted_sq_sum_disk_jetMatched;
  TH1D* h_weight_sum_disk_jetMatched;
  TH1D* h_weight_sq_sum_disk_jetMatched;
  
  const double pt_min_cut;
  const double dxySig_min_cut;
  const double dxySig_max_cut;
  const int npixelHits_min_cut;
  const int nstripHits_min_cut;
  const int ntrackerLayers_min_cut;
  const int n_tracks_per_seed_vertex;
  const double max_seed_vertex_chi2;
  const bool use_2d_vertex_dist;
  const bool use_2d_track_dist;
  const bool remove_one_track_at_a_time;
  const double merge_shared_dist;
  const double merge_shared_sig;
  const double max_track_vertex_dist;
  const double max_track_vertex_sig;
  const double min_track_vertex_sig_to_remove;
  const bool resolve_split_vertices_loose;
  const bool resolve_split_vertices_tight;
  const double merge_anyway_sig;
  const double merge_anyway_dist;
  const double max_nm1_refit_dist3;
  const double max_nm1_refit_distz;
  const int max_nm1_refit_count;
  const bool investigate_merged_vertices;
  const bool verbose;
  const edm::ESGetToken<BeamSpotOnlineObjects, BeamSpotOnlineHLTObjectsRcd> bsOnlineToken_;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_token;
  const edm::EDGetTokenT<std::vector<reco::Track>> seed_tracks_token_;
  const edm::EDGetTokenT<std::vector<reco::PFJet> >  pfjetsToken_;
  const edm::ESGetToken<TransientTrackBuilder, TransientTrackRecord> token_builder;
  const edm::EDGetTokenT<std::map<std::string, float>> weightsToken_;
  
  edm::EDPutTokenT<reco::VertexCollection> putToken_;
  // ----------member data ---------------------------

  VertexDistanceXY vertex_dist_2d;
  VertexDistance3D vertex_dist_3d;

  KalmanVertexFitter kv_reco;
  std::vector<TransientVertex> kv_reco_dropin(std::vector<reco::TransientTrack> & ttks) {
    if (ttks.size() < 2)
      return std::vector<TransientVertex>();
    std::vector<TransientVertex> v(1, kv_reco.vertex(ttks));
    if (v[0].normalisedChiSquared() > 5)
      return std::vector<TransientVertex>();
    return v;
  }
  
  bool is_track_subset(const track_set & a, const track_set & b) const {
    bool is_subset = true;
    const track_set& smaller = a.size() <= b.size() ? a : b;
    const track_set& bigger = a.size() <= b.size() ? b : a;
    
    for (auto t : smaller)
      if (bigger.count(t) < 1) {
	is_subset = false;
	break;
      }
    
    return is_subset;
  }
  
  
  Measurement1D vertex_dist(const reco::Vertex & v0, const reco::Vertex & v1) {
    if (use_2d_vertex_dist)
      return vertex_dist_2d.distance(v0, v1);
    else
      return vertex_dist_3d.distance(v0, v1);
  }
  
    track_set vertex_track_set(const reco::Vertex & v, const double min_weight = 0.5) const {
      track_set result;

      for (auto it = v.tracks_begin(), ite = v.tracks_end(); it != ite; ++it) {
        const double w = v.trackWeight(*it);
        const bool use = w >= min_weight;
        assert(use);
        if (use)
          result.insert(it->castTo<reco::TrackRef>());
      }

      return result;
    }

  
  
  std::pair<bool, Measurement1D> track_dist(const reco::TransientTrack& t, const reco::Vertex & v) const {
    if (use_2d_track_dist)
      return IPTools::absoluteTransverseImpactParameter(t, v);
    else
      return IPTools::absoluteImpactParameter3D(t, v);
  }

  track_vec vertex_track_vec(const reco::Vertex & v, const double min_weight = 0.5) const {
    track_set s = vertex_track_set(v, min_weight);
    return track_vec(s.begin(), s.end());
  }

  template <typename T>
  void print_track_set(const T& ts) const {
    for (auto r : ts)
      printf(" %u", r.key());
  }
  
  template <typename T>
  void print_track_set(const T & ts, const reco::Vertex & v) const {
    for (auto r : ts)
      printf(" %u%s", r.key(), (v.trackWeight(r) < 0.5 ? "!" : ""));
  }
  
  void print_track_set(const reco::Vertex & v) const {
    for (auto r = v.tracks_begin(), re = v.tracks_end(); r != re; ++r)
      printf(" %lu%s", r->key(), (v.trackWeight(*r) < 0.5 ? "!" : ""));
  }
  
  
};


//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//

K0Vertexer::K0Vertexer(edm::ParameterSet const& params)
  :
  //GeneratorToken_(consumes(params.getParameter<edm::InputTag>("generatorName"))),
  luminosity(params.existsAs<double>("luminosity") ? params.getParameter<double>  ("luminosity") : 1.0),
  crossSection(params.existsAs<double>("crossSection") ? params.getParameter<double>  ("crossSection") : 1.0),
  //truePileupToken(consumes<std::vector<PileupSummaryInfo>>(params.getParameter<edm::InputTag>("truePileup"))),
  //PUCorrectionArray(params.getParameter<std::vector<double>>("PUCorrectionArray")),
  isMC(params.existsAs<bool>("isMC") ?  params.getParameter<bool>  ("isMC") : false),
  pt_min_cut(params.getParameter<double>("pt_min_cut")),
  dxySig_min_cut(params.getParameter<double>("dxySig_min_cut")),
  dxySig_max_cut(params.getParameter<double>("dxySig_max_cut")),
  npixelHits_min_cut(params.getParameter<int>("npixelHits_min_cut")),
  nstripHits_min_cut(params.getParameter<int>("nstripHits_min_cut")),
  ntrackerLayers_min_cut(params.getParameter<int>("ntrackerLayers_min_cut")),
  n_tracks_per_seed_vertex(params.getParameter<int>("n_tracks_per_seed_vertex")),
  max_seed_vertex_chi2(params.getParameter<double>("max_seed_vertex_chi2")),
  use_2d_vertex_dist(params.getParameter<bool>("use_2d_vertex_dist")),
  use_2d_track_dist(params.getParameter<bool>("use_2d_track_dist")),
  remove_one_track_at_a_time(params.getParameter<bool>("remove_one_track_at_a_time")),
  merge_shared_dist(params.getParameter<double>("merge_shared_dist")),
  merge_shared_sig(params.getParameter<double>("merge_shared_sig")),
  max_track_vertex_dist(params.getParameter<double>("max_track_vertex_dist")),
  max_track_vertex_sig(params.getParameter<double>("max_track_vertex_sig")),
  min_track_vertex_sig_to_remove(params.getParameter<double>("min_track_vertex_sig_to_remove")),
  resolve_split_vertices_loose(params.getParameter<bool>("resolve_split_vertices_loose")),
  resolve_split_vertices_tight(params.getParameter<bool>("resolve_split_vertices_tight")),
  merge_anyway_sig(params.getParameter<double>("merge_anyway_sig")),
  merge_anyway_dist(params.getParameter<double>("merge_anyway_dist")),
  max_nm1_refit_dist3(params.getParameter<double>("max_nm1_refit_dist3")),
  max_nm1_refit_distz(params.getParameter<double>("max_nm1_refit_distz")),
  max_nm1_refit_count(params.getParameter<int>("max_nm1_refit_count")),
  investigate_merged_vertices(params.getParameter<bool>("investigate_merged_vertices")),
  verbose(params.getParameter<bool>("verbose")),
  bsOnlineToken_(esConsumes<BeamSpotOnlineObjects, BeamSpotOnlineHLTObjectsRcd>()),
  beamspot_token(consumes<reco::BeamSpot>(params.getParameter<edm::InputTag>("beamspot_src"))),
  seed_tracks_token_(consumes(params.getParameter<edm::InputTag>("seed_tracks_src"))),
  pfjetsToken_(consumes<std::vector<reco::PFJet>>(params.getParameter<edm::InputTag>("pfjets"))),
  token_builder(esConsumes(edm::ESInputTag("", "TransientTrackBuilder"))),
  weightsToken_(consumes<std::map<std::string, float>>(edm::InputTag("K0Filter", "weightMap"))),
  putToken_{produces()} {
}


K0Vertexer::~K0Vertexer() {}

//
// member functions
//


// ------------ method called to produce the data  ------------
void K0Vertexer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  //////////////////////////////////////////////////////////////////////                                                                              
  // DataFormats setup and track preselection                                                                                
  ////////////////////////////////////////////////////////////////////// 
  const auto& bs = iSetup.getData(bsOnlineToken_);
  reco::BeamSpot::CovarianceMatrix onlineCovariance;
  for(uint i=0; i<7; i++){
    for(uint j=i; j<7; j++){
      onlineCovariance(i,j) = bs.covariance(i,j);
    }
  }
  reco::BeamSpot::Point onlinePosition(bs.x(), bs.y(), bs.z());
  auto beamspot = std::make_unique<reco::BeamSpot>(onlinePosition,
					  bs.sigmaZ(),
					  bs.dxdz(),
					  bs.dydz(),
					  bs.beamWidthX(),
					  onlineCovariance,
					  static_cast<reco::BeamSpot::BeamType>(bs.beamType())
					  );
  beamspot->setBeamWidthY(bs.beamWidthY());
  beamspot->setEmittanceX(bs.emittanceX());
  beamspot->setEmittanceY(bs.emittanceY());
  beamspot->setbetaStar(bs.betaStar());
  
  //edm::Handle<reco::BeamSpot> beamspot; //temp while testing online beam spot
  //iEvent.getByToken(beamspot_token, beamspot); //same as above
  const double bsx = beamspot->position().x();
  const double bsy = beamspot->position().y();
  const double bsz = beamspot->position().z();
  const reco::Vertex fake_bs_vtx(beamspot->position(), beamspot->covariance3D());

  //double genWeight = 1.0;
  double weight = 1.0;
  
  if(isMC){
    /*
    edm::Handle<GenEventInfoProduct> generatorHandle;
    iEvent.getByToken(GeneratorToken_, generatorHandle);
    genWeight = generatorHandle->weight();
    weight = genWeight*luminosity*crossSection;

    edm::Handle<std::vector<PileupSummaryInfo>> pileup;
    iEvent.getByToken(truePileupToken, pileup);
    std::vector<PileupSummaryInfo>::const_iterator pileupIter;
    for(pileupIter = pileup->begin(); pileupIter != pileup->end(); ++pileupIter){
      if (pileupIter->getBunchCrossing() == 0) {
	truePU = pileupIter->getTrueNumInteractions();
      }
    }
    if(truePU>99) truePU = 99;
    weight *= PUCorrectionArray[truePU];
    */
    edm::Handle<std::map<std::string, float>> weightMap;
    iEvent.getByToken(weightsToken_, weightMap);
    weight = weightMap->at("correctedNominal");
  }

  //Get jets for matching to tracks
  Handle<std::vector<reco::PFJet> > pfjetsH;
  iEvent.getByToken(pfjetsToken_, pfjetsH);
  std::vector<reco::PFJet> pfJetVector;

  if(pfjetsH.isValid()){
    for (auto jets_iter = pfjetsH->begin(); jets_iter != pfjetsH->end(); ++jets_iter) {
      pfJetVector.push_back(*jets_iter);
    }
  }
  
  //Get the Transient Track Builder
  auto const &tt_builder = iSetup.getData(token_builder);

  //Get the reco tracks from the events
  edm::Handle<std::vector<reco::Track>> seed_track_handle;
  iEvent.getByToken(seed_tracks_token_, seed_track_handle);

  // Build the references to the tracks
  std::vector<reco::TrackRef> seed_track_refs;
  std::map<reco::TrackRef, size_t> seed_track_index_map;
  
  for (size_t i_tk = 0; i_tk < seed_track_handle->size(); i_tk++){
    const edm::Ref<reco::TrackCollection> tk_ref(seed_track_handle, i_tk);
    reco::TransientTrack ttk = tt_builder.build(tk_ref);
    std::pair<bool, Measurement1D> ttk_dist = IPTools::absoluteTransverseImpactParameter(ttk, fake_bs_vtx);
    //std::pair<bool, Measurement1D> ttk_dist = track_dist(ttk, fake_bs_vtx);
    float IP_sig = ttk_dist.second.significance();
    if ((tk_ref->pt()>pt_min_cut) && (tk_ref->hitPattern().numberOfValidPixelHits() > npixelHits_min_cut) && (tk_ref->hitPattern().numberOfValidStripHits() > nstripHits_min_cut) && (tk_ref->hitPattern().trackerLayersWithMeasurement() > ntrackerLayers_min_cut) && (fabs(tk_ref->eta())<2.4)){
      //if ((tk_ref->pt()>0.9) && (fabs(tk_ref->eta())<2.4)){
      if(fabs(tk_ref->eta())<1.5){
	h_dxyErr_weighted_sum_barrel->Fill(tk_ref->pt(),weight*tk_ref->dxyError());
	h_dszErr_weighted_sum_barrel->Fill(tk_ref->pt(),weight*tk_ref->dszError());
	h_dszdxyCov_weighted_sum_barrel->Fill(tk_ref->pt(),weight*fabs(tk_ref->covariance(3,4)));
	h_dxyErr_weighted_sq_sum_barrel->Fill(tk_ref->pt(),weight*pow(tk_ref->dxyError(),2));
	h_dszErr_weighted_sq_sum_barrel->Fill(tk_ref->pt(),weight*pow(tk_ref->dszError(),2));
	h_dszdxyCov_weighted_sq_sum_barrel->Fill(tk_ref->pt(),weight*pow(tk_ref->covariance(3,4),2));
	h_weight_sum_barrel->Fill(tk_ref->pt(),weight);
	h_weight_sq_sum_barrel->Fill(tk_ref->pt(),pow(weight,2));
      }
      else{
	h_dxyErr_weighted_sum_disk->Fill(tk_ref->pt(),weight*tk_ref->dxyError());
	h_dszErr_weighted_sum_disk->Fill(tk_ref->pt(),weight*tk_ref->dszError());
	h_dszdxyCov_weighted_sum_disk->Fill(tk_ref->pt(),weight*fabs(tk_ref->covariance(3,4)));
	h_dxyErr_weighted_sq_sum_disk->Fill(tk_ref->pt(),weight*pow(tk_ref->dxyError(),2));
	h_dszErr_weighted_sq_sum_disk->Fill(tk_ref->pt(),weight*pow(tk_ref->dszError(),2));
	h_dszdxyCov_weighted_sq_sum_disk->Fill(tk_ref->pt(),weight*pow(tk_ref->covariance(3,4),2));
	h_weight_sum_disk->Fill(tk_ref->pt(),weight);
	h_weight_sq_sum_disk->Fill(tk_ref->pt(),pow(weight,2));
      }

      int i_jet = 0;
      int i_bestMatch = -1;
      float bestDeltaR = 9999999;
      for (auto jet: pfJetVector) {
	float deltaR = reco::deltaR(tk_ref->eta(),tk_ref->phi(),jet.eta(),jet.phi());
	if((deltaR<bestDeltaR) && (deltaR<0.4)){
	  i_bestMatch = i_jet;
	  bestDeltaR = deltaR;
	}
	i_jet++;
      }

      if(i_bestMatch!=-1){
	if(fabs(tk_ref->eta())<1.5){
	  h_dxyErr_weighted_sum_barrel_jetMatched->Fill(tk_ref->pt(),weight*tk_ref->dxyError());
	  h_dszErr_weighted_sum_barrel_jetMatched->Fill(tk_ref->pt(),weight*tk_ref->dszError());
	  h_dszdxyCov_weighted_sum_barrel_jetMatched->Fill(tk_ref->pt(),weight*fabs(tk_ref->covariance(3,4)));
	  h_dxyErr_weighted_sq_sum_barrel_jetMatched->Fill(tk_ref->pt(),weight*pow(tk_ref->dxyError(),2));
	  h_dszErr_weighted_sq_sum_barrel_jetMatched->Fill(tk_ref->pt(),weight*pow(tk_ref->dszError(),2));
	  h_dszdxyCov_weighted_sq_sum_barrel_jetMatched->Fill(tk_ref->pt(),weight*pow(tk_ref->covariance(3,4),2));
	  h_weight_sum_barrel_jetMatched->Fill(tk_ref->pt(),weight);
	  h_weight_sq_sum_barrel_jetMatched->Fill(tk_ref->pt(),pow(weight,2));
	}
	else{
	  h_dxyErr_weighted_sum_disk_jetMatched->Fill(tk_ref->pt(),weight*tk_ref->dxyError());
	  h_dszErr_weighted_sum_disk_jetMatched->Fill(tk_ref->pt(),weight*tk_ref->dszError());
	  h_dszdxyCov_weighted_sum_disk_jetMatched->Fill(tk_ref->pt(),weight*fabs(tk_ref->covariance(3,4)));
	  h_dxyErr_weighted_sq_sum_disk_jetMatched->Fill(tk_ref->pt(),weight*pow(tk_ref->dxyError(),2));
	  h_dszErr_weighted_sq_sum_disk_jetMatched->Fill(tk_ref->pt(),weight*pow(tk_ref->dszError(),2));
	  h_dszdxyCov_weighted_sq_sum_disk_jetMatched->Fill(tk_ref->pt(),weight*pow(tk_ref->covariance(3,4),2));
	  h_weight_sum_disk_jetMatched->Fill(tk_ref->pt(),weight);
	  h_weight_sq_sum_disk_jetMatched->Fill(tk_ref->pt(),pow(weight,2));
	}
      
	if((((dxySig_max_cut>0) && (IP_sig < dxySig_max_cut)) || (dxySig_max_cut<=0)) && (IP_sig > dxySig_min_cut)){
	  //if(IP_sig > 2){
	  seed_track_refs.push_back(tk_ref);
	  seed_track_index_map[tk_ref] = i_tk;
	}
      }
    }
    //if ((IP_sig > 4) && (tk_ref->pt()>0.9)) seed_track_refs.push_back(tk_ref);
    if (verbose) printf("Build track references. IP_sig = %f\n", IP_sig);
  }
  
  
  //Build transient tracks from reco tracks
  std::vector<reco::TransientTrack> seed_tracks;

  std::map<reco::TrackRef, size_t> seed_track_ref_map;
  for (const reco::TrackRef& tk : seed_track_refs) {
    seed_tracks.push_back(tt_builder.build(tk));
    seed_track_ref_map[tk] = seed_tracks.size() - 1;
  }

  //////////////////////////////////////////////////////////////////////
  // Form seed vertices from all pairs of tracks whose vertex fit
  // passes cuts.
  //////////////////////////////////////////////////////////////////////

  const size_t ntk = seed_tracks.size();
  std::unique_ptr<reco::VertexCollection> vertices(new reco::VertexCollection);
  std::vector<size_t> itks(n_tracks_per_seed_vertex, 0);
  std::vector<float> vtxMasses;
  
  auto try_seed_vertex = [&]() {
    std::vector<reco::TransientTrack> ttks(n_tracks_per_seed_vertex);
    for (int i = 0; i < n_tracks_per_seed_vertex; ++i)
      ttks[i] = seed_tracks[itks[i]];

    TransientVertex seed_vertex = kv_reco.vertex(ttks);
    if (seed_vertex.isValid() && seed_vertex.normalisedChiSquared() < max_seed_vertex_chi2) {
      reco::Vertex vertex = reco::Vertex(seed_vertex);
      track_set tracks = vertex_track_set(vertex);
      TLorentzVector vtx_p4(0.,0.,0.,0.);
      int netCharge = 0;
      for(auto trk: tracks){
	//const reco::Track& trkRefit = vertex.refittedTrack(trk);
	TLorentzVector trk_p4;
	trk_p4.SetPtEtaPhiM(trk->pt(), trk->eta(), trk->phi(), 0.13957); //pion mass in GeV
	vtx_p4 += trk_p4;
	netCharge += trk->charge();
      }
      float vtxMass = vtx_p4.M();
      const TVector3 vp42(vtx_p4.X(), vtx_p4.Y(), 0);
      const TVector3 flight2(vertex.x() - bsx, vertex.y() - bsy, 0);
      const double costh2 = vp42.Unit().Dot(flight2.Unit());
      //std::cout<<"vertex params: costh2 "<<costh2<<" vtxMass "<<vtxMass<<std::endl;
      if((costh2>=0.9) && (vtxMass>=0.3) && (vtxMass<=0.7) && (netCharge==0)){
	vertices->push_back(vertex);
	vtxMasses.push_back(vtxMass);
	if (verbose) {
	  const reco::Vertex& v = vertices->back();
	  const double vchi2 = v.normalizedChi2();
	  const double vndof = v.ndof();
	  const double vx = v.position().x() - bsx;
	  const double vy = v.position().y() - bsy;
	  const double vz = v.position().z() - bsz;
	  const double phi = atan2(vy, vx);
	  const double rho = sqrt(vx*vx + vy*vy);
	  const double r = sqrt(vx*vx + vy*vy + vz*vz);
	  
	  printf("from tracks");
	  for (auto itk : itks)
	    printf(" %lu", itk);
	  printf(": vertex #%3lu: chi2/dof: %7.3f dof: %7.3f pos: <%7.3f, %7.3f, %7.3f>  rho: %7.3f  phi: %7.3f  r: %7.3f\n", vertices->size() - 1, vchi2, vndof, vx, vy, vz, rho, phi, r);
	  
	}
      }
    }
  };

  // ha
  for (size_t itk = 0; itk < ntk; ++itk) {
    itks[0] = itk;
    for (size_t jtk = itk + 1; jtk < ntk; ++jtk) {
      itks[1] = jtk;
      if (n_tracks_per_seed_vertex == 2) { try_seed_vertex(); continue; }
      for (size_t ktk = jtk + 1; ktk < ntk; ++ktk) {
        itks[2] = ktk;
        if (n_tracks_per_seed_vertex == 3) { try_seed_vertex(); continue; }
        for (size_t ltk = ktk + 1; ltk < ntk; ++ltk) {
          itks[3] = ltk;
          if (n_tracks_per_seed_vertex == 4) { try_seed_vertex(); continue; }
          for (size_t mtk = ltk + 1; mtk < ntk; ++mtk) {
            itks[4] = mtk;
            try_seed_vertex();
          }
        }
      }
    }
  }

  //////////////////////////////////////////////////////////////////////
  // Take care of track sharing. If a track is in two vertices, and
  // the vertices are "close", refit the tracks from the two together
  // as one vertex. If the vertices are not close, keep the track in
  // the vertex to which it is "closer".
  //////////////////////////////////////////////////////////////////////
  
  //printf("entering the track sharing part\n");
  
  track_set discarded_tracks;
  int n_resets = 0;
  int n_onetracks = 0;
  std::vector<reco::Vertex>::iterator v[2];
  float k0Mass = 0.497611; //GeV
  size_t ivtx[2];
  
  for (v[0] = vertices->begin(); v[0] != vertices->end(); ++v[0]) {
    track_set tracks[2];
    ivtx[0] = v[0] - vertices->begin();
    tracks[0] = vertex_track_set(*v[0]);
    
    if (tracks[0].size() < 2) {
      if (verbose)
        printf("track-sharing: vertex-0 #%lu is down to one track, junking it\n", ivtx[0]);
      v[0] = vertices->erase(v[0]) - 1;
      ++n_onetracks;
      continue;
    }

    bool duplicate = false;
    bool shareTrack = false;
    
    for (v[1] = v[0] + 1; v[1] != vertices->end(); ++v[1]) {
      ivtx[1] = v[1] - vertices->begin();
      tracks[1] = vertex_track_set(*v[1]);

      if (tracks[1].size() < 2) {
        if (verbose)
          printf("track-sharing: vertex-1 #%lu is down to one track, junking it\n", ivtx[1]);	
	v[1] = vertices->erase(v[1]) - 1;
        ++n_onetracks;
        continue;
      }


      
      if (verbose) {
        printf("track-sharing: # vertices = %lu. considering vertices #%lu (chi2/dof %.3f, track set", vertices->size(), ivtx[0], v[0]->chi2() / v[0]->ndof());
        print_track_set(tracks[0], *v[0]);
        printf(") and #%lu (chi2/dof %.3f, track set", ivtx[1], v[1]->chi2() / v[1]->ndof());
        print_track_set(tracks[1], *v[1]);
        printf("):\n");
      }

      
      if (is_track_subset(tracks[0], tracks[1])) {
	if (verbose)
          printf("   subset/duplicate vertices %lu and %lu, erasing second and starting over\n", ivtx[0], ivtx[1]);
        duplicate = true;
        break;
      }

      std::vector<reco::TrackRef> shared_tracks;
      for (auto tk : tracks[0])
        if (tracks[1].count(tk) > 0)
          shared_tracks.push_back(tk);

      if (verbose) {
        if (shared_tracks.size()) {
          printf("   shared tracks are: ");
          print_track_set(shared_tracks);
          printf("\n");
        }
        else
          printf("   no shared tracks\n");
      }

      
      if (shared_tracks.size() > 0){
	shareTrack = true;
	break;
      }
    }
        
    if (duplicate) {
      vertices->erase(v[1]);
    }
    else if (shareTrack) {
      float mass1 = vtxMasses.at(ivtx[0]);
      float mass2 = vtxMasses.at(ivtx[1]);
      float massDiff1 = abs(mass1-k0Mass);
      float massDiff2 = abs(mass2-k0Mass);
      if(massDiff1<massDiff2){
	vertices->erase(v[1]);
      }
      else{
	vertices->erase(v[0]);
      }
    }
    
    // If we changed the vertices at all, start loop over completely.
    if (duplicate || shareTrack) {
      //printf("duplicate = %d, merge = %d, refit = %d\n", duplicate, merge, refit);
      
      v[0] = vertices->begin() - 1;  // -1 because about to ++sv
      ++n_resets;
      
      //if (n_resets == 3000){
      //std::cout<<"I'm dumb"<<std::endl;
      //}
    }
  }

  //////////////////////////////////////////////////////////////////////
  // Put the output.
  //////////////////////////////////////////////////////////////////////
  
  //Save the vertices
  //std::cout<<"found "<<vertices->size()<<" kaon vertices"<<std::endl;
  iEvent.emplace(putToken_, std::move(*vertices));
}

// ------------ method called once each stream before processing any runs, lumis or events  ------------
void K0Vertexer::beginStream(edm::StreamID) {
  // please remove this method if not needed
  edm::Service<TFileService> fs;
  h_dxyErr_weighted_sum_barrel = fs->make<TH1D>("dxyErr_weighted_sum_barrel",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszErr_weighted_sum_barrel = fs->make<TH1D>("dszErr_weighted_sum_barrel",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszdxyCov_weighted_sum_barrel = fs->make<TH1D>("dszdxyCov_weighted_sum_barrel",";Track p_{T}; Weighted Sum",200,0,200);
  h_dxyErr_weighted_sq_sum_barrel = fs->make<TH1D>("dxyErr_weighted_sq_sum_barrel",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszErr_weighted_sq_sum_barrel = fs->make<TH1D>("dszErr_weighted_sq_sum_barrel",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszdxyCov_weighted_sq_sum_barrel = fs->make<TH1D>("dszdxyCov_weighted_sq_sum_barrel",";Track p_{T}; Weighted Sum",200,0,200);
  h_weight_sum_barrel = fs->make<TH1D>("weight_sum_barrel",";Track p_{T}; Weight Sum",200,0,200);
  h_weight_sq_sum_barrel = fs->make<TH1D>("weight_sq_sum_barrel",";Track p_{T}; Weight Squared Sum",200,0,200);

  h_dxyErr_weighted_sum_disk = fs->make<TH1D>("dxyErr_weighted_sum_disk",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszErr_weighted_sum_disk = fs->make<TH1D>("dszErr_weighted_sum_disk",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszdxyCov_weighted_sum_disk = fs->make<TH1D>("dszdxyCov_weighted_sum_disk",";Track p_{T}; Weighted Sum",200,0,200);
  h_dxyErr_weighted_sq_sum_disk = fs->make<TH1D>("dxyErr_weighted_sq_sum_disk",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszErr_weighted_sq_sum_disk = fs->make<TH1D>("dszErr_weighted_sq_sum_disk",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszdxyCov_weighted_sq_sum_disk = fs->make<TH1D>("dszdxyCov_weighted_sq_sum_disk",";Track p_{T}; Weighted Sum",200,0,200);
  h_weight_sum_disk = fs->make<TH1D>("weight_sum_disk",";Track p_{T}; Weight Sum",200,0,200);
  h_weight_sq_sum_disk = fs->make<TH1D>("weight_sq_sum_disk",";Track p_{T}; Weight Squared Sum",200,0,200);

  h_dxyErr_weighted_sum_barrel_jetMatched = fs->make<TH1D>("dxyErr_weighted_sum_barrel_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszErr_weighted_sum_barrel_jetMatched = fs->make<TH1D>("dszErr_weighted_sum_barrel_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszdxyCov_weighted_sum_barrel_jetMatched = fs->make<TH1D>("dszdxyCov_weighted_sum_barrel_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_dxyErr_weighted_sq_sum_barrel_jetMatched = fs->make<TH1D>("dxyErr_weighted_sq_sum_barrel_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszErr_weighted_sq_sum_barrel_jetMatched = fs->make<TH1D>("dszErr_weighted_sq_sum_barrel_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszdxyCov_weighted_sq_sum_barrel_jetMatched = fs->make<TH1D>("dszdxyCov_weighted_sq_sum_barrel_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_weight_sum_barrel_jetMatched = fs->make<TH1D>("weight_sum_barrel_jetMatched",";Track p_{T}; Weight Sum",200,0,200);
  h_weight_sq_sum_barrel_jetMatched = fs->make<TH1D>("weight_sq_sum_barrel_jetMatched",";Track p_{T}; Weight Squared Sum",200,0,200);

  h_dxyErr_weighted_sum_disk_jetMatched = fs->make<TH1D>("dxyErr_weighted_sum_disk_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszErr_weighted_sum_disk_jetMatched = fs->make<TH1D>("dszErr_weighted_sum_disk_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszdxyCov_weighted_sum_disk_jetMatched = fs->make<TH1D>("dszdxyCov_weighted_sum_disk_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_dxyErr_weighted_sq_sum_disk_jetMatched = fs->make<TH1D>("dxyErr_weighted_sq_sum_disk_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszErr_weighted_sq_sum_disk_jetMatched = fs->make<TH1D>("dszErr_weighted_sq_sum_disk_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_dszdxyCov_weighted_sq_sum_disk_jetMatched = fs->make<TH1D>("dszdxyCov_weighted_sq_sum_disk_jetMatched",";Track p_{T}; Weighted Sum",200,0,200);
  h_weight_sum_disk_jetMatched = fs->make<TH1D>("weight_sum_disk_jetMatched",";Track p_{T}; Weight Sum",200,0,200);
  h_weight_sq_sum_disk_jetMatched = fs->make<TH1D>("weight_sq_sum_disk_jetMatched",";Track p_{T}; Weight Squared Sum",200,0,200);
}

// ------------ method called once each stream after processing all runs, lumis and events  ------------
void K0Vertexer::endStream() {
  // please remove this method if not needed
  h_dxyErr_weighted_sum_barrel->Draw();
  h_dxyErr_weighted_sum_barrel->Write();
  
  h_dszErr_weighted_sum_barrel->Draw();
  h_dszErr_weighted_sum_barrel->Write();
  
  h_dszdxyCov_weighted_sum_barrel->Draw();
  h_dszdxyCov_weighted_sum_barrel->Write();

  h_dxyErr_weighted_sq_sum_barrel->Draw();
  h_dxyErr_weighted_sq_sum_barrel->Write();
  
  h_dszErr_weighted_sq_sum_barrel->Draw();
  h_dszErr_weighted_sq_sum_barrel->Write();
  
  h_dszdxyCov_weighted_sq_sum_barrel->Draw();
  h_dszdxyCov_weighted_sq_sum_barrel->Write();
  
  h_weight_sum_barrel->Draw();
  h_weight_sum_barrel->Write();
  
  h_weight_sq_sum_barrel->Draw();
  h_weight_sq_sum_barrel->Write();

  h_dxyErr_weighted_sum_disk->Draw();
  h_dxyErr_weighted_sum_disk->Write();
  
  h_dszErr_weighted_sum_disk->Draw();
  h_dszErr_weighted_sum_disk->Write();
  
  h_dszdxyCov_weighted_sum_disk->Draw();
  h_dszdxyCov_weighted_sum_disk->Write();

  h_dxyErr_weighted_sq_sum_disk->Draw();
  h_dxyErr_weighted_sq_sum_disk->Write();
  
  h_dszErr_weighted_sq_sum_disk->Draw();
  h_dszErr_weighted_sq_sum_disk->Write();
  
  h_dszdxyCov_weighted_sq_sum_disk->Draw();
  h_dszdxyCov_weighted_sq_sum_disk->Write();
  
  h_weight_sum_disk->Draw();
  h_weight_sum_disk->Write();
  
  h_weight_sq_sum_disk->Draw();
  h_weight_sq_sum_disk->Write();

  //jet matched histograms

  h_dxyErr_weighted_sum_barrel_jetMatched->Draw();
  h_dxyErr_weighted_sum_barrel_jetMatched->Write();
  
  h_dszErr_weighted_sum_barrel_jetMatched->Draw();
  h_dszErr_weighted_sum_barrel_jetMatched->Write();
  
  h_dszdxyCov_weighted_sum_barrel_jetMatched->Draw();
  h_dszdxyCov_weighted_sum_barrel_jetMatched->Write();

  h_dxyErr_weighted_sq_sum_barrel_jetMatched->Draw();
  h_dxyErr_weighted_sq_sum_barrel_jetMatched->Write();
  
  h_dszErr_weighted_sq_sum_barrel_jetMatched->Draw();
  h_dszErr_weighted_sq_sum_barrel_jetMatched->Write();
  
  h_dszdxyCov_weighted_sq_sum_barrel_jetMatched->Draw();
  h_dszdxyCov_weighted_sq_sum_barrel_jetMatched->Write();
  
  h_weight_sum_barrel_jetMatched->Draw();
  h_weight_sum_barrel_jetMatched->Write();
  
  h_weight_sq_sum_barrel_jetMatched->Draw();
  h_weight_sq_sum_barrel_jetMatched->Write();

  h_dxyErr_weighted_sum_disk_jetMatched->Draw();
  h_dxyErr_weighted_sum_disk_jetMatched->Write();
  
  h_dszErr_weighted_sum_disk_jetMatched->Draw();
  h_dszErr_weighted_sum_disk_jetMatched->Write();
  
  h_dszdxyCov_weighted_sum_disk_jetMatched->Draw();
  h_dszdxyCov_weighted_sum_disk_jetMatched->Write();

  h_dxyErr_weighted_sq_sum_disk_jetMatched->Draw();
  h_dxyErr_weighted_sq_sum_disk_jetMatched->Write();
  
  h_dszErr_weighted_sq_sum_disk_jetMatched->Draw();
  h_dszErr_weighted_sq_sum_disk_jetMatched->Write();
  
  h_dszdxyCov_weighted_sq_sum_disk_jetMatched->Draw();
  h_dszdxyCov_weighted_sq_sum_disk_jetMatched->Write();
  
  h_weight_sum_disk_jetMatched->Draw();
  h_weight_sum_disk_jetMatched->Write();
  
  h_weight_sq_sum_disk_jetMatched->Draw();
  h_weight_sq_sum_disk_jetMatched->Write();
}

// ------------ method called when starting to processes a run  ------------
/*
void
K0Vertexer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a run  ------------
/*
void
K0Vertexer::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when starting to processes a luminosity block  ------------
/*
void
K0Vertexer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
K0Vertexer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

/* ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void K0Vertexer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}
*/

//define this as a plug-in
DEFINE_FWK_MODULE(K0Vertexer);
