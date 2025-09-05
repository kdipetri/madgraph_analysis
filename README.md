
# Structure
madgraph_analysis
- cards     # Madgraph cards
- scripts   # Analysis scripts
- data      # Processed events / analysis outputs
-- lhe          # LHE files produced by madgraph (not used yet)
-- hepmc        # HEPMC2 files produced by madgraph
-- root         # ROOT files produced by analysis scripts
- plots     # Plots produced by analysis scripts

# Installation
For now assumes you have madgraph installed, with pythia and hepmc 

# How to Run 

Generate events
```
./mg5_aMC cards/{process_name}.mg5
```

Clean up the output
```
source scripts/cleanup_hepmc.sh
```

Convert hepmc file to root
```
python scripts/hepmc_to_root.py --t {process_name} 
```

Analyze the root file
```
python scripts/analyze_events.py --t {process_name} 
```

Make final plots
```
python scripts/plot_events.py 
``` 