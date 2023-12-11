description = "Use PHASE v2.1 to reconstruct haplotypes from population genotype data.\nInput and output is done with FASTA or TSV files via SeqPhase."

ambiguity = "This can happen if the probability thresholds were set too high in the parameters. Consider reducing the phase and allele thresholds (referred to as -p and -q in the PHASE documentation) and rerunning the program. Keep in mind that lowering these thresholds may affect the reliability of the results."

author_1 = "ConvPhase by Jan-Christopher Schmidt."
author_2 = "Gui by Stefanos Patmanidis."
authors = author_1 + "\n" + author_2

phase_citation_1 = "[1] Stephens, M., Smith, N., and Donnelly, P. (2001). A new statistical method for haplotype reconstruction from population data. American Journal of Human Genetics, 68, 978--989."
phase_citation_2 = "[2] Stephens, M., and Donnelly, P. (2003). A comparison of Bayesian methods for haplotype reconstruction from population genotype data. American Journal of Human Genetics, 73:1162-1169."
seqphase_citation = "[3] Flot (2010) SeqPHASE: a web tool for interconverting PHASE input/output files and FASTA sequence alignments Molecular Ecology Resources 10 (1): 162-166."
citations = phase_citation_1 + "\n\n" + phase_citation_2 + "\n\n" + seqphase_citation

homepage_url = "https://github.com/iTaxoTools/ConvPhaseGui"
itaxotools_url = "http://itaxotools.org/"
