#!/usr/bin/env python3
"""Pull plot for a signal-injection test from `combine -M MultiDimFit --algo singles -t N` output.

Pull per toy = (r_hat - r_inj) / sigma, with sigma chosen by --error:
  side (default): profile-likelihood uncertainty on the side facing r_inj
                  (low error if r_hat > r_inj, else high error). With asymmetric
                  errors this gives a jump in the pull density at 0 of size ~ sigma_lo/sigma_hi.
  avg:            average error 0.5*(sigma_lo + sigma_hi), as in the Combine bias-study docs.
                  No jump at 0, but any skew in r_hat shows up directly in the pulls.
Also prints the interval coverage (fraction of toys with lo <= r_inj <= hi), which
does not depend on the choice of pull definition.

Usage:
  python3 plot_injection_pulls.py higgsCombine_inj0p05.MultiDimFit.mH125.1.root \
      --rinj 0.05 --rmin -0.2 --rmax 0.3 -o pulls_inj0p05 [--error avg]
"""
import argparse
import numpy as np
import uproot
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

p = argparse.ArgumentParser()
p.add_argument("input", help="MultiDimFit output ROOT file (hadd the files first if split into jobs)")
p.add_argument("--rinj", type=float, required=True, help="injected signal strength (--expectSignal)")
p.add_argument("--rmin", type=float, default=None, help="--rMin used in the fits, to flag toys whose crossing hit the range edge")
p.add_argument("--rmax", type=float, default=None, help="--rMax used in the fits")
p.add_argument("-o", "--output", default="pulls", help="output file stem (writes .png and .pdf)")
p.add_argument("--range", type=float, default=4.0, help="pull histogram range +/- value")
p.add_argument("--nbins", type=int, default=40)
p.add_argument("--error", choices=["side", "avg"], default="side",
               help="pull denominator: 'side' = error on the side facing r_inj, 'avg' = 0.5*(lo + hi errors)")
args = p.parse_args()

t = uproot.open(args.input)["limit"].arrays(["r", "quantileExpected", "iToy", "iSeed"], library="np")

# Group rows by (seed, toy): one best-fit row (quantileExpected == -1) plus two crossing rows.
key = t["iSeed"].astype(np.int64) * 10_000_000 + t["iToy"].astype(np.int64)
order = np.argsort(key, kind="stable")
key, r, q = key[order], t["r"][order], t["quantileExpected"][order]
_, starts, counts = np.unique(key, return_index=True, return_counts=True)

edge_tol = 1e-4 * ((args.rmax - args.rmin) if (args.rmin is not None and args.rmax is not None) else 1.0)
pulls, los, his, n_bad, n_edge = [], [], [], 0, 0
for s, c in zip(starts, counts):
    rr, qq = r[s:s + c], q[s:s + c]
    best, cross = rr[qq == -1], rr[qq != -1]
    if len(best) != 1 or len(cross) != 2:
        n_bad += 1  # failed fit / missing crossing rows
        continue
    rhat, lo, hi = best[0], cross.min(), cross.max()
    if (args.rmin is not None and abs(lo - args.rmin) < edge_tol) or \
       (args.rmax is not None and abs(hi - args.rmax) < edge_tol):
        n_edge += 1  # crossing not found inside the range; error is meaningless
        continue
    if args.error == "avg":
        err = 0.5 * (hi - lo)
    else:
        err = (rhat - lo) if rhat > args.rinj else (hi - rhat)
    if err <= 0:
        n_bad += 1
        continue
    pulls.append((rhat - args.rinj) / err)
    los.append(lo)
    his.append(hi)

pulls = np.array(pulls)
n = len(pulls)
if n < 10:
    raise SystemExit(f"Only {n} usable toys (bad={n_bad}, edge={n_edge}); check the input file and fit range.")

mean, std = pulls.mean(), pulls.std(ddof=1)
mean_err, std_err = std / np.sqrt(n), std / np.sqrt(2 * (n - 1))

edges = np.linspace(-args.range, args.range, args.nbins + 1)
h, _ = np.histogram(pulls, bins=edges)
centers = 0.5 * (edges[1:] + edges[:-1])
n_out = np.sum(np.abs(pulls) > args.range)

def gauss(x, A, mu, sig):
    return A * np.exp(-0.5 * ((x - mu) / sig) ** 2)

m = h > 0
popt, pcov = curve_fit(gauss, centers[m], h[m], p0=[h.max(), 0.0, 1.0],
                       sigma=np.sqrt(h[m]), absolute_sigma=True)
perr = np.sqrt(np.diag(pcov))
popt[2] = abs(popt[2])

fig, ax = plt.subplots(figsize=(7, 5))
ax.errorbar(centers, h, yerr=np.sqrt(h), fmt="ko", ms=3, label=f"Toys (N = {n})")
x = np.linspace(-args.range, args.range, 400)
ax.plot(x, gauss(x, *popt), "r-",
        label=f"Gaussian fit: $\\mu$ = {popt[1]:.3f} $\\pm$ {perr[1]:.3f}, "
              f"$\\sigma$ = {popt[2]:.3f} $\\pm$ {perr[2]:.3f}")
ax.axvline(0, color="gray", ls="--", lw=1)
if args.error == "avg":
    ax.set_xlabel(r"$(\hat{r} - r_{\mathrm{inj}}) / \frac{1}{2}(\sigma_{\mathrm{lo}} + \sigma_{\mathrm{hi}})$")
else:
    ax.set_xlabel(r"$(\hat{r} - r_{\mathrm{inj}}) / \sigma_{\hat{r}}$ (side facing $r_{\mathrm{inj}}$)")
ax.set_ylabel("Toys / bin")
ax.set_title(f"Signal injection test, $r_{{\\mathrm{{inj}}}}$ = {args.rinj}")
ax.legend(loc="upper left", fontsize=9, frameon=False)
ax.text(0.98, 0.97,
        f"mean = {mean:.3f} $\\pm$ {mean_err:.3f}\nstd = {std:.3f} $\\pm$ {std_err:.3f}\n"
        f"failed = {n_bad}, edge = {n_edge}\n|pull| > {args.range:g}: {n_out}",
        transform=ax.transAxes, ha="right", va="top", fontsize=9)
ax.set_ylim(0, 1.35 * max(h.max(), 1))
fig.tight_layout()
fig.savefig(args.output + ".png", dpi=150)
fig.savefig(args.output + ".pdf")

print(f"r_inj = {args.rinj}: N = {n}, failed = {n_bad}, edge = {n_edge}, |pull| > {args.range:g}: {n_out}")
print(f"  sample mean = {mean:.3f} +/- {mean_err:.3f}, sample std = {std:.3f} +/- {std_err:.3f}")
print(f"  Gaussian fit: mu = {popt[1]:.3f} +/- {perr[1]:.3f}, sigma = {popt[2]:.3f} +/- {perr[2]:.3f}")
los, his = np.array(los), np.array(his)
cov = np.mean((los <= args.rinj) & (args.rinj <= his))
below = np.mean(his < args.rinj)
above = np.mean(los > args.rinj)
cov_err = np.sqrt(cov * (1 - cov) / n)
print(f"  coverage of [lo, hi] = {cov:.3f} +/- {cov_err:.3f} (expect 0.683); "
      f"interval below r_inj = {below:.3f}, above r_inj = {above:.3f} (expect 0.159 each)")
print(f"  pull denominator: {args.error}")
print(f"  wrote {args.output}.png and {args.output}.pdf")
