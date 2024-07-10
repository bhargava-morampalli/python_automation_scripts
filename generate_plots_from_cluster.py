#!/usr/bin/env python3

import argparse
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from tqdm import tqdm
import functools
import numpy as np

@functools.lru_cache(maxsize=None)
def cached_key_function(value):
    # Replace this with your actual key function
    return value

def create_sankey_diagram(df, columns, output_file):
    # Create node labels and assign unique codes
    node_labels = []
    node_codes = {}
    for col in columns:
        unique_values = df[col].unique()
        for value in unique_values:
            if value not in node_codes:
                node_codes[value] = len(node_codes)
                node_labels.append(value)

    # Create links
    sources = []
    targets = []
    values = []
    colors = []

    # Country to ST links
    country_st_groups = df.groupby([columns[0], columns[1]]).size().reset_index(name='count')
    shared_st = country_st_groups[columns[1]].value_counts()[country_st_groups[columns[1]].value_counts() > 1].index
    color_map = {}
    
    print("Processing country to ST links...")
    for _, row in tqdm(country_st_groups.iterrows(), total=len(country_st_groups), desc="Country to ST links"):
        sources.append(node_codes[row[columns[0]]])
        targets.append(node_codes[row[columns[1]]])
        values.append(row['count'])
        if row[columns[1]] in shared_st:
            if row[columns[1]] not in color_map:
                color_map[row[columns[1]]] = f'rgba({np.random.randint(0, 256)}, {np.random.randint(0, 256)}, {np.random.randint(0, 256)}, 0.8)'
            colors.append(color_map[row[columns[1]]])
        else:
            colors.append(f'rgba({np.random.randint(0, 256)}, {np.random.randint(0, 256)}, {np.random.randint(0, 256)}, 0.8)')

    # ST to Year links
    st_year_groups = df.groupby([columns[1], columns[2]]).size().reset_index(name='count')
    print("Processing ST to Year links...")
    for _, row in tqdm(st_year_groups.iterrows(), total=len(st_year_groups)):
        sources.append(node_codes[row[columns[1]]])
        targets.append(node_codes[row[columns[2]]])
        values.append(row['count'])
        colors.append(color_map.get(row[columns[1]], 'rgba(200, 200, 200, 0.8)'))  # Use gray for non-shared ST values

    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color="blue"
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors
        )
    )])

    fig.update_layout(title_text=f'Sankey Diagram: {" → ".join(columns)}', font_size=10)
    fig.write_image(output_file)

def process_file(file_path, columns, output_folder):
    print(f"Processing file: {file_path}")
    df = pd.read_csv(file_path, sep='\t')
    base_name = Path(file_path).stem
    output_file = Path(output_folder) / f"{base_name}_{'_'.join(columns)}_sankey.png"
    create_sankey_diagram(df, columns, output_file)
    print(f"Sankey diagram saved to: {output_file}")

def main(input_path, columns, output_folder):
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    if Path(input_path).is_file():
        process_file(input_path, columns, output_folder)
    elif Path(input_path).is_dir():
        files = list(Path(input_path).glob('*.txt'))
        print(f"Found {len(files)} text files in the input directory.")
        for file_path in tqdm(files, desc="Processing files"):
            process_file(file_path, columns, output_folder)
    else:
        print(f"Invalid input path: {input_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Sankey diagrams from text files.")
    parser.add_argument("input_path", help="Path to a text file or folder containing text files")
    parser.add_argument("columns", nargs='+', help="Columns to visualize (e.g., country ST year)")
    parser.add_argument("output_folder", help="Folder to save generated Sankey diagrams")
    
    args = parser.parse_args()
    main(args.input_path, args.columns, args.output_folder)