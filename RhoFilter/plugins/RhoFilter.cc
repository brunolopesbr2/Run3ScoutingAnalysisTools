// -*- C++ -*-
//
// Package:    Run3ScoutingAnalysisTools/RhoFilter
// Class:      RhoFilter
//
/**\class RhoFilter RhoFilter.cc Run3ScoutingAnalysisTools/RhoFilter/plugins/RhoFilter.cc

 Description: Filters events based on whether the hltScoutingPFPacker "rho"
              product is present, so downstream JEC producers only run when
              rho is available.

 Implementation:
     Uses mayConsume<double> since the product is expected to be missing
     for some events (e.g. sparse/empty scouting collections), and we do
     not want the framework to complain about an always-required branch.
*/
//
// Original Author:  Bruno
//         Created:  Tue, 14 Jul 2026 17:32:28 GMT
//
//

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDFilter.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"
#include "FWCore/Utilities/interface/InputTag.h"

//
// class declaration
//

class RhoFilter : public edm::stream::EDFilter<> {
public:
  explicit RhoFilter(const edm::ParameterSet&);
  ~RhoFilter() override;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void beginStream(edm::StreamID) override;
  bool filter(edm::Event&, const edm::EventSetup&) override;
  void endStream() override;

  // ----------member data ---------------------------
  edm::EDGetTokenT<double> rhoToken_;
};

//
// constructors and destructor
//
RhoFilter::RhoFilter(const edm::ParameterSet& iConfig)
    : rhoToken_(mayConsume<double>(iConfig.getParameter<edm::InputTag>("src"))) {
  //now do what ever initialization is needed
}

RhoFilter::~RhoFilter() {
  // do anything here that needs to be done at destruction time
  // (e.g. close files, deallocate resources etc.)
  //
  // please remove this method altogether if it would be left empty
}

//
// member functions
//

// ------------ method called on each new Event  ------------
bool RhoFilter::filter(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;

  edm::Handle<double> rhoHandle;
  iEvent.getByToken(rhoToken_, rhoHandle);

  return rhoHandle.isValid();
}

// ------------ method called once each stream before processing any runs, lumis or events  ------------
void RhoFilter::beginStream(edm::StreamID) {
  // please remove this method if not needed
}

// ------------ method called once each stream after processing all runs, lumis and events  ------------
void RhoFilter::endStream() {
  // please remove this method if not needed
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void RhoFilter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("src", edm::InputTag("hltScoutingPFPacker", "rho"));
  descriptions.add("rhoFilter", desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(RhoFilter);