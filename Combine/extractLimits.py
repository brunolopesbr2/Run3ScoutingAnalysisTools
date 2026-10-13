import ROOT
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import uproot
hep.style.use("CMS")

masses = [55]
ctaus = [0.1, 1, 10]

results = {}  # (mass, ctau) -> {obs, exp, exp_1up, exp_1down, exp_2up, exp_2down}

for mass in masses:
    for ctau in ctaus:
        if(ctau==0.1):
            #f = ROOT.TFile.Open(f"Higgs-M{mass}-cT0p1AsymptoticLimits.root")
            f = ROOT.TFile.Open(f"Hto2Sto4D-cT0p1-MS{mass}AsymptoticLimits.root")
            
        else:
            #f = ROOT.TFile.Open(f"Higgs-M{mass}-cT{ctau}AsymptoticLimits.root")
            f = ROOT.TFile.Open(f"Hto2Sto4D-cT{ctau}-MS{mass}AsymptoticLimits.root")
        tree = f.Get("limit")
        
        limits = []
        for i, entry in enumerate(tree):
            limits.append(entry.limit)
        
        # Order: 2.5%, 16%, 50% (expected), 84%, 97.5%, observed
        results[(mass, ctau)] = {
            'exp_2down': limits[0],
            'exp_1down': limits[1],
            'exp': limits[2],
            'exp_1up': limits[3],
            'exp_2up': limits[4],
            #'obs': limits[5]
        }
        f.Close()

limitDict = {}
lim_cts = [0.3,0.5, 0.7,1,2,3,5,7,10]
with uproot.open("/afs/cern.ch/user/r/rmccarth/private/scouting/CMSSW_14_0_18_patch1/src/Run3ScoutingAnalysisTools/EXO-23-13-ExoHiggsBRLimitvsLifetime.root") as file:
    masses = [55,40,30,23,15]
    for i in range(2,11,2): #root file alternates between expected and observed limits
        folder = file["Figure 4b"]
        plot = folder["Graph1D_y"+str(i)]
        x = plot.member("fX")
        y = plot.member("fY")
        mass = masses[int(i/2)-1]
        for j in range(len(x)):
            y_lim = y[j]
            if(y_lim>8): 
                y_lim = 8
            limitDict[(mass, x[j])] = y_lim
        limitDict[(mass, 0.1)] = 8
# Pick a fixed lifetime slice
mass_fixed = 55  # GeV
fig, ax = plt.subplots(figsize=(10, 8))
ctaus = np.array([0.1, 1, 10])
#obs = np.array([results[(mass_fixed, ct)]['obs'] for ct in ctaus])
exp = np.array([results[(mass_fixed, ct)]['exp'] for ct in ctaus]) #* (8/52.23)
exp_1up = np.array([results[(mass_fixed, ct)]['exp_1up'] for ct in ctaus]) #* (8/52.23)
exp_1down = np.array([results[(mass_fixed, ct)]['exp_1down'] for ct in ctaus]) #* (8/52.23)
exp_2up = np.array([results[(mass_fixed, ct)]['exp_2up'] for ct in ctaus]) #* (8/52.23)
exp_2down = np.array([results[(mass_fixed, ct)]['exp_2down'] for ct in ctaus]) #* (8/52.23)
currentLimit = np.array([limitDict[(mass_fixed, ct)] for ct in lim_cts])
                  
ax.fill_between(ctaus, exp_2down, exp_2up, color='gold')
ax.fill_between(ctaus, exp_1down, exp_1up, color='limegreen')
ax.plot(ctaus, exp, 'k--', linewidth=2)
ax.plot(lim_cts, currentLimit, 'r-', linewidth=2,label="EXO-23-13")
#ax.plot(ctaus, obs * xsec_ref, 'k-', marker='o', linewidth=2)
ax.legend()
ax.set_xscale('log')
ax.set_yscale('log')
#ax.set_ylim(8*pow(10,-7),2)
#ax.set_xlim(None,4*pow(10,3))
ax.set_xlabel(r'$c\tau$ [mm]', fontsize=18)
#ax.set_ylabel(r'$\sigma/\sigma_{SM}(H\rightarrow undetected) $', fontsize=14)
ax.set_ylabel(r'$\sigma/\sigma_{SM}(gg\rightarrow H) $', fontsize=18)
#ax.set_title(rf'95% CL Upper Limit ($m_{{\phi}} = {mass_fixed}$ GeV)', fontsize=18)
ax.text(0.05, 0.95, rf'95% CL Upper Limit ($m_{{\phi}} = {mass_fixed}$ GeV)',
        transform=ax.transAxes,
        fontsize=18,
        verticalalignment='top')
hep.cms.label("Work in progress", loc=0, ax=ax, com=13.6, fontsize=16,data=True)

plt.savefig(f'brazil_higgs_ctau_m{mass_fixed}_JEC10ClosureUnc.pdf')
