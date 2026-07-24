import FWCore.ParameterSet.Config as cms
import os
import FWCore.ParameterSet.VarParsing as VarParsing

process = cms.Process("JetCorrectorOffline")
options = VarParsing.VarParsing ('analysis')

options.register('isMC',
                 False,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "If using MC or data"
    )

options.parseArguments()
process.load("FWCore.MessageService.MessageLogger_cfi")
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)
process.MessageLogger.cerr.FwkSummary.reportEvery = 100
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        '/store/data/Run2024D/ScoutingPFMonitor/MINIAOD/PromptReco-v1/000/380/306/00000/7236c128-bb6e-4a16-aeda-2091c9544adc.root'
    )
)

#Choosing the GlobalTag
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag

if(options.isMC):
    process.GlobalTag = GlobalTag(process.GlobalTag, '140X_mcRun3_2024_realistic_v26', '')  
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_HLT_v3', '')

# Scouting
process.jecAppliedJetProducer = cms.EDProducer(
    "JecAppliedJetProducer",
    isDebug = cms.bool(False),  # set True to dump [JERC DEBUG] logs

    Jets = cms.PSet(
        srcAK4 = cms.InputTag("slimmedJets"),          # pat::JetCollection
        rho    = cms.InputTag("fixedGridRhoFastjetAll"),
        Year   = cms.string("2024"),
        IsData = cms.bool(True),

        # Optional era ("" => None)
        Era    = cms.string("Era2024All"),

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
        JecConfig = cms.FileInPath("Run3ScoutingAnalysisTools/JecConfigAK4.json"),
        JerToolConfig = cms.FileInPath("Run3ScoutingAnalysisTools/jer_smear.json.gz"),
    ),
)




process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('scoutMonitorJetCorrected.root'),
)

# Usually it is better to put producers on a task instead of a path
# but paths also work.
process.p = cms.Path(
    process.jecAppliedJetProducer
)
process.e = cms.EndPath(process.out)