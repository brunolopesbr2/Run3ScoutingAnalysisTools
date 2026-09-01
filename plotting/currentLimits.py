import uproot
import numpy as np

def build_limits(fileA, fileB):
    """ Creates limit dictionary for current exotic Higgs and RPV SUSY cross sections based off input files from hepdata"""
    limitDict = {}
    ggF_CS = 52.23 #pb
    with uproot.open(fileA) as file:
        masses = [55,40,30,23,15]
        for i in range(2,11,2):
            folder = file["Figure 4b"]
            plot = folder["Graph1D_y"+str(i)]
            x = plot.member("fX")
            y = plot.member("fY")
            mass = masses[int(i/2)-1]
            for j in range(len(x)):
                if((x[j]==1) or (x[j]==10)):
                    key = f"Hto2Sto4D-cT{int(x[j])}-MS{mass}"
                    y_lim = y[j]*ggF_CS
                    if(y_lim>8): 
                        y_lim = 8
                    limitDict[key] = y_lim / 8 #divide out 8 pb cross-section I used to normalize signals

    with uproot.open(fileB) as file:
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
                key = ""
                if(lifetimes[i] == 0.1):
                    key = f"Stop-M{masses[j]}-cT0p1"
                elif(lifetimes[i] == 0.3):
                    key = f"Stop-M{masses[j]}-cT0p3"
                elif(lifetimes[i] == 0.7):
                    key = f"Stop-M{masses[j]}-cT0p7"
                else:
                    key = f"Stop-M{masses[j]}-cT{int(lifetimes[i])}"
                limitDict[key] = limitArray[j]
    return limitDict
