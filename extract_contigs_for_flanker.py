#!/usr/bin/env python3

import argparse
import os
import shutil
from Bio import SeqIO
from Bio.Seq import Seq
from tqdm import tqdm

def reverse_complement(seq):
    return str(Seq(seq).reverse_complement())

def process_contigs(abricate_file, contig_folder, output_folder, gene_string, flank_size):
    os.makedirs(output_folder, exist_ok=True)
    
    # Count total number of entries in the abricate file
    with open(abricate_file, 'r') as f:
        total_entries = sum(1 for _ in f) - 1  # Subtract 1 for header

    copied_files = 0
    skipped_files = 0

    with open(abricate_file, 'r') as f:
        next(f)  # Skip header
        for line in tqdm(f, total=total_entries, desc="Processing abricate results"):
            fields = line.strip().split('\t')
            file_name = fields[0]
            start = int(fields[2])
            end = int(fields[3])
            strand = fields[4]
            gene = fields[5]

            if gene_string in gene:
                contig_path = os.path.join(contig_folder, file_name)
                if os.path.exists(contig_path):
                    for record in SeqIO.parse(contig_path, "fasta"):
                        contig_length = len(record.seq)
                        if start > flank_size and contig_length - end > flank_size:
                            output_path = os.path.join(output_folder, file_name)
                            if strand == '-':
                                # Reverse complement the entire sequence for genes on the reverse strand
                                # This ensures the gene faces the same direction in all copied contigs
                                record.seq = Seq(reverse_complement(str(record.seq)))
                            shutil.copy2(contig_path, output_path)
                            copied_files += 1
                        else:
                            skipped_files += 1
                else:
                    print(f"Warning: Contig file not found: {file_name}")

    return copied_files, skipped_files

def main():
    parser = argparse.ArgumentParser(description="Process contig files based on Abricate results.")
    parser.add_argument("abricate_file", help="Path to the Abricate results TSV file")
    parser.add_argument("contig_folder", help="Path to the folder containing contig FASTA files")
    parser.add_argument("output_folder", help="Path to the output folder for processed contig files")
    parser.add_argument("gene_string", help="String to search for in the GENE column")
    parser.add_argument("flank_size", type=int, help="Minimum size (in kb) of flanking sequence required on each side")
    
    args = parser.parse_args()

    copied_files, skipped_files = process_contigs(
        args.abricate_file,
        args.contig_folder,
        args.output_folder,
        args.gene_string,
        args.flank_size * 1000  # Convert kb to bp
    )

    print(f"\nProcessing complete!")
    print(f"Files copied: {copied_files}")
    print(f"Files skipped: {skipped_files}")
    print(f"Processed files are located in: {os.path.abspath(args.output_folder)}")

if __name__ == "__main__":
    main()
