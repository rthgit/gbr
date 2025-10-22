#!/usr/bin/env python3
"""
SIMPLE ALL 6 GRBs ANALYSIS
Analizza tutti i GRB con metodo semplificato
"""

import pandas as pd
import numpy as np
from scipy import stats

print("SIMPLE ALL 6 GRBs ANALYSIS")
print("=" * 50)

# Lista GRB
grbs = ['GRB090926A', 'GRB090510', 'GRB090902B', 'GRB130427A', 'GRB160625B', 'GRB080916C']

results = []

for grb_name in grbs:
    print(f"\nAnalyzing: {grb_name}")
    print("-" * 30)
    
    try:
        # Carica dati
        df = pd.read_csv(f'{grb_name}_PH00.csv')
        print(f"✅ Loaded {len(df)} photons")
        
        # Converti energia se necessario
        if df['ENERGY'].max() > 1000:
            df['ENERGY'] = df['ENERGY'] / 1000.0
            print("⚠️ Energy converted to GeV")
        
        energy = df['ENERGY'].values
        time = df['TIME'].values
        
        print(f"E_max: {energy.max():.2f} GeV")
        
        # Analisi Spearman
        rho, p_value = stats.spearmanr(energy, time)
        
        # Calcola sigma in modo sicuro
        if p_value <= 1e-300:
            sigma = 15.0  # Cap at 15σ
        else:
            try:
                sigma = stats.norm.ppf(1 - p_value/2)
                if not np.isfinite(sigma) or sigma > 15:
                    sigma = 15.0
            except:
                sigma = 15.0
        
        print(f"Spearman ρ: {rho:.4f}")
        print(f"P-value: {p_value:.2e}")
        print(f"Sigma: {sigma:.2f}")
        
        # Classification
        if sigma >= 5:
            classification = "STRONG"
            emoji = "🔥"
        elif sigma >= 3:
            classification = "SIGNIFICANT"
            emoji = "✅"
        elif sigma >= 2:
            classification = "MARGINAL"
            emoji = "📊"
        else:
            classification = "BELOW THRESHOLD"
            emoji = "❌"
        
        print(f"{emoji} {classification}")
        
        results.append({
            'GRB': grb_name,
            'N_photons': len(energy),
            'E_max_GeV': energy.max(),
            'Spearman_rho': rho,
            'Sigma': sigma,
            'P_value': p_value,
            'Classification': classification
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        continue

# Risultati finali
print("\n" + "=" * 50)
print("FINAL RESULTS")
print("=" * 50)

if results:
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('Sigma', ascending=False)
    
    print("\n" + df_results.to_string(index=False))
    
    # Statistiche
    strong = df_results[df_results['Sigma'] >= 5]
    significant = df_results[(df_results['Sigma'] >= 3) & (df_results['Sigma'] < 5)]
    
    print(f"\n🔥 Strong (≥5σ): {len(strong)}/6")
    print(f"✅ Significant (3-5σ): {len(significant)}/6")
    
    detection_rate = len(df_results[df_results['Sigma'] >= 3]) / len(df_results) * 100
    print(f"📊 Detection rate (≥3σ): {detection_rate:.1f}%")
    print(f"📈 Max sigma: {df_results['Sigma'].max():.2f}")
    
    # Salva risultati
    df_results.to_csv('SIMPLE_ALL_GRBs_RESULTS.csv', index=False)
    print(f"\n✅ Results saved: SIMPLE_ALL_GRBs_RESULTS.csv")

print(f"\n🎉 Analysis complete!")

