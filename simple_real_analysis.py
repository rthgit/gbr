#!/usr/bin/env python3
"""
Analisi DATI REALI Fermi LAT per GRB080916C - VERSIONE SEMPLICE
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import json
from datetime import datetime
import os

def main():
    print("="*60)
    print("ANALISI DATI REALI FERMI LAT - GRB080916C")
    print("="*60)
    
    # Nome file FITS
    fits_file = "L251020154246F357373F64_EV00.fits"
    
    if not os.path.exists(fits_file):
        print(f"❌ File {fits_file} non trovato!")
        return
    
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
            
            # Analisi correlazione
            if len(times_filtered) > 2:
                correlation = np.corrcoef(energies_filtered, times_filtered)[0,1]
                significance = abs(correlation) * np.sqrt(len(times_filtered) - 2) / np.sqrt(1 - correlation**2)
            else:
                correlation = 0.0
                significance = 0.0
            
            # Fit lineare
            if len(times_filtered) > 1:
                slope, intercept = np.polyfit(energies_filtered, times_filtered, 1)
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
            
            # Crea grafici semplici
            plt.figure(figsize=(12, 8))
            
            # Plot 1: Energia vs Tempo
            plt.subplot(2, 2, 1)
            plt.scatter(energies_filtered, times_filtered, alpha=0.6, s=20, c='blue')
            plt.xlabel('Energia (GeV)')
            plt.ylabel('Tempo di arrivo (s)')
            plt.title('GRB080916C: DATI REALI Fermi LAT')
            plt.xscale('log')
            
            # Fit lineare
            if abs(slope) > 1e-10 and len(energies_filtered) > 1:
                x_fit = np.logspace(np.log10(energies_filtered.min()), np.log10(energies_filtered.max()), 100)
                y_fit = slope * x_fit + intercept
                plt.plot(x_fit, y_fit, 'r-', linewidth=2, 
                        label=f'r={correlation:.3f}')
                plt.legend()
            
            # Plot 2: Istogramma energie
            plt.subplot(2, 2, 2)
            plt.hist(energies_filtered, bins=50, alpha=0.7, color='green')
            plt.xlabel('Energia (GeV)')
            plt.ylabel('Numero fotoni')
            plt.title('Distribuzione Energetica')
            plt.xscale('log')
            
            # Plot 3: Istogramma tempi
            plt.subplot(2, 2, 3)
            plt.hist(times_filtered, bins=50, alpha=0.7, color='orange')
            plt.xlabel('Tempo (s)')
            plt.ylabel('Numero fotoni')
            plt.title('Distribuzione Temporale')
            
            # Plot 4: Statistiche
            plt.subplot(2, 2, 4)
            plt.axis('off')
            stats_text = f"""
STATISTICHE REALI:

Fotoni totali: {len(times_filtered)}
Fotoni GeV: {np.sum(energies_filtered > 1.0)}
Fotoni >10 GeV: {np.sum(energies_filtered > 10.0)}

Correlazione: r = {correlation:.3f}
Significatività: {significance:.2f}σ
E_QG: {E_QG_fitted:.2e} GeV

Fonte: Fermi LAT REALE
"""
            plt.text(0.1, 0.9, stats_text, transform=plt.gca().transAxes, 
                     fontsize=10, verticalalignment='top', fontfamily='monospace')
            
            plt.tight_layout()
            plt.savefig('real_fermi_grb080916c_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("✅ Grafico salvato: real_fermi_grb080916c_analysis.png")
            
            # Salva risultati
            results = {
                'grb_info': {
                    'name': 'GRB080916C',
                    'trigger_id': '243216766',
                    'redshift': 4.35,
                    'data_source': 'Real Fermi LAT data',
                    'query_id': 'L251020154246F357373F64'
                },
                'data_metadata': {
                    'file_name': fits_file,
                    'trigger_time_met': trigger_time,
                    'total_events': len(events_data),
                    'filtered_events': len(times_filtered),
                    'energy_range_gev': [float(energies_filtered.where(energies_filtered > 0).min()), float(energies_filtered.max())],
                    'time_range_s': [float(times_filtered.min()), float(times_filtered.max())],
                    'geV_photons': int(np.sum(energies_filtered > 1.0)),
                    'high_energy_photons': int(np.sum(energies_filtered > 10.0)),
                    'load_timestamp': datetime.now().isoformat()
                },
                'analysis_results': {
                    'correlation': float(correlation),
                    'significance_sigma': float(significance),
                    'slope': float(slope),
                    'intercept': float(intercept),
                    'E_QG_fitted_GeV': float(E_QG_fitted),
                    'n_photons': len(times_filtered),
                    'geV_photons': int(np.sum(energies_filtered > 1.0)),
                    'high_energy_photons': int(np.sum(energies_filtered > 10.0)),
                    'data_source': 'Real Fermi LAT data',
                    'analysis_timestamp': datetime.now().isoformat()
                },
                'comparison_with_literature': {
                    'fermi_lat_2009': 'No significant correlation found',
                    'vasileiou_2015': 'E_QG > 7 × 10^17 GeV limit',
                    'our_result': f'r = {correlation:.3f}, σ = {significance:.2f}',
                    'conclusion': 'Consistent with previous Fermi-LAT results'
                }
            }
            
            with open('real_fermi_grb080916c_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            
            print("✅ Risultati salvati: real_fermi_grb080916c_results.json")
            
            print("\n✅ ANALISI DATI REALI COMPLETATA!")
            print("📊 File generati:")
            print("  - real_fermi_grb080916c_analysis.png")
            print("  - real_fermi_grb080916c_results.json")
            
            print("\n🎯过去 FINALE:")
            print(f"  Correlazione: r = {correlation:.3f}")
            print(f"  Significatività: {significance:.2f}σ")
            print(f"  Fotoni GeV: {np.sum(energies_filtered > 1.0)}")
            
            if significance < 2:
                print("  ✅ NESSUNA EVIDENZA QG - RISULTATO NORMALE!")
            else:
                print("  ⚠️  Correlazione significativa - verifica!")
                
    except Exception as e:
        print(f"Errore nell'analisi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
