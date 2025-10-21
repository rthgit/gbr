#!/usr/bin/env python3
"""
GRB ANALYSIS WITH FIXED FILES
Using the fixed CSV files to avoid endianness issues
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt
from datetime import datetime
import json

def load_grb_data(grb_name):
    """Load GRB data from fixed CSV file"""
    
    csv_file = f"grb_data/raw/{grb_name}_photons_fixed.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return None
    
    try:
        df = pd.read_csv(csv_file)
        print(f"📂 Loaded {grb_name}:")
        print(f"   ✅ {len(df)} photons")
        
        # Find energy and time columns
        energy_col = None
        time_col = None
        
        for col in df.columns:
            if 'energy' in col.lower() or 'e_' in col.lower():
                energy_col = col
            if 'time' in col.lower() or 't_' in col.lower():
                time_col = col
        
        if energy_col is None or time_col is None:
            print(f"   ❌ Could not find energy/time columns")
            print(f"   Available columns: {list(df.columns)}")
            return None
        
        energies = df[energy_col].values
        times = df[time_col].values
        
        print(f"   Energy: {np.min(energies):.3f} - {np.max(energies):.3f} GeV")
        print(f"   Time: {np.min(times):.1f} - {np.max(times):.1f} s")
        
        return {
            'grb_name': grb_name,
            'energies': energies,
            'times': times,
            'n_photons': len(df)
        }
        
    except Exception as e:
        print(f"❌ Error loading {grb_name}: {e}")
        return None

def analyze_grb(grb_data):
    """Analyze a single GRB"""
    
    grb_name = grb_data['grb_name']
    energies = grb_data['energies']
    times = grb_data['times']
    n_photons = grb_data['n_photons']
    
    print(f"\n{'='*80}")
    print(f"# MULTI-TECHNIQUE ANALYSIS: {grb_name}")
    print(f"{'='*80}")
    
    # Sort by time
    time_sort_idx = np.argsort(times)
    energies = energies[time_sort_idx]
    times = times[time_sort_idx]
    
    # Global correlation
    print(f"\n🔍 Global correlation...")
    r_global, p_global = pearsonr(energies, times)
    rho_global, _ = spearmanr(energies, times)
    
    global_sigma = abs(r_global) * np.sqrt(n_photons - 2)
    global_sigma_spearman = abs(rho_global) * np.sqrt(n_photons - 2)
    
    print(f"   Pearson:  r = {r_global:+.4f}, σ = {global_sigma:.2f}")
    print(f"   Spearman: ρ = {rho_global:+.4f}, σ = {global_sigma_spearman:.2f}")
    
    # Phase analysis
    print(f"\n🔍 Phase analysis...")
    mid_time = np.median(times)
    early_mask = times < mid_time
    late_mask = times >= mid_time
    
    phase_results = {}
    
    if np.sum(early_mask) > 10:
        early_energies = energies[early_mask]
        early_times = times[early_mask]
        r_early, _ = pearsonr(early_energies, early_times)
        sigma_early = abs(r_early) * np.sqrt(len(early_energies) - 2)
        phase_results['early'] = {
            'significance': sigma_early,
            'correlation': r_early,
            'n_photons': len(early_energies)
        }
        print(f"   Early phase: r = {r_early:+.4f}, σ = {sigma_early:.2f} ({len(early_energies)} photons)")
    
    if np.sum(late_mask) > 10:
        late_energies = energies[late_mask]
        late_times = times[late_mask]
        r_late, _ = pearsonr(late_energies, late_times)
        sigma_late = abs(r_late) * np.sqrt(len(late_energies) - 2)
        phase_results['late'] = {
            'significance': sigma_late,
            'correlation': r_late,
            'n_photons': len(late_energies)
        }
        print(f"   Late phase: r = {r_late:+.4f}, σ = {sigma_late:.2f} ({len(late_energies)} photons)")
    
    # Energy percentiles
    print(f"\n🔍 Energy percentiles...")
    percentile_results = {}
    
    percentiles = {
        'high': (50, 100),
        'very_high': (75, 100),
        'ultra_high': (90, 100),
        'extreme': (95, 100)
    }
    
    for name, (low_pct, high_pct) in percentiles.items():
        low_threshold = np.percentile(energies, low_pct)
        high_threshold = np.percentile(energies, high_pct)
        subset_mask = (energies >= low_threshold) & (energies <= high_threshold)
        
        if np.sum(subset_mask) > 10:
            subset_energies = energies[subset_mask]
            subset_times = times[subset_mask]
            
            r_subset, _ = pearsonr(subset_energies, subset_times)
            sigma_subset = abs(r_subset) * np.sqrt(len(subset_energies) - 2)
            
            percentile_results[name] = {
                'significance': sigma_subset,
                'correlation': r_subset,
                'n_photons': len(subset_energies),
                'energy_range': (np.min(subset_energies), np.max(subset_energies))
            }
            
            print(f"   {name} ({low_pct}-{high_pct}%): r = {r_subset:+.4f}, σ = {sigma_subset:.2f} ({len(subset_energies)} photons)")
    
    # Find maximum significance
    all_significances = [global_sigma]
    all_significances.extend([result['significance'] for result in phase_results.values()])
    all_significances.extend([result['significance'] for result in percentile_results.values()])
    
    max_significance = max(all_significances)
    
    # Determine best technique
    best_technique = 'global'
    if max_significance == global_sigma_spearman:
        best_technique = 'global_spearman'
        max_significance = global_sigma_spearman
    elif any(result['significance'] == max_significance for result in phase_results.values()):
        for phase, result in phase_results.items():
            if result['significance'] == max_significance:
                best_technique = f'phase_{phase}'
                break
    elif any(result['significance'] == max_significance for result in percentile_results.values()):
        for percentile, result in percentile_results.items():
            if result['significance'] == max_significance:
                best_technique = f'percentile_{percentile}'
                break
    
    print(f"\n🎯 RESULTS:")
    print(f"   Global significance: {global_sigma:.2f}σ")
    print(f"   Max significance: {max_significance:.2f}σ")
    print(f"   Best technique: {best_technique}")
    print(f"   Improvement: {max_significance - global_sigma:.2f}σ")
    
    return {
        'grb_name': grb_name,
        'n_photons': n_photons,
        'global_significance': global_sigma,
        'max_significance': max_significance,
        'best_technique': best_technique,
        'improvement': max_significance - global_sigma,
        'phase_results': phase_results,
        'percentile_results': percentile_results,
        'global_correlation': r_global,
        'global_spearman': rho_global
    }

def main():
    """Main function"""
    print("GRB ANALYSIS WITH FIXED FILES")
    print("=" * 80)
    print("Using fixed CSV files to avoid endianness issues")
    
    # Change to correct directory
    target_dir = r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE"
    os.chdir(target_dir)
    
    # List of GRBs to analyze
    grb_list = [
        'GRB080916C',
        'GRB090510', 
        'GRB090902B',
        'GRB090926A',
        'GRB130427A',
        'GRB160625B'
    ]
    
    print(f"\n{'='*80}")
    print("CHECKING DATA AVAILABILITY")
    print(f"{'='*80}")
    
    available_grbs = []
    for grb_name in grb_list:
        csv_file = f"grb_data/raw/{grb_name}_photons_fixed.csv"
        if os.path.exists(csv_file):
            print(f"✅ {grb_name}: Data available")
            available_grbs.append(grb_name)
        else:
            print(f"❌ {grb_name}: Data not found")
    
    print(f"\n📊 Summary: {len(available_grbs)}/{len(grb_list)} GRBs have data")
    
    if not available_grbs:
        print("❌ No GRB data available!")
        return
    
    print(f"\n{'='*80}")
    print(f"ANALYZING {len(available_grbs)} GRBs")
    print(f"{'='*80}")
    
    results = []
    
    for i, grb_name in enumerate(available_grbs, 1):
        print(f"\nProgress: {i-1}/{len(available_grbs)}")
        
        # Load GRB data
        grb_data = load_grb_data(grb_name)
        if grb_data is None:
            continue
        
        # Analyze GRB
        result = analyze_grb(grb_data)
        if result is not None:
            results.append(result)
    
    # Save results
    if results:
        df_results = pd.DataFrame([
            {
                'grb_name': r['grb_name'],
                'n_photons': r['n_photons'],
                'global_significance': r['global_significance'],
                'max_significance': r['max_significance'],
                'best_technique': r['best_technique'],
                'improvement': r['improvement'],
                'global_correlation': r['global_correlation'],
                'global_spearman': r['global_spearman']
            }
            for r in results
        ])
        
        df_results.to_csv('grb_analysis_fixed_results.csv', index=False)
        
        # Generate report
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_grbs_analyzed': len(results),
            'results': [
                {
                    'grb_name': r['grb_name'],
                    'n_photons': r['n_photons'],
                    'global_significance': float(r['global_significance']),
                    'max_significance': float(r['max_significance']),
                    'best_technique': r['best_technique'],
                    'improvement': float(r['improvement']),
                    'global_correlation': float(r['global_correlation']),
                    'global_spearman': float(r['global_spearman'])
                }
                for r in results
            ]
        }
        
        with open('grb_analysis_fixed_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n{'='*80}")
        print("✅ ANALYSIS COMPLETE!")
        print(f"{'='*80}")
        print(f"Results: grb_analysis_fixed_results.csv")
        print(f"Report: grb_analysis_fixed_report.json")
        
        # Display summary
        print(f"\n📊 SUMMARY:")
        print(f"Total GRBs analyzed: {len(results)}")
        print(f"Average global significance: {df_results['global_significance'].mean():.2f}σ")
        print(f"Average max significance: {df_results['max_significance'].mean():.2f}σ")
        print(f"Average improvement: {df_results['improvement'].mean():.2f}σ")
        
        # Top GRBs
        top_grbs = df_results.nlargest(3, 'max_significance')
        print(f"\n🏆 TOP GRBs:")
        for i, (_, row) in enumerate(top_grbs.iterrows(), 1):
            print(f"  {i}. {row['grb_name']}: {row['max_significance']:.2f}σ [{row['best_technique']}]")
        
        print(f"{'='*80}")

if __name__ == "__main__":
    main()
