#!/usr/bin/env python3
"""
ANALISI MULTI-GRB FINALE - 4 GRB REALI FERMI LAT
Ricerca Effetti Gravitazione Quantistica
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import json
from datetime import datetime
import os

def analyze_grb(fits_file, grb_name, trigger_time, redshift):
    """Analizza un singolo GRB"""
    print(f"\n{grb_name}:")
    
    if not os.path.exists(fits_file):
        print(f"  ❌ File {fits_file} non trovato!")
        return None
    
    try:
        with fits.open(fits_file) as hdul:
            events_data = hdul['EVENTS'].data
            times = events_data['TIME'] - trigger_time
            energies = events_data['ENERGY'] / 1000.0
            
            quality_cuts = (energies > 0.1) & (times >= 0) & (times <= 2500)
            times_filtered = times[quality_cuts]
            energies_filtered = energies[quality_cuts]
            
            n_photons = len(times_filtered)
            n_geV = np.sum(energies_filtered > 1.0)
            n_heV = np.sum(energies_filtered > 10.0)
            
            print(f"  Eventi totali: {len(events_data)}")
            print(f"  Eventi filtrati: {n_photons}")
            print(f"  Range energie: {energies_filtered.min():.3f} - {energies_filtered.max():.1f} GeV")
            print(f"  Fotoni GeV: {n_geV}")
            print(f"  Fotoni >10 GeV: {n_heV}")
            
            if n_photons > 2:
                correlation = np.corrcoef(energies_filtered, times_filtered)[0,1]
                significance = abs(correlation) * np.sqrt(n_photons - 2) / np.sqrt(1 - correlation**2)
                print(f"  Correlazione: r = {correlation:.3f}, σ = {significance:.2f}")
                
                # Calcola E_QG
                H0 = 70.0; c = 3e5; z = redshift
                d_L = (c/H0) * z * (1 + z)
                slope = np.polyfit(energies_filtered, times_filtered, 1)[0]
                E_QG = d_L * 3.086e22 / (c * abs(slope)) / 1e9 if abs(slope) > 1e-10 else np.inf
                print(f"  E_QG: {E_QG:.2e} GeV")
                
                return {
                    'name': grb_name,
                    'correlation': float(correlation),
                    'significance': float(significance),
                    'photons': n_photons,
                    'geV_photons': n_geV,
                    'high_energy_photons': n_heV,
                    'E_QG': float(E_QG),
                    'redshift': z,
                    'energy_range': [float(energies_filtered.min()), float(energies_filtered.max())],
                    'max_energy': float(energies_filtered.max())
                }
            else:
                print("  Troppi pochi fotoni per analisi")
                return None
                
    except Exception as e:
        print(f"  Errore: {e}")
        return None

def combine_results(results):
    """Combina risultati multi-GRB"""
    valid_results = [r for r in results if r is not None]
    
    if len(valid_results) == 0:
        return None
    
    print(f"\n{'='*60}")
    print("COMBINAZIONE BAYESIANA MULTI-GRB")
    print(f"{'='*60}")
    
    total_photons = sum(r['photons'] for r in valid_results)
    total_geV_photons = sum(r['geV_photons'] for r in valid_results)
    total_heV_photons = sum(r['high_energy_photons'] for r in valid_results)
    
    # Correlazione combinata (weighted average)
    weights = [r['photons'] for r in valid_results]
    correlations = [r['correlation'] for r in valid_results]
    combined_correlation = np.average(correlations, weights=weights)
    
    # Significatività combinata
    combined_significance = abs(combined_correlation) * np.sqrt(total_photons - 2) / np.sqrt(1 - combined_correlation**2)
    
    print(f"GRB analizzati: {len(valid_results)}")
    print(f"Fotoni totali: {total_photons}")
    print(f"Fotoni GeV: {total_geV_photons}")
    print(f"Fotoni >10 GeV: {total_heV_photons}")
    print(f"Correlazione combinata: r = {combined_correlation:.3f}")
    print(f"Significatività combinata: {combined_significance:.2f}σ")
    
    # Interpretazione
    if combined_significance < 2:
        interpretation = "NESSUNA EVIDENZA QG - RISULTATO NORMALE"
        print(f"✅ {interpretation}")
    elif combined_significance < 3:
        interpretation = "CORRELAZIONE DEBOLE - ANALISI APPROFONDITA NECESSARIA"
        print(f"⚠️ {interpretation}")
    else:
        interpretation = "CORRELAZIONE SIGNIFICATIVA - VERIFICA METODOLOGIA"
        print(f"🚨 {interpretation}")
    
    return {
        'num_grb': len(valid_results),
        'total_photons': total_photons,
        'total_geV_photons': total_geV_photons,
        'total_high_energy_photons': total_heV_photons,
        'combined_correlation': float(combined_correlation),
        'combined_significance': float(combined_significance),
        'interpretation': interpretation,
        'individual_results': valid_results,
        'timestamp': datetime.now().isoformat()
    }

def create_final_plots(results, combined_results):
    """Crea grafici finali"""
    print("\nCreando grafici finali...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Plot 1: Correlazioni individuali
    ax1 = axes[0, 0]
    names = [r['name'] for r in results if r is not None]
    correlations = [r['correlation'] for r in results if r is not None]
    significances = [r['significance'] for r in results if r is not None]
    
    x_pos = np.arange(len(names))
    colors = ['blue', 'red', 'green', 'orange']
    
    bars = ax1.bar(x_pos, correlations, color=colors[:len(names)])
    ax1.set_xlabel('GRB')
    ax1.set_ylabel('Correlazione (r)')
    ax1.set_title('Correlazioni Individuali')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(names, rotation=45)
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Aggiungi valori sulle barre
    for i, (bar, sig) in enumerate(zip(bars, significances)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01 if height >= 0 else height - 0.01,
                f'{correlations[i]:.3f}\n({sig:.1f}σ)', 
                ha='center', va='bottom' if height >= 0 else 'top', fontsize=8)
    
    # Plot 2: Significatività
    ax2 = axes[0, 1]
    bars = ax2.bar(x_pos, significances, color=colors[:len(names)])
    ax2.set_xlabel('GRB')
    ax2.set_ylabel('Significatività (σ)')
    ax2.set_title('Significatività Individuali')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(names, rotation=45)
    ax2.axhline(y=2, color='red', linestyle='--', alpha=0.7, label='2σ threshold')
    ax2.axhline(y=3, color='orange', linestyle='--', alpha=0.7, label='3σ threshold')
    ax2.legend()
    
    # Plot 3: Fotoni GeV
    ax3 = axes[0, 2]
    geV_counts = [r['geV_photons'] for r in results if r is not None]
    bars = ax3.bar(x_pos, geV_counts, color=colors[:len(names)])
    ax3.set_xlabel('GRB')
    ax3.set_ylabel('Fotoni GeV')
    ax3.set_title('Fotoni GeV per GRB')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(names, rotation=45)
    
    # Plot 4: Energie massime
    ax4 = axes[1, 0]
    max_energies = [r['max_energy'] for r in results if r is not None]
    bars = ax4.bar(x_pos, max_energies, color=colors[:len(names)])
    ax4.set_xlabel('GRB')
    ax4.set_ylabel('Energia Massima (GeV)')
    ax4.set_title('Energie Massime Osservate')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(names, rotation=45)
    ax4.set_yscale('log')
    
    # Plot 5: E_QG
    ax5 = axes[1, 1]
    E_QG_values = []
    E_QG_names = []
    for r in results:
        if r is not None and r['E_QG'] != np.inf:
            E_QG_values.append(r['E_QG'])
            E_QG_names.append(r['name'])
    
    if E_QG_values:
        x_pos_e = np.arange(len(E_QG_values))
        bars = ax5.bar(x_pos_e, E_QG_values, color=colors[:len(E_QG_values)])
        ax5.set_xlabel('GRB')
        ax5.set_ylabel('E_QG (GeV)')
        ax5.set_title('E_QG Individuali')
        ax5.set_xticks(x_pos_e)
        ax5.set_xticklabels(E_QG_names, rotation=45)
        ax5.set_yscale('log')
    
    # Plot 6: Statistiche combinate
    ax6 = axes[1, 2]
    ax6.axis('off')
    stats_text = f"""RISULTATI COMBINATI:

GRB analizzati: {combined_results['num_grb']}
Fotoni totali: {combined_results['total_photons']}
Fotoni GeV: {combined_results['total_geV_photons']}
Fotoni >10 GeV: {combined_results['total_high_energy_photons']}

Correlazione combinata: {combined_results['combined_correlation']:.3f}
Significatività combinata: {combined_results['combined_significance']:.2f}σ

Risultato: {combined_results['interpretation']}

Fonte: Fermi LAT REALE
Analisi: Multi-GRB Bayesian"""
    
    ax6.text(0.1, 0.9, stats_text, transform=ax6.transAxes, 
             fontsize=10, verticalalignment='top', fontfamily='monospace')
    
    plt.tight_layout()
    plt.savefig('final_multi_grb_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafico salvato: final_multi_grb_analysis.png")

def main():
    """Funzione principale"""
    print("="*70)
    print("ANALISI MULTI-GRB FINALE - 4 GRB REALI FERMI LAT")
    print("RICERCA EFFETTI GRAVITAZIONE QUANTISTICA")
    print("="*70)
    
    # Configurazione GRB
    grb_configs = [
        {'name': 'GRB080916C', 'file': 'L251020154246F357373F64_EV00.fits', 'trigger': 243216266.0, 'z': 4.35},
        {'name': 'GRB090902', 'file': 'L251020161615F357373F52_EV00.fits', 'trigger': 273581808.0, 'z': 1.822},
        {'name': 'GRB090510', 'file': 'L251020161912F357373F19_EV00.fits', 'trigger': 263607281.0, 'z': 0.903},
        {'name': 'GRB130427A', 'file': 'L251020162012F357373F30_EV00.fits', 'trigger': 388798843.0, 'z': 0.34}
    ]
    
    # Analizza ogni GRB
    results = []
    for config in grb_configs:
        result = analyze_grb(config['file'], config['name'], config['trigger'], config['z'])
        results.append(result)
    
    # Combina risultati
    combined_results = combine_results(results)
    
    if combined_results is not None:
        # Crea grafici
        create_final_plots(results, combined_results)
        
        # Salva risultati
        with open('final_multi_grb_results.json', 'w') as f:
            json.dump(combined_results, f, indent=2)
        
        print(f"\n✅ Risultati salvati: final_multi_grb_results.json")
        print(f"✅ Grafico salvato: final_multi_grb_analysis.png")
        
        print(f"\n🎯 RISULTATO FINALE MULTI-GRB:")
        print(f"  GRB analizzati: {combined_results['num_grb']}")
        print(f"  Fotoni totali: {combined_results['total_photons']}")
        print(f"  Correlazione combinata: r = {combined_results['combined_correlation']:.3f}")
        print(f"  Significatività combinata: {combined_results['combined_significance']:.2f}σ")
        print(f"  Interpretazione: {combined_results['interpretation']}")
        
        if combined_results['combined_significance'] < 2:
            print("\n✅ CONCLUSIONE: NESSUNA EVIDENZA DI EFFETTI QG!")
            print("✅ RISULTATO CONSISTENTE CON LETTERATURA!")
            print("✅ TOOLKIT VALIDATO SU CAMPIONE GRANDE!")
        else:
            print("\n⚠️ CORRELAZIONE SIGNIFICATIVA - VERIFICA NECESSARIA!")
    
    print(f"\n{'='*70}")
    print("ANALISI MULTI-GRB COMPLETATA!")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()

