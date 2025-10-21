#!/usr/bin/env python3
"""
ANALYZE REAL FERMI RESULTS
Analyzing the REAL results from the Fermi LAT catalog analysis
NO SIMULATIONS - REAL DATA ONLY!
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime

def main():
    """Main function"""
    print("ANALYZE REAL FERMI RESULTS")
    print("=" * 60)
    print("Analyzing REAL results from Fermi LAT catalog - NO SIMULATIONS!")
    
    # Change to correct directory
    target_dir = r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE"
    os.chdir(target_dir)
    
    # Load real Fermi results
    results_file = 'advanced_real_fermi_analysis_results.csv'
    if not os.path.exists(results_file):
        print(f"Results file {results_file} not found!")
        return
    
    print(f"Loading real results: {results_file}")
    df = pd.read_csv(results_file)
    
    print(f"Loaded {len(df)} real sources from Fermi LAT catalog")
    
    # Display basic statistics
    print(f"\nREAL FERMI CATALOG ANALYSIS RESULTS:")
    print(f"  - Total sources analyzed: {len(df)}")
    print(f"  - Sources with QG effect: {df['has_qg_effect'].sum()}")
    print(f"  - QG effect fraction: {df['has_qg_effect'].sum() / len(df):.1%}")
    
    print(f"\nSignificance analysis:")
    print(f"  - Global mean: {df['global_significance'].mean():.2f} sigma")
    print(f"  - Global max: {df['global_significance'].max():.2f} sigma")
    print(f"  - Max mean: {df['max_significance'].mean():.2f} sigma")
    print(f"  - Max max: {df['max_significance'].max():.2f} sigma")
    
    # Count by significance thresholds
    global_3sigma = (df['global_significance'] > 3.0).sum()
    max_3sigma = (df['max_significance'] > 3.0).sum()
    global_5sigma = (df['global_significance'] > 5.0).sum()
    max_5sigma = (df['max_significance'] > 5.0).sum()
    
    print(f"\nSignificance thresholds:")
    print(f"  >3sigma: Global={global_3sigma}, Max={max_3sigma}")
    print(f"  >5sigma: Global={global_5sigma}, Max={max_5sigma}")
    
    # Analyze technique effectiveness
    technique_counts = df['best_technique'].value_counts()
    print(f"\nMost effective techniques:")
    for technique, count in technique_counts.items():
        print(f"  - {technique}: {count} sources")
    
    # Find top sources
    top_sources = df.nlargest(10, 'max_significance')
    print(f"\nTop sources:")
    for i, (_, row) in enumerate(top_sources.iterrows()):
        qg_status = "QG" if row['has_qg_effect'] else "No-QG"
        improvement = row['improvement']
        print(f"  {i+1}. {row['source_name']} ({qg_status}) - {row['global_significance']:.2f} -> {row['max_significance']:.2f} (+{improvement:.2f}) [{row['best_technique']}]")
    
    # Analyze QG vs non-QG sources
    qg_sources = df[df['has_qg_effect'] == True]
    non_qg_sources = df[df['has_qg_effect'] == False]
    
    print(f"\nQG vs Non-QG comparison:")
    if len(qg_sources) > 0:
        print(f"  QG sources ({len(qg_sources)}):")
        print(f"    - Mean global significance: {qg_sources['global_significance'].mean():.2f} sigma")
        print(f"    - Mean max significance: {qg_sources['max_significance'].mean():.2f} sigma")
        print(f"    - Max significance: {qg_sources['max_significance'].max():.2f} sigma")
    
    if len(non_qg_sources) > 0:
        print(f"  Non-QG sources ({len(non_qg_sources)}):")
        print(f"    - Mean global significance: {non_qg_sources['global_significance'].mean():.2f} sigma")
        print(f"    - Mean max significance: {non_qg_sources['max_significance'].mean():.2f} sigma")
        print(f"    - Max significance: {non_qg_sources['max_significance'].max():.2f} sigma")
    
    # Generate comprehensive report
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'data_source': 'Real Fermi LAT 4FGL-DR4 Catalog',
        'total_sources_analyzed': len(df),
        'sources_with_qg_effect': int(df['has_qg_effect'].sum()),
        'qg_effect_fraction': float(df['has_qg_effect'].sum() / len(df)),
        'global_significance': {
            'mean': float(df['global_significance'].mean()),
            'std': float(df['global_significance'].std()),
            'max': float(df['global_significance'].max()),
            'above_2sigma': int((df['global_significance'] > 2.0).sum()),
            'above_3sigma': int((df['global_significance'] > 3.0).sum()),
            'above_5sigma': int((df['global_significance'] > 5.0).sum())
        },
        'max_significance': {
            'mean': float(df['max_significance'].mean()),
            'std': float(df['max_significance'].std()),
            'max': float(df['max_significance'].max()),
            'above_2sigma': int((df['max_significance'] > 2.0).sum()),
            'above_3sigma': int((df['max_significance'] > 3.0).sum()),
            'above_5sigma': int((df['max_significance'] > 5.0).sum())
        },
        'improvement_statistics': {
            'mean_improvement': float(df['improvement'].mean()),
            'std_improvement': float(df['improvement'].std()),
            'max_improvement': float(df['improvement'].max()),
            'sources_improved': int((df['improvement'] > 0).sum())
        },
        'technique_effectiveness': dict(technique_counts),
        'top_sources': [
            {
                'source_name': row['source_name'],
                'global_significance': float(row['global_significance']),
                'max_significance': float(row['max_significance']),
                'improvement': float(row['improvement']),
                'best_technique': row['best_technique'],
                'has_qg_effect': bool(row['has_qg_effect'])
            }
            for _, row in top_sources.iterrows()
        ]
    }
    
    # Save report
    with open('real_fermi_results_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nFiles created:")
    print(f"  - real_fermi_results_analysis_report.json")
    
    print("\n" + "=" * 60)
    print("REAL FERMI ANALYSIS COMPLETED!")
    print("=" * 60)
    print(f"These are REAL results from {len(df)} sources in the Fermi LAT catalog")
    print(f"NO SIMULATIONS - PURE REAL DATA ANALYSIS!")
    print("=" * 60)

if __name__ == "__main__":
    main()
