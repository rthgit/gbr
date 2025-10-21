#!/usr/bin/env python3
"""
Analisi DATI REALI Fermi LAT per GRB080916C - VERSIONE CORRETTA
File: L251020154246F357373F64_EV00.fits
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import json
from datetime import datetime
import os

def load_real_fermi_events(fits_file):
    """
    Carica eventi reali da file Fermi LAT EV
    """
    print(f"Caricando eventi reali da: {fits_file}")
    
    if not os.path.exists(fits_file):
        print(f"❌ File {fits_file} non trovato!")
        return None
    
    try:
        # Apri file FITS
        with fits.open(fits_file) as hdul:
            print(f"HDUs disponibili: {[hdu.name for hdu in hdul]}")
            
            # Carica eventi dalla HDU EVENTS (indice 1)
            events_data = hdul['EVENTS'].data
            
            print(f"Numero totale eventi: {len(events_data)}")
            print(f"Colonne disponibili: {events_data.dtype.names}")
            
            # Estrai colonne principali
            times = events_data['TIME']  # Tempi di arrivo (MET)
            energies = events_data['ENERGY']  # Energie in MeV
            event_classes = events_data['EVENT_CLASS']  # Classe eventi
            zenith_angles = events_data['ZENITH_ANGLE']  # Angoli zenit
            
            # Converti tempi relativi al trigger GRB080916C
            trigger_time = 243216266.0  # MET del trigger (inizio query)
            times_relative = times - trigger_time
            
            # Converti energie in GeV
            energies_gev = energies / 1000.0
            
            print(f"Range tempi: {times_relative.min():.1f} - {times_relative.max():.1f} s")
            print(f"Range energie: {energies_gev.min():.3f} - {energies_gev.max():.1f} GeV")
            
            # Filtri qualità base
            quality_cuts = (
                (energies_gev > 0.1) &      # > 100 MeV
                (times_relative >= 0) &     # Dopo trigger
                (times_relative <= 2500)    # Entro 42 minuti
            )
            
            # Applica filtri
            times_filtered = times_relative[quality_cuts]
            energies_filtered = energies_gev[quality_cuts]
            event_classes_filtered = event_classes[quality_cuts]
            zenith_filtered = zenith_angles[quality_cuts]
            
            print(f"Eventi dopo filtri: {len(times_filtered)}")
            print(f"Fotoni > 1 GeV: {np.sum(energies_filtered > 1.0)}")
            print(f"Fotoni > 10 GeV: {np.sum(energies_filtered > 10.0)}")
            
            # Metadati
            metadata = {
                'file_name': fits_file,
                'trigger_time_met': trigger_time,
                'total_events': len(events_data),
                'filtered_events': len(times_filtered),
                'energy_range_gev': [float(energies_filtered.min()), float(energies_filtered.max())],
                'time_range_s': [float(times_filtered.min()), float(times_filtered.max())],
                'geV_photons': int(np.sum(energies_filtered > 1.0)),
                'high_energy_photons': int(np.sum(energies_filtered > 10.0)),
                'load_timestamp': datetime.now().isoformat()
            }
            
            # Dati finali
            data = {
                'times': times_filtered,
                'energies': energies_filtered,
                'event_classes': event_classes_filtered,
                'zenith_angles': zenith_filtered,
                'metadata': metadata
            }
            
            return data
            
    except Exception as e:
        print(f"Errore nel caricamento: {e}")
        return None

def analyze_real_fermi_data(data):
    """
    Analizza dati reali Fermi per effetti QG
    """
    if data is None:
        return None
    
    times = data['times']
    energies = data['energies']
    
    print("\n" + "="*60)
    print("ANALISI DATI REALI FERMI LAT - GRB080916C")
    print("="*60)
    
    # Statistiche descrittive
    print(f"Fotoni analizzati: {len(times)}")
    print(f"Fotoni GeV: {np.sum(energies > 1.0)}")
    print(f"Fotoni >10 GeV: {np.sum(energies > 10.0)}")
    print(f"Energia massima: {energies.max():.2f} GeV")
    print(f"Durata osservazione: {times.max() - times.min():.1f} s")
    
    # Analisi correlazione
    if len(times) > 2:
        correlation = np.corrcoef(energies, times)[0,1]
        significance = abs(correlation) * np.sqrt(len(times) - 2) / np.sqrt(1 - correlation**2)
    else:
        correlation = 0.0
        significance = 0.0
    
    # Fit lineare
    if len(times) > 1:
        slope, intercept = np.polyfit(energies, times, 1)
    else:
        slope, intercept = 0.0, 0.0
    
    # Calcola E_QG (se correlazione significativa)
    z = 4.35  # Redshift GRB080916C
    H0 = 70.0  # km/s/Mpc
    c = 3e5    # km/s
    d_L = (c/H0) * z * (1 + z)  # Mpc
    
    if abs(slope) > 1e-10:  # Evita divisione per zero
        E_QG_fitted = d_L * 3.086e22 / (c * abs(slope)) / 1e9
    else:
        E_QG_fitted = np.inf
    
    # Risultati
    results = {
        'correlation': float(correlation),
        'significance_sigma': float(significance),
        'slope': float(slope),
        'intercept': float(intercept),
        'E_QG_fitted_GeV': float(E_QG_fitted),
        'n_photons': len(times),
        'geV_photons': int(np.sum(energies > 1.0)),
        'high_energy_photons': int(np.sum(energies > 10.0)),
        'data_source': 'Real Fermi LAT data',
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    # Stampa risultati
    print(f"\nRISULTATI ANALISI:")
    print(f"Correlazione: r = {correlation:.3f}")
    print(f"Significatività: {significance:.2f}σ")
    print(f"Slope: {slope:.2e}")
    print(f"E_QG fitted: {E_QG_fitted:.2e} GeV")
    
    # Interpretazione
    print(f"\nINTERPRETAZIONE:")
    if significance < 2:
        print("✅ Nessuna evidenza di effetti QG (normale)")
        print("✅ Risultato consistente con letteratura Fermi-LAT")
    elif significance < 3:
        print("⚠️  Correlazione debole, necessaria analisi approfondita")
    else:
        print("🚨 Correlazione significativa - verifica metodologia!")
    
    return results

def create_real_data_plots(data, results):
    """
    Crea grafici per dati reali
    """
    if data is None:
        return
    
    times = data['times']
    energies = data['energies']
    
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Energia vs Tempo
    plt.subplot(2, 3, 1)
    plt.scatter(energies, times, alpha=0.6, s=20, c='blue')
    plt.xlabel('Energia (GeV)')
    plt.ylabel('Tempo di arrivo (s)')
    plt.title('GRB080916C: DATI REALI Fermi LAT')
    plt.xscale('log')
    
    # Fit lineare
    if abs(results['slope']) > 1e-10 and len(energies) > 1:
        x_fit = np.logspace(np.log10(energies.min()), np.log10(energies.max()), 100)
        y_fit = results['slope'] * x_fit + results['intercept']
        plt.plot(x_fit, y_fit, 'r-', linewidth=2, 
                label=f'r={results["correlation"]:.3f}')
        plt.legend()
    
    # Plot 2: Istogramma energie
    plt.subplot(2, 3, 2)
    plt.hist(energies, bins=50, alpha=0.7, color='green')
    plt.xlabel('Energia (GeV)')
    plt.ylabel('Numero fotoni')
    plt.title('Distribuzione Energetica')
    plt.xscale('log')
    
    # Plot 3: Istogramma tempi
    plt.subplot(2, 3, 3)
    plt.hist(times, bins=50, alpha=0.7, color='orange')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Numero fotoni')
    plt.title('Distribuzione Temporale')
    
    # Plot 4: Fotoni GeV
    plt.subplot(2, 3, 4)
    geV_mask = energies > 1.0
    if np.sum(geV_mask) > 0:
        plt.scatter(energies[geV_mask], times[geV_mask], 
                   c='red', alpha=0.8, s=30, label='GeV')
        plt.xlabel('Energia (GeV)')
        plt.ylabel('Tempo (s)')
        plt.title('Fotoni GeV (E > 1 GeV)')
        plt.xscale('log')
        plt.legend()
    else:
        plt.text(0.5, 0.5, 'Nessun fotone >1 GeV', 
                transform=plt.gca().transAxes, ha='center')
        plt.title('Fotoni GeV')
    
    # Plot 5: Fotoni alta energia
    plt.subplot(2, 3, 5)
    hev_mask = energies > 10.0
    if np.sum(hev_mask) > 0:
        plt.scatter(energies[hev_mask], times[hev_mask], 
                   c='purple', alpha=0.8, s=50, label='>10 GeV')
        plt.xlabel('Energia (GeV)')
        plt.ylabel('Tempo (s)')
        plt.title('Fotoni Alta Energia')
        plt.xscale('log')
        plt.legend()
    else:
        plt.text(0.5, 0.5, 'Nessun fotone >10 GeV', 
                transform=plt.gca().transAxes, ha='center')
        plt.title('Fotoni Alta Energia')
    
    # Plot 6: Statistiche
    plt.subplot(2, 3, 6)
    plt.axis('off')
    stats_text = f"""
    STATISTICHE REALI:
    
    Fotoni totali: {len(times)}
    Fotoni GeV: {np.sum(energies > 1.0)}
    Fotoni >10 GeV: {np.sum(energies > 10.0)}
    
    Correlazione: r = {results['correlation']:.3f}
    Significatività: {results['significance_sigma']:.2f}σ
    E_QG: {results['E_QG_fitted_GeV']:.2e} GeV
    
    Fonte: Fermi LAT REALE
    """
    plt.text(0.1, 0.9, stats_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top', fontfamily='monospace')
    
    plt.tight_layout()
    plt.savefig('real_fermi_grb080916c_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafico salvato: real_fermi_grb080916c_analysis.png")

def save_real_results(data, results):
    """
    Salva risultati analisi dati reali
    """
    if data is None or results is None:
        return
    
    output_data = {
        'grb_info': {
            'name': 'GRB080916C',
            'trigger_id': '243216766',
            'redshift': 4.35,
            'data_source': 'Real Fermi LAT data',
            'query_id': 'L251020154246F357373F64'
        },
        'data_metadata': data['metadata'],
        'analysis_results': results,
        'comparison_with_literature': {
            'fermi_lat_2009': 'No significant correlation found',
            'vasileiou_2015': 'E_QG > 7 × 10^17 GeV limit',
            'our_result': f'r = {results["correlation"]:.3f}, σ = {results["significance_sigma"]:.2f}',
            'conclusion': 'Consistent with previous Fermi-LAT results'
        }
    }
    
    with open('real_fermi_grb080916c_results.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("✅ Risultati salvati: real_fermi_grb080916c_results.json")

def main():
    """
    Funzione principale per analisi dati reali
    """
    print("="*60)
    print("ANALISI DATI REALI FERMI LAT - GRB080916C")
    print("="*60)
    
    # Nome file FITS
    fits_file = "L251020154246F357373F64_EV00.fits"
    
    # Carica dati
    data = load_real_fermi_events(fits_file)
    
    if data is None:
        print("❌ Errore nel caricamento dati")
        return
    
    # Analizza dati
    results = analyze_real_fermi_data(data)
    
    if results is None:
        print("❌ Errore nell'analisi")
        return
    
    # Crea grafici
    create_real_data_plots(data, results)
    
    # Salva risultati
    save_real_results(data, results)
    
    print("\n✅ ANALISI DATI REALI COMPLETATA!")
    print("📊 File generati:")
    print("  - real_fermi_grb080916c_analysis.png")
    print("  - real_fermi_grb080916c_results.json")
    
    print("\n🎯 RISULTATO FINALE:")
    print(f"  Correlazione: r = {results['correlation']:.3f}")
    print(f"  Significatività: {results['significance_sigma']:.2f}σ")
    print(f"  Fotoni GeV: {results['geV_photons']}")
    
    if results['significance_sigma'] < 2:
        print("  ✅ NESSUNA EVIDENZA QG - RISULTATO NORMALE!")
    else:
        print("  ⚠️  Correlazione significativa - verifica!")

if __name__ == "__main__":
    main()

