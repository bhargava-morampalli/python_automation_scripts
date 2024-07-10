#!/usr/bin/env python3

import os
import sys
import shutil
import argparse

def filter_files(input_folder, output_folder, criteria_path):
    """
    Filters and organizes files from the input folder into subfolders in the output folder based on criteria.

    :param input_folder: The folder containing files from which files need to be extracted.
    :param output_folder: The folder where the organized files and folders will be stored.
    :param criteria_path: Path to a single text file or a folder containing multiple text files.
    """

    print("Input folder:", input_folder)
    print("Output folder:", output_folder)
    print("Criteria path:", criteria_path)

    # Determine if criteria_path is a file or a folder and list all applicable .txt files
    if os.path.isfile(criteria_path):
        values_files = [criteria_path]
    else:
        values_files = [os.path.join(criteria_path, f) for f in os.listdir(criteria_path) if f.endswith(".txt")]

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    for values_file in values_files:
        # Derive subfolder name from the values file name and create the subfolder
        values_file_name = os.path.basename(values_file)
        subfolder_name = os.path.splitext(values_file_name)[0]
        subfolder_path = os.path.join(output_folder, subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)

        # Read filtering criteria from the values file
        with open(values_file, "r") as f:
            values = set(line.strip() for line in f)

        # Loop through each file in the input folder and copy to the appropriate subfolder if it matches the criteria
        for file in os.listdir(input_folder):
            if any(value.lower() in file.lower() for value in values):
                try:
                    shutil.copy(os.path.join(input_folder, file), os.path.join(subfolder_path, file))
                except Exception as e:
                    print(f"Error copying file '{file}': {e}")


def main():
    """
    Main function to parse command-line arguments and call the filter_files function.
    """

    # Define and parse command-line arguments
    parser = argparse.ArgumentParser(description="Filter and extract files into subfolders based on filenames defined in text files.")
    parser.add_argument("input_folder", help="Path to the input folder containing files to be organized.")
    parser.add_argument("output_folder", help="Path to the output folder where organized files will be stored - folder names are based on the name of the textfile(s)")
    parser.add_argument("criteria_path", help="Path to a text file or a folder containing text files with filtering criteria i.e., filenames - filenames can be partial.")
    args = parser.parse_args()

    # Check for the existence of input_folder
    if not os.path.exists(args.input_folder):
        print(f"Error: Input folder '{args.input_folder}' does not exist.")
        sys.exit(1)

    if not os.path.exists(args.criteria_path):
        print(f"Error: Criteria file/folder '{args.criteria_path}' does not exist.")
        sys.exit(1)

    # Call the file filtering function with the parsed arguments
    filter_files(args.input_folder, args.output_folder, args.criteria_path)

if __name__ == "__main__":
    # Entry point for the script; calls the main function.
    main()
