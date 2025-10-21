#!/usr/bin/env python3
"""
Caricamento e analisi dati FITS reali da Fermi LAT
Per GRB080916C
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
import json
from datetime import datetime

def load_real_fermi_data(fits_file):
    """
    Carica dati FITS reali da Fermi LAT
    
    Parameters:
    -----------
    fits_file : str
        Path al file FITS di Fermi LAT
        
    Returns:
    --------
    dict : Dizionario con dati e metadati
    """
    print(f"Caricando dati Fermi LAT da: {fits_file}")
    
    try:
        # Apri file FITS
        with fits.open(fits_file) as hdul:
            print(f"HDUs disponibili: {[hdu.name for hdu in hdul]}")
            
            # Carica eventi
            events_hdu = hdul['EVENTS']
            events_data = events_hdu.data
            
            print(f"Numero totale eventi: {len(events_data)}")
            
            # Estrai colonne principali
            times = events_data['TIME']  # Tempi di arrivo (MET)
            energies = events_data['ENERGY']  # Energie in MeV
            event_classes = events_data['EVENT_CLASS']  # Classe eventi
            zenith_angles = events_data['ZENITH_ANGLE']  # Angoli zenit
            
            # Converti tempi relativi al trigger GRB080916C
            trigger_time = 243216766.614  # MET del trigger
            times_relative = times - trigger_time
            
            # Converti energie in GeV
            energies_gev = energies / 1000.0
            
            print(f"Range tempi: {times_relative.min():.1f} - {times_relative.max():.1f} s")
            print(f"Range energie: {energies_gev.min():.3f} - {energies_gev.max():.1f} GeV")
            
            # Applica filtri qualità (stesso di Fermi-LAT)
            quality_cuts = (
                (event_classes >= 128) &  # Transient class
                (zenith_angles < 90) &    # No Earth limb
                (energies_gev > 0.1) &    # > 100 MeV
                (times_relative >= 0) &   # Dopo trigger
                (times_relative <= 1200)  # Entro 20 minuti
            )
            
            # Applica filtri
            times_filtered = times_relative[quality_cuts]
            energies_filtered = energies_gev[quality_cuts]
            event_classes_filtered = event_classes[quality_cuts]
            zenith_filtered = zenith_angles[quality_cuts]
            
            print(f"Eventi dopo filtri qualità: {len(times_filtered)}")
            print(f"Fotoni > 1 GeV: {np.sum(energies_filtered > 1.0)}")
            print(f"Fotoni > 10 GeV: {np.sum(energies_filtered > 10.0)}")
            
            # Metadati
            metadata = {
                'file_name': fits_file,
                'trigger_time_met': trigger_time,
                'total_events': len(events_data),
                'filtered_events': len(times_filtered),
                'energy_range_gev': [energies_filtered.min(), energies_filtered.max()],
                'time_range_s': [times_filtered.min(), times_filtered.max()],
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
        print(f"Errore nel caricamento FITS: {e}")
        return None

def analyze_real_data(data):
    """
    Analizza dati reali per effetti QG
    """
    if data is None:
        print("Nessun dato da analizzare")
        return None
    
    times = data['times']
    energies = data['energies']
    
    print("\n" + "="*50)
    print("ANALISI DATI REALI GRB080916C")
    print("="*50)
    
    # Statistiche descrittive
    print(f"Fotoni analizzati: {len(times)}")
    print(f"Fotoni GeV: {np.sum(energies > 1.0)}")
    print(f"Energia massima: {energies.max():.2f} GeV")
    print(f"Durata osservazione: {times.max() - times.min():.1f} s")
    
    # Analisi correlazione
    correlation = np.corrcoef(energies, times)[0,1]
    significance = abs(correlation) * np.sqrt(len(times) - 2) / np.sqrt(1 - correlation**2)
    
    # Fit lineare
    slope, intercept = np.polyfit(energies, times, 1)
    
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
        print("✅ Risultato consistente con letteratura")
    elif significance < 3:
        print("⚠️  Correlazione debole, necessaria analisi approfondita")
    else:
        print("🚨 Correlazione significativa - verifica metodologia!")
    
    return results

def create_real_data_plot(data, results):
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
    plt.title('GRB080916C: Dati Reali Fermi LAT')
    plt.xscale('log')
    
    # Fit lineare
    if abs(results['slope']) > 1e-10:
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
    plt.scatter(energies[geV_mask], times[geV_mask], 
               c='red', alpha=0.8, s=30, label='GeV')
    plt.xlabel('Energia (GeV)')
    plt.ylabel('Tempo (s)')
    plt.title('Fotoni GeV (E > 1 GeV)')
    plt.xscale('log')
    plt.legend()
    
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
    STATISTICHE:
    
    Fotoni totali: {len(times)}
    Fotoni GeV: {np.sum(energies > 1.0)}
    Fotoni >10 GeV: {np.sum(energies > 10.0)}
    
    Correlazione: r = {results['correlation']:.3f}
    Significatività: {results['significance_sigma']:.2f}σ
    E_QG: {results['E_QG_fitted_GeV']:.2e} GeV
    
    Fonte: Fermi LAT
    """
    plt.text(0.1, 0.9, stats_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top', fontfamily='monospace')
    
    plt.tight_layout()
    plt.savefig('real_fermi_data_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafico salvato: real_fermi_data_analysis.png")

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
            'data_source': 'Real Fermi LAT data'
        },
        'data_metadata': data['metadata'],
        'analysis_results': results,
        'comparison_with_literature': {
            'fermi_lat_2009': 'No significant correlation found',
            'vasileiou_2015': 'E_QG > 7 × 10^17 GeV limit',
            'our_result': f'r = {results["correlation"]:.3f}, σ = {results["significance_sigma"]:.2f}'
        }
    }
    
    with open('real_fermi_analysis_results.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print("✅ Risultati salvati: real_fermi_analysis_results.json")

def main():
    """
    Funzione principale per analisi dati reali
    """
    print("="*60)
    print("ANALISI DATI REALI FERMI LAT - GRB080916C")
    print("="*60)
    
    # Nome file FITS (da scaricare)
    fits_file = "GRB080916C_LAT_events.fits"
    
    # Controlla se file esiste
    import os
    if not os.path.exists(fits_file):
        print(f"❌ File {fits_file} non trovato!")
        print("📋 Segui la guida in FERMI_REGISTRATION_GUIDE.md")
        print("📥 Scarica i dati da: https://fermi.gsfc.nasa.gov/cgi-bin/ssc/LAT/LATDataQuery.cgi")
        return
    
    # Carica dati
    data = load_real_fermi_data(fits_file)
    
    if data is None:
        print("❌ Errore nel caricamento dati")
        return
    
    # Analizza dati
    results = analyze_real_data(data)
    
    if results is None:
        print("❌ Errore nell'analisi")
        return
    
    # Crea grafici
    create_real_data_plot(data, results)
    
    # Salva risultati
    save_real_results(data, results)
    
    print("\n✅ ANALISI COMPLETATA!")
    print("📊 File generati:")
    print("  - real_fermi_data_analysis.png")
    print("  - real_fermi_analysis_results.json")

if __name__ == "__main__":
    main()
