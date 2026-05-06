import ROOT
import sys

# set batch mode and style
ROOT.gROOT.SetBatch(True) # run without opening graphical windows
ROOT.gStyle.SetOptStat(0) # disable/enable histogram statistics box (1=on; 0=off)
path = "ckf_multi_runs/2026-04-10_16-47-33/" # define your path

# configuration for histograms based on eta distribution
n_bins_eta = 50
eta_min, eta_max = -0.15, 0.15 

# load file and extract tree
file_particle = ROOT.TFile.Open(path + "particles.root")
tree_particle = file_particle.Get("particles")

# Create a map to connect (event_id, particle_id -> eta)
particle_map = {}
for event in tree_particle: # loop over all events in the tree
    eid = int(event.event_id) # get event id
    for i in range(len(event.particle_id)): # Loop over all particles in the event
        # fill the map with key (event_id, particle_id) and value eta
        particle_map[(eid, int(event.particle_id[i]))] = float(event.eta[i])

file_match = ROOT.TFile.Open(path + "performance_finding_ckf_matchingdetails.root")
tree_match = file_match.Get("matchingdetails")


# TProfile creates a profile histogram
# Profile histrograms are used to plot the mean value of a variable as a function of another variable
# In this case, we want to plot the mean of purity and completeness as a function of eta
h_purity_eta = ROOT.TProfile("h_purity_eta", "", n_bins_eta, eta_min, eta_max)
h_comp_eta   = ROOT.TProfile("h_comp_eta",   "", n_bins_eta, eta_min, eta_max)

# loop over the matching details tree to fill the profile histograms
for entry in tree_match:
    # Only process matched tracks
    if entry.matched:
        key = (int(entry.event_nr), int(entry.particle_id))
        
        if key in particle_map: # check if the key exists in the particle map to avoid KeyError
            eta = particle_map[key] # get eta from the map
            
            # formula for purity: nMatchedHitsOnTrack / nTrackMeasurementsWithOutliers
            # formula calculates number of matched tracks hits divided by total number of track hits
            denom = entry.nTrackMeasurementsWithOutliers
            if denom > 0:
                calc_purity = float(entry.nMatchedHitsOnTrack) / denom
                # minimum to ensure we don't exceed 100% purity due to data issues or outliers
                calc_purity = min(1.0, calc_purity)
                
                # Fill histograms
                h_purity_eta.Fill(eta, calc_purity)
                h_comp_eta.Fill(eta, entry.completeness) # completness is available in the tree as a variable
                # these values are averaged in the profile histograms for each eta bin

# Plotting details and design (adjustable according to preferences)
canvas = ROOT.TCanvas("c_eta_hits", "Hit Performance vs Eta", 1200, 600)
canvas.Divide(2, 1) # divide canvas into 2 pads (1 row, 2 columns)

def style_pad(pad, hist, title, y_label, y_min=0.0):
    pad.cd()
    ROOT.gPad.SetGrid(1, 1) 
    ROOT.gPad.SetLeftMargin(0.15)
    ROOT.gPad.SetBottomMargin(0.15)
    hist.SetTitle(f"{title};Truth #eta;{y_label}")
    hist.SetMarkerStyle(0) # set 0 for no markers
    hist.SetMarkerSize(0.8)
    hist.SetMarkerColor(ROOT.kBlack)
    hist.SetLineColor(ROOT.kBlack)
    hist.SetMinimum(y_min) # set y axis minimum
    hist.SetMaximum(1.05) # set maximum to give some space for clearer visualisation
    hist.Draw("E1")

# Purity Plot
style_pad(canvas.cd(1), h_purity_eta, "Hit Purity vs #eta", "Purity", y_min=0.8)

# Completeness Plot
style_pad(canvas.cd(2), h_comp_eta, "Hit Completeness vs #eta", "Completeness", y_min=0.0)

canvas.SaveAs("hit_performance_vs_eta_finally.png")