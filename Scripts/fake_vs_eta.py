import ROOT
import sys

# set batch mode and style
ROOT.gROOT.SetBatch(True) # run without opening graphical windows
ROOT.gStyle.SetOptStat(0) # disable/enable histogram statistics box
path = "ckf_multi_runs/2026-04-15_14-51-00/" # set general path to directory with files

n_bins_eta = 50 # number of bins for eta histogram
eta_min, eta_max = -0.15, 0.15 # range for histogram (based on expected distribution)

# Data files
file_particle = ROOT.TFile.Open(path + "particles.root") # Contains truth particles and their properties
tree_particle = file_particle.Get("particles") # Tree from a file (event_id, particle_id, etc.)

# Map: (event_id, particle_id) -> truth eta
# We create a loop to fill the map which itself is a dictionary
# Connecting the track-based information (which contains particle_id) to the eta values
particle_map = {}
for event in tree_particle: # Loop over all events in the tree
    event_id = int(event.event_id)
    for i in range(len(event.particle_id)):
        particle_map[(event_id, int(event.particle_id[i]))] = float(event.eta[i])

# Take the matching details file and the corresponding tree from it
file_match = ROOT.TFile.Open(path + "performance_finding_ckf_matchingdetails.root")
tree_match = file_match.Get("matchingdetails")

# Histograms for fake rate calculation
# Denominator = nAllTracks (Total reconstructed tracks)
h_den_eta = ROOT.TH1F("h_track_den", "", n_bins_eta, eta_min, eta_max)
# Numerator = nFakeTracks (Tracks with matched == False)
h_num_eta = ROOT.TH1F("h_track_fake", "", n_bins_eta, eta_min, eta_max)

# Loop over the matching details tree to fill the histograms accordingly
for entry in tree_match:
    # Use the particle_id associated with the track to find its Eta location
    key = (int(entry.event_nr), int(entry.particle_id))
    
    if key in particle_map:
        eta = particle_map[key]
        
        # Based on the formula nFakeTracks/nAllTracks
        h_den_eta.Fill(eta) # All tracks
        if not entry.matched:
            h_num_eta.Fill(eta) # Only fakes

# Fake rate via TEfficiency
fake_eta = ROOT.TEfficiency(h_num_eta, h_den_eta)
fake_eta.SetTitle("Track Fake Rate;#eta;Fake Rate")


# Plotting details and design (adjustable according to preferences)
canvas = ROOT.TCanvas("c_fake_eta", "Fake Rate Analysis", 800, 600)
canvas.SetLeftMargin(0.15)
canvas.SetBottomMargin(0.15)
canvas.SetGrid()

fake_eta.Draw("AP") # AP = points + error bars (A = axis, P = points)
ROOT.gPad.Update()  # Update the canvas for drawring the graph and setting styles

graph = fake_eta.GetPaintedGraph()
if graph:
    graph.SetMarkerStyle(20) # full circle marker for points
    graph.SetMarkerSize(1.0) # size of the marker
    graph.SetMarkerColor(ROOT.kBlack)
    graph.SetLineColor(ROOT.kBlack)
    graph.SetMinimum(0.0) # y axis min
    graph.SetMaximum(1.05) # y axis max

# Save output
output = "fake_rate_vs_eta_"
canvas.SaveAs(output + ".png")
print(f"{output}.png created, go check it out!")