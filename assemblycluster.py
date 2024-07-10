#!/usr/bin/env python3

import os
import subprocess
import argparse
import itertools
import tqdm
import sqlite3
import tempfile
from scipy.cluster.hierarchy import linkage, fcluster
import numpy as np
import concurrent.futures
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_assemblies(directory):
    """Recursively find all assembly files in the given directory."""
    assemblies = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.fasta', '.fna', '.fa', '.fasta.gz', '.fna.gz', '.fa.gz')):
                assemblies.append(os.path.join(root, file))
    return assemblies

def run_mash(pair):
    """Run Mash distance calculation for a pair of assemblies."""
    a1, a2 = pair
    cmd = ['mash', 'dist', a1, a2]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        parts = result.stdout.strip().split('\t')
        return (a1, a2, float(parts[2]))
    except subprocess.CalledProcessError as e:
        logging.warning(f"Mash comparison failed for {a1} and {a2}: {e}")
        return None

def init_db(db_path):
    """Initialize SQLite database for storing Mash distances."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS distances
                 (assembly1 TEXT, assembly2 TEXT, distance REAL)''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_assemblies ON distances(assembly1, assembly2)')
    conn.commit()
    return conn

def store_distances(conn, distances):
    """Store calculated distances in the SQLite database."""
    c = conn.cursor()
    c.executemany('INSERT INTO distances VALUES (?, ?, ?)', distances)
    conn.commit()

def run_mash_all_vs_all(assemblies, threads, db_path):
    """Run all-vs-all Mash distance calculations in parallel, processing and reporting in chunks."""
    pairs = list(itertools.combinations(assemblies, 2))
    total_comparisons = len(pairs)
    conn = init_db(db_path)
    
    chunk_size = 1000
    total_chunks = (total_comparisons + chunk_size - 1) // chunk_size

    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=threads) as executor:
            for i in tqdm.tqdm(range(0, total_comparisons, chunk_size), 
                               desc="Calculating Mash distances", 
                               total=total_chunks,
                               unit="chunk"):
                chunk = pairs[i:i+chunk_size]
                results = list(executor.map(run_mash, chunk))
                valid_results = [r for r in results if r is not None]
                store_distances(conn, valid_results)

        logging.info(f"Completed {total_comparisons} Mash comparisons in {total_chunks} chunks")
    except Exception as e:
        logging.error(f"An error occurred during Mash calculations: {e}")
    finally:
        conn.close()

def get_distance_matrix(assemblies, db_path):
    """Construct a distance matrix from the stored Mash distances."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    n = len(assemblies)
    dist_matrix = np.zeros((n, n))
    
    for i, a1 in enumerate(assemblies):
        for j, a2 in enumerate(assemblies[i+1:], i+1):
            c.execute('SELECT distance FROM distances WHERE assembly1 = ? AND assembly2 = ?', (a1, a2))
            result = c.fetchone()
            if result:
                dist_matrix[i, j] = dist_matrix[j, i] = result[0]
    
    conn.close()
    return dist_matrix

def cluster_assemblies(dist_matrix, threshold):
    """Perform hierarchical clustering on the distance matrix."""
    linkage_matrix = linkage(dist_matrix[np.triu_indices(len(dist_matrix), k=1)], method='average')
    clusters = fcluster(linkage_matrix, t=threshold, criterion='distance')
    return clusters

def write_groups_to_file(assemblies, clusters, output_file):
    """Write assembly names and their corresponding cluster numbers to a file."""
    with open(output_file, 'w') as f:
        for assembly, cluster in zip(assemblies, clusters):
            assembly_name = os.path.splitext(os.path.basename(assembly))[0]
            # Remove any remaining extension (handles .fasta, .fa, .fna)
            assembly_name = os.path.splitext(assembly_name)[0]
            f.write(f"{assembly_name}\t{cluster}\n")

def process_folder(folder, threshold, threads):
    """Process a single folder of assemblies."""
    assemblies = find_assemblies(folder)
    if not assemblies:
        logging.warning(f"No assemblies found in {folder}")
        return

    logging.info(f"Processing {len(assemblies)} assemblies in {folder}")

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    run_mash_all_vs_all(assemblies, threads, db_path)
    dist_matrix = get_distance_matrix(assemblies, db_path)
    clusters = cluster_assemblies(dist_matrix, threshold)

    output_file = os.path.join(folder, f"{os.path.basename(folder)}_grouped.txt")
    write_groups_to_file(assemblies, clusters, output_file)
    logging.info(f"Wrote assembly groupings to {output_file}")

    os.unlink(db_path)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Group assemblies based on Mash distances",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process a single folder of assemblies:
    python script.py /path/to/assembly/folder

  Process a folder with multiple subdirectories containing assemblies:
    python script.py /path/to/parent/folder

  Specify a custom threshold and number of threads:
    python script.py /path/to/folder --threshold 0.005 --threads 16

Notes:
  - The script automatically detects whether it's processing a single folder
    or multiple subdirectories.
  - Output files are named '<foldername>_grouped.txt' and placed in the
    respective folders.
  - The script scales well with increased threads, but performance gains may
    plateau depending on I/O limitations and the number of CPU cores available.
        """
    )
    parser.add_argument("input_dir", 
                        help="Directory containing assembly files or subdirectories")
    parser.add_argument("--threshold", type=float, default=0.001, 
                        help="Mash distance threshold for grouping (default: 0.001)")
    parser.add_argument("--threads", type=int, default=10, 
                        help="Number of threads for parallel processing (default: 10)")
    return parser.parse_args()

def main():
    args = parse_arguments()

    if os.path.isfile(args.input_dir):
        logging.error("Error: Input must be a directory, not a file.")
        return

    if not os.path.exists(args.input_dir):
        logging.error(f"Error: Directory {args.input_dir} does not exist.")
        return

    # Check if the input directory contains subdirectories with assemblies
    subdirs = [d for d in os.listdir(args.input_dir) if os.path.isdir(os.path.join(args.input_dir, d))]
    has_assemblies = any(find_assemblies(os.path.join(args.input_dir, d)) for d in subdirs)

    if has_assemblies:
        # Process each subdirectory separately
        for subdir in subdirs:
            full_path = os.path.join(args.input_dir, subdir)
            if find_assemblies(full_path):
                process_folder(full_path, args.threshold, args.threads)
    else:
        # Process the input directory itself
        process_folder(args.input_dir, args.threshold, args.threads)

if __name__ == "__main__":
    main()