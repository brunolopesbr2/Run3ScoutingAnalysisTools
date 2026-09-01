from currentLimits import build_limits
from sampleDict import makeDict
import uproot
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
import awkward as ak
import numpy as np
import mplhep as hep
hep.style.use("CMS")

# ---- what to plot ----
BRANCH = "vertTrack_dxy"          # per-vertex scoutVert_* or per-track vertTrack_*

# ---- peak window (on scoutVert_mass) ----
MASS_MIN, MASS_MAX = 0.46, 0.54

# ---- mass fit range / binning (window edges should land on bin edges) ----
FIT_MIN, FIT_MAX, FIT_NBINS = 0.3, 0.7, 41

# ---- target-branch histogram binning ----
BRANCH_MIN, BRANCH_MAX, BRANCH_NBINS = 0.0, 0.16, 9

# ---- misc ----
NORMALIZE   = True                # unit-area shapes; False = absolute subtracted yields
MAX_WORKERS = 16
DATA_ERAS   = None                # None = sum all eras in signalDict
XSEC_LUMI_SCALE = 1  # kept from the original script

# ---- ROOT output ----
SAVE_ROOT = True                  # write data/MC/ratio (+mass fit) histograms to a .root file
ROOT_OUT  = "TrackEffCorrection.root"                  # None -> f"{BRANCH}_sidebandsub.root"

def process_root_file(args):
    rootFile, process, is_mc, cfg = args
    print(f"Processing {rootFile}")

    massBins = cfg["massBins"]
    tgtBins  = cfg["tgtBins"]
    mass_min = cfg["mass_min"]
    mass_max = cfg["mass_max"]
    branch   = cfg["branch"]
    xsec     = cfg["xsec_scale"]
    is_track = branch.startswith("vertTrack")

    output = {}
    genWeightSum = 0.0

    with uproot.open(rootFile) as file:
        output["genWeightSum"] = {}
        if is_mc:
            genWeightSum = file["K0Filter/genWeightsSkim"].values()[0]

        tree = file["K0Tree/objectTree"]

        branches = ["scoutVert_mass", "scoutVert_dBV", "scoutVert_ctau",
                    "scoutVert_costh2", "scoutVert_nTracks", "scoutVert_chi2", "scoutVert_pt",
                    "muon_phi", "dimuon_mass", "weight", branch]
        if is_track:
            branches += ["vertTrack_iVtx", "scoutVert_dBVErr"]
        if is_mc:
            branches += ["uncorrectedWeight", "weight_PU_BCDEFGHI_nominal",
                         "weight_PU_BCDEFGHI_up", "weight_PU_BCDEFGHI_down"]
        branches = list(dict.fromkeys(branches))

        for batch in tree.iterate(branches, library="ak", step_size=40000):

            # ---- event weights ----
            if is_mc:
                w    = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_nominal"] * xsec
                w_up = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_up"]      * xsec
                w_dn = batch["uncorrectedWeight"] * batch["weight_PU_BCDEFGHI_down"]    * xsec
                w, w_up, w_dn = w / genWeightSum, w_up / genWeightSum, w_dn / genWeightSum
            else:
                w = ak.ones_like(batch["weight"])

            # ---- per-object mass, target and vertex selection ----
            # ---- selections ----
            if is_track:
                iVtx  = batch["vertTrack_iVtx"]
                vmass = batch["scoutVert_mass"]                       # per-vertex (mass fit)
                vsel  = ((batch["scoutVert_dBV"]    >= 0.01)   &
                         (batch["scoutVert_dBV"]    <  2.0)    &
                         (batch["scoutVert_ctau"]   >= 0.0268) &
                         (batch["scoutVert_costh2"]  > 0.9) &
                         (batch["scoutVert_pt"]  > 2) &
                         (batch["scoutVert_chi2"]  < 7))
                tmass = batch["scoutVert_mass"][iVtx]                 # per-track parent mass (window split)
                tgt   = batch[branch]                                 # per-track target
                tsel  = vsel[iVtx]                                    # same cut, mapped to tracks
            else:
                vmass = batch["scoutVert_mass"]; tmass = batch["scoutVert_mass"]
                tgt   = batch[branch]
                vsel  = ((batch["scoutVert_dBV"]    >= 0.01)   &
                         (batch["scoutVert_dBV"]    <  2.0)    &
                         (batch["scoutVert_ctau"]   >= 0.0268) &
                         (batch["scoutVert_costh2"]  > 0.9)&
                         (batch["scoutVert_pt"]  > 2) &
                         (batch["scoutVert_chi2"]  < 7))
                tsel  = vsel

            vmass        = vmass[vsel]
            tmass, tgt   = tmass[tsel], tgt[tsel]

            # ---- event-level dimuon (Z) requirement ----
            evt = ((ak.num(batch["muon_phi"], axis=1) >= 2) &
                   ak.any((batch["dimuon_mass"] > 70) & (batch["dimuon_mass"] < 110), axis=1))
            vmass        = vmass[evt]
            tmass, tgt   = tmass[evt], tgt[evt]
            w = w[evt]
            if is_mc:
                w_up, w_dn = w_up[evt], w_dn[evt]

            def flat(x):
                return ak.to_numpy(ak.flatten(x, axis=None)).astype(float)

            # ---- per-VERTEX pipeline (mass fit) ----
            vmassFlat = flat(vmass)
            vwFlat    = flat(ak.broadcast_arrays(w, vmass)[0])
            if is_mc:
                vwUp = flat(ak.broadcast_arrays(w_up, vmass)[0])
                vwDn = flat(ak.broadcast_arrays(w_dn, vmass)[0])

            # ---- per-TRACK pipeline (target) ----
            tmassFlat = flat(tmass)
            tgtFlat   = flat(tgt)
            twFlat    = flat(ak.broadcast_arrays(w, tgt)[0])
            if is_mc:
                twUp = flat(ak.broadcast_arrays(w_up, tgt)[0])
                twDn = flat(ak.broadcast_arrays(w_dn, tgt)[0])

            # ---- mass histograms: one entry per vertex ----
            m_n,  _ = np.histogram(vmassFlat, bins=massBins, weights=vwFlat)
            m_n2, _ = np.histogram(vmassFlat, bins=massBins, weights=vwFlat**2)

            # ---- target window split: each track uses its parent-vertex mass ----
            inWin  = (tmassFlat >= mass_min) & (tmassFlat < mass_max)
            inFit  = (tmassFlat >= massBins[0]) & (tmassFlat < massBins[-1])
            outWin = inFit & ~inWin

            def h(vals, wgt):
                return np.histogram(vals, bins=tgtBins, weights=wgt)[0]

            contrib = {
                "mass": m_n, "mass_sq": m_n2,
                "tgt_in":     h(tgtFlat[inWin],  twFlat[inWin]),
                "tgt_in_sq":  h(tgtFlat[inWin],  twFlat[inWin]**2),
                "tgt_out":    h(tgtFlat[outWin], twFlat[outWin]),
                "tgt_out_sq": h(tgtFlat[outWin], twFlat[outWin]**2),
            }
            if is_mc:
                contrib["mass_PU_up"], _   = np.histogram(vmassFlat, bins=massBins, weights=vwUp)
                contrib["mass_PU_down"], _ = np.histogram(vmassFlat, bins=massBins, weights=vwDn)
                contrib["tgt_in_PU_up"]    = h(tgtFlat[inWin],  twUp[inWin])
                contrib["tgt_in_PU_down"]  = h(tgtFlat[inWin],  twDn[inWin])
                contrib["tgt_out_PU_up"]   = h(tgtFlat[outWin], twUp[outWin])
                contrib["tgt_out_PU_down"] = h(tgtFlat[outWin], twDn[outWin])

            for key, arr in contrib.items():
                output.setdefault(key, {})
                output[key][process] = output[key].get(process, np.zeros_like(arr)) + arr

    return output

def parallel_processing(files_dict, is_mc, cfg, max_workers=16):
    results = {}
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_root_file, (f, p, is_mc, cfg)): (f, p)
                   for p, files in files_dict.items() for f in files}
        for future in as_completed(futures):
            result = future.result()
            for key in result:
                results.setdefault(key, {})
                for process in result[key]:
                    results[key][process] = results[key].get(process, 0) + result[key][process]
    return results

def combine(res, keys, group_name, members):
    """Normalize MC sub-processes by genWeightSum and sum members into group_name."""
    for proc, gw in res.get("genWeightSum", {}).items():
        for key in keys:
            if proc in res.get(key, {}):
                res[key][proc] = res[key][proc] / (gw**2 if key.endswith("_sq") else gw)
    for key in keys:
        total = None
        for proc in members:
            if proc not in res.get(key, {}):
                continue
            arr = np.asarray(res[key][proc], dtype=float)
            total = arr.copy() if total is None else total + arr
        res[key][group_name] = total

def fit_sideband(mass_n, mass_n2, massBins, mass_min, mass_max):
    """Quadratic fit to sideband bins; return coeffs, window integral, bkg yield."""
    centers = 0.5 * (massBins[:-1] + massBins[1:])
    binw = massBins[1] - massBins[0]
    sb = (massBins[1:] <= mass_min) | (massBins[:-1] >= mass_max)
    x, y = centers[sb], mass_n[sb]
    ye = np.sqrt(np.maximum(mass_n2[sb], 0.0))
    good = ye > 0
    if good.sum() >= 3:
        coeffs = np.polyfit(x[good], y[good], 2, w=1.0 / ye[good])
    else:
        coeffs = np.polyfit(x, y, 2)
    P = np.poly1d(coeffs)
    I = np.polyint(P)
    integral = I(mass_max) - I(mass_min)   # area under the fit in the window
    bkg_yield = integral / binw            # -> predicted event count in the window
    return coeffs, integral, bkg_yield

def subtract(tin, tout, bkg_yield, tin2=None, tout2=None):
    sb_total = float(np.sum(tout))
    scale = (bkg_yield / sb_total) if sb_total > 0 else 0.0
    sig = tin - scale * tout
    err2 = (tin2 + (scale**2) * tout2) if (tin2 is not None and tout2 is not None) else None
    return sig, err2, scale

def run_subtraction(res, label, group, is_mc, massBins, mass_min, mass_max):
    def g(key):
        return np.asarray(res[key][group], dtype=float)

    coeffs, integral, byield = fit_sideband(g("mass"), g("mass_sq"), massBins, mass_min, mass_max)
    if byield < 0:
        print(f"  [warning] {label}: fitted background yield is negative ({byield:.3g}).")

    sig, sig_e2, scale = subtract(g("tgt_in"), g("tgt_out"), byield, g("tgt_in_sq"), g("tgt_out_sq"))
    print(f"  {label}: fit integral over window = {integral:.4g}, "
          f"pred. bkg yield = {byield:.4g}, sideband scale = {scale:.4g}")

    out = {"mass_n": g("mass"), "mass_n2": g("mass_sq"), "coeffs": coeffs,
           "integral": integral, "bkg_yield": byield,
           "sig": sig, "sig_e2": sig_e2, "scale": scale}
    if is_mc:
        _, _, byield_up = fit_sideband(g("mass_PU_up"),   g("mass_sq"), massBins, mass_min, mass_max)
        _, _, byield_dn = fit_sideband(g("mass_PU_down"), g("mass_sq"), massBins, mass_min, mass_max)
        sig_up, _, _ = subtract(g("tgt_in_PU_up"),   g("tgt_out_PU_up"),   byield_up)
        sig_dn, _, _ = subtract(g("tgt_in_PU_down"), g("tgt_out_PU_down"), byield_dn)
        out["sys_up_raw"] = sig_up - sig
        out["sys_dn_raw"] = sig_dn - sig
    return out

def compute_subtracted_curves(dataR, mcR, tgtBins, normalize=True):
    """Single source of truth for the subtracted data/MC curves and their
    uncertainties. Returns exactly the arrays that plot_subtracted draws and
    that save_root writes, so the figure and the .root file always agree."""
    centers = 0.5 * (tgtBins[:-1] + tgtBins[1:])
    binw = tgtBins[1] - tgtBins[0]
    d, d_e2 = dataR["sig"], dataR["sig_e2"]
    m, m_e2 = mcR["sig"],  mcR["sig_e2"]

    if normalize:
        dI, mI = binw * np.sum(d), binw * np.sum(m)
        if dI <= 0 or not np.isfinite(dI):
            print("  [warning] data subtracted integral <= 0; using absolute yields."); dI = 1.0
        if mI <= 0 or not np.isfinite(mI):
            print("  [warning] MC subtracted integral <= 0; using absolute yields."); mI = 1.0
    else:
        dI = mI = 1.0

    dV = d / dI;  dE = np.sqrt(np.maximum(d_e2, 0.0)) / abs(dI)
    mV = m / mI;  mE_stat = np.sqrt(np.maximum(m_e2, 0.0)) / abs(mI)

    su, sd = mcR["sys_up_raw"] / mI, mcR["sys_dn_raw"] / mI
    sys_hi = np.maximum.reduce([su, sd, np.zeros_like(su)])
    sys_lo = np.abs(np.minimum.reduce([su, sd, np.zeros_like(su)]))
    mE_hi = np.sqrt(mE_stat**2 + sys_hi**2)
    mE_lo = np.sqrt(mE_stat**2 + sys_lo**2)

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio    = dV / mV
        ratio_e  = dE / mV
        stat_rel = mE_stat / np.abs(mV)
        hi_rel   = mE_hi / np.abs(mV)
        lo_rel   = mE_lo / np.abs(mV)

    return dict(centers=centers, edges=np.asarray(tgtBins, float), binw=binw,
                dV=dV, dE=dE, mV=mV, mE_stat=mE_stat, mE_hi=mE_hi, mE_lo=mE_lo,
                sys_hi=sys_hi, sys_lo=sys_lo,
                ratio=ratio, ratio_e=ratio_e,
                stat_rel=stat_rel, hi_rel=hi_rel, lo_rel=lo_rel)

def plot_mass_fit(dataR, mcR, massBins, mass_min, mass_max, branch):
    centers = 0.5 * (massBins[:-1] + massBins[1:])
    xs = np.linspace(massBins[0], massBins[-1], 400)
    fig, axes = plt.subplots(2, 1, figsize=[10, 10], sharex=True)
    for ax, R, name, col in ((axes[0], dataR, "Data", "black"),
                             (axes[1], mcR,   "MC",   "tab:blue")):
        ne = np.sqrt(np.maximum(R["mass_n2"], 0.0))
        ax.errorbar(centers, R["mass_n"], yerr=ne, linestyle="none", marker=".",
                    color=col, label=f"{name} mass")
        ax.plot(xs, np.poly1d(R["coeffs"])(xs), color="red", label="quadratic sideband fit")
        ax.axvspan(mass_min, mass_max, color="orange", alpha=0.15, label="window")
        ax.set_ylabel("weighted events / bin")
        ax.legend(fontsize=9)
        ax.text(0.02, 0.95,
                f"{name}\nfit integral = {R['integral']:.3g}\npred. bkg yield = {R['bkg_yield']:.3g}",
                transform=ax.transAxes, va="top", fontsize=9,
                bbox=dict(boxstyle="round", fc="white", alpha=0.7))
    axes[1].set_xlabel("scoutVert_mass [GeV]")
    fig.suptitle(f"scoutVert_mass sideband fit (target: {branch})")
    fig.tight_layout()
    fig.savefig("scoutVert_mass_sidebandfit.pdf", bbox_inches="tight")

def plot_subtracted(dataR, mcR, tgtBins, branch, normalize=True):
    c = compute_subtracted_curves(dataR, mcR, tgtBins, normalize)
    centers = c["centers"]
    dV, dE = c["dV"], c["dE"]
    mV, mE_stat, mE_hi, mE_lo = c["mV"], c["mE_stat"], c["mE_hi"], c["mE_lo"]
    ratio, ratio_e = c["ratio"], c["ratio_e"]
    stat_rel, hi_rel, lo_rel = c["stat_rel"], c["hi_rel"], c["lo_rel"]

    fig, (ax, rax) = plt.subplots(2, 1, figsize=[12, 12],
                                  gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
    fig.subplots_adjust(hspace=0.06)
    edges_step = np.repeat(tgtBins, 2)[1:-1]

    ax.stairs(mV, tgtBins, color="tab:blue", label="MC (subtracted)")
    ax.fill_between(edges_step, np.repeat(mV - mE_lo, 2), np.repeat(mV + mE_hi, 2),
                    alpha=0.3, color="tab:blue", linewidth=0, label=r"MC stat $\oplus$ sys")
    ax.errorbar(centers, dV, yerr=dE, linestyle="none", marker=".", color="black",
                label="Data (subtracted)", zorder=3)
    ax.axhline(0, color="gray", lw=0.8, ls=":")
    ax.set_ylabel("A.U" if normalize else "subtracted yield")
    ax.legend(fontsize=10)

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = dV / mV
        ratio_e = dE / mV
        stat_rel = mE_stat / np.abs(mV)
        hi_rel = mE_hi / np.abs(mV)
        lo_rel = mE_lo / np.abs(mV)

    rax.fill_between(edges_step, 1 - np.repeat(stat_rel, 2), 1 + np.repeat(stat_rel, 2),
                     alpha=0.5, color="gray", hatch="///", edgecolor="gray",
                     linewidth=0, label="MC stat", zorder=1)
    rax.fill_between(edges_step, 1 - np.repeat(lo_rel, 2), 1 + np.repeat(hi_rel, 2),
                     alpha=0.3, color="blue", linewidth=0, label=r"MC stat $\oplus$ sys", zorder=2)
    rax.errorbar(centers, ratio, yerr=ratio_e, linestyle="none", marker=".",
                 color="black", label="Data", zorder=3)
    rax.hlines(1, tgtBins[0], tgtBins[-1], linestyle="dashed", color="black", linewidth=1)
    rax.set_ylim(0.7, 1.3)
    rax.set_ylabel("Data/MC"); rax.set_xlabel(branch)
    rax.legend(loc="best", fontsize=10, ncol=3)

    fig.suptitle(f"Sideband-subtracted {branch}")
    fig.savefig(f"{branch}_sidebandsub.pdf", bbox_inches="tight")

def _make_th1f(name, values, edges):
    """Build a writable TH1F (float32) with bin contents `values` over `edges`.
    No per-bin errors are stored -- the uncertainty is carried by the separate
    +/- 1 sigma histograms. Written via uproot.recreate()[name] = _make_th1f(...).
    Requires uproot >= 4 (uses the low-level TH1x writer so the type is forced to
    TH1F rather than the TH1D that boost-histogram/hist would produce)."""
    from uproot.writing.identify import to_TH1x, to_TAxis
    values  = np.asarray(values, dtype=np.float32)
    # Empty-MC bins give ratio = x/0 (inf) or 0/0 (nan); ROOT can't build an axis
    # range from non-finite bins (TCanvas::ResizePad Inf/NaN), so zero them out.
    values  = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
    edges   = np.asarray(edges,  dtype=float)
    nb      = len(values)
    centers = 0.5 * (edges[:-1] + edges[1:])
    data  = np.zeros(nb + 2, dtype=np.float32); data[1:-1] = values  # float32 -> TH1F
    sumw2 = np.zeros(nb + 2, dtype=np.float64)          # fSumw2 must be TArrayD (float64)
    fTsumw   = float(np.nansum(values))
    fTsumwx  = float(np.nansum(values * centers))
    fTsumwx2 = float(np.nansum(values * centers ** 2))
    axis = to_TAxis("xaxis", "", nb, float(edges[0]), float(edges[-1]))
    return to_TH1x(name, name, data, fTsumw, fTsumw, fTsumw,
                   fTsumwx, fTsumwx2, sumw2, axis)

def save_root(dataR, mcR, tgtBins, branch, filename, normalize=True):
    """Write three TH1F histograms of the Data/MC ratio R = D / M to `filename`:

        ratio             nominal Data/MC
        ratio_plus1sigma  ratio + 1 sigma  of the combined error
        ratio_minus1sigma ratio - 1 sigma  of the combined error

    The 1 sigma combines, in quadrature, the data statistical error (sigma_D),
    the MC statistical error, and the MC systematic error, propagated into the
    ratio.  With R = D / M and independent D, M:

        sigma_R^2 = (sigma_D / M)^2 + (|R| * sigma_M / |M|)^2

    sigma_M is the MC stat (+) sys uncertainty and is asymmetric here: the +1
    sigma histogram uses its upper side (mE_hi) and the -1 sigma histogram uses
    its lower side (mE_lo).  Since mE_hi/mE_lo already fold MC stat and syst
    together, the result includes all three requested sources.
    """
    c = compute_subtracted_curves(dataR, mcR, tgtBins, normalize)
    ratio, dE, mV = c["ratio"], c["dE"], c["mV"]
    mE_hi, mE_lo  = c["mE_hi"], c["mE_lo"]

    with np.errstate(divide="ignore", invalid="ignore"):
        data_term = dE / np.abs(mV)                        # data stat -> ratio
        mc_up     = np.abs(ratio) * mE_hi / np.abs(mV)     # MC stat (+) sys, + side
        mc_dn     = np.abs(ratio) * mE_lo / np.abs(mV)     # MC stat (+) sys, - side
        sigma_up  = np.sqrt(data_term ** 2 + mc_up ** 2)
        sigma_dn  = np.sqrt(data_term ** 2 + mc_dn ** 2)
        ratio_up  = ratio + sigma_up
        # ratio - 1 sigma can dip below 0 in low-stat bins (sigma_dn > ratio),
        # which is unphysical for a ratio of positive yields; floor it at 0.
        ratio_dn  = np.maximum(ratio - sigma_dn, 0.0)

    with uproot.recreate(filename) as f:
        f["ratio"]             = _make_th1f("ratio",             ratio,    tgtBins)
        f["ratio_plus1sigma"]  = _make_th1f("ratio_plus1sigma",  ratio_up, tgtBins)
        f["ratio_minus1sigma"] = _make_th1f("ratio_minus1sigma", ratio_dn, tgtBins)

    print(f"  wrote 3 TH1F ratio histograms to {filename}")
    
def main():
    limitDict = build_limits("../EXO-23-13-ExoHiggsBRLimitvsLifetime.root","../EXO-19-13-RPVSUSYSigmaBSquaredLimitsMassvsLifetime.root")
    signalDict, processDict = makeDict("v4-K0",["2024"],["QCD","DY","Wto","WW","WZ","ZZ","TTTo"])

    massBins = np.linspace(FIT_MIN, FIT_MAX, FIT_NBINS)
    tgtBins  = np.linspace(BRANCH_MIN, BRANCH_MAX, BRANCH_NBINS)
    for edge in (MASS_MIN, MASS_MAX):
        if np.min(np.abs(massBins - edge)) > 1e-9:
            print(f"  [warning] window edge {edge} is not on a mass-bin edge; "
                  f"sideband/window split may be off by up to one bin.")

    cfg = {"massBins": massBins, "tgtBins": tgtBins,
           "mass_min": MASS_MIN, "mass_max": MASS_MAX, "branch": BRANCH,
           "xsec_scale": XSEC_LUMI_SCALE,
           "multiFileProcesses": [p for p, f in processDict.items() if len(f) > 1]}

    bg  = parallel_processing(processDict, is_mc=True,  cfg=cfg, max_workers=MAX_WORKERS)
    sig = parallel_processing(signalDict, is_mc=False, cfg=cfg, max_workers=MAX_WORKERS)

    mc_keys = ["mass", "mass_sq", "mass_PU_up", "mass_PU_down",
               "tgt_in", "tgt_in_sq", "tgt_in_PU_up", "tgt_in_PU_down",
               "tgt_out", "tgt_out_sq", "tgt_out_PU_up", "tgt_out_PU_down"]
    data_keys = ["mass", "mass_sq", "tgt_in", "tgt_in_sq", "tgt_out", "tgt_out_sq"]

    combine(bg, mc_keys, "MC", members=list(processDict.keys()))
    eras = DATA_ERAS if DATA_ERAS else list(signalDict.keys())
    combine(sig, data_keys, "Data", members=eras)

    print("Sideband subtraction:")
    dataR = run_subtraction(sig, "Data", "Data", False, massBins, MASS_MIN, MASS_MAX)
    mcR   = run_subtraction(bg,  "MC",   "MC",   True,  massBins, MASS_MIN, MASS_MAX)

    plot_mass_fit(dataR, mcR, massBins, MASS_MIN, MASS_MAX, BRANCH)
    plot_subtracted(dataR, mcR, tgtBins, BRANCH, normalize=NORMALIZE)

    if SAVE_ROOT:
        root_out = ROOT_OUT or f"{BRANCH}_ratio.root"
        save_root(dataR, mcR, tgtBins, BRANCH, root_out, normalize=NORMALIZE)
    
if __name__=="__main__":
    main()
