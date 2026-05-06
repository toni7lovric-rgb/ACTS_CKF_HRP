import ROOT
import sys

# Set Batch Mode to prevent X11 errors
ROOT.gROOT.SetBatch(True)

# Open File and extract its tree
file = ROOT.TFile.Open("ckf_multi_runs/2026-04-15_14-51-00/performance_finding_ckf_matchingdetails.root")
tree = file.Get("matchingdetails")

if not tree:
    print("Error: Could not find 'matchingdetails' tree in the file")
    sys.exit(1) # system exit with error code

# Configuration of histograms based on transverse momentum distribution
n_bins = 50
pt_min, pt_max = 0.05, 0.5   

h_den_pt = ROOT.TH1F("h_den_pt", "Total Tracks", n_bins, pt_min, pt_max)
h_num_pt = ROOT.TH1F("h_num_pt", "Fake Tracks",  n_bins, pt_min, pt_max)

print(f"Analyzing {tree.GetEntries()} tracks from tree...")

# Loop over data and fill histograms
for entry in tree:
    t_pt = entry.track_pt
    
    # Fill Denominator (All Reconstructed Tracks)
    h_den_pt.Fill(t_pt)
    
    # Fill Numerator (Only Fakes)
    # A track is considered fake if it has no matched true particle
    # This is determined by the matched variable in the tree (false or 0 means no match)
    # Based on the number of matched track hits
    if not entry.matched:
        h_num_pt.Fill(t_pt)

# Create Efficiency histograms using TEfficiency
fake_pt = ROOT.TEfficiency(h_num_pt, h_den_pt)

# Create a canvas and generate the plot
canvas = ROOT.TCanvas("c1", "Fake Rate versus p_{T}", 800, 600)
canvas.SetGrid(0, 0) # grid off

# Style the plot
fake_pt.SetTitle("Fake Rate vs p_{T};p_{T} [GeV];Fake Rate")
fake_pt.SetMarkerStyle(0)
fake_pt.SetLineColor(ROOT.kBlack)
fake_pt.SetMarkerColor(ROOT.kBlack)

fake_pt.Draw("AP") # AP = points + error bars (A = axis, P = points)

# Save the output
out = "fake_rate_vs_pt_"
canvas.SaveAs(out + ".png")

# Calculate global average fake rate and print it
total_reco = h_den_pt.Integral() # total reconstructed tracks (denominator)
total_fake = h_num_pt.Integral() # total fake tracks (numerator)
if total_reco > 0:
    print(f"Overall Fake Rate: {total_fake/total_reco*100:.2f}% ({total_fake:.0f}/{total_reco:.0f} tracks)")

print(f"Plot saved as {out}.png, check it out!")