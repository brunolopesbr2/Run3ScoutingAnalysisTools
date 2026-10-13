import ROOT
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import uproot
hep.style.use("CMS")

masses = [200]
ctaus = [0.1, 0.3, 0.7, 1, 3, 10]

results = {}  # (mass, ctau) -> {obs, exp, exp_1up, exp_1down, exp_2up, exp_2down}

for mass in masses:
    for ctau in ctaus:
        print(mass,ctau)
        if(ctau==0.1):
            f = ROOT.TFile.Open(f"Stop-M{mass}-cT0p1AsymptoticLimits.root")
        elif(ctau==0.3):
            f = ROOT.TFile.Open(f"Stop-M{mass}-cT0p3AsymptoticLimits.root")
        elif(ctau==0.7):
            f = ROOT.TFile.Open(f"Stop-M{mass}-cT0p7AsymptoticLimits.root")
        else:
            f = ROOT.TFile.Open(f"Stop-M{mass}-cT{ctau}AsymptoticLimits.root")
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
with uproot.open("/afs/cern.ch/user/r/rmccarth/private/scouting/CMSSW_14_0_18_patch1/src/Run3ScoutingAnalysisTools/EXO-19-13-RPVSUSYSigmaBSquaredLimitsMassvsLifetime.root") as file:
    folder = file["Figure 7b (right), grid of limit values"]
    lifetimes = [0.1,0.3,0.7,1,3,10]
    masses = [300,400,600,800]
    plot = folder["Hist2D_y1"]
    xbins = plot.to_numpy()[1]
    ybins = plot.to_numpy()[2]
    limits = plot.to_numpy()[0] #fb
    x_data_binned = np.digitize(lifetimes,xbins)
    x_data_binned = x_data_binned - 1
    y_data_binned = np.digitize(masses,ybins)
    y_data_binned = y_data_binned - 1   
    masses = [200] + masses
    for i in range(len(lifetimes)):
        limitArray = limits[[x_data_binned[i]]*len(y_data_binned),y_data_binned]
        slope = (limitArray[1] - limitArray[0]) / (400 - 300) 
        limit_200GeV = (slope * -100) + limitArray[0]
        limitArray = np.insert(limitArray,0,limit_200GeV)
        for j in range(len(masses)):
            limitDict[(masses[j], lifetimes[i])] = limitArray[j]
        
        

# Pick a fixed lifetime slice
mass_fixed = 200  # GeV
fig, ax = plt.subplots(figsize=(10, 8))
ctaus = np.array([0.1, 0.3, 0.7, 1, 3, 10])
#obs = np.array([results[(mass_fixed, ct)]['obs'] for ct in ctaus])
exp = np.array([results[(mass_fixed, ct)]['exp'] for ct in ctaus])
exp_1up = np.array([results[(mass_fixed, ct)]['exp_1up'] for ct in ctaus])
exp_1down = np.array([results[(mass_fixed, ct)]['exp_1down'] for ct in ctaus])
exp_2up = np.array([results[(mass_fixed, ct)]['exp_2up'] for ct in ctaus])
exp_2down = np.array([results[(mass_fixed, ct)]['exp_2down'] for ct in ctaus])
currentLimit = np.array([limitDict[(mass_fixed, ct)] for ct in ctaus])
ax.fill_between(ctaus, exp_2down, exp_2up, color='gold')
ax.fill_between(ctaus, exp_1down, exp_1up, color='limegreen')
ax.plot(ctaus, exp, 'k--', linewidth=2)
ax.plot(ctaus, currentLimit, 'r-', linewidth=2,label="EXO-19-13")
#ax.plot(ctaus, obs * xsec_ref, 'k-', marker='o', linewidth=2)
ax.legend()
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_ylim(pow(10,-3),pow(10,5))
ax.set_xlabel(r'$c\tau$ [mm]', fontsize=18)
ax.set_ylabel(r'$\sigma B^{2}$ [fb]', fontsize=18)
ax.text(0.05, 0.95, rf'95% CL Upper Limit ($m_{{\tilde{{t}}}} = {mass_fixed}$ GeV)',
        transform=ax.transAxes,
        fontsize=18,
        verticalalignment='top')

hep.cms.label("Work in progress", loc=0, ax=ax, com=13.6, fontsize=16,data=True)
plt.savefig(f'brazil_stop_ctau_m{mass_fixed}_JEC10ClosureUnc.pdf')
