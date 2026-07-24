// -*- C++ -*-
//
// Package:    Run3ScoutingAnalysisTools/TriggerEffs
// Class:      TriggerEffs
//
/**\class TriggerEffs TriggerEffs.cc Run3ScoutingAnalysisTools/TriggerEffs/plugins/TriggerEffs.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Bruno Lopes
//         Created:  Tue, 09 Sep 2025 16:54:35 GMT
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

#include "DataFormats/Math/interface/deltaPhi.h"

#include "L1Trigger/L1TGlobal/interface/L1TGlobalUtil.h"
#include "DataFormats/L1TGlobal/interface/GlobalAlgBlk.h"
#include "DataFormats/L1Trigger/interface/BXVector.h"
#include "DataFormats/L1Trigger/interface/EtSum.h"

#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"
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

class TriggerEffs : public edm::one::EDAnalyzer<edm::one::SharedResources> {
public:
  explicit TriggerEffs(const edm::ParameterSet&);
  ~TriggerEffs() override;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void beginJob() override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  void endJob() override;

  // ----------member data ---------------------------
  const edm::EDGetTokenT<std::vector<reco::PFJet> >  pfjetsToken;
  const edm::EDGetTokenT<std::vector<pat::Jet> >  offlineJetsToken;
  const edm::EDGetTokenT<GenEventInfoProduct> GeneratorToken_;
  const edm::EDGetTokenT<edm::TriggerResults> triggerResultsToken;

  std::vector<std::string> triggerPathsVector;
  std::map<std::string, int> triggerPathsMap;

  float genWeight;
  float theWeight;
  float luminosity;
  float crossSection;

  triggerExpression::Data triggerCache_;

  edm::InputTag                algInputTag_;
  edm::InputTag                extInputTag_;
  edm::EDGetToken              algToken_;
  std::unique_ptr<l1t::L1TGlobalUtil> l1GtUtils_;
  std::vector<std::string>     l1Seeds_;
  const edm::EDGetTokenT<BXVector<l1t::EtSum>> L1etSum;

  bool isMC;
  bool hasReco;
  TTree* objectTree;

  int nPFJets;

  int nPFJets_corrected;
  float hltHT;

  float l1HT;
  float offlineHT;


  bool L1_HTT280er;
  bool L1_ETT2000;
  bool L1_SingleJet180;
  bool L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5;

  const edm::EDGetTokenT<std::vector<PileupSummaryInfo>> truePileupToken;

  const edm::EDGetTokenT<std::vector<Run3ScoutingMuon>> muonsToken;
  const edm::EDGetTokenT<std::vector<Run3ScoutingParticle>> scoutingParticle_collection_token_;
  double muon_pt;
  double muon_eta;
  double muon_chi2;
  int muon_trackLayers;
  int muon_pixelHits;
  int muon_muonHits;
  int muon_matchedStation;

  double matchTolerance;
  double muon_iso;
  double muon_iso_max;

  int observedPU;
  int truePU;

  int nMuons;
  int nSelectedMuons;

  int nPFMuons;

  double mu1s_pt;
  double mu1s_eta;
  double mu1s_chi2;
  int mu1s_trackLayers;
  int mu1s_pixelHits;
  int mu1s_muonHits;
  int mu1s_matchedStation;

  bool passHTTrigger;
  bool passMuonTrigger;

  bool muonIso;
  bool isPFMuon;

  std::vector<double> muonsIsoCustom;
  std::vector<double> muonsIsoDefault;
  std::vector<int> isPFMuons;

  bool offlineMuon;
  bool finalMuon;

  //variables for the jet veto
  TH2F* jetVetoMap_;
  float Jet_eta;
  float Jet_pt;
  float Jet_phi;
  int binX;
  int binY;
  float maskBit;
  float energy;
  float Jet_chHEF;
  float Jet_neHEF;
  float Jet_muEF;
  float Jet_chEmEF;
  float Jet_neEmEF;
  int Jet_chMultiplicity;
  int Jet_neMultiplicity;
  bool Jet_passJetIdTight;
  bool Jet_passJetIdTightLepVeto;
  float dEta_jet_mu;
  float dPhi_jet_mu;
  float dR_jet_mu;

  std::vector<float>* offlineJet_pt;
  std::vector<float>* offlineJet_eta;
  std::vector<float>* offlineJet_phi;

  std::vector<float>* onlineJet_pt;
  std::vector<float>* onlineJet_eta;
  std::vector<float>* onlineJet_phi;


  double MuonTrackIso(Run3ScoutingMuon const& muonTrack, edm::Handle<std::vector<Run3ScoutingParticle>> const& scoutingParticleH){

    double mu_pt = muonTrack.pt();
    double mu_eta = muonTrack.eta();
    double mu_phi = muonTrack.phi();

    double pf_pt = 0.0;
    double pf_eta;
    double pf_phi;

    double dEta;
    double dPhi;
    double dR;

    for (size_t pf_index = 0; pf_index < scoutingParticleH->size(); pf_index++) {
      auto & scoutingPFCandidate = scoutingParticleH->at(pf_index);

      pf_eta = scoutingPFCandidate.eta();
      pf_phi = scoutingPFCandidate.phi();
      
      dEta = mu_eta - pf_eta;
      dPhi = deltaPhi(mu_phi, pf_phi);
      dR = sqrt(pow(dEta, 2) + pow(dPhi, 2));

      if(abs(scoutingPFCandidate.pdgId()) != 13){
        if(dR < 0.3){
          pf_pt = pf_pt + scoutingPFCandidate.pt();
        }
      }
    }

    double iso = pf_pt / mu_pt;

    return iso;
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

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
TriggerEffs::TriggerEffs(const edm::ParameterSet& iConfig):
    pfjetsToken(consumes<std::vector<reco::PFJet> >(iConfig.getParameter<edm::InputTag>("pfjets"))),
    offlineJetsToken(consumes<std::vector<pat::Jet> >(iConfig.getParameter<edm::InputTag>("offlineJets"))),
    GeneratorToken_(consumes(iConfig.getParameter<edm::InputTag>("generatorName"))),
    triggerResultsToken(consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("triggerresults"))),
    luminosity(iConfig.existsAs<double>("luminosity") ? iConfig.getParameter<double>  ("luminosity") : 1.0),
    crossSection(iConfig.existsAs<double>("crossSection") ? iConfig.getParameter<double>  ("crossSection") : 1.0),
    algInputTag_(iConfig.getParameter<edm::InputTag>("AlgInputTag")),
    extInputTag_(iConfig.getParameter<edm::InputTag>("l1tExtBlkInputTag")), 
    algToken_(consumes<BXVector<GlobalAlgBlk>>(iConfig.getParameter<edm::InputTag>("AlgInputTag"))),
    l1Seeds_(iConfig.getParameter<std::vector<std::string>>("l1Seeds")),
    L1etSum(consumes<BXVector<l1t::EtSum>>(iConfig.getParameter<edm::InputTag>("l1Et"))),
    isMC(iConfig.existsAs<bool>("isMC") ?  iConfig.getParameter<bool>  ("isMC") : false),
    hasReco(iConfig.existsAs<bool>("hasReco") ?  iConfig.getParameter<bool>  ("hasReco") : false),
    truePileupToken(consumes<std::vector<PileupSummaryInfo>>(iConfig.getParameter<edm::InputTag>("truePileup"))),
    muonsToken(consumes<std::vector<Run3ScoutingMuon>>(iConfig.getParameter<edm::InputTag>("scoutingMuon"))),
    scoutingParticle_collection_token_(consumes(iConfig.getParameter<edm::InputTag>("scoutingParticle"))),
    muon_pt(iConfig.getParameter<double>("muon_pt")),
    muon_eta(iConfig.getParameter<double>("muon_eta")),
    muon_chi2(iConfig.getParameter<double>("muon_chi2")),
    muon_trackLayers(iConfig.getParameter<int>("muon_trackLayers")),
    muon_pixelHits(iConfig.getParameter<int>("muon_pixelHits")),
    muon_muonHits(iConfig.getParameter<int>("muon_muonHits")),
    muon_matchedStation(iConfig.getParameter<int>("muon_matchedStation")),
    matchTolerance(iConfig.getParameter<double>("matchingTolerance")),
    muon_iso_max(iConfig.getParameter<double>("muon_iso_max"))
    {
  //now do what ever initialization is needed
    usesResource("TFileService");

    algInputTag_ = iConfig.getParameter<edm::InputTag>("AlgInputTag");
    extInputTag_ = iConfig.getParameter<edm::InputTag>("l1tExtBlkInputTag");
    algToken_ = consumes<BXVector<GlobalAlgBlk>>(algInputTag_);
    l1Seeds_ = iConfig.getParameter<std::vector<std::string> >("l1Seeds");
    l1GtUtils_ = std::make_unique<l1t::L1TGlobalUtil>(iConfig, consumesCollector(), *this, algInputTag_, extInputTag_, l1t::UseEventSetupIn::Event);
    }

TriggerEffs::~TriggerEffs() {
  // do anything here that needs to be done at desctruction time
  // (e.g. close files, deallocate resources etc.)
  //
  // please remove this method altogether if it would be left empty
}

//
// member functions
//

// ------------ method called for each event  ------------
void TriggerEffs::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;
  using namespace std;
  using correction::CorrectionSet;

  offlineJet_pt->clear();
  offlineJet_eta->clear();
  offlineJet_phi->clear();
  onlineJet_pt->clear();
  onlineJet_eta->clear();
  onlineJet_phi->clear();

  if(isMC){
    edm::Handle<std::vector<PileupSummaryInfo>> pileup;
    iEvent.getByToken(truePileupToken, pileup);
    std::vector<PileupSummaryInfo>::const_iterator pileupIter;
    for(pileupIter = pileup->begin(); pileupIter != pileup->end(); ++pileupIter){
      if (pileupIter->getBunchCrossing() == 0) {
        truePU = pileupIter->getTrueNumInteractions();
      }
    }

    edm::Handle<GenEventInfoProduct> generatorHandle;
    iEvent.getByToken(GeneratorToken_, generatorHandle);
    genWeight = generatorHandle->weight();
    theWeight = genWeight*luminosity*crossSection;

    // Load the correction set from file
    std::string fileName = "/cvmfs/cms-griddata.cern.ch/cat/metadata/LUM/Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15/2025-12-02/puWeights_BCDEFGHI.json.gz";
    auto cset = CorrectionSet::from_file(fileName);
    auto corr = cset->at("Collisions24_BCDEFGHI_goldenJSON");
    double w = corr->evaluate({float(truePU), "nominal"});

    theWeight = theWeight * w; //PU corrected weight
  
  }

  else{
    genWeight = 1;
    theWeight = 1;
  }


  //L1 HT
  edm::Handle<BXVector<l1t::EtSum>> etSums;
  iEvent.getByToken(L1etSum, etSums);
  if (etSums.isValid()) {
      for (auto it = etSums->begin(0); it != etSums->end(0); ++it) {
          if (it->getType() == l1t::EtSum::kTotalHt) {
              l1HT = it->et();
              break;
          }
      }
  }

  //Offline objects
  edm::Handle<std::vector<pat::Jet>> offlineJets;
  iEvent.getByToken(offlineJetsToken, offlineJets);

  offlineHT = 0;
  if(offlineJets.isValid()){
    for (auto jets_iter = offlineJets->begin(); jets_iter != offlineJets->end(); ++jets_iter){
      if(jets_iter->pt() > 30 && abs(jets_iter->eta()) < 2.5){
        binX = jetVetoMap_->GetXaxis()->FindBin(jets_iter->eta());
        binY = jetVetoMap_->GetYaxis()->FindBin(jets_iter->phi());
        maskBit = jetVetoMap_->GetBinContent(binX, binY);

        float energy = jets_iter->chargedHadronEnergy() + jets_iter->neutralHadronEnergy() + jets_iter->muonEnergy() + jets_iter->electronEnergy() + jets_iter->photonEnergy() + jets_iter->HFEMEnergy();
        if(energy > 0){
          Jet_chHEF = jets_iter->chargedHadronEnergy()/energy;
          Jet_neHEF = jets_iter->neutralHadronEnergy()/energy;
          Jet_muEF = jets_iter->muonEnergy()/energy;
          Jet_chEmEF = jets_iter->electronEnergy()/energy;
          Jet_neEmEF = (jets_iter->photonEnergy()+jets_iter->HFEMEnergy())/energy;
          Jet_chMultiplicity = jets_iter->chargedHadronMultiplicity()+jets_iter->electronMultiplicity()+jets_iter->muonMultiplicity();
          Jet_neMultiplicity = jets_iter->neutralHadronMultiplicity()+jets_iter->photonMultiplicity()+jets_iter->HFHadronMultiplicity()+jets_iter->HFEMMultiplicity();

          Jet_passJetIdTight = (Jet_neHEF < 0.99) && (Jet_neEmEF < 0.9) && (Jet_chMultiplicity+Jet_neMultiplicity > 1) && (Jet_chHEF > 0.01) && (Jet_chMultiplicity > 0);
          Jet_passJetIdTightLepVeto = Jet_passJetIdTight && (Jet_muEF < 0.8) && (Jet_chEmEF < 0.8);
          
          if((maskBit==0) && Jet_passJetIdTightLepVeto && ((Jet_chEmEF+Jet_neEmEF)<0.9) ){
            offlineHT = offlineHT + jets_iter->pt();

            offlineJet_pt->push_back(jets_iter->pt());
            offlineJet_eta->push_back(jets_iter->eta());
            offlineJet_phi->push_back(jets_iter->phi());
          }
        }
      }
    }
  }

  //Get the trigger bits for both HT L1 seeds and SingleMuon (DST_PFScouting_SingleMuon_v)
  l1GtUtils_->retrieveL1(iEvent,iSetup,algToken_);

  l1GtUtils_->getFinalDecisionByName(string("L1_HTT280er"), L1_HTT280er);
  l1GtUtils_->getFinalDecisionByName(string("L1_ETT2000"), L1_ETT2000);
  l1GtUtils_->getFinalDecisionByName(string("L1_SingleJet180"), L1_SingleJet180);
  l1GtUtils_->getFinalDecisionByName(string("L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5"), L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5);
  passHTTrigger = L1_HTT280er || L1_ETT2000 || L1_SingleJet180 || L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5;


  Handle<edm::TriggerResults> triggerBits;
  iEvent.getByToken(triggerResultsToken, triggerBits);
  const edm::TriggerNames &names = iEvent.triggerNames(*triggerBits);
  bool HLT_FinalResult = false;
  for (unsigned int i = 0, n = triggerBits->size(); i < n; ++i) {
    std::string name = names.triggerName(i);
    if((name.find("DST_PFScouting_SingleMuon_v")!=std::string::npos) ){
       if(triggerBits->accept(i)) HLT_FinalResult = true;
    }
  }
  passMuonTrigger = HLT_FinalResult;

  //Offline muon selection -- tight id, following Run 2 AN (until there are recommendations for 2024)
  Handle<vector<Run3ScoutingMuon> > muonsH;
  iEvent.getByToken(muonsToken, muonsH);
  // Temporary container for selected muons
  std::vector<const Run3ScoutingMuon*> orderedMuons;
  std::vector<const Run3ScoutingMuon*> selectedMuons;

  //Get scouting particle flow candidates
  edm::Handle<std::vector<Run3ScoutingParticle>> scoutingParticleH;
  iEvent.getByToken(scoutingParticle_collection_token_, scoutingParticleH);

  nPFMuons = 0;
  for (auto pfcands_iter = scoutingParticleH->begin(); pfcands_iter != scoutingParticleH->end(); ++pfcands_iter) {
    if (abs(pfcands_iter->pdgId()) == 13) nPFMuons++;
  }

  muonsIsoCustom.clear();
  muonsIsoDefault.clear();
  isPFMuons.clear();
  nMuons = 0;
  nSelectedMuons = 0;
  offlineMuon = false;

  for (auto muons_iter = muonsH->begin(); muons_iter != muonsH->end(); ++muons_iter) {
    nMuons++;
    orderedMuons.push_back(&(*muons_iter));

    muon_iso = MuonTrackIso(*muons_iter, scoutingParticleH);
    isPFMuon = matchesPF(13, matchTolerance, *muons_iter, scoutingParticleH);

    muonsIsoCustom.push_back(muon_iso);
    muonsIsoDefault.push_back(muons_iter->trackIso());
    isPFMuons.push_back(isPFMuon ? 1 : 0);

    if (muons_iter->pt() > muon_pt &&
        abs(muons_iter->eta()) < muon_eta &&
        muons_iter->normalizedChi2() < muon_chi2 &&
        muons_iter->nTrackerLayersWithMeasurement() > muon_trackLayers &&
        muons_iter->nValidPixelHits() > muon_pixelHits &&
        muons_iter->nValidRecoMuonHits() > muon_muonHits &&
        muons_iter->nRecoMuonMatchedStations() > muon_matchedStation &&
        muons_iter->trackIso() < muon_iso_max &&
        isPFMuon == true) 
    {
      offlineMuon = true;
      selectedMuons.push_back(&(*muons_iter));
      nSelectedMuons++;
    }
  }

  // Sort by pT
  if(orderedMuons.size() > 1){
    std::sort(orderedMuons.begin(), orderedMuons.end(),
              [](const Run3ScoutingMuon* a, const Run3ScoutingMuon* b){ return a->pt() > b->pt(); });
  }

    // Sort by pT
  if(selectedMuons.size() > 1){
    std::sort(selectedMuons.begin(), selectedMuons.end(),
              [](const Run3ScoutingMuon* a, const Run3ScoutingMuon* b){ return a->pt() > b->pt(); });
  }


  mu1s_pt = -100;
  mu1s_eta = -100;
  mu1s_chi2 = -100;
  mu1s_trackLayers = -100;
  mu1s_pixelHits = -100;
  mu1s_muonHits = -100;
  mu1s_matchedStation = -100;

  // Fill leading selected muon info if it exists
  if (selectedMuons.size() > 0) {
    const Run3ScoutingMuon* mu = selectedMuons[0];
    mu1s_pt = mu->pt();
    mu1s_eta = mu->eta();
    mu1s_chi2 = mu->normalizedChi2();
    mu1s_trackLayers = mu->nTrackerLayersWithMeasurement();
    mu1s_pixelHits = mu->nValidPixelHits();
    mu1s_muonHits = mu->nValidRecoMuonHits();
    mu1s_matchedStation = mu->nRecoMuonMatchedStations();
  }

  finalMuon = passMuonTrigger && offlineMuon;

    //Testing the jet requirements for the HT calculation

  Handle<vector<reco::PFJet> > pfjetsH;
  iEvent.getByToken(pfjetsToken, pfjetsH);
  std::vector<reco::PFJet> pfJetVector;

  hltHT = 0;
  if(pfjetsH.isValid()){
    for (auto jets_iter = pfjetsH->begin(); jets_iter != pfjetsH->end(); ++jets_iter) {
      if(jets_iter->pt() > 30 && abs(jets_iter->eta()) < 2.4){ //same requirements as L1_HTTer

        binX = jetVetoMap_->GetXaxis()->FindBin(jets_iter->eta());
        binY = jetVetoMap_->GetYaxis()->FindBin(jets_iter->phi());
        maskBit = jetVetoMap_->GetBinContent(binX, binY);
        float energy = jets_iter->chargedHadronEnergy() + jets_iter->neutralHadronEnergy() + jets_iter->muonEnergy() + jets_iter->electronEnergy() + jets_iter->photonEnergy() + jets_iter->HFEMEnergy();
        
        if(energy > 0){
          //float Jet_chHEF = jets_iter->chargedHadronEnergy()/energy;
          float Jet_neHEF = jets_iter->neutralHadronEnergy()/energy;
          float Jet_muEF = jets_iter->muonEnergy()/energy;
          float Jet_chEmEF = jets_iter->electronEnergy()/energy;
          float Jet_neEmEF = (jets_iter->photonEnergy()+jets_iter->HFEMEnergy())/energy;

          int Jet_chMultiplicity = jets_iter->chargedHadronMultiplicity()+jets_iter->electronMultiplicity()+jets_iter->muonMultiplicity();
          int Jet_neMultiplicity = jets_iter->neutralHadronMultiplicity()+jets_iter->photonMultiplicity()+jets_iter->HFHadronMultiplicity()+jets_iter->HFEMMultiplicity();

          Jet_passJetIdTight = (Jet_neHEF < 0.99) && (Jet_neEmEF < 0.90) && (Jet_chMultiplicity+Jet_neMultiplicity > 1) && (Jet_muEF < 0.80) && (Jet_chMultiplicity > 0);

          if((maskBit==0) && Jet_passJetIdTightLepVeto && ((Jet_chEmEF+Jet_neEmEF)<0.9) ){
            bool dR20 = true;
            
            for (auto muon : selectedMuons) {
                dEta_jet_mu = jets_iter->eta() - muon->eta();
                dPhi_jet_mu = deltaPhi(Jet_phi, muon->phi());
                dR_jet_mu = sqrt(pow(dEta_jet_mu, 2) + pow(dPhi_jet_mu, 2));
                if(dR_jet_mu < 0.20){
                  dR20 = false;
                } 
            }  
            if(dR20){
              hltHT = hltHT + jets_iter->pt();
              onlineJet_pt->push_back(jets_iter->pt());
              onlineJet_eta->push_back(jets_iter->eta());
              onlineJet_phi->push_back(jets_iter->phi());
            }
          }
        }
      }
    }
  }


  //std::cout<<"passMuonTrigger: "<< passMuonTrigger <<std::endl;
  //std::cout<<"offlineMuon: "<< offlineMuon <<std::endl;
  //std::cout<<"finalMuon: "<< finalMuon <<std::endl;

  objectTree->Fill();
}
// ------------ method called once each job just before starting event loop  ------------
void TriggerEffs::beginJob() {
  // please remove this method if not needed
  edm::Service<TFileService> fs;

  onlineJet_pt = new std::vector<float>;
  onlineJet_eta = new std::vector<float>;
  onlineJet_phi = new std::vector<float>;
  offlineJet_pt = new std::vector<float>;
  offlineJet_eta = new std::vector<float>;
  offlineJet_phi = new std::vector<float>;

  objectTree = fs->make<TTree>("objectTree","objectTree");

  TFile* vetoFile = TFile::Open("Summer24Prompt24_RunBCDEFGHI.root", "READ");
  jetVetoMap_ = (TH2F*)vetoFile->Get("jetvetomap");
  
  objectTree->Branch("genWeight",&genWeight, "genWeight/F" );
  objectTree->Branch("theWeight",&theWeight, "theWeight/F" );
  //PU corrected, no trigger weights
  
  objectTree->Branch("hltHT",&hltHT, "hltHT/F" );
  objectTree->Branch("l1HT",&l1HT, "l1HT/F" );
  objectTree->Branch("offlineHT",&offlineHT, "offlineHT/F" );

  //Offline and online jets
  objectTree->Branch("onlineJet_pt", &onlineJet_pt);
  objectTree->Branch("onlineJet_eta", &onlineJet_eta);
  objectTree->Branch("onlineJet_phi", &onlineJet_phi);
  objectTree->Branch("offlineJet_pt", &offlineJet_pt);
  objectTree->Branch("offlineJet_eta", &offlineJet_eta);
  objectTree->Branch("offlineJet_phi", &offlineJet_phi);


  objectTree->Branch("L1_HTT280er",&L1_HTT280er, "L1_HTT280er/O" );
  objectTree->Branch("L1_ETT2000",&L1_ETT2000, "L1_ETT2000/O" );
  objectTree->Branch("L1_SingleJet180",&L1_SingleJet180, "L1_SingleJet180/O" );
  objectTree->Branch("L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5",&L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5, "L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5/O" );

  objectTree->Branch("passHTTrigger",&passHTTrigger, "passHTTrigger/O" );
  objectTree->Branch("passMuonTrigger",&passMuonTrigger, "passMuonTrigger/O" );
  objectTree->Branch("offlineMuon",&offlineMuon, "offlineMuon/O" );
  objectTree->Branch("finalMuon",&finalMuon, "finalMuon/O" );


  objectTree->Branch("nMuons",&nMuons, "nMuons/I" );
  objectTree->Branch("nSelectedMuons",&nSelectedMuons, "nSelectedMuons/I" );

  //require one muon that satisfy the other cuts, leave leading muon pT free
  objectTree->Branch("mu1s_pt",&mu1s_pt, "mu1s_pt/D" );
  objectTree->Branch("mu1s_eta",&mu1s_eta, "mu1s_eta/D" );
  objectTree->Branch("mu1s_chi2",&mu1s_chi2, "mu1s_chi2/D" );
  objectTree->Branch("mu1s_trackLayers",&mu1s_trackLayers, "mu1s_trackLayers/I" );
  objectTree->Branch("mu1s_pixelHits",&mu1s_pixelHits, "mu1s_pixelHits/I" );
  objectTree->Branch("mu1s_muonHits",&mu1s_muonHits, "mu1s_muonHits/I" );
  objectTree->Branch("mu1s_matchedStation",&mu1s_matchedStation, "mu1s_matchedStation/I" );

  objectTree->Branch("nPFMuons",&nPFMuons, "nPFMuons/I" );
  objectTree->Branch("muonsIsoCustom", &muonsIsoCustom);
  objectTree->Branch("muonsIsoDefault", &muonsIsoDefault);
  objectTree->Branch("isPFMuons", &isPFMuons);

}

// ------------ method called once each job just after ending the event loop  ------------
void TriggerEffs::endJob() {
  // please remove this method if not needed
  delete onlineJet_pt;
  delete onlineJet_eta;
  delete onlineJet_phi;
  delete offlineJet_pt;
  delete offlineJet_eta;
  delete offlineJet_phi;
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void TriggerEffs::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
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
DEFINE_FWK_MODULE(TriggerEffs);