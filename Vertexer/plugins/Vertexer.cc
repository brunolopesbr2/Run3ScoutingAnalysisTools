// -*- C++ -*-
//
// Package:    Run3ScoutingAnalysisTools/Vertexer
// Class:      Vertexer
//
/**\class Vertexer Vertexer.cc Run3ScoutingAnalysisTools/Vertexer/plugins/Vertexer.cc

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

#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "MagneticField/Engine/interface/MagneticField.h"

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


using namespace edm;

//
// class declaration
//

class Vertexer : public edm::stream::EDProducer<> {
public:
  ~Vertexer() override;

  explicit Vertexer(edm::ParameterSet const& params);
  //static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void beginStream(edm::StreamID) override;
  void produce(edm::Event&, const edm::EventSetup&) override;
  void endStream() override;

  const edm::EDGetTokenT<std::vector<reco::Track>> seed_tracks_token_;
  const edm::ESGetToken<TransientTrackBuilder, TransientTrackRecord> token_builder;

  edm::EDPutTokenT<reco::VertexCollection> putToken_;

  //void beginRun(edm::Run const&, edm::EventSetup const&) override;
  //void endRun(edm::Run const&, edm::EventSetup const&) override;
  //void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
  //void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

  // ----------member data ---------------------------

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

Vertexer::Vertexer(edm::ParameterSet const& params)
  :
  seed_tracks_token_(consumes(params.getParameter<edm::InputTag>("seed_tracks_src"))),
  token_builder(esConsumes(edm::ESInputTag("", "TransientTrackBuilder"))),
  putToken_{produces()} {}

Vertexer::~Vertexer() {}

//
// member functions
//


// ------------ method called to produce the data  ------------
void Vertexer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {

  //Get the Transient Track Builder
  auto const &tt_builder = iSetup.getData(token_builder);

  //Get the reco tracks from the events
  edm::Handle<std::vector<reco::Track>> seed_track_refs;
  iEvent.getByToken(seed_tracks_token_, seed_track_refs);

  //Build transient tracks from reco tracks
  std::vector<reco::TransientTrack> seed_tracks = tt_builder.build(seed_track_refs);

  reco::VertexCollection myvs;

  //Do the vertex fitting
  if (seed_tracks.size() < 2)
    return;
  
  KalmanVertexFitter kv_reco;
  TransientVertex tv = kv_reco.vertex(seed_tracks);
  if (tv.normalisedChiSquared() > 5)
    return;
  
  reco::Vertex v(tv);

  //Save the vertices
  myvs.push_back(v);
  
  iEvent.emplace(putToken_, std::move(myvs));
}

// ------------ method called once each stream before processing any runs, lumis or events  ------------
void Vertexer::beginStream(edm::StreamID) {
  // please remove this method if not needed
}

// ------------ method called once each stream after processing all runs, lumis and events  ------------
void Vertexer::endStream() {
  // please remove this method if not needed
}

// ------------ method called when starting to processes a run  ------------
/*
void
Vertexer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a run  ------------
/*
void
Vertexer::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when starting to processes a luminosity block  ------------
/*
void
Vertexer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
Vertexer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

/* ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void Vertexer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}
*/

//define this as a plug-in
DEFINE_FWK_MODULE(Vertexer);
