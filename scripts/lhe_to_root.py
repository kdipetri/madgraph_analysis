#!/usr/bin/env python3

import uproot
import numpy as np
import awkward as ak
from lxml import etree
import gzip
import sys

dir(uproot)
# -------------------------------
# Usage: python lhe_to_root.py unweighted_events.lhe output.root
# -------------------------------

# configurable
#if len(sys.argv) != 3:
#    print("Usage: python lhe_to_root.py input.lhe output.root")
#    sys.exit(1)
#
#lhe_file = sys.argv[1]
#root_file = sys.argv[2]


lhe_file = "ww_events/Events/run_01_decayed_1/unweighted_events.lhe" 
root_file = "output.root"

# Support .gz LHE files
if lhe_file.endswith(".gz"):
    f = gzip.open(lhe_file, "rt")
else:
    f = open(lhe_file, "r")

px_list, py_list, pz_list, E_list = [], [], [], []
pdg_list, status_list = [], []
mother1_list, mother2_list = [], []

in_event = False
for line in f:
    line = line.strip()
    if "<event>" in line:
            in_event = True
            px_evt, py_evt, pz_evt, E_evt, pdg_evt, status_evt = [], [], [], [], [], []
            continue
    elif "</event>" in line:
            in_event = False
            # Save jagged arrays for one event
            px_list.append(px_evt)
            py_list.append(py_evt)
            pz_list.append(pz_evt)
            E_list.append(E_evt)
            pdg_list.append(pdg_evt)
            status_list.append(status_evt)
            continue

    if in_event: 
            if line.strip() == "" or line.startswith("#"):
                continue
            parts = line.strip().split()
            if len(parts) < 10:
                continue
            # LHE format: https://arxiv.org/pdf/hep-ph/0609017.pdf
            # Columns: id, status, mother1, mother2, col1, col2, px, py, pz, E, m, lifetime, spin
            pdg_id = int(parts[0])
            status = int(parts[1])
            px, py, pz, E = map(float, parts[6:10])

            pdg_evt.append(pdg_id)
            status_evt.append(status)
            px_evt.append(px)
            py_evt.append(py)
            pz_evt.append(pz)
            E_evt.append(E)

f.close()

# Convert to awkward arrays (jagged)
px_array = ak.Array(px_list)
py_array = ak.Array(py_list)
pz_array = ak.Array(pz_list)
E_array = ak.Array(E_list)
pdg_array = ak.Array(pdg_list)
status_array = ak.Array(status_list)



# Write to ROOT using uproot4 API
with uproot.recreate(root_file) as froot:
    #tree=froot.mktree('events',{name: "float32" for name in arrays})
    froot["events"] = {
        "px": px_array,
        "py": py_array,
        "pz": pz_array,
        "E": E_array,
        "pdg_id": pdg_array,
        "status": status_array,
    }


print(f"Done! ROOT file saved as: {root_file}")
