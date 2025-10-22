#!/usr/bin/env python3
"""
FIX INFINITE SIGMA - DIRECT CALCULATION
"""

import numpy as np
import pandas as pd
from scipy import stats
import json

print("FIXING INFINITE SIGMA FOR GRB090926A")
print("="*50)

# Load data
df = pd.read_csv('grb_data/raw/GRB090926A_corrected_GeV.csv')

# Convert energy if needed
if df['ENERGY'].max() > 1000:
    df['ENERGY'] = df['ENERGY'] / 1000.0
    print("✅ Energy converted to GeV")

energy = df['ENERGY'].values
time = df['TIME'].values

print(f"Data: {len(energy)} photons, E_max = {energy.max():.2f} GeV")

# Calculate correlation
rho, p_value = stats.spearmanr(energy, time)
print(f"Spearman ρ = {rho:.6f}")
print(f"P-value = {p_value:.2e}")

# PROBLEM: p_value too small causes inf sigma
print(f"\n🔍 DIAGNOSIS:")
print(f"P-value: {p_value:.2e}")
print(f"This is extremely small - causes numerical overflow in ppf()")

# SOLUTION 1: Bootstrap method (most robust)
print(f"\n🔧 SOLUTION 1: BOOTSTRAP METHOD")
n_boot = 2000
boot_correlations = []

print("Running bootstrap...")
for i in range(n_boot):
    if i % 500 == 0:
        print(f"  {i}/{n_boot}")
    # Shuffle time to break correlation
    time_shuffled = np.random.permutation(time)
    boot_rho, _ = stats.spearmanr(energy, time_shuffled)
    boot_correlations.append(boot_rho)

boot_correlations = np.array(boot_correlations)
boot_std = np.std(boot_correlations)

# Bootstrap sigma
sigma_bootstrap = abs(rho) / boot_std
p_bootstrap = np.sum(np.abs(boot_correlations) >= abs(rho)) / n_boot

print(f"Bootstrap σ = {sigma_bootstrap:.2f}")
print(f"Bootstrap p-value = {p_bootstrap:.2e}" if p_bootstrap > 0 else f"Bootstrap p-value < {1/n_boot:.2e}")

# SOLUTION 2: Safe analytical
print(f"\n🔧 SOLUTION 2: SAFE ANALYTICAL")
if p_value <= 1e-300:
    sigma_safe = 10.0  # Cap at 10σ
    print(f"P-value extremely small, capping at σ = {sigma_safe}")
else:
    try:
        sigma_safe = stats.norm.ppf(1 - p_value/2)
        if not np.isfinite(sigma_safe) or sigma_safe > 10:
            sigma_safe = 10.0
        print(f"Analytical σ = {sigma_safe:.2f}")
    except:
        sigma_safe = 10.0
        print(f"Error in calculation, capping at σ = {sigma_safe}")

# FINAL RESULT
print(f"\n🎯 FINAL RESULT:")
print(f"GRB090926A: {sigma_bootstrap:.2f}σ (Bootstrap method)")
print(f"Spearman ρ = {rho:.4f}")
print(f"P-value < {1/n_boot:.2e}")

# Classification
if sigma_bootstrap >= 5:
    classification = "STRONG (≥5σ)"
elif sigma_bootstrap >= 3:
    classification = "SIGNIFICANT (3-5σ)"
else:
    classification = "BELOW THRESHOLD (<3σ)"

print(f"Classification: {classification}")

# Save corrected result
result = {
    'grb': 'GRB090926A',
    'n_photons': int(len(energy)),
    'e_max_gev': float(energy.max()),
    'spearman_rho': float(rho),
    'sigma_corrected': float(sigma_bootstrap),
    'p_value': float(p_bootstrap) if p_bootstrap > 0 else f'<{1/n_boot:.2e}',
    'classification': classification,
    'method': 'Bootstrap (robust)'
}

with open('GRB090926A_CORRECTED_sigma.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"\n✅ Corrected result saved: GRB090926A_CORRECTED_sigma.json")
print("="*50)

