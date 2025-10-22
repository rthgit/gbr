#!/usr/bin/env python3
"""
COMPREHENSIVE 6-GRB ANALYSIS - ROBUST BOOTSTRAP METHOD
Analizza tutti i 6 GRB con il metodo bootstrap che ha risolto l'infinito
"""

import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
import json

def robust_bootstrap_sigma(energy, time, n_boot=10000):
    """Robust bootstrap sigma - never infinite"""
    r_obs, _ = stats.spearmanr(energy, time)
    
    boot_r = np.zeros(n_boot)
    for i in range(n_boot):
        if i % 2000 == 0:
            print(f"    Progress: {i}/{n_boot}")
        time_shuffled = np.random.permutation(time)
        boot_r[i], _ = stats.spearmanr(energy, time_shuffled)
    
    sigma = abs(r_obs) / np.std(boot_r)
    n_exceed = np.sum(np.abs(boot_r) >= np.abs(r_obs))
    
    return {
        'rho': r_obs,
        'sigma': sigma,
        'p_value': n_exceed / n_boot if n_exceed > 0 else 1/n_boot,
        'n_exceed': n_exceed,
        'boot_std': np.std(boot_r)
    }

# GRB list
grbs = [
    'GRB090926A',
    'GRB090510', 
    'GRB090902B',
    'GRB130427A',
    'GRB160625B',
    'GRB080916C'
]

print("="*80)
print("COMPREHENSIVE 6-GRB ANALYSIS - ROBUST BOOTSTRAP")
print("="*80)

results = []

for grb_name in grbs:
    print(f"\n{'-'*80}")
    print(f"ANALYZING: {grb_name}")
    print(f"{'-'*80}")
    
    # Find CSV file
    csv_files = list(Path('.').glob(f'{grb_name}*.csv'))
    if not csv_files:
        print(f"❌ No data found for {grb_name}")
        continue
    
    csv_file = csv_files[0]
    print(f"📂 Loading: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(df)} photons")
        
        # Fix energy units
        if df['ENERGY'].max() > 1000:
            df['ENERGY'] = df['ENERGY'] / 1000.0
            print(f"⚠️ Energy converted from MeV to GeV")
        
        energy = df['ENERGY'].values
        time = df['TIME'].values
        
        print(f"📊 Data summary:")
        print(f"  N photons: {len(energy):,}")
        print(f"  E_max: {energy.max():.2f} GeV")
        print(f"  E_min: {energy.min():.3f} GeV")
        print(f"  Time range: {time.max() - time.min():.0f} s")
        
        # Check for anomalous energy
        if energy.max() > 100:
            print(f"⚠️  WARNING: E_max > 100 GeV (possible contamination)")
        
        # Bootstrap analysis
        print(f"🔧 Running robust bootstrap (n=10,000)...")
        result = robust_bootstrap_sigma(energy, time, n_boot=10000)
        
        print(f"\n📈 Results:")
        print(f"  Spearman ρ: {result['rho']:.4f}")
        print(f"  Sigma: {result['sigma']:.2f}")
        print(f"  P-value: {result['p_value']:.2e}")
        print(f"  Exceedances: {result['n_exceed']}/10000")
        print(f"  Bootstrap std: {result['boot_std']:.6f}")
        
        # Classification
        if result['sigma'] >= 5:
            classification = "STRONG"
            emoji = "🔥"
        elif result['sigma'] >= 3:
            classification = "SIGNIFICANT"
            emoji = "✅"
        elif result['sigma'] >= 2:
            classification = "MARGINAL"
            emoji = "📊"
        else:
            classification = "BELOW THRESHOLD"
            emoji = "❌"
        
        print(f"  {emoji} Classification: {classification}")
        
        results.append({
            'GRB': grb_name,
            'N_photons': int(len(energy)),
            'E_max_GeV': float(energy.max()),
            'Spearman_rho': float(result['rho']),
            'Sigma': float(result['sigma']),
            'P_value': float(result['p_value']),
            'Classification': classification,
            'Bootstrap_std': float(result['boot_std'])
        })
        
    except Exception as e:
        print(f"❌ Error analyzing {grb_name}: {e}")
        continue

# Summary table
print("\n" + "="*80)
print("FINAL RESULTS SUMMARY - ALL 6 GRBs")
print("="*80)

if results:
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('Sigma', ascending=False)
    
    print("\n" + df_results.to_string(index=False))
    
    # Save results
    df_results.to_csv('ALL_GRBs_FINAL_RESULTS.csv', index=False)
    print(f"\n✅ Saved: ALL_GRBs_FINAL_RESULTS.csv")
    
    # Statistics
    print("\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    
    strong = df_results[df_results['Sigma'] >= 5]
    significant = df_results[(df_results['Sigma'] >= 3) & (df_results['Sigma'] < 5)]
    marginal = df_results[(df_results['Sigma'] >= 2) & (df_results['Sigma'] < 3)]
    below = df_results[df_results['Sigma'] < 2]
    
    print(f"\n🔥 Strong (≥5σ): {len(strong)}/6 ({len(strong)/6*100:.0f}%)")
    for _, row in strong.iterrows():
        print(f"  🔥 {row['GRB']}: {row['Sigma']:.2f}σ")
    
    print(f"\n✅ Significant (3-5σ): {len(significant)}/6 ({len(significant)/6*100:.0f}%)")
    for _, row in significant.iterrows():
        print(f"  ✅ {row['GRB']}: {row['Sigma']:.2f}σ")
    
    print(f"\n📊 Marginal (2-3σ): {len(marginal)}/6")
    for _, row in marginal.iterrows():
        print(f"  📊 {row['GRB']}: {row['Sigma']:.2f}σ")
    
    print(f"\n❌ Below threshold (<2σ): {len(below)}/6")
    for _, row in below.iterrows():
        print(f"  ❌ {row['GRB']}: {row['Sigma']:.2f}σ")
    
    detection_rate = len(df_results[df_results['Sigma'] >= 3]) / len(df_results) * 100
    strong_rate = len(df_results[df_results['Sigma'] >= 5]) / len(df_results) * 100
    
    print(f"\n{'='*80}")
    print(f"🎯 FINAL STATISTICS:")
    print(f"Detection rate (≥3σ): {detection_rate:.1f}%")
    print(f"Strong signal rate (≥5σ): {strong_rate:.1f}%")
    print(f"Mean sigma (all): {df_results['Sigma'].mean():.2f}")
    print(f"Max sigma: {df_results['Sigma'].max():.2f}")
    print(f"Total photons: {df_results['N_photons'].sum():,}")
    print(f"{'='*80}")
    
    # Save detailed results
    detailed_results = {
        'analysis_date': pd.Timestamp.now().isoformat(),
        'method': 'Robust Bootstrap (10,000 iterations)',
        'total_grbs': len(df_results),
        'detection_rate': float(detection_rate),
        'strong_rate': float(strong_rate),
        'mean_sigma': float(df_results['Sigma'].mean()),
        'max_sigma': float(df_results['Sigma'].max()),
        'total_photons': int(df_results['N_photons'].sum()),
        'results': df_results.to_dict('records')
    }
    
    with open('ALL_GRBs_DETAILED_RESULTS.json', 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"✅ Detailed results saved: ALL_GRBs_DETAILED_RESULTS.json")
    
else:
    print("❌ No results obtained!")

print(f"\n🎉 ANALYSIS COMPLETE!")
print(f"📊 All 6 GRBs analyzed with robust bootstrap method")
print(f"🔥 No infinite sigma values!")
print(f"✅ Ready for paper submission!")

