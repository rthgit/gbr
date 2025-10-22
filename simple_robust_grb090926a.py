#!/usr/bin/env python3
"""
SIMPLE ROBUST GRB090926A ANALYSIS - NO INFINITIES!
"""

import numpy as np
import pandas as pd
from scipy import stats
import json

print("="*80)
print("GRB090926A - SIMPLE ROBUST ANALYSIS")
print("="*80)

# Load data
df = pd.read_csv('grb_data/raw/GRB090926A_corrected_GeV.csv')

# Convert energy if needed
if df['ENERGY'].max() > 1000:
    df['ENERGY'] = df['ENERGY'] / 1000.0
    print("✅ Energy converted to GeV")

energy = df['ENERGY'].values
time = df['TIME'].values

print(f"\nData loaded:")
print(f"  N photons: {len(energy)}")
print(f"  Energy range: {energy.min():.3f} - {energy.max():.2f} GeV")
print(f"  Time range: {time.min():.1f} - {time.max():.1f} s")

# Observed correlation
r_obs, p_obs = stats.spearmanr(energy, time)
print(f"\nObserved Spearman ρ: {r_obs:.6f}")
print(f"Observed p-value: {p_obs:.2e}")

# Method 1: Bootstrap (simplified)
print("\n" + "-"*60)
print("BOOTSTRAP ANALYSIS (n=5,000)")
print("-"*60)

n_boot = 5000
boot_r = np.zeros(n_boot)

print("Running bootstrap...")
for i in range(n_boot):
    if i % 1000 == 0:
        print(f"  Progress: {i}/{n_boot}")
    time_shuffled = np.random.permutation(time)
    boot_r[i], _ = stats.spearmanr(energy, time_shuffled)

sigma_boot = abs(r_obs) / np.std(boot_r)
p_boot = np.sum(np.abs(boot_r) >= np.abs(r_obs)) / n_boot

print(f"\nBootstrap results:")
print(f"  σ (bootstrap): {sigma_boot:.2f}")
print(f"  p-value (bootstrap): {p_boot:.2e}" if p_boot > 0 else f"  p-value: < {1/n_boot:.2e}")
print(f"  Bootstrap std: {np.std(boot_r):.6f}")

# Method 2: Safe analytical
print("\n" + "-"*60)
print("SAFE ANALYTICAL")
print("-"*60)

# Safe p-value to sigma conversion
if p_obs <= 1e-300:
    sigma_safe = 15.0  # Cap at 15σ
    print(f"P-value extremely small: {p_obs:.2e}")
    print(f"σ (capped): {sigma_safe:.2f}")
else:
    try:
        sigma_safe = stats.norm.ppf(1 - p_obs/2)
        if not np.isfinite(sigma_safe) or sigma_safe > 15:
            sigma_safe = 15.0
        print(f"σ (analytical): {sigma_safe:.2f}")
    except:
        sigma_safe = 15.0
        print(f"σ (capped due to error): {sigma_safe:.2f}")

# Final result
print("\n" + "="*80)
print("FINAL RESULT")
print("="*80)

# Use bootstrap as most reliable
sigma_final = sigma_boot

print(f"\n🎯 GRB090926A Significance: {sigma_final:.2f}σ")
print(f"Method: Bootstrap (most robust)")
print(f"Spearman ρ: {r_obs:.4f}")
print(f"P-value: {p_boot:.2e}" if p_boot > 0 else f"P-value: < {1/n_boot:.2e}")
print(f"N photons: {len(energy):,}")
print(f"E_max: {energy.max():.2f} GeV")

# Classification
if sigma_final >= 5:
    classification = "STRONG (≥5σ)"
elif sigma_final >= 3:
    classification = "SIGNIFICANT (3-5σ)"
elif sigma_final >= 2:
    classification = "MARGINAL (2-3σ)"
else:
    classification = "BELOW THRESHOLD (<2σ)"

print(f"Classification: {classification}")

# Save results
result = {
    'grb': 'GRB090926A',
    'n_photons': int(len(energy)),
    'e_max_gev': float(energy.max()),
    'spearman_rho': float(r_obs),
    'sigma_bootstrap': float(sigma_boot),
    'sigma_final': float(sigma_final),
    'p_value': float(p_boot) if p_boot > 0 else f'<{1/n_boot:.2e}',
    'classification': classification
}

with open('GRB090926A_SIMPLE_results.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"\n✅ Results saved: GRB090926A_SIMPLE_results.json")
print("="*80)

