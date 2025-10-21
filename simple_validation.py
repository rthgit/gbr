#!/usr/bin/env python3
"""
SIMPLE VALIDATION - GRB090510 6.46 SIGMA
Simple validation of the 6.46 sigma effect
"""

import pandas as pd
import numpy as np
from scipy import stats

def main():
    print("SIMPLE VALIDATION - GRB090510 6.46 SIGMA")
    print("=" * 60)
    
    # Load data
    df = pd.read_csv('GRB090510_PH00.csv')
    print(f"✅ Loaded {len(df)} photons")
    
    # Phase analysis (early/late split)
    df_sorted = df.sort_values('TIME').reset_index(drop=True)
    split_idx = len(df_sorted) // 2
    early_df = df_sorted.iloc[:split_idx]
    late_df = df_sorted.iloc[split_idx:]
    
    print(f"\nPhase analysis:")
    print(f"  Early phase: {len(early_df)} photons")
    print(f"  Late phase: {len(late_df)} photons")
    
    # Calculate correlations
    early_r, early_p = stats.pearsonr(early_df['ENERGY'], early_df['TIME'])
    late_r, late_p = stats.pearsonr(late_df['ENERGY'], late_df['TIME'])
    
    print(f"\nCorrelations:")
    print(f"  Early phase: r = {early_r:.4f}, p = {early_p:.2e}")
    print(f"  Late phase: r = {late_r:.4f}, p = {late_p:.2e}")
    
    # Calculate sigma
    if late_p > 0:
        late_sigma = stats.norm.ppf(1 - late_p/2)
    else:
        late_sigma = float('inf')
    
    print(f"\nResults:")
    print(f"  Late phase sigma: {late_sigma:.2f}")
    
    # Bootstrap validation
    print(f"\nBootstrap validation (100 samples)...")
    bootstrap_sigmas = []
    
    for i in range(100):
        boot_df = df.sample(n=len(df), replace=True)
        boot_sorted = boot_df.sort_values('TIME').reset_index(drop=True)
        split_idx = len(boot_sorted) // 2
        late_boot = boot_sorted.iloc[split_idx:]
        
        if len(late_boot) >= 3:
            _, boot_p = stats.pearsonr(late_boot['ENERGY'], late_boot['TIME'])
            if boot_p > 0:
                boot_sigma = stats.norm.ppf(1 - boot_p/2)
                bootstrap_sigmas.append(boot_sigma)
    
    if bootstrap_sigmas:
        bootstrap_mean = np.mean(bootstrap_sigmas)
        bootstrap_std = np.std(bootstrap_sigmas)
        
        print(f"  Bootstrap mean: {bootstrap_mean:.2f} ± {bootstrap_std:.2f}")
        print(f"  Bootstrap samples: {len(bootstrap_sigmas)}")
        
        if bootstrap_mean > 5.0:
            print(f"  ✅ EFFECT VALIDATED - Bootstrap confirms high significance")
        elif bootstrap_mean > 3.0:
            print(f"  ⚠️ EFFECT PARTIALLY VALIDATED - Bootstrap shows moderate significance")
        else:
            print(f"  ❌ EFFECT NOT VALIDATED - Bootstrap shows low significance")
    
    print(f"\n{'='*60}")
    print("VALIDATION COMPLETE!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
