/**
 * Very light JERC application tutorial.
 *
 * Usage:
 *   root -l -q -b applyJecAndJvmLite.C
 */

#if defined(__CLING__)
#pragma cling add_include_path("/afs/cern.ch/work/r/rverma/public/JME/JERC/cms-jerc-run2/Hist/corrlib/include")
#pragma cling add_library_path("/afs/cern.ch/work/r/rverma/public/JME/JERC/cms-jerc-run2/Hist/corrlib/lib")
#pragma cling add_include_path("/usr/local/include")
#pragma cling add_library_path("/usr/local/lib")
#pragma cling load("libcorrectionlib.so")
#endif

#include <correction.h>

#include <cmath>
#include <iostream>
#include <optional>
#include <string>
#include <utility>
#include <vector>

// ROOT
#include "TLorentzVector.h"

// JERC application tutorial
#include "JecConfigReader.cpp"
#include "JecApplication.cpp"
#include "JvmApplication.cpp"
#include "JvmConfigReader.cpp"


void applyJecAndJvmLite()
{
    using std::cout;
    using std::endl;

    // ---------------------------------------------------------
    // Choose year and build config / applier / JVM
    // ---------------------------------------------------------
    const bool        isData = false;          // MC to see JER
    const std::string year   = "2016Pre";

    // Global JEC config
    JecConfigReader::JecConfig& cfg = JecConfigReader::JecConfig::defaultInstance();

    // JEC applier 
    const bool print = true;
    auto apAK4 = JecApplication::Applier::McAK4(cfg, year, print);

    // Jet Veto Map 
    auto jvmCfg = JvmConfigReader::JvmConfig::defaultInstance().getJvmForYear(year);
    JvmApplication::VetoChecker jvmChecker(jvmCfg.ref, jvmCfg.key);

    // ---------------------------------------------------------
    // Dummy event content (one AK4 jet + gen jet + MET)
    // ---------------------------------------------------------
    const unsigned long long eventNumber = 42ULL;
    const double rho = 20.0;   

    //Jet inputs
    double jet_pt_nano   = 50.0; 
    double jet_eta       = 0.30;
    double jet_phi       = 1.00;
    double jet_mass      = 10.0; 
    double jet_area      = 0.80;
    double jet_rawFactor = 0.02;  
    //Raw jet pT
    double jet_pt_raw = jet_pt_nano * (1-jet_rawFactor); 

    int    jetId   = 6;    // e.g. tight
    double chEmEF  = 0.05;
    double neEmEF  = 0.10;

    // Dummy gen jet
    bool   hasGen  = true;
    double gen_pt  = 52.0;
    double gen_eta = 0.32;
    double gen_phi = 1.05;

    // Raw MET
    double met_pt_raw  = 80.0;
    double met_phi_raw = -2.0;

    // ---------------------------------------------------------
    cout << "\n---- Dummy event inputs:\n";
    // ---------------------------------------------------------
    cout << "isData      = " << (isData ? "true" : "false") << "\n";
    cout << "event       = " << eventNumber << "\n";
    cout << "rho         = " << rho << " GeV\n\n";

    cout << "AK4 jet (NanoAOD-like):\n";
    cout << "  pt        = " << jet_pt_nano  << " GeV\n";
    cout << "  eta, phi  = " << jet_eta << ", " << jet_phi << "\n";
    cout << "  mass      = " << jet_mass     << " GeV\n";
    cout << "  area      = " << jet_area     << "\n";
    cout << "  rawFactor = " << jet_rawFactor << "\n\n";

    cout << "Raw MET:\n";
    cout << "  pt, phi   = " << met_pt_raw << ", " << met_phi_raw << "\n\n";

    // ---------------------------------------------------------
    cout << "---- JES nominal: \n";
    // ---------------------------------------------------------
    JecApplication::JesInputs jesIn{
        jet_pt_nano,   
        jet_eta,
        jet_phi,
        jet_area,
        rho,
        jet_rawFactor 
    };
    double jesFactorNom = apAK4.jesFactorNominal(jesIn);
    double jet_pt_jes   = jet_pt_nano * jesFactorNom ;
    cout << "   Jet pt after JES nom = " << jet_pt_jes << "\n\n";


    // ---------------------------------------------------------
    cout << "---- One JES systematic: \n";
    // ---------------------------------------------------------
    auto jesUncAK4 = cfg.getJesUncSetsMcAK4Ref(year);   
    const auto& totalMap = jesUncAK4.total; //JesUncertaintySetTotal         
    std::string cmsName = "CMS_scale_j_Total";
    auto it = totalMap.find(cmsName);
    correction::Correction::Ref jesTotalRef;
    jesTotalRef = it->second;
    cout << "   Using JesUncertaintySetTotal component: " << cmsName << "\n";
    double jesTotalUpFactor = JecApplication::Applier::jesComponentSyst(
            jesTotalRef,
            "Up",           // direction
            jet_eta,
            jet_pt_jes,     // pt AFTER JES nominal
            print
        );
    double jet_pt_jes_systUp     = jet_pt_jes * jesTotalUpFactor;
    cout << "   Jet pt after JES nom + systUp= " << jet_pt_jes_systUp << "\n\n";


    // ---------------------------------------------------------
    cout << "---- JER nominal (MC only): \n";
    // ---------------------------------------------------------
    JecApplication::JerInputs jerIn{};
    jerIn.event = eventNumber;
    jerIn.rho   = rho;
    jerIn.maxDr = 0.2;
    if (hasGen) {
        jerIn.hasGen = true;
        jerIn.genPt  = gen_pt;
        jerIn.genEta = gen_eta;
        jerIn.genPhi = gen_phi;
    }
    JecApplication::SystematicOptions systJerNom{};
    systJerNom.jerVar = "nom";  // "nom", "up", "down"
    JecApplication::JesInputs jAfterJes{
        jet_pt_jes_systUp,
        jet_eta,
        jet_phi,
        jet_area,
        rho,
        0.0  // not used 
    };
    double jerFactorNom  = apAK4.jerFactor(jAfterJes, jerIn, systJerNom);
    double jet_pt_jes_systUp_jer = jet_pt_jes_systUp * jerFactorNom;


    // ---------------------------------------------------------
    cout << "---- Jet Veto Map (JVM): \n";
    // ---------------------------------------------------------
    bool inVeto = jvmChecker.checkJetInVetoRegion(
        jet_eta,
        jet_phi,
        jet_pt_nano,
        jetId,
        chEmEF,
        neEmEF
    );
    cout << "   JVM decision: " << (inVeto ? "IN VETO REGION -> veto event"
                    : "NOT in veto region -> keep event") << "\n\n";


    // ---------------------------------------------------------
    cout << "---- Type-1 MET via correctedMet: \n";
    // ---------------------------------------------------------
    // (a) Build MetInputs 
    JecApplication::MetInputs metIn{};
    metIn.metPt  = met_pt_raw;
    metIn.metPhi = met_phi_raw;

    // (b) Build JetForMet list (just one jet here)
    std::vector<JecApplication::JetForMet> jetsForMet;
    JecApplication::JetForMet jf{};
    jf.phi             = jet_phi;
    jf.eta             = jet_eta;
    jf.area            = jet_area;
    jf.rawPt           = jet_pt_raw; 
    jf.muonSubtrFactor = 0.0; //e.g.
    jf.chEmEf          = chEmEF;
    jf.neEmEf          = neEmEF;
    jetsForMet.push_back(jf);

    // (c) Build JerInputs list (parallel to jetsForMet)
    std::vector<JecApplication::JerInputs> jerForMet;
    JecApplication::JerInputs jerMet{};
    jerMet.event = eventNumber;
    jerMet.rho   = rho;
    jerMet.maxDr = 0.2;
    if (hasGen) {
        jerMet.hasGen = true;
        jerMet.genPt  = gen_pt;
        jerMet.genEta = gen_eta;
        jerMet.genPhi = gen_phi;
    }
    jerForMet.push_back(jerMet);

    // (d) Systematics for MET: JER nominal for illustration
    // The MET has to be corrected for: Jes syst up, down and jer syst up, down also
    // Basically any JEC that changes jet pT, the MET should also be corrected.
    JecApplication::SystematicOptions systForMet{};
    systForMet.jerVar     = "nom";
    systForMet.jerRegion  = std::nullopt;
    systForMet.jesSystRef = std::nullopt;
    systForMet.jesSystVar = "";

    // (e) Call correctedMet
    TLorentzVector p4MetCorr = apAK4.correctedMet(
        metIn,
        jetsForMet,
        jerForMet,
        rho,
        systForMet
    );
}
