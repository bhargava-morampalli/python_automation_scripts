#!/usr/bin/env python3

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from tqdm import tqdm
import numpy as np
import argparse

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

    # Cluster to Country links
    cluster_country_groups = df.groupby([columns[0], columns[1]]).size().reset_index(name='count')
    print("Processing Cluster to Country links...")
    for _, row in tqdm(cluster_country_groups.iterrows(), total=len(cluster_country_groups), desc="Cluster to Country links"):
        sources.append(node_codes[row[columns[0]]])
        targets.append(node_codes[row[columns[1]]])
        values.append(row['count'])
        colors.append(f'rgba({np.random.randint(0, 256)}, {np.random.randint(0, 256)}, {np.random.randint(0, 256)}, 0.8)')

    # Country to ST links
    country_st_groups = df.groupby([columns[1], columns[2]]).size().reset_index(name='count')
    print("Processing Country to ST links...")
    for _, row in tqdm(country_st_groups.iterrows(), total=len(country_st_groups), desc="Country to ST links"):
        sources.append(node_codes[row[columns[1]]])
        targets.append(node_codes[row[columns[2]]])
        values.append(row['count'])
        colors.append(f'rgba({np.random.randint(0, 256)}, {np.random.randint(0, 256)}, {np.random.randint(0, 256)}, 0.8)')

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
    
    # Filter for clusters with multiple countries
    cluster_country_counts = df.groupby('cluster')['country'].nunique()
    multi_country_clusters = cluster_country_counts[cluster_country_counts > 1].index
    df_filtered = df[df['cluster'].isin(multi_country_clusters)]
    
    # Additional filter: only keep rows where the ST value is the same for each cluster
    df_filtered = df_filtered.groupby('cluster').filter(lambda x: x['ST'].nunique() == 1)
    
    # Check if there are any rows left after filtering
    if df_filtered.empty:
        print(f"No data meeting the criteria in file: {file_path}. Skipping plot generation.")
        return
    
    base_name = Path(file_path).stem
    output_file = Path(output_folder) / f"{base_name}_{'_'.join(columns)}_sankey.png"
    create_sankey_diagram(df_filtered, columns, output_file)
    print(f"Sankey diagram saved to: {output_file}")

def main(input_path, output_folder):
    columns = ['cluster', 'country', 'ST']  # Specify the correct column order
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
    parser.add_argument("output_folder", help="Folder to save generated Sankey diagrams")
    args = parser.parse_args()

    main(args.input_path, args.output_folder)