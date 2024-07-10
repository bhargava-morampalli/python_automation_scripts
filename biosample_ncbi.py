#!/usr/bin/env python3

"""
This script processes BioSample information from NCBI.
It can extract BioSample information and filter TSV files containing BioSample data.

Usage:
    python biosample_ncbi.py extract <input_file> [--retry <num>] [--verbose]
    python biosample_ncbi.py filter <input_file> --columns <col1> <col2> ...

Examples:
    python biosample_ncbi.py extract biosample_ids.txt --retry 5 --verbose
    python biosample_ncbi.py filter biosample_info.tsv --columns Accession Description "Organism Name"
"""

import requests
import xml.etree.ElementTree as ET
import sys
import os
import csv
import argparse
import time
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_biosample_info_with_retry(accession, max_retries=3):
    for attempt in range(max_retries):
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=biosample&id={accession}&retmode=xml"
            response = requests.get(url)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                sample_data = root.find("BioSample")
                if sample_data is not None:
                    biosample_info = {}
                    biosample_info["accession"] = accession
                    biosample_info["description"] = sample_data.find("Description/Title").text if sample_data.find("Description/Title") is not None else ""
                    biosample_info["organism_name"] = sample_data.find("Description/Organism/OrganismName").text if sample_data.find("Description/Organism/OrganismName") is not None else ""
                    biosample_info["owner_name"] = sample_data.find("Owner/Name").text if sample_data.find("Owner/Name") is not None else ""
                    biosample_info["owner_abbreviation"] = sample_data.find("Owner/Name").get("abbreviation") if sample_data.find("Owner/Name") is not None else ""
                    biosample_info["ids"] = ",".join([id_elem.text for id_elem in sample_data.findall("Ids/Id")])
                    biosample_info["attributes"] = {attribute.get("attribute_name"): attribute.text for attribute in sample_data.findall("Attributes/Attribute")}
                    return biosample_info
            return None
        except requests.exceptions.RequestException:
            if attempt == max_retries - 1:
                logging.error(f"Failed to retrieve information for BioSample {accession}")
            else:
                time.sleep(1)  # Wait before retrying
    return None

def save_to_tsv(biosample_infos, file_path):
    all_attributes = set()
    for biosample_info in biosample_infos:
        all_attributes.update(biosample_info["attributes"].keys())
    
    header = ["Accession", "Description", "Organism Name", "Owner Name", "Owner Abbreviation", "IDs"] + list(all_attributes)
    
    with open(file_path, "w", encoding="utf-8", newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(header)
        
        for biosample_info in biosample_infos:
            row = [
                biosample_info["accession"],
                biosample_info["description"],
                biosample_info["organism_name"],
                biosample_info["owner_name"],
                biosample_info["owner_abbreviation"],
                biosample_info["ids"]
            ]
            for attr in all_attributes:
                row.append(biosample_info["attributes"].get(attr, ""))
            writer.writerow(row)

def filter_tsv(input_file, output_file, columns):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile, delimiter='\t')
        fieldnames = [col for col in reader.fieldnames if col in columns]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
        
        writer.writeheader()
        for row in reader:
            filtered_row = {col: row[col] for col in fieldnames}
            writer.writerow(filtered_row)

def main():
    parser = argparse.ArgumentParser(description="Process BioSample information from NCBI", 
                                     epilog="For more information, use the --help option with each command.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract BioSample information")
    extract_parser.add_argument("input_file", help="Input file containing BioSample IDs, one per line")
    extract_parser.add_argument("--retry", type=int, default=3, help="Number of retries for failed requests (default: 3)")
    extract_parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    # Filter command
    filter_parser = subparsers.add_parser("filter", help="Filter TSV file")
    filter_parser.add_argument("input_file", help="Input TSV file to filter")
    filter_parser.add_argument("--columns", nargs='+', required=True, help="Columns to include in filtered output")

    args = parser.parse_args()

    if args.command == "extract":
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        base_name = os.path.splitext(os.path.basename(args.input_file))[0]
        output_file = f"{base_name}_biosample_info.tsv"
        failed_file = f"{base_name}_failed_ids.txt"

        with open(args.input_file, "r") as f:
            accessions = [line.strip() for line in f]

        biosample_infos = []
        failed_ids = []

        for accession in tqdm(accessions, desc="Processing BioSamples"):
            biosample_info = get_biosample_info_with_retry(accession, max_retries=args.retry)
            if biosample_info:
                biosample_infos.append(biosample_info)
            else:
                failed_ids.append(accession)

        if biosample_infos:
            save_to_tsv(biosample_infos, output_file)
            logging.info(f"BioSample information saved to {output_file}")
        else:
            logging.warning("No BioSample information could be retrieved.")

        if failed_ids:
            with open(failed_file, 'w') as f:
                f.write('\n'.join(failed_ids))
            logging.warning(f"Failed IDs written to {failed_file}")

    elif args.command == "filter":
        base_name = os.path.splitext(os.path.basename(args.input_file))[0]
        output_file = f"{base_name}_filtered.tsv"
        filter_tsv(args.input_file, output_file, args.columns)
        logging.info(f"Filtered TSV saved to {output_file}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()