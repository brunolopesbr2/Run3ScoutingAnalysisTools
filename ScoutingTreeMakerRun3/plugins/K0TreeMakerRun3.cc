// -*- C++ -*-
//
// Package:    Run3ScoutingAnalysisTools/K0TreeMakerRun3
// Class:      K0TreeMakerRun3
//
/**\class K0TreeMakerRun3 K0TreeMakerRun3.cc Run3ScoutingAnalysisTools/K0TreeMakerRun3/plugins/K0TreeMakerRun3.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  David Sperka
//         Created:  Sat, 11 Feb 2023 14:15:08 GMT
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

class K0TreeMakerRun3 : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:

  explicit K0TreeMakerRun3(const edm::ParameterSet&);
  ~K0TreeMakerRun3() override;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  using Run3ScoutingParticleCollection = std::vector<Run3ScoutingParticle>;
private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  void endJob() override;
  //void beginRun(edm::Run const&, edm::EventSetup const&) override;
  //void endRun(edm::Run const&, edm::EventSetup const&) override;
  //void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
  //void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;   

  const int required_ntk;
  
  const edm::EDGetTokenT<std::vector<Run3ScoutingMuon> >      muonsToken;
  const edm::EDGetTokenT<std::vector<Run3ScoutingElectron> >  electronsToken;
  const edm::EDGetTokenT<std::vector<reco::Vertex> >    primaryVerticesToken;
  //const edm::EDGetTokenT<std::vector<Run3ScoutingVertex> >    verticesToken;
  const edm::EDGetTokenT<double>                          rhoToken;
  const edm::EDGetTokenT<std::vector<Run3ScoutingPhoton> >  photonsToken;
  const edm::EDGetTokenT<std::vector<reco::PFJet> >  pfjetsToken;
  const edm::EDGetTokenT<std::vector<pat::Jet> >  patjetsToken;
  //const edm::EDGetTokenT<std::vector<Run3ScoutingTrack> >  tracksToken;
  const edm::EDGetTokenT<std::vector<reco::Track> >  tracksToken;
  const edm::EDGetTokenT<edm::ValueMap<edm::Ref<std::vector<Run3ScoutingTrack>>> >  tracksRefToken;
  const edm::EDGetTokenT<std::vector<reco::Vertex> >  verticesToken;

  //For reco-scout comparison
  const edm::EDGetTokenT<std::vector<reco::Track> >  recoTracksToken;

  const edm::EDGetTokenT<std::vector<PileupSummaryInfo>> truePileupToken;

  const edm::ESGetToken<BeamSpotOnlineObjects, BeamSpotOnlineHLTObjectsRcd> bsOnlineToken_;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_token;
  const edm::EDGetTokenT<std::vector<reco::GenParticle>> GenParticleToken_;
  const edm::EDGetTokenT<std::vector<reco::GenJet>> GenJetToken_;
  const edm::EDGetTokenT<GenEventInfoProduct> GeneratorToken_;
  const edm::ESGetToken<TransientTrackBuilder, TransientTrackRecord> token_builder;
  const edm::EDGetTokenT<Run3ScoutingParticleCollection> scoutingParticle_collection_token_;
  
  std::vector<std::string> triggerPathsVector;
  std::map<std::string, int> triggerPathsMap;

  bool isScouting;
  bool doPhiCorrection;
  bool doGenMatching;
  bool fillScoutTrack;
  double luminosity;
  double crossSection;
  std::vector<double> PUCorrectionArray;
  double isMC;

  triggerExpression::Data triggerCache_;

  bool L1_HTT200er;
  bool L1_HTT255er;
  bool L1_HTT280er;
  bool L1_HTT320er;
  bool L1_HTT360er;
  bool L1_HTT400er;
  bool L1_HTT450er;
  bool L1_ETT2000;
  bool L1_SingleJet180;
  bool L1_SingleJet200;
  bool L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5;
  bool L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5;
  bool L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5;
  bool L1_FinalResult;
  bool HLT_FinalResult;
  
  const edm::EDGetTokenT<std::map<std::string, float>> weightsToken_;

  TTree* tree;
  TTree* objectTree;

  int nPFJets;

  float HT;
  
  float ptjet1;
  float ptjet2;
  float ptjet3;
  float ptjet4;

  float etajet1;
  float etajet2;
  float etajet3;
  float etajet4;

  float phijet1;
  float phijet2;
  float phijet3;
  float phijet4; 
  
  int nVertices;

  int nPV;
  int observedPU;
  int truePU;
  
  int ntk_1;
  int ntk_2;
  
  float bs2derr_1;
  float bs2derr_2;

  float dBV_1;
  float dBV_2;

  float genVert_x_1 = -999;
  float genVert_y_1 = -999;
  float genVert_z_1 = -999;
  float genVert_dBV_1 = -999;
  float genVert_3d_1 = -999;
  float genVert_motherEta = -999;
  float genVert_motherPhi = -999;
  float genVert_motherPt = -999;
  float genVert_motherDistTraveled = -999;
  float genVert_dVV_2 = -999;
  float genVert_dPhi_2 = -999;
  int genScout_nMatches = -999;
  int genScoutVert_nMatches = -999;
  
  std::vector<float>* scoutTrack_pt;
  std::vector<float>* scoutTrack_eta;
  std::vector<float>* scoutTrack_phi;
  std::vector<float>* scoutTrack_phiBeamspot;
  std::vector<float>* scoutTrack_reducedChi2;
  std::vector<float>* scoutTrack_charge;
  std::vector<float>* scoutTrack_dxy;
  std::vector<float>* scoutTrack_dxyErr;
  std::vector<float>* scoutTrack_dxySig;
  std::vector<float>* scoutTrack_dxySigned;
  std::vector<float>* scoutTrack_d3D;
  std::vector<float>* scoutTrack_d3DErr;
  std::vector<float>* scoutTrack_d3DSig;
  std::vector<float>* scoutTrack_dz;
  std::vector<float>* scoutTrack_dzErr;
  std::vector<float>* scoutTrack_dzSig;
  std::vector<float>* scoutTrack_dszUncertainty;
  std::vector<float>* scoutTrack_dxyUncertainty;
  std::vector<float>* scoutTrack_dszdxyCovariance;
  std::vector<float>* scoutTrack_vx;
  std::vector<float>* scoutTrack_vy;
  std::vector<int>* scoutTrack_iJet;
  std::vector<int>* scoutTrack_nValidPixelHits;
  std::vector<int>* scoutTrack_nTrackerLayersWithMeasurement;
  std::vector<int>* scoutTrack_nValidStripHits;
  std::vector<int>* scoutTrack_nMissingInnerHits;
  std::vector<float>* scoutTrack_minPVDxy;
  std::vector<float>* scoutTrack_minPVDz;

  std::vector<float>* vertTrack_pt;
  std::vector<float>* vertTrack_eta;
  std::vector<float>* vertTrack_phi;
  std::vector<float>* vertTrack_reducedChi2;
  std::vector<float>* vertTrack_charge;
  std::vector<float>* vertTrack_dxy;
  std::vector<float>* vertTrack_dxyErr;
  std::vector<float>* vertTrack_dxySig;
  std::vector<float>* vertTrack_dxySigned;
  std::vector<float>* vertTrack_d3D;
  std::vector<float>* vertTrack_d3DErr;
  std::vector<float>* vertTrack_d3DSig;
  std::vector<float>* vertTrack_dz;
  std::vector<float>* vertTrack_dzErr;
  std::vector<float>* vertTrack_dzSig;
  std::vector<int>* vertTrack_nValidPixelHits;
  std::vector<int>* vertTrack_nTrackerLayersWithMeasurement;
  std::vector<int>* vertTrack_nValidStripHits;
  std::vector<int>* vertTrack_nMissingInnerHits;
  std::vector<int>* vertTrack_iVtx;
  std::vector<int>* vertTrack_iJet;
  std::vector<bool>* vertTrack_hasPFMatch;

  std::vector<float>* reco_dpt_diff;
  std::vector<float>* reco_deta_diff;
  std::vector<float>* reco_dphi_diff;
  std::vector<float>* reco_dxy_diff;
  std::vector<float>* reco_dchi2_diff;
  
  std::vector<float>* match_ptRatio;
  std::vector<float>* match_deltaR;
  std::vector<float>* match_diffPt;
  std::vector<float>* match_diffEta;
  std::vector<float>* match_diffPhi;
  std::vector<float>* match_diffPhiCorrected;
  std::vector<float>* match_gen_dxy;
  std::vector<float>* match_gen_dxyCorrected;
  std::vector<float>* match_diffDxy;
  std::vector<float>* match_diffDxyCorrected;
  std::vector<float>* gen_dxy;
  std::vector<float>* gen_dxyCorrected;
  std::vector<float>* match_vert_x;
  std::vector<float>* match_vert_y;
  std::vector<float>* match_genVert_x;
  std::vector<float>* match_genVert_y;
  std::vector<float>* match_genVert_dBV;
  std::vector<float>* genVert_dBV;
  std::vector<float>* genVert_phi;
  std::vector<float>* genVert_z;
  std::vector<float>* genVert_x;
  std::vector<float>* genVert_y;
  std::vector<float>* genVert_nParticles;
  std::vector<float>* genVert_dPhi;
  std::vector<float>* genVert_dVV;
  int genVert_nVertices;
  std::vector<float>* resVert_x;
  std::vector<float>* resVert_y;
  std::vector<float>* resVert_z;
  std::vector<float>* scoutVert_dBV;
  std::vector<float>* scoutVert_dPVV;
  std::vector<float>* scoutVert_dBVErr;
  std::vector<float>* scoutVert_dPVVErr;
  std::vector<float>* scoutVert_phi;
  std::vector<float>* scoutVert_z;
  std::vector<float>* scoutVert_x;
  std::vector<float>* scoutVert_y;
  std::vector<float>* scoutVert_nTracks;
  std::vector<float>* scoutVert_chi2;
  std::vector<float>* scoutVert_dPhi;
  std::vector<float>* scoutVert_dVV;
  std::vector<float>* scoutVert_dT;
  std::vector<float>* scoutVert_cosT;
  std::vector<float>* scoutVert_pMag;
  std::vector<float>* scoutVert_costh2;
  std::vector<float>* scoutVert_ctau;
  std::vector<float>* scoutVert_pt;
  std::vector<float>* scoutVert_mass;
  int scoutVert_nVertices;
  double weight;
  double uncorrectedWeight;
  double weight_PU_BCDEFGHI_nominal;
  double weight_PU_BCDEFGHI_up;
  double weight_PU_BCDEFGHI_down;
  double weight_PU_C_nominal;
  double weight_PU_C_up;
  double weight_PU_C_down;
  double weight_PU_D_nominal;
  double weight_PU_D_up;
  double weight_PU_D_down;
  double weight_PU_E_nominal;
  double weight_PU_E_up;
  double weight_PU_E_down;
  double weight_PU_F_nominal;
  double weight_PU_F_up;
  double weight_PU_F_down;
  double weight_PU_G_nominal;
  double weight_PU_G_up;
  double weight_PU_G_down;
  double weight_PU_H_nominal;
  double weight_PU_H_up;
  double weight_PU_H_down;
  double weight_PU_I_nominal;
  double weight_PU_I_up;
  double weight_PU_I_down;
  float beamspot_x;
  float beamspot_y;
  float beamspot_z;
  float beamspot_xErr;
  float beamspot_yErr;
  float beamspot_zErr;
  float beamspot_xWidth;
  float beamspot_yWidth;
  float beamspot_widthErr;
  int beamspot_type;
  float offlineBeamspot_x;
  float offlineBeamspot_y;
  float offlineBeamspot_z;
  float offlineBeamspot_xErr;
  float offlineBeamspot_yErr;
  float offlineBeamspot_zErr;

  float ht_corrected;
  
  int eventId;
  int runNumber;
  int lumiBlock;

  std::vector<float>* jet_pt;
  std::vector<float>* jet_eta;
  std::vector<float>* jet_phi;
  std::vector<float>* jet_mass;
  std::vector<float>* jet_energy;
  std::vector<float>* jet_chHEF;
  std::vector<float>* jet_neHEF;
  std::vector<float>* jet_muonEF;
  std::vector<float>* jet_chEmEF;
  std::vector<float>* jet_neEmEF;
  std::vector<float>* jet_hfHEF;
  std::vector<float>* jet_hfEmEF;
  std::vector<float>* jet_hoEF;
  std::vector<int>* jet_chMultiplicity;
  std::vector<int>* jet_neMultiplicity;
  std::vector<bool>* jet_passJetIdTight;

  std::vector<float>* genJet_pt;
  std::vector<float>* genJet_eta;
  std::vector<float>* genJet_phi;
  std::vector<float>* genJet_mass;
  std::vector<float>* genJet_energy;
  std::vector<int>* genJet_nConstituents;
  float genHT;
  int nGenJets;

  std::vector<float>* muon_pt;
  std::vector<float>* muon_eta;
  std::vector<float>* muon_phi;
  std::vector<float>* muon_chi2;
  std::vector<int>* muon_nTrackerLayersWithMeasurement;
  std::vector<int>* muon_nValidPixelHits;
  std::vector<int>* muon_nValidRecoMuonHits;
  std::vector<int>* muon_nRecoMuonMatchedStations;
  std::vector<float>* muon_trackIso;
  
  TH1F* h_match_gen_dxy = new TH1F("match_gen_dxy",";Gen particle d_{xy} [cm]; Gen particles / 0.01 cm", 100, 0, 1);
  TH1F* h_gen_dxy = new TH1F("gen_dxy",";Gen particle d_{xy} [cm]; Gen particles / 0.01 cm", 100, 0, 1);
  TH2F* h_match_vert_x_y = new TH2F("match_vert_x_y","Vertex Position; X Position [cm] / 0.02 cm; Y Position [cm] / 0.02 cm", 100, -1, 1, 100, -1, 1);
  TH2F* h_match_genVert_x_y = new TH2F("match_genVert_x_y","Gen Vertex Position; X Position [cm] / 0.02 cm; Y Position [cm] / 0.02 cm", 100, -1, 1, 100, -1, 1);
  TH1F* h_match_genVert_dBV = new TH1F("match_genVert_dBV",";Gen Vertex d_{BV} [cm]; Gen Vertices / 0.01 cm", 100, 0, 1);
  TH1F* h_genVert_dBV = new TH1F("genVert_dBV",";Gen Vertex d_{BV} [cm]; Gen Vertices / 0.01 cm", 100, 0, 1);
  TH1F* h_genVert_phi = new TH1F("genVert_phi",";Gen Vertex #phi; Gen Vertices / 0.06284", 100, -3.142, 3.142);
  TH1F* h_genVert_z = new TH1F("genVert_z",";Gen Vertex z [cm]; Gen Vertices / 0.4 cm", 100, -20, 20);
  TH2F* h_genVert_x_y = new TH2F("genVert_x_y","Gen Vertex Position; X Position [cm] / 0.02 cm; Y Position [cm] / 0.02 cm", 100, -1, 1, 100, -1, 1);
  TH1F* h_genVert_nParticles = new TH1F("genVert_nParticles",";Gen Vertex Number of Particles; Gen Vertices / 1", 100, 0, 100);
  TH1F* h_genVert_dPhi = new TH1F("genVert_dPhi",";Gen Vertex d#phi; Occurrences / 0.03142", 100, 0, 3.142);
  TH1F* h_genVert_dVV = new TH1F("genVert_dVV",";Gen Vertex d_{VV} [cm]; Occurrences / 0.015 cm", 1000, 0, 15);
  TH1F* h_genVert_nVertices = new TH1F("genVert_nVertices",";Number of Gen Vertices; Occurrences / 1", 5, 0, 5);
  TH1F* h_resVert_x = new TH1F("resVert_x",";Gen X Position - Scout X Position [cm]; Gen Vertices / 0.02 cm", 100, -1, 1);
  TH1F* h_resVert_y = new TH1F("resVert_y",";Gen Y Position - Scout Y Position [cm]; Gen Vertices / 0.02 cm", 100, -1, 1);
  TH1F* h_resVert_z = new TH1F("resVert_z",";Gen Z Position - Scout Z Position [cm]; Gen Vertices / 0.02 cm", 100, -1, 1);
  TH1F* h_scoutVert_dBV = new TH1F("scoutVert_dBV",";Scout Vertex d_{BV} [cm]; Scout Vertices / 0.01 cm", 100, 0, 1);
  TH1F* h_scoutVert_phi = new TH1F("scoutVert_phi",";Scout Vertex #phi; Scout Vertices / 0.06284", 100, -3.142, 3.142);
  TH1F* h_scoutVert_z = new TH1F("scoutVert_z",";Scout Vertex z [cm]; Scout Vertices / 0.4 cm", 100, -20, 20);
  TH2F* h_scoutVert_x_y = new TH2F("scoutVert_x_y","Scout Vertex Position; X Position [cm] / 0.02 cm; Y Position [cm] / 0.02 cm", 100, -1, 1, 100, -1, 1);
  TH1F* h_scoutVert_nTracks = new TH1F("scoutVert_nTracks",";Scout Vertex Number of Particles; Scout Vertices / 1", 100, 0, 100);
  TH1F* h_scoutVert_dPhi = new TH1F("scoutVert_dPhi",";Scout Vertex d#phi; Occurrences / 0.03142", 100, 0, 3.142);
  TH1F* h_scoutVert_dVV = new TH1F("scoutVert_dVV",";Scout Vertex d_{VV} [cm]; Occurrences / 0.015 cm", 1000, 0, 15);
  TH1F* h_scoutVert_nVertices = new TH1F("scoutVert_nVertices",";Number of Scout Vertices; Occurrences / 1", 10, 0, 10);
  TH1D* h_genWeights = new TH1D("genWeights",";Cut Applied; Sum of Gen Weights",5,0,5);
  TH1D* h_weights = new TH1D("weights",";Cut Applied; Sum of Weights",5,0,5);
  TH1D* h_weightsSquared = new TH1D("weightsSquared",";Cut Applied; Sum of Squared Weights",5,0,5);
  TH1D* h_weights_LUMCorrected = new TH1D("weightsLUMCorrected",";Cut Applied; Sum of Weights",5,0,5);
  TH1D* h_weightsSquared_LUMCorrected = new TH1D("weightsSquaredLUMCorrected",";Cut Applied; Sum of Squared Weights",5,0,5);
    
  typedef std::set<reco::TrackRef> track_set;
  typedef std::vector<reco::TrackRef> track_vec;
  
  static bool CompareDeltaR(std::vector<float> a, std::vector<float> b) { return a[2] < b[2]; }

  int findCompatibleScoutingTrack(edm::Handle<Run3ScoutingParticleCollection> const& scoutingParticleCollection, edm::Ref<std::vector<Run3ScoutingTrack> > scoutingTrack) {
    int index = 0;
    auto is_close = [](float a, float b, float relative_tolerance) -> bool {
      return fabs(a-b) <= relative_tolerance * fmax(fabs(a), fabs(b));
    };
    for (size_t pf_index = 0; pf_index < scoutingParticleCollection->size(); pf_index++) {
      auto & scoutingPFCandidate = scoutingParticleCollection->at(pf_index);
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
      if (is_close(normchi2, scoutingTrack->tk_chi2()/scoutingTrack->tk_ndof(), 0.001)
	  && is_close(pt, scoutingTrack->tk_pt(), 0.000001)
	  && is_close(eta, scoutingTrack->tk_eta(), 0.000001)
	  && is_close(phi, scoutingTrack->tk_phi(), 0.000001)
	  ) {
	return index;
      }
      index++;
    }
    return -1;
  }
  
  std::pair<bool,GlobalPoint> isStopDecay(const reco::Candidate* part){
    if(fabs(part->pdgId())==1000006 && part->numberOfDaughters()==2){
      int daughterId = part->daughter(0)->pdgId();
      bool sameDaughters = (daughterId==part->daughter(1)->pdgId());
      if(sameDaughters && fabs(daughterId)==1){
	return std::make_pair(true, GlobalPoint(part->daughter(0)->vx(),part->daughter(0)->vy(),part->daughter(0)->vz()));
      }
    }
    return std::make_pair(false, GlobalPoint(-999,-999,-999));
  }

  std::pair<bool,GlobalPoint> isStopDecay(std::vector<reco::GenParticle>::const_iterator part){
    if(fabs(part->pdgId())==1000006 && part->numberOfDaughters()==2){
      int daughterId = part->daughter(0)->pdgId();
      bool sameDaughters = (daughterId==part->daughter(1)->pdgId());
      if(sameDaughters && fabs(daughterId)==1){
	return std::make_pair(true, GlobalPoint(part->daughter(0)->vx(),part->daughter(0)->vy(),part->daughter(0)->vz()));
      }
    }
    return std::make_pair(false, GlobalPoint(-999,-999,-999));
  }

  std::pair<bool,GlobalPoint> isChargedStopDecayProductStatusOne(std::vector<reco::GenParticle>::const_iterator part){
    if(part->status()!=1 || part->charge()==0 || part->numberOfMothers()==0) return std::make_pair(false,GlobalPoint(-999,-999,-999));
    const reco::Candidate* candidate = part->mother(0);
    std::pair<bool,GlobalPoint> isStopProduct = std::make_pair(false,GlobalPoint(-999,-999,-999));
    while(!isStopProduct.first){
      isStopProduct = isStopDecay(candidate);
      if(candidate->numberOfMothers()==0) break;
      candidate = candidate->mother(0);
    }
    return isStopProduct;
  }
  
  const reco::Candidate* getFinalCopy(std::vector<reco::GenParticle>::const_iterator part){
    const reco::Candidate* candidate = part->clone();
    if(part->numberOfDaughters()==0) return candidate;
    bool foundLast = false;
    while(!foundLast){
      int selfIndex = -1;
      for(uint i=0; i<candidate->numberOfDaughters(); i++){
	if(candidate->daughter(i)->pdgId()==candidate->pdgId()) selfIndex = i;
      }
      if(selfIndex==-1){
	foundLast=true;
      }
      else{
	candidate = candidate->daughter(selfIndex);
      }
    }
    return candidate;
    
  }

  template <typename T>
  std::pair<double,double> gen_dxy_correction(std::vector<reco::GenParticle>::const_iterator gtk, const T refpoint){
    // calculate dxy for gen track
    double r = 88.*gtk->pt();
    double cx = gtk->vx() + gtk->charge() * r * sin(gtk->phi());
    double cy = gtk->vy() - gtk->charge() * r * cos(gtk->phi());
    double dxy = fabs(r-sqrt(pow((cx-( refpoint->x0() )), 2) + pow((cy-( refpoint->y0() )), 2)));

    double vX = refpoint->x0() - cx;
    double vY = refpoint->y0() - cy;
    double magV = sqrt(vX*vX + vY*vY);
    double aX = cx + (vX / magV) * r;
    double aY = cy + (vY / magV) * r;
    
    std::valarray<double> r_vec = {aX-cx,aY-cy};
    std::valarray<double> p_vec = {-r_vec[1], r_vec[0]};
    if(gtk->charge()>0){
      p_vec *= -1;
    }
    p_vec /= TMath::Sqrt(pow(p_vec[0],2)+pow(p_vec[1],2));
    p_vec *= gtk->pt();
    double phi = atan2(p_vec[1],p_vec[0]);
    return {dxy,phi};
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
  
  track_vec vertex_track_vec(const reco::Vertex & v, const double min_weight = 0.5) const {
    track_set s = vertex_track_set(v, min_weight);
    return track_vec(s.begin(), s.end());
  }


  std::pair<size_t, size_t> findTwoLargestIndices(const std::vector<double>& vec) {
    int firstIndex = -1, secondIndex = -1;
    float firstMax = -std::numeric_limits<float>::infinity();
    float secondMax = -std::numeric_limits<float>::infinity();

    for (size_t i = 0; i < vec.size(); ++i) {
      if (vec[i] > firstMax) {
	secondMax = firstMax;
	secondIndex = firstIndex;
	firstMax = vec[i];
	firstIndex = i;
      } else if (vec[i] > secondMax) {
	secondMax = vec[i];
	secondIndex = i;
      }
    }
    
    return {firstIndex, secondIndex};
  }

  void removeFlows(TH1F* h) {
    int nbins = h->GetNbinsX();
    double underflow = h->GetBinContent(0);
    double overflow = h->GetBinContent(nbins+1);
    h->AddBinContent(1,underflow);
    h->AddBinContent(nbins,overflow);
    h->SetBinContent(0,0);
    h->SetBinContent(nbins+1,0);
  }

bool matchesPF(int ID, double tolerance, Run3ScoutingMuon const& muonTrack,  edm::Handle<std::vector<Run3ScoutingParticle>> const& scoutingParticleH){

  bool matches = false;

  float mu_eta = muonTrack.eta();
  float mu_phi = muonTrack.phi();

  double dEta;
  double dPhi;
  double dR;

  for (size_t pf_index = 0; pf_index < scoutingParticleH->size(); pf_index++) {
    auto & scoutingPFCandidate = scoutingParticleH->at(pf_index);

    float pf_eta = scoutingPFCandidate.eta();
    float pf_phi = scoutingPFCandidate.phi();

    dEta = mu_eta - pf_eta;
    dPhi = deltaPhi(mu_phi, pf_phi);
    dR = sqrt(pow(dEta, 2) + pow(dPhi, 2));

    if(abs(scoutingPFCandidate.pdgId()) == 13 && dR < tolerance){
          matches = true;
      }
  }
  return matches;
}

};

K0TreeMakerRun3::K0TreeMakerRun3(const edm::ParameterSet& iConfig):
  required_ntk             (iConfig.getParameter<int>("required_ntk")),
  muonsToken               (consumes<std::vector<Run3ScoutingMuon> >             (iConfig.getParameter<edm::InputTag>("muons"))),
  electronsToken           (consumes<std::vector<Run3ScoutingElectron> >         (iConfig.getParameter<edm::InputTag>("electrons"))),
  primaryVerticesToken     (consumes<std::vector<reco::Vertex> >           (iConfig.getParameter<edm::InputTag>("primaryVertices"))),
  //verticesToken            (consumes<std::vector<Run3ScoutingVertex> >           (iConfig.getParameter<edm::InputTag>("displacedVertices"))),
  rhoToken                 (consumes<double>                                 (iConfig.getParameter<edm::InputTag>("rho"))), 
  photonsToken             (consumes<std::vector<Run3ScoutingPhoton> >         (iConfig.getParameter<edm::InputTag>("photons"))),
  pfjetsToken              (consumes<std::vector<reco::PFJet> >            (iConfig.getParameter<edm::InputTag>("pfjets"))),
  patjetsToken              (consumes<std::vector<pat::Jet> >            (iConfig.getParameter<edm::InputTag>("patjets"))),
  //tracksToken              (consumes<std::vector<Run3ScoutingTrack> >            (iConfig.getParameter<edm::InputTag>("tracks"))),
  tracksToken              (consumes<std::vector<reco::Track> >            (iConfig.getParameter<edm::InputTag>("tracks"))),
  tracksRefToken              (consumes<edm::ValueMap<edm::Ref<std::vector<Run3ScoutingTrack>>> >            (iConfig.getParameter<edm::InputTag>("trackRefs"))),
  verticesToken            (consumes<std::vector<reco::Vertex> >           (iConfig.getParameter<edm::InputTag>("displacedVertices"))),  
  recoTracksToken              (consumes<std::vector<reco::Track> >            (iConfig.getParameter<edm::InputTag>("recoTrack"))),
  truePileupToken(consumes<std::vector<PileupSummaryInfo>>(iConfig.getParameter<edm::InputTag>("truePileup"))),
  bsOnlineToken_(esConsumes<BeamSpotOnlineObjects, BeamSpotOnlineHLTObjectsRcd>()),
  beamspot_token(consumes<reco::BeamSpot>(iConfig.getParameter<edm::InputTag>("beamspot_src"))),
  GenParticleToken_(consumes(iConfig.getParameter<edm::InputTag>("genParticle_src"))),
  GenJetToken_(consumes(iConfig.getParameter<edm::InputTag>("genJet_src"))),
  GeneratorToken_(consumes(iConfig.getParameter<edm::InputTag>("generatorName"))),
  token_builder(esConsumes(edm::ESInputTag("", "TransientTrackBuilder"))),
  scoutingParticle_collection_token_(consumes(iConfig.getParameter<edm::InputTag>("scoutingParticle"))),
  isScouting                     (iConfig.existsAs<bool>("isScouting")               ?    iConfig.getParameter<bool>  ("isScouting")            : false),
  doPhiCorrection          (iConfig.existsAs<bool>("doPhiCorrection")    ?    iConfig.getParameter<bool>  ("doPhiCorrection") : false),
  doGenMatching       (iConfig.existsAs<bool>("doGenMatching")   ?    iConfig.getParameter<bool>  ("doGenMatching") : false),
  fillScoutTrack       (iConfig.existsAs<bool>("fillScoutTrack")   ?    iConfig.getParameter<bool>  ("fillScoutTrack") : false),
  luminosity          (iConfig.existsAs<double>("luminosity")    ?    iConfig.getParameter<double>  ("luminosity") : 1.0),
  crossSection        (iConfig.existsAs<double>("crossSection")    ?    iConfig.getParameter<double>  ("crossSection") : 1.0),
  PUCorrectionArray(iConfig.getParameter<std::vector<double>>("PUCorrectionArray")),
  isMC                    (iConfig.existsAs<bool>("isMC")               ?    iConfig.getParameter<bool>  ("isMC")            : false),
  weightsToken_(consumes<std::map<std::string, float>>(edm::InputTag("K0Filter", "weightMap")))
{
    usesResource("TFileService");
}

K0TreeMakerRun3::~K0TreeMakerRun3() {
  // do anything here that needs to be done at desctruction time
  // (e.g. close files, deallocate resources etc.)
  //
  // please remove this method altogether if it would be left empty
}

//
// member functions
//


// ------------ method called for each event  ------------
void K0TreeMakerRun3::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;
  using namespace std;
  using namespace reco;
  using correction::CorrectionSet;
  
  scoutTrack_pt->clear();
  scoutTrack_eta->clear();
  scoutTrack_phi->clear();
  scoutTrack_phiBeamspot->clear();
  scoutTrack_reducedChi2->clear();
  scoutTrack_charge->clear();
  scoutTrack_dxy->clear();
  scoutTrack_dxyErr->clear();
  scoutTrack_dxySig->clear();
  scoutTrack_dxySigned->clear();
  scoutTrack_d3D->clear();
  scoutTrack_d3DErr->clear();
  scoutTrack_d3DSig->clear();
  scoutTrack_dz->clear();
  scoutTrack_dzErr->clear();
  scoutTrack_dzSig->clear();
  scoutTrack_dszUncertainty->clear();
  scoutTrack_dxyUncertainty->clear();
  scoutTrack_dszdxyCovariance->clear();
  scoutTrack_vx->clear();
  scoutTrack_vy->clear();
  scoutTrack_iJet->clear();
  scoutTrack_nValidPixelHits->clear();
  scoutTrack_nTrackerLayersWithMeasurement->clear();
  scoutTrack_nValidStripHits->clear();
  scoutTrack_nMissingInnerHits->clear();
  scoutTrack_minPVDxy->clear();
  scoutTrack_minPVDz->clear();

  vertTrack_pt->clear();
  vertTrack_eta->clear();
  vertTrack_phi->clear();
  vertTrack_reducedChi2->clear();
  vertTrack_charge->clear();
  vertTrack_dxy->clear();
  vertTrack_dxyErr->clear();
  vertTrack_dxySig->clear();
  vertTrack_dxySigned->clear();
  vertTrack_d3D->clear();
  vertTrack_d3DErr->clear();
  vertTrack_d3DSig->clear();
  vertTrack_dz->clear();
  vertTrack_dzErr->clear();
  vertTrack_dzSig->clear();
  vertTrack_nValidPixelHits->clear();
  vertTrack_nTrackerLayersWithMeasurement->clear();
  vertTrack_nValidStripHits->clear();
  vertTrack_nMissingInnerHits->clear();
  vertTrack_iVtx->clear();
  vertTrack_iJet->clear();
  vertTrack_hasPFMatch->clear();

  reco_dpt_diff->clear();
  reco_deta_diff->clear();
  reco_dphi_diff->clear();
  reco_dxy_diff->clear();
  reco_dchi2_diff->clear();
  
  match_deltaR->clear();
  match_ptRatio->clear();
  match_diffPt->clear();
  match_diffEta->clear();
  match_diffPhi->clear();
  match_diffPhiCorrected->clear();
  match_gen_dxy->clear();
  match_gen_dxyCorrected->clear();
  match_diffDxy->clear();
  match_diffDxyCorrected->clear();
  gen_dxy->clear();
  gen_dxyCorrected->clear();
  match_vert_x->clear();
  match_vert_y->clear();
  match_genVert_x->clear();
  match_genVert_y->clear();
  match_genVert_dBV->clear();
  genVert_dBV->clear();
  genVert_phi->clear();
  genVert_z->clear();
  genVert_x->clear();
  genVert_y->clear();
  genVert_nParticles->clear();
  genVert_dPhi->clear();
  genVert_dVV->clear();
  resVert_x->clear();
  resVert_y->clear();
  resVert_z->clear();
  scoutVert_dBV->clear();
  scoutVert_dPVV->clear();
  scoutVert_dBVErr->clear();
  scoutVert_dPVVErr->clear();
  scoutVert_phi->clear();
  scoutVert_z->clear();
  scoutVert_x->clear();
  scoutVert_y->clear();
  scoutVert_nTracks->clear();
  scoutVert_chi2->clear();
  scoutVert_dPhi->clear();
  scoutVert_dVV->clear();
  scoutVert_dT->clear();
  scoutVert_cosT->clear();
  scoutVert_pMag->clear();
  scoutVert_costh2->clear();
  scoutVert_ctau->clear();
  scoutVert_pt->clear();
  scoutVert_mass->clear();
  
  jet_pt->clear();
  jet_eta->clear();
  jet_phi->clear();
  jet_mass->clear();
  jet_energy->clear();
  jet_chHEF->clear();
  jet_neHEF->clear();
  jet_muonEF->clear();
  jet_chEmEF->clear();
  jet_neEmEF->clear();
  jet_hfHEF->clear();
  jet_hfEmEF->clear();
  jet_hoEF->clear();
  jet_chMultiplicity->clear();
  jet_neMultiplicity->clear();
  jet_passJetIdTight->clear();

  genJet_pt->clear();
  genJet_eta->clear();
  genJet_phi->clear();
  genJet_mass->clear();
  genJet_energy->clear();
  genJet_nConstituents->clear();

  muon_pt->clear();
  muon_eta->clear();
  muon_phi->clear();
  muon_chi2->clear();
  muon_nTrackerLayersWithMeasurement->clear();
  muon_nValidPixelHits->clear();
  muon_nValidRecoMuonHits->clear();
  muon_nRecoMuonMatchedStations->clear();
  muon_trackIso->clear();
  
  eventId = iEvent.id().event();
  runNumber = iEvent.id().run();
  lumiBlock = iEvent.luminosityBlock();

  double genWeight = 1;
  double theWeight = 1;

  edm::Handle<std::map<std::string, float>> weightMap;
  iEvent.getByToken(weightsToken_, weightMap);
  
  if(isMC){
    edm::Handle<GenEventInfoProduct> generatorHandle;
    iEvent.getByToken(GeneratorToken_, generatorHandle);
    genWeight = generatorHandle->weight();
    h_genWeights->Fill("None",genWeight);
    theWeight = genWeight*luminosity*crossSection;
    uncorrectedWeight = theWeight;
    
    edm::Handle<std::vector<PileupSummaryInfo>> pileup;
    iEvent.getByToken(truePileupToken, pileup);
    std::vector<PileupSummaryInfo>::const_iterator pileupIter;
    for(pileupIter = pileup->begin(); pileupIter != pileup->end(); ++pileupIter){
      if (pileupIter->getBunchCrossing() == 0) {
	truePU = pileupIter->getTrueNumInteractions();
      }
    }

    weight_PU_BCDEFGHI_nominal = weightMap->at("PU_BCDEFGHI_nominal");
    weight_PU_BCDEFGHI_up = weightMap->at("PU_BCDEFGHI_up");
    weight_PU_BCDEFGHI_down = weightMap->at("PU_BCDEFGHI_down");
    weight_PU_C_nominal = weightMap->at("PU_C_nominal");
    weight_PU_C_up = weightMap->at("PU_C_up");
    weight_PU_C_down = weightMap->at("PU_C_down");
    weight_PU_D_nominal = weightMap->at("PU_D_nominal");
    weight_PU_D_up = weightMap->at("PU_D_up");
    weight_PU_D_down = weightMap->at("PU_D_down");
    weight_PU_E_nominal = weightMap->at("PU_E_nominal");
    weight_PU_E_up = weightMap->at("PU_E_up");
    weight_PU_E_down = weightMap->at("PU_E_down");
    weight_PU_F_nominal = weightMap->at("PU_F_nominal");
    weight_PU_F_up = weightMap->at("PU_F_up");
    weight_PU_F_down = weightMap->at("PU_F_down");
    weight_PU_G_nominal = weightMap->at("PU_G_nominal");
    weight_PU_G_up = weightMap->at("PU_G_up");
    weight_PU_G_down = weightMap->at("PU_G_down");
    weight_PU_H_nominal = weightMap->at("PU_H_nominal");
    weight_PU_H_up = weightMap->at("PU_H_up");
    weight_PU_H_down = weightMap->at("PU_H_down");
    weight_PU_I_nominal = weightMap->at("PU_I_nominal");
    weight_PU_I_up = weightMap->at("PU_I_up");
    weight_PU_I_down = weightMap->at("PU_I_down");
    
    if(truePU>99) truePU = 99;
    theWeight *= PUCorrectionArray[truePU];
    
    h_weights->Fill("None",theWeight);
    h_weightsSquared->Fill("None",pow(theWeight,2));

    h_weights_LUMCorrected->Fill("None",weightMap->at("correctedNominal"));
    h_weightsSquared_LUMCorrected->Fill("None",pow(weightMap->at("correctedNominal"),2));
  }
  else {
    genWeight = 1;
    theWeight = 1;
    uncorrectedWeight = 1;
    h_genWeights->Fill("None",genWeight);
    h_weights->Fill("None",theWeight);
    h_weightsSquared->Fill("None",pow(theWeight,2));
  }
  weight = theWeight;
  //Pileup info -- only for MC

  observedPU = -1;
  truePU = -1;

  if(isMC){
    edm::Handle<std::vector<PileupSummaryInfo>> pileup;
    iEvent.getByToken(truePileupToken, pileup);

    std::vector<PileupSummaryInfo>::const_iterator pileupIter;
    for(pileupIter = pileup->begin(); pileupIter != pileup->end(); ++pileupIter){
      if (pileupIter->getBunchCrossing() == 0) {
	observedPU = pileupIter->getPU_NumInteractions();
	truePU = pileupIter->getTrueNumInteractions();
      }
    }
    
  }

  const auto& bs = iSetup.getData(bsOnlineToken_);
  reco::BeamSpot::CovarianceMatrix onlineCovariance;
  for(uint i=0; i<7; i++){
    for(uint j=i; j<7; j++){
      onlineCovariance(i,j) = bs.covariance(i,j);
    }
  }
  reco::BeamSpot::Point onlinePosition(bs.x(), bs.y(), bs.z());
  reco::BeamSpot* beamspot = new BeamSpot(onlinePosition,
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
  
  //Get the offline beamspot
  edm::Handle<reco::BeamSpot> offlineBeamspot; 
  iEvent.getByToken(beamspot_token, offlineBeamspot); 
  offlineBeamspot_x = offlineBeamspot->x0();
  offlineBeamspot_xErr = offlineBeamspot->x0Error();
  offlineBeamspot_y = offlineBeamspot->y0();
  offlineBeamspot_yErr = offlineBeamspot->y0Error();
  offlineBeamspot_z = offlineBeamspot->z0();
  offlineBeamspot_zErr = offlineBeamspot->z0Error();

  const reco::Vertex fake_bs_vtx(beamspot->position(), beamspot->covariance3D());
  beamspot_x = beamspot->x0();
  beamspot_xErr = beamspot->x0Error();
  beamspot_y = beamspot->y0();
  beamspot_yErr = beamspot->y0Error();
  beamspot_z = beamspot->z0();
  beamspot_zErr = beamspot->z0Error();
  beamspot_xWidth = beamspot->BeamWidthX();
  beamspot_yWidth = beamspot->BeamWidthY();
  beamspot_widthErr = beamspot->BeamWidthXError();
  beamspot_type = beamspot->type();
  //std::cout<<"beamspot: "<<beamspot->position()<<std::endl;
  //Get the primary vertices
  edm::Handle<std::vector<reco::Vertex>> primaryVertices;
  iEvent.getByToken(primaryVerticesToken, primaryVertices);
  std::vector<reco::Vertex>::const_iterator primaryVertexIter;
  nPV = primaryVertices->size();
  
  edm::Handle<std::vector<reco::Track>> ScoutingTrackHandle;
  //edm::Handle<std::vector<Run3ScoutingTrack>> ScoutingTrackHandle;
  iEvent.getByToken(tracksToken, ScoutingTrackHandle);

  edm::Handle<edm::ValueMap<edm::Ref<std::vector<Run3ScoutingTrack>>>> ScoutingTrackRefHandle;
  if(isScouting) iEvent.getByToken(tracksRefToken, ScoutingTrackRefHandle);
  
  auto const &tt_builder = iSetup.getData(token_builder);
  std::vector<reco::Track>::const_iterator scoutingTrackIter;
  //std::vector<Run3ScoutingTrack>::const_iterator scoutingTrackIter;

  nGenJets = 0;
  genHT = 0;
  //Get gen jets
  std::vector<reco::GenJet>::const_iterator genJetIter;
  edm::Handle<std::vector<reco::GenJet>> genJet_handle;
  if(isMC){
    iEvent.getByToken(GenJetToken_,genJet_handle);
    for(genJetIter = genJet_handle->begin(); genJetIter != genJet_handle->end(); ++genJetIter){
      genJet_pt->push_back(genJetIter->pt());
      genJet_eta->push_back(genJetIter->eta());
      genJet_phi->push_back(genJetIter->phi());
      genJet_mass->push_back(genJetIter->mass());
      float energy = TMath::Sqrt(pow(TMath::CosH(genJetIter->eta())*genJetIter->pt(),2)+pow(genJetIter->mass(),2));
      genJet_energy->push_back(energy);
      genJet_nConstituents->push_back(genJetIter->nConstituents());
      nGenJets++;
      genHT += genJetIter->pt();
    }
  }
  
  //Get the jets
  Handle<vector<reco::PFJet> > pfjetsH;
  iEvent.getByToken(pfjetsToken, pfjetsH);
  std::vector<reco::PFJet> pfJetVector;
  
  //Require 4 PF Jets
  if(pfjetsH.isValid() && isScouting){
    for (auto jets_iter = pfjetsH->begin(); jets_iter != pfjetsH->end(); ++jets_iter) {
      pfJetVector.push_back(*jets_iter);      
    }
    h_genWeights->Fill("nJets",genWeight);
    h_weights->Fill("nJets",theWeight);
    h_weightsSquared->Fill("nJets",pow(theWeight,2));

    if(isMC){
      h_weights_LUMCorrected->Fill("nJets",weightMap->at("correctedNominal"));
      h_weightsSquared_LUMCorrected->Fill("nJets",pow(weightMap->at("correctedNominal"),2));
    }
  
    HT = 0;
    int t = 0;
    for (auto jet: pfJetVector) {
      jet_pt->push_back(jet.pt());
      float Jet_eta = jet.eta();
      jet_eta->push_back(Jet_eta);
      jet_phi->push_back(jet.phi());
      jet_mass->push_back(jet.mass());
      float energy = TMath::Sqrt(pow(TMath::CosH(jet.eta())*jet.pt(),2)+pow(jet.mass(),2));
      jet_energy->push_back(energy);
      float Jet_chHEF = jet.chargedHadronEnergy()/energy;
      jet_chHEF->push_back(Jet_chHEF);
      float Jet_neHEF = jet.neutralHadronEnergy()/energy;
      jet_neHEF->push_back(Jet_neHEF);
      jet_muonEF->push_back(jet.muonEnergy()/energy);
      jet_chEmEF->push_back(jet.electronEnergy()/energy);
      float Jet_neEmEF = (jet.photonEnergy()+jet.HFEMEnergy())/energy;
      jet_neEmEF->push_back(Jet_neEmEF);
      jet_hfHEF->push_back(jet.HFHadronEnergy()/energy);
      jet_hfEmEF->push_back(jet.HFEMEnergy()/energy);
      jet_hoEF->push_back(jet.hoEnergy()/energy);
      int Jet_chMultiplicity = jet.chargedHadronMultiplicity()+jet.electronMultiplicity()+jet.muonMultiplicity();
      jet_chMultiplicity->push_back(Jet_chMultiplicity);
      int Jet_neMultiplicity = jet.neutralHadronMultiplicity()+jet.photonMultiplicity()+jet.HFHadronMultiplicity()+jet.HFEMMultiplicity();
      jet_neMultiplicity->push_back(Jet_neMultiplicity);
      bool Jet_passJetIdTight = false;
      if (abs(Jet_eta) <= 2.6) 
	      Jet_passJetIdTight = (Jet_neHEF < 0.99) && (Jet_neEmEF < 0.9) && (Jet_chMultiplicity+Jet_neMultiplicity > 1) && (Jet_chHEF > 0.01) && (Jet_chMultiplicity > 0);
      else if (abs(Jet_eta) > 2.6 && abs(Jet_eta) <= 2.7)
	      Jet_passJetIdTight = (Jet_neHEF < 0.90) && (Jet_neEmEF < 0.99);
      else if (abs(Jet_eta) > 2.7 && abs(Jet_eta) <= 3.0)
	      Jet_passJetIdTight = (Jet_neHEF < 0.99);
      else if (abs(Jet_eta) > 3.0)
	      Jet_passJetIdTight = (Jet_neMultiplicity >= 2) && (Jet_neEmEF < 0.4);
      jet_passJetIdTight->push_back(Jet_passJetIdTight);
      HT = HT + jet.pt();
      t++;
    }
  }

  // Get same HT as in Trigger Effs
  Handle<std::vector<Run3ScoutingMuon> > muonsH;
  iEvent.getByToken(muonsToken, muonsH);

  //Get scouting particle flow candidates
  Handle<Run3ScoutingParticleCollection> scoutingParticle_collection_handle;
  iEvent.getByToken(scoutingParticle_collection_token_, scoutingParticle_collection_handle);

  std::vector<const Run3ScoutingMuon*> selectedMuons;

  bool isPFMuon;

  for (auto muons_iter = muonsH->begin(); muons_iter != muonsH->end(); ++muons_iter) {
    muon_pt->push_back(muons_iter->pt());
    muon_eta->push_back(muons_iter->eta());
    muon_phi->push_back(muons_iter->phi());
    muon_chi2->push_back(muons_iter->normalizedChi2());
    muon_nTrackerLayersWithMeasurement->push_back(muons_iter->nTrackerLayersWithMeasurement());
    muon_nValidPixelHits->push_back(muons_iter->nValidPixelHits());
    muon_nValidRecoMuonHits->push_back(muons_iter->nValidRecoMuonHits());
    muon_nRecoMuonMatchedStations->push_back(muons_iter->nRecoMuonMatchedStations());
    muon_trackIso->push_back(muons_iter->trackIso());
    selectedMuons.push_back(&(*muons_iter));    
  }

  float dEta_jet_mu;
  float dPhi_jet_mu;
  float dR_jet_mu;

  ht_corrected = 0;
  int imuon = 0;

  for (auto jet: pfJetVector) {
    if((jet.pt() > 30) && (abs(jet.eta()) < 2.4)){    
      for (auto muon : selectedMuons) {
        dEta_jet_mu = jet.eta() - muon->eta();
        dPhi_jet_mu = deltaPhi(jet.phi(), muon->phi());
        dR_jet_mu = sqrt(pow(dEta_jet_mu, 2) + pow(dPhi_jet_mu, 2));
                
          if(dR_jet_mu >= 0.20)
            ht_corrected = ht_corrected + jet.pt();
        
        imuon++;
      }
      if(imuon == 0) //in case there are no muons, ofc the jet is isolated
        ht_corrected = ht_corrected + jet.pt();
    }
  }

  // end HT calculation

  //std::cout<<"ht: "<<ht_corrected<<std::endl;
  //std::cout<<"weight_nominal: "<<weight_trigger_nominal<<std::endl;
  //std::cout<<"weight_up: "<<weight_trigger_up<<std::endl;
  //std::cout<<"weight_down: "<<weight_trigger_down<<std::endl;

  //Get the pat jets, only for MC
  Handle<vector<pat::Jet> > patjetsH;
  if(isMC) iEvent.getByToken(patjetsToken, patjetsH);
  std::vector<pat::Jet> patJetVector;
  
  //Require 4 Pat Jets
  if(isMC && patjetsH.isValid() && !isScouting){
    for (auto jets_iter = patjetsH->begin(); jets_iter != patjetsH->end(); ++jets_iter) {
      patJetVector.push_back(*jets_iter);
    }

    h_genWeights->Fill("nJets",genWeight);
    h_weights->Fill("nJets",theWeight);
    h_weightsSquared->Fill("nJets",pow(theWeight,2));

    if(isMC){
      h_weights_LUMCorrected->Fill("nJets",weightMap->at("correctedNominal"));
      h_weightsSquared_LUMCorrected->Fill("nJets",pow(weightMap->at("correctedNominal"),2));
    }
    
    HT = 0;
    int t = 0;
    for (auto jet: patJetVector) {
      jet_pt->push_back(jet.pt());
      jet_eta->push_back(jet.eta());
      jet_phi->push_back(jet.phi());
      jet_mass->push_back(jet.mass());
      HT = HT + jet.pt();
      t++;
    }
  }

  uint i_tk = 0;
  if(fillScoutTrack){
    for(scoutingTrackIter = ScoutingTrackHandle->begin(); scoutingTrackIter != ScoutingTrackHandle->end(); ++scoutingTrackIter){
      scoutTrack_pt->push_back(scoutingTrackIter->pt());
      scoutTrack_eta->push_back(scoutingTrackIter->eta());
      scoutTrack_phi->push_back(scoutingTrackIter->phi());
      scoutTrack_phiBeamspot->push_back(atan2(scoutingTrackIter->py()-beamspot->y0(),scoutingTrackIter->px()-beamspot->x0()));
      //std::cout<<"track phi: "<<scoutingTrackIter->phi()<<std::endl;
      //std::cout<<"recalc origin phi: "<<atan2(scoutingTrackIter->py(),scoutingTrackIter->px())<<std::endl;
      //std::cout<<"recalc beamspot phi: "<<atan2(scoutingTrackIter->py()-beamspot->y0(),scoutingTrackIter->px()-beamspot->x0())<<std::endl;
      scoutTrack_reducedChi2->push_back(scoutingTrackIter->chi2()/scoutingTrackIter->ndof());
      scoutTrack_charge->push_back(scoutingTrackIter->charge());
      reco::TransientTrack transientScoutTrack = tt_builder.build(*scoutingTrackIter);
      std::pair<bool, Measurement1D> ttk_transverseDist = IPTools::absoluteTransverseImpactParameter(transientScoutTrack, fake_bs_vtx);
      std::pair<bool, Measurement1D> ttk_3DDist = IPTools::absoluteImpactParameter3D(transientScoutTrack, fake_bs_vtx);
      scoutTrack_dxy->push_back(ttk_transverseDist.second.value());
      scoutTrack_dxyErr->push_back(ttk_transverseDist.second.error());
      scoutTrack_dxySig->push_back(ttk_transverseDist.second.significance());
      GlobalVector dir(scoutingTrackIter->px(), scoutingTrackIter->py(), scoutingTrackIter->pz());
      std::pair<bool, Measurement1D> ttk_transverseDistSigned = IPTools::signedTransverseImpactParameter(transientScoutTrack, dir, fake_bs_vtx);
      scoutTrack_dxySigned->push_back(ttk_transverseDistSigned.second.value());
      scoutTrack_d3D->push_back(ttk_3DDist.second.value());
      scoutTrack_d3DErr->push_back(ttk_3DDist.second.error());
      scoutTrack_d3DSig->push_back(ttk_3DDist.second.significance());
      //Note: This is a linear approximation that breaks down in reference point of track is far from beamspot. Significance doesn't consider beamspot error in z.
      float dz = scoutingTrackIter->dz(beamspot->position());
      scoutTrack_dz->push_back(dz);
      scoutTrack_dzErr->push_back(scoutingTrackIter->dzError());
      scoutTrack_dzSig->push_back(dz/scoutingTrackIter->dzError());
      scoutTrack_dszUncertainty->push_back(scoutingTrackIter->dszError());
      scoutTrack_dxyUncertainty->push_back(scoutingTrackIter->dxyError());
      scoutTrack_dszdxyCovariance->push_back(scoutingTrackIter->covariance(3,4));
      scoutTrack_vx->push_back(scoutingTrackIter->vx());
      scoutTrack_vy->push_back(scoutingTrackIter->vy());

      int i_jet = 0;
      int i_bestMatch = -1;
      float bestDeltaR = 9999999;
      for (auto jet: pfJetVector) {
	float deltaR = reco::deltaR(scoutingTrackIter->eta(),scoutingTrackIter->phi(),jet.eta(),jet.phi());
	if((deltaR<bestDeltaR) && (deltaR<0.4)){
	  i_bestMatch = i_jet;
	  bestDeltaR = deltaR;
	}
	i_jet++;
      }
      scoutTrack_iJet->push_back(i_bestMatch);
      
      
      edm::Ref<std::vector<reco::Track>> trackRef(ScoutingTrackHandle, i_tk);
      if(isScouting){
	auto scoutTrack = (*ScoutingTrackRefHandle)[trackRef];
	scoutTrack_nValidPixelHits->push_back(scoutTrack->tk_nValidPixelHits());
	scoutTrack_nTrackerLayersWithMeasurement->push_back(scoutTrack->tk_nTrackerLayersWithMeasurement());
	scoutTrack_nValidStripHits->push_back(scoutTrack->tk_nValidStripHits());
      }
      else{
	scoutTrack_nValidPixelHits->push_back(scoutingTrackIter->hitPattern().numberOfValidPixelHits());
	scoutTrack_nTrackerLayersWithMeasurement->push_back(scoutingTrackIter->hitPattern().trackerLayersWithMeasurement());
	scoutTrack_nValidStripHits->push_back(scoutingTrackIter->hitPattern().numberOfValidStripHits());
      }
      //scoutTrack_nMissingInnerHits->push_back(scoutingTrackIter->missingInnerHits());
    
      float minPVDxy = 999999;
      float minPVDz = 999999;
      /*
      for(primaryVertexIter = primaryVertices->begin(); primaryVertexIter != primaryVertices->end(); ++primaryVertexIter){
	ttk_transverseDist = IPTools::absoluteTransverseImpactParameter(transientScoutTrack, *primaryVertexIter);
	if(ttk_transverseDist.second.value()<minPVDxy) minPVDxy = ttk_transverseDist.second.value();
	dz = scoutingTrackIter->dz(primaryVertexIter->position());
	if(fabs(dz)<fabs(minPVDz)) minPVDz = dz;
      }
      scoutTrack_minPVDxy->push_back(minPVDxy);
      scoutTrack_minPVDz->push_back(minPVDz);
      */
      i_tk++;
    }
  }
  
  //Get the vertices
  Handle<vector<Vertex> > verticesH;
  iEvent.getByToken(verticesToken, verticesH);
  
  int t=0;
  Vertex v;
  int ntk_t=0;
  vector<TrackRef> tks_t;
  vector<Vertex> vertices_ntk;
  
  if(verticesH.isValid()){
    for (auto vertex_iter = verticesH->begin(); vertex_iter != verticesH->end(); ++vertex_iter) {
      v = verticesH->at(t);
      tks_t = vertex_track_vec(v);
      ntk_t = tks_t.size();
      if (ntk_t > required_ntk - 1) vertices_ntk.push_back(v);
      t++;
    }
  
    nVertices = vertices_ntk.size();

    if (nVertices<1) return;
    
    h_genWeights->Fill("nVertices",genWeight);
    h_weights->Fill("nVertices",theWeight);
    h_weightsSquared->Fill("nVertices",pow(theWeight,2));

    if(isMC){
      h_weights_LUMCorrected->Fill("nVertices",weightMap->at("correctedNominal"));
      h_weightsSquared_LUMCorrected->Fill("nVertices",pow(weightMap->at("correctedNominal"),2));
    }
    
    h_scoutVert_nVertices->Fill(vertices_ntk.size());
    scoutVert_nVertices = vertices_ntk.size();

    t=0;
    for (auto vertex_iter = vertices_ntk.begin(); vertex_iter != vertices_ntk.end(); ++vertex_iter) {
      v = vertices_ntk.at(t);
      tks_t = vertex_track_vec(v);
      for(auto vertTrack: tks_t){
	vertTrack_pt->push_back(vertTrack->pt());
	vertTrack_eta->push_back(vertTrack->eta());
	vertTrack_phi->push_back(vertTrack->phi());
	vertTrack_reducedChi2->push_back(vertTrack->chi2()/vertTrack->ndof());
	vertTrack_charge->push_back(vertTrack->charge());
	reco::TransientTrack transientTrack = tt_builder.build(vertTrack);
	std::pair<bool, Measurement1D> ttransverseDist = IPTools::absoluteTransverseImpactParameter(transientTrack, fake_bs_vtx);
	std::pair<bool, Measurement1D> t3DDist = IPTools::absoluteImpactParameter3D(transientTrack, fake_bs_vtx);
	vertTrack_dxy->push_back(ttransverseDist.second.value());
	vertTrack_dxyErr->push_back(ttransverseDist.second.error());
	vertTrack_dxySig->push_back(ttransverseDist.second.significance());
	GlobalVector dir(vertTrack->px(), vertTrack->py(), vertTrack->pz());
	std::pair<bool, Measurement1D> ttk_transverseDistSigned = IPTools::signedTransverseImpactParameter(transientTrack, dir, fake_bs_vtx);
	vertTrack_dxySigned->push_back(ttk_transverseDistSigned.second.value());
	vertTrack_d3D->push_back(t3DDist.second.value());
	vertTrack_d3DErr->push_back(t3DDist.second.error());
	vertTrack_d3DSig->push_back(t3DDist.second.significance());
	//Note: This is a linear approximation that breaks down in reference point of track is far from beamspot. Significance doesn't consider beamspot error in z.
	float dz = vertTrack->dz(beamspot->position());
	vertTrack_dz->push_back(dz);
	vertTrack_dzErr->push_back(vertTrack->dzError());
	vertTrack_dzSig->push_back(dz/vertTrack->dzError());
	vertTrack_iVtx->push_back(t);
	if(isScouting){
	  auto scoutTrack = (*ScoutingTrackRefHandle)[vertTrack];
	  vertTrack_nValidPixelHits->push_back(scoutTrack->tk_nValidPixelHits());
	  vertTrack_nTrackerLayersWithMeasurement->push_back(scoutTrack->tk_nTrackerLayersWithMeasurement());
	  vertTrack_nValidStripHits->push_back(scoutTrack->tk_nValidStripHits());
	  int match_index = findCompatibleScoutingTrack(scoutingParticle_collection_handle, scoutTrack);
	  vertTrack_hasPFMatch->push_back(match_index!=-1);
	  
	  int i_jet = 0;
	  int i_bestMatch = -1;
	  float bestDeltaR = 9999999;
	  for (auto jet: pfJetVector) {
	    float deltaR = reco::deltaR(vertTrack->eta(),vertTrack->phi(),jet.eta(),jet.phi());
	    if((deltaR<bestDeltaR) && (deltaR<0.4)){
	      i_bestMatch = i_jet;
	      bestDeltaR = deltaR;
	    }
	    i_jet++;
	  }
	  vertTrack_iJet->push_back(i_bestMatch);
	}
	else{
	  vertTrack_nValidPixelHits->push_back(vertTrack->hitPattern().numberOfValidPixelHits());
	  vertTrack_nTrackerLayersWithMeasurement->push_back(vertTrack->hitPattern().trackerLayersWithMeasurement());
	  vertTrack_nValidStripHits->push_back(vertTrack->hitPattern().numberOfValidStripHits());
	}
	vertTrack_nMissingInnerHits->push_back(vertTrack->missingInnerHits());
      }
      t++;
    }
  }

  std::vector<reco::GenParticle>::const_iterator genParticleIter;
  edm::Handle<std::vector<reco::GenParticle>> genParticle_handle;
  std::vector<GlobalPoint> genVertices;
  
  if(isMC && doGenMatching){
    //Get gen particles for truth-level vertices
    iEvent.getByToken(GenParticleToken_,genParticle_handle);
    
    float maxDist = 0;
    for(genParticleIter = genParticle_handle->begin(); genParticleIter != genParticle_handle->end(); ++genParticleIter){
      if(genParticleIter->numberOfMothers()<1) continue;
      if(isStopDecay(genParticleIter->mother(0)).first){
	//std::cout<<"isStop block"<<std::endl;
	//std::cout<<"pdgid: "<<genParticleIter->pdgId()<<" vertex xyz: "<<genParticleIter->vx()<<" "<<genParticleIter->vy()<<" "<<genParticleIter->vz()<<" status: "<<genParticleIter->status()<<" parent id: "<<genParticleIter->mother(0)->pdgId()<<" parent vertex: "<<genParticleIter->mother(0)->vx()<<" "<<genParticleIter->mother(0)->vy()<<" "<<genParticleIter->mother(0)->vz()<<" parent status: "<<genParticleIter->mother(0)->status()<<std::endl;
	float dist = TMath::Sqrt(pow(genParticleIter->vx()-beamspot->x0(),2)+pow(genParticleIter->vy()-beamspot->y0(),2));
	const reco::Candidate* mother = genParticleIter->mother(0);
	while(mother->mother(0)->pdgId()==mother->pdgId()){
	  mother = mother->mother(0);
	}
      
	bool isDupe = false;
	GlobalPoint genVertex = GlobalPoint(genParticleIter->vx(),genParticleIter->vy(),genParticleIter->vz());
	for(auto vertex: genVertices){
	  if((vertex.x()==genVertex.x()) && (vertex.y()==genVertex.y()) && (vertex.z()==genVertex.z())) isDupe = true;
	}
	if(!isDupe){
	  genVertices.push_back(genVertex);
	  h_genVert_dBV->Fill(dist);
	  genVert_dBV->push_back(dist);
	  h_genVert_phi->Fill(atan2(genVertex.y()-beamspot->y0(),genVertex.x()-beamspot->x0()));
	  genVert_phi->push_back(atan2(genVertex.y()-beamspot->y0(),genVertex.x()-beamspot->x0()));
	  h_genVert_z->Fill(genVertex.z()-beamspot->z0());
	  genVert_z->push_back(genVertex.z()-beamspot->z0());
	  h_genVert_x_y->Fill(genVertex.x()-beamspot->x0(),genVertex.y()-beamspot->y0());
	  genVert_x->push_back(genVertex.x()-beamspot->x0());
	  genVert_y->push_back(genVertex.y()-beamspot->y0());
	}
	//std::cout<<"first mother id: "<<mother->pdgId()<<" status: "<<mother->status()<<" vertex: "<<mother->vx()<<" "<<mother->vy()<<" "<<mother->vz()<<" parent id: "<<mother->mother(0)->pdgId()<<" parent status: "<<mother->mother(0)->status()<<" mother vertex: "<<mother->mother(0)->vx()<<" "<<mother->mother(0)->vy()<<" "<<mother->mother(0)->vz()<<std::endl;
	if(dist>maxDist){
	  maxDist = dist;
	  genVert_x_1 = genParticleIter->vx()-beamspot->x0();
	  genVert_y_1 = genParticleIter->vy()-beamspot->y0();
	  genVert_z_1 = genParticleIter->vz()-beamspot->z0();
	  genVert_dBV_1 = dist;
	  genVert_3d_1 = TMath::Sqrt(pow(genParticleIter->vx()-beamspot->x0(),2)+pow(genParticleIter->vy()-beamspot->y0(),2)+pow(genParticleIter->vz()-beamspot->z0(),2));
	  genVert_motherEta = mother->eta();
	  genVert_motherPhi = mother->phi();
	  genVert_motherPt = mother->pt();
	  genVert_motherDistTraveled = TMath::Sqrt(pow(genParticleIter->vx()-mother->mother(0)->vx(),2)+pow(genParticleIter->vy()-mother->mother(0)->vy(),2)+pow(genParticleIter->vz()-mother->mother(0)->vz(),2));
	}
      } //isStopDecay
      std::pair<bool,GlobalPoint> isChargedStopDecayProduct = isChargedStopDecayProductStatusOne(genParticleIter);
      if(isChargedStopDecayProduct.first){
	//std::cout<<"pdgid: "<<genParticleIter->pdgId()<<" vertex xyz: "<<genParticleIter->vx()<<" "<<genParticleIter->vy()<<" "<<genParticleIter->vz()<<" status: "<<genParticleIter->status()<<" parent id: "<<genParticleIter->mother(0)->pdgId()<<" parent vertex: "<<genParticleIter->mother(0)->vx()<<" "<<genParticleIter->mother(0)->vy()<<" "<<genParticleIter->mother(0)->vz()<<" parent status: "<<genParticleIter->mother(0)->status()<<std::endl;
	
	float dxy = TMath::Sqrt(pow(genParticleIter->vx()-beamspot->x0(),2)+pow(genParticleIter->vy()-beamspot->y0(),2));
	h_gen_dxy->Fill(dxy);
	gen_dxy->push_back(dxy);
	std::pair<double,double> correction = gen_dxy_correction(genParticleIter,beamspot);
	float dxy_corrected = correction.first;
	gen_dxyCorrected->push_back(dxy_corrected);
      }
    } //loop over gen particles

    h_genVert_nVertices->Fill(genVertices.size());
    genVert_nVertices = genVertices.size();
    //count number of gen particles from same vertex
    std::vector<int> nMatches(genVertices.size(),0);
    for(genParticleIter = genParticle_handle->begin(); genParticleIter != genParticle_handle->end(); ++genParticleIter){
      std::pair<bool,GlobalPoint> isChargedStopDecayProduct = isChargedStopDecayProductStatusOne(genParticleIter);
      if(!isChargedStopDecayProduct.first) continue;
      uint i = -1;
      for(auto vertex: genVertices){
	i++;
	if((vertex.x()==isChargedStopDecayProduct.second.x()) && (vertex.y()==isChargedStopDecayProduct.second.y()) && (vertex.z()==isChargedStopDecayProduct.second.z())) nMatches[i]++;
      }
    }
    for(uint i=0; i<nMatches.size(); i++){
      h_genVert_nParticles->Fill(nMatches[i]);
      genVert_nParticles->push_back(nMatches[i]);
    }

    if(genVertices.size()==2){
      genVert_dVV_2 = TMath::Sqrt(pow(genVertices[0].x()-genVertices[1].x(),2)+pow(genVertices[0].y()-genVertices[1].y(),2)+pow(genVertices[0].z()-genVertices[1].z(),2));
      float dPhi = fabs(atan2(genVertices[0].y()-beamspot->y0(),genVertices[0].x()-beamspot->x0())-atan2(genVertices[1].y()-beamspot->y0(),genVertices[1].x()-beamspot->x0()));
      if(dPhi>TMath::Pi()) dPhi = 2*TMath::Pi() - dPhi;
      genVert_dPhi_2 = dPhi;
    }

    if(genVertices.size()>1){
      for(uint i=0; i<(genVertices.size()-1); i++){
	for(uint j=i+1; j<genVertices.size(); j++){
	  float dPhi = fabs(atan2(genVertices[i].y()-beamspot->y0(),genVertices[i].x()-beamspot->x0())-atan2(genVertices[j].y()-beamspot->y0(),genVertices[j].x()-beamspot->x0()));
	  if(dPhi>TMath::Pi()) dPhi = 2*TMath::Pi() - dPhi;
	  h_genVert_dPhi->Fill(dPhi);
	  genVert_dPhi->push_back(dPhi);
	  h_genVert_dVV->Fill(TMath::Sqrt(pow(genVertices[i].x()-genVertices[j].x(),2)+pow(genVertices[i].y()-genVertices[j].y(),2)+pow(genVertices[i].z()-genVertices[j].z(),2)));
	  genVert_dVV->push_back(TMath::Sqrt(pow(genVertices[i].x()-genVertices[j].x(),2)+pow(genVertices[i].y()-genVertices[j].y(),2)+pow(genVertices[i].z()-genVertices[j].z(),2)));
	}
      }
    }
      
    //Get scouting tracks
    //edm::Handle<std::vector<Run3ScoutingTrack>> ScoutingTrackHandle;
    int i_track = -1;
    std::vector<std::vector<float>> deltaRVec;
    for(scoutingTrackIter = ScoutingTrackHandle->begin(); scoutingTrackIter != ScoutingTrackHandle->end(); ++scoutingTrackIter){
      i_track++;
      //std::cout<<"scouting track pt: "<<scoutingTrackIter->pt()<<" eta: "<<scoutingTrackIter->eta()<<" phi: "<<scoutingTrackIter->phi()<<" vertex: "<<scoutingTrackIter->vx()<<" "<<scoutingTrackIter->vy()<<" "<<scoutingTrackIter->vz()<<std::endl;
      int i_gen = -1;
      for(genParticleIter = genParticle_handle->begin(); genParticleIter != genParticle_handle->end(); ++genParticleIter){
	i_gen++;
	if(!isChargedStopDecayProductStatusOne(genParticleIter).first) continue;
	float dPhi = 0;
	if(doPhiCorrection){
	  std::pair<double,double> correction = gen_dxy_correction(genParticleIter,beamspot);
	  dPhi = fabs(scoutingTrackIter->phi()-correction.second);
	}
	else{
	  dPhi = fabs(scoutingTrackIter->phi()-genParticleIter->phi());
	}
	if(dPhi>TMath::Pi()) dPhi = 2*TMath::Pi() - dPhi;
	float dEta = fabs(scoutingTrackIter->eta()-genParticleIter->eta());
	float deltaR = TMath::Sqrt(pow(dPhi,2)+pow(dEta,2));
	float ptRatio = fabs(scoutingTrackIter->pt()-genParticleIter->pt())/(scoutingTrackIter->pt()+genParticleIter->pt());
	if(deltaR<0.05 && ptRatio<0.1){
	  deltaRVec.push_back({float(i_gen),float(i_track),deltaR});
	}
      }
    }
  
    sort(deltaRVec.begin(), deltaRVec.end(), CompareDeltaR); //sort matches by deltaR smallest to largest
    std::vector<std::vector<float>> finalMatches;
    while(deltaRVec.size()>0){
      finalMatches.push_back(deltaRVec[0]);
      int i_genMatch = deltaRVec[0][0];
      int i_trackMatch = deltaRVec[0][1];
      deltaRVec.erase(std::remove_if( deltaRVec.begin(), deltaRVec.end(), [i_genMatch](std::vector<float> x){return x[0]==i_genMatch;}), deltaRVec.end());
      deltaRVec.erase(std::remove_if( deltaRVec.begin(), deltaRVec.end(), [i_trackMatch](std::vector<float> x){return x[1]==i_trackMatch;}), deltaRVec.end());
    }
    for(auto match: finalMatches){
      float pt_gen = (genParticle_handle->begin()+match[0])->pt();
      float pt_track = (ScoutingTrackHandle->begin()+match[1])->pt();
      float eta_gen = (genParticle_handle->begin()+match[0])->eta();
      float eta_track = (ScoutingTrackHandle->begin()+match[1])->eta();
      float phi_gen = (genParticle_handle->begin()+match[0])->phi();
      float phi_track = (ScoutingTrackHandle->begin()+match[1])->phi();
      match_ptRatio->push_back(fabs(pt_track-pt_gen)/(pt_track+pt_gen));
      match_deltaR->push_back(match[2]);
      match_diffPt->push_back(fabs(pt_gen-pt_track));
      match_diffEta->push_back(fabs(eta_gen-eta_track));
      float diffPhi = fabs(phi_gen-phi_track);
      if(diffPhi>TMath::Pi()) diffPhi = 2*TMath::Pi() - diffPhi;
      match_diffPhi->push_back(diffPhi);
      
      float dxy = TMath::Sqrt(pow((genParticle_handle->begin()+match[0])->vx()-beamspot->x0(),2)+pow((genParticle_handle->begin()+match[0])->vy()-beamspot->y0(),2));
      h_match_gen_dxy->Fill(dxy);
      match_gen_dxy->push_back(dxy);
      float dxy_track = TMath::Sqrt(pow((ScoutingTrackHandle->begin()+match[1])->vx()-beamspot->x0(),2)+pow((ScoutingTrackHandle->begin()+match[1])->vy()-beamspot->y0(),2));
      match_diffDxy->push_back(dxy-dxy_track);
      std::pair<double,double> correction = gen_dxy_correction((genParticle_handle->begin()+match[0]),beamspot);
      float dxy_corrected = correction.first;
      match_gen_dxy->push_back(dxy_corrected);
      match_diffDxyCorrected->push_back(dxy_corrected-dxy_track);
      float diffPhiCorrected = fabs(correction.second-phi_track);
      if(diffPhiCorrected>TMath::Pi()) diffPhiCorrected = 2*TMath::Pi() - diffPhiCorrected;
      match_diffPhiCorrected->push_back(diffPhiCorrected);
      //std::cout<<"phi gen: "<<phi_gen<<" phi corrected: "<<correction.second<<std::endl;
      //std::cout<<"dxy gen: "<<dxy<<" dxy corrected: "<<dxy_corrected<<std::endl;
    }
    genScout_nMatches = finalMatches.size();
  }  //doGenMatching

  //Scouting and Reco track matching

  //Structure: for a scouting track, loop over reco tracks, add delta(pt, eta, phi)/(pt, eta, phi) entry to the histograms if it matches
  
  edm::Handle<std::vector<reco::Track>> RecoTrackHandle;
  iEvent.getByToken(recoTracksToken, RecoTrackHandle);
  
  // Loop over Scouting Tracks
  /*
  for (auto scout_track_iter = ScoutingTrackHandle->begin(); scout_track_iter != ScoutingTrackHandle->end(); ++scout_track_iter) {
    const reco::Track& scout_track = *scout_track_iter;

    float pt_scout = scout_track.pt();
    float eta_scout = scout_track.eta();
    float phi_scout = scout_track.phi();
    
    // Loop over Reco Tracks
    for (auto reco_track_iter = RecoTrackHandle->begin(); reco_track_iter != RecoTrackHandle->end(); ++reco_track_iter) {
      const reco::Track& reco_track = *reco_track_iter;
      
      float pt_reco = reco_track.pt();
      float eta_reco = reco_track.eta();
      float phi_reco = reco_track.phi();
      
      float precision = 0.01;
      
      float dpt_reco = (pt_reco - pt_scout) / pt_reco;
      float deta_reco = (eta_reco - eta_scout);
      float dphi_reco = reco::deltaPhi(phi_reco, phi_scout);  // Use CMSSW's deltaPhi() 
      
      if(dpt_reco < precision && deta_reco < precision && dphi_reco < precision){
	//printf("matched track\n");
	reco_dpt_diff->push_back(dpt_reco);
	reco_dpt_diff->push_back(deta_reco);
	reco_dpt_diff->push_back(dphi_reco);
	reco_dxy_diff->push_back(0.0);  //not yet implemented
	reco_dchi2_diff->push_back(0.0);//not yet implemented
      }
      else{
	//printf("did not match track\n");
      }
    }
  }
  */
  
  //Two leading vertices
  vector<double> dBVs;
  VertexDistanceXY vertex_dist_2d;
  t=0;
  Measurement1D dBV_measurement;
  Measurement1D dPVV_measurement;
  float dBV_t;
  
  std::vector<std::vector<float>> deltaRVecVertices;
  for (auto vertex_iter = vertices_ntk.begin(); vertex_iter != vertices_ntk.end(); ++vertex_iter) {
    v = vertices_ntk.at(t);
    dBV_measurement = vertex_dist_2d.distance(v, fake_bs_vtx);
    dBV_t = dBV_measurement.value();
    dBVs.push_back(dBV_t);

    //calculate the distance between the displaced vertices and the leading primary vertex
    Vertex leading_pv = primaryVertices->at(0);
    dPVV_measurement = vertex_dist_2d.distance(v, leading_pv);
    scoutVert_dPVV->push_back(dPVV_measurement.value());
    scoutVert_dPVVErr->push_back(dPVV_measurement.error());
    
    std::vector<TrackRef> trks = vertex_track_vec(v);
    //std::cout<<"vertex number of tracks: "<<trks.size()<<std::endl;
    float p_tot[3] = {0.0, 0.0, 0.0};
    TLorentzVector vtx_p4(0.,0.,0.,0.);
    for(auto trk:trks){
      TLorentzVector trk_p4;
      trk_p4.SetPtEtaPhiM(trk->pt(), trk->eta(), trk->phi(), 0.13957); //pion mass in GeV
      vtx_p4 += trk_p4;
      p_tot[0] += trk->px();
      p_tot[1] += trk->py();
      p_tot[2] += trk->pz();
    }
    float cos_T = ( p_tot[0]*(v.x()-beamspot->x0())+p_tot[1]*(v.y()-beamspot->y0())) / (sqrt(pow(p_tot[0],2)+pow(p_tot[1],2))*sqrt(pow(v.x()-beamspot->x0(),2)+pow(v.y()-beamspot->y0(),2)) );
    float phi = atan2(p_tot[1],p_tot[0]);
    float d_T = fabs( cos(phi)*(v.y()-beamspot->y0()) - sin(phi)*(v.x()-beamspot->x0()) );
    
    h_scoutVert_dBV->Fill(dBV_t);
    scoutVert_dBV->push_back(dBV_t);
    scoutVert_dBVErr->push_back(dBV_measurement.error());
    h_scoutVert_phi->Fill(atan2(v.y()-beamspot->y0(),v.x()-beamspot->x0()));
    scoutVert_phi->push_back(atan2(v.y()-beamspot->y0(),v.x()-beamspot->x0()));
    h_scoutVert_z->Fill(v.z()-beamspot->z0());
    scoutVert_z->push_back(v.z()-beamspot->z0());
    h_scoutVert_x_y->Fill(v.x()-beamspot->x0(),v.y()-beamspot->y0());
    scoutVert_x->push_back(v.x()-beamspot->x0());
    scoutVert_y->push_back(v.y()-beamspot->y0());
    h_scoutVert_nTracks->Fill(trks.size());
    scoutVert_nTracks->push_back(trks.size());
    scoutVert_chi2->push_back(v.normalizedChi2());
    scoutVert_dT->push_back(d_T);
    scoutVert_cosT->push_back(cos_T);
    scoutVert_pMag->push_back(sqrt(pow(p_tot[0],2)+pow(p_tot[1],2)+pow(p_tot[2],2)));

    //kaon specific branches
    float vtxMass = vtx_p4.M();
    float vtxPt = vtx_p4.Pt();
    const TVector3 vp42(vtx_p4.X(), vtx_p4.Y(), 0);
    const TVector3 flight(v.x() - beamspot->x0(), v.y() - beamspot->y0(), v.z() - beamspot->z0());
    const TVector3 flight2(v.x() - beamspot->x0(), v.y() - beamspot->y0(), 0);
    const double costh2 = vp42.Unit().Dot(flight2.Unit());
    const double ct = flight.Mag();
    const double ctau = ct / vtx_p4.Beta() / vtx_p4.Gamma();
    
    scoutVert_costh2->push_back(costh2);
    scoutVert_ctau->push_back(ctau);
    scoutVert_pt->push_back(vtxPt);
    scoutVert_mass->push_back(vtxMass);
    
    if(isMC && doGenMatching){
      int i_trk = -1;
      for(auto trk: trks){
	i_trk++;
	int i_gen = -1;
	for(genParticleIter = genParticle_handle->begin(); genParticleIter != genParticle_handle->end(); ++genParticleIter){
	  i_gen++;
	  std::pair<bool,GlobalPoint> isDecayProduct = isChargedStopDecayProductStatusOne(genParticleIter);
	  if(!isDecayProduct.first) continue;
	  float dPhi = 0;
	  if(doPhiCorrection){
	    std::pair<double,double> correction = gen_dxy_correction(genParticleIter,beamspot);
	    dPhi = fabs(trk->phi()-correction.second);
	  }
	  else{
	    dPhi = fabs(trk->phi()-genParticleIter->phi());
	  }
	  if(dPhi>TMath::Pi()) dPhi = 2*TMath::Pi() - dPhi;
	  float dEta = fabs(trk->eta()-genParticleIter->eta());
	  float deltaR = TMath::Sqrt(pow(dPhi,2)+pow(dEta,2));
	  float ptRatio = fabs(trk->pt()-genParticleIter->pt())/(trk->pt()+genParticleIter->pt());
	  if(deltaR<0.05 && ptRatio<0.1){
	    deltaRVecVertices.push_back({float(i_gen),float(i_trk),deltaR,float(t),isDecayProduct.second.x(),isDecayProduct.second.y(),isDecayProduct.second.z()});
	  }
	} // loop over gen particles
      } // loop over vertex tracks
    } // doGenMatching
    t++;  
  } //loop over vertices
  
  if(isMC && doGenMatching){
    sort(deltaRVecVertices.begin(), deltaRVecVertices.end(), CompareDeltaR); //sort matches by deltaR smallest to largest
    std::vector<std::vector<float>> finalMatchesVertices;
    while(deltaRVecVertices.size()>0){
      finalMatchesVertices.push_back(deltaRVecVertices[0]);
      int i_genMatch = deltaRVecVertices[0][0];
      int i_trackMatch = deltaRVecVertices[0][1];
      int i_vtx = deltaRVecVertices[0][3];
      deltaRVecVertices.erase(std::remove_if( deltaRVecVertices.begin(), deltaRVecVertices.end(), [i_genMatch](std::vector<float> x){return x[0]==i_genMatch;}), deltaRVecVertices.end());
      deltaRVecVertices.erase(std::remove_if( deltaRVecVertices.begin(), deltaRVecVertices.end(), [i_trackMatch,i_vtx](std::vector<float> x){return ((x[1]==i_trackMatch)&&(x[3]==i_vtx));}), deltaRVecVertices.end());
    }
    std::vector<int> vectorNumMatches(t,0);
    for(auto match: finalMatchesVertices){
      vectorNumMatches[match[3]]++;
      if(vectorNumMatches[match[3]]==2){
	Vertex vert = vertices_ntk.at(match[3]);
	h_match_vert_x_y->Fill(vert.x()-beamspot->x0(),vert.y()-beamspot->y0());
	match_vert_x->push_back(vert.x()-beamspot->x0());
	match_vert_y->push_back(vert.y()-beamspot->y0());
      }
    }
    int nVertMatches = 0;
    for(auto numMatches: vectorNumMatches){
      if(numMatches>1) nVertMatches++;
    }
    genScoutVert_nMatches = nVertMatches;
    
    //gen vertex matching
    for(auto vertex: genVertices){
      std::vector<int> numMatches(t,0);
      for(auto match: finalMatchesVertices){
	if((vertex.x()==match[4]) && (vertex.y()==match[5]) && (vertex.z()==match[6])){
	  numMatches[match[3]]++;
	}
      }
      //std::cout<<"gen vertex num matches: ";
      for(uint i=0; i<numMatches.size(); i++){
	//std::cout<<numMatches[i]<<" ";
      }
      //std::cout<<std::endl;
      bool isMatched = false;
      uint i_match=0;
      int maxMatches = 1;
      for(uint i=0; i<numMatches.size(); i++){
	if(numMatches[i]>maxMatches){
	  isMatched = true;
	  maxMatches = numMatches[i];
	  i_match = i;
	}
      }
      if(isMatched){
	h_match_genVert_x_y->Fill(vertex.x()-beamspot->x0(),vertex.y()-beamspot->y0());
	match_genVert_x->push_back(vertex.x()-beamspot->x0());
	match_genVert_y->push_back(vertex.y()-beamspot->y0());
	h_match_genVert_dBV->Fill(TMath::Sqrt(pow(vertex.x()-beamspot->x0(),2)+pow(vertex.y()-beamspot->y0(),2)));
	match_genVert_dBV->push_back(TMath::Sqrt(pow(vertex.x()-beamspot->x0(),2)+pow(vertex.y()-beamspot->y0(),2)));
	Vertex scoutVert = vertices_ntk.at(i_match);
	h_resVert_x->Fill(vertex.x()-scoutVert.x());
	resVert_x->push_back(vertex.x()-scoutVert.x());
	h_resVert_y->Fill(vertex.y()-scoutVert.y());
	resVert_y->push_back(vertex.y()-scoutVert.y());
	h_resVert_z->Fill(vertex.z()-scoutVert.z());
	resVert_z->push_back(vertex.z()-scoutVert.z());
      }
    }
  } //doGenMatching

  if(vertices_ntk.size()>1){
    for (uint i=0; i<(vertices_ntk.size()-1); i++){
      for(uint j=i+1; j<vertices_ntk.size(); j++){
	float dPhi = fabs(atan2(vertices_ntk[i].y()-beamspot->y0(),vertices_ntk[i].x()-beamspot->x0())-atan2(vertices_ntk[j].y()-beamspot->y0(),vertices_ntk[j].x()-beamspot->x0()));
	if(dPhi>TMath::Pi()) dPhi = 2*TMath::Pi() - dPhi;
	h_scoutVert_dPhi->Fill(dPhi);
	scoutVert_dPhi->push_back(dPhi);
	h_scoutVert_dVV->Fill(TMath::Sqrt(pow(vertices_ntk[i].x()-vertices_ntk[j].x(),2)+pow(vertices_ntk[i].y()-vertices_ntk[j].y(),2)+pow(vertices_ntk[i].z()-vertices_ntk[j].z(),2)));
	scoutVert_dVV->push_back(TMath::Sqrt(pow(vertices_ntk[i].x()-vertices_ntk[j].x(),2)+pow(vertices_ntk[i].y()-vertices_ntk[j].y(),2)+pow(vertices_ntk[i].z()-vertices_ntk[j].z(),2)));
      }
    }
  }

  if(pfjetsH.isValid()){
    //Get the jets distributions
    if(pfJetVector.size()>0) ptjet1 = pfJetVector[0].pt();
    if(pfJetVector.size()>1) ptjet2 = pfJetVector[1].pt();
    if(pfJetVector.size()>2) ptjet3 = pfJetVector[2].pt();
    if(pfJetVector.size()>3) ptjet4 = pfJetVector[3].pt();
    
    if(pfJetVector.size()>0) etajet1 = pfJetVector[0].eta();
    if(pfJetVector.size()>1) etajet2 = pfJetVector[1].eta();
    if(pfJetVector.size()>2) etajet3 = pfJetVector[2].eta();
    if(pfJetVector.size()>3) etajet4 = pfJetVector[3].eta();
    
    if(pfJetVector.size()>0) phijet1 = pfJetVector[0].phi();
    if(pfJetVector.size()>1) phijet2 = pfJetVector[1].phi();
    if(pfJetVector.size()>2) phijet3 = pfJetVector[2].phi();
    if(pfJetVector.size()>3) phijet4 = pfJetVector[3].phi();
  }

  if(patjetsH.isValid()){
    //Get the jets distributions
    if(patJetVector.size()>0) ptjet1 = patJetVector[0].pt();
    if(patJetVector.size()>1) ptjet2 = patJetVector[1].pt();
    if(patJetVector.size()>2) ptjet3 = patJetVector[2].pt();
    if(patJetVector.size()>3) ptjet4 = patJetVector[3].pt();
    
    if(patJetVector.size()>0) etajet1 = patJetVector[0].eta();
    if(patJetVector.size()>1) etajet2 = patJetVector[1].eta();
    if(patJetVector.size()>2) etajet3 = patJetVector[2].eta();
    if(patJetVector.size()>3) etajet4 = patJetVector[3].eta();
    
    if(patJetVector.size()>0) phijet1 = patJetVector[0].phi();
    if(patJetVector.size()>1) phijet2 = patJetVector[1].phi();
    if(patJetVector.size()>2) phijet3 = patJetVector[2].phi();
    if(patJetVector.size()>3) phijet4 = patJetVector[3].phi();
  }
  
  if(verticesH.isValid() && (nVertices>0)){
    //Calculate the vertex distributions
    auto largest_dBV = findTwoLargestIndices(dBVs);
  
    Vertex v1 = vertices_ntk.at(largest_dBV.first);
    Measurement1D dBV_Meas1D_1 = vertex_dist_2d.distance(v1, fake_bs_vtx);
    vector<TrackRef> tks_1 = vertex_track_vec(v1);
    ntk_1 = tks_1.size();
    dBV_1 = dBV_Meas1D_1.value();
    bs2derr_1 = dBV_Meas1D_1.error();

    if(dBV_1<0.01) return; 

    h_genWeights->Fill("dBV",genWeight);
    h_weights->Fill("dBV",theWeight);
    h_weightsSquared->Fill("dBV",pow(theWeight,2));

    if(isMC){
      h_weights_LUMCorrected->Fill("dBV",weightMap->at("correctedNominal"));
      h_weightsSquared_LUMCorrected->Fill("dBV",pow(weightMap->at("correctedNominal"),2));
    }
    
    //printf("First dBV = %f, second dBV = %f\n", dBV_1, dBV_2);
    if(nVertices>1){
      Vertex v2 = vertices_ntk.at(largest_dBV.second);
      Measurement1D dBV_Meas1D_2 = vertex_dist_2d.distance(v2, fake_bs_vtx);
      vector<TrackRef> tks_2 = vertex_track_vec(v2);
      dBV_2 = dBV_Meas1D_2.value();
      bs2derr_2 = dBV_Meas1D_2.error();
      ntk_2 = tks_2.size();
    }
  }

  tree->Fill();
  objectTree->Fill();
}

//Fill the tree with the variables retrieved above
void K0TreeMakerRun3::beginJob() {
    edm::Service<TFileService> fs;
    tree = fs->make<TTree>("tree"      , "tree");

    //tree->Branch("nPFJets"             , &nPFJets                     , "nPFJets/F"     );

    tree->Branch("ptjet1"              , &ptjet1                      , "ptjet1/F"      );
    tree->Branch("ptjet2"              , &ptjet2                      , "ptjet2/F"      ); 
    tree->Branch("ptjet3"              , &ptjet3                      , "ptjet3/F"      );
    tree->Branch("ptjet4"              , &ptjet4                      , "ptjet4/F"      );    

    tree->Branch("etajet1"             , &etajet1                     , "etajet1/F"     );
    tree->Branch("etajet2"             , &etajet2                     , "etajet2/F"     );
    tree->Branch("etajet3"             , &etajet3                     , "etajet3/F"     );
    tree->Branch("etajet4"             , &etajet4                     , "etajet4/F"     );

    tree->Branch("phijet1"             , &phijet1                     , "phijet1/F"     );
    tree->Branch("phijet2"             , &phijet2                     , "phijet2/F"     );
    tree->Branch("phijet3"             , &phijet3                     , "phijet3/F"     );
    tree->Branch("phijet4"             , &phijet4                     , "phijet4/F"     );

    //Add the missing distributions
    tree->Branch("dBV_1"               , &dBV_1                       , "dBV_1/F"       );
    tree->Branch("dBV_2"               , &dBV_2                       , "dBV_2/F"       );

    tree->Branch("bs2derr_1"           , &bs2derr_1                   , "bs2derr_1/F"   );
    tree->Branch("bs2derr_2"           , &bs2derr_2                   , "bs2derr_2/F"   );
    
    tree->Branch("ntk_1"               , &ntk_1                       , "ntk_1/I"       );
    tree->Branch("ntk_2"               , &ntk_2                       , "ntk_2/I"       );

    tree->Branch("nVertices"               , &nVertices                       , "nVertices/I"       );
    
    tree->Branch("HT"                  , &HT                          , "HT/F"          );

    //the L1 results also in separeated branches  
    tree->Branch("L1_HTT200er"           , &L1_HTT200er                   , "L1_HTT200er/O"  );
    tree->Branch("L1_HTT255er"           , &L1_HTT255er                   , "L1_HTT255er/O"  );
    tree->Branch("L1_HTT280er"           , &L1_HTT280er                   , "L1_HTT280er/O"  );
    tree->Branch("L1_HTT320er"           , &L1_HTT320er                   , "L1_HTT320er/O"  );
    tree->Branch("L1_HTT360er"           , &L1_HTT360er                   , "L1_HTT360er/O"  );
    tree->Branch("L1_HTT400er"           , &L1_HTT400er                   , "L1_HTT400er/O"  );
    tree->Branch("L1_HTT450er"           , &L1_HTT450er                   , "L1_HTT450er/O"  );
    tree->Branch("L1_ETT2000"           , &L1_ETT2000                   , "L1_ETT2000/O"  );
    tree->Branch("L1_SingleJet180"           , &L1_SingleJet180                   , "L1_SingleJet180/O"  );
    tree->Branch("L1_SingleJet200"           , &L1_SingleJet200                   , "L1_SingleJet200/O"  );
    tree->Branch("L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5", &L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5, "L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5/O"  );
    tree->Branch("L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5", &L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5, "L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5/O"  );
    tree->Branch("L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5", &L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5, "L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5/O"  );
    tree->Branch("L1_FinalResult"           , &L1_FinalResult                   , "L1_FinalResult/O"  );
    
    tree->Branch("genVert_x_1"              , &genVert_x_1                      , "genVert_x_1/F"      );
    tree->Branch("genVert_y_1"              , &genVert_y_1                      , "genVert_y_1/F"      );
    tree->Branch("genVert_z_1"              , &genVert_z_1                      , "genVert_z_1/F"      );
    tree->Branch("genVert_dBV_1"              , &genVert_dBV_1                      , "genVert_dBV_1/F"      );
    tree->Branch("genVert_3d_1"              , &genVert_3d_1                      , "genVert_3d_1/F"      );
    tree->Branch("genVert_motherEta_1"       , &genVert_motherEta               , "genVert_motherEta_1/F"      );
    tree->Branch("genVert_motherPhi_1"       , &genVert_motherPhi               , "genVert_motherPhi_1/F"      );
    tree->Branch("genVert_motherPt_1"       , &genVert_motherPt               , "genVert_motherPt_1/F"      );
    tree->Branch("genVert_motherDistTraveled_1"       , &genVert_motherDistTraveled               , "genVert_motherDistTraveled_1/F"      );
    tree->Branch("genVert_dVV"              , &genVert_dVV_2                      , "genVert_dVV/F"      );
    tree->Branch("genVert_dPhi"              , &genVert_dPhi_2                      , "genVert_dPhi/F"      );
    tree->Branch("genScout_nMatches"              , &genScout_nMatches                      , "genScout_nMatches/I"      );
    tree->Branch("genScoutVert_nMatches"              , &genScoutVert_nMatches                      , "genScoutVert_nMatches/I"      );
    tree->Branch("genVert_nVertices", &genVert_nVertices, "genVert_nVertices/I");
    tree->Branch("scoutVert_nVertices", &scoutVert_nVertices, "scoutVert_nVertices/I");
    //tree->Branch("scoutVert_dPVV"           , &scoutVert_dPVV                        , "scoutVert_dPVV/F"      );
    
    scoutTrack_pt = new std::vector<float>;
    scoutTrack_eta = new std::vector<float>;
    scoutTrack_phi = new std::vector<float>;
    scoutTrack_phiBeamspot = new std::vector<float>;
    scoutTrack_reducedChi2 = new std::vector<float>;
    scoutTrack_charge = new std::vector<float>;
    scoutTrack_dxy = new std::vector<float>;
    scoutTrack_dxyErr = new std::vector<float>;
    scoutTrack_dxySig = new std::vector<float>;
    scoutTrack_dxySigned = new std::vector<float>;
    scoutTrack_d3D = new std::vector<float>;
    scoutTrack_d3DErr = new std::vector<float>;
    scoutTrack_d3DSig = new std::vector<float>;
    scoutTrack_dz = new std::vector<float>;
    scoutTrack_dzErr = new std::vector<float>;
    scoutTrack_dzSig = new std::vector<float>;
    scoutTrack_dszUncertainty = new std::vector<float>;
    scoutTrack_dxyUncertainty = new std::vector<float>;
    scoutTrack_dszdxyCovariance = new std::vector<float>;
    scoutTrack_vx = new std::vector<float>;
    scoutTrack_vy = new std::vector<float>;
    scoutTrack_iJet = new std::vector<int>;
    scoutTrack_nValidPixelHits = new std::vector<int>;
    scoutTrack_nTrackerLayersWithMeasurement = new std::vector<int>;
    scoutTrack_nValidStripHits = new std::vector<int>;
    scoutTrack_nMissingInnerHits = new std::vector<int>;
    scoutTrack_minPVDxy = new std::vector<float>;
    scoutTrack_minPVDz = new std::vector<float>;

    vertTrack_pt = new std::vector<float>;
    vertTrack_eta = new std::vector<float>;
    vertTrack_phi = new std::vector<float>;
    vertTrack_reducedChi2 = new std::vector<float>;
    vertTrack_charge = new std::vector<float>;
    vertTrack_dxy = new std::vector<float>;
    vertTrack_dxyErr = new std::vector<float>;
    vertTrack_dxySig = new std::vector<float>;
    vertTrack_dxySigned = new std::vector<float>;
    vertTrack_d3D = new std::vector<float>;
    vertTrack_d3DErr = new std::vector<float>;
    vertTrack_d3DSig = new std::vector<float>;
    vertTrack_dz = new std::vector<float>;
    vertTrack_dzErr = new std::vector<float>;
    vertTrack_dzSig = new std::vector<float>;
    vertTrack_nValidPixelHits = new std::vector<int>;
    vertTrack_nTrackerLayersWithMeasurement = new std::vector<int>;
    vertTrack_nValidStripHits = new std::vector<int>;
    vertTrack_nMissingInnerHits = new std::vector<int>;
    vertTrack_iVtx = new std::vector<int>;
    vertTrack_iJet = new std::vector<int>;
    vertTrack_hasPFMatch = new std::vector<bool>;

    reco_dpt_diff = new std::vector<float>;
    reco_deta_diff = new std::vector<float>;
    reco_dphi_diff = new std::vector<float>;
    reco_dxy_diff = new std::vector<float>;
    reco_dchi2_diff = new std::vector<float>;
    
    match_ptRatio = new std::vector<float>;
    match_deltaR = new std::vector<float>;
    match_diffPt = new std::vector<float>;
    match_diffEta = new std::vector<float>;
    match_diffPhi = new std::vector<float>;
    match_diffPhiCorrected = new std::vector<float>;
    match_gen_dxy = new std::vector<float>;
    match_gen_dxyCorrected = new std::vector<float>;
    match_diffDxy = new std::vector<float>;
    match_diffDxyCorrected = new std::vector<float>;
    gen_dxy = new std::vector<float>;
    gen_dxyCorrected = new std::vector<float>;
    match_vert_x = new std::vector<float>;
    match_vert_y = new std::vector<float>;
    match_genVert_x = new std::vector<float>;
    match_genVert_y = new std::vector<float>;
    match_genVert_dBV = new std::vector<float>;
    genVert_dBV = new std::vector<float>;
    genVert_phi = new std::vector<float>;
    genVert_z = new std::vector<float>;
    genVert_x = new std::vector<float>;
    genVert_y = new std::vector<float>;
    genVert_nParticles = new std::vector<float>;
    genVert_dPhi = new std::vector<float>;
    genVert_dVV = new std::vector<float>;
    resVert_x = new std::vector<float>;
    resVert_y = new std::vector<float>;
    resVert_z = new std::vector<float>;
    scoutVert_dBV = new std::vector<float>;
    scoutVert_dBVErr = new std::vector<float>;
    scoutVert_dPVV = new std::vector<float>;
    scoutVert_dPVVErr = new std::vector<float>;
    scoutVert_phi = new std::vector<float>;
    scoutVert_z = new std::vector<float>;
    scoutVert_x = new std::vector<float>;
    scoutVert_y = new std::vector<float>;
    scoutVert_nTracks = new std::vector<float>;
    scoutVert_chi2 = new std::vector<float>;
    scoutVert_dPhi = new std::vector<float>;
    scoutVert_dVV = new std::vector<float>;
    scoutVert_dT = new std::vector<float>;
    scoutVert_cosT = new std::vector<float>;
    scoutVert_pMag = new std::vector<float>;
    scoutVert_costh2 = new std::vector<float>;
    scoutVert_ctau = new std::vector<float>;
    scoutVert_pt = new std::vector<float>;
    scoutVert_mass = new std::vector<float>;
    
    jet_pt = new std::vector<float>;
    jet_eta = new std::vector<float>;
    jet_phi = new std::vector<float>;
    jet_mass = new std::vector<float>;
    jet_energy = new std::vector<float>;
    jet_chHEF = new std::vector<float>;
    jet_neHEF = new std::vector<float>;
    jet_muonEF = new std::vector<float>;
    jet_chEmEF = new std::vector<float>;
    jet_neEmEF = new std::vector<float>;
    jet_hfHEF = new std::vector<float>;
    jet_hfEmEF = new std::vector<float>;
    jet_hoEF = new std::vector<float>;
    jet_chMultiplicity = new std::vector<int>;
    jet_neMultiplicity = new std::vector<int>;
    jet_passJetIdTight = new std::vector<bool>;

    genJet_pt = new std::vector<float>;
    genJet_eta = new std::vector<float>;
    genJet_phi = new std::vector<float>;
    genJet_mass = new std::vector<float>;
    genJet_energy = new std::vector<float>;
    genJet_nConstituents = new std::vector<int>;

    muon_pt = new std::vector<float>;
    muon_eta = new std::vector<float>;
    muon_phi = new std::vector<float>;
    muon_chi2 = new std::vector<float>;
    muon_nTrackerLayersWithMeasurement = new std::vector<int>;
    muon_nValidPixelHits = new std::vector<int>;
    muon_nValidRecoMuonHits = new std::vector<int>;
    muon_nRecoMuonMatchedStations = new std::vector<int>;
    muon_trackIso = new std::vector<float>;
    
    objectTree = fs->make<TTree>("objectTree","objectTree");
    //std::cout<<"objectTree directory beginJob "<<objectTree->GetDirectory()->GetPath()<<std::endl;
    objectTree->Branch("vertTrack_pt",&vertTrack_pt);
    objectTree->Branch("vertTrack_eta",&vertTrack_eta);
    objectTree->Branch("vertTrack_phi",&vertTrack_phi);
    objectTree->Branch("vertTrack_reducedChi2",&vertTrack_reducedChi2);
    objectTree->Branch("vertTrack_charge",&vertTrack_charge);
    objectTree->Branch("vertTrack_dxy",&vertTrack_dxy);
    objectTree->Branch("vertTrack_dxyErr",&vertTrack_dxyErr);
    objectTree->Branch("vertTrack_dxySig",&vertTrack_dxySig);
    objectTree->Branch("vertTrack_dxySigned",&vertTrack_dxySigned);
    objectTree->Branch("vertTrack_d3D",&vertTrack_d3D);
    objectTree->Branch("vertTrack_d3DErr",&vertTrack_d3DErr);
    objectTree->Branch("vertTrack_d3DSig",&vertTrack_d3DSig);
    objectTree->Branch("vertTrack_dz",&vertTrack_dz);
    objectTree->Branch("vertTrack_dzErr",&vertTrack_dzErr);
    objectTree->Branch("vertTrack_dzSig",&vertTrack_dzSig);
    objectTree->Branch("vertTrack_nValidPixelHits",&vertTrack_nValidPixelHits);
    objectTree->Branch("vertTrack_nTrackerLayersWithMeasurement",&vertTrack_nTrackerLayersWithMeasurement);
    objectTree->Branch("vertTrack_nValidStripHits",&vertTrack_nValidStripHits);
    objectTree->Branch("vertTrack_nMissingInnerHits",&vertTrack_nMissingInnerHits);
    objectTree->Branch("vertTrack_iVtx",&vertTrack_iVtx);
    objectTree->Branch("vertTrack_iJet",&vertTrack_iJet);
    objectTree->Branch("vertTrack_hasPFMatch",&vertTrack_hasPFMatch);

    //For the matching between reco and scout tracks
    objectTree->Branch("reco_dpt_diff",&reco_dpt_diff);
    objectTree->Branch("reco_deta_diff",&reco_deta_diff);
    objectTree->Branch("reco_dphi_diff",&reco_dphi_diff);
    objectTree->Branch("reco_dxy_diff",&reco_dxy_diff);
    objectTree->Branch("reco_dchi2_diff",&reco_dchi2_diff);
    
    objectTree->Branch("scoutTrack_pt",&scoutTrack_pt);
    objectTree->Branch("scoutTrack_eta",&scoutTrack_eta);
    objectTree->Branch("scoutTrack_phi",&scoutTrack_phi);
    objectTree->Branch("scoutTrack_phiBeamspot",&scoutTrack_phiBeamspot);
    objectTree->Branch("scoutTrack_reducedChi2",&scoutTrack_reducedChi2);
    objectTree->Branch("scoutTrack_charge",&scoutTrack_charge);
    objectTree->Branch("scoutTrack_dxy",&scoutTrack_dxy);
    objectTree->Branch("scoutTrack_dxyErr",&scoutTrack_dxyErr);
    objectTree->Branch("scoutTrack_dxySig",&scoutTrack_dxySig);
    objectTree->Branch("scoutTrack_dxySigned",&scoutTrack_dxySigned);
    objectTree->Branch("scoutTrack_d3D",&scoutTrack_d3D);
    objectTree->Branch("scoutTrack_d3DErr",&scoutTrack_d3DErr);
    objectTree->Branch("scoutTrack_d3DSig",&scoutTrack_d3DSig);
    objectTree->Branch("scoutTrack_dz",&scoutTrack_dz);
    objectTree->Branch("scoutTrack_dzErr",&scoutTrack_dzErr);
    objectTree->Branch("scoutTrack_dzSig",&scoutTrack_dzSig);
    objectTree->Branch("scoutTrack_dszUncertainty",&scoutTrack_dszUncertainty);
    objectTree->Branch("scoutTrack_dxyUncertainty",&scoutTrack_dxyUncertainty);
    objectTree->Branch("scoutTrack_dszdxyCovariance",&scoutTrack_dszdxyCovariance);
    objectTree->Branch("scoutTrack_vx",&scoutTrack_vx);
    objectTree->Branch("scoutTrack_vy",&scoutTrack_vy);
    objectTree->Branch("scoutTrack_iJet",&scoutTrack_iJet);
    objectTree->Branch("scoutTrack_nValidPixelHits",&scoutTrack_nValidPixelHits);
    objectTree->Branch("scoutTrack_nTrackerLayersWithMeasurement",&scoutTrack_nTrackerLayersWithMeasurement);
    objectTree->Branch("scoutTrack_nValidStripHits",&scoutTrack_nValidStripHits);
    objectTree->Branch("scoutTrack_nMissingInnerHits",&scoutTrack_nMissingInnerHits);
    objectTree->Branch("scoutTrack_minPVDxy",&scoutTrack_minPVDxy);
    objectTree->Branch("scoutTrack_minPVDz",&scoutTrack_minPVDz);
    
    objectTree->Branch("match_ptRatio",&match_ptRatio);
    objectTree->Branch("match_deltaR",&match_deltaR);
    objectTree->Branch("match_diffPt",&match_diffPt);
    objectTree->Branch("match_diffEta",&match_diffEta);
    objectTree->Branch("match_diffPhi",&match_diffPhi);
    objectTree->Branch("match_diffPhiCorrected",&match_diffPhiCorrected);
    objectTree->Branch("match_gen_dxy",&match_gen_dxy);
    objectTree->Branch("match_gen_dxyCorrected",&match_gen_dxyCorrected);
    objectTree->Branch("match_diffDxy",&match_diffDxy);
    objectTree->Branch("match_diffDxyCorrected",&match_diffDxyCorrected);
    objectTree->Branch("gen_dxy",&gen_dxy);
    objectTree->Branch("gen_dxyCorrected",&gen_dxyCorrected);
    objectTree->Branch("match_vert_x",&match_vert_x);
    objectTree->Branch("match_vert_y",&match_vert_y);
    objectTree->Branch("match_genVert_x",&match_genVert_x);
    objectTree->Branch("match_genVert_y",&match_genVert_y);
    objectTree->Branch("match_genVert_dBV",&match_genVert_dBV);
    objectTree->Branch("genVert_dBV",&genVert_dBV);
    objectTree->Branch("genVert_phi",&genVert_phi);
    objectTree->Branch("genVert_z",&genVert_z);
    objectTree->Branch("genVert_x",&genVert_x);
    objectTree->Branch("genVert_y",&genVert_y);
    objectTree->Branch("genVert_nParticles",&genVert_nParticles);
    objectTree->Branch("genVert_dPhi",&genVert_dPhi);
    objectTree->Branch("genVert_dVV",&genVert_dVV);
    objectTree->Branch("resVert_x",&resVert_x);
    objectTree->Branch("resVert_y",&resVert_y);
    objectTree->Branch("resVert_z",&resVert_z);
    objectTree->Branch("scoutVert_dBV",&scoutVert_dBV);
    objectTree->Branch("scoutVert_dBVErr",&scoutVert_dBVErr);
    objectTree->Branch("scoutVert_dPVV",&scoutVert_dPVV);
    objectTree->Branch("scoutVert_dPVVErr",&scoutVert_dPVVErr);
    objectTree->Branch("scoutVert_phi",&scoutVert_phi);
    objectTree->Branch("scoutVert_z",&scoutVert_z);
    objectTree->Branch("scoutVert_x",&scoutVert_x);
    objectTree->Branch("scoutVert_y",&scoutVert_y);
    objectTree->Branch("scoutVert_nTracks",&scoutVert_nTracks);
    objectTree->Branch("scoutVert_chi2",&scoutVert_chi2);
    objectTree->Branch("scoutVert_dPhi",&scoutVert_dPhi);
    objectTree->Branch("scoutVert_dVV",&scoutVert_dVV);
    objectTree->Branch("scoutVert_dT",&scoutVert_dT);
    objectTree->Branch("scoutVert_cosT",&scoutVert_cosT);
    objectTree->Branch("scoutVert_pMag",&scoutVert_pMag);
    objectTree->Branch("scoutVert_costh2",&scoutVert_costh2);
    objectTree->Branch("scoutVert_ctau",&scoutVert_ctau);
    objectTree->Branch("scoutVert_pt",&scoutVert_pt);
    objectTree->Branch("scoutVert_mass",&scoutVert_mass);
    objectTree->Branch("weight", &weight, "weight/D");
    objectTree->Branch("uncorrectedWeight", &uncorrectedWeight, "uncorrectedWeight/D");
    objectTree->Branch("weight_PU_BCDEFGHI_nominal", &weight_PU_BCDEFGHI_nominal, "weight_PU_BCDEFGHI_nominal/D");
    objectTree->Branch("weight_PU_BCDEFGHI_up", &weight_PU_BCDEFGHI_up, "weight_PU_BCDEFGHI_up/D");
    objectTree->Branch("weight_PU_BCDEFGHI_down", &weight_PU_BCDEFGHI_down, "weight_PU_BCDEFGHI_down/D");
    objectTree->Branch("weight_PU_C_nominal", &weight_PU_C_nominal, "weight_PU_C_nominal/D");
    objectTree->Branch("weight_PU_C_up", &weight_PU_C_up, "weight_PU_C_up/D");
    objectTree->Branch("weight_PU_C_down", &weight_PU_C_down, "weight_PU_C_down/D");
    objectTree->Branch("weight_PU_D_nominal", &weight_PU_D_nominal, "weight_PU_D_nominal/D");
    objectTree->Branch("weight_PU_D_up", &weight_PU_D_up, "weight_PU_D_up/D");
    objectTree->Branch("weight_PU_D_down", &weight_PU_D_down, "weight_PU_D_down/D");
    objectTree->Branch("weight_PU_E_nominal", &weight_PU_E_nominal, "weight_PU_E_nominal/D");
    objectTree->Branch("weight_PU_E_up", &weight_PU_E_up, "weight_PU_E_up/D");
    objectTree->Branch("weight_PU_E_down", &weight_PU_E_down, "weight_PU_E_down/D");
    objectTree->Branch("weight_PU_F_nominal", &weight_PU_F_nominal, "weight_PU_F_nominal/D");
    objectTree->Branch("weight_PU_F_up", &weight_PU_F_up, "weight_PU_F_up/D");
    objectTree->Branch("weight_PU_F_down", &weight_PU_F_down, "weight_PU_F_down/D");
    objectTree->Branch("weight_PU_G_nominal", &weight_PU_G_nominal, "weight_PU_G_nominal/D");
    objectTree->Branch("weight_PU_G_up", &weight_PU_G_up, "weight_PU_G_up/D");
    objectTree->Branch("weight_PU_G_down", &weight_PU_G_down, "weight_PU_G_down/D");
    objectTree->Branch("weight_PU_H_nominal", &weight_PU_H_nominal, "weight_PU_H_nominal/D");
    objectTree->Branch("weight_PU_H_up", &weight_PU_H_up, "weight_PU_H_up/D");
    objectTree->Branch("weight_PU_H_down", &weight_PU_H_down, "weight_PU_H_down/D");
    objectTree->Branch("weight_PU_I_nominal", &weight_PU_I_nominal, "weight_PU_I_nominal/D");
    objectTree->Branch("weight_PU_I_up", &weight_PU_I_up, "weight_PU_I_up/D");
    objectTree->Branch("weight_PU_I_down", &weight_PU_I_down, "weight_PU_I_down/D");
    objectTree->Branch("observedPU", &observedPU, "observedPU/I");
    objectTree->Branch("truePU", &truePU, "truePU/I");
    objectTree->Branch("nPV", &nPV, "nPV/I");
    objectTree->Branch("beamspot_x", &beamspot_x, "beamspot_x/F");
    objectTree->Branch("beamspot_y", &beamspot_y, "beamspot_y/F");
    objectTree->Branch("beamspot_z", &beamspot_z, "beamspot_z/F");
    objectTree->Branch("beamspot_xErr", &beamspot_xErr, "beamspot_xErr/F");
    objectTree->Branch("beamspot_yErr", &beamspot_yErr, "beamspot_yErr/F");
    objectTree->Branch("beamspot_zErr", &beamspot_zErr, "beamspot_zErr/F");
    objectTree->Branch("beamspot_xWidth", &beamspot_xWidth, "beamspot_xWidth/F");
    objectTree->Branch("beamspot_yWidth", &beamspot_yWidth, "beamspot_yWidth/F");
    objectTree->Branch("beamspot_widthErr", &beamspot_widthErr, "beamspot_widthErr/F");
    objectTree->Branch("beamspot_type", &beamspot_type, "beamspot_type/F");
    objectTree->Branch("offlineBeamspot_x", &offlineBeamspot_x, "offlineBeamspot_x/F");
    objectTree->Branch("offlineBeamspot_y", &offlineBeamspot_y, "offlineBeamspot_y/F");
    objectTree->Branch("offlineBeamspot_z", &offlineBeamspot_z, "offlineBeamspot_z/F");
    objectTree->Branch("offlineBeamspot_xErr", &offlineBeamspot_xErr, "offlineBeamspot_xErr/F");
    objectTree->Branch("offlineBeamspot_yErr", &offlineBeamspot_yErr, "offlineBeamspot_yErr/F");
    objectTree->Branch("offlineBeamspot_zErr", &offlineBeamspot_zErr, "offlineBeamspot_zErr/F");
    objectTree->Branch("eventId", &eventId, "eventId/I");
    objectTree->Branch("runNumber", &runNumber, "runNumber/I");
    objectTree->Branch("lumiBlock", &lumiBlock, "lumiBlock/I");
    objectTree->Branch("jet_pt",&jet_pt);
    objectTree->Branch("jet_eta",&jet_eta);
    objectTree->Branch("jet_phi",&jet_phi);
    objectTree->Branch("jet_mass",&jet_mass);
    objectTree->Branch("jet_energy",&jet_energy);
    objectTree->Branch("jet_chHEF",&jet_chHEF);
    objectTree->Branch("jet_neHEF",&jet_neHEF);
    objectTree->Branch("jet_muonEF",&jet_muonEF);
    objectTree->Branch("jet_chEmEF",&jet_chEmEF);
    objectTree->Branch("jet_neEmEF",&jet_neEmEF);
    objectTree->Branch("jet_hfHEF",&jet_hfHEF);
    objectTree->Branch("jet_hfEmEF",&jet_hfEmEF);
    objectTree->Branch("jet_hoEF",&jet_hoEF);
    objectTree->Branch("jet_chMultiplicity",&jet_chMultiplicity);
    objectTree->Branch("jet_neMultiplicity",&jet_neMultiplicity);
    objectTree->Branch("jet_passJetIdTight",&jet_passJetIdTight);
    objectTree->Branch("genJet_pt",&genJet_pt);
    objectTree->Branch("genJet_eta",&genJet_eta);
    objectTree->Branch("genJet_phi",&genJet_phi);
    objectTree->Branch("genJet_mass",&genJet_mass);
    objectTree->Branch("genJet_energy",&genJet_energy);
    objectTree->Branch("genJet_nConstituents",&genJet_nConstituents);
    objectTree->Branch("nGenJets", &nGenJets, "nGenJets/I");
    objectTree->Branch("genHT", &genHT, "genHT/F");
    objectTree->Branch("ht_corrected", &ht_corrected, "ht_corrected/F");
    objectTree->Branch("muon_pt",&muon_pt);
    objectTree->Branch("muon_eta",&muon_eta);
    objectTree->Branch("muon_phi",&muon_phi);
    objectTree->Branch("muon_chi2",&muon_chi2);
    objectTree->Branch("muon_nTrackerLayersWithMeasurement",&muon_nTrackerLayersWithMeasurement);
    objectTree->Branch("muon_nValidPixelHits",&muon_nValidPixelHits);
    objectTree->Branch("muon_nValidRecoMuonHits",&muon_nValidRecoMuonHits);
    objectTree->Branch("muon_nRecoMuonMatchedStations",&muon_nRecoMuonMatchedStations);
    objectTree->Branch("muon_trackIso",&muon_trackIso);
    
    h_genWeights->GetXaxis()->SetBinLabel(1,"None");
    h_genWeights->GetXaxis()->SetBinLabel(2,"nJets");
    h_genWeights->GetXaxis()->SetBinLabel(3,"nVertices");
    h_genWeights->GetXaxis()->SetBinLabel(4,"dBV");
    h_weights->GetXaxis()->SetBinLabel(1,"None");
    h_weights->GetXaxis()->SetBinLabel(2,"nJets");
    h_weights->GetXaxis()->SetBinLabel(3,"nVertices");
    h_weights->GetXaxis()->SetBinLabel(4,"dBV");
    h_weights_LUMCorrected->GetXaxis()->SetBinLabel(1,"None");
    h_weights_LUMCorrected->GetXaxis()->SetBinLabel(2,"nJets");
    h_weights_LUMCorrected->GetXaxis()->SetBinLabel(3,"nVertices");
    h_weights_LUMCorrected->GetXaxis()->SetBinLabel(4,"dBV");
    h_weightsSquared->GetXaxis()->SetBinLabel(1,"None");
    h_weightsSquared->GetXaxis()->SetBinLabel(2,"nJets");
    h_weightsSquared->GetXaxis()->SetBinLabel(3,"nVertices");
    h_weightsSquared->GetXaxis()->SetBinLabel(4,"dBV");
    h_weightsSquared_LUMCorrected->GetXaxis()->SetBinLabel(1,"None");
    h_weightsSquared_LUMCorrected->GetXaxis()->SetBinLabel(2,"nJets");
    h_weightsSquared_LUMCorrected->GetXaxis()->SetBinLabel(3,"nVertices");
    h_weightsSquared_LUMCorrected->GetXaxis()->SetBinLabel(4,"dBV");
}

// ------------ method called once each job just after ending the event loop  ------------
void K0TreeMakerRun3::endJob() {
  //std::cout<<"objectTree directory endJob "<<objectTree->GetDirectory()->GetPath()<<std::endl;
  removeFlows(h_match_gen_dxy);
  removeFlows(h_gen_dxy);
  h_match_gen_dxy->Sumw2();
  h_gen_dxy->Sumw2();
  TH1F* h_matchEff_dxy = (TH1F*)h_match_gen_dxy->Clone();
  h_matchEff_dxy->SetName("matchEff_dxy");
  h_matchEff_dxy->GetYaxis()->SetTitle("Match Efficiency");
  h_matchEff_dxy->Divide(h_match_gen_dxy, h_gen_dxy, 1.0, 1.0, "B");
  h_matchEff_dxy->SetAxisRange(0, 1.1, "Y");
  h_matchEff_dxy->Draw();
  //std::cout<<"test 1"<<std::endl;
  //std::cout<<"gDir "<<gDirectory->GetName()<<std::endl;
  objectTree->GetDirectory()->cd();
  h_matchEff_dxy->Write("", TObject::kOverwrite);
  //std::cout<<"test 2"<<std::endl;
  removeFlows(h_match_genVert_dBV);
  removeFlows(h_genVert_dBV);
  h_match_genVert_dBV->Sumw2();
  h_genVert_dBV->Sumw2();
  TH1F* h_vertMatchEff_dBV = (TH1F*)h_match_genVert_dBV->Clone();
  h_vertMatchEff_dBV->SetName("vertMatchEff_dBV");
  h_vertMatchEff_dBV->GetYaxis()->SetTitle("Match Efficiency");
  h_vertMatchEff_dBV->Divide(h_match_genVert_dBV, h_genVert_dBV, 1.0, 1.0, "B");
  h_vertMatchEff_dBV->SetAxisRange(0, 1.1, "Y");
  h_vertMatchEff_dBV->Draw();
  h_vertMatchEff_dBV->Write();
  
  h_match_vert_x_y->Draw();
  h_match_vert_x_y->Write();

  h_match_genVert_x_y->Draw();
  h_match_genVert_x_y->Write();

  h_match_genVert_dBV->Draw();
  h_match_genVert_dBV->Write();

  h_genWeights->Draw();
  h_genWeights->Write();

  h_weights->Draw();
  h_weights->Write();

  h_weights_LUMCorrected->Draw();
  h_weights_LUMCorrected->Write();
  
  h_weightsSquared->Draw();
  h_weightsSquared->Write();

  h_weightsSquared_LUMCorrected->Draw();
  h_weightsSquared_LUMCorrected->Write();
  
  removeFlows(h_genVert_phi);
  h_genVert_phi->Draw();
  h_genVert_phi->Write();

  removeFlows(h_genVert_z);
  h_genVert_z->Draw();
  h_genVert_z->Write();

  removeFlows(h_genVert_nParticles);
  h_genVert_nParticles->Draw();
  h_genVert_nParticles->Write();

  removeFlows(h_genVert_dPhi);
  h_genVert_dPhi->Draw();
  h_genVert_dPhi->Write();

  removeFlows(h_genVert_dVV);
  h_genVert_dVV->Draw();
  h_genVert_dVV->Write();

  removeFlows(h_genVert_nVertices);
  h_genVert_nVertices->Draw();
  h_genVert_nVertices->Write();
  
  h_genVert_x_y->Draw();
  h_genVert_x_y->Write();
  
  removeFlows(h_resVert_x);
  h_resVert_x->Draw();
  h_resVert_x->Write();

  removeFlows(h_resVert_y);
  h_resVert_y->Draw();
  h_resVert_y->Write();

  removeFlows(h_resVert_z);
  h_resVert_z->Draw();
  h_resVert_z->Write();

  removeFlows(h_scoutVert_dBV);
  h_scoutVert_dBV->Draw();
  h_scoutVert_dBV->Write();

  removeFlows(h_scoutVert_phi);
  h_scoutVert_phi->Draw();
  h_scoutVert_phi->Write();

  removeFlows(h_scoutVert_z);
  h_scoutVert_z->Draw();
  h_scoutVert_z->Write();

  h_scoutVert_x_y->Draw();
  h_scoutVert_x_y->Write();

  removeFlows(h_scoutVert_nTracks);
  h_scoutVert_nTracks->Draw();
  h_scoutVert_nTracks->Write();

  removeFlows(h_scoutVert_dPhi);
  h_scoutVert_dPhi->Draw();
  h_scoutVert_dPhi->Write();

  removeFlows(h_scoutVert_dVV);
  h_scoutVert_dVV->Draw();
  h_scoutVert_dVV->Write();

  removeFlows(h_scoutVert_nVertices);
  h_scoutVert_nVertices->Draw();
  h_scoutVert_nVertices->Write();
  
  delete scoutTrack_pt;
  delete scoutTrack_eta;
  delete scoutTrack_phi;
  delete scoutTrack_phiBeamspot;
  delete scoutTrack_reducedChi2;
  delete scoutTrack_charge;
  delete scoutTrack_dxy;
  delete scoutTrack_dxyErr;
  delete scoutTrack_dxySig;
  delete scoutTrack_dxySigned;
  delete scoutTrack_d3D;
  delete scoutTrack_d3DErr;
  delete scoutTrack_d3DSig;
  delete scoutTrack_dz;
  delete scoutTrack_dzErr;
  delete scoutTrack_dzSig;
  delete scoutTrack_dszUncertainty;
  delete scoutTrack_dxyUncertainty;
  delete scoutTrack_dszdxyCovariance;
  delete scoutTrack_vx;
  delete scoutTrack_vy;
  delete scoutTrack_iJet;
  delete scoutTrack_nValidPixelHits;
  delete scoutTrack_nTrackerLayersWithMeasurement;
  delete scoutTrack_nValidStripHits;
  delete scoutTrack_nMissingInnerHits;
  delete scoutTrack_minPVDxy;
  delete scoutTrack_minPVDz;

  delete vertTrack_pt;
  delete vertTrack_eta;
  delete vertTrack_phi;
  delete vertTrack_reducedChi2;
  delete vertTrack_charge;
  delete vertTrack_dxy;
  delete vertTrack_dxyErr;
  delete vertTrack_dxySig;
  delete vertTrack_dxySigned;
  delete vertTrack_d3D;
  delete vertTrack_d3DErr;
  delete vertTrack_d3DSig;
  delete vertTrack_dz;
  delete vertTrack_dzErr;
  delete vertTrack_dzSig;
  delete vertTrack_nValidPixelHits;
  delete vertTrack_nTrackerLayersWithMeasurement;
  delete vertTrack_nValidStripHits;
  delete vertTrack_nMissingInnerHits;
  delete vertTrack_iVtx;
  delete vertTrack_iJet;
  delete vertTrack_hasPFMatch;

  delete reco_dpt_diff;
  delete reco_deta_diff;
  delete reco_dphi_diff;
  delete reco_dxy_diff;
  delete reco_dchi2_diff; 
  
  delete match_ptRatio;
  delete match_deltaR;
  delete match_diffPt;
  delete match_diffEta;
  delete match_diffPhi;
  delete match_diffPhiCorrected;
  delete match_gen_dxy;
  delete match_gen_dxyCorrected;
  delete match_diffDxy;
  delete match_diffDxyCorrected;
  delete gen_dxy;
  delete gen_dxyCorrected;
  delete match_vert_x;
  delete match_vert_y;
  delete match_genVert_x;
  delete match_genVert_y;
  delete match_genVert_dBV;
  delete genVert_dBV;
  delete genVert_phi;
  delete genVert_z;
  delete genVert_x;
  delete genVert_y;
  delete genVert_nParticles;
  delete genVert_dPhi;
  delete genVert_dVV;
  delete resVert_x;
  delete resVert_y;
  delete resVert_z;
  delete scoutVert_dBV;
  delete scoutVert_dBVErr;
  delete scoutVert_dPVV;
  delete scoutVert_dPVVErr;
  delete scoutVert_phi;
  delete scoutVert_z;
  delete scoutVert_x;
  delete scoutVert_y;
  delete scoutVert_nTracks;
  delete scoutVert_chi2;
  delete scoutVert_dPhi;
  delete scoutVert_dVV;
  delete scoutVert_dT;
  delete scoutVert_cosT;
  delete scoutVert_pMag;
  delete scoutVert_costh2;
  delete scoutVert_ctau;
  delete scoutVert_pt;
  delete scoutVert_mass;
  
  delete jet_pt;
  delete jet_eta;
  delete jet_phi;
  delete jet_mass;
  delete jet_energy;
  delete jet_chHEF;
  delete jet_neHEF;
  delete jet_muonEF;
  delete jet_chEmEF;
  delete jet_neEmEF;
  delete jet_hfHEF;
  delete jet_hfEmEF;
  delete jet_hoEF;
  delete jet_chMultiplicity;
  delete jet_neMultiplicity;
  delete jet_passJetIdTight;

  delete genJet_pt;
  delete genJet_eta;
  delete genJet_phi;
  delete genJet_mass;
  delete genJet_energy;
  delete genJet_nConstituents;

  delete muon_pt;
  delete muon_eta;
  delete muon_phi;
  delete muon_chi2;
  delete muon_nTrackerLayersWithMeasurement;
  delete muon_nValidPixelHits;
  delete muon_nValidRecoMuonHits;
  delete muon_nRecoMuonMatchedStations;
  delete muon_trackIso;
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void K0TreeMakerRun3::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);

  //Specify that only 'tracks' is allowed
  //To use, remove the default given above and uncomment below
  //ParameterSetDescription desc;
  //desc.addUntracked<edm::InputTag>("tracks","ctfWithMaterialTracks");
  //descriptions.addWithDefaultLabel(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(K0TreeMakerRun3);
