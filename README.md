# Run3ScoutingAnalysisTools
### Repository for Run 3 scouting analysis tools

#### Setup
Setup a CMSSW working area and clone the `Run3ScoutingAnalysisTools` repo in the specific branch `Run3`:
```
cmsrel CMSSW_13_3_0
cd CMSSW_14_0_4/src
cmsenv
git cms-init
git clone https://github.com/brunolopesbr2/Run3ScoutingAnalysisTools.git -b Run3_JetHT_Winter24
scram b -j 8
```

#### Run on the scouting dataset
Run a basic example on a file of the Scouting dataset:

```
voms-proxy-init --voms cms --valid 168:00
cmsRun tree.py
```

If no errors are observed, you can proceed to the crab submission taking care of updating properly the configuration file chenging the dataset name and output name and checking the certification json file:

``` 
crab submit crabConfigTree.py
``` 

#### Check production status and luminosity
The status of the jobs can be monitored and failed jobs can be resubmitted:

``` 
crab status CRABDIR
crab resubmit CRABDIR
```

After having run successfully all jobs, the integrated luminosity corresponding to the processed data can be checked using [brilcalc](https://twiki.cern.ch/twiki/bin/view/CMS/BrilcalcQuickStart) in the following way:

``` 
crab report CRABDIR
source /cvmfs/cms-bril.cern.ch/cms-lumi-pog/brilws-docker/brilws-env
brilcalc --version
brilcalc lumi -i CRABDIR/results/processedLumis.json
``` 

#### Run the HLTScoutingUnpackProducer

IMPORTANT: there are some changes to the Scouting DataFormats needed to run this EDProducer. Move the `DataFormats` folder of this repo to the `src` folder and compile before running. This was taken from [this branch from Patin](https://github.com/patinkaew/cmssw/blob/scouting_nano_dev_14_0_13_patch1/PhysicsTools/Scouting/plugins/HLTScoutingUnpackProducer.cc)

For now, this version of the UnpackProducer takes the Scouting collections and build the standard vertices and tracks collections using fake hit patterns. It only saves trigger results and scouting collections on the output. Simply change the input file and run with `cmsRun HLTScoutingUnpackProducer.py`