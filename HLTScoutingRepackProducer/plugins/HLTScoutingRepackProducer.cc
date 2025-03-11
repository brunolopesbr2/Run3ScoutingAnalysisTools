// -*- C++ -*-
//
// Package:    Run3ScoutingAnalysisTools/HLTScoutingRepackProducer
// Class:      HLTScoutingRepackProducer
//
/**\class HLTScoutingRepackProducer HLTScoutingRepackProducer.cc Run3ScoutingAnalysisTools/HLTScoutingRepackProducer/plugins/HLTScoutingRepackProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Bruno Lopes
//         Created:  Thu, 27 Feb 2025 19:06:31 GMT
//
//

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/Utilities/interface/EDPutToken.h"
#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/Common/interface/OrphanHandle.h"

#include "DataFormats/Scouting/interface/Run3ScoutingTrack.h"
#include "DataFormats/Scouting/interface/Run3ScoutingVertex.h"

#include "DataFormats/JetReco/interface/PFJet.h"
#include "DataFormats/JetReco/interface/PFJetCollection.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "SimGeneral/HepPDTRecord/interface/ParticleDataTable.h"
#include "fastjet/contrib/SoftKiller.hh"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/SiPixelDetId/interface/PixelSubdetector.h"
#include "DataFormats/SiStripDetId/interface/StripSubdetector.h"
#include "DataFormats/TrackingRecHit/interface/TrackingRecHit.h"


//
// class declaration
//

class HLTScoutingRepackProducer : public edm::stream::EDProducer<> {
public:
  using Run3ScoutingTrackCollection = std::vector<Run3ScoutingTrack>;
  using Run3ScoutingVertexCollection = std::vector<Run3ScoutingVertex>;
  
  //template <typename T> using RefCollection = std::vector<edm::Ref<std::vector<T>>>;
  //template <typename T> using RefMap = edm::ValueMap<edm::Ref<std::vector<T>>>;
  
  explicit HLTScoutingRepackProducer(const edm::ParameterSet& params);
  ~HLTScoutingRepackProducer() override = default;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void produce(edm::Event& iEvent, edm::EventSetup const& iSetup) override;
    
  // private helper functions
  Run3ScoutingVertex createScoutingVertex(reco::Vertex const& vertex);  
    
  // register products for reco object and corresponding Value to Ref to original scouting objects
  //template<typename RecoObjectType, typename ScoutingObjectType>
  //void produceWithRef(std::string const& name);
  
  // put reco object together with ValueMap to Ref to original scouting object
  //template<typename RecoObjectType, typename ScoutingObjectType>
  //void putWithRef(edm::Event& iEvent, std::string const& name, std::unique_ptr<RefCollection<reco::Vertex>>& recoObjectRef_collection_ptr, std::unique_ptr<std::vector<Run3ScoutingVertex>>& scoutingObject_collection_ptr);
  
  //edm::EDGetTokenT<Run3ScoutingTrackCollection> scoutingTrack_collection_token_;
  //edm::EDGetTokenT<Run3ScoutingVertexCollection> scoutingPrimaryVertex_collection_token_;
  edm::EDGetTokenT<std::vector<reco::Vertex>> displacedVertices_token_;
  edm::EDPutTokenT<std::vector<Run3ScoutingVertex>> putToken_;

  //bool produce_PFCHSCandidate_; // CHS = charged hadron subtraction
  //bool produce_PFSKCandidate_; // SK = soft killer
  //HepPDT::ParticleDataTable const *particle_data_table_;

  //inline static const std::string REF_TO_RECO_LABEL_SUFFIX_ = "-RefToOriginal"; 
};

HLTScoutingRepackProducer::HLTScoutingRepackProducer(edm::ParameterSet const& params)
  :  displacedVertices_token_(consumes(params.getParameter<edm::InputTag>("displacedVertices"))),
     putToken_{produces("scoutingDispalcedVertices")}
{

  //produces<std::vector<Run3ScoutingVertex>>("DisplacedVertex");
  
}

/*
template <typename ScoutingObjectType, typename RecoObjectType>
void HLTScoutingRepackProducer::produceWithRef(std::string const& name) {
    produces<std::vector<ScoutingObjectType>>(name);
    produces<RefMap<RecoObjectType>>(name + REF_TO_RECO_LABEL_SUFFIX_);
    }*/

void HLTScoutingRepackProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  // produce Scouting Vertex
  edm::Handle<std::vector<reco::Vertex>> displacedVertices_handle = iEvent.getHandle(displacedVertices_token_);
  std::unique_ptr<std::vector<Run3ScoutingVertex>> scoutingDisplacedVertex_ptr(new std::vector<Run3ScoutingVertex>);
  //auto recoDisplacedVertexRef_ptr = std::unique_ptr<RefCollection<reco::Vertex>>();
  if (displacedVertices_handle.isValid()) {
    for (size_t DisplacedVertex_index = 0; DisplacedVertex_index < displacedVertices_handle->size(); DisplacedVertex_index++) {
      auto &DisplacedVertex = displacedVertices_handle->at(DisplacedVertex_index);
      scoutingDisplacedVertex_ptr->push_back(createScoutingVertex(DisplacedVertex));
      //recoDisplacedVertexRef_ptr->push_back(edm::Ref<reco::VertexCollection>(displacedVertices_handle, DisplacedVertex_index));
    }
  }
  
  // put products in Event
  iEvent.emplace(putToken_, std::move(*scoutingDisplacedVertex_ptr));
}

Run3ScoutingVertex HLTScoutingRepackProducer::createScoutingVertex(reco::Vertex const& vertex) {
  // Extract position (x, y, z)
  const auto& point = vertex.position();
  float x = point.x();
  float y = point.y();
  float z = point.z();
  
  // Extract errors (sqrt of diagonal terms of the covariance matrix)
  const auto& error = vertex.error();
  float xError = std::sqrt(error[0][0]);  // cov(0, 0) -> xError^2
  float yError = std::sqrt(error[1][1]);  // cov(1, 1) -> yError^2
  float zError = std::sqrt(error[2][2]);  // cov(2, 2) -> zError^2

  // Extract the covariance terms (off-diagonal) if they are available
  float xyCov = 0.0f, xzCov = 0.0f, yzCov = 0.0f;

  try {
    xyCov = vertex.covariance(0, 1);  // cov(0, 1)
    xzCov = vertex.covariance(0, 2);  // cov(0, 2)
    yzCov = vertex.covariance(1, 2);  // cov(1, 2)
  } catch (...) {
    // In case the covariance terms are not available, they will remain 0
  }
  
  // Extract other vertex properties like chi2, ndof, and tracksSize
  float chi2 = vertex.chi2();
  int ndof = vertex.ndof();
  int tracksSize = vertex.tracksSize();
  bool isValidVtx = vertex.isValid();
  
  // Create the Run3ScoutingVertex object using all the extracted values
  Run3ScoutingVertex scoutingVertex(
				    x, y, z,       // position
				    zError, xError, yError,  // errors
				    tracksSize, chi2, ndof,  // additional properties
				    isValidVtx,   // vertex validity
				    xyCov, xzCov, yzCov // covariance terms
				    );

  return scoutingVertex;
}

/*
template <typename ScoutingObjectType, typename RecoObjectType>
void HLTScoutingRepackProducer::putWithRef(edm::Event& iEvent, std::string const& name,
                                           std::unique_ptr<RefCollection<reco::Vertex>>& recoObjectRef_collection_ptr, std::unique_ptr<std::vector<Run3ScoutingVertex>>& scoutingObject_collection_ptr) {
    auto scoutingObject_collection_handle = iEvent.put(std::move(scoutingObject_collection_ptr), name);

    std::unique_ptr<RefMap<RecoObjectType>> refmap_to_reco(new RefMap<RecoObjectType>());
    typename RefMap<RecoObjectType>::Filler filler_refmap_to_reco(*refmap_to_reco);
    filler_refmap_to_reco.insert(scoutingObject_collection_handle, recoObjectRef_collection_ptr->begin(), recoObjectRef_collection_ptr->end());
    filler_refmap_to_reco.fill();
    iEvent.put(std::move(refmap_to_reco), name + REF_TO_RECO_LABEL_SUFFIX_);
    }*/


void HLTScoutingRepackProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("displacedVertices", edm::InputTag("Vertexer"));
    //desc.add<edm::InputTag>("scoutingDisplacedVertex", edm::InputTag("DisplacedVertexFromVertexer"));
    descriptions.addWithDefaultLabel(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(HLTScoutingRepackProducer);
