#!/usr/bin/env python3
"""
FIX INFINITE SIGMA - DEFINITIVE SOLUTION
Risolve il problema dell'infinito con metodo bootstrap robusto
"""

import pandas as pd
import numpy as np
from scipy import stats
import json

def fix_infinite_sigma():
    """Risolve definitivamente il problema dell'infinito"""
    print("FIX INFINITE SIGMA - DEFINITIVE SOLUTION")
    print("=" * 60)
    
    # Carica dati
    df = pd.read_csv('GRB090926A_PH00.csv')
    print(f"✅ Loaded {len(df)} photons")
    
    # Converti energia da MeV a GeV se necessario
    if df['ENERGY'].max() > 1000:
        print("⚠️ Converting energy from MeV to GeV")
        df['ENERGY'] = df['ENERGY'] / 1000.0
    
    print(f"Energy range: {df['ENERGY'].min():.3f} - {df['ENERGY'].max():.3f} GeV")
    print(f"Time range: {df['TIME'].min():.1f} - {df['TIME'].max():.1f} s")
    
    # Analisi correlazioni
    energy = df['ENERGY'].values
    time = df['TIME'].values
    
    # Spearman correlation
    spearman_rho, spearman_p = stats.spearmanr(energy, time)
    
    print(f"\nOBSERVED CORRELATION:")
    print(f"Spearman ρ: {spearman_rho:.6f}")
    print(f"P-value: {spearman_p:.2e}")
    
    # METODO 1: Bootstrap robusto
    print(f"\n🔧 BOOTSTRAP METHOD (n=10,000):")
    print("Running bootstrap to avoid infinite sigma...")
    
    n_bootstrap = 10000
    boot_correlations = []
    
    for i in range(n_bootstrap):
        if i % 2000 == 0:
            print(f"  Progress: {i}/{n_bootstrap}")
        # Shuffle time to break correlation
        time_shuffled = np.random.permutation(time)
        boot_corr, _ = stats.spearmanr(energy, time_shuffled)
        boot_correlations.append(boot_corr)
    
    # Calculate sigma from bootstrap distribution
    boot_std = np.std(boot_correlations)
    sigma_bootstrap = abs(spearman_rho) / boot_std
    
    # Count how many bootstrap correlations exceed observed
    n_exceed = np.sum(np.abs(boot_correlations) >= np.abs(spearman_rho))
    p_bootstrap = n_exceed / n_bootstrap
    
    print(f"\nBootstrap results:")
    print(f"  Bootstrap std: {boot_std:.6f}")
    print(f"  Sigma (bootstrap): {sigma_bootstrap:.2f}")
    print(f"  P-value (bootstrap): {p_bootstrap:.2e}" if p_bootstrap > 0 else f"  P-value: < {1/n_bootstrap:.2e}")
    print(f"  Exceedances: {n_exceed}/{n_bootstrap}")
    
    # METODO 2: Safe analytical
    print(f"\n🔧 SAFE ANALYTICAL METHOD:")
    
    if spearman_p <= 1e-300:
        sigma_analytical = 15.0  # Cap at 15σ
        print(f"  P-value extremely small: {spearman_p:.2e}")
        print(f"  Sigma (capped): {sigma_analytical:.2f}")
    else:
        try:
            sigma_analytical = stats.norm.ppf(1 - spearman_p/2)
            if not np.isfinite(sigma_analytical) or sigma_analytical > 15:
                sigma_analytical = 15.0
            print(f"  Sigma (analytical): {sigma_analytical:.2f}")
        except:
            sigma_analytical = 15.0
            print(f"  Sigma (capped due to error): {sigma_analytical:.2f}")
    
    # RISULTATO FINALE
    print(f"\n" + "="*60)
    print(f"FINAL RESULT")
    print(f"="*60)
    
    # Usa bootstrap come più robusto
    sigma_final = sigma_bootstrap
    
    print(f"\n🎯 GRB090926A Significance: {sigma_final:.2f}σ")
    print(f"Method: Bootstrap (most robust)")
    print(f"Spearman ρ: {spearman_rho:.4f}")
    print(f"P-value: {p_bootstrap:.2e}" if p_bootstrap > 0 else f"P-value: < {1/n_bootstrap:.2e}")
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
    
    # Salva risultati
    result = {
        'grb': 'GRB090926A',
        'n_photons': int(len(energy)),
        'e_max_gev': float(energy.max()),
        'spearman_rho': float(spearman_rho),
        'sigma_bootstrap': float(sigma_bootstrap),
        'sigma_analytical': float(sigma_analytical),
        'sigma_final': float(sigma_final),
        'p_value_bootstrap': float(p_bootstrap) if p_bootstrap > 0 else f'<{1/n_bootstrap:.2e}',
        'p_value_analytical': float(spearman_p),
        'classification': classification,
        'method': 'Bootstrap (robust)'
    }
    
    with open('GRB090926A_FIXED_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Results saved: GRB090926A_FIXED_results.json")
    print(f"🎉 NO MORE INFINITE SIGMA!")
    print(f"🎯 Final sigma: {sigma_final:.2f}σ (robust bootstrap)")
    
    return sigma_final

if __name__ == "__main__":
    fix_infinite_sigma()
