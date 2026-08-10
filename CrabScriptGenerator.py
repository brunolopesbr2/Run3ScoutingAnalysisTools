inputDatasets = ["/QCD-4Jets_Bin-HT-200to400_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD-4Jets_Bin-HT-400to600_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD-4Jets_Bin-HT-600to800_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD-4Jets_Bin-HT-800to1000_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD-4Jets_Bin-HT-1000to1200_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD-4Jets_Bin-HT-1200to1500_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD-4Jets_Bin-HT-1500to2000_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD-4Jets_Bin-HT-2000_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD-4Jets_Bin-HT-40to70_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD-4Jets_Bin-HT-70to100_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/QCD-4Jets_Bin-HT-100to200_TuneCP5_13p6TeV_madgraphMLM-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/StopStopbarTo2Dbar2D_M-200_CTau-10mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-200_CTau-10mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-200_CTau-1mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-200_CTau-1mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-200_CTau-3mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-200_CTau-3mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-400_CTau-10mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-400_CTau-10mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-400_CTau-1mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-400_CTau-1mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-400_CTau-3mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-400_CTau-3mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-600_CTau-10mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-600_CTau-10mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-600_CTau-1mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-600_CTau-1mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-600_CTau-3mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-600_CTau-3mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-800_CTau-10mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-800_CTau-10mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-800_CTau-1mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-800_CTau-1mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-800_CTau-3mm_Summer24_100k_v2/brlopesd-StopStopbarTo2Dbar2D_M-800_CTau-3mm_Summer24_100k_miniAOD_v2-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-200_ctau-0p1mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-200_ctau-0p1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-200_ctau-0p3mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-200_ctau-0p3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-200_ctau-0p7mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-200_ctau-0p7mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-400_ctau-0p1mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-400_ctau-0p1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-400_ctau-0p3mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-400_ctau-0p3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-400_ctau-0p7mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-400_ctau-0p7mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-600_ctau-0p1mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-600_ctau-0p1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-600_ctau-0p3mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-600_ctau-0p3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-600_ctau-0p7mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-600_ctau-0p7mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-800_ctau-0p1mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-800_ctau-0p1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-800_ctau-0p3mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-800_ctau-0p3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Dbar2D_M-800_ctau-0p7mm_100kEvts_v2/brlopesd-StopStopbarTo2Dbar2D_M-800_ctau-0p7mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-200_ctau-0p1mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-200_ctau-0p1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-200_ctau-0p3mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-200_ctau-0p3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-200_ctau-0p7mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-200_ctau-0p7mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-200_ctau-10mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-200_ctau-10mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-200_ctau-1mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-200_ctau-1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-200_ctau-3mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-200_ctau-3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-400_ctau-0p1mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-400_ctau-0p1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-400_ctau-0p3mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-400_ctau-0p3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-400_ctau-0p7mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-400_ctau-0p7mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-400_ctau-10mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-400_ctau-10mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-400_ctau-1mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-400_ctau-1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-400_ctau-3mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-400_ctau-3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-600_ctau-0p1mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-600_ctau-0p1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-600_ctau-0p3mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-600_ctau-0p3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-600_ctau-0p7mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-600_ctau-0p7mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-600_ctau-10mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-600_ctau-10mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-600_ctau-1mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-600_ctau-1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-600_ctau-3mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-600_ctau-3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-800_ctau-0p1mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-800_ctau-0p1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-800_ctau-0p3mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-800_ctau-0p3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-800_ctau-0p7mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-800_ctau-0p7mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-800_ctau-10mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-800_ctau-10mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-800_ctau-1mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-800_ctau-1mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StopStopbarTo2Bbar2B_M-800_ctau-3mm_100kEvts_v1/brlopesd-StopStopbarTo2Bbar2B_M-800_ctau-3mm_100kEvts_step4_miniAOD_v1-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/ScoutingPFRun3/Run2024C-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024D-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024E-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024F-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024G-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024H-v1/HLTSCOUT",
                 "/ScoutingPFRun3/Run2024I-v1/HLTSCOUT",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-1_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-0p1-MH-125-MS-7_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-1_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-1-MH-125-MS-7_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-1_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4D_Par-ctauS-10-MH-125-MS-7_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-1_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-0p1-MH-125-MS-7_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-1_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-1-MH-125-MS-7_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-15_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-1_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-23_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-30_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-40_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-55_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/GluGluH-Hto2Sto4B_Par-ctauS-10-MH-125-MS-7_TuneCP5_13p6TeV_powheg-pythia8/RunIII2024Summer24MiniAOD-140X_mcRun3_2024_realistic_v26-v2/MINIAODSIM",
                 "/StealthSHH_mStop-300_mSo-100_ctau-0p1mm100kEvts_v2/brlopesd-StealthSHH_mStop-300_mSo-100_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-300_mSo-100_ctau-10mm100kEvts_v2/brlopesd-StealthSHH_mStop-300_mSo-100_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-300_mSo-100_ctau-1mm100kEvts_v2/brlopesd-StealthSHH_mStop-300_mSo-100_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-300_mSo-100_ctau-3mm100kEvts_v2/brlopesd-StealthSHH_mStop-300_mSo-100_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-325_mSo-100_ctau-0p1mm100kEvts_v2/brlopesd-StealthSHH_mStop-325_mSo-100_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-325_mSo-100_ctau-10mm100kEvts_v2/brlopesd-StealthSHH_mStop-325_mSo-100_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-325_mSo-100_ctau-1mm100kEvts_v2/brlopesd-StealthSHH_mStop-325_mSo-100_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-325_mSo-100_ctau-3mm100kEvts_v2/brlopesd-StealthSHH_mStop-325_mSo-100_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-500_mSo-100_ctau-0p1mm100kEvts_v2/brlopesd-StealthSHH_mStop-500_mSo-100_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-500_mSo-100_ctau-10mm100kEvts_v2/brlopesd-StealthSHH_mStop-500_mSo-100_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-500_mSo-100_ctau-1mm100kEvts_v2/brlopesd-StealthSHH_mStop-500_mSo-100_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-500_mSo-100_ctau-3mm100kEvts_v2/brlopesd-StealthSHH_mStop-500_mSo-100_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-500_mSo-275_ctau-0p1mm100kEvts_v2/brlopesd-StealthSHH_mStop-500_mSo-275_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-500_mSo-275_ctau-10mm100kEvts_v2/brlopesd-StealthSHH_mStop-500_mSo-275_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-500_mSo-275_ctau-1mm100kEvts_v2/brlopesd-StealthSHH_mStop-500_mSo-275_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-500_mSo-275_ctau-3mm100kEvts_v2/brlopesd-StealthSHH_mStop-500_mSo-275_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-700_mSo-100_ctau-0p1mm100kEvts_v2/brlopesd-StealthSHH_mStop-700_mSo-100_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-700_mSo-100_ctau-10mm100kEvts_v2/brlopesd-StealthSHH_mStop-700_mSo-100_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-700_mSo-100_ctau-1mm100kEvts_v2/brlopesd-StealthSHH_mStop-700_mSo-100_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-700_mSo-100_ctau-3mm100kEvts_v2/brlopesd-StealthSHH_mStop-700_mSo-100_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-700_mSo-475_ctau-0p1mm100kEvts_v2/brlopesd-StealthSHH_mStop-700_mSo-475_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-700_mSo-475_ctau-10mm100kEvts_v2/brlopesd-StealthSHH_mStop-700_mSo-475_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-700_mSo-475_ctau-1mm100kEvts_v2/brlopesd-StealthSHH_mStop-700_mSo-475_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-700_mSo-475_ctau-3mm100kEvts_v2/brlopesd-StealthSHH_mStop-700_mSo-475_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-900_mSo-100_ctau-0p1mm100kEvts_v2/brlopesd-StealthSHH_mStop-900_mSo-100_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-900_mSo-100_ctau-10mm100kEvts_v2/brlopesd-StealthSHH_mStop-900_mSo-100_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-900_mSo-100_ctau-1mm100kEvts_v2/brlopesd-StealthSHH_mStop-900_mSo-100_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-900_mSo-100_ctau-3mm100kEvts_v2/brlopesd-StealthSHH_mStop-900_mSo-100_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-900_mSo-675_ctau-0p1mm100kEvts_v2/brlopesd-StealthSHH_mStop-900_mSo-675_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-900_mSo-675_ctau-10mm100kEvts_v2/brlopesd-StealthSHH_mStop-900_mSo-675_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-900_mSo-675_ctau-1mm100kEvts_v2/brlopesd-StealthSHH_mStop-900_mSo-675_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSHH_mStop-900_mSo-675_ctau-3mm100kEvts_v2/brlopesd-StealthSHH_mStop-900_mSo-675_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-300_mSo-100_ctau-0p1mm100kEvts_v2/brlopesd-StealthSYY_mStop-300_mSo-100_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-300_mSo-100_ctau-10mm100kEvts_v2/brlopesd-StealthSYY_mStop-300_mSo-100_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-300_mSo-100_ctau-1mm100kEvts_v2/brlopesd-StealthSYY_mStop-300_mSo-100_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-300_mSo-100_ctau-3mm100kEvts_v2/brlopesd-StealthSYY_mStop-300_mSo-100_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-325_mSo-100_ctau-0p1mm100kEvts_v2/brlopesd-StealthSYY_mStop-325_mSo-100_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-325_mSo-100_ctau-10mm100kEvts_v2/brlopesd-StealthSYY_mStop-325_mSo-100_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-325_mSo-100_ctau-1mm100kEvts_v2/brlopesd-StealthSYY_mStop-325_mSo-100_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-325_mSo-100_ctau-3mm100kEvts_v2/brlopesd-StealthSYY_mStop-325_mSo-100_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-500_mSo-100_ctau-0p1mm100kEvts_v2/brlopesd-StealthSYY_mStop-500_mSo-100_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-500_mSo-100_ctau-10mm100kEvts_v2/brlopesd-StealthSYY_mStop-500_mSo-100_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-500_mSo-100_ctau-1mm100kEvts_v2/brlopesd-StealthSYY_mStop-500_mSo-100_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-500_mSo-100_ctau-3mm100kEvts_v2/brlopesd-StealthSYY_mStop-500_mSo-100_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-500_mSo-275_ctau-0p1mm100kEvts_v2/brlopesd-StealthSYY_mStop-500_mSo-275_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-500_mSo-275_ctau-10mm100kEvts_v2/brlopesd-StealthSYY_mStop-500_mSo-275_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-500_mSo-275_ctau-1mm100kEvts_v2/brlopesd-StealthSYY_mStop-500_mSo-275_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-500_mSo-275_ctau-3mm100kEvts_v2/brlopesd-StealthSYY_mStop-500_mSo-275_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-700_mSo-100_ctau-0p1mm100kEvts_v2/brlopesd-StealthSYY_mStop-700_mSo-100_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-700_mSo-100_ctau-10mm100kEvts_v2/brlopesd-StealthSYY_mStop-700_mSo-100_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-700_mSo-100_ctau-1mm100kEvts_v2/brlopesd-StealthSYY_mStop-700_mSo-100_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-700_mSo-100_ctau-3mm100kEvts_v2/brlopesd-StealthSYY_mStop-700_mSo-100_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-700_mSo-475_ctau-0p1mm100kEvts_v2/brlopesd-StealthSYY_mStop-700_mSo-475_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-700_mSo-475_ctau-10mm100kEvts_v2/brlopesd-StealthSYY_mStop-700_mSo-475_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-700_mSo-475_ctau-1mm100kEvts_v2/brlopesd-StealthSYY_mStop-700_mSo-475_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-700_mSo-475_ctau-3mm100kEvts_v2/brlopesd-StealthSYY_mStop-700_mSo-475_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-900_mSo-100_ctau-0p1mm100kEvts_v2/brlopesd-StealthSYY_mStop-900_mSo-100_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-900_mSo-100_ctau-10mm100kEvts_v2/brlopesd-StealthSYY_mStop-900_mSo-100_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-900_mSo-100_ctau-1mm100kEvts_v2/brlopesd-StealthSYY_mStop-900_mSo-100_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-900_mSo-100_ctau-3mm100kEvts_v2/brlopesd-StealthSYY_mStop-900_mSo-100_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-900_mSo-675_ctau-0p1mm100kEvts_v2/brlopesd-StealthSYY_mStop-900_mSo-675_ctau-0p1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-900_mSo-675_ctau-10mm100kEvts_v2/brlopesd-StealthSYY_mStop-900_mSo-675_ctau-10mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-900_mSo-675_ctau-1mm100kEvts_v2/brlopesd-StealthSYY_mStop-900_mSo-675_ctau-1mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 "/StealthSYY_mStop-900_mSo-675_ctau-3mm100kEvts_v2/brlopesd-StealthSYY_mStop-900_mSo-675_ctau-3mm_step4-miniAOD_100kEvts_v4-df1e99b50d14b85be33e7e4ab518ee3a/USER",
                 ]

crossSections = [1961000000, 95620000, 13540000, 3033000, 883700, 383500, 125200, 26490, 311400000000, 58500000000, 25400000000, 762100*0.439, 762100*0.455] #Backgrounds should go first in dataset list with corresponding cross sections listed here
tagSuffix = "v33-3to4Dxy"
scouting = True

for i in range(len(inputDatasets)):
    dataset = inputDatasets[i]
    if ("TTto" in dataset) or ("QCD" in dataset):
        crossSection = crossSections[i]
        PUFile = "PURatio_Full2024.npy"
    elif ("GluGluH" in dataset):
        crossSection = 8000;
        lifetime = dataset.split("-")[3]
        mass = dataset.split("-")[7]
        mass = mass.split("_")[0]
        PUFile = f"Hto2Sto4D-cT{lifetime}-MS{mass}_PURatio_Full2024.npy"
    elif ("ScoutingPF" in dataset):
        crossSection = 1
        PUFile = "empty.npy"
    elif ("Stealth" in dataset):
        crossSection = 1
        PUFile = "Stop-M200-cT1_PURatio_Full2024.npy"
    else:
        crossSection = 1
        mass = dataset.split("-")[1]
        mass = mass[:3]
        lifetime = dataset.split("-")[2]
        lifetime = lifetime.split("mm")[0]
        if("step4" in dataset):
            PUFile = "Stop-M200-cT1_PURatio_Full2024.npy"
        else:
            PUFile = f"Stop-M{mass}-cT{lifetime}_PURatio_Full2024.npy"
    if "StopStop" in dataset:
        tag = ""
        if ("step4" in dataset):
            tag = dataset[1:].split("_100kEvts")[0] + "_Tree_" + tagSuffix
        else:
            tag = dataset[1:].split("_Summer24")[0] + "_Tree_" + tagSuffix
        dataBase = "phys03"
        totalUnits = 100000
        isMC = True
        hasReco = True
        unitsPerJob = 60000
        splitting = 'EventAwareLumiBased'
        memory = 2500
    elif "ScoutingPF" in dataset:
        tag = dataset[16:].split("-v1")[0] + "_Tree_" + tagSuffix
        dataBase = "global"
        #totalUnits = 900000000
        isMC = False
        hasReco = False
        unitsPerJob = 20
        splitting = 'LumiBased'
        memory = 3000
        if "2024C" in dataset:
            totalUnits = 24298
        elif "2024D" in dataset:
            totalUnits = 23251
        elif "2024E" in dataset:
            totalUnits = 31576
        elif "2024F" in dataset:
            totalUnits = 70035
        elif "2024G" in dataset:
            totalUnits = 92654
        elif "2024H" in dataset:
            totalUnits = 13078
        elif "2024I" in dataset:
            totalUnits = 27112
            
    elif "GluGluH" in dataset:
        tag = dataset[1:].split("_Tune")[0] + "_Tree_" + tagSuffix
        dataBase = "global"
        totalUnits = 6000000
        isMC = True
        hasReco = True
        unitsPerJob = 200000
        splitting = 'EventAwareLumiBased'
        memory = 2500
    elif "Stealth" in dataset:
        tag = tag = dataset[1:].split("100kEvts")[0] + "_Tree_" + tagSuffix            
        dataBase = "phys03"
        totalUnits = 120000
        isMC = True
        hasReco = True
        unitsPerJob = 60000
        splitting = 'EventAwareLumiBased'
        memory = 2500
    else:
        tag = dataset[1:].split("_Tune")[0] + "_Tree_" + tagSuffix
        dataBase = "global"
        totalUnits = 125000000
        isMC = True
        hasReco = True
        unitsPerJob = 200000
        splitting = 'EventAwareLumiBased'
        memory = 2500
    string = f"""from CRABClient.UserUtilities import config \n
config = config() \n
theTag = '{tag}' \n
config.General.requestName = theTag \n
config.JobType.pluginName = 'Analysis' \n
config.JobType.psetName = '../VertexNTupleMaker.py' \n
config.JobType.inputFiles = ['/afs/cern.ch/user/r/rmccarth/private/scouting/CMSSW_14_0_18_patch1/src/Run3ScoutingAnalysisTools/Summer24Prompt24_RunBCDEFGHI.root'] \n
config.JobType.maxMemoryMB = 3000 \n
config.Data.inputDBS = '{dataBase}' \n
config.Data.inputDataset = '{dataset}' \n
config.Data.splitting = '{splitting}' \n
config.Data.unitsPerJob = {unitsPerJob} \n
config.Data.totalUnits = {totalUnits} \n
config.Data.allowNonValidInputDataset = True \n
config.Data.publication = False \n
config.JobType.pyCfgParams = ['isScouting={scouting}','lumi=109.99','crossSection={crossSection}','isMC={isMC}','hasReco={hasReco}','PUFile=/afs/cern.ch/user/r/rmccarth/private/scouting/CMSSW_14_0_18_patch1/src/Run3ScoutingAnalysisTools/{PUFile}','doJEC=True'] \n
config.Data.outputDatasetTag = theTag \n
config.Data.outLFNDirBase = '/store/group/phys_exotica/DVScouting' \n
config.Site.storageSite = 'T2_CH_CERN' \n
""" 

    # Write to a temporary file
    if "StopStop" in dataset:
        #string += """config.Site.whitelist = ['T2_CH_CERN'] \n
#config.Data.ignoreLocality = True"""
        if ("step4" in dataset):
            with open("crabSubmitScripts/"+dataset[1:].split("_100kEvts")[0]+"_crabConfig.py", "w") as f:
                f.write(string)
        else:
            with open("crabSubmitScripts/"+dataset[1:].split("_Summer24")[0]+"_crabConfig.py", "w") as f:
                f.write(string)
    elif "ScoutingPF" in dataset:
        string += f"""config.Data.lumiMask = '../GoldenJSON/2024' + '{dataset[23]}' + '_Golden.json'"""
        with open("crabSubmitScripts/"+dataset[16:].split("-v1")[0]+"_crabConfig.py", "w") as f:
            f.write(string)
    elif "Stealth" in dataset:
        with open("crabSubmitScripts/"+dataset[1:].split("100kEvts")[0]+"_crabConfig.py", "w") as f:
                f.write(string)
    else:
        with open("crabSubmitScripts/"+dataset[1:].split("_Tune")[0]+"_crabConfig.py", "w") as f:
            f.write(string)
