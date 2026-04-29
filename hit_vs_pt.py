import ROOT
import sys

# batch mode and style
ROOT.gROOT.SetBatch(True) # run without opening graphical windows
ROOT.gStyle.SetOptStat(0) # disable/enable histogram statistics box (1=om; 0=off)

# Open File and extract tree
file_path = "ckf_multi_runs/2026-04-10_16-47-33/performance_finding_ckf_matchingdetails.root"
file = ROOT.TFile.Open(file_path)
tree = file.Get("matchingdetails")

if not tree:
    print(f"Could not find tree in {file_path}")
    sys.exit(1)

# Histograms configuration based on transverse momentum distribution
n_bins = 50
pt_min, pt_max = 0.05, 0.5   

# TProfile calculates the mean value of purity and completeness for each pt bin
purity_hist = ROOT.TProfile("p_purity", "Hit Purity", n_bins, pt_min, pt_max)
compl_hist  = ROOT.TProfile("p_compl", "Hit Completeness", n_bins, pt_min, pt_max)

print(f"Analyzing {tree.GetEntries()} tracks...")

# Loop over data and fill histograms
for entry in tree:
    # We only care about purity/completeness for tracks matched to a truth particle
    if entry.matched:
        t_pt = entry.track_pt
        
        # for denominator we use the total number of track hits
        denom = entry.nTrackMeasurementsWithOutliers
        if denom > 0:
            # Matched Hits/Total Hits found on track
            calc_purity = float(entry.nMatchedHitsOnTrack) / denom
            
            # for clear visualization we cap at 100%
            calc_purity = min(1.0, calc_purity)
            
            purity_hist.Fill(t_pt, calc_purity)
            compl_hist.Fill(t_pt, entry.completeness) # completeness is already available in the tree

# Set Canvas
canvas = ROOT.TCanvas("c_hit_eff", "Hit Efficiency Analysis", 1200, 600)
canvas.Divide(2, 1) # split canvas into 2 pads (1 row, 2 columns)

# Purity plot configuration
canvas.cd(1)
ROOT.gPad.SetGrid(0, 0) # No grid
ROOT.gPad.SetLeftMargin(0.15) # Move the margin in to make room for titles
ROOT.gPad.SetBottomMargin(0.15)
purity_hist.SetTitle("Hit Purity vs p_{T};p_{T} [GeV];Purity")
purity_hist.SetMarkerStyle(0) # set 0 for no markers
purity_hist.SetLineColor(ROOT.kBlack)
purity_hist.SetLineWidth(2)
purity_hist.SetMinimum(0.8)   # Zoom in (optional, adjust as needed)
purity_hist.SetMaximum(1.02)
purity_hist.Draw()

# Completeness
canvas.cd(2)
ROOT.gPad.SetGrid(0, 0)      # No grid (optioanal)
ROOT.gPad.SetLeftMargin(0.15) # Move the margin in to make room for titles
ROOT.gPad.SetBottomMargin(0.15)
compl_hist.SetTitle("Hit Completeness vs p_{T};p_{T} [GeV];Completeness")
compl_hist.SetMarkerStyle(0) # set 0 for no markers
compl_hist.SetLineColor(ROOT.kBlack)
compl_hist.SetLineWidth(2)
compl_hist.SetMinimum(0.0)
compl_hist.SetMaximum(1.05)
compl_hist.Draw()

# Output
out_name = "hit_efficiency_results"
canvas.SaveAs(out_name + ".png")

print(f"{out_name}.png created, go check it out!")