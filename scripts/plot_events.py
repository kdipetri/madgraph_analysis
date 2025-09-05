# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
import h5py

plt.rcParams.update({
    "font.size": 16,
    "axes.titlesize": 18,
    "axes.labelsize": 18,
    "legend.fontsize": 16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "lines.linewidth": 5,
    "patch.linewidth": 2.0
})

def label(sample):
    if sample == "hww":
        return r"$h \rightarrow WW$"
    elif sample == "ww":
        return r"$WW$"
    elif sample == "ttbar":
        return r"$t\bar{t}$"
    elif sample == "zll":
        return r"$Z/\gamma^* \rightarrow ll$"
    elif sample == "ztt":
        return r"$Z/\gamma^* \rightarrow \tau\tau$"
    else:
        return sample
    
def xlabel(distname):
    if distname == "MT2_WW":
        return r"$M_{T2}(\ell,\ell,E_{T}^{miss})$ [GeV]"
    elif distname == "MT_WW":
        return r"$M_{T}(\ell\ell,E_{T}^{miss})$ [GeV]"
    elif distname == "mll":
        return r"$m(\ell\ell)$ [GeV]"
    elif distname == "dphi_lep":
        return r"$\Delta\phi(\ell_1\ell_2)$"
    elif distname == "MET":
        return r"$E_{T}^{miss}$ [GeV]"  
    elif distname == "l1_pt":
        return r"$p_{T}(\ell_1)$ [GeV]"
    elif distname == "l2_pt":
        return r"$p_{T}(\ell_2)$ [GeV]"
    else:
        return distname


def main():


    # Get Input files
    samples = ["hww", "ww", "ttbar", "zll", 'ztt']
    distnames = ["MT2_WW", "MT_WW", "mll", "dphi_lep", "MET","l1_pt", "l2_pt"]

    filenames = [f"data/h5py/{sample}.h5py" for sample in samples]
    files = [h5py.File(file, 'r') for file in filenames]
    
    # Read data
    data = {}
    for sample, file in zip(samples, files):
        data[sample] = {}
        for dist in distnames:
            data[sample][dist] = file[dist][:]
    
    # Function to plot distributions
    def plotfig(distname, nbins, xmin, xmax):
   
        # Plot
        plt.figure(figsize=(6, 6))
        for sample in samples:
            dist = data[sample][distname]
            plt.hist(dist, bins=nbins, range=(xmin,xmax), histtype='step',density=True, label=label(sample))
        plt.xlabel(xlabel(distname))
        plt.ylabel("Events")
        plt.grid(True)
        plt.tight_layout()
        plt.legend()  
        plt.savefig(f"plots/{distname}.pdf")
        plt.close() 

    # Plot all distributions
    nbins = 30
    plotfig("MT2_WW", nbins, 0, 150)
    plotfig("MT_WW", 20, 0, 600)
    plotfig("mll", nbins, 0, 300)
    plotfig("MET", nbins, 0, 250)
    plotfig("dphi_lep", 20, 0, np.pi)
    plotfig("l1_pt", nbins, 0, 200)
    plotfig("l2_pt", nbins, 0, 150)



# Example usage with your file
if __name__ == "__main__":
    main()



