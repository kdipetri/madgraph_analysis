# Cleans up hepmc files produced by madgraph


# Single sample
#sample=ttbar
#gunzip -c ${sample}_events/Events/*/*.hepmc.gz > data/hepmc/${sample}.hepmc


# All samples
for sample in hww ww zll ztt ttbar ; do

	gunzip -c ${sample}_events/Events/*/*.hepmc.gz > data/hepmc/${sample}.hepmc

done
