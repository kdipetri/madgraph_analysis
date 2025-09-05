# Import necessary libraries
import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt
import vector
vector.register_awkward()
from mt2 import mt2
import h5py

# Configure inputs and outputs here
import argparse

def main():

    parser = argparse.ArgumentParser(description="Convert HepMC file to ROOT file.")
    parser.add_argument("-i","--input_file", type=str, default=None, help="Path to the input root file.")
    parser.add_argument("-o", "--output_file", type=str, default="output.h5py", help="Output file name (default: %(default)s).")
    parser.add_argument("-t", "--type", help="Type of sample (eg. ttbar, ww etc)")
    parser.add_argument("--tree_name", help="root tree name", default="events")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    args = parser.parse_args()

    # Determine input and output files
    input_file = None
    output_file = "data/h5py/output.h5py"
    if args.type is None:
        if args.input_file is None:
            sys.exit("Error: Must provide input file if type is not specified.")
        else:
            input_file = args.input_file    
        if args.output_file is not None:
            output_file = args.output_file

    else: 
        input_file = f"data/root/{args.type}.root" 
        output_file = f"data/h5py/{args.type}.h5py"
        print(f"Processing sample type: {args.type}")
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    tree_name = args.tree_name

    #Calculates and plots the W boson transverse mass from a ROOT n-tuple,
    #given branches for stable particles' 4-vectors and PDG IDs.

    try:
        # Open the ROOT file and access the TTree
        with uproot.open(f"{input_file}:{tree_name}") as tree:
            print("Successfully opened the ROOT file and TTree.")

            # Read the necessary branches into awkward arrays
            try:
                px = tree["px"].array()
                py = tree["py"].array()
                pz = tree["pz"].array()
                E  = tree["E"].array()
                pdg_id = tree["pdg_id"].array()
                status = tree["status"].array()
            except KeyError as e:
                print(f"Error: Could not find a required branch. Please check the branch names in your TTree.")
                print(f"Missing key: {e}")
                return

            # Ensure arrays are not empty
            if len(pdg_id) == 0:
                print("Error: Input arrays are empty. Check your data.")


            # Build 4-vectors
            #print(E)
            #print(E[0])
            particles = ak.zip(
                {
                    "px": px,
                    "py": py,
                    "pz": pz,
                    "E" : E,
                    "pdg_id": pdg_id,
                    "status": status
                },
                with_name="Momentum4D",
                behavior=vector.backends.awkward.behavior
            )
            # Make sure particles are in detector acceptance
            in_acceptance = (particles.pt>1) & (np.abs(particles.eta) < 2.5 ) & (particles.status == 1) 
            particles = particles[in_acceptance]
            #print(particles)
            #print(particles[0])
            #print(particles[0].pt)
            #print(pdg_id)

            # Filter leptons (electrons/muons)
            leptons = particles[((np.abs(particles.pdg_id) == 11) | (np.abs(particles.pdg_id) == 13)) & (particles.pt > 25)]
            # Sort leptons by pT (highest first)
            leptons = leptons[ak.argsort(leptons.pt, axis=1, ascending=False)]
            #print(leptons.pt)

            # Filter out neutrinos
            visibles = particles[(np.abs(particles.pdg_id) != 12) & (np.abs(particles.pdg_id) != 14) & (np.abs(particles.pdg_id) != 16)]
            #print(visibles)

            # Compute missing transverse momentum
            visibles2D = ak.zip({
                "px": visibles.px, 
                "py": visibles.py, 
                "pz": np.zeros_like(visibles.px),
                "E": visibles.pt,
                }, with_name="Momentum4D")
            MET_vec = -ak.sum(visibles2D, axis=1)
            MET_pt = MET_vec.pt
            MET_phi = MET_vec.phi
            #print(MET_vec.pt)

            # Select events with at least two leptons and met
            n_leptons = ak.num(leptons)
            mask_two_leptons = (n_leptons >= 2)
            mask_met = (MET_vec.pt > 1.0)
            leptons = leptons[mask_two_leptons & mask_met]
            MET_vec = MET_vec[mask_two_leptons & mask_met]

            # get the leading leptons
            l1 = leptons[:,0]
            l2 = leptons[:,1]
            #print(l1.pt)
            #print(l2.pt)

            # Compute kinematics of WW system
            mll = (l1+l2).m
            dphi_lep = np.abs(l1.deltaphi(l2))
            MT_WW = (l1 + l2 + MET_vec).transverse_mass
            
            # Compute s-transverse mass (M_T2-like) of WW system
            MT2_WW = mt2(
                l1.m, l1.px, l1.py,  # Visible 1: mass, px, py
                l2.m, l2.px, l2.py,  # Visible 2: mass, px, py
                MET_vec.px, MET_vec.py,  # Missing transverse momentum: x, y
                0.1, 0.1)  # Invisible 1 mass, invisible 2 mass


            # Save results to HDF5 file
            with h5py.File(output_file, 'w') as hf:
                hf.create_dataset('MT2_WW', data=MT2_WW)
                hf.create_dataset('MT_WW', data=MT_WW)
                hf.create_dataset('mll', data=mll)
                hf.create_dataset('dphi_lep', data=dphi_lep)
                hf.create_dataset('l1_pt', data=l1.pt)
                hf.create_dataset('l2_pt', data=l2.pt)
                hf.create_dataset('MET', data=MET_vec.pt)
                hf.create_dataset('MET_phi', data=MET_vec.phi)
            print(f"Results saved to {output_file}")

    

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()


