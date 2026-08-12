// -*- C++ -*-
//
// Package:    Run3ScoutingAnalysisTools/TrackMover
// Class:      TrackMover
//
/**\class TrackMover TrackMover.cc Run3ScoutingAnalysisTools/TrackMover/plugins/TrackMover.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Tue, 31 Mar 2026 14:59:21 GMT
//
//

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

//From JMT framework
#include "TVector3.h"
#include "CLHEP/Random/RandomEngine.h"
#include "CLHEP/Random/RandExponential.h"
#include "CLHEP/Random/RandGauss.h"
#include "CLHEP/Random/RandBinomial.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Utilities/interface/RandomNumberGenerator.h"

#include "RecoVertex/VertexTools/interface/VertexDistance3D.h"
#include "RecoVertex/VertexTools/interface/VertexDistanceXY.h"
#include "TrackingTools/IPTools/interface/IPTools.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/TrajectoryState/interface/TrajectoryStateClosestToPoint.h"

#include "CondFormats/DataRecord/interface/BeamSpotOnlineHLTObjectsRcd.h"
#include "CondFormats/BeamSpotObjects/interface/BeamSpotObjects.h"
#include "CondFormats/BeamSpotObjects/interface/BeamSpotOnlineObjects.h"

//Scouting data formats
#include "DataFormats/Scouting/interface/Run3ScoutingElectron.h"
#include "DataFormats/Scouting/interface/Run3ScoutingPhoton.h"
#include "DataFormats/Scouting/interface/Run3ScoutingPFJet.h"
#include "DataFormats/Scouting/interface/Run3ScoutingVertex.h"
#include "DataFormats/Scouting/interface/Run3ScoutingTrack.h"
#include "DataFormats/Scouting/interface/Run3ScoutingMuon.h"
#include "DataFormats/Scouting/interface/Run3ScoutingParticle.h"

//Other formats
#include "DataFormats/JetReco/interface/PFJet.h"
#include "DataFormats/JetReco/interface/PFJetCollection.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "TH1.h"


//Get from JMT
//#include "JMTucker/Formats/interface/TracksMap.h"
//#include "JMTucker/Tools/interface/BTagging.h"
//#include "JMTucker/Tools/interface/TrackRefGetter.h"

//
// class declaration
//

class TrackMover : public edm::stream::EDProducer<> {
public:
  explicit TrackMover(const edm::ParameterSet&);
  ~TrackMover() override;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void beginStream(edm::StreamID) override;
  void produce(edm::Event&, const edm::EventSetup&) override;
  void endStream() override;

  //void beginRun(edm::Run const&, edm::EventSetup const&) override;
  //void endRun(edm::Run const&, edm::EventSetup const&) override;
  //void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
  //void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

  // ----------member data ---------------------------

  //Input tokens, in order
  const edm::EDGetTokenT<std::vector<reco::Track>> tracks_token;
  const edm::EDGetTokenT<std::vector<reco::Vertex>> primary_vertices_token;
  const edm::EDGetTokenT<std::vector<reco::PFJet>> jets_token;
  const edm::EDGetTokenT<std::vector<Run3ScoutingMuon>> muons_token;
  const edm::ESGetToken<TransientTrackBuilder, TransientTrackRecord> token_builder;
  const edm::ESGetToken<BeamSpotOnlineObjects, BeamSpotOnlineHLTObjectsRcd> bsOnlineToken_;

  //Input parameters, in order
  bool isMC;
  const double min_jet_pt;
  const int min_jet_ntracks;
  const double max_jet_track_dR;
  const int njets;
  const double tau;
  const double track_keep_prob;
  const double sig_theta;
  const double sig_phi;
  const std::string trackEffVariation; 

  //Output tokens, in order 
  edm::EDPutTokenT<reco::TrackCollection> outputTrackToken_;
  edm::EDPutTokenT<reco::TrackCollection> movedTrackToken_;
  edm::EDPutTokenT<int> nPreselJetsToken_;
  edm::EDPutTokenT<std::vector<reco::PFJet>> movedJetsToken_;
  edm::EDPutTokenT<std::vector<double>> flightAxisToken_;
  edm::EDPutTokenT<std::vector<double>> movedVertexToken_;


  //Auxiliary variables
  int jet_ntracks;
  double jet_track_dR;
  bool pass_presel;
  TVector3 move;
  int nPV;
  TH1F* trackEff;

  //Auxiliary functions

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
TrackMover::TrackMover(const edm::ParameterSet& iConfig) 
  :
  tracks_token(consumes<reco::TrackCollection>(iConfig.getParameter<edm::InputTag>("tracks_src"))),
  primary_vertices_token(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("primary_vertices_src"))),
  jets_token(consumes<std::vector<reco::PFJet>>(iConfig.getParameter<edm::InputTag>("jets_src"))),
  muons_token(consumes<std::vector<Run3ScoutingMuon>>(iConfig.getParameter<edm::InputTag>("muons_src"))),
  token_builder(esConsumes(edm::ESInputTag("", "TransientTrackBuilder"))),
  bsOnlineToken_(esConsumes<BeamSpotOnlineObjects, BeamSpotOnlineHLTObjectsRcd>()),
  isMC(iConfig.existsAs<bool>("isMC") ?  iConfig.getParameter<bool>  ("isMC") : false),
  min_jet_pt(iConfig.getParameter<double>("min_jet_pt")),
  min_jet_ntracks(iConfig.getParameter<int>("min_jet_ntracks")),
  max_jet_track_dR(iConfig.getParameter<double>("max_jet_track_dR")),
  njets(iConfig.getParameter<int>("njets")),
  tau(iConfig.getParameter<double>("tau")),
  track_keep_prob(iConfig.getParameter<double>("track_keep_prob")),
  sig_theta(iConfig.getParameter<double>("sig_theta")),
  sig_phi(iConfig.getParameter<double>("sig_phi")),
  trackEffVariation(iConfig.getParameter<std::string>("trackEffVariation")),
  outputTrackToken_{produces<reco::TrackCollection>("outputTracks")},
  movedTrackToken_{produces<reco::TrackCollection>("movedTracks")},
  nPreselJetsToken_{produces<int>("npreseljets")},
  movedJetsToken_{produces<std::vector<reco::PFJet>>("jetsUsed")},
  flightAxisToken_{produces<std::vector<double>>("flightAxis")},
  movedVertexToken_{produces<std::vector<double> >("moveVertex")}
{
  edm::Service<edm::RandomNumberGenerator> rng;
  if (!rng.isAvailable())
    throw cms::Exception("TrackMover", "RandomNumberGeneratorService not available");
}

TrackMover::~TrackMover() {
  // do anything here that needs to be done at destruction time
  // (e.g. close files, deallocate resources etc.)
  //
  // please remove this method altogether if it would be left empty
}

//
// member functions
//

// ------------ method called to produce the data  ------------
void TrackMover::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;
  //using namespace std;

  //Objects to fill and put in the event
  //auto output_tracks = std::make_unique<reco::TrackCollection>();
  //auto moved_tracks = std::make_unique<reco::TrackCollection>();
  //auto jets_used = std::make_unique<std::vector<reco::PFJet>>();
  //auto flight_axis = std::make_unique<std::vector<reco::PFJet>>();
  //auto move_vertex = std::make_unique<std::vector<double>>(3, 0.);

  std::unique_ptr<reco::TrackCollection> output_tracks(new reco::TrackCollection);
  std::unique_ptr<reco::TrackCollection> moved_tracks(new reco::TrackCollection);
  std::unique_ptr<std::vector<reco::PFJet>> jets_used(new std::vector<reco::PFJet>);
  std::unique_ptr<std::vector<double>> flight_vect(new std::vector<double>(3, 0.));
  std::unique_ptr<std::vector<double>> move_vertex(new std::vector<double>(3, 0.));

  std::unique_ptr<TVector3> flight_axis(new TVector3);

  //auxiliary vectors
  std::vector<reco::PFJet> presel_jets;
  std::vector<reco::PFJet> selected_jets;

  double track_keep_prob_perEvent = track_keep_prob;

  edm::Service<edm::RandomNumberGenerator> rng;
  CLHEP::HepRandomEngine& rng_engine = rng->getEngine(iEvent.streamID());
  auto knuth_select = [&rng_engine](int n, int N) -> std::vector<int> {
    std::vector<int> ts;
    int t = 0, m = 0;
    while (m < n) {
      if ((N - t) * rng_engine.flat() >= n - m)
        ++t;
      else {
        ++m;
        ts.push_back(t++);
      }
    }
    return ts;
  };

  //Random distributions to sample from later
  CLHEP::RandExponential rexp(rng_engine);
  CLHEP::RandGauss rgau(rng_engine);
  CLHEP::RandBinomial rint(rng_engine);

  Handle<std::vector<reco::PFJet> > pfjetsH;
  iEvent.getByToken(jets_token, pfjetsH);

  Handle<reco::TrackCollection> tracksH;
  iEvent.getByToken(tracks_token, tracksH);

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

  //TransientTrack builder for later
  auto const &tt_builder = iSetup.getData(token_builder);

  //jets preselection
  presel_jets.clear();

  if(pfjetsH.isValid()){
    for (auto jets_iter = pfjetsH->begin(); jets_iter != pfjetsH->end(); ++jets_iter) {
      if (jets_iter->pt() > min_jet_pt) {
        jet_ntracks = 0;
        if (tracksH.isValid()) {
          for (auto tracks_iter = tracksH->begin(); tracks_iter != tracksH->end(); ++tracks_iter) {
            //Do not select already displaced tracks
            reco::TransientTrack ttk = tt_builder.build(*tracks_iter);
            std::pair<bool, Measurement1D> ttk_dist = IPTools::absoluteTransverseImpactParameter(ttk, fake_bs_vtx);
            float IP_sig = ttk_dist.second.significance();
            if (IP_sig < 4){
              //Track quality requirements
              float pt_min_cut = 1.0;
              int  npixelHits_min_cut = 2;
              int nstripHits_min_cut = 1;
              int ntrackerLayers_min_cut = 5;
              if ((tracks_iter->pt()>pt_min_cut) && (tracks_iter->hitPattern().numberOfValidPixelHits() > npixelHits_min_cut) && (tracks_iter->hitPattern().numberOfValidStripHits() > nstripHits_min_cut) && (tracks_iter->hitPattern().trackerLayersWithMeasurement() > ntrackerLayers_min_cut) && (fabs(tracks_iter->eta())<2.4)){
                jet_track_dR = reco::deltaR(tracks_iter->eta(), tracks_iter->phi(), jets_iter->eta(), jets_iter->phi());
                if (jet_track_dR < max_jet_track_dR) {
                  jet_ntracks++;
                }
              }
            }
          }
        }
        if(jet_ntracks > min_jet_ntracks) {
          presel_jets.emplace_back(*jets_iter);
        }
      }
    }
  }

  edm::Handle<reco::VertexCollection> primary_vertices;
  iEvent.getByToken(primary_vertices_token, primary_vertices);

  nPV = primary_vertices->size();

  //Random selection of the desired number of jets
  pass_presel = static_cast<int>(presel_jets.size()) >= njets;  

  move.SetXYZ(0., 0., 0.); //clear move vector before start
  move_vertex->at(0) = 0;
  move_vertex->at(1) = 0;
  move_vertex->at(2) = 0;

  //create a reco::Vertex to check for close tracks with IPTools
  reco::Vertex::Point p(move_vertex->at(0), move_vertex->at(1), move_vertex->at(2));
  // negligible error -> significance dominated by the track's own uncertainty
  reco::Vertex::Error e;
  e(0,0) = 1e-10;
  e(1,1) = 1e-10;
  e(2,2) = 1e-10;
  reco::Vertex move_vertex_vtx(p, e);

  if (pass_presel && nPV > 0) {
    for (int i : knuth_select(njets, presel_jets.size())) {
      selected_jets.emplace_back(presel_jets[i]);
      jets_used->emplace_back(presel_jets[i]);
    }

    //Get the direction of the jets momentum to displace the tracks
    for (reco::PFJet jet : selected_jets)
      *flight_axis += TVector3(jet.px(), jet.py(), jet.pz());
    flight_axis->SetMag(1.);
    flight_vect->at(0) = flight_axis->x();
    flight_vect->at(1) = flight_axis->y();
    flight_vect->at(2) = flight_axis->z();

    //Mess with the displace direction a bit and displace the leading PV to create the "move vertex" 
    const double dist = rexp.fire(tau);
    const double theta = rgau.fire(flight_axis->Theta(), sig_theta);
    const double phi   = rgau.fire(flight_axis->Phi(),   sig_phi);
    move.SetMagThetaPhi(dist, theta, phi);

    
    move_vertex->at(0) = primary_vertices->at(0).x() + move.x();
    move_vertex->at(1) = primary_vertices->at(0).y() + move.y();
    move_vertex->at(2) = primary_vertices->at(0).z() + move.z();

    //std::cout<<"Move x: "<<move.x()<<", move vertex x: "<<move_vertex->at(0)<<", PV x: "<<primary_vertices->at(0).x()<<std::endl;
  }

  //Copy input tracks that do not match selected jets
  //Move the matched tracks to the "move vertex"
  for (auto tracks_iter = tracksH->begin(); tracks_iter != tracksH->end(); ++tracks_iter) {
    bool to_move = false;
    //do not move already displaced tracks
    reco::TransientTrack ttk = tt_builder.build(*tracks_iter);
    std::pair<bool, Measurement1D> ttk_dist = IPTools::absoluteTransverseImpactParameter(ttk, fake_bs_vtx);
    float IP_sig = ttk_dist.second.significance();
    if (IP_sig < 4){
      for (reco::PFJet jet : selected_jets){
        jet_track_dR = reco::deltaR(tracks_iter->eta(), tracks_iter->phi(), jet.eta(), jet.phi());
        if (jet_track_dR < max_jet_track_dR) {
          to_move = true;
          goto done_check_to_move;
        }
      }
    }
    done_check_to_move:
    
    if (to_move){
      //Track quality requirements
      float pt_min_cut = 1.0;
      int  npixelHits_min_cut = 2;
      int nstripHits_min_cut = 1;
      int ntrackerLayers_min_cut = 5;
      if ( !((tracks_iter->pt()>pt_min_cut) && (tracks_iter->hitPattern().numberOfValidPixelHits() > npixelHits_min_cut) && (tracks_iter->hitPattern().numberOfValidStripHits() > nstripHits_min_cut) && (tracks_iter->hitPattern().trackerLayersWithMeasurement() > ntrackerLayers_min_cut) && (fabs(tracks_iter->eta())<2.4)) ) continue;

      reco::TrackBase::Point new_point(tracks_iter->vx() + move.x(),
                                  tracks_iter->vy() + move.y(),
                                  tracks_iter->vz() + move.z());
      reco::Track new_tk(tracks_iter->chi2(), tracks_iter->ndof(), new_point, tracks_iter->momentum(), tracks_iter->charge(), tracks_iter->covariance(), tracks_iter->algo());
            
      //Before tossing out tracks, save the "Gen TM" tracks collection to perform signal reweighting later
      moved_tracks->push_back(new_tk);

      /* Not considering the track eff correction for now
      //Update probability to drop tracks based on the track reconstruction efficiency
      if(isMC){
        if(new_tk.dxy() > 0 && new_tk.dxy() < 0.15){ //For dxy > 0.15, track efficiency corrections are not well defined
          int bin = trackEff->GetXaxis()->FindBin(new_tk.dxy());
          double correction = trackEff->GetBinContent(bin);

          track_keep_prob_perEvent = std::min(track_keep_prob_perEvent * correction, 1.0);
        }
      }
      */

      if (rint.fire(1,track_keep_prob_perEvent) == 0) continue; //To toss out a track randomly 

      //impose same PV matching requirement as scouting tracks
      bool keepTrack = false;
      double originRadius = 0.1;
      double originHalfLength = 0.3; //same parameters as in the 2024 trigger menu

      //get the closest point from the new track to the beamspot
      reco::TransientTrack ttk = tt_builder.build(new_tk);

      GlobalPoint bsPos(
        fake_bs_vtx.x(),
        fake_bs_vtx.y(),
        fake_bs_vtx.z()
      );

      TrajectoryStateClosestToPoint tscp = ttk.trajectoryStateClosestToPoint(bsPos);
      GlobalPoint pca = tscp.theState().position();

      for (reco::VertexCollection::const_iterator iv = primary_vertices->begin(); iv != primary_vertices->end(); ++iv) {
        GlobalPoint aPV(iv->position().x(), iv->position().y(), iv->position().z());
        double distR2 = std::pow((pca.x() - aPV.x()), 2) + std::pow((pca.y() - aPV.y()), 2);
        double distZ = fabs(pca.z() - aPV.z());
        if (distR2 < std::pow(originRadius, 2) && distZ < originHalfLength) {
          keepTrack = true;
        } 
      }
      if(!keepTrack) continue;

      new_tk.setQualityMask(tracks_iter->qualityMask());
      new_tk.setNLoops(tracks_iter->nLoops());
      reco::HitPattern* hp = const_cast<reco::HitPattern*>(&new_tk.hitPattern());  *hp = tracks_iter->hitPattern(); 

      output_tracks->push_back(new_tk);
    }
    else {
      output_tracks->push_back(*tracks_iter);
      //If the track, by coindicence, is close to the move vertex, also consider for the TM reweighting
      reco::TransientTrack ttk = tt_builder.build(*tracks_iter);
      std::pair<bool, Measurement1D> ttk_dist = IPTools::absoluteTransverseImpactParameter(ttk, move_vertex_vtx);
      float IP_sig = ttk_dist.second.significance();
      if (IP_sig < 5){
        moved_tracks->push_back(*tracks_iter);
      }
    }
  }

  iEvent.emplace(outputTrackToken_, std::move(*output_tracks));
  iEvent.emplace(movedTrackToken_, std::move(*moved_tracks));
  iEvent.emplace(nPreselJetsToken_, static_cast<int>(presel_jets.size()));
  iEvent.emplace(movedJetsToken_, std::move(*jets_used));
  iEvent.emplace(flightAxisToken_, std::move(*flight_vect));
  iEvent.emplace(movedVertexToken_, std::move(*move_vertex));
}

// ------------ method called once each stream before processing any runs, lumis or events  ------------
void TrackMover::beginStream(edm::StreamID) {
  // please remove this method if not needed
  
  TFile* effFile = TFile::Open("TrackEffCorrection.root", "READ");
  trackEff = (TH1F*)effFile->Get(trackEffVariation.c_str());
}

// ------------ method called once each stream after processing all runs, lumis and events  ------------
void TrackMover::endStream() {
  // please remove this method if not needed
}

// ------------ method called when starting to processes a run  ------------
/*
void
TrackMover::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a run  ------------
/*
void
TrackMover::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when starting to processes a luminosity block  ------------
/*
void
TrackMover::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
TrackMover::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void TrackMover::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(TrackMover);
