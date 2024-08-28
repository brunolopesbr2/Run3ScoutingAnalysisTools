#include <memory>

#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/Utilities/interface/EDPutToken.h"
#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/Common/interface/OrphanHandle.h"

//#include "DataFormats/Scouting/interface/Run3ScoutingElectron.h"
//#include "DataFormats/Scouting/interface/Run3ScoutingMuon.h"
#include "DataFormats/Scouting/interface/Run3ScoutingPFJet.h"
#include "DataFormats/Scouting/interface/Run3ScoutingParticle.h"
//#include "DataFormats/Scouting/interface/Run3ScoutingPhoton.h"
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

/*
 * HLTScoutingUnpackProducer unpacks Run3Scouting data formats to their reco format counterparts
 * and cross link collections (currently PFCandidate - Track)
*/

class HLTScoutingUnpackProducer : public edm::stream::EDProducer<> {
public:
    //using Run3ScoutingElectron = std::vector<Run3ScoutingElectron>;
    //using Run3ScoutingMuon = std::vector<Run3ScoutingMuon>;
    using Run3ScoutingPFJetCollection = std::vector<Run3ScoutingPFJet>;
    using Run3ScoutingParticleCollection = std::vector<Run3ScoutingParticle>;
    //using Run3ScoutingPhotonCollection = std::vector<Run3ScoutingPhoton>;
    using Run3ScoutingTrackCollection = std::vector<Run3ScoutingTrack>;
    using Run3ScoutingVertexCollection = std::vector<Run3ScoutingVertex>;
    
    template <typename T> using RefCollection = std::vector<edm::Ref<std::vector<T>>>;
    template <typename T> using RefMap = edm::ValueMap<edm::Ref<std::vector<T>>>;

    explicit HLTScoutingUnpackProducer(edm::ParameterSet const& params);
    ~HLTScoutingUnpackProducer() override = default;

    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
 
private: 
    void produce(edm::Event& iEvent, edm::EventSetup const& iSetup) override;
    
    // private helper functions
    reco::PFJet createPFJet(Run3ScoutingPFJet const& scoutingPFJet);
    reco::Vertex createVertex(Run3ScoutingVertex const& scoutingVertex);
    reco::Track createTrack(Run3ScoutingTrack const& scoutingTrack);
    reco::PFCandidate createPFCandidate(Run3ScoutingParticle const& scoutingPFCandidate);
    bool hasPFTrackDetails(Run3ScoutingParticle const& scoutingPFCandidate);
    int findCompatibleScoutingTrack(Run3ScoutingParticle const& scoutingPFCandidate, Run3ScoutingVertex const& scoutingPrimaryVertex0, std::unique_ptr<reco::TrackCollection> & recoTrack_collection_ptr);
    void buildHitPattern(Run3ScoutingParticle const& scoutingPFCandidate, Run3ScoutingTrack const& scoutingTrack, reco::Track & recoTrack);
    std::unique_ptr<reco::Track> createPFTrack(Run3ScoutingParticle const& scoutingPFCandidate, edm::Handle<Run3ScoutingVertexCollection> const& scoutingPrimaryVertex_collection_handle);
    
    // register products for reco object and corresponding Value to Ref to original scouting objects
    template<typename RecoObjectType, typename ScoutingObjectType>
    void produceWithRef(std::string const& name);

    // put reco object together with ValueMap to Ref to original scouting object
    template<typename RecoObjectType, typename ScoutingObjectType>
    void putWithRef(edm::Event& iEvent, std::string const& name, std::unique_ptr<std::vector<RecoObjectType>>& recoObject_collection_ptr, std::unique_ptr<RefCollection<ScoutingObjectType>>& scoutingObjectRef_collection_ptr);

    //edm::EDGetTokenT<Run3ScoutingElectronCollection> scoutingElectron_collection_token_;
    //edm::EDGetTokenT<Run3ScoutingMuonCollection> scoutingMuon_collection_token_;
    edm::EDGetTokenT<Run3ScoutingPFJetCollection> scoutingPFJet_collection_token_;
    edm::EDGetTokenT<Run3ScoutingParticleCollection> scoutingPFCandidate_collection_token_;
    //edm::EDGetTokenT<Run3ScoutingPhotonCollection> scoutingPhoton_collection_token_;
    edm::EDGetTokenT<Run3ScoutingTrackCollection> scoutingTrack_collection_token_;
    edm::EDGetTokenT<Run3ScoutingVertexCollection> scoutingPrimaryVertex_collection_token_;

    edm::ESGetToken<HepPDT::ParticleDataTable, edm::DefaultRecord> particle_data_table_token_;

    bool produce_PFCandidate_;
    bool produce_PFCandidateMatchTrack_;
    bool produce_PFCHSCandidate_; // CHS = charged hadron subtraction
    bool produce_PFSKCandidate_; // SK = soft killer
    HepPDT::ParticleDataTable const *particle_data_table_;

    inline static const std::string REF_TO_SCOUTING_LABEL_SUFFIX_ = "-RefToScouting"; 
};

// constructor
HLTScoutingUnpackProducer::HLTScoutingUnpackProducer(edm::ParameterSet const& params)
    : //scoutingElectron_token_(consumes(params.getParameter<edm::InputTag>("scoutingElectron"))),
      //scoutingMuon_token_(consumes(params.getParameter<edm::InputTag>("scoutingMuon"))),
      scoutingPFJet_collection_token_(consumes(params.getParameter<edm::InputTag>("scoutingPFJet"))),
      scoutingPFCandidate_collection_token_(consumes(params.getParameter<edm::InputTag>("scoutingPFCandidate"))),
      //scoutingPhoton_token_(consumes(params.getParameter<edm::InputTag>("scoutingPhoton"))),
      scoutingTrack_collection_token_(consumes(params.getParameter<edm::InputTag>("scoutingTrack"))),
      scoutingPrimaryVertex_collection_token_(consumes(params.getParameter<edm::InputTag>("scoutingPrimaryVertex"))),
      particle_data_table_token_(esConsumes<HepPDT::ParticleDataTable, edm::DefaultRecord>()),
      produce_PFCandidate_(params.getParameter<bool>("producePFCandidate")),
      produce_PFCandidateMatchTrack_(params.getParameter<bool>("producePFCandidateMatchTrack")),
      produce_PFCHSCandidate_(params.getParameter<bool>("producePFCHSCandidate")){
      //produce_PFSKCandidate_(params.getParameter<bool>("producePFSKCandidate"))
    
    produceWithRef<reco::PFJet, Run3ScoutingPFJet>("PFJet");
     
    produceWithRef<reco::Track, Run3ScoutingTrack>("Track");

    produceWithRef<reco::Vertex, Run3ScoutingVertex>("PrimaryVertex");
    
    if (produce_PFCandidate_){
        produceWithRef<reco::PFCandidate, Run3ScoutingParticle>("PFCandidate");
    }
    if (produce_PFCandidateMatchTrack_){
        produceWithRef<reco::PFCandidate, Run3ScoutingParticle>("PFCandidateMatchTrack");
    }
    if (produce_PFCHSCandidate_){
        produceWithRef<reco::PFCandidate, Run3ScoutingParticle>("PFCHSCandidate");
    }
    /*if (produce_PFSKCandidate_){
        produces<reco::PFCandidateCollection>("PFSKCandidate");
    }*/
    if (produce_PFCandidate_ || produce_PFCandidateMatchTrack_ || produce_PFCHSCandidate_ || produce_PFSKCandidate_) {
        produces<reco::TrackCollection>("PFTrack"); // reco::track collection from best track parameters of PF
    }
}

template <typename RecoObjectType, typename ScoutingObjectType>
void HLTScoutingUnpackProducer::produceWithRef(std::string const& name) {
    produces<std::vector<RecoObjectType>>(name);
    produces<RefMap<ScoutingObjectType>>(name + REF_TO_SCOUTING_LABEL_SUFFIX_);
}

void HLTScoutingUnpackProducer::produce(edm::Event& iEvent, edm::EventSetup const& iSetup) {
    // produce reco::PFJet
    edm::Handle<Run3ScoutingPFJetCollection> scoutingPFJet_collection_handle = iEvent.getHandle(scoutingPFJet_collection_token_);
    auto recoPFJet_collection_ptr = std::make_unique<reco::PFJetCollection>();
    auto scoutingPFJetRef_collection_ptr = std::make_unique<RefCollection<Run3ScoutingPFJet>>();
    if (scoutingPFJet_collection_handle.isValid()) {
        for (size_t scoutingPFJet_index = 0; scoutingPFJet_index < scoutingPFJet_collection_handle->size(); scoutingPFJet_index++) {
            auto &scoutingPFJet = scoutingPFJet_collection_handle->at(scoutingPFJet_index);
            recoPFJet_collection_ptr->push_back(createPFJet(scoutingPFJet));
            scoutingPFJetRef_collection_ptr->push_back(edm::Ref<Run3ScoutingPFJetCollection>(scoutingPFJet_collection_handle, scoutingPFJet_index));
        }
    }

    // produce reco::Vertex
    edm::Handle<Run3ScoutingVertexCollection> scoutingPrimaryVertex_collection_handle = iEvent.getHandle(scoutingPrimaryVertex_collection_token_);
    auto recoPrimaryVertex_collection_ptr = std::make_unique<reco::VertexCollection>();
    auto scoutingPrimaryVertexRef_collection_ptr = std::make_unique<RefCollection<Run3ScoutingVertex>>();
    if (scoutingPrimaryVertex_collection_handle.isValid()) {
        for (size_t scoutingPrimaryVertex_index = 0; scoutingPrimaryVertex_index < scoutingPrimaryVertex_collection_handle->size(); scoutingPrimaryVertex_index++) {
            auto &scoutingPrimaryVertex = scoutingPrimaryVertex_collection_handle->at(scoutingPrimaryVertex_index);
            recoPrimaryVertex_collection_ptr->push_back(createVertex(scoutingPrimaryVertex));
            scoutingPrimaryVertexRef_collection_ptr->push_back(edm::Ref<Run3ScoutingVertexCollection>(scoutingPrimaryVertex_collection_handle, scoutingPrimaryVertex_index));
        }
    }

    // produce reco::Track
    edm::Handle<Run3ScoutingTrackCollection> scoutingTrack_collection_handle = iEvent.getHandle(scoutingTrack_collection_token_);
    auto recoTrack_collection_ptr = std::make_unique<reco::TrackCollection>();
    auto scoutingTrackRef_collection_ptr = std::make_unique<RefCollection<Run3ScoutingTrack>>();
    if (scoutingTrack_collection_handle.isValid()) {
        for (size_t scoutingTrack_index = 0; scoutingTrack_index < scoutingTrack_collection_handle->size(); scoutingTrack_index++) {
            auto &scoutingTrack = scoutingTrack_collection_handle->at(scoutingTrack_index);
            recoTrack_collection_ptr->push_back(createTrack(scoutingTrack));
            scoutingTrackRef_collection_ptr->push_back(edm::Ref<Run3ScoutingTrackCollection>(scoutingTrack_collection_handle, scoutingTrack_index));
        }
    }

    // produce reco::PFCandidate
    edm::Handle<Run3ScoutingParticleCollection> scoutingPFCandidate_collection_handle = iEvent.getHandle(scoutingPFCandidate_collection_token_);
    auto recoPFTrack_collection_ptr = std::make_unique<reco::TrackCollection>();
    
    auto recoPFCandidate_collection_ptr = std::make_unique<reco::PFCandidateCollection>();
    auto recoPFCandidateMatchTrack_collection_ptr = std::make_unique<reco::PFCandidateCollection>();
    auto recoPFCHSCandidate_collection_ptr = std::make_unique<reco::PFCandidateCollection>();

    auto scoutingPFCandidateRef_collection_ptr = std::make_unique<RefCollection<Run3ScoutingParticle>>();
    auto scoutingPFCandidateMatchTrackRef_collection_ptr = std::make_unique<RefCollection<Run3ScoutingParticle>>();

    if (scoutingPFCandidate_collection_handle.isValid() && (produce_PFCandidate_ || produce_PFCHSCandidate_ || produce_PFSKCandidate_)) {
        reco::TrackRefProd recoTrack_collection_refProd = iEvent.getRefBeforePut<reco::TrackCollection>("Track");
        reco::TrackRefProd recoPFTrack_collection_refProd = iEvent.getRefBeforePut<reco::TrackCollection>("PFTrack");
        particle_data_table_ = iSetup.getHandle(particle_data_table_token_).product();
        for (size_t scoutingPFCandidate_index = 0; scoutingPFCandidate_index < scoutingPFCandidate_collection_handle->size(); scoutingPFCandidate_index++) {
            auto &scoutingPFCandidate = scoutingPFCandidate_collection_handle->at(scoutingPFCandidate_index);
            
            // create base reco::PFCandidate
            reco::PFCandidate recoPFCandidate = createPFCandidate(scoutingPFCandidate);

            // build track and vertex for output reco::PFCandidate
            if (hasPFTrackDetails(scoutingPFCandidate)) { 
                // try to search for track built from ScoutingTrack containing more information
                int recoTrack_index = findCompatibleScoutingTrack(scoutingPFCandidate, scoutingPrimaryVertex_collection_handle->at(0), recoTrack_collection_ptr);
                if (recoTrack_index >= 0) {
                    // found compatible track in ScoutingTrack collection
                    // set TrackRef and vertex for reco::PFCandidate to track in ScoutingTrack collection
                    reco::TrackRef trackRef(recoTrack_collection_refProd, recoTrack_index);
                    recoPFCandidate.setTrackRef(trackRef);
                    recoPFCandidate.setVertex((recoTrack_collection_ptr->at(recoTrack_index)).vertex());
                    if (produce_PFCandidateMatchTrack_) {
                        recoPFCandidateMatchTrack_collection_ptr->push_back(recoPFCandidate);
                        scoutingPFCandidateMatchTrackRef_collection_ptr->push_back(edm::Ref<Run3ScoutingParticleCollection>(scoutingPFCandidate_collection_handle, scoutingPFCandidate_index));
                    }
                    // combine information from ScoutingPFCandidate and ScoutingTrack to build fake HitPattern similar to pat::PackedCandidate
                    buildHitPattern(scoutingPFCandidate, scoutingTrack_collection_handle->at(recoTrack_index), recoTrack_collection_ptr->at(recoTrack_index));
                    
                    // set quality mask from PFCandidate
                    (recoTrack_collection_ptr->at(recoTrack_index)).setQualityMask(static_cast<int8_t>(scoutingPFCandidate.quality()));

                } else {
                    // cannot find compatible track in ScoutingTrack collection
                    // build another track collection (PFTrack) using only information from ScoutingPFCandidate
                    std::unique_ptr<reco::Track> recoPFTrack_ptr = createPFTrack(scoutingPFCandidate, scoutingPrimaryVertex_collection_handle);
                    // set TrackRef and vertex for reco::PFCandidate
                    recoPFTrack_collection_ptr->push_back(*recoPFTrack_ptr);
                    reco::TrackRef trackRef(recoPFTrack_collection_refProd, recoPFTrack_collection_ptr->size() - 1);
                    recoPFCandidate.setTrackRef(trackRef);
                    recoPFCandidate.setVertex(recoPFTrack_ptr->vertex());
                }
            } else {
                if (produce_PFCandidateMatchTrack_) {
                    recoPFCandidateMatchTrack_collection_ptr->push_back(recoPFCandidate);
                    scoutingPFCandidateMatchTrackRef_collection_ptr->push_back(edm::Ref<Run3ScoutingParticleCollection>(scoutingPFCandidate_collection_handle, scoutingPFCandidate_index));
                }
            }
            recoPFCandidate_collection_ptr->push_back(recoPFCandidate);
            scoutingPFCandidateRef_collection_ptr->push_back(edm::Ref<Run3ScoutingParticleCollection>(scoutingPFCandidate_collection_handle, scoutingPFCandidate_index));
            if (produce_PFCHSCandidate_) {
                // currently apply CHS similar to Run3ScoutingParticleToRecoPFCandidateProducer which is not the same as, e.g. PAT
                // For applying CHS to pat::, see
                // https://github.com/cms-sw/cmssw/blob/master/CommonTools/ParticleFlow/python/pfCHS_cff.py
                // https://github.com/cms-sw/cmssw/blob/master/DataFormats/PatCandidates/interface/PackedCandidate.h#L718-L731
                // For applying CHS to reco::, see
                // https://github.com/cms-sw/cmssw/blob/master/CommonTools/ParticleFlow/python/pfNoPileUpJME_cff.py#L33
                // https://github.com/cms-sw/cmssw/blob/master/CommonTools/ParticleFlow/src/PFPileUpAlgo.cc#L6
                if (scoutingPFCandidate.vertex() <= 0) {
                    recoPFCHSCandidate_collection_ptr->push_back(recoPFCandidate);
                }
            }
        }
    }

    // build fake HitPattern for ScoutingTracks which are not matched with ScoutingPFCandidate
    // this might be needed if perform vertexing with all tracks 

    // put products in Event
    putWithRef<reco::PFJet, Run3ScoutingPFJet>(iEvent, "PFJet", recoPFJet_collection_ptr, scoutingPFJetRef_collection_ptr);

    putWithRef<reco::Vertex, Run3ScoutingVertex>(iEvent, "PrimaryVertex", recoPrimaryVertex_collection_ptr, scoutingPrimaryVertexRef_collection_ptr);
    
    putWithRef<reco::Track, Run3ScoutingTrack>(iEvent, "Track", recoTrack_collection_ptr, scoutingTrackRef_collection_ptr);
    
    if (produce_PFCandidate_ || produce_PFCandidateMatchTrack_ || produce_PFCHSCandidate_ || produce_PFSKCandidate_) {
        iEvent.put(std::move(recoPFTrack_collection_ptr), "PFTrack");
    }
    if (produce_PFCandidate_) {
        putWithRef<reco::PFCandidate, Run3ScoutingParticle>(iEvent, "PFCandidate", recoPFCandidate_collection_ptr, scoutingPFCandidateRef_collection_ptr);
    }
    if (produce_PFCandidateMatchTrack_) {
        putWithRef<reco::PFCandidate, Run3ScoutingParticle>(iEvent, "PFCandidateMatchTrack", recoPFCandidateMatchTrack_collection_ptr, scoutingPFCandidateMatchTrackRef_collection_ptr);
    }
    if (produce_PFCHSCandidate_) {
        iEvent.put(std::move(recoPFCHSCandidate_collection_ptr), "PFCHSCandidate");
    }
}

reco::PFJet HLTScoutingUnpackProducer::createPFJet(Run3ScoutingPFJet const& scoutingPFJet) {
    // fill LorentzVector P4
    float px = scoutingPFJet.pt() * cos(scoutingPFJet.phi());
    float py = scoutingPFJet.pt() * sin(scoutingPFJet.phi());
    float pz = scoutingPFJet.pt() * sinh(scoutingPFJet.eta());
    float p = scoutingPFJet.pt() * cosh(scoutingPFJet.eta());
    float energy = std::sqrt(p * p + scoutingPFJet.m() * scoutingPFJet.m());
    reco::Particle::LorentzVector p4(px, py, pz, energy);
    
    // fill vertex with default (0, 0, 0)
    reco::Particle::Point vertex(0, 0, 0);
    
    // fill specific
    reco::PFJet::Specific specific;
    specific.mChargedHadronEnergy = scoutingPFJet.chargedHadronEnergy();
    specific.mNeutralHadronEnergy = scoutingPFJet.neutralHadronEnergy();
    specific.mPhotonEnergy = scoutingPFJet.photonEnergy();
    specific.mElectronEnergy = scoutingPFJet.electronEnergy();
    specific.mMuonEnergy = scoutingPFJet.muonEnergy();
    specific.mHFHadronEnergy = scoutingPFJet.HFHadronEnergy();
    specific.mHFEMEnergy = scoutingPFJet.HFEMEnergy();
    
    specific.mChargedHadronMultiplicity = scoutingPFJet.chargedHadronMultiplicity();
    specific.mNeutralHadronMultiplicity = scoutingPFJet.neutralHadronMultiplicity();
    specific.mPhotonMultiplicity = scoutingPFJet.photonMultiplicity();
    specific.mElectronMultiplicity = scoutingPFJet.electronMultiplicity();
    specific.mMuonMultiplicity = scoutingPFJet.muonMultiplicity();
    specific.mHFHadronMultiplicity = scoutingPFJet.HFHadronMultiplicity();
    specific.mHFEMMultiplicity = scoutingPFJet.HFEMMultiplicity();

    specific.mChargedEmEnergy = scoutingPFJet.electronEnergy();
    specific.mChargedMuEnergy = scoutingPFJet.muonEnergy();
    specific.mNeutralEmEnergy = scoutingPFJet.photonEnergy();
    specific.mChargedMultiplicity = scoutingPFJet.chargedHadronMultiplicity() + scoutingPFJet.electronMultiplicity() + scoutingPFJet.muonMultiplicity();
    specific.mNeutralMultiplicity = scoutingPFJet.neutralHadronMultiplicity() + scoutingPFJet.photonMultiplicity() + scoutingPFJet.HFHadronMultiplicity() + scoutingPFJet.HFEMMultiplicity();

    specific.mHOEnergy = scoutingPFJet.HOEnergy();
    
    // create reco::PFJet output
    reco::PFJet recoPFJet(p4, vertex, specific);

    // set jetArea
    recoPFJet.setJetArea(scoutingPFJet.jetArea());
    
    return recoPFJet;
}

reco::Vertex HLTScoutingUnpackProducer::createVertex(Run3ScoutingVertex const& scoutingVertex) {
    // fill point coordinate
    reco::Vertex::Point point(scoutingVertex.x(), scoutingVertex.y(), scoutingVertex.z());
    
    // fill error
    std::vector<float> error_vec(6);
    error_vec[0] = scoutingVertex.xError() * scoutingVertex.xError(); // cov(0, 0)
    error_vec[1] = 0; // cov(0, 1)
    error_vec[2] = 0; // cov(0, 2)
    error_vec[3] = scoutingVertex.yError() * scoutingVertex.yError(); // cov(1, 1)
    error_vec[4] = 0; // cov(1, 2)
    error_vec[5] = scoutingVertex.zError() * scoutingVertex.zError(); // cov(2, 2)

    // off-diagonal errors are added in the begining of 2024
    // see https://github.com/cms-sw/cmssw/pull/43758
    /*try { 
      error_vec[1] = scoutingVertex.xyCov();
      error_vec[2] = scoutingVertex.xzCov();
      error_vec[4] = scoutingVertex.yzCov();
      }
    catch (...) { 
    }*/
    //Commented out the above to use for 2023

    reco::Vertex::Error error(error_vec.begin(), error_vec.end());

    return scoutingVertex.isValidVtx() ? reco::Vertex(point, error, scoutingVertex.chi2(), scoutingVertex.ndof(), scoutingVertex.tracksSize()): reco::Vertex(point, error);

    }

reco::Track HLTScoutingUnpackProducer::createTrack(Run3ScoutingTrack const& scoutingTrack){
    float chi2 = scoutingTrack.tk_chi2();
    float ndof = scoutingTrack.tk_ndof();
    reco::TrackBase::Point referencePoint(scoutingTrack.tk_vx(), scoutingTrack.tk_vy(), scoutingTrack.tk_vz());
    
    float px = scoutingTrack.tk_pt() * cos(scoutingTrack.tk_phi());
    float py = scoutingTrack.tk_pt() * sin(scoutingTrack.tk_phi());
    float pz = scoutingTrack.tk_pt() * sinh(scoutingTrack.tk_eta());
    reco::TrackBase::Vector momentum(px, py, pz);
    
    int charge = scoutingTrack.tk_charge();
    
    std::vector<float> cov_vec(15); // 5*(5+1)/2 = 15
    cov_vec[0] = scoutingTrack.tk_qoverp_Error() * scoutingTrack.tk_qoverp_Error(); // cov(0, 0)
    cov_vec[1] = scoutingTrack.tk_qoverp_lambda_cov(); // cov(0, 1)
    cov_vec[3] = scoutingTrack.tk_qoverp_phi_cov(); // cov(0, 2)
    cov_vec[6] = scoutingTrack.tk_qoverp_dxy_cov(); // cov(0, 3)
    cov_vec[10] = scoutingTrack.tk_qoverp_dsz_cov(); // cov(0, 4)
    cov_vec[2] = scoutingTrack.tk_lambda_Error() * scoutingTrack.tk_lambda_Error(); // cov(1, 1)
    cov_vec[4] = scoutingTrack.tk_lambda_phi_cov(); // cov(1, 2)
    cov_vec[7] = scoutingTrack.tk_lambda_dxy_cov(); // cov(1, 3)
    cov_vec[11] = scoutingTrack.tk_lambda_dsz_cov(); // cov(1, 4)
    cov_vec[5] = scoutingTrack.tk_phi_Error() * scoutingTrack.tk_phi_Error(); // cov(2, 2) 
    cov_vec[8] = scoutingTrack.tk_phi_dxy_cov(); // cov(2, 3)
    cov_vec[12] = scoutingTrack.tk_phi_dsz_cov(); // cov(2, 4)
    cov_vec[9] = scoutingTrack.tk_dxy_Error() * scoutingTrack.tk_dxy_Error(); // cov(3, 3)
    cov_vec[13] = scoutingTrack.tk_dxy_dsz_cov(); // cov(3, 4)
    cov_vec[14] = scoutingTrack.tk_dsz_Error() * scoutingTrack.tk_dsz_Error(); // cov(4, 4)
    reco::TrackBase::CovarianceMatrix cov(cov_vec.begin(), cov_vec.end());

    reco::TrackBase::TrackAlgorithm algo(reco::TrackBase::undefAlgorithm); // undefined
    reco::TrackBase::TrackQuality quality(reco::TrackBase::confirmed); // confirmed
    
    // the rests are default: t0 = 0, beta = 0, covt0t0 = -1, covbetabeta = -1 
  
    reco::Track recoTrack(chi2, ndof, referencePoint, momentum, charge, cov, algo, quality);

    return recoTrack;
}

reco::PFCandidate HLTScoutingUnpackProducer::createPFCandidate(Run3ScoutingParticle const& scoutingPFCandidate) {
    int pdgId = scoutingPFCandidate.pdgId();
    // fill mass and charge from pdgId
    float m = 0.;
    int charge = 0;
    auto particle_data_ptr = particle_data_table_->particle(HepPDT::ParticleID(pdgId)); // particle data
    // fake pdgId: h_HF (1), egamma_HF (2), X(0)
    if (!(pdgId == 1 || pdgId == 2 || pdgId == 0) && (particle_data_ptr != nullptr)) {
        m = particle_data_ptr->mass();
        charge = particle_data_ptr->charge();
    } else {
        return reco::PFCandidate();
    }
    
    // fill 4-momentum
    float px = scoutingPFCandidate.pt() * cos(scoutingPFCandidate.phi());
    float py = scoutingPFCandidate.pt() * sin(scoutingPFCandidate.phi());
    float pz = scoutingPFCandidate.pt() * sinh(scoutingPFCandidate.eta());
    float p = scoutingPFCandidate.pt() * cosh(scoutingPFCandidate.eta());
    float energy = std::sqrt(p * p + m * m);
    reco::Particle::LorentzVector p4(px, py, pz, energy);
    
    static const reco::PFCandidate dummy;
    return reco::PFCandidate(charge, p4, dummy.translatePdgIdToType(pdgId));
}

bool HLTScoutingUnpackProducer::hasPFTrackDetails(Run3ScoutingParticle const& scoutingPFCandidate) { 
    // retrive pdgId
    int pdgId = scoutingPFCandidate.pdgId();
    // no track for photon(22), neutral hadron(130), h_HF (1), egamma_HF (2), X(0)
    // see https://github.com/cms-sw/cmssw/blob/master/DataFormats/ParticleFlowCandidate/src/PFCandidate.cc#L231-L276
    if (pdgId == 22 || pdgId == 130 || pdgId == 1 || pdgId == 2 || pdgId == 0) {
        return false;
    }

    if (scoutingPFCandidate.normchi2() >= 900) { // 999
        return false;
    }
 
    auto particle_data_ptr = particle_data_table_->particle(HepPDT::ParticleID(pdgId)); // particle data
    if (particle_data_ptr == nullptr) {
        return false;
    }

    return true;
}

int HLTScoutingUnpackProducer::findCompatibleScoutingTrack(Run3ScoutingParticle const& scoutingPFCandidate, Run3ScoutingVertex const& scoutingPrimaryVertex0, std::unique_ptr<reco::TrackCollection> & recoTrack_collection_ptr) {
    int index = 0;
    reco::TrackBase::Point v0(scoutingPrimaryVertex0.x(), scoutingPrimaryVertex0.y(), scoutingPrimaryVertex0.z());

    // retrieve track parameters from PFCandidate
    float pt = scoutingPFCandidate.trk_pt();
    float eta = scoutingPFCandidate.trk_eta();
    float phi = scoutingPFCandidate.trk_phi();
    if (scoutingPFCandidate.relative_trk_vars()){
        pt += scoutingPFCandidate.pt();
        eta += scoutingPFCandidate.eta();
        phi += scoutingPFCandidate.phi();
    }
    float normchi2 = scoutingPFCandidate.normchi2();
    float dxy = scoutingPFCandidate.dxy();
    float dz = scoutingPFCandidate.dz();
    float dxysig = scoutingPFCandidate.dxysig();
    float dzsig = scoutingPFCandidate.dzsig();

    // https://www.boost.org/doc/libs/1_35_0/libs/test/doc/components/test_tools/floating_point_comparison.html
    auto is_close = [](float a, float b, float relative_tolerance) -> bool {
        return fabs(a-b) <= relative_tolerance * fmax(fabs(a), fabs(b));
    };

    for (auto const& recoTrack: *recoTrack_collection_ptr) { 
        if (is_close(normchi2, recoTrack.normalizedChi2(), 0.001)
            && is_close(dxy, recoTrack.dxy(v0), 0.5)
            && is_close(dz, recoTrack.dz(v0), 0.5)
            && is_close(dxysig, recoTrack.dxy(v0)/recoTrack.dxyError(), 0.5)
            && is_close(dzsig, recoTrack.dz(v0)/recoTrack.dzError(), 0.5)
            && is_close(pt, recoTrack.pt(), 0.000001)
            && is_close(eta, recoTrack.eta(), 0.000001)
            && is_close(phi, recoTrack.phi(), 0.000001)
           ) {
            return index;
        }
        index++;
    }
    return -1;
}

// example from https://github.com/cms-sw/cmssw/blob/master/DataFormats/PatCandidates/src/PackedCandidate.cc#L219
void HLTScoutingUnpackProducer::buildHitPattern(Run3ScoutingParticle const& scoutingPFCandidate, Run3ScoutingTrack const& scoutingTrack, reco::Track & recoTrack) {
    // retrieve information from scoutingPFCandidate
    auto lost_inner_hits = static_cast<pat::PackedCandidate::LostInnerHits>(static_cast<int8_t>(scoutingPFCandidate.lostInnerHits()));

    // retrieve information from scoutingTrack
    int number_of_pixel_hits = scoutingTrack.tk_nValidPixelHits();
    int number_of_strip_hits = scoutingTrack.tk_nValidStripHits();
    int number_of_tracker_layers_with_measurement = scoutingTrack.tk_nTrackerLayersWithMeasurement(); // pixel + strip number of layers?
    int number_of_hits = number_of_pixel_hits + number_of_strip_hits;

    // pixel has 7 layers: 4 in BPIX + 3 FPIX
    int number_of_pxb_layers = 4;
    int number_of_pxf_layers = 3;
    int number_of_pixel_layers = number_of_pxb_layers + number_of_pxf_layers;
    // we assume the number of pixel layers with measurement is min(number_of_pixel_layers, number_of_layers_with_measurement)
    // in fact, even if we have number of layers with measurement more than number of pixel layers, we can have pixel layers with measurement less than number of pixel layers
    // but we don't have access to this information, so we will make this assumption here
    int number_of_pixel_layers_with_measurement = number_of_tracker_layers_with_measurement > number_of_pixel_layers ? number_of_pixel_layers : number_of_tracker_layers_with_measurement; 
    // number of pixel layers with measurement cannot exceed number of pixel hits
    number_of_pixel_layers_with_measurement = number_of_pixel_layers_with_measurement > number_of_pixel_hits ? number_of_pixel_hits : number_of_pixel_layers_with_measurement;
    
    // strip has 22 layers: 4 TIB + 3 TID + 6 TOB + 9 TEC
    int number_of_tib_layers = 4;
    int number_of_tid_layers = 3;
    int number_of_tob_layers = 6;
    int number_of_tec_layers = 9;
    int number_of_strip_layers = number_of_tib_layers + number_of_tob_layers + number_of_tid_layers + number_of_tec_layers;

    // assume the remaining layers with measuremnet are in strip
    int number_of_strip_layers_with_measurement = number_of_tracker_layers_with_measurement - number_of_pixel_layers_with_measurement;
    // number of strip layers with measurement cannot exceed number of strip layers
    // in fact, this it exceeds, we should throw error
    number_of_strip_layers_with_measurement = number_of_strip_layers_with_measurement > number_of_strip_layers ? number_of_strip_layers : number_of_strip_layers_with_measurement;
    // number of strip layers with measurement cannot exceed number of strip hits
    number_of_strip_layers_with_measurement = number_of_strip_layers_with_measurement > number_of_strip_hits ? number_of_strip_hits : number_of_strip_layers_with_measurement;
 
    // now, proceed similar to PackedCandidate
    uint16_t first_hit = 0; // assume 0 since ScoutingTrack does not save HitPattern

    int i = 0;

    if (first_hit == 0) {
        if (lost_inner_hits == pat::PackedCandidate::validHitInFirstPixelBarrelLayer) {
            recoTrack.appendTrackerHitPattern(PixelSubdetector::PixelBarrel, 1, 0, TrackingRecHit::valid);
            i = 1;
        }
    } else {
        recoTrack.appendHitPattern(first_hit, TrackingRecHit::valid);
        if (reco::HitPattern::pixelHitFilter(first_hit)) {
            i = 1;
        }
    }

    // add hits to match the number of layers and validHitInFirstPixelBarrelLayer
    if (lost_inner_hits == pat::PackedCandidate::validHitInFirstPixelBarrelLayer) {
        for (; i < number_of_pixel_layers_with_measurement; i++) {
            if (i <= 3) {
                recoTrack.appendTrackerHitPattern(PixelSubdetector::PixelBarrel, i + 1, 0, TrackingRecHit::valid);
            } else {
                recoTrack.appendTrackerHitPattern(PixelSubdetector::PixelEndcap, i - 3, 0, TrackingRecHit::valid);
            }
        }
    } else {
        int i_offset = 0;
        if (first_hit != 0 && reco::HitPattern::pixelHitFilter(first_hit)) {
            i_offset = reco::HitPattern::getLayer(first_hit);
            if (reco::HitPattern::getSubStructure(first_hit) == PixelSubdetector::PixelEndcap) {
                i_offset += 3;
            }
        } else {
            i_offset = 1;
        }
        for (; i < number_of_pixel_layers_with_measurement; i++) {
            if (i + i_offset <= 2) {
                recoTrack.appendTrackerHitPattern(PixelSubdetector::PixelBarrel, i + i_offset + 1, 0, TrackingRecHit::valid);
            } else {
                recoTrack.appendTrackerHitPattern(PixelSubdetector::PixelEndcap, i + i_offset + 1 - 3, 0, TrackingRecHit::valid);
            } 
        }
    }

    // add extra hits (overlaps, etc), all on the first layer with a hit
    // to avoid increasing the layer count
    for (; i < number_of_pixel_hits; i++) {
        if (first_hit != 0 && reco::HitPattern::pixelHitFilter(first_hit)) {
            recoTrack.appendTrackerHitPattern(reco::HitPattern::getSubStructure(first_hit), reco::HitPattern::getLayer(first_hit), 0, TrackingRecHit::valid);
        } else {
            recoTrack.appendTrackerHitPattern(PixelSubdetector::PixelBarrel, lost_inner_hits == pat::PackedCandidate::validHitInFirstPixelBarrelLayer ? 1 : 2, 0, TrackingRecHit::valid);
        }
    }
 
    // now start adding strip layers, putting one hit on each layer
    // we don't know what the layers where, so we just start with 4 TIB, then 3 TID, then 6 TOB, and then 9 TEC
    // note the comment in PackedCandidate is incorrect 
    if (first_hit != 0 && reco::HitPattern::stripHitFilter(first_hit)) {
        i += 1;
    }
    int sl_offset = 0;
    if (first_hit != 0 && reco::HitPattern::stripHitFilter(first_hit)) {
        sl_offset = reco::HitPattern::stripHitFilter(first_hit) - 1;
        if (reco::HitPattern::getSubStructure(first_hit) == StripSubdetector::TID)
            sl_offset += 4;
        if (reco::HitPattern::getSubStructure(first_hit) == StripSubdetector::TOB)
            sl_offset += 7;
        if (reco::HitPattern::getSubStructure(first_hit) == StripSubdetector::TEC)
            sl_offset += 13;
    }

    for (int sl = sl_offset; sl < number_of_strip_layers_with_measurement + sl_offset; sl++, i++) {
        if (sl < 4) {
            recoTrack.appendTrackerHitPattern(StripSubdetector::TIB, sl + 1, 1, TrackingRecHit::valid);
        } else if (sl < 4 + 3) {
            recoTrack.appendTrackerHitPattern(StripSubdetector::TID, (sl - 4) + 1, 1, TrackingRecHit::valid);
        } else if (sl < 7 + 6) {
            recoTrack.appendTrackerHitPattern(StripSubdetector::TOB, (sl - 7) + 1, 1, TrackingRecHit::valid);
        } else if (sl < 13 + 9) {
            recoTrack.appendTrackerHitPattern(StripSubdetector::TEC, (sl - 13) + 1, 1, TrackingRecHit::valid);
        } else {
            break;
        }
    }

    for (; i < number_of_hits; i++) {
        if (reco::HitPattern::stripHitFilter(first_hit)) {
            recoTrack.appendTrackerHitPattern(reco::HitPattern::getSubStructure(first_hit), reco::HitPattern::getLayer(first_hit), 1, TrackingRecHit::valid);
        } else {
            recoTrack.appendTrackerHitPattern(StripSubdetector::TIB, 1, 1, TrackingRecHit::valid);
        }
    }

    switch (lost_inner_hits) {
        case pat::PackedCandidate::validHitInFirstPixelBarrelLayer:
            break;
        case pat::PackedCandidate::noLostInnerHits:
            break;
        case pat::PackedCandidate::oneLostInnerHit:
            recoTrack.appendTrackerHitPattern(PixelSubdetector::PixelBarrel, 1, 0, TrackingRecHit::missing_inner);
            break;
        case pat::PackedCandidate::moreLostInnerHits:
            recoTrack.appendTrackerHitPattern(PixelSubdetector::PixelBarrel, 1, 0, TrackingRecHit::missing_inner);
            recoTrack.appendTrackerHitPattern(PixelSubdetector::PixelBarrel, 2, 0, TrackingRecHit::missing_inner);
            break;
    };

    //std::cout << "pixel hits expected: " << number_of_pixel_hits << " get: " << recoTrack.hitPattern().numberOfValidPixelHits() << " strip hits expected: " << number_of_strip_hits << " get: " << recoTrack.hitPattern().numberOfValidStripHits();
    //std::cout << " layers with measurement expect: " << number_of_tracker_layers_with_measurement << " get: " << recoTrack.hitPattern().trackerLayersWithMeasurement() << std::endl;
}

std::unique_ptr<reco::Track> HLTScoutingUnpackProducer::createPFTrack(Run3ScoutingParticle const& scoutingPFCandidate,
                                                                      edm::Handle<Run3ScoutingVertexCollection> const& scoutingPrimaryVertex_collection_handle) {
    
    int pdgId = scoutingPFCandidate.pdgId(); 
    int charge = particle_data_table_->particle(HepPDT::ParticleID(pdgId))->charge();

    // fill chi2 and ndof
    // only save normalized chi2 = chi2/ndof is saved, assume ndof = 1
    float chi2 = scoutingPFCandidate.normchi2();
    int ndof = 1;

    // retrieve track parameters
    float pt = scoutingPFCandidate.trk_pt();
    float eta = scoutingPFCandidate.trk_eta();
    float phi = scoutingPFCandidate.trk_phi();
    if (scoutingPFCandidate.relative_trk_vars()){
        pt += scoutingPFCandidate.pt();
        eta += scoutingPFCandidate.eta();
        phi += scoutingPFCandidate.phi();
    }
  
    // fill momentum
    float px = pt * cos(phi);
    float py = pt * sin(phi);
    float pz = pt * sinh(eta);
    float p = pt * cosh(eta);
    reco::TrackBase::Vector momentum(px, py, pz);
    
    // fill 5D curvilinear covariance matrix
    // only dxysig and dzsig are stored
    std::vector<float> cov_vec(15, 0); // number of element is 5*(5+1)/2 = 15, default value to 0
    float dxy = scoutingPFCandidate.dxy();
    float dz = scoutingPFCandidate.dz();
    float dxyError = dxy / scoutingPFCandidate.dxysig();
    float dzError = dz / scoutingPFCandidate.dzsig();
    float dszError = dzError * pt/p;
    //cov_vec[0] = 999; 
    //cov_vec[2] = 999;
    //cov_vec[5] = 999;
    cov_vec[9] = dxyError * dxyError;
    cov_vec[14] = dszError * dszError;
    reco::TrackBase::CovarianceMatrix cov(cov_vec.begin(), cov_vec.end());

    reco::TrackBase::TrackAlgorithm algo(reco::TrackBase::undefAlgorithm); // undefined
    reco::TrackBase::TrackQuality quality(reco::TrackBase::undefQuality); // undefined for constructor, but will set qualityMask later

    // the rests are default: t0 = 0, beta = 0, covt0t0 = -1, covbetabeta = -1

    // fill reference point
    // reference point is not stored, try PFCandidate's vertex, otherwise default to closest point to PV0 
    Run3ScoutingVertex pv0 = scoutingPrimaryVertex_collection_handle->at(0);
    reco::TrackBase::Point pv0_point(pv0.x(), pv0.y(), pv0.z());
    int vertex_index = scoutingPFCandidate.vertex();
    // try using PFCandidate's vertex as referencePoint
    if (vertex_index >= 0) {
        Run3ScoutingVertex pv = scoutingPrimaryVertex_collection_handle->at(vertex_index);
        reco::TrackBase::Point referencePoint(pv.x(), pv.y(), pv.z());
        auto recoTrack_ptr = std::make_unique<reco::Track>(chi2, ndof, referencePoint, momentum, charge, cov, algo, quality);
        float epsilon = 0.0001;
        if (fabs(recoTrack_ptr->dxy(pv0_point) - scoutingPFCandidate.dxy()) < epsilon
            && fabs(recoTrack_ptr->dxy(pv0_point)/recoTrack_ptr->dxyError() - scoutingPFCandidate.dxysig()) < epsilon
            && fabs(recoTrack_ptr->dz(pv0_point) - scoutingPFCandidate.dz()) < epsilon
            && fabs(recoTrack_ptr->dz(pv0_point)/recoTrack_ptr->dzError() - scoutingPFCandidate.dzsig()) < epsilon) {
            // set quality
            recoTrack_ptr->setQualityMask(static_cast<int8_t>(scoutingPFCandidate.quality()));
            return recoTrack_ptr;
        }
    }
    // estimate to closest point to PV0
    float vx = pv0.x() - fabs(dxy)*sin(phi);
    float vy = pv0.y() + fabs(dxy)*cos(phi);
    float vz = pv0.z() + dz;
    reco::TrackBase::Point referencePoint(vx, vy, vz);
    // create reco::track
    auto recoTrack_ptr = std::make_unique<reco::Track>(chi2, ndof, referencePoint, momentum, charge, cov, algo, quality);
    // set quality
    recoTrack_ptr->setQualityMask(static_cast<int8_t>(scoutingPFCandidate.quality()));

    return recoTrack_ptr;
}

template <typename RecoObjectType, typename ScoutingObjectType>
void HLTScoutingUnpackProducer::putWithRef(edm::Event& iEvent, std::string const& name,
                                           std::unique_ptr<std::vector<RecoObjectType>>& recoObject_collection_ptr, std::unique_ptr<RefCollection<ScoutingObjectType>>& scoutingObjectRef_collection_ptr) {
    auto recoObject_collection_handle = iEvent.put(std::move(recoObject_collection_ptr), name);

    std::unique_ptr<RefMap<ScoutingObjectType>> refmap_to_scouting(new RefMap<ScoutingObjectType>());
    typename RefMap<ScoutingObjectType>::Filler filler_refmap_to_scouting(*refmap_to_scouting);
    filler_refmap_to_scouting.insert(recoObject_collection_handle, scoutingObjectRef_collection_ptr->begin(), scoutingObjectRef_collection_ptr->end());
    filler_refmap_to_scouting.fill();
    iEvent.put(std::move(refmap_to_scouting), name + REF_TO_SCOUTING_LABEL_SUFFIX_);
}

void HLTScoutingUnpackProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;

    desc.add<edm::InputTag>("scoutingPFJet", edm::InputTag("hltScoutingPFPacker"));
    desc.add<edm::InputTag>("scoutingPFCandidate", edm::InputTag("hltScoutingPFPacker"));
    desc.add<edm::InputTag>("scoutingTrack", edm::InputTag("hltScoutingTrack"));
    desc.add<edm::InputTag>("scoutingPrimaryVertex", edm::InputTag("hltScoutingPrimaryVertex"));
    
    desc.add<bool>("producePFCandidate", true);
    desc.add<bool>("producePFCandidateMatchTrack", false)->setComment("if PFCandidate has track, keep only ones that can be matched to track");
    desc.add<bool>("producePFCHSCandidate", false);
    //desc.add<bool>("producePFSKCandidate", false);

    descriptions.addWithDefaultLabel(desc);
}

DEFINE_FWK_MODULE(HLTScoutingUnpackProducer);
