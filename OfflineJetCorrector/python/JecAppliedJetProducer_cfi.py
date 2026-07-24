import FWCore.ParameterSet.Config as cms

jecAppliedJetProducer = cms.EDProducer(
    "JecAppliedJetProducer",
    isDebug = cms.bool(False),  # set True to dump [JERC DEBUG] logs

    Jets = cms.PSet(
        srcAK4 = cms.InputTag("slimmedJets"),          # pat::JetCollection
        rho    = cms.InputTag("fixedGridRhoFastjetAll"),
        Year   = cms.string("2024"),
        IsData = cms.bool(False),

        # Optional era ("" => None)
        Era    = cms.string(""),

        # --- Choose one of: "Nominal", "JES", "JER"
        SystKind    = cms.string("Nominal"),

        # If SystKind == "JES"
        JesSystName = cms.string("AbsoluteStat"),  # correction set key
        JesSystVar  = cms.string("Up"),            # "Up" | "Down"

        # If SystKind == "JER"
        JerVar      = cms.string("nom"),           # "nom" | "up" | "down"
        JerRegion   = cms.PSet(                    # optional gate
            etaMin = cms.double(0.0),
            etaMax = cms.double(999.0),
            ptMin  = cms.double(0.0),
            ptMax  = cms.double(1.0e9),
        ),
        JecConfig = cms.FileInPath("jerc-application-tutorial/JecConfigAK4.json"),
        JerToolConfig = cms.FileInPath("jerc-application-tutorial/jer_smear.json.gz"),
    ),
)

