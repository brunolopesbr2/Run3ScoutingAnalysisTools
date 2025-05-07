// -*- C++ -*-
//
// Package:    Run3ScoutingAnalysisTools/EventSkim
// Class:      TriggerFilter
//
/**\class TriggerFilter  Run3ScoutingAnalysisTools/EventSkim/plugins/TriggerFilter.cc

   Description: [one line class summary]
                                                                
   Implementation:
   [Notes on implementation]
*/

// system include files
#include <memory>
#include <iostream>

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
//#include "SimDataFormats/GeneratorProducts/interface/HepMCProduct.h"
//#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
//#include "SimDataFormats/GeneratorProducts/interface/GenRunInfoProduct.h"
#include "TH1.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
//
// class declaration
//

class TriggerFilter : public edm::one::EDFilter<edm::one::SharedResources> {
   public:
      explicit TriggerFilter(const edm::ParameterSet&);
      ~TriggerFilter();
  
      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual bool filter(edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() ;
      
      virtual bool beginRun(edm::Run&, edm::EventSetup const&);
      virtual bool endRun(edm::Run&, edm::EventSetup const&);
      virtual bool beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual bool endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
  
      // ----------member data ---------------------------
      const edm::EDGetTokenT<std::vector<Run3ScoutingPFJet> >  pfjetsToken;
  //const edm::EDGetTokenT<std::vector<pat::Jet> >  patjetsToken;
  //const edm::EDGetTokenT<GenEventInfoProduct> GeneratorToken_;
      const edm::EDGetTokenT<edm::TriggerResults> triggerResultsToken;
      
      double luminosity;
      double crossSection;
      edm::InputTag algInputTag_;
      edm::InputTag extInputTag_;
      edm::EDGetToken algToken_;
      std::unique_ptr<l1t::L1TGlobalUtil> l1GtUtils_;
      std::vector<std::string>     l1Seeds_;
      bool isScouting;
  
      TH1D* h_genWeights;
      TH1D* h_weights;
      TH1D* h_weightsSquared;

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
TriggerFilter::TriggerFilter(const edm::ParameterSet& iConfig):
  pfjetsToken(consumes<std::vector<Run3ScoutingPFJet> >(iConfig.getParameter<edm::InputTag>("pfjets"))),
  //patjetsToken(consumes<std::vector<pat::Jet> >(iConfig.getParameter<edm::InputTag>("patjets"))),
  //GeneratorToken_(consumes(iConfig.getParameter<edm::InputTag>("generatorName"))),
  triggerResultsToken(consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("triggerresults"))),
  luminosity(iConfig.existsAs<double>("luminosity") ? iConfig.getParameter<double>  ("luminosity") : 1.0),
  crossSection(iConfig.existsAs<double>("crossSection") ? iConfig.getParameter<double>  ("crossSection") : 1.0),  
  isScouting(iConfig.existsAs<bool>("isScouting") ? iConfig.getParameter<bool>  ("isScouting") : false)
{
  usesResource("TFileService");
  algInputTag_ = iConfig.getParameter<edm::InputTag>("AlgInputTag");
  extInputTag_ = iConfig.getParameter<edm::InputTag>("l1tExtBlkInputTag");
  algToken_ = consumes<BXVector<GlobalAlgBlk>>(algInputTag_);
  l1Seeds_ = iConfig.getParameter<std::vector<std::string> >("l1Seeds");
  l1GtUtils_ = std::make_unique<l1t::L1TGlobalUtil>(iConfig, consumesCollector(), *this, algInputTag_, extInputTag_, l1t::UseEventSetupIn::Event);
}


TriggerFilter::~TriggerFilter()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called on each new Event  ------------
bool
TriggerFilter::filter(edm::Event& iEvent, const edm::EventSetup& iSetup)
{

  using namespace edm;
  using namespace std;

  bool passFilter = true;
  
  //edm::Handle<GenEventInfoProduct> generatorHandle;
  //iEvent.getByToken(GeneratorToken_, generatorHandle);
  double genWeight = 1; //weights=1 for data
  h_genWeights->Fill("None",genWeight);
  double theWeight = 1;
  h_weights->Fill("None",theWeight);
  h_weightsSquared->Fill("None",pow(theWeight,2));
  
  int nPFJets = -1;
  //Get the jets
  Handle<vector<Run3ScoutingPFJet> > pfjetsH;
  iEvent.getByToken(pfjetsToken, pfjetsH);
  std::vector<Run3ScoutingPFJet> pfJetVector;

  //Require 4 PF Jets
  if(pfjetsH.isValid()){
    for (auto jets_iter = pfjetsH->begin(); jets_iter != pfjetsH->end(); ++jets_iter) {
      if(jets_iter->pt() > 20){
	pfJetVector.push_back(*jets_iter);
      }
    }
    nPFJets = pfJetVector.size();
  }

  //Get the jets
  //Handle<vector<pat::Jet> > patjetsH;
  //iEvent.getByToken(patjetsToken, patjetsH);
  //std::vector<pat::Jet> patJetVector;

  /*  //Require 4 Pat Jets -- not present in data
  if(patjetsH.isValid()){
    for (auto jets_iter = patjetsH->begin(); jets_iter != patjetsH->end(); ++jets_iter) {
      if(jets_iter->pt() > 20){
	patJetVector.push_back(*jets_iter);
      }
    }
    nPFJets = patJetVector.size();  
    }*/
  passFilter = passFilter && (nPFJets>3);
  if(passFilter){
    h_genWeights->Fill("nJets",genWeight);
    h_weights->Fill("nJets",theWeight);
    h_weightsSquared->Fill("nJets",pow(theWeight,2));
  }
  
  bool passTrigger;
  if(isScouting){
    l1GtUtils_->retrieveL1(iEvent,iSetup,algToken_);
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
  else{
    edm::Handle<edm::TriggerResults> triggerBits;
    iEvent.getByToken(triggerResultsToken, triggerBits);
    const edm::TriggerNames &names = iEvent.triggerNames(*triggerBits);
    bool HLT_FinalResult = false;
    for (unsigned int i = 0, n = triggerBits->size(); i < n; ++i) {
      std::string name = names.triggerName(i);
      if((name.find("HLT_PFHT330PT30_QuadPFJet_75_60_45_40_PNet3BTag_4p3_v")!=std::string::npos) || (name.find("HLT_PFHT1050_v")!=std::string::npos) ){
	if(triggerBits->accept(i)) HLT_FinalResult = true;
      }
    }
    passTrigger = HLT_FinalResult; 
  }

  passFilter = passFilter && passTrigger;
  if(passFilter){
    h_genWeights->Fill("Trigger",genWeight);
    h_weights->Fill("Trigger",theWeight);
    h_weightsSquared->Fill("Trigger",pow(theWeight,2));
  }
  
  return passFilter;
}

// ------------ method called once each job just before starting event loop  ------------
void 
TriggerFilter::beginJob()
{
  edm::Service<TFileService> fs;
  h_genWeights = fs->make<TH1D>("genWeightsSkim",";Cut Applied; Sum of Gen Weights",3,0,3);
  h_genWeights->GetXaxis()->SetBinLabel(1,"None");
  h_genWeights->GetXaxis()->SetBinLabel(2,"nJets");
  h_genWeights->GetXaxis()->SetBinLabel(3,"Trigger");
  h_weights = fs->make<TH1D>("weightsSkim",";Cut Applied; Sum of Weights",3,0,3);
  h_weights->GetXaxis()->SetBinLabel(1,"None");
  h_weights->GetXaxis()->SetBinLabel(2,"nJets");
  h_weights->GetXaxis()->SetBinLabel(3,"Trigger");
  h_weightsSquared = fs->make<TH1D>("weightsSquaredSkim",";Cut Applied; Sum of Squared Weights",3,0,3);
  h_weightsSquared->GetXaxis()->SetBinLabel(1,"None");
  h_weightsSquared->GetXaxis()->SetBinLabel(2,"nJets");
  h_weightsSquared->GetXaxis()->SetBinLabel(3,"Trigger");
}

// ------------ method called once each job just after ending the event loop  ------------
void 
TriggerFilter::endJob() {
  h_genWeights->GetDirectory()->cd();
  h_genWeights->Draw();
  h_genWeights->Write();

  h_weights->Draw();
  h_weights->Write();

  h_weightsSquared->Draw();
  h_weightsSquared->Write();
}

// ------------ method called when starting to processes a run  ------------
bool 
TriggerFilter::beginRun(edm::Run&, edm::EventSetup const&)
{ 
  return true;
}

// ------------ method called when ending the processing of a run  ------------
bool 
TriggerFilter::endRun(edm::Run&, edm::EventSetup const&)
{
  return true;
}

// ------------ method called when starting to processes a luminosity block  ------------
bool 
TriggerFilter::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
  return true;
}

// ------------ method called when ending the processing of a luminosity block  ------------
bool 
TriggerFilter::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
  return true;
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
TriggerFilter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}
//define this as a plug-in
DEFINE_FWK_MODULE(TriggerFilter);
