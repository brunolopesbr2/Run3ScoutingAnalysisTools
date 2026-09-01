from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")
from scipy.optimize import curve_fit
import ROOT
plotDict = {
    "scoutTrack_pt": [0,50,26]
}

# --- Fit models ---
def exp_model(x, a, b, c):
    return a - np.exp(-b * x + c)

def quad_model(x, a, b, c):
    return a + b * x + c * x**2

def log_model(x, a, b, c):
    return a + b * np.log(x + c)

def bathtub_model(x, a, b, c):
    return a + b / x + c * x

def saturate_model(x, a, b, c):
    return a * x / (x + b) + c

def cubic_model(x, a, b, c, d):
    return a + b * x + c * x**2 + d * x**3

def tanh_model(x, a, b, c, d):
    return a * np.tanh(b * x + c) + d

# --- Model registry ---
models = {
    "exp":      {"func": exp_model,      "label": "a-exp(-b*x+c)",    "npar": 3},
    "quad":     {"func": quad_model,     "label": "a+b*x+c*x^2",       "npar": 3},
    "log":      {"func": log_model,      "label": "a+b*ln(x+c)",      "npar": 3},
    "bathtub":  {"func": bathtub_model,  "label": "a+b/x+c*x",       "npar": 3},
    "saturate": {"func": saturate_model, "label": "a*x/(x+b)+c",     "npar": 3},
    "cubic":    {"func": cubic_model,    "label": "a+b*x+c*x^2+d*x^3", "npar": 4},
    "tanh":     {"func": tanh_model,     "label": "a*tanh(b*x+c)+d",  "npar": 4},
}

# --- Configuration per fit ---
fit_config = {
    ("dxyErr",   "barrel_jetMatched"): {"model": "exp",      "p0": [1.5, 0.5, 0.0],   "bounds": ([0, 0, -10], [3, 10, 10])},
    ("dxyErr",   "disk_jetMatched"):   {"model": "bathtub",  "p0": [1.1, 0.5, 0.001], "bounds": (-np.inf, np.inf)},
    ("dzErr",    "barrel_jetMatched"): {"model": "exp",      "p0": [1.5, 0.5, 0.0],   "bounds": ([0, 0, -10], [3, 10, 10])},
    ("dzErr",    "disk_jetMatched"):   {"model": "exp",      "p0": [1.5, 0.5, 0.0],   "bounds": ([0, 0, -10], [3, 10, 10])},
    ("dzdxyCov", "barrel_jetMatched"): {"model": "tanh",      "p0": [0.15, 0.2, 0.0, 1.2], "bounds": ([0, 0, -5, 0], [1, 5, 5, 2])},
    ("dzdxyCov", "disk_jetMatched"):   {"model": "bathtub",  "p0": [1.1, 0.5, 0.001], "bounds": (-np.inf, np.inf)},
}

# Helper function to combine weighted statistics
def combine_weighted_stats(data, components):
    """Combine weighted statistics from multiple components"""
    combined = {}
    
    # First combine the raw sums
    sum_keys = ["weight_sum", "weight_sq_sum", "dxyErr_weighted_sum", "dszErr_weighted_sum", "dszdxyCov_weighted_sum",
                "dxyErr_weighted_sq_sum", "dszErr_weighted_sq_sum", "dszdxyCov_weighted_sq_sum"]
    
    for key in sum_keys:
        for string in ["_barrel","_disk","_barrel_jetMatched","_disk_jetMatched"]:
            fullKey = key+string
            if fullKey in data:
                combined[fullKey] = sum(data[fullKey][comp] for comp in components if comp in data[fullKey])
    
    # Recalculate means and standard errors
    for string in ["_barrel","_disk","_barrel_jetMatched","_disk_jetMatched"]:
        with np.errstate(divide='ignore', invalid='ignore'):
            # Weighted means
            combined["dxyErr_mean"+string] = np.where(combined["weight_sum"+string] > 0, 
                                              combined["dxyErr_weighted_sum"+string] / combined["weight_sum"+string], 0)
            combined["dzErr_mean"+string] = np.where(combined["weight_sum"+string] > 0, 
                                             combined["dszErr_weighted_sum"+string] / combined["weight_sum"+string], 0)
            combined["cov_mean"+string] = np.where(combined["weight_sum"+string] > 0, 
                                             combined["dszdxyCov_weighted_sum"+string] / combined["weight_sum"+string], 0)

            # Weighted variances
            dxyErr_var = np.where(combined["weight_sum"+string] > 0,
                                  combined["dxyErr_weighted_sq_sum"+string] / combined["weight_sum"+string] - combined["dxyErr_mean"+string]**2, 0)
            dzErr_var = np.where(combined["weight_sum"+string] > 0,
                                 combined["dszErr_weighted_sq_sum"+string] / combined["weight_sum"+string] - combined["dzErr_mean"+string]**2, 0)
            cov_var = np.where(combined["weight_sum"+string] > 0,
                                 combined["dszdxyCov_weighted_sq_sum"+string] / combined["weight_sum"+string] - combined["cov_mean"+string]**2, 0)

            # Effective sample size
            eff_n = np.where(combined["weight_sq_sum"+string] > 0, 
                             combined["weight_sum"+string]**2 / combined["weight_sq_sum"+string], 0)

            # Standard errors
            combined["dxyErr_stderr"+string] = np.where(eff_n > 0, np.sqrt(dxyErr_var / eff_n), 0)
            combined["dzErr_stderr"+string] = np.where(eff_n > 0, np.sqrt(dzErr_var / eff_n), 0)
            combined["cov_stderr"+string] = np.where(eff_n > 0, np.sqrt(cov_var / eff_n), 0)
    
    return combined

def main():
    limitDict = build_limits("../EXO-23-13-ExoHiggsBRLimitvsLifetime.root","../EXO-19-13-RPVSUSYSigmaBSquaredLimitsMassvsLifetime.root")
    dataDict, bkgDict = makeDict("v28-4DxyMin",["2024"],["QCD","TTTo"])
    plotWeights = {}
    dict = dataDict | bkgDict

    for process, rootFiles in dict.items():
        for rootFile in rootFiles:
            f = ROOT.TFile.Open(rootFile, "READ")

            #Assuming only one file per process here
            h_genWeights = f.Get("triggerFilter/genWeightsSkim")
            n_binsSkim = h_genWeights.GetNbinsX() 
            genWeights = np.array([h_genWeights.GetBinContent(i) for i in range(1, n_binsSkim + 1)])
            genWeightSum = genWeights[0]

            for plot in ["weight_sum","weight_sq_sum","dxyErr_weighted_sum","dszErr_weighted_sum","dszdxyCov_weighted_sum","dxyErr_weighted_sq_sum","dszErr_weighted_sq_sum","dszdxyCov_weighted_sq_sum"]:
                for string in ["_barrel","_disk","_barrel_jetMatched","_disk_jetMatched"]:
                    hist = f.Get("p/"+plot+string)
                    nbins = hist.GetNbinsX() 
                    data = np.array([hist.GetBinContent(i) for i in range(1, nbins + 1)])
                    rebinned = data[:50].reshape(25, 2).sum(axis=1) #rebin to 25 bins
                    rebinned[-1] += data[50:].sum()  # overflow from x > 50


                    if process in bkgDict:
                        if ("weight_sq_sum" == plot):
                            rebinned = rebinned/(genWeightSum**2)
                        else:
                            rebinned = rebinned/genWeightSum

                    if (plot+string) not in plotWeights:
                        plotWeights[(plot+string)] = {process: rebinned}
                    else:
                        if process in plotWeights[(plot+string)]:
                            plotWeights[(plot+string)][process] = plotWeights[(plot+string)][process] + rebinned
                        else:
                            plotWeights[(plot+string)][process] = rebinned
                        
    # Combine QCD components
    qcd_components = ["QCD40to70", "QCD70to100", "QCD100to200", "QCD200to400", "QCD400to600", 
                     "QCD600to800", "QCD800to1000", "QCD1000to1200", "QCD1200to1500", "QCD1500to2000", "QCD2000"]

    # Combine TTbar components
    ttbar_components = ["TTTo4Q", "TTToLNu2Q"]

    # Combine 2024 data
    data_components = ["2024C", "2024D", "2024E", "2024F", "2024G", "2024H", "2024I"]

    # Combine weighted statistics for QCD
    bg_stats = combine_weighted_stats(plotWeights, qcd_components+ttbar_components)
    for key in bg_stats.keys():
        if key in plotWeights:
            plotWeights[key]["BG"] = bg_stats[key]
        else:
            plotWeights[key] = {"BG": bg_stats[key]}

    # Combine weighted statistics for 2024 data
    data_stats = combine_weighted_stats(plotWeights, data_components)
    for key in data_stats.keys():
        if key in plotWeights:
            plotWeights[key]["2024"] = data_stats[key]
        else:
            plotWeights[key] = {"2024": data_stats[key]}

    # **Plotting**
    # Plot average dxyErr and dzErr vs PT with error bars
    pt_bins = np.linspace(plotDict["scoutTrack_pt"][0], plotDict["scoutTrack_pt"][1], plotDict["scoutTrack_pt"][2])
    pt_centers = (pt_bins[:-1] + pt_bins[1:]) / 2

    for string in ["_barrel_jetMatched","_disk_jetMatched"]:
        mc_dxyErr_mean = plotWeights["dxyErr_mean"+string]["BG"]
        mc_dzErr_mean = plotWeights["dzErr_mean"+string]["BG"]
        mc_cov_mean = plotWeights["cov_mean"+string]["BG"]
        mc_dxyErr_stderr = plotWeights["dxyErr_stderr"+string]["BG"]
        mc_dzErr_stderr = plotWeights["dzErr_stderr"+string]["BG"]
        mc_cov_stderr = plotWeights["cov_stderr"+string]["BG"]
        # Create figure with 2 subplots for dxyErr and dzErr
        fig, axes = plt.subplots(1, 3, figsize=[32, 16])
        #fig.suptitle("Weighted Average Track Uncertainties vs PT "+string[1:], fontsize=16)

        # Plot 1: Average dxyErr vs PT with error bars
        ax = axes[0]
        ax.errorbar(pt_centers, mc_dxyErr_mean, 
                   yerr=mc_dxyErr_stderr,
                   label="MC (QCD+TTbar)", marker='o', markersize=4, capsize=2, alpha=0.8, linestyle='none', color='red')
        ax.errorbar(pt_centers, plotWeights["dxyErr_mean"+string]["2024"], 
                   yerr=plotWeights["dxyErr_stderr"+string]["2024"],
                   label="2024 Data", marker='^', markersize=4, color='black', capsize=2, linestyle='none')
        ax.set_xlabel("Track PT [GeV]")
        ax.set_ylabel("Average dxyErr [cm]")
        ax.set_title("Weighted Average dxyErr vs PT "+string[1:])
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(pt_bins[0], pt_bins[-1])

        # Plot 2: Average dzErr vs PT with error bars
        ax = axes[1]
        ax.errorbar(pt_centers, mc_dzErr_mean, 
                   yerr=mc_dzErr_stderr,
                   label="MC (QCD+TTbar)", marker='o', markersize=4, capsize=2, alpha=0.8, linestyle='none', color='red')
        ax.errorbar(pt_centers, plotWeights["dzErr_mean"+string]["2024"], 
                   yerr=plotWeights["dzErr_stderr"+string]["2024"],
                   label="2024 Data", marker='^', markersize=4, color='black', capsize=2, linestyle='none')
        ax.set_xlabel("Track PT [GeV]")
        ax.set_ylabel("Average dzErr [cm]")
        ax.set_title("Weighted Average dzErr vs PT "+string[1:])
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(pt_bins[0], pt_bins[-1])

        # Plot 3: Average dxydz covariance vs PT with error bars
        ax = axes[2]
        ax.errorbar(pt_centers, mc_cov_mean, 
                   yerr=mc_cov_stderr,
                   label="MC (QCD+TTbar)", marker='o', markersize=4, capsize=2, alpha=0.8, linestyle='none', color='red')
        ax.errorbar(pt_centers, plotWeights["cov_mean"+string]["2024"], 
                   yerr=plotWeights["cov_stderr"+string]["2024"],
                   label="2024 Data", marker='^', markersize=4, color='black', capsize=2, linestyle='none')
        ax.set_xlabel("Track PT [GeV]")
        ax.set_ylabel("Average dzdxy Covariance [sq cm]")
        ax.set_title("Weighted Average dzdxy Covariance vs PT "+string[1:])
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(pt_bins[0], pt_bins[-1])

        #plt.tight_layout()
        plt.savefig("trackAvgUnc_datamc"+string+".pdf")

        # Create ratio plots for error comparisons with uncertainties
        fig, axes = plt.subplots(1, 3, figsize=[32, 16])
        #fig.suptitle("Data/MC Ratio of Average Track Uncertainties "+string[1:], fontsize=16)

        # Calculate ratios (mc_dxyErr_mean etc already calculated above)
        with np.errstate(divide='ignore', invalid='ignore'):
            # Calculate ratios
            ratio_dxyErr = np.where(mc_dxyErr_mean > 0, 
                                   plotWeights["dxyErr_mean"+string]["2024"] / mc_dxyErr_mean, 0)
            ratio_dzErr = np.where(mc_dzErr_mean > 0, 
                                  plotWeights["dzErr_mean"+string]["2024"] / mc_dzErr_mean, 0)
            ratio_cov = np.where(mc_cov_mean > 0, 
                                  plotWeights["cov_mean"+string]["2024"] / mc_cov_mean, 0)

            # Propagate errors for ratios
            ratio_dxyErr_err = ratio_dxyErr * np.sqrt(
                np.where(plotWeights["dxyErr_mean"+string]["2024"] > 0, 
                        (plotWeights["dxyErr_stderr"+string]["2024"] / plotWeights["dxyErr_mean"+string]["2024"])**2, 0) +
                np.where(mc_dxyErr_mean > 0, (mc_dxyErr_stderr / mc_dxyErr_mean)**2, 0))

            ratio_dzErr_err = ratio_dzErr * np.sqrt(
                np.where(plotWeights["dzErr_mean"+string]["2024"] > 0,
                        (plotWeights["dzErr_stderr"+string]["2024"] / plotWeights["dzErr_mean"+string]["2024"])**2, 0) +
                np.where(mc_dzErr_mean > 0, (mc_dzErr_stderr / mc_dzErr_mean)**2, 0))

            ratio_cov_err = ratio_cov * np.sqrt(
                np.where(plotWeights["cov_mean"+string]["2024"] > 0,
                        (plotWeights["cov_stderr"+string]["2024"] / plotWeights["cov_mean"+string]["2024"])**2, 0) +
                np.where(mc_cov_mean > 0, (mc_cov_stderr / mc_cov_mean)**2, 0))

        # Ratio plot for dxyErr
        ax = axes[0]
        valid = ratio_dxyErr > 0
        ax.errorbar(pt_centers[valid], ratio_dxyErr[valid], yerr=ratio_dxyErr_err[valid],
                   marker='o', markersize=4, color='black', label='dxyErr Data/MC', capsize=3, linestyle='none')
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5)
        ax.set_xlabel("Track PT [GeV]")
        ax.set_ylabel("Data/MC Ratio")
        ax.set_title("dxyErr Data/MC Ratio vs PT "+string[1:])
        ax.set_ylim(1, 1.5)
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Ratio plot for dzErr
        ax = axes[1]
        valid = ratio_dzErr > 0
        ax.errorbar(pt_centers[valid], ratio_dzErr[valid], yerr=ratio_dzErr_err[valid],
                   marker='s', markersize=4, color='black', label='dzErr Data/MC', capsize=3, linestyle='none')
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5)
        ax.set_xlabel("Track PT [GeV]")
        ax.set_ylabel("Data/MC Ratio")
        ax.set_title("dzErr Data/MC Ratio vs PT "+string[1:])
        ax.set_ylim(1, 1.5)
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Ratio plot for dzErr
        ax = axes[2]
        valid = ratio_cov > 0
        ax.errorbar(pt_centers[valid], ratio_cov[valid], yerr=ratio_cov_err[valid],
                   marker='s', markersize=4, color='black', label='dzdxy cov Data/MC', capsize=3, linestyle='none')
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5)
        ax.set_xlabel("Track PT [GeV]")
        ax.set_ylabel("Data/MC Ratio")
        ax.set_title("dzdxyCov Data/MC Ratio vs PT "+string[1:])
        ax.set_ylim(1, 1.5)
        ax.grid(True, alpha=0.3)
        ax.legend()

        #plt.tight_layout()
        plt.savefig("trackUncRatio"+string+".pdf")

    # Store corrections
    corrections = {}
    for string in ["_barrel_jetMatched", "_disk_jetMatched"]:
        mc_dxyErr_mean = plotWeights["dxyErr_mean" + string]["BG"]
        mc_dzErr_mean = plotWeights["dzErr_mean" + string]["BG"]
        mc_cov_mean = plotWeights["cov_mean" + string]["BG"]
        mc_dxyErr_stderr = plotWeights["dxyErr_stderr" + string]["BG"]
        mc_dzErr_stderr = plotWeights["dzErr_stderr" + string]["BG"]
        mc_cov_stderr = plotWeights["cov_stderr" + string]["BG"]

        # Recalculate ratios and errors
        with np.errstate(divide='ignore', invalid='ignore'):
            ratio_dxyErr = np.where(mc_dxyErr_mean > 0,
                                    plotWeights["dxyErr_mean" + string]["2024"] / mc_dxyErr_mean, 0)
            ratio_dzErr = np.where(mc_dzErr_mean > 0,
                                   plotWeights["dzErr_mean" + string]["2024"] / mc_dzErr_mean, 0)
            ratio_cov = np.where(mc_cov_mean > 0,
                                 plotWeights["cov_mean" + string]["2024"] / mc_cov_mean, 0)

            ratio_dxyErr_err = ratio_dxyErr * np.sqrt(
                np.where(plotWeights["dxyErr_mean" + string]["2024"] > 0,
                         (plotWeights["dxyErr_stderr" + string]["2024"] / plotWeights["dxyErr_mean" + string]["2024"])**2, 0) +
                np.where(mc_dxyErr_mean > 0, (mc_dxyErr_stderr / mc_dxyErr_mean)**2, 0))

            ratio_dzErr_err = ratio_dzErr * np.sqrt(
                np.where(plotWeights["dzErr_mean" + string]["2024"] > 0,
                         (plotWeights["dzErr_stderr" + string]["2024"] / plotWeights["dzErr_mean" + string]["2024"])**2, 0) +
                np.where(mc_dzErr_mean > 0, (mc_dzErr_stderr / mc_dzErr_mean)**2, 0))

            ratio_cov_err = ratio_cov * np.sqrt(
                np.where(plotWeights["cov_mean" + string]["2024"] > 0,
                         (plotWeights["cov_stderr" + string]["2024"] / plotWeights["cov_mean" + string]["2024"])**2, 0) +
                np.where(mc_cov_mean > 0, (mc_cov_stderr / mc_cov_mean)**2, 0))
        region = string[1:]  # "barrel" or "disk"

        for label, ratio, ratio_err in [
        ("dxyErr", ratio_dxyErr, ratio_dxyErr_err),
        ("dzErr", ratio_dzErr, ratio_dzErr_err),
        ("dzdxyCov", ratio_cov, ratio_cov_err),
        ]:
            valid = (ratio > 0) & (ratio_err > 0)
            x_fit = pt_centers[valid]
            y_fit = ratio[valid]
            yerr_fit = ratio_err[valid]

            # Look up config
            cfg = fit_config[(label, region)]
            model_info = models[cfg["model"]]
            fit_func = model_info["func"]
            npar = model_info["npar"]

            try:
                popt, pcov = curve_fit(fit_func, x_fit, y_fit, p0=cfg["p0"],
                                       sigma=yerr_fit, absolute_sigma=True,
                                       bounds=cfg["bounds"], maxfev=10000)
                perr = np.sqrt(np.diag(pcov))

                # Reduced chi-squared
                residuals = y_fit - fit_func(x_fit, *popt)
                chi2 = np.sum((residuals / yerr_fit)**2)
                ndf = len(x_fit) - npar
                red_chi2 = chi2 / ndf if ndf > 0 else np.inf

                param_str = ", ".join(f"{chr(97+i)}={popt[i]:.6f}+-{perr[i]:.6f}" for i in range(npar))
                print(f"{label}_{region} [{cfg['model']}]: {param_str}")
                print(f"  chi2/ndf = {chi2:.2f}/{ndf} = {red_chi2:.3f}")

            except RuntimeError as e:
                print(f"Fit failed for {label}_{region}: {e}")
                popt = cfg["p0"]
                red_chi2 = np.inf

            # Evaluate fit at all bin centers and save
            fit_values = fit_func(pt_centers, *popt)
            key = f"ratio_correction_{label}_{region}"
            corrections[key] = fit_values

            #fname = f"{key}.npy"
            #np.save(fname, fit_values)
            #print(f"  Saved {fname}  (shape={fit_values.shape})")

            # Plot
            fig, ax = plt.subplots(figsize=[10, 6])
            ax.errorbar(x_fit, y_fit, yerr=yerr_fit,
                         marker='o', markersize=4, color='blue', capsize=3,
                         linestyle='none', label='Data/MC')
            x_smooth = np.linspace(pt_bins[0], pt_bins[-1], 200)
            param_lines = "\n".join(f"{chr(97+i)}={popt[i]:.4g}" for i in range(npar))
            ax.plot(x_smooth, fit_func(x_smooth, *popt), 'r-',
                    label=(f'Fit: {model_info["label"]}\n'
                           f'{param_lines}\n'
                           f'$\\chi^2$/ndf = {chi2:.1f}/{ndf} = {red_chi2:.2f}'))
            ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5)
            ax.set_xlabel("Track PT [GeV]")
            ax.set_ylabel("Data/MC Ratio")
            ax.set_title(f"{label} Data/MC Ratio Fit - {region}")
            ax.set_ylim(1, 1.5)
            ax.set_xlim(pt_bins[0], pt_bins[-1])
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.savefig(f"dataMCUncRatioFit_{region}_{label}.pdf")
    #np.savez("ratio_uncertaintyCorrections_v33.npz", **corrections)

        
if __name__=="__main__":
    main()
