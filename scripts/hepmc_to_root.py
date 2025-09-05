#!/usr/bin/env python3

import uproot
import numpy as np
import awkward as ak
import gzip
import sys
import argparse

# Reads in HepMC file and converts to ROOT file
# Reference for uproot: https://uproot.readthedocs.io/en/latest/

# Configure inputs and outputs here
import argparse

def main():

    parser = argparse.ArgumentParser(description="Convert HepMC file to ROOT file.")
    parser.add_argument("-i","--input_file", type=str, default=None, help="Path to the input HepMC file.")
    parser.add_argument("-o", "--output_file", type=str, default="output.root", help="Output file name (default: %(default)s).")
    parser.add_argument("-t", "--type", help="Type of sample (eg. ttbar ww.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    parser.add_argument("--max_events", type=int, default=-1, help="Maximum number of events to process (default: all).")
    args = parser.parse_args()

    # Determine input and output files
    hepmc_file = None
    root_file = "data/root/output.root"
    if args.type is None:
        if args.input_file is None:
            sys.exit("Error: Must provide input file if type is not specified.")
        else:
            hepmc_file = args.input_file    
        if args.output_file is not None:
            root_file = args.output_file

    else: 
        hepmc_file = f"data/hepmc/{args.type}.hepmc" 
        root_file = f"data/root/{args.type}.root"
        print(f"Processing sample type: {args.type}")
    
    print(f"Input file: {hepmc_file}")
    print(f"Output file: {root_file}")
        
                  
    # Lists to hold data
    pxs, pys, pzs, Es, pdg_ids, status_ids = [], [], [], [], [], []
    # Temporary lists for current event
    event_pxs, event_pys, event_pzs, event_E, event_pdg, event_status = [], [], [], [], [], []
    
    evt_counter=0
    max_events = args.max_events if args.max_events>0 else float('inf')
    
    # Analysis begins
    with open(hepmc_file, "r") as f:
        print(f"Running analysis")   
        for line in f:
            
            if line.startswith("E "): # New event

                if evt_counter>max_events: break
                if evt_counter%1000==0 and evt_counter>0:
                    print(f"Processed {evt_counter} events")

                # If not the first event, save the previous event's data
                if event_pxs:
                    pxs.append(event_pxs)
                    pys.append(event_pys)
                    pzs.append(event_pzs)
                    Es.append(event_E)
                    pdg_ids.append(event_pdg)
                    status_ids.append(event_status)

                # Reset temporary lists for new event
                event_pxs, event_pys, event_pzs, event_E, event_pdg, event_status = [], [], [], [], [], []
                
                parts = line.split()
                event_number = int(parts[1]) # MC event number
                if args.debug :
                    print(f"Event {evt_counter}") # Our event counter
                
                evt_counter+=1
                
            elif line.startswith("P "): # Particle line
                parts = line.split()
                
                pdg = int(parts[2])
                status = int(parts[8])
                px, py, pz, e = map(float, parts[3:7])

                event_pxs.append(px)
                event_pys.append(py)
                event_pzs.append(pz)
                event_E.append(e)
                event_pdg.append(pdg)
                event_status.append(status)
                
                if args.debug :
                    print(f"Particle {pdg}, px={px}, py={py}, pz={pz}, e={e}, status={status}")
                
            

    # Convert to awkward arrays
    pxs = ak.Array(pxs)
    pys = ak.Array(pys)
    pzs = ak.Array(pzs)
    Es  = ak.Array(Es)
    pdg_ids = ak.Array(pdg_ids)
    status_ids = ak.Array(status_ids)

    # Save to ROOT file
    with uproot.recreate(root_file) as f:
        f["events"] = {
            "px": pxs,
            "py": pys,
            "pz": pzs,
            "E": Es,
            "pdg_id": pdg_ids,
            "status": status_ids
    }

    print(f"Saved ROOT file: {root_file}")

if __name__ == "__main__":
    main()