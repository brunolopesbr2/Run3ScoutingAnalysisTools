## Plotting scripts for the Trigger Efficiency study

This folder contains two python scripts: `effPlot.py`, which makes the efficiency plot for both data vs background MC and signal vs background MC, and `testHT.py`, which makes the validation plots for the proxy HT. Both scripts are intended to work with the trees made by `TriggerEffs.py`.

### Efficiency plots script

A simple `python3 effPlot.py` makes the efficiency plots. The main are:

- processDict, signalDict and backgroundDict to be replaced with the actual path for the corresponding input trees. The format is a list of ROOT files. The helper function FileList takes all the files in a given folder.

- signalFamiles: used on the signal vs background plot. Makes one plot for each entry with the naive efficiencies for the corresponding list of signals.

- isSignal: a flag to tell the script to do the data vs background or de sinal vs background plot.

- Fit: whether to make the turn-on fit. Not used in the ANv5 version anymore.

- Trigger: the trigger bit used to evaluate the efficiency.

- HT_EXPR: the formula for the HT proxy.

- JECvar: JEC variation to use. Leave empty for nominal.


### Proxy HT validation plots script

`testHT.py` makes the HT distribution plots, the 2D correlation plots and the correlation coefficiency plot. The configs are:

- processDict, signalDict and backgroundDict to be replaced with the actual path for the corresponding input trees. The format is a string pointing to a single ROOT file.

- ht_proxy: the variable to use as the HT proxy. The ANv5 proxy is defined as "hltNeutralPlusChargedPFCands", but can use e.g. hltHT for a test.

- signals are the signal families to make the validaiton plots.

- JECvar: JEC variation to use. Leave empty for nominal.
