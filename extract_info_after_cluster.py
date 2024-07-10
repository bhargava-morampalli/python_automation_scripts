#!/usr/bin/env python3

import os
import csv
import argparse
from typing import List, Dict
import pandas as pd
from pathlib import Path
import logging
from multiprocessing import Pool, cpu_count
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_tsv_data(tsv_file: str, assembly_column: str, columns_to_add: List[str]) -> Dict[str, Dict[str, str]]:
    """Load TSV data into a dictionary for faster lookup."""
    df = pd.read_csv(tsv_file, sep='\t')
    tsv_data = {}
    for _, row in df.iterrows():
        assembly = row[assembly_column]
        tsv_data[assembly] = {col: str(row[col]) for col in columns_to_add}
    return tsv_data

def find_matching_assembly(assembly: str, tsv_data: Dict[str, Dict[str, str]]) -> str:
    """Find a matching assembly in the TSV data, allowing for partial matches."""
    for tsv_assembly in tsv_data:
        if assembly in tsv_assembly or tsv_assembly in assembly:
            return tsv_assembly
    return None

def write_header(output_file: Path, columns_to_add: List[str]):
    """Write header to the output file."""
    header = ["assembly", "cluster"] + columns_to_add
    with open(output_file, 'w') as f:
        f.write('\t'.join(header) + '\n')

def process_file(args):
    """Process a single text file."""
    file_path, tsv_data, columns_to_add, output_folder, skip_header = args
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        if skip_header and lines:
            lines = lines[1:]  # Skip the first line if skip_header is True

        output_file = Path(output_folder) / Path(file_path).name
        
        # Write header
        write_header(output_file, columns_to_add)

        # Process and write data
        with open(output_file, 'a') as f:  # Open in append mode
            for line in lines:
                assembly, cluster = line.strip().split()
                matching_assembly = find_matching_assembly(assembly, tsv_data)
                if matching_assembly:
                    additional_data = [str(tsv_data[matching_assembly].get(col, '')) for col in columns_to_add]
                    f.write("{0}\t{1}\t{2}\n".format(assembly, cluster, '\t'.join(additional_data)))
                else:
                    f.write("{0}\t{1}\t{2}\n".format(assembly, cluster, '\t'.join([''] * len(columns_to_add))))

        return f"Processed {file_path}"
    except Exception as e:
        return f"Error processing {file_path}: {str(e)}"

def main(input_folder: str, tsv_file: str, assembly_column: str, columns_to_add: List[str], output_folder: str, skip_header: bool):
    """Main function to process all text files."""
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Load TSV data
    tsv_data = load_tsv_data(tsv_file, assembly_column, columns_to_add)

    # Get list of text files
    text_files = list(Path(input_folder).glob('*.txt'))
    total_files = len(text_files)
    print(f"Found {total_files} text files in the input folder.")

    # Process files using multiprocessing with simple progress indicator
    with Pool(processes=cpu_count()) as pool:
        args = [(str(file), tsv_data, columns_to_add, output_folder, skip_header) for file in text_files]
        for i, result in enumerate(pool.imap_unordered(process_file, args), 1):
            sys.stdout.write(f'\rProcessing files: {i}/{total_files} ({i/total_files:.1%})')
            sys.stdout.flush()
            logging.info(result)
    
    print("\nProcessing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add columns from TSV to text files based on partial assembly matches.")
    parser.add_argument("input_folder", help="Folder containing input text files")
    parser.add_argument("tsv_file", help="TSV file with additional data")
    parser.add_argument("assembly_column", help="Name of the assembly column in the TSV file")
    parser.add_argument("columns_to_add", nargs='+', help="One or more column names from the TSV file to add to the text files")
    parser.add_argument("output_folder", help="Folder to save processed files (will be created if it doesn't exist)")
    parser.add_argument("--skip_header", action="store_true", help="Skip the first line of each text file (use if text files have headers)")
    
    args = parser.parse_args()

    # Check if specified columns exist in the TSV file
    tsv_df = pd.read_csv(args.tsv_file, sep='\t')
    missing_columns = set([args.assembly_column] + args.columns_to_add) - set(tsv_df.columns)
    if missing_columns:
        parser.error(f"The following columns are not found in the TSV file: {', '.join(missing_columns)}")

    main(args.input_folder, args.tsv_file, args.assembly_column, args.columns_to_add, args.output_folder, args.skip_header)