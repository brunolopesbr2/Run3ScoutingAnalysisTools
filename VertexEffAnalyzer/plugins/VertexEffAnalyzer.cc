// -*- C++ -*-
//
// Package:    Run3ScoutingAnalysisTools/VertexEffAnalyzer
// Class:      VertexEffAnalyzer
//
/**\class VertexEffAnalyzer VertexEffAnalyzer.cc Run3ScoutingAnalysisTools/VertexEffAnalyzer/plugins/VertexEffAnalyzer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Bruno
//         Created:  Tue, 14 Apr 2026 17:02:56 GMT
//
//

// system include files
#include <memory>
#include <TTree.h>
#include <TLorentzVector.h>
#include <algorithm>
#include "TMath.h"
#include <valarray>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "CondFormats/DataRecord/interface/BeamSpotOnlineHLTObjectsRcd.h"
#include "CondFormats/BeamSpotObjects/interface/BeamSpotObjects.h"
#include "CondFormats/BeamSpotObjects/interface/BeamSpotOnlineObjects.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/HLTReco/interface/TriggerEvent.h"

#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "SimDataFormats/TrackingAnalysis/interface/TrackingParticle.h"
#include "SimDataFormats/TrackingAnalysis/interface/TrackingVertex.h"
#include "SimDataFormats/GeneratorProducts/interface/HepMCProduct.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "SimDataFormats/GeneratorProducts/interface/GenRunInfoProduct.h"

#include "DataFormats/Scouting/interface/Run3ScoutingElectron.h"
#include "DataFormats/Scouting/interface/Run3ScoutingPhoton.h"
#include "DataFormats/Scouting/interface/Run3ScoutingPFJet.h"
#include "DataFormats/Scouting/interface/Run3ScoutingVertex.h"
#include "DataFormats/Scouting/interface/Run3ScoutingTrack.h"
#include "DataFormats/Scouting/interface/Run3ScoutingMuon.h"
#include "DataFormats/Scouting/interface/Run3ScoutingParticle.h"

#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"

#include "RecoVertex/VertexTools/interface/VertexDistance3D.h"
#include "RecoVertex/VertexTools/interface/VertexDistanceXY.h"
#include "TrackingTools/IPTools/interface/IPTools.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"

#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"
#include "L1Trigger/L1TGlobal/interface/L1TGlobalUtil.h"
#include "DataFormats/L1TGlobal/interface/GlobalAlgBlk.h"
#include "HLTrigger/HLTcore/interface/TriggerExpressionData.h"
#include "HLTrigger/HLTcore/interface/TriggerExpressionEvaluator.h"
#include "HLTrigger/HLTcore/interface/TriggerExpressionParser.h"

#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h" 
#include "TH2.h"
#include "correction.h"
//
// class declaration
//

// If the analyzer does not use TFileService, please remove
// the template argument to the base class so the class inherits
// from  edm::one::EDAnalyzer<>
// This will improve performance in multithreaded jobs.

class VertexEffAnalyzer : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit VertexEffAnalyzer(const edm::ParameterSet&);
  ~VertexEffAnalyzer() override;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  void endJob() override;

  //Input Tokens
  const edm::EDGetTokenT<std::vector<reco::Vertex>> primary_vertices_token;
  const edm::EDGetTokenT<std::vector<reco::Track>> originalTracksToken_;
  const edm::EDGetTokenT<std::vector<reco::Track>> tracksToken_;
  const edm::EDGetTokenT<std::vector<reco::Track>> movedTracksToken_;
  const edm::EDGetTokenT<std::vector<double>> moveVertexToken_;
  const edm::EDGetTokenT<std::vector<reco::Vertex>> verticesToken_;
  const edm::EDGetTokenT<int> nPreselJetsToken_;
  const edm::EDGetTokenT<std::vector<reco::PFJet>> movedJetsToken_;
  const edm::EDGetTokenT<std::vector<double>> flightAxisToken_;
  double matchVertexDistance;
  bool isMC;
  const edm::EDGetTokenT<std::map<std::string, float>> weightsToken_;
  const edm::ESGetToken<BeamSpotOnlineObjects, BeamSpotOnlineHLTObjectsRcd> bsOnlineToken_;

  //Auxiliary Variables
  TTree* objectTree;
  double vertexDist;

  //track level
  std::vector<double> originalTracks_pt;
  std::vector<double> originalTracks_eta;
  std::vector<double> originalTracks_phi;
  std::vector<double> originalTracks_dxy;
  std::vector<double> originalTracks_dz;

  std::vector<double> tracks_pt;
  std::vector<double> tracks_eta;
  std::vector<double> tracks_phi;
  std::vector<double> tracks_dxy;
  std::vector<double> tracks_dz;

  std::vector<double> movedTracks_pt;
  std::vector<double> movedTracks_eta;
  std::vector<double> movedTracks_phi;
  std::vector<double> movedTracks_dxy;
  std::vector<double> movedTracks_dz;

  //vertex level
  double primaryVertex_x;
  double primaryVertex_y;
  double primaryVertex_z;

  double moveVertex_x;
  double moveVertex_y;
  double moveVertex_z;
  double moveVertex_dBV;
  double moveVertex_dBV3D;

  std::vector<double> vertices_x;
  std::vector<double> vertices_y;
  std::vector<double> vertices_z;
  std::vector<double> vertices_dBV;

  double LLP_dR;
  double LLP_PtSum;

  //event level
  int nVertices;
  int nMovedTracks;
  int nPreselJets;
  int nPV;
  bool matchedVertex;

  int nMatchedVertices;
  double matchedVert_chi2;
  double matchedVert_cosT;
  int matchedVert_nTracks;

  double matchedVert_dBV;
  double matchedVert_dBVerr;

  double weight;
  double weight_noTrigger;
  double genWeight;

  //Auxiliary functions

  typedef std::set<reco::TrackRef> track_set;
  typedef std::vector<reco::TrackRef> track_vec;

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
  
  track_vec vertex_track_vec(const reco::Vertex & v, const double min_weight = 0.5) const {
    track_set s = vertex_track_set(v, min_weight);
    return track_vec(s.begin(), s.end());
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
VertexEffAnalyzer::VertexEffAnalyzer(const edm::ParameterSet& iConfig)
    : 
    primary_vertices_token(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("primary_vertices"))),
    originalTracksToken_(consumes<std::vector<reco::Track>>(iConfig.getParameter<edm::InputTag>("original_tracks"))),
    tracksToken_(consumes<std::vector<reco::Track>>(iConfig.getParameter<edm::InputTag>("tracks"))),
    movedTracksToken_(consumes<std::vector<reco::Track>>(iConfig.getParameter<edm::InputTag>("moved_tracks"))),
    moveVertexToken_(consumes<std::vector<double>>(iConfig.getParameter<edm::InputTag>("move_vertex"))),
    verticesToken_(consumes<std::vector<reco::Vertex>>(iConfig.getParameter<edm::InputTag>("vertices"))),
    nPreselJetsToken_(consumes<int>(iConfig.getParameter<edm::InputTag>("n_presel_jets"))),
    movedJetsToken_(consumes<std::vector<reco::PFJet>>(iConfig.getParameter<edm::InputTag>("moved_jets"))),
    flightAxisToken_(consumes<std::vector<double>>(iConfig.getParameter<edm::InputTag>("flight_axis"))),
    matchVertexDistance(iConfig.getParameter<double>("matchVertexDistance")),
    isMC(iConfig.existsAs<bool>("isMC") ?  iConfig.getParameter<bool>  ("isMC") : false),
    weightsToken_(consumes<std::map<std::string, float>>(edm::InputTag("triggerFilter", "weightMap"))),
    bsOnlineToken_(esConsumes<BeamSpotOnlineObjects, BeamSpotOnlineHLTObjectsRcd>())
    {}

VertexEffAnalyzer::~VertexEffAnalyzer() {
  // do anything here that needs to be done at desctruction time
  // (e.g. close files, deallocate resources etc.)
  //
  // please remove this method altogether if it would be left empty
}

//
// member functions
//

// ------------ method called for each event  ------------
void VertexEffAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {

  //clear global vectors
  vertices_x.clear();
  vertices_y.clear();
  vertices_z.clear();
  vertices_dBV.clear();

  originalTracks_pt.clear();
  originalTracks_eta.clear();
  originalTracks_phi.clear();
  originalTracks_dxy.clear();
  originalTracks_dz.clear();

  tracks_pt.clear();
  tracks_eta.clear();
  tracks_phi.clear();
  tracks_dxy.clear();
  tracks_dz.clear();

  movedTracks_pt.clear();
  movedTracks_eta.clear();
  movedTracks_phi.clear();
  movedTracks_dxy.clear();
  movedTracks_dz.clear();

  edm::Handle<int> nPreselJetsH;
  iEvent.getByToken(nPreselJetsToken_, nPreselJetsH);

  nPreselJets = 0;
  if(nPreselJetsH.isValid()){
    nPreselJets = *nPreselJetsH;
  }

  edm::Handle<reco::VertexCollection> primaryVerticesH;
  iEvent.getByToken(primary_vertices_token, primaryVerticesH);

  nPV = 0;
  if (primaryVerticesH.isValid()) {
    nPV = primaryVerticesH->size();
  }

  if(nPreselJets < 2 || nPV < 1) return;

  primaryVertex_x = primaryVerticesH->at(0).x();
  primaryVertex_y = primaryVerticesH->at(0).y();
  primaryVertex_z = primaryVerticesH->at(0).z();

  //get online beamspot
  const auto& bs = iSetup.getData(bsOnlineToken_);
  reco::BeamSpot::CovarianceMatrix onlineCovariance;
  for(uint i=0; i<7; i++){
    for(uint j=i; j<7; j++){
      onlineCovariance(i,j) = bs.covariance(i,j);
    }
  }
  reco::BeamSpot::Point onlinePosition(bs.x(), bs.y(), bs.z());
  reco::BeamSpot* beamspot = new reco::BeamSpot(onlinePosition,
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

  const reco::Vertex fake_bs_vtx(beamspot->position(), beamspot->covariance3D());

  if(isMC){
    edm::Handle<std::map<std::string, float>> weightMap;
    iEvent.getByToken(weightsToken_, weightMap);
    weight = weightMap->at("correctedNominal");
    weight_noTrigger = weightMap->at("corrected_NoTrigger");
    genWeight = weightMap->at("GEN");
  }
  else{
    weight = 1;
    weight_noTrigger = 1;
    genWeight = 1;
  }

  edm::Handle<std::vector<reco::Vertex>> verticesH;
  iEvent.getByToken(verticesToken_, verticesH);

  edm::Handle<std::vector<double>> moveVertexH;
  iEvent.getByToken(moveVertexToken_, moveVertexH);

  if (moveVertexH.isValid()){
    moveVertex_x = moveVertexH->at(0);
    moveVertex_y = moveVertexH->at(1);
    moveVertex_z = moveVertexH->at(2);

    moveVertex_dBV = TMath::Sqrt(pow(moveVertex_x - fake_bs_vtx.x(), 2) + pow(moveVertex_y - fake_bs_vtx.y(), 2));
    moveVertex_dBV3D = TMath::Sqrt(pow(moveVertex_x - fake_bs_vtx.x(), 2) + pow(moveVertex_y - fake_bs_vtx.y(), 2) + pow(moveVertex_z - fake_bs_vtx.z(), 2));

    //std::cout<<"Analyser sees move vertex x as: "<<moveVertex_x<<std::endl;
  }

  else{
    moveVertex_x = 0;
    moveVertex_y = 0;
    moveVertex_z = 0;
    moveVertex_dBV = 0;
    moveVertex_dBV3D = 0;
  }

  matchedVertex = false;
  matchedVert_nTracks = 0;
  matchedVert_chi2 = 0;
  matchedVert_cosT = 0;
  matchedVert_dBV = 0;
  matchedVert_dBVerr = 0;

  int v_idx = 0;
  nMatchedVertices = 0;

  reco::Vertex v;

  Measurement1D dBV_measurement;
  VertexDistanceXY vertex_dist_2d;

  

  if(verticesH.isValid() && moveVertexH.isValid()){
    nVertices = verticesH->size();
    for (auto vertex_iter = verticesH->begin(); vertex_iter != verticesH->end(); ++vertex_iter) {
      vertices_x.push_back(vertex_iter->x());
      vertices_y.push_back(vertex_iter->y());
      vertices_z.push_back(vertex_iter->z());

      vertexDist = TMath::Sqrt(pow(vertex_iter->x()-moveVertexH->at(0), 2) + pow(vertex_iter->y()-moveVertexH->at(1), 2));

      if (vertexDist < matchVertexDistance){
        matchedVertex = true;
        nMatchedVertices++;

        v = verticesH->at(v_idx);
        if (vertex_track_vec(v).size() > static_cast<size_t>(matchedVert_nTracks)) {
          matchedVert_nTracks = vertex_track_vec(v).size();

          float p_tot[3] = {0.0, 0.0, 0.0};
          std::vector<reco::TrackRef> trks = vertex_track_vec(v);

          for(auto trk:trks){
            p_tot[0] += trk->px();
            p_tot[1] += trk->py();
            p_tot[2] += trk->pz();
          }

          matchedVert_cosT = ( p_tot[0]*(v.x()-beamspot->x0())+p_tot[1]*(v.y()-beamspot->y0())) / (sqrt(pow(p_tot[0],2)+pow(p_tot[1],2))*sqrt(pow(v.x()-beamspot->x0(),2)+pow(v.y()-beamspot->y0(),2)) );
          matchedVert_chi2 = v.normalizedChi2();
          dBV_measurement = vertex_dist_2d.distance(v, fake_bs_vtx);
          matchedVert_dBV = dBV_measurement.value();
          matchedVert_dBVerr = dBV_measurement.error();
        }
      }
      v_idx++;
    }
  }

  //get the 4 track collections
  edm::Handle<std::vector<reco::Track>> originalTracksH;
  iEvent.getByToken(originalTracksToken_, originalTracksH);

  edm::Handle<std::vector<reco::Track>> tracksH;
  iEvent.getByToken(tracksToken_, tracksH);

  edm::Handle<std::vector<reco::Track>> movedTracksH;
  iEvent.getByToken(movedTracksToken_, movedTracksH);


  
  if(originalTracksH.isValid()){
    for (auto originalTracks_iter = originalTracksH->begin(); originalTracks_iter != originalTracksH->end(); ++originalTracks_iter) {
      originalTracks_pt.push_back(originalTracks_iter->pt());
      originalTracks_eta.push_back(originalTracks_iter->eta());
      originalTracks_phi.push_back(originalTracks_iter->phi());
      originalTracks_dxy.push_back(originalTracks_iter->dxy());
      originalTracks_dz.push_back(originalTracks_iter->dz());
    }
  }

  if(tracksH.isValid()){
    for (auto tracks_iter = tracksH->begin(); tracks_iter != tracksH->end(); ++tracks_iter) {
      tracks_pt.push_back(tracks_iter->pt());
      tracks_eta.push_back(tracks_iter->eta());
      tracks_phi.push_back(tracks_iter->phi());
      tracks_dxy.push_back(tracks_iter->dxy());
      tracks_dz.push_back(tracks_iter->dz());
    }
  }

  LLP_PtSum = 0;
  LLP_dR = 0;
  nMovedTracks = 0;
  if(movedTracksH.isValid()){
    for (auto movedTracks_iter = movedTracksH->begin(); movedTracks_iter != movedTracksH->end(); ++movedTracks_iter) {
      movedTracks_pt.push_back(movedTracks_iter->pt());
      movedTracks_eta.push_back(movedTracks_iter->eta());
      movedTracks_phi.push_back(movedTracks_iter->phi());
      movedTracks_dxy.push_back(movedTracks_iter->dxy());
      movedTracks_dz.push_back(movedTracks_iter->dz());
      nMovedTracks++;

      for (auto movedTracks_iter2 = movedTracksH->begin(); movedTracks_iter2 != movedTracksH->end(); ++movedTracks_iter2) {
          double tmp_dR = reco::deltaR(movedTracks_iter->eta(), movedTracks_iter->phi(), movedTracks_iter2->eta(), movedTracks_iter2->phi());
          if (tmp_dR > LLP_dR) LLP_dR = tmp_dR;
      }

      LLP_PtSum = LLP_PtSum + movedTracks_iter->pt();
      }
  }

  objectTree->Fill();
}

// ------------ method called once each job just before starting event loop  ------------
void VertexEffAnalyzer::beginJob() {

  edm::Service<TFileService> fs;
  objectTree = fs->make<TTree>("objectTree","objectTree");

  objectTree->Branch("weight", &weight, "weight/D");
  objectTree->Branch("weight_noTrigger", &weight_noTrigger, "weight_noTrigger/D");
  objectTree->Branch("genWeight", &genWeight, "genWeight/D");

  objectTree->Branch("originalTracks_pt",&originalTracks_pt);
  objectTree->Branch("originalTracks_eta",&originalTracks_eta);
  objectTree->Branch("originalTracks_phi",&originalTracks_phi);
  objectTree->Branch("originalTracks_dxy",&originalTracks_dxy);
  objectTree->Branch("originalTracks_dz",&originalTracks_dz);

  objectTree->Branch("tracks_pt",&tracks_pt);
  objectTree->Branch("tracks_eta",&tracks_eta);
  objectTree->Branch("tracks_phi",&tracks_phi);
  objectTree->Branch("tracks_dxy",&tracks_dxy);
  objectTree->Branch("tracks_dz",&tracks_dz);

  objectTree->Branch("movedTracks_pt",&movedTracks_pt);
  objectTree->Branch("movedTracks_eta",&movedTracks_eta);
  objectTree->Branch("movedTracks_phi",&movedTracks_phi);
  objectTree->Branch("movedTracks_dxy",&movedTracks_dxy);
  objectTree->Branch("movedTracks_dz",&movedTracks_dz);

  objectTree->Branch("nMovedTracks", &nMovedTracks, "nMovedTracks/I");

  objectTree->Branch("nPreselJets", &nPreselJets, "nPreselJets/I");

  objectTree->Branch("moveVertex_x", &moveVertex_x, "moveVertex_x/D");
  objectTree->Branch("moveVertex_y", &moveVertex_y, "moveVertex_y/D");
  objectTree->Branch("moveVertex_z", &moveVertex_z, "moveVertex_z/D");
  objectTree->Branch("moveVertex_dBV", &moveVertex_dBV, "moveVertex_dBV/D");
  objectTree->Branch("moveVertex_dBV3D", &moveVertex_dBV3D, "moveVertex_dBV3D/D");

  objectTree->Branch("primaryVertex_x", &primaryVertex_x, "primaryVertex_x/D");
  objectTree->Branch("primaryVertex_y", &primaryVertex_y, "primaryVertex_y/D");
  objectTree->Branch("primaryVertex_z", &primaryVertex_z, "primaryVertex_z/D");

  objectTree->Branch("nPV", &nPV, "nPV/I");
  objectTree->Branch("nVertices", &nVertices, "nVertices/I");

  objectTree->Branch("matchedVertex", &matchedVertex, "matchedVertex/O");
  objectTree->Branch("nMatchedVertices", &nMatchedVertices, "nMatchedVertices/I");

  objectTree->Branch("matchedVertex_nTracks", &matchedVert_nTracks, "matchedVert_nTracks/I");
  objectTree->Branch("matchedVertex_cosT", &matchedVert_cosT, "matchedVert_cosT/D");
  objectTree->Branch("matchedVertex_chi2", &matchedVert_chi2, "matchedVert_chi2/D");
  objectTree->Branch("matchedVertex_dBV", &matchedVert_dBV, "matchedVert_dBV/D");
  objectTree->Branch("matchedVertex_dBVerr", &matchedVert_dBVerr, "matchedVert_dBVerr/D");

  objectTree->Branch("LLP_dR", &LLP_dR, "LLP_dR/D");
  objectTree->Branch("LLP_PtSum", &LLP_PtSum, "LLP_PtSum/D");
}

// ------------ method called once each job just after ending the event loop  ------------
void VertexEffAnalyzer::endJob() {

}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void VertexEffAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);

  //Specify that only 'tracks' is allowed
  //To use, remove the default given above and uncomment below
  //edm::ParameterSetDescription desc;
  //desc.addUntracked<edm::InputTag>("tracks", edm::InputTag("ctfWithMaterialTracks"));
  //descriptions.addWithDefaultLabel(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(VertexEffAnalyzer);
