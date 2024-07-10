#!/usr/bin/env python3

import argparse

def read_filenames(file_path):
    with open(file_path, 'r') as file:
        return set(line.strip() for line in file)

def find_unique_filenames(all_filenames_path, compare_filenames_path):
    original_filenames = read_filenames(all_filenames_path)
    comparison_filenames = read_filenames(compare_filenames_path)

    # Find filenames in original_filenames not partially matched in comparison_filenames
    unique_filenames = [filename for filename in original_filenames if not any(comp in filename for comp in comparison_filenames)]

    return unique_filenames

def main():
    parser = argparse.ArgumentParser(description='Compare two lists of filenames for partial matches.')
    parser.add_argument('all_filenames', help='File containing all filenames')
    parser.add_argument('compare_filenames', help='File with filenames to compare against')

    args = parser.parse_args()

    unique_filenames = find_unique_filenames(args.all_filenames, args.compare_filenames)

    output_file = args.compare_filenames.rsplit('.', 1)[0] + '_missing.txt'
    with open(output_file, 'w') as file:
        for filename in unique_filenames:
            file.write(filename + '\n')

    print(f"Unique filenames written to {output_file}")

if __name__ == "__main__":
    main()
