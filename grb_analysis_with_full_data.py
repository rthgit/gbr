#!/usr/bin/env python3
"""
GRB ANALYSIS WITH FULL DATA
Analyze the complete GRB datasets with multi-technique QG analysis
"""

import os
import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path

def load_grb_data(grb_name):
    """Load GRB data from CSV file"""
    csv_file = f"{grb_name}_PH00.csv"
    
    if not os.path.exists(csv_file):
        return None
    
    try:
        df = pd.read_csv(csv_file)
        print(f"📂 Loaded {grb_name}:")
        print(f"   ✅ {len(df)} photons")
        print(f"   Energy: {df['ENERGY'].min():.3f} - {df['ENERGY'].max():.3f} GeV")
        print(f"   Time: {df['TIME'].min():.1f} - {df['TIME'].max():.1f} s")
        return df
    except Exception as e:
        print(f"   ❌ Error loading {csv_file}: {e}")
        return None

def calculate_correlation_significance(df, method='pearson'):
    """Calculate correlation and significance"""
    if len(df) < 3:
        return 0.0, 0.0
    
    try:
        if method == 'pearson':
            r, p_value = stats.pearsonr(df['ENERGY'], df['TIME'])
        elif method == 'spearman':
            r, p_value = stats.spearmanr(df['ENERGY'], df['TIME'])
        else:
            return 0.0, 0.0
        
        # Convert p-value to sigma
        if p_value > 0:
            sigma = stats.norm.ppf(1 - p_value/2)
        else:
            sigma = 0.0
        
        return r, sigma
    except:
        return 0.0, 0.0

def phase_analysis(df, split_ratio=0.5):
    """Perform phase analysis (early/late split)"""
    if len(df) < 4:
        return {}
    
    # Sort by time
    df_sorted = df.sort_values('TIME').reset_index(drop=True)
    
    # Split at specified ratio
    split_idx = int(len(df_sorted) * split_ratio)
    early_df = df_sorted.iloc[:split_idx]
    late_df = df_sorted.iloc[split_idx:]
    
    results = {}
    
    if len(early_df) >= 3:
        r_early, sigma_early = calculate_correlation_significance(early_df)
        results['phase_early'] = {
            'r': r_early,
            'sigma': sigma_early,
            'n_photons': len(early_df)
        }
    
    if len(late_df) >= 3:
        r_late, sigma_late = calculate_correlation_significance(late_df)
        results['phase_late'] = {
            'r': r_late,
            'sigma': sigma_late,
            'n_photons': len(late_df)
        }
    
    return results

def energy_percentile_analysis(df):
    """Perform energy percentile analysis"""
    if len(df) < 10:
        return {}
    
    results = {}
    
    # Define percentile ranges
    percentiles = {
        'high': (50, 100),
        'very_high': (75, 100),
        'ultra_high': (90, 100),
        'extreme': (95, 100)
    }
    
    for name, (low_pct, high_pct) in percentiles.items():
        low_val = np.percentile(df['ENERGY'], low_pct)
        high_val = np.percentile(df['ENERGY'], high_pct)
        
        subset_df = df[(df['ENERGY'] >= low_val) & (df['ENERGY'] <= high_val)]
        
        if len(subset_df) >= 3:
            r, sigma = calculate_correlation_significance(subset_df)
            results[f'percentile_{name}'] = {
                'r': r,
                'sigma': sigma,
                'n_photons': len(subset_df),
                'energy_range': f"{low_val:.1f}-{high_val:.1f} GeV"
            }
    
    return results

def analyze_grb(grb_name):
    """Perform complete analysis on a GRB"""
    print(f"\n{'='*80}")
    print(f"# MULTI-TECHNIQUE ANALYSIS: {grb_name}")
    print(f"{'='*80}")
    
    # Load data
    df = load_grb_data(grb_name)
    if df is None:
        return None
    
    results = {
        'grb_name': grb_name,
        'total_photons': len(df),
        'energy_range': [df['ENERGY'].min(), df['ENERGY'].max()],
        'time_range': [df['TIME'].min(), df['TIME'].max()]
    }
    
    # Global correlation
    print(f"\n🔍 Global correlation...")
    r_global, sigma_global = calculate_correlation_significance(df, 'pearson')
    r_spearman, sigma_spearman = calculate_correlation_significance(df, 'spearman')
    
    results['global'] = {
        'pearson': {'r': r_global, 'sigma': sigma_global},
        'spearman': {'r': r_spearman, 'sigma': sigma_spearman}
    }
    
    print(f"   Pearson:  r = {r_global:+.4f}, σ = {sigma_global:.2f}")
    print(f"   Spearman: ρ = {r_spearman:+.4f}, σ = {sigma_spearman:.2f}")
    
    # Phase analysis
    print(f"\n🔍 Phase analysis...")
    phase_results = phase_analysis(df)
    results['phase'] = phase_results
    
    for phase, data in phase_results.items():
        print(f"   {phase}: r = {data['r']:+.4f}, σ = {data['sigma']:.2f} ({data['n_photons']} photons)")
    
    # Energy percentile analysis
    print(f"\n🔍 Energy percentiles...")
    percentile_results = energy_percentile_analysis(df)
    results['percentile'] = percentile_results
    
    for percentile, data in percentile_results.items():
        print(f"   {percentile}: r = {data['r']:+.4f}, σ = {data['sigma']:.2f} ({data['n_photons']} photons)")
    
    # Find maximum significance
    all_sigmas = [sigma_global, sigma_spearman]
    for phase_data in phase_results.values():
        all_sigmas.append(phase_data['sigma'])
    for percentile_data in percentile_results.values():
        all_sigmas.append(percentile_data['sigma'])
    
    max_sigma = max(all_sigmas) if all_sigmas else 0.0
    
    # Find best technique
    best_technique = 'global_pearson'
    if sigma_spearman > sigma_global:
        best_technique = 'global_spearman'
    
    for phase, data in phase_results.items():
        if data['sigma'] > max_sigma:
            max_sigma = data['sigma']
            best_technique = phase
    
    for percentile, data in percentile_results.items():
        if data['sigma'] > max_sigma:
            max_sigma = data['sigma']
            best_technique = percentile
    
    results['global_significance'] = sigma_global
    results['max_significance'] = max_sigma
    results['best_technique'] = best_technique
    results['improvement'] = max_sigma - sigma_global
    
    print(f"\n🎯 RESULTS:")
    print(f"   Global significance: {sigma_global:.2f}σ")
    print(f"   Max significance: {max_sigma:.2f}σ")
    print(f"   Best technique: {best_technique}")
    print(f"   Improvement: {max_sigma - sigma_global:+.2f}σ")
    
    return results

def main():
    """Main function"""
    print("GRB ANALYSIS WITH FULL DATA")
    print("=" * 80)
    print("Analyzing complete GRB datasets with multi-technique QG analysis")
    
    # List of GRBs to analyze
    grb_list = [
        'GRB090902B',
        'GRB130427A', 
        'GRB160625B',
        'GRB090926A',
        'GRB090510',
        'GRB080916C'
    ]
    
    print(f"\n{'='*80}")
    print("CHECKING DATA AVAILABILITY")
    print(f"{'='*80}")
    
    available_grbs = []
    for grb in grb_list:
        csv_file = f"{grb}_PH00.csv"
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            print(f"✅ {grb}: {len(df)} photons")
            available_grbs.append(grb)
        else:
            print(f"❌ {grb}: Data not found")
    
    print(f"\n📊 Summary: {len(available_grbs)}/{len(grb_list)} GRBs have data")
    
    if not available_grbs:
        print("❌ No GRB data available for analysis!")
        return
    
    print(f"\n{'='*80}")
    print(f"ANALYZING {len(available_grbs)} GRBs")
    print(f"{'='*80}")
    
    all_results = []
    
    for i, grb in enumerate(available_grbs):
        print(f"\nProgress: {i}/{len(available_grbs)}")
        result = analyze_grb(grb)
        if result:
            all_results.append(result)
    
    # Save results
    results_df = pd.DataFrame(all_results)
    results_df.to_csv('grb_analysis_full_results.csv', index=False)
    
    # Create summary report
    summary = {
        'analysis_date': pd.Timestamp.now().isoformat(),
        'total_grbs': len(all_results),
        'results': all_results,
        'summary_stats': {
            'avg_global_significance': np.mean([r['global_significance'] for r in all_results]),
            'avg_max_significance': np.mean([r['max_significance'] for r in all_results]),
            'avg_improvement': np.mean([r['improvement'] for r in all_results]),
            'grbs_with_sigma_3plus': len([r for r in all_results if r['max_significance'] >= 3.0]),
            'grbs_with_sigma_5plus': len([r for r in all_results if r['max_significance'] >= 5.0])
        }
    }
    
    with open('grb_analysis_full_report.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n{'='*80}")
    print("✅ ANALYSIS COMPLETE!")
    print(f"{'='*80}")
    print(f"Results: grb_analysis_full_results.csv")
    print(f"Report: grb_analysis_full_report.json")
    
    print(f"\n📊 SUMMARY:")
    print(f"Total GRBs analyzed: {len(all_results)}")
    print(f"Average global significance: {summary['summary_stats']['avg_global_significance']:.2f}σ")
    print(f"Average max significance: {summary['summary_stats']['avg_max_significance']:.2f}σ")
    print(f"Average improvement: {summary['summary_stats']['avg_improvement']:.2f}σ")
    
    print(f"\n🏆 TOP GRBs:")
    sorted_results = sorted(all_results, key=lambda x: x['max_significance'], reverse=True)
    for i, result in enumerate(sorted_results[:3]):
        print(f"  {i+1}. {result['grb_name']}: {result['max_significance']:.2f}σ [{result['best_technique']}]")
    
    print(f"\n🎯 QG DETECTION RATE:")
    print(f"  σ ≥ 3.0: {summary['summary_stats']['grbs_with_sigma_3plus']}/{len(all_results)} ({summary['summary_stats']['grbs_with_sigma_3plus']/len(all_results)*100:.1f}%)")
    print(f"  σ ≥ 5.0: {summary['summary_stats']['grbs_with_sigma_3plus']}/{len(all_results)} ({summary['summary_stats']['grbs_with_sigma_5plus']/len(all_results)*100:.1f}%)")
    
    print(f"{'='*80}")

if __name__ == "__main__":
    main()