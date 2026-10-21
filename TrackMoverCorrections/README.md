## TrackMover plotting scripts and correction file

This folder contains all scripts used to make the validation plots for the TrackMover and to derive the vertex efficiency correction file for the analysis. Here's a brief description of what each script does. It requires `ROOT` installed in a python environment.

### File database: `TMWeights_dsets.py`

This file contains the path to all ROOT files in form of python dictionaries, and all other scripts will import this information from this database. Its default is an example of what it should look like. The `backgroundDict` and `dataDict` are TrackMover trees (made by `TrackMoverTest.py` in the root of this repo), and `signalDict` is a regular analysis ntuple (made by `VertexNTupleMaker.py`) with `doTrackMoverTree=True`. When making the signal tree, also be careful to set `LLP_pdgId` accordingly in the `process.scoutingTree` config block.

### Weight maps: `TMWeights.py` and `TMLifetimeWeights.py`

Those two scripts make the kinematic and lifetime weight maps, respectively. The kinematic weights are based, by default, on the moved tracks delta R and net 3D momentum, while the lifetime weights are based on the 2D and 3D distances of the gen (or move) vertices with respect to the leading PV. For all four quantities, there's a variable `upper*`, which sets the upper limit of the maps, and includes the overflow in the last bin. The most sensitive of those is `upperNetP`, that can be tuned to enhance stats or to reproduce better the signal tail. The actual version of the analysis uses 500 GeV for the Higgs signals and 750 GeV for the SUSY signals as the upper bound for the net momentum.

For the Higgs signal, the cut on phiVV kills most of the signal due to its topology, so it is advised to comment out the line `df = df.Filter("abs(genVert_dPhiVV_TM) > 0.5")` for both scripts. Once it is all set, just run both with

```
python3 TMWeights.py
python3 TMLifetimeWeights.py
```

The scripts then will load all signals available in the `signalDict` and make one map for each in a root file. To be compatible with the next scripts, make two versions of the weight maps (for Higgs and for SUSY signals) and rename the output to:

```
TMWeights_Higgs.root
TMWeights_SUSY.root
TMLifetimeWeights_Higgs.root
TMLifetimeWeights_SUSY.root
```

### Validation plots `TMValPlots.py`

With the helper file `plottingFunctions.py`, this script makes several validation plots and outputs to the folder set in `plotsFolder`. It makes both the non-reweighted version and the version reweighted to the signal in `test_signal` (to be set for one of the entries in `signalDict`). The track plots only work for trees made in debug mode, so if it is not the case, leave `doTrackPlots` set to False. There's also an option to do only the kinematic reweighting by setting `doLifetimeReweighting` to False. Once everything is set, just run with `python3 TMValPlots.py`.

### Correction file: `makeCorrectionFile.py`

This final script makes the ROOT correction file with the efficiency ratios for all signals listed in `signalDict`, binned in the number of tracks associated to the matched vertex. It also includes a `raw` folder, with the distributions used for the numerator and denominator of the efficiencies for both data and MC. If all previous scripts are properly set, just run with `python3 maleCorrectionFile.py`.