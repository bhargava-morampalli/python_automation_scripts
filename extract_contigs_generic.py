#!/usr/bin/env python3

import os
import sys

# Check for the correct number of command-line arguments
if len(sys.argv) != 3:
    print("Usage: python extract_contigs.py input_fasta output_directory")
    sys.exit(1)

# Extract the input FASTA file and output directory from command-line arguments
input_fasta_file = sys.argv[1]
output_directory = sys.argv[2]

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Initialize variables to store contig name and sequence
current_contig_name = None
current_contig_sequence = []

# Open the input FASTA file
with open(input_fasta_file, 'r') as infile:
    for line in infile:
        if line.startswith('>'):  # Header line
            # If there's a previous contig, write it to a separate file
            if current_contig_name and current_contig_sequence:
                output_filename = os.path.join(output_directory, f'{current_contig_name}.fasta')
                with open(output_filename, 'w') as outfile:
                    outfile.write(f'>{current_contig_name}\n')
                    outfile.write(''.join(current_contig_sequence))
                current_contig_sequence = []

            # Extract the contig name from the header
            current_contig_name = line.strip().lstrip('>')
        else:
            # Append the sequence lines to the current contig
            if current_contig_name is not None:
                current_contig_sequence.append(line)

# Write the last contig to a separate file
if current_contig_name and current_contig_sequence:
    output_filename = os.path.join(output_directory, f'{current_contig_name}.fasta')
    with open(output_filename, 'w') as outfile:
        outfile.write(f'>{current_contig_name}\n')
        outfile.write(''.join(current_contig_sequence))

print(f'Separated contigs from {input_fasta_file} into individual files in {output_directory}')
