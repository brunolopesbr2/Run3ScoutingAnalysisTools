// -*- C++ -*-
//
// Package:    Run3ScoutingAnalysisTools/EventSkim
// Class:      K0Filter
//
/**\class K0Filter  Run3ScoutingAnalysisTools/EventSkim/plugins/K0Filter.cc

   Description: [one line class summary]
                                                                
   Implementation:
   [Notes on implementation]
*/

// system include files
#include <memory>
#include <iostream>
#include <TTree.h>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDFilter.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"

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
#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/HLTReco/interface/TriggerEvent.h"
#include "DataFormats/Scouting/interface/Run3ScoutingPFJet.h"
#include "DataFormats/Scouting/interface/Run3ScoutingMuon.h"
#include "DataFormats/Scouting/interface/Run3ScoutingParticle.h"
#include "SimDataFormats/GeneratorProducts/interface/HepMCProduct.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "SimDataFormats/GeneratorProducts/interface/GenRunInfoProduct.h"
#include "TH1.h"
#include "TH2.h"
#include "TMath.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"
#include "correction.h"
#include "CondFormats/DataRecord/interface/BeamSpotOnlineHLTObjectsRcd.h"
#include "CondFormats/BeamSpotObjects/interface/BeamSpotObjects.h"
#include "CondFormats/BeamSpotObjects/interface/BeamSpotOnlineObjects.h"
#include "TrackingTools/IPTools/interface/IPTools.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
//
// class declaration
//

class K0Filter : public edm::one::EDFilter<edm::one::SharedResources, edm::one::WatchRuns> {
   public:
      explicit K0Filter(const edm::ParameterSet&);
      ~K0Filter();
  
      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual bool filter(edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() ;
      
      //virtual bool beginRun(edm::Run&, edm::EventSetup const&);
      void beginRun(edm::Run const&, edm::EventSetup const&) override;
      void endRun(edm::Run const&, edm::EventSetup const&) override;
      virtual bool beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual bool endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
  
      // ----------member data ---------------------------
      const edm::EDGetTokenT<std::vector<reco::PFJet> >  pfjetsToken;
      const edm::EDGetTokenT<std::vector<pat::Jet> >  patjetsToken;
      const edm::EDGetTokenT<GenEventInfoProduct> GeneratorToken_;
      const edm::EDGetTokenT<std::vector<reco::GenJet>> GenJetToken_;
      const edm::EDGetTokenT<edm::TriggerResults> triggerResultsToken;

      double luminosity;
      double crossSection;
      const edm::EDGetTokenT<std::vector<PileupSummaryInfo>> truePileupToken;
      int truePU;
      std::vector<double> PUCorrectionArray;
      edm::InputTag algInputTag_;
      edm::InputTag extInputTag_;
      edm::EDGetToken algToken_;
      std::unique_ptr<l1t::L1TGlobalUtil> l1GtUtils_;
      std::vector<std::string>     l1Seeds_;
      bool isScouting;
      bool isMC;
      bool storeGenJets;
      TH2F* jetVetoMap_;
      TH1D* h_genWeights;
      TH1D* h_weights;
      TH1D* h_weightsSquared;
      TH1D* h_weights_LUMCorrected;
      TH1D* h_weightsSquared_LUMCorrected;

      TTree* tree;
      std::vector<float>* genJet_pt;
      std::vector<float>* genJet_eta;
      std::vector<float>* genJet_phi;
      std::vector<float>* genJet_mass;
      std::vector<float>* genJet_energy;
      std::vector<int>* genJet_nConstituents;
      float genHT;
      int nGenJets;

      const edm::EDGetTokenT<Run3ScoutingParticleCollection> scoutingParticle_collection_token_;
      const edm::EDGetTokenT<std::vector<Run3ScoutingMuon> >      muonsToken;
      const edm::ESGetToken<BeamSpotOnlineObjects, BeamSpotOnlineHLTObjectsRcd> bsOnlineToken_;
      const edm::ESGetToken<TransientTrackBuilder, TransientTrackRecord> token_builder;
      /*
      std::vector<double> triggerNominal;
      std::vector<double> triggerUp;
      std::vector<double> triggerDown;
      std::vector<double> triggerEdge;
      */
  bool matchesPF(int ID, double tolerance, Run3ScoutingMuon const& muonTrack,  edm::Handle<std::vector<Run3ScoutingParticle>> const& scoutingParticleH){

    bool matches = false;

    float mu_eta = muonTrack.eta();
    float mu_phi = muonTrack.phi();

    double dEta;
    double dPhi;
    double dR;

    for (size_t pf_index = 0; pf_index < scoutingParticleH->size(); pf_index++) {
      auto & scoutingPFCandidate = scoutingParticleH->at(pf_index);
      if (abs(scoutingPFCandidate.pdgId()) != 13){
	continue;
      }
      float pf_eta = scoutingPFCandidate.eta();
      float pf_phi = scoutingPFCandidate.phi();
      
      dEta = mu_eta - pf_eta;
      dPhi = deltaPhi(mu_phi, pf_phi);
      dR = sqrt(pow(dEta, 2) + pow(dPhi, 2));
      
      if(dR < tolerance){
	matches = true;
	return matches;
      }
    }
    return matches;
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
K0Filter::K0Filter(const edm::ParameterSet& iConfig):
  pfjetsToken(consumes<std::vector<reco::PFJet> >(iConfig.getParameter<edm::InputTag>("pfjets"))),
  patjetsToken(consumes<std::vector<pat::Jet> >(iConfig.getParameter<edm::InputTag>("patjets"))),
  GeneratorToken_(consumes(iConfig.getParameter<edm::InputTag>("generatorName"))),
  GenJetToken_(consumes(iConfig.getParameter<edm::InputTag>("genJet_src"))),
  triggerResultsToken(consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("triggerresults"))),
  luminosity(iConfig.existsAs<double>("luminosity") ? iConfig.getParameter<double>  ("luminosity") : 1.0),
  crossSection(iConfig.existsAs<double>("crossSection") ? iConfig.getParameter<double>  ("crossSection") : 1.0),
  truePileupToken(consumes<std::vector<PileupSummaryInfo>>(iConfig.getParameter<edm::InputTag>("truePileup"))),
  PUCorrectionArray(iConfig.getParameter<std::vector<double>>("PUCorrectionArray")),
  isScouting(iConfig.existsAs<bool>("isScouting") ? iConfig.getParameter<bool>  ("isScouting") : false),
  isMC(iConfig.existsAs<bool>("isMC") ?  iConfig.getParameter<bool>  ("isMC") : false),
  storeGenJets(iConfig.existsAs<bool>("storeGenJets") ? iConfig.getParameter<bool>  ("storeGenJets") : false),
  scoutingParticle_collection_token_(consumes(iConfig.getParameter<edm::InputTag>("scoutingParticle"))),
  muonsToken(consumes<std::vector<Run3ScoutingMuon> > (iConfig.getParameter<edm::InputTag>("muons"))),
  bsOnlineToken_(esConsumes<BeamSpotOnlineObjects, BeamSpotOnlineHLTObjectsRcd>()),
  token_builder(esConsumes(edm::ESInputTag("", "TransientTrackBuilder")))
  //triggerNominal(iConfig.getParameter<std::vector<double>>("triggerNominal")),
  //triggerUp(iConfig.getParameter<std::vector<double>>("triggerUp")),
  //triggerDown(iConfig.getParameter<std::vector<double>>("triggerDown")),
  //triggerEdge(iConfig.getParameter<std::vector<double>>("triggerEdge"))
{
  usesResource("TFileService");
  algInputTag_ = iConfig.getParameter<edm::InputTag>("AlgInputTag");
  extInputTag_ = iConfig.getParameter<edm::InputTag>("l1tExtBlkInputTag");
  algToken_ = consumes<BXVector<GlobalAlgBlk>>(algInputTag_);
  l1Seeds_ = iConfig.getParameter<std::vector<std::string> >("l1Seeds");
  l1GtUtils_ = std::make_unique<l1t::L1TGlobalUtil>(iConfig, consumesCollector(), *this, algInputTag_, extInputTag_, l1t::UseEventSetupIn::RunAndEvent);
  if(isScouting){
    produces<std::vector<reco::PFJet>>("pfjets");
    produces<std::vector<Run3ScoutingMuon>>("muons");
  }
  else{
    produces<std::vector<pat::Jet>>("patjets");
  }
  if(isMC) produces<std::map<std::string, float>>("weightMap");
}


K0Filter::~K0Filter()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called on each new Event  ------------
bool
K0Filter::filter(edm::Event& iEvent, const edm::EventSetup& iSetup)
{

  using namespace edm;
  using namespace std;
  using correction::CorrectionSet;
  
  bool passFilter = true;
  
  double genWeight;
  double theWeight;
  
  genJet_pt->clear();
  genJet_eta->clear();
  genJet_phi->clear();
  genJet_mass->clear();
  genJet_energy->clear();
  genJet_nConstituents->clear();

  //Get the Transient Track Builder
  auto const &tt_builder = iSetup.getData(token_builder);
  
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
  
  int nPFJets = -1;
  //Get the jets
  Handle<vector<reco::PFJet> > pfjetsH;
  iEvent.getByToken(pfjetsToken, pfjetsH);
  std::unique_ptr<std::vector<reco::PFJet>> pfJetVector(new std::vector<reco::PFJet>());

  //Require 4 PF Jets
  if(pfjetsH.isValid() && isScouting){
    for (auto jets_iter = pfjetsH->begin(); jets_iter != pfjetsH->end(); ++jets_iter) {
      float Jet_eta = jets_iter->eta();
      float Jet_pt = jets_iter->pt();
      if((Jet_pt > 30) && (abs(Jet_eta) < 2.5)){
        int binX = jetVetoMap_->GetXaxis()->FindBin(Jet_eta);
        int binY = jetVetoMap_->GetYaxis()->FindBin(jets_iter->phi());
        float maskBit = jetVetoMap_->GetBinContent(binX, binY);

        float energy = TMath::Sqrt(pow(TMath::CosH(Jet_eta)*jets_iter->pt(),2)+pow(jets_iter->mass(),2));
        float Jet_chHEF = jets_iter->chargedHadronEnergy()/energy;
        float Jet_neHEF = jets_iter->neutralHadronEnergy()/energy;
        float Jet_muEF = jets_iter->muonEnergy()/energy;
        float Jet_chEmEF = jets_iter->electronEnergy()/energy;
        float Jet_neEmEF = (jets_iter->photonEnergy()+jets_iter->HFEMEnergy())/energy;
        int Jet_chMultiplicity = jets_iter->chargedHadronMultiplicity()+jets_iter->electronMultiplicity()+jets_iter->muonMultiplicity();
        int Jet_neMultiplicity = jets_iter->neutralHadronMultiplicity()+jets_iter->photonMultiplicity()+jets_iter->HFHadronMultiplicity()+jets_iter->HFEMMultiplicity();
        bool Jet_passJetIdTight = false;

        if (abs(Jet_eta) <= 2.6)
          Jet_passJetIdTight = (Jet_neHEF < 0.99) && (Jet_neEmEF < 0.9) && (Jet_chMultiplicity+Jet_neMultiplicity > 1) && (Jet_chHEF > 0.01) && (Jet_chMultiplicity > 0);
        else if (abs(Jet_eta) > 2.6 && abs(Jet_eta) <= 2.7)
          Jet_passJetIdTight = (Jet_neHEF < 0.90) && (Jet_neEmEF < 0.99);
        else if (abs(Jet_eta) > 2.7 && abs(Jet_eta) <= 3.0)
          Jet_passJetIdTight = (Jet_neHEF < 0.99);
        else if (abs(Jet_eta) > 3.0)
          Jet_passJetIdTight = (Jet_neMultiplicity >= 2) && (Jet_neEmEF < 0.4);

        bool Jet_passJetIdTightLepVeto = false;
        if (abs(Jet_eta) <= 2.7)
          Jet_passJetIdTightLepVeto = Jet_passJetIdTight && (Jet_muEF < 0.8) && (Jet_chEmEF < 0.8);
        else
          Jet_passJetIdTightLepVeto = Jet_passJetIdTight;
        
        if((maskBit==0) && Jet_passJetIdTightLepVeto && ((Jet_chEmEF+Jet_neEmEF)<0.9) ){
          pfJetVector->emplace_back(*jets_iter);
        }
      }
    }
    nPFJets = pfJetVector->size();
  }
  
  Handle<std::vector<Run3ScoutingMuon> > muonsH;
  iEvent.getByToken(muonsToken, muonsH);
  std::unique_ptr<std::vector<Run3ScoutingMuon>> muonVector(new std::vector<Run3ScoutingMuon>());
  
  //Get scouting particle flow candidates
  Handle<Run3ScoutingParticleCollection> scoutingParticle_collection_handle;
  iEvent.getByToken(scoutingParticle_collection_token_, scoutingParticle_collection_handle);

  //select muons to require isolation from jets to get ht
  //std::vector<const Run3ScoutingMuon*> selectedMuons;
  //selectedMuons.clear(); //just to be sure

  bool isPFMuon;

  for (auto muons_iter = muonsH->begin(); muons_iter != muonsH->end(); ++muons_iter) {
    if (muons_iter->pt() > 20 &&
        abs(muons_iter->eta()) < 2.4 &&
        muons_iter->normalizedChi2() < 10 &&
        muons_iter->nTrackerLayersWithMeasurement() > 5 &&
        muons_iter->nValidPixelHits() > 0 &&
        muons_iter->nValidRecoMuonHits() > 0 &&
        muons_iter->nRecoMuonMatchedStations() > 1 &&
	muons_iter->trackIso() < 0.1) 
    {
      isPFMuon = matchesPF(13, 0.1, *muons_iter, scoutingParticle_collection_handle);
      if (isPFMuon){
	float chi2 = muons_iter->trk_chi2();
	float ndof = muons_iter->trk_ndof();
	reco::TrackBase::Point referencePoint(muons_iter->trk_vx(), muons_iter->trk_vy(), muons_iter->trk_vz());
	float px = muons_iter->trk_pt() * cos(muons_iter->trk_phi());
	float py = muons_iter->trk_pt() * sin(muons_iter->trk_phi());
	float pz = muons_iter->trk_pt() * sinh(muons_iter->trk_eta());
	reco::TrackBase::Vector momentum(px, py, pz);
	int charge = muons_iter->charge();
	std::vector<float> cov_vec(15);
	cov_vec[0] = muons_iter->trk_qoverpError() * muons_iter->trk_qoverpError(); // cov(0, 0)
	cov_vec[1] = muons_iter->trk_qoverp_lambda_cov(); // cov(0, 1)
	cov_vec[3] = muons_iter->trk_qoverp_phi_cov(); // cov(0, 2)
	cov_vec[6] = muons_iter->trk_qoverp_dxy_cov(); // cov(0, 3)
	cov_vec[10] = muons_iter->trk_qoverp_dsz_cov(); // cov(0, 4)
	cov_vec[2] = muons_iter->trk_lambdaError() * muons_iter->trk_lambdaError(); // cov(1, 1)
	cov_vec[4] = muons_iter->trk_lambda_phi_cov(); // cov(1, 2)
	cov_vec[7] = muons_iter->trk_lambda_dxy_cov(); // cov(1, 3)
	cov_vec[11] = muons_iter->trk_lambda_dsz_cov(); // cov(1, 4)
	cov_vec[5] = muons_iter->trk_phiError() * muons_iter->trk_phiError(); // cov(2, 2)
	cov_vec[8] = muons_iter->trk_phi_dxy_cov(); // cov(2, 3)
	cov_vec[12] = muons_iter->trk_phi_dsz_cov(); // cov(2, 4)
	cov_vec[9] = muons_iter->trk_dxyError() * muons_iter->trk_dxyError(); // cov(3, 3)
	cov_vec[13] = muons_iter->trk_dxy_dsz_cov(); // cov(3, 4)
	cov_vec[14] = muons_iter->trk_dszError() * muons_iter->trk_dszError(); // cov(4, 4)
	reco::TrackBase::CovarianceMatrix cov(cov_vec.begin(), cov_vec.end());
	reco::TrackBase::TrackAlgorithm algo(reco::TrackBase::undefAlgorithm); // undefined
	reco::TrackBase::TrackQuality quality(reco::TrackBase::confirmed); // confirmed
	reco::Track recoTrack(chi2, ndof, referencePoint, momentum, charge, cov, algo, quality);
	reco::TransientTrack transientTrack = tt_builder.build(recoTrack);
	std::pair<bool, Measurement1D> ttk_transverseDist = IPTools::absoluteTransverseImpactParameter(transientTrack, fake_bs_vtx);
	float dxybs = ttk_transverseDist.second.value();
	float dz = abs(recoTrack.dz(beamspot->position()));
	if((dxybs<0.02) && (dz<0.5)){
	  muonVector->emplace_back(*muons_iter);
	}
      }
    }
  }
  int nSelMuons = muonVector->size();
  
  /*
  float ht_corrected = 0;
  int imuon = 0;

  float dEta_jet_mu;
  float dPhi_jet_mu;
  float dR_jet_mu;

  for (const auto& jet: *pfJetVector) {
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
  // get trigger weights

  // Find the bin index: first edge that is >= ht_corrected
  auto it = std::lower_bound(triggerEdge.begin(), triggerEdge.end(), ht_corrected);
  int idx = std::distance(triggerEdge.begin(), it);

  // Clamp to valid range
  idx = std::min(idx, (int)triggerNominal.size() - 1);

  float weight_trigger_nominal = triggerNominal[idx];
  float weight_trigger_up = triggerUp[idx];
  float weight_trigger_down = triggerDown[idx];
  */
  std::string pileupCorrectionList[] = {"BCDEFGHI","C","D","E","F","G","H","I"};
  std::string pileupVariationList[] = {"nominal","up","down"};
  std::unique_ptr<std::map<std::string, float>> weightMap(new std::map<std::string, float>());
  if(isMC){
    edm::Handle<GenEventInfoProduct> generatorHandle;
    iEvent.getByToken(GeneratorToken_, generatorHandle);
    genWeight = generatorHandle->weight();
    h_genWeights->Fill("None",genWeight);
    theWeight = genWeight*luminosity*crossSection;
    
    edm::Handle<std::vector<PileupSummaryInfo>> pileup;
    iEvent.getByToken(truePileupToken, pileup);
    std::vector<PileupSummaryInfo>::const_iterator pileupIter;
    for(pileupIter = pileup->begin(); pileupIter != pileup->end(); ++pileupIter){
      if (pileupIter->getBunchCrossing() == 0) {
	      truePU = pileupIter->getTrueNumInteractions();
      }
    }
    for(auto fileString: pileupCorrectionList){
      // Load the correction set from file
      std::string fileName = "/cvmfs/cms-griddata.cern.ch/cat/metadata/LUM/Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15/2025-12-02/puWeights_"+fileString+".json.gz";
      auto cset = CorrectionSet::from_file(fileName);
      auto corr = cset->at("Collisions24_"+fileString+"_goldenJSON");
      for(auto variationString: pileupVariationList){
        double w = corr->evaluate({float(truePU), variationString});
        (*weightMap)["PU_"+fileString+"_"+variationString] = w;
      }
    }
    //(*weightMap)["correctedNominal"] = theWeight * weight_trigger_nominal * weightMap->at("PU_BCDEFGHI_nominal");
    (*weightMap)["correctedNominal"] = theWeight * weightMap->at("PU_BCDEFGHI_nominal");
    //(*weightMap)["triggerNominal"] = weight_trigger_nominal;
    //(*weightMap)["triggerUp"] = weight_trigger_up;
    //(*weightMap)["triggerDown"] = weight_trigger_down;

    if(truePU>99) truePU = 99;
    theWeight *= PUCorrectionArray[truePU];

    h_weights->Fill("None",theWeight);
    h_weightsSquared->Fill("None",pow(theWeight,2));

    h_weights_LUMCorrected->Fill("None",weightMap->at("correctedNominal"));
    h_weightsSquared_LUMCorrected->Fill("None",pow(weightMap->at("correctedNominal"),2));
  }
  else{
    genWeight = 1;
    theWeight = 1;
    //weight_trigger_nominal = 1;
    //weight_trigger_up = 1;
    //weight_trigger_down = 1;

    
    //Just to get the number of events
    h_genWeights->Fill("None",genWeight);
    h_weights->Fill("None",theWeight);
    h_weightsSquared->Fill("None",pow(theWeight,2));
  }

  /*
  bool passTrigger;
  if(isScouting){
    l1GtUtils_->retrieveL1Event(iEvent,iSetup,algToken_);
    bool L1_HTT280er;
    bool L1_ETT2000;
    bool L1_SingleJet180;
    bool L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5;
    l1GtUtils_->getFinalDecisionByName(string("L1_HTT280er"), L1_HTT280er);
    l1GtUtils_->getFinalDecisionByName(string("L1_ETT2000"), L1_ETT2000);
    l1GtUtils_->getFinalDecisionByName(string("L1_SingleJet180"), L1_SingleJet180);
    l1GtUtils_->getFinalDecisionByName(string("L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5"), L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5);
    passTrigger = L1_HTT280er || L1_ETT2000 || L1_SingleJet180 || L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5;
  }
  */

  edm::Handle<edm::TriggerResults> triggerBits;
  iEvent.getByToken(triggerResultsToken, triggerBits);
  const edm::TriggerNames &names = iEvent.triggerNames(*triggerBits);
  bool HLT_FinalResult = false;
  for (unsigned int i = 0, n = triggerBits->size(); i < n; ++i) {
    std::string name = names.triggerName(i);
    if(name.find("DST_PFScouting_SingleMuon_v")!=std::string::npos){
      if(triggerBits->accept(i)) HLT_FinalResult = true;
    }
  }
  bool passTrigger = HLT_FinalResult; 

  passFilter = passFilter && passTrigger;
  if(passFilter){
    h_genWeights->Fill("Trigger",genWeight);
    h_weights->Fill("Trigger",theWeight);
    h_weightsSquared->Fill("Trigger",pow(theWeight,2));

    if(isMC){
      h_weights_LUMCorrected->Fill("Trigger",weightMap->at("correctedNominal"));
      h_weightsSquared_LUMCorrected->Fill("Trigger",pow(weightMap->at("correctedNominal"),2));
    }
  }

  //Get gen jets
  std::vector<reco::GenJet>::const_iterator genJetIter;
  edm::Handle<std::vector<reco::GenJet>> genJet_handle;
  if(isMC && storeGenJets){
    nGenJets = 0;
    genHT = 0;
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
  Handle<vector<pat::Jet> > patjetsH;
  iEvent.getByToken(patjetsToken, patjetsH);
  std::unique_ptr<std::vector<pat::Jet>> patJetVector(new std::vector<pat::Jet>());

  //Require 4 Pat Jets, only for MC
  if(isMC && patjetsH.isValid() && !isScouting){
    for (auto jets_iter = patjetsH->begin(); jets_iter != patjetsH->end(); ++jets_iter) {
      float Jet_eta = jets_iter->eta();
      float Jet_pt = jets_iter->pt();
      if((Jet_pt > 30) && (abs(Jet_eta) < 2.5)){
	int binX = jetVetoMap_->GetXaxis()->FindBin(Jet_eta);
        int binY = jetVetoMap_->GetYaxis()->FindBin(jets_iter->phi());
        float maskBit = jetVetoMap_->GetBinContent(binX, binY);

	if(maskBit==0){
	  patJetVector->emplace_back(*jets_iter);
	}
      }
    }
    nPFJets = patJetVector->size();  
  }
  passFilter = passFilter && (nPFJets>0);
  if(passFilter){
    h_genWeights->Fill("nJets",genWeight);
    h_weights->Fill("nJets",theWeight);
    h_weightsSquared->Fill("nJets",pow(theWeight,2));

    if(isMC){
      h_weights_LUMCorrected->Fill("nJets",weightMap->at("correctedNominal"));
      h_weightsSquared_LUMCorrected->Fill("nJets",pow(weightMap->at("correctedNominal"),2));
    }
  }
  passFilter = passFilter && (nSelMuons>0);
  if(passFilter){
    h_genWeights->Fill("nMuons",genWeight);
    h_weights->Fill("nMuons",theWeight);
    h_weightsSquared->Fill("nMuons",pow(theWeight,2));

    if(isMC){
      h_weights_LUMCorrected->Fill("nMuons",weightMap->at("correctedNominal"));
      h_weightsSquared_LUMCorrected->Fill("nMuons",pow(weightMap->at("correctedNominal"),2));
    }
  }
  
  
  if(isScouting){
    iEvent.put(std::move(pfJetVector),"pfjets");
    iEvent.put(std::move(muonVector),"muons");
  }
  else{
    iEvent.put(std::move(patJetVector),"patjets");
  }
  if(isMC) iEvent.put(std::move(weightMap),"weightMap");
  tree->Fill();
  return passFilter;
}

// ------------ method called once each job just before starting event loop  ------------
void 
K0Filter::beginJob()
{
  edm::Service<TFileService> fs;
  h_genWeights = fs->make<TH1D>("genWeightsSkim",";Cut Applied; Sum of Gen Weights",4,0,4);
  h_genWeights->GetXaxis()->SetBinLabel(1,"None");
  h_genWeights->GetXaxis()->SetBinLabel(2,"Trigger");
  h_genWeights->GetXaxis()->SetBinLabel(3,"nJets");
  h_genWeights->GetXaxis()->SetBinLabel(4,"nMuons");
  
  h_weights = fs->make<TH1D>("weightsSkim",";Cut Applied; Sum of Weights",4,0,4);
  h_weights->GetXaxis()->SetBinLabel(1,"None");
  h_weights->GetXaxis()->SetBinLabel(2,"Trigger");
  h_weights->GetXaxis()->SetBinLabel(3,"nJets");
  h_weights->GetXaxis()->SetBinLabel(4,"nMuons");

  h_weights_LUMCorrected = fs->make<TH1D>("weightsSkimLUMCorrected",";Cut Applied; Sum of Weights",4,0,4);
  h_weights_LUMCorrected->GetXaxis()->SetBinLabel(1,"None");
  h_weights_LUMCorrected->GetXaxis()->SetBinLabel(2,"Trigger");
  h_weights_LUMCorrected->GetXaxis()->SetBinLabel(3,"nJets");
  h_weights_LUMCorrected->GetXaxis()->SetBinLabel(4,"nMuons");
  
  h_weightsSquared = fs->make<TH1D>("weightsSquaredSkim",";Cut Applied; Sum of Squared Weights",4,0,4);
  h_weightsSquared->GetXaxis()->SetBinLabel(1,"None");
  h_weightsSquared->GetXaxis()->SetBinLabel(2,"Trigger");
  h_weightsSquared->GetXaxis()->SetBinLabel(3,"nJets");
  h_weightsSquared->GetXaxis()->SetBinLabel(4,"nMuons");

  h_weightsSquared_LUMCorrected = fs->make<TH1D>("weightsSquaredSkimLUMCorrected",";Cut Applied; Sum of Squared Weights",4,0,4);
  h_weightsSquared_LUMCorrected->GetXaxis()->SetBinLabel(1,"None");
  h_weightsSquared_LUMCorrected->GetXaxis()->SetBinLabel(2,"Trigger");
  h_weightsSquared_LUMCorrected->GetXaxis()->SetBinLabel(3,"nJets");
  h_weightsSquared_LUMCorrected->GetXaxis()->SetBinLabel(4,"nMuons");

  TFile* vetoFile = TFile::Open("Summer24Prompt24_RunBCDEFGHI.root", "READ");
  jetVetoMap_ = (TH2F*)vetoFile->Get("jetvetomap");

  tree = fs->make<TTree>("filterTree","filterTree");
  
  genJet_pt = new std::vector<float>;
  genJet_eta = new std::vector<float>;
  genJet_phi = new std::vector<float>;
  genJet_mass = new std::vector<float>;
  genJet_energy = new std::vector<float>;
  genJet_nConstituents = new std::vector<int>;

  if(storeGenJets){
    tree->Branch("genJet_pt",&genJet_pt);
    tree->Branch("genJet_eta",&genJet_eta);
    tree->Branch("genJet_phi",&genJet_phi);
    tree->Branch("genJet_mass",&genJet_mass);
    tree->Branch("genJet_energy",&genJet_energy);
    tree->Branch("genJet_nConstituents",&genJet_nConstituents);
    tree->Branch("nGenJets", &nGenJets, "nGenJets/I");
    tree->Branch("genHT", &genHT, "genHT/F");
  }
}

// ------------ method called once each job just after ending the event loop  ------------
void 
K0Filter::endJob() {
  h_genWeights->GetDirectory()->cd();
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

  tree->GetDirectory()->cd();
  
  delete genJet_pt;
  delete genJet_eta;
  delete genJet_phi;
  delete genJet_mass;
  delete genJet_energy;
  delete genJet_nConstituents;
}

// ------------ method called when starting to processes a run  ------------
void 
K0Filter::beginRun(edm::Run const& iRun, edm::EventSetup const& iSetup)
{
  
  l1GtUtils_->retrieveL1Setup(iSetup);
  
}

// ------------ method called when ending the processing of a run  ------------
void 
K0Filter::endRun(edm::Run const&, edm::EventSetup const&)
{
  
}

// ------------ method called when starting to processes a luminosity block  ------------
bool 
K0Filter::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
  return true;
}

// ------------ method called when ending the processing of a luminosity block  ------------
bool 
K0Filter::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
  return true;
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
K0Filter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}
//define this as a plug-in
DEFINE_FWK_MODULE(K0Filter);
