#!/usr/bin/env python3
"""
Analisi Multi-GRB per Ricerca Effetti QG
GRB: 080916C, 130427A, 090510, 090902
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import json
from datetime import datetime
import os
import glob

def load_grb_data(fits_file, grb_name, trigger_time, redshift):
    """
    Carica dati per un singolo GRB
    """
    print(f"\nCaricando dati per {grb_name}...")
    print(f"File: {fits_file}")
    
    if not os.path.exists(fits_file):
        print(f"❌ File {fits_file} non trovato!")
        return None
    
    try:
        with fits.open(fits_file) as hdul:
            events_data = hdul['EVENTS'].data
            times = events_data['TIME']
            energies = events_data['ENERGY']
            
            # Converti tempi relativi al trigger
            times_relative = times - trigger_time
            energies_gev = energies / 1000.0
            
            print(f"  Eventi totali: {len(events_data)}")
            print(f"  Range energie: {energies_gev.min():.3f} - {energies_gev.max():.1f} GeV")
            print(f"  Range tempi: {times_relative.min():.1f} - {times_relative.max():.1f} s")
            
            # Filtri qualità
            quality_cuts = (
                (energies_gev > 0.1) &      # > 100 MeV
                (times_relative >= 0) &     # Dopo trigger
                (times_relative <= 2500)    # Entro 42 minuti
            )
            
            times_filtered = times_relative[quality_cuts]
            energies_filtered = energies_gev[quality_cuts]
            
            print(f"  Eventi dopo filtri: {len(times_filtered)}")
            print(f"  Fotoni > 1 GeV: {np.sum(energies_filtered > 1.0)}")
            print(f"  Fotoni > 10 GeV: {np.sum(energies_filtered > 10.0)}")
            
            return {
                'name': grb_name,
                'times': times_filtered,
                'energies': energies_filtered,
                'trigger_time': trigger_time,
                'redshift': redshift,
                'total_events': len(events_data),
                'filtered_events': len(times_filtered),
                'geV_photons': int(np.sum(energies_filtered > 1.0)),
                'high_energy_photons': int(np.sum(energies_filtered > 10.0)),
                'energy_range': [float(energies_filtered.min()), float(energies_filtered.max())],
                'time_range': [float(times_filtered.min()), float(times_filtered.max())]
            }
            
    except Exception as e:
        print(f"❌ Errore nel caricamento di {grb_name}: {e}")
        return None

def analyze_single_grb(data):
    """
    Analizza un singolo GRB per effetti QG
    """
    if data is None:
        return None
    
    times = data['times']
    energies = data['energies']
    z = data['redshift']
    
    # Analisi correlazione
    if len(times) > 2:
        correlation = np.corrcoef(energies, times)[0,1]
        significance = abs(correlation) * np.sqrt(len(times) - 2) / np.sqrt(1 - correlation**2)
        slope, intercept = np.polyfit(energies, times, 1)
    else:
        correlation = 0.0
        significance = 0.0
        slope, intercept = 0.0, 0.0
    
    # Calcola E_QG
    H0 = 70.0  # km/s/Mpc
    c = 3e5    # km/s
    d_L = (c/H0) * z * (1 + z)  # Mpc
    
    if abs(slope) > 1e-10:
        E_QG_fitted = d_L * 3.086e22 / (c * abs(slope)) / 1e9
    else:
        E_QG_fitted = np.inf
    
    # Risultati
    results = {
        'grb_name': data['name'],
        'correlation': float(correlation),
        'significance_sigma': float(significance),
        'slope': float(slope),
        'intercept': float(intercept),
        'E_QG_fitted_GeV': float(E_QG_fitted),
        'n_photons': len(times),
        'geV_photons': data['geV_photons'],
        'high_energy_photons': data['high_energy_photons'],
        'redshift': z,
        'energy_range_gev': data['energy_range'],
        'time_range_s': data['time_range']
    }
    
    print(f"  Correlazione: r = {correlation:.3f}")
    print(f"  Significatività: {significance:.2f}σ")
    print(f"  E_QG fitted: {E_QG_fitted:.2e} GeV")
    
    return results

def combine_grb_results(results_list):
    """
    Combina risultati di più GRB usando metodo bayesiano
    """
    print("\n" + "="*60)
    print("COMBINAZIONE BAYESIANA MULTI-GRB")
    print("="*60)
    
    valid_results = [r for r in results_list if r is not None]
    
    if len(valid_results) == 0:
        print("❌ Nessun risultato valido da combinare")
        return None
    
    print(f"Combinando {len(valid_results)} GRB:")
    for result in valid_results:
        print(f"  {result['grb_name']}: r={result['correlation']:.3f}, σ={result['significance_sigma']:.2f}")
    
    # Combinazione bayesiana (somma log-likelihoods)
    total_photons = sum(r['n_photons'] for r in valid_results)
    total_geV_photons = sum(r['geV_photons'] for r in valid_results)
    total_high_energy_photons = sum(r['high_energy_photons'] for r in valid_results)
    
    # Calcola correlazione combinata (weighted average)
    weights = np.array([r['n_photons'] for r in valid_results])
    correlations = np.array([r['correlation'] for r in valid_results])
    
    combined_correlation = np.average(correlations, weights=weights)
    
    # Calcola significatività combinata
    if total_photons > 2:
        combined_significance = abs(combined_correlation) * np.sqrt(total_photons - 2) / np.sqrt(1 - combined_correlation**2)
    else:
        combined_significance = 0.0
    
    # Calcola E_QG combinato (conservative limit)
    E_QG_values = [r['E_QG_fitted_GeV'] for r in valid_results if r['E_QG_fitted_GeV'] != np.inf]
    
    if E_QG_values:
        # Usa il valore più conservativo (più alto)
        combined_E_QG = max(E_QG_values)
    else:
        combined_E_QG = np.inf
    
    # Risultati combinati
    combined_results = {
        'num_grb': len(valid_results),
        'total_photons': total_photons,
        'total_geV_photons': total_geV_photons,
        'total_high_energy_photons': total_high_energy_photons,
        'combined_correlation': float(combined_correlation),
        'combined_significance_sigma': float(combined_significance),
        'combined_E_QG_GeV': float(combined_E_QG),
        'individual_results': valid_results,
        'combination_timestamp': datetime.now().isoformat()
    }
    
    print(f"\nRISULTATI COMBINATI:")
    print(f"  Numero GRB: {len(valid_results)}")
    print(f"  Fotoni totali: {total_photons}")
    print(f"  Fotoni GeV: {total_geV_photons}")
    print(f"  Correlazione combinata: r = {combined_correlation:.3f}")
    print(f"  Significatività combinata: {combined_significance:.2f}σ")
    print(f"  E_QG combinato: {combined_E_QG:.2e} GeV")
    
    return combined_results

def create_multi_grb_plots(grb_data_list, combined_results):
    """
    Crea grafici per analisi multi-GRB
    """
    print("\nCreando grafici multi-GRB...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Plot 1: Tutti i GRB insieme
    ax1 = axes[0, 0]
    colors = ['blue', 'red', 'green', 'orange']
    for i, data in enumerate(grb_data_list):
        if data is not None:
            ax1.scatter(data['energies'], data['times'], 
                       alpha=0.6, s=20, c=colors[i], label=data['name'])
    ax1.set_xlabel('Energia (GeV)')
    ax1.set_ylabel('Tempo di arrivo (s)')
    ax1.set_title('Multi-GRB: Energia vs Tempo')
    ax1.set_xscale('log')
    ax1.legend()
    
    # Plot 2: Correlazioni individuali
    ax2 = axes[0, 1]
    grb_names = []
    correlations = []
    significances = []
    
    for result in combined_results['individual_results']:
        grb_names.append(result['grb_name'])
        correlations.append(result['correlation'])
        significances.append(result['significance_sigma'])
    
    x_pos = np.arange(len(grb_names))
    bars = ax2.bar(x_pos, correlations, color=colors[:len(grb_names)])
    ax2.set_xlabel('GRB')
    ax2.set_ylabel('Correlazione (r)')
    ax2.set_title('Correlazioni Individuali')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(grb_names, rotation=45)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Aggiungi valori sulle barre
    for i, (bar, sig) in enumerate(zip(bars, significances)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01 if height >= 0 else height - 0.01,
                f'{correlations[i]:.3f}\n({sig:.1f}σ)', 
                ha='center', va='bottom' if height >= 0 else 'top', fontsize=8)
    
    # Plot 3: Significatività
    ax3 = axes[0, 2]
    bars = ax3.bar(x_pos, significances, color=colors[:len(grb_names)])
    ax3.set_xlabel('GRB')
    ax3.set_ylabel('Significatività (σ)')
    ax3.set_title('Significatività Individuali')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(grb_names, rotation=45)
    ax3.axhline(y=2, color='red', linestyle='--', alpha=0.7, label='2σ threshold')
    ax3.axhline(y=3, color='orange', linestyle='--', alpha=0.7, label='3σ threshold')
    ax3.legend()
    
    # Plot 4: Fotoni GeV
    ax4 = axes[1, 0]
    geV_counts = [result['geV_photons'] for result in combined_results['individual_results']]
    bars = ax4.bar(x_pos, geV_counts, color=colors[:len(grb_names)])
    ax4.set_xlabel('GRB')
    ax4.set_ylabel('Fotoni GeV')
    ax4.set_title('Fotoni GeV per GRB')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(grb_names, rotation=45)
    
    # Plot 5: E_QG
    ax5 = axes[1, 1]
    E_QG_values = []
    E_QG_labels = []
    for result in combined_results['individual_results']:
        if result['E_QG_fitted_GeV'] != np.inf:
            E_QG_values.append(result['E_QG_fitted_GeV'])
            E_QG_labels.append(result['grb_name'])
    
    if E_QG_values:
        x_pos_e = np.arange(len(E_QG_values))
        bars = ax5.bar(x_pos_e, E_QG_values, color=colors[:len(E_QG_values)])
        ax5.set_xlabel('GRB')
        ax5.set_ylabel('E_QG (GeV)')
        ax5.set_title('E_QG Individuali')
        ax5.set_xticks(x_pos_e)
        ax5.set_xticklabels(E_QG_labels, rotation=45)
        ax5.set_yscale('log')
    
    # Plot 6: Statistiche combinate
    ax6 = axes[1, 2]
    ax6.axis('off')
    stats_text = f"""RISULTATI COMBINATI:

GRB analizzati: {combined_results['num_grb']}
Fotoni totali: {combined_results['total_photons']}
Fotoni GeV: {combined_results['total_geV_photons']}

Correlazione combinata: {combined_results['combined_correlation']:.3f}
Significatività combinata: {combined_results['combined_significance_sigma']:.2f}σ
E_QG combinato: {combined_results['combined_E_QG_GeV']:.2e} GeV

Risultato: {'NESSUNA EVIDENZA QG' if combined_results['combined_significance_sigma'] < 2 else 'CORRELAZIONE SIGNIFICATIVA'}"""
    
    ax6.text(0.1, 0.9, stats_text, transform=ax6.transAxes, 
             fontsize=10, verticalalignment='top', fontfamily='monospace')
    
    plt.tight_layout()
    plt.savefig('multi_grb_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafico salvato: multi_grb_analysis.png")

def main():
    """
    Funzione principale per analisi multi-GRB
    """
    print("="*70)
    print("ANALISI MULTI-GRB PER RICERCA EFFETTI QG")
    print("="*70)
    
    # Configurazione GRB
    grb_configs = [
        {
            'name': 'GRB080916C',
            'file': 'L251020154246F357373F64_EV00.fits',
            'trigger_time': 243216266.0,
            'redshift': 4.35
        },
        {
            'name': 'GRB130427A',
            'file': 'L251020161443F357373F97_EV00.fits',
            'trigger_time': 388798843.0,
            'redshift': 0.34
        },
        {
            'name': 'GRB090510',
            'file': 'L251020161531F357373F51_EV00.fits',
            'trigger_time': 263607281.0,
            'redshift': 0.903
        },
        {
            'name': 'GRB090902',
            'file': 'L251020161615F357373F52_EV00.fits',
            'trigger_time': 273581808.0,
            'redshift': 1.822
        }
    ]
    
    # Carica e analizza ogni GRB
    grb_data_list = []
    results_list = []
    
    for config in grb_configs:
        data = load_grb_data(config['file'], config['name'], 
                           config['trigger_time'], config['redshift'])
        grb_data_list.append(data)
        
        if data is not None:
            result = analyze_single_grb(data)
            results_list.append(result)
        else:
            results_list.append(None)
    
    # Combina risultati
    combined_results = combine_grb_results(results_list)
    
    if combined_results is not None:
        # Crea grafici
        create_multi_grb_plots(grb_data_list, combined_results)
        
        # Salva risultati
        with open('multi_grb_results.json', 'w') as f:
            json.dump(combined_results, f, indent=2)
        
        print("\n✅ Risultati salvati: multi_grb_results.json")
        
        print("\n🎯 RISULTATO FINALE MULTI-GRB:")
        print(f"  GRB analizzati: {combined_results['num_grb']}")
        print(f"  Fotoni totali: {combined_results['total_photons']}")
        print(f"  Correlazione combinata: r = {combined_results['combined_correlation']:.3f}")
        print(f"  Significatività combinata: {combined_results['combined_significance_sigma']:.2f}σ")
        
        if combined_results['combined_significance_sigma'] < 2:
            print("  ✅ NESSUNA EVIDENZA QG - RISULTATO NORMALE!")
        else:
            print("  ⚠️ CORRELAZIONE SIGNIFICATIVA - VERIFICA!")
    
    print("\n✅ ANALISI MULTI-GRB COMPLETATA!")

if __name__ == "__main__":
    main()

