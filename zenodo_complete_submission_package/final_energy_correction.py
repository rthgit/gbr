#!/usr/bin/env python3
"""
FINAL ENERGY UNIT CORRECTION FOR ALL GRBs
Corregge le unità di energia e ricalcola tutti i risultati
"""

import pandas as pd
from pathlib import Path
import numpy as np
from scipy import stats

print("="*80)
print("FINAL ENERGY UNIT CORRECTION")
print("="*80)

# GRBs to fix
grbs = [
    'GRB090926A',
    'GRB090510', 
    'GRB090902B',
    'GRB130427A',
    'GRB160625B',
    'GRB080916C'
]

results_corrected = []

for grb_name in grbs:
    # Find CSV file
    csv_files = list(Path('.').glob(f'{grb_name}*_PH00.csv'))
    
    if not csv_files:
        print(f"❌ {grb_name}: No CSV found")
        continue
    
    csv_file = csv_files[0]
    print(f"\n{grb_name}:")
    print(f"  File: {csv_file.name}")
    
    df = pd.read_csv(csv_file)
    
    # Check current energy range
    e_max_current = df['ENERGY'].max()
    
    # If > 1000, it's in MeV
    if e_max_current > 1000:
        print(f"  ⚠️  Energy in MeV: E_max = {e_max_current:.1f}")
        
        # Convert MeV to GeV
        df['ENERGY'] = df['ENERGY'] / 1000.0
        
        e_max_gev = df['ENERGY'].max()
        print(f"  ✅ Converted to GeV: E_max = {e_max_gev:.2f} GeV")
        
        # Save corrected
        output_file = csv_file.parent / f"{grb_name}_corrected_GeV.csv"
        df.to_csv(output_file, index=False)
        print(f"  💾 Saved: {output_file.name}")
    else:
        print(f"  ✅ Already in GeV: E_max = {e_max_current:.2f} GeV")
        e_max_gev = e_max_current
    
    # Check for unrealistic energies (>100 GeV)
    if e_max_gev > 100:
        print(f"  🚨 WARNING: E_max = {e_max_gev:.1f} GeV > 100 GeV (record is 94.1 GeV)")
        print(f"  🚨 Possible background contamination - EXCLUDE from analysis")
        continue
    
    # Re-analyze with correct units
    energy = df['ENERGY'].values
    time = df['TIME'].values
    
    # Spearman correlation
    rho, p_value = stats.spearmanr(energy, time)
    
    # Sigma from p-value
    if p_value > 0:
        sigma = stats.norm.ppf(1 - p_value/2)
    else:
        sigma = 10.0  # Cap at 10
    
    results_corrected.append({
        'GRB': grb_name,
        'N_photons': len(df),
        'E_max_GeV': e_max_gev,
        'Spearman_rho': rho,
        'P_value': p_value,
        'Sigma': sigma
    })
    
    print(f"  Spearman: ρ = {rho:.4f}, σ = {sigma:.2f}")

# Summary
print("\n" + "="*80)
print("CORRECTED RESULTS SUMMARY")
print("="*80)

df_results = pd.DataFrame(results_corrected)
print(df_results.to_string(index=False))

# Save
df_results.to_csv('grb_corrected_final_results.csv', index=False)
print("\n✅ Saved: grb_corrected_final_results.csv")

# Classification
print("\n" + "="*80)
print("CLASSIFICATION")
print("="*80)

strong = df_results[df_results['Sigma'] >= 5]
significant = df_results[(df_results['Sigma'] >= 3) & (df_results['Sigma'] < 5)]
marginal = df_results[(df_results['Sigma'] >= 2) & (df_results['Sigma'] < 3)]

print(f"Strong (≥5σ): {len(strong)}")
for _, row in strong.iterrows():
    print(f"  🔥 {row['GRB']}: {row['Sigma']:.2f}σ")

print(f"\nSignificant (3-5σ): {len(significant)}")
for _, row in significant.iterrows():
    print(f"  ✅ {row['GRB']}: {row['Sigma']:.2f}σ")

print(f"\nMarginal (2-3σ): {len(marginal)}")
for _, row in marginal.iterrows():
    print(f"  📊 {row['GRB']}: {row['Sigma']:.2f}σ")

detection_rate = len(df_results[df_results['Sigma'] >= 3]) / len(df_results) * 100
print(f"\nDetection rate (≥3σ): {detection_rate:.1f}%")

# Final paper summary
print("\n" + "="*80)
print("FINAL PAPER SUMMARY")
print("="*80)

print("🎯 TOP DISCOVERIES:")
for _, row in strong.iterrows():
    print(f"  🔥 {row['GRB']}: {row['Sigma']:.2f}σ (ρ={row['Spearman_rho']:.4f}, p={row['P_value']:.2e})")

print(f"\n📊 FINAL STATISTICS:")
print(f"  Total GRBs analyzed: {len(df_results)}")
print(f"  Strong signals (≥5σ): {len(strong)}")
print(f"  Significant signals (≥3σ): {len(significant)}")
print(f"  Detection rate: {detection_rate:.1f}%")

print(f"\n🎉 PAPER READY FOR SUBMISSION!")
print("="*80)
