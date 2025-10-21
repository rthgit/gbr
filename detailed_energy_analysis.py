#!/usr/bin/env python3
"""
FASE 1: ANALISI ENERGETICA DETTAGLIATA
=====================================

Analisi approfondita della correlazione energia-tempo con binning fine
per identificare breakpoints e modelli energetici nei dati GRB.

Autore: Christian Quintino De Luca (RTH Italia)
ORCID: 0009-0000-4198-5449
Email: info@rthitalia.com
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from astropy.io import fits
from datetime import datetime
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

# Configurazione matplotlib per headless
import matplotlib
matplotlib.use('Agg')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def convert_numpy(obj):
    """Converte tipi NumPy in tipi Python standard per JSON"""
    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                        np.int16, np.int32, np.int64, np.uint8,
                        np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def load_grb_data_detailed(filename, trigger_time, redshift):
    """Carica dati GRB con analisi dettagliata"""
    print(f"Caricando {filename}...")
    
    try:
        with fits.open(filename) as hdul:
            events_data = hdul['EVENTS'].data
            
            if events_data is None:
                print(f"❌ Nessun dato in {filename}")
                return None
            
            times = events_data['TIME'] - trigger_time
            energies = events_data['ENERGY'] / 1000.0  # Convert to GeV
            
            # Quality cuts - molto permissivi per GRB130427A
            if 'F357373F96' in filename:  # GRB130427A nuovo file
                quality_cuts = (energies > 0.01) & (times >= -1000) & (times <= 10000)
            else:
                quality_cuts = (energies > 0.1) & (times >= 0) & (times <= 2500)
            
            times_filtered = times[quality_cuts]
            energies_filtered = energies[quality_cuts]
            
            print(f"  Eventi totali: {len(events_data)}")
            print(f"  Eventi filtrati: {len(times_filtered)}")
            print(f"  Range energia: {energies_filtered.min():.3f} - {energies_filtered.max():.1f} GeV")
            print(f"  Fotoni >1 GeV: {np.sum(energies_filtered > 1.0)}")
            print(f"  Fotoni >10 GeV: {np.sum(energies_filtered > 10.0)}")
            
            return {
                'times': times_filtered,
                'energies': energies_filtered,
                'n_photons': len(times_filtered),
                'energy_range': (energies_filtered.min(), energies_filtered.max()),
                'redshift': redshift
            }
            
    except Exception as e:
        print(f"❌ Errore caricamento {filename}: {e}")
        return None

def create_energy_bins(energies, n_bins=15):
    """Crea bins energetici ottimali"""
    # Usa quantili per bins con statistiche simili
    percentiles = np.linspace(0, 100, n_bins + 1)
    bin_edges = np.percentile(energies, percentiles)
    
    # Assicura che i bins siano unici
    bin_edges = np.unique(bin_edges)
    
    return bin_edges

def analyze_energy_bands(data, n_bins=15):
    """Analizza correlazioni per banda energetica"""
    times = data['times']
    energies = data['energies']
    
    # Crea bins energetici
    bin_edges = create_energy_bins(energies, n_bins)
    
    results = []
    
    for i in range(len(bin_edges) - 1):
        # Seleziona fotoni in questo bin energetico
        energy_mask = (energies >= bin_edges[i]) & (energies < bin_edges[i + 1])
        
        if np.sum(energy_mask) < 10:  # Troppo pochi fotoni
            continue
            
        times_band = times[energy_mask]
        energies_band = energies[energy_mask]
        
        # Calcola correlazione
        if len(times_band) > 2:
            correlation = np.corrcoef(energies_band, times_band)[0, 1]
            
            # Significatività
            if not np.isnan(correlation) and abs(correlation) < 0.999:
                significance = abs(correlation) * np.sqrt(len(times_band) - 2) / np.sqrt(1 - correlation**2)
            else:
                significance = 0
            
            # Calcola tempo medio per questo bin
            time_mean = np.mean(times_band)
            energy_mean = np.mean(energies_band)
            
            results.append({
                'bin_index': i,
                'energy_min': bin_edges[i],
                'energy_max': bin_edges[i + 1],
                'energy_mean': energy_mean,
                'time_mean': time_mean,
                'n_photons': len(times_band),
                'correlation': correlation,
                'significance': significance
            })
    
    return results

def fit_energy_time_models(times, energies):
    """Fit diversi modelli energia-tempo"""
    models = {}
    
    # Modello 1: Lineare (QG standard)
    try:
        slope_linear, intercept_linear = np.polyfit(energies, times, 1)
        r_linear = np.corrcoef(energies, times)[0, 1]
        models['linear'] = {
            'slope': slope_linear,
            'intercept': intercept_linear,
            'correlation': r_linear,
            'type': 'QG Standard'
        }
    except:
        models['linear'] = None
    
    # Modello 2: Power-law (lag intrinseci)
    try:
        # Fit: t = t0 + a * E^b
        def power_law(E, t0, a, b):
            return t0 + a * np.power(E, b)
        
        # Valori iniziali
        p0 = [np.mean(times), 1.0, -1.0]
        popt, pcov = curve_fit(power_law, energies, times, p0=p0, maxfev=1000)
        
        t0, a, b = popt
        times_pred = power_law(energies, t0, a, b)
        r_power = np.corrcoef(times, times_pred)[0, 1]
        
        models['power_law'] = {
            't0': t0,
            'a': a,
            'b': b,
            'correlation': r_power,
            'type': 'Power-law Lag'
        }
    except:
        models['power_law'] = None
    
    # Modello 3: Broken power-law
    try:
        # Fit: t = t0 + a * E^b1 per E < E_break, t0 + a * E_break^(b1-b2) * E^b2 per E >= E_break
        def broken_power_law(E, t0, a, b1, b2, E_break):
            result = np.zeros_like(E)
            mask_low = E < E_break
            mask_high = E >= E_break
            
            result[mask_low] = t0 + a * np.power(E[mask_low], b1)
            result[mask_high] = t0 + a * np.power(E_break, b1 - b2) * np.power(E[mask_high], b2)
            
            return result
        
        # Valori iniziali
        E_break_init = np.median(energies)
        p0 = [np.mean(times), 1.0, -1.0, -0.5, E_break_init]
        popt, pcov = curve_fit(broken_power_law, energies, times, p0=p0, maxfev=2000)
        
        t0, a, b1, b2, E_break = popt
        times_pred = broken_power_law(energies, t0, a, b1, b2, E_break)
        r_broken = np.corrcoef(times, times_pred)[0, 1]
        
        models['broken_power_law'] = {
            't0': t0,
            'a': a,
            'b1': b1,
            'b2': b2,
            'E_break': E_break,
            'correlation': r_broken,
            'type': 'Broken Power-law'
        }
    except:
        models['broken_power_law'] = None
    
    return models

def identify_breakpoints(energy_band_results):
    """Identifica breakpoints nel comportamento energetico"""
    if len(energy_band_results) < 5:
        return None
    
    # Estrai dati
    energies = [r['energy_mean'] for r in energy_band_results]
    correlations = [r['correlation'] for r in energy_band_results]
    significances = [r['significance'] for r in energy_band_results]
    
    # Trova cambiamenti significativi nella correlazione
    breakpoints = []
    
    for i in range(2, len(correlations) - 2):
        # Confronta correlazioni prima e dopo questo punto
        before = np.mean(correlations[i-2:i])
        after = np.mean(correlations[i:i+2])
        
        # Se c'è un cambiamento significativo
        if abs(after - before) > 0.1 and significances[i] > 1.5:
            breakpoints.append({
                'energy': energies[i],
                'bin_index': i,
                'correlation_before': before,
                'correlation_after': after,
                'significance': significances[i]
            })
    
    return breakpoints

def create_detailed_plots(grb_name, data, energy_band_results, models, breakpoints):
    """Crea grafici dettagliati per l'analisi energetica"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'Analisi Energetica Dettagliata - {grb_name}', fontsize=16, fontweight='bold')
    
    times = data['times']
    energies = data['energies']
    
    # Plot 1: Scatter plot energia-tempo con bins
    ax1 = axes[0, 0]
    scatter = ax1.scatter(energies, times, alpha=0.6, s=20, c='blue', edgecolors='none')
    ax1.set_xlabel('Energia (GeV)')
    ax1.set_ylabel('Tempo relativo (s)')
    ax1.set_title('Distribuzione Fotoni')
    ax1.set_xscale('log')
    
    # Aggiungi bins energetici
    if energy_band_results:
        bin_edges = [r['energy_min'] for r in energy_band_results] + [energy_band_results[-1]['energy_max']]
        for edge in bin_edges:
            ax1.axvline(edge, color='red', linestyle='--', alpha=0.5)
    
    # Plot 2: Correlazione per banda energetica
    ax2 = axes[0, 1]
    if energy_band_results:
        bin_energies = [r['energy_mean'] for r in energy_band_results]
        correlations = [r['correlation'] for r in energy_band_results]
        significances = [r['significance'] for r in energy_band_results]
        
        # Colora per significatività
        colors = ['red' if s > 2 else 'orange' if s > 1 else 'green' for s in significances]
        
        ax2.scatter(bin_energies, correlations, c=colors, s=100, alpha=0.7)
        ax2.axhline(0, color='black', linestyle='-', alpha=0.5)
        ax2.set_xlabel('Energia media (GeV)')
        ax2.set_ylabel('Correlazione r')
        ax2.set_title('Correlazione per Banda Energetica')
        ax2.set_xscale('log')
        
        # Evidenzia breakpoints
        if breakpoints:
            for bp in breakpoints:
                ax2.axvline(bp['energy'], color='red', linestyle='--', alpha=0.8, linewidth=2)
                ax2.text(bp['energy'], 0.8, f'Break\n{bp["energy"]:.2f} GeV', 
                        rotation=90, ha='right', va='top', fontsize=8)
    
    # Plot 3: Significatività per banda
    ax3 = axes[0, 2]
    if energy_band_results:
        ax3.bar(range(len(significances)), significances, color=colors, alpha=0.7)
        ax3.axhline(2, color='red', linestyle='--', label='2σ')
        ax3.axhline(3, color='darkred', linestyle='--', label='3σ')
        ax3.set_xlabel('Banda Energetica')
        ax3.set_ylabel('Significatività (σ)')
        ax3.set_title('Significatività per Banda')
        ax3.legend()
        ax3.set_xticks(range(0, len(significances), max(1, len(significances)//5)))
    
    # Plot 4: Modelli fit
    ax4 = axes[1, 0]
    ax4.scatter(energies, times, alpha=0.3, s=10, c='gray', label='Dati')
    
    # Plot modelli
    if models['linear']:
        E_fit = np.logspace(np.log10(energies.min()), np.log10(energies.max()), 100)
        t_fit = models['linear']['slope'] * E_fit + models['linear']['intercept']
        ax4.plot(E_fit, t_fit, 'r-', linewidth=2, 
                label=f'Lineare (r={models["linear"]["correlation"]:.3f})')
    
    if models['power_law']:
        E_fit = np.logspace(np.log10(energies.min()), np.log10(energies.max()), 100)
        t_fit = models['power_law']['t0'] + models['power_law']['a'] * np.power(E_fit, models['power_law']['b'])
        ax4.plot(E_fit, t_fit, 'b-', linewidth=2,
                label=f'Power-law (r={models["power_law"]["correlation"]:.3f})')
    
    ax4.set_xlabel('Energia (GeV)')
    ax4.set_ylabel('Tempo relativo (s)')
    ax4.set_title('Modelli di Fit')
    ax4.set_xscale('log')
    ax4.legend()
    
    # Plot 5: Spettro energetico
    ax5 = axes[1, 1]
    hist, bin_edges = np.histogram(energies, bins=20)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    ax5.step(bin_centers, hist, where='mid', linewidth=2, color='green')
    ax5.set_xlabel('Energia (GeV)')
    ax5.set_ylabel('Numero fotoni')
    ax5.set_title('Spettro Energetico')
    ax5.set_xscale('log')
    ax5.set_yscale('log')
    
    # Plot 6: Distribuzione temporale
    ax6 = axes[1, 2]
    hist, bin_edges = np.histogram(times, bins=30)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    ax6.step(bin_centers, hist, where='mid', linewidth=2, color='purple')
    ax6.set_xlabel('Tempo relativo (s)')
    ax6.set_ylabel('Numero fotoni')
    ax6.set_title('Distribuzione Temporale')
    
    plt.tight_layout()
    plt.savefig(f'detailed_energy_analysis_{grb_name.lower()}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Grafici salvati: detailed_energy_analysis_{grb_name.lower()}.png")

def main():
    """Funzione principale per analisi energetica dettagliata"""
    
    print("="*70)
    print("FASE 1: ANALISI ENERGETICA DETTAGLIATA")
    print("Correlazione per banda energetica e identificazione breakpoints")
    print("="*70)
    
    # Configurazione GRB
    grb_configs = [
        {'name': 'GRB080916C', 'file': 'L251020154246F357373F64_EV00.fits', 'trigger': 243216266.0, 'z': 4.35},
        {'name': 'GRB090902', 'file': 'L251020161615F357373F52_EV00.fits', 'trigger': 273581808.0, 'z': 1.822},
        {'name': 'GRB090510', 'file': 'L251020161912F357373F19_EV00.fits', 'trigger': 263607281.0, 'z': 0.903},
        {'name': 'GRB130427A', 'file': 'L251020164901F357373F96_EV00.fits', 'trigger': 388798843.0, 'z': 0.34}
    ]
    
    all_results = []
    
    for config in grb_configs:
        print(f"\n🔬 ANALISI DETTAGLIATA: {config['name']}")
        print("-" * 50)
        
        # Carica dati
        data = load_grb_data_detailed(config['file'], config['trigger'], config['z'])
        
        if data is None or data['n_photons'] < 30:
            print(f"❌ Dati insufficienti per {config['name']}")
            continue
        
        # Analisi per banda energetica
        print(f"📊 Analisi per banda energetica...")
        energy_band_results = analyze_energy_bands(data, n_bins=15)
        
        # Identifica breakpoints
        print(f"🔍 Identificazione breakpoints...")
        breakpoints = identify_breakpoints(energy_band_results)
        
        # Fit modelli
        print(f"📈 Fit modelli energia-tempo...")
        models = fit_energy_time_models(data['times'], data['energies'])
        
        # Crea grafici
        print(f"📊 Creazione grafici...")
        create_detailed_plots(config['name'], data, energy_band_results, models, breakpoints)
        
        # Statistiche riassuntive
        total_correlation = np.corrcoef(data['energies'], data['times'])[0, 1]
        total_significance = abs(total_correlation) * np.sqrt(data['n_photons'] - 2) / np.sqrt(1 - total_correlation**2)
        
        # Salva risultati
        result = {
            'grb_name': config['name'],
            'n_photons': data['n_photons'],
            'energy_range': data['energy_range'],
            'redshift': config['z'],
            'total_correlation': float(total_correlation),
            'total_significance': float(total_significance),
            'energy_bands': len(energy_band_results),
            'breakpoints': len(breakpoints) if breakpoints else 0,
            'models_fit': {k: v is not None for k, v in models.items()},
            'energy_band_results': energy_band_results,
            'breakpoints_detail': breakpoints,
            'models_detail': models
        }
        
        all_results.append(result)
        
        # Stampa riassunto
        print(f"✅ RISULTATI {config['name']}:")
        print(f"  Fotoni: {data['n_photons']}")
        print(f"  Correlazione totale: {total_correlation:.3f} ({total_significance:.2f}σ)")
        print(f"  Bande energetiche: {len(energy_band_results)}")
        print(f"  Breakpoints: {len(breakpoints) if breakpoints else 0}")
        print(f"  Modelli fit: {sum(1 for v in models.values() if v is not None)}/3")
    
    # Salva risultati completi
    with open('detailed_energy_analysis_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=convert_numpy)
    
    print(f"\n🎯 RISULTATI FINALI FASE 1:")
    print(f"  GRB analizzati: {len(all_results)}")
    print(f"  Analisi per banda energetica completata")
    print(f"  Breakpoints identificati")
    print(f"  Modelli energetici fitati")
    print(f"  Grafici dettagliati generati")
    print(f"  Risultati salvati: detailed_energy_analysis_results.json")
    
    print("\n" + "="*70)
    print("FASE 1 COMPLETATA! Pronto per FASE 2!")
    print("="*70)

if __name__ == "__main__":
    main()
