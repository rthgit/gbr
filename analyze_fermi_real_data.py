#!/usr/bin/env python3
"""
ANALYZE FERMI REAL DATA
======================

Analisi dati reali Fermi LAT per effetti QG.
Pipeline completa per analisi GRB reali.

Autore: Christian Quintino De Luca
Affiliazione: RTH Italia - Research & Technology Hub
DOI: 10.5281/zenodo.17404757
"""

import numpy as np
import pandas as pd
import json
from datetime import datetime
from scipy import stats
from sklearn.linear_model import RANSACRegressor
from sklearn.utils import resample
import os

def load_fermi_data():
    """
    Carica dati Fermi scaricati
    """
    print("🛰️ Loading Fermi LAT real data...")
    
    data_files = []
    for file in os.listdir('fermi_data/grb_catalog/'):
        if file.endswith('_fermi_data.csv'):
            data_files.append(file)
    
    print(f"✅ Found {len(data_files)} GRB data files")
    return data_files

def analyze_grb_real_data(grb_name, data):
    """
    Analizza singolo GRB con dati reali
    """
    print(f"🔍 Analyzing {grb_name} with real data...")
    
    # Estrai dati
    E = data['energy'].values
    t = data['time'].values
    z = data['redshift'].iloc[0]
    trigger_time = data['trigger_time'].iloc[0]
    
    # Converti tempi in secondi relativi al trigger
    t_rel = t - trigger_time
    
    # Analisi correlazione energia-tempo
    pearson_r, pearson_p = stats.pearsonr(E, t_rel)
    spearman_r, spearman_p = stats.spearmanr(E, t_rel)
    
    # Test significatività
    n = len(E)
    t_stat = pearson_r * np.sqrt((n-2)/(1-pearson_r**2))
    sigma = abs(t_stat)
    
    # Permutation test
    n_perm = 1000
    perm_correlations = []
    for _ in range(n_perm):
        E_perm = np.random.permutation(E)
        r_perm, _ = stats.pearsonr(E_perm, t_rel)
        perm_correlations.append(r_perm)
    
    perm_p = np.mean(np.abs(perm_correlations) >= abs(pearson_r))
    
    # Bootstrap analysis
    n_bootstrap = 1000
    bootstrap_correlations = []
    for _ in range(n_bootstrap):
        indices = resample(range(n), n_samples=n)
        E_bs = E[indices]
        t_bs = t_rel[indices]
        r_bs, _ = stats.pearsonr(E_bs, t_bs)
        bootstrap_correlations.append(r_bs)
    
    bootstrap_ci = np.percentile(bootstrap_correlations, [2.5, 97.5])
    
    # RANSAC regression
    X = E.reshape(-1, 1)
    y = t_rel
    ransac = RANSACRegressor(random_state=42)
    ransac.fit(X, y)
    slope = ransac.estimator_.coef_[0]
    inliers = np.sum(ransac.inlier_mask_)
    inlier_ratio = inliers / n
    
    # Stima E_QG
    if abs(slope) > 1e-10:
        K_z = (1 + z) * z / 70  # Fattore cosmologico
        E_QG = K_z / abs(slope)
        E_QG_Planck = E_QG / 1.22e19  # Rispetto a E_Planck
    else:
        E_QG = np.inf
        E_QG_Planck = np.inf
    
    # Risultati
    results = {
        'grb_name': grb_name,
        'redshift': z,
        'n_photons': n,
        'energy_range': [E.min(), E.max()],
        'time_range': [t_rel.min(), t_rel.max()],
        'pearson_r': pearson_r,
        'pearson_p': pearson_p,
        'spearman_r': spearman_r,
        'spearman_p': spearman_p,
        'sigma': sigma,
        'permutation_p': perm_p,
        'bootstrap_ci': bootstrap_ci,
        'ransac_slope': slope,
        'ransac_inliers': inliers,
        'ransac_inlier_ratio': inlier_ratio,
        'E_QG_GeV': E_QG,
        'E_QG_Planck': E_QG_Planck,
        'significant': sigma > 3.0 and perm_p < 0.05
    }
    
    print(f"   📊 Correlation: r={pearson_r:.4f}, σ={sigma:.2f}, p={perm_p:.4f}")
    print(f"   📊 RANSAC: slope={slope:.2e}, inliers={inliers}/{n} ({inlier_ratio:.1%})")
    print(f"   📊 E_QG: {E_QG:.2e} GeV ({E_QG_Planck:.2e} E_Planck)")
    print(f"   📊 Significant: {results['significant']}")
    
    return results

def analyze_fermi_real_data():
    """
    Analisi completa dati Fermi reali
    """
    print("🔬 FERMI REAL DATA ANALYSIS")
    print("=" * 60)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 60)
    
    # Carica dati
    data_files = load_fermi_data()
    
    results = {}
    qg_effects = []
    
    # Analizza ogni GRB
    for file in data_files:
        grb_name = file.replace('_fermi_data.csv', '')
        print(f"\n🔍 Analyzing {grb_name}...")
        
        try:
            # Carica dati
            data = pd.read_csv(f'fermi_data/grb_catalog/{file}')
            
            # Analizza GRB
            result = analyze_grb_real_data(grb_name, data)
            results[grb_name] = result
            
            if result['significant']:
                qg_effects.append(grb_name)
                
        except Exception as e:
            print(f"❌ Error analyzing {grb_name}: {e}")
            continue
    
    # Analisi statistica popolazione
    print(f"\n📊 POPULATION ANALYSIS:")
    print(f"   Total GRBs: {len(results)}")
    print(f"   Significant: {len(qg_effects)}")
    print(f"   Success Rate: {len(qg_effects)/len(results):.1%}")
    
    # Salva risultati
    save_fermi_results(results, qg_effects)
    
    print("=" * 60)
    print("✅ FERMI REAL DATA ANALYSIS COMPLETE!")
    print("📊 Check generated files for results")
    print("=" * 60)

def save_fermi_results(results, qg_effects):
    """
    Salva risultati analisi Fermi
    """
    print("💾 Saving Fermi real data analysis results...")
    
    # Salva risultati JSON
    results_data = {
        'analysis_date': datetime.now().isoformat(),
        'total_grbs': len(results),
        'significant_grbs': len(qg_effects),
        'success_rate': len(qg_effects) / len(results),
        'grb_results': results
    }
    
    with open('fermi_data/analysis_results/fermi_real_analysis_results.json', 'w') as f:
        json.dump(results_data, f, indent=2, default=str)
    
    # Salva summary CSV
    summary_data = []
    for grb_name, result in results.items():
        summary_data.append({
            'GRB': grb_name,
            'Redshift': result['redshift'],
            'Photons': result['n_photons'],
            'Correlation': result['pearson_r'],
            'Significance': result['sigma'],
            'P_value': result['permutation_p'],
            'RANSAC_slope': result['ransac_slope'],
            'RANSAC_inliers': result['ransac_inliers'],
            'RANSAC_inlier_ratio': result['ransac_inlier_ratio'],
            'E_QG_GeV': result['E_QG_GeV'],
            'E_QG_Planck': result['E_QG_Planck'],
            'Significant': result['significant']
        })
    
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_csv('fermi_data/analysis_results/fermi_real_analysis_summary.csv', index=False)
    
    print("✅ Results saved: fermi_real_analysis_results.json, fermi_real_analysis_summary.csv")

if __name__ == "__main__":
    analyze_fermi_real_data()
