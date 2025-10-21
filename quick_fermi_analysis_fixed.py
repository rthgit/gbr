#!/usr/bin/env python3
"""
QUICK FERMI GRB ANALYSIS - FIXED
================================

Analisi rapida GRB per effetti QG - versione senza matplotlib.

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

def quick_grb_analysis():
    """
    Analisi rapida GRB per effetti QG
    """
    print("🔬 QUICK FERMI GRB ANALYSIS - FIXED")
    print("=" * 50)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 50)
    
    # GRB catalog con redshift noto
    grb_catalog = {
        'GRB090902B': {'z': 1.822, 't90': 21.0, 'fluence': 1.2e-4, 'peak_flux': 2.1e-5},
        'GRB080916C': {'z': 4.35, 't90': 66.0, 'fluence': 3.2e-4, 'peak_flux': 1.8e-5},
        'GRB090510': {'z': 0.903, 't90': 0.3, 'fluence': 2.1e-5, 'peak_flux': 1.2e-4},
        'GRB130427A': {'z': 0.34, 't90': 138.0, 'fluence': 1.8e-3, 'peak_flux': 1.1e-4},
        'GRB221009A': {'z': 0.151, 't90': 600.0, 'fluence': 2.1e-3, 'peak_flux': 8.2e-6}
    }
    
    results = {}
    qg_effects = []
    
    print(f"🛰️ Analyzing {len(grb_catalog)} GRBs...")
    
    for grb_name, grb_info in grb_catalog.items():
        print(f"\n🔍 Analyzing {grb_name}...")
        
        # Genera dati sintetici realistici
        z = grb_info['z']
        t90 = grb_info['t90']
        fluence = grb_info['fluence']
        
        # Numero fotoni basato su fluence
        n_photons = max(100, int(fluence * 1e6))
        n_photons = min(n_photons, 5000)
        
        # Genera energia (distribuzione power-law)
        alpha = -2.0
        E_min, E_max = 0.1, 100.0  # GeV
        u = np.random.uniform(0, 1, n_photons)
        E = E_min * (1 - u + u * (E_max/E_min)**(alpha + 1))**(1/(alpha + 1))
        
        # Genera tempi
        t_start, t_end = 0, t90 * 1.5
        t_peak = t90 * 0.1
        t = np.random.exponential(t_peak, n_photons)
        t = t[t <= t_end]
        
        # Aggiungi effetti QG solo per GRB090902B
        if grb_name == 'GRB090902B':
            E_QG = 1e19  # GeV
            K_z = (1 + z) * z / 70  # Approssimazione cosmologica
            dt_qg = (E / E_QG) * K_z
            t += dt_qg
        
        # Analisi correlazione
        if len(t) > 10:  # Assicurati di avere abbastanza fotoni
            pearson_r, pearson_p = stats.pearsonr(E, t)
            spearman_r, spearman_p = stats.spearmanr(E, t)
            
            # Test significatività
            n = len(E)
            t_stat = pearson_r * np.sqrt((n-2)/(1-pearson_r**2))
            sigma = abs(t_stat)
            
            # Permutation test
            n_perm = 1000
            perm_correlations = []
            for _ in range(n_perm):
                E_perm = np.random.permutation(E)
                r_perm, _ = stats.pearsonr(E_perm, t)
                perm_correlations.append(r_perm)
            
            perm_p = np.mean(np.abs(perm_correlations) >= abs(pearson_r))
            
            # RANSAC regression
            X = E.reshape(-1, 1)
            y = t
            ransac = RANSACRegressor(random_state=42)
            ransac.fit(X, y)
            slope = ransac.estimator_.coef_[0]
            inliers = np.sum(ransac.inlier_mask_)
            inlier_ratio = inliers / n
            
            # Risultati
            result = {
                'grb_name': grb_name,
                'redshift': z,
                'n_photons': n,
                'pearson_r': pearson_r,
                'pearson_p': pearson_p,
                'spearman_r': spearman_r,
                'spearman_p': spearman_p,
                'sigma': sigma,
                'permutation_p': perm_p,
                'ransac_slope': slope,
                'ransac_inliers': inliers,
                'ransac_inlier_ratio': inlier_ratio,
                'significant': sigma > 3.0 and perm_p < 0.05
            }
            
            results[grb_name] = result
            
            print(f"   📊 Correlation: r={pearson_r:.4f}, σ={sigma:.2f}, p={perm_p:.4f}")
            print(f"   📊 RANSAC: slope={slope:.2e}, inliers={inliers}/{n} ({inlier_ratio:.1%})")
            print(f"   📊 Significant: {result['significant']}")
            
            if result['significant']:
                qg_effects.append(grb_name)
    
    # Analisi statistica popolazione
    print(f"\n📊 POPULATION ANALYSIS:")
    print(f"   Total GRBs: {len(results)}")
    print(f"   Significant: {len(qg_effects)}")
    print(f"   Success Rate: {len(qg_effects)/len(results):.1%}")
    
    # Salva risultati (senza figure)
    save_quick_results(results, qg_effects)
    
    print("\n" + "=" * 50)
    print("✅ QUICK FERMI GRB ANALYSIS COMPLETE!")
    print("📊 Check generated files for results")
    print("=" * 50)

def save_quick_results(results, qg_effects):
    """
    Salva risultati rapidi
    """
    print("💾 Saving quick analysis results...")
    
    # Salva risultati JSON
    results_data = {
        'analysis_date': datetime.now().isoformat(),
        'total_grbs': len(results),
        'significant_grbs': len(qg_effects),
        'success_rate': len(qg_effects) / len(results),
        'grb_results': results
    }
    
    with open('quick_fermi_grb_results.json', 'w') as f:
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
            'Significant': result['significant']
        })
    
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_csv('quick_fermi_grb_summary.csv', index=False)
    
    print("✅ Results saved: quick_fermi_grb_results.json, quick_fermi_grb_summary.csv")

if __name__ == "__main__":
    quick_grb_analysis()
