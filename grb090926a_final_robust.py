#!/usr/bin/env python3
"""
FINAL GRB090926A ANALYSIS - NO INFINITIES!
Combines all robust methods to eliminate infinite sigma
"""

import numpy as np
import pandas as pd
from scipy import stats
from tqdm import tqdm
import matplotlib.pyplot as plt
import json

print("="*80)
print("GRB090926A - FINAL ROBUST ANALYSIS")
print("="*80)

# Load data
df = pd.read_csv('GRB090926A_corrected_GeV.csv')

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

# Method 1: Bootstrap
print("\n" + "-"*80)
print("METHOD 1: BOOTSTRAP ANALYSIS (n=10,000)")
print("-"*80)

r_obs, _ = stats.spearmanr(energy, time)
print(f"Observed Spearman ρ: {r_obs:.6f}")

n_boot = 10000
boot_r = np.zeros(n_boot)

for i in tqdm(range(n_boot), desc="Bootstrap"):
    time_shuffled = np.random.permutation(time)
    boot_r[i], _ = stats.spearmanr(energy, time_shuffled)

sigma_boot = abs(r_obs) / np.std(boot_r)
p_boot = np.sum(np.abs(boot_r) >= np.abs(r_obs)) / n_boot

print(f"\nBootstrap results:")
print(f"  σ (bootstrap): {sigma_boot:.2f}")
print(f"  p-value (bootstrap): {p_boot:.2e}" if p_boot > 0 else f"  p-value: < {1/n_boot:.2e}")
print(f"  Bootstrap std: {np.std(boot_r):.6f}")

# Method 2: Permutation Test
print("\n" + "-"*80)
print("METHOD 2: PERMUTATION TEST (n=100,000)")
print("-"*80)

n_perm = 100000
r_perm = np.zeros(n_perm)

for i in tqdm(range(n_perm), desc="Permutation"):
    time_perm = np.random.permutation(time)
    r_perm[i], _ = stats.spearmanr(energy, time_perm)

n_exceed = np.sum(np.abs(r_perm) >= np.abs(r_obs))
p_perm = n_exceed / n_perm

if p_perm == 0:
    sigma_perm = stats.norm.ppf(1 - 1/(2*n_perm))
    print(f"No permutations exceeded observed")
    print(f"σ > {sigma_perm:.2f} (lower bound)")
else:
    sigma_perm = stats.norm.ppf(1 - p_perm/2)
    print(f"{n_exceed} / {n_perm} permutations exceeded")
    print(f"σ = {sigma_perm:.2f}")

# Method 3: Analytical (safe)
print("\n" + "-"*80)
print("METHOD 3: ANALYTICAL (SAFE)")
print("-"*80)

_, p_analytical = stats.spearmanr(energy, time)
print(f"Analytical p-value: {p_analytical:.2e}")

# Safe conversion
if p_analytical > 1e-300:
    sigma_analytical = min(stats.norm.ppf(1 - p_analytical/2), 15.0)
else:
    sigma_analytical = 15.0

print(f"σ (analytical, capped): {sigma_analytical:.2f}")

# Final recommendation
print("\n" + "="*80)
print("FINAL RECOMMENDED RESULT")
print("="*80)

sigma_final = sigma_boot  # Use bootstrap as most robust
print(f"\n🎯 GRB090926A Significance: {sigma_final:.2f}σ")
print(f"\nMethod: Bootstrap (most robust)")
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

# Plot distributions
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.hist(boot_r, bins=50, alpha=0.7, edgecolor='black', density=True)
ax.axvline(r_obs, color='red', linewidth=2, label=f'Observed: {r_obs:.4f}')
ax.axvline(-r_obs, color='red', linewidth=2, linestyle='--')
ax.set_xlabel('Spearman ρ')
ax.set_ylabel('Density')
ax.set_title('Bootstrap Distribution')
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.scatter(time - time.min(), energy, alpha=0.3, s=10)
ax.set_xlabel('Time since trigger (s)')
ax.set_ylabel('Energy (GeV)')
ax.set_yscale('log')
ax.set_title(f'GRB090926A: σ = {sigma_final:.2f}')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('GRB090926A_FINAL_robust.png', dpi=150, bbox_inches='tight')
print(f"\n✅ Plot saved: GRB090926A_FINAL_robust.png")

# Save results
result = {
    'grb': 'GRB090926A',
    'n_photons': int(len(energy)),
    'e_max_gev': float(energy.max()),
    'spearman_rho': float(r_obs),
    'sigma_bootstrap': float(sigma_boot),
    'sigma_permutation': float(sigma_perm) if p_perm > 0 else f'>{sigma_perm:.2f}',
    'sigma_final': float(sigma_final),
    'p_value': float(p_boot) if p_boot > 0 else f'<{1/n_boot:.2e}',
    'classification': classification
}

with open('GRB090926A_FINAL_results.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"✅ Results saved: GRB090926A_FINAL_results.json")
print("="*80)
