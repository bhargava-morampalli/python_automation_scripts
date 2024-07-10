#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import multiprocessing
import itertools
from pathlib import Path
import logging
from tqdm import tqdm

def setup_logging(debug):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run all-vs-all Mash comparisons on two sets of genome files.",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
Examples:
  %(prog)s folder1 folder2 -o output.tsv
  %(prog)s folder1 folder2 -o output.tsv --threads 20 --threshold 0.05 --lessverbose
  %(prog)s --help
""")
    parser.add_argument("folder1", help="Path to first folder containing genome files")
    parser.add_argument("folder2", help="Path to second folder containing genome files")
    parser.add_argument("-o", "--output", required=True, help="Output TSV file")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads to use (default: 10)")
    parser.add_argument("--threshold", type=float, help="Distance threshold for filtering results (optional)")
    parser.add_argument("--lessverbose", action="store_true", help="Output only Reference-ID, Query-ID, and Mash-distance (optional)")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Number of comparisons per chunk (default: 1000)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()

def get_genome_files(folder):
    extensions = ('.fna', '.fa', '.fasta', '.fsa')
    return [f for f in Path(folder).glob('*') if f.suffix.lower() in extensions]

def run_mash(genome1, genome2):
    try:
        cmd = ["mash", "dist", str(genome1), str(genome2)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Mash error for {genome1} vs {genome2}: {e}")
        return None

def process_chunk(chunk):
    return [run_mash(genome1, genome2) for genome1, genome2 in chunk]

def main():
    args = parse_arguments()
    setup_logging(args.debug)

    logging.info("Starting genome comparison process")

    genomes1 = get_genome_files(args.folder1)
    genomes2 = get_genome_files(args.folder2)

    if not genomes1 or not genomes2:
        logging.error("No genome files found in one or both folders")
        sys.exit(1)

    print(f"Found {len(genomes1)} genomes in folder1 and {len(genomes2)} genomes in folder2")

    all_pairs = list(itertools.product(genomes1, genomes2))
    total_comparisons = len(all_pairs)
    print(f"Total comparisons to be made: {total_comparisons}")

    chunks = [all_pairs[i:i + args.chunk_size] for i in range(0, len(all_pairs), args.chunk_size)]

    results = []
    filtered_count = 0
    total_processed = 0

    with multiprocessing.Pool(args.threads) as pool:
        with tqdm(total=total_comparisons, desc="Processing") as pbar:
            for chunk_results in pool.imap_unordered(process_chunk, chunks):
                for result in chunk_results:
                    if result is not None:
                        fields = result.split('\t')
                        if args.threshold is None or float(fields[2]) < args.threshold:
                            if args.lessverbose:
                                results.append('\t'.join(fields[:3]))
                            else:
                                results.append(result)
                        else:
                            filtered_count += 1
                    total_processed += 1
                    pbar.update(1)

    print(f"Comparisons completed. Total processed: {total_processed}")
    if args.threshold is not None:
        print(f"Rows filtered out due to threshold: {filtered_count}")

    print(f"Writing results to {args.output}")
    with open(args.output, 'w') as outfile:
        for result in results:
            outfile.write(result + '\n')

    print("Process completed successfully.")

if __name__ == "__main__":
    main()