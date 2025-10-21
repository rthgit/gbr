#!/usr/bin/env python3
"""
ANALISI GRB221009A - BOAT (Brightest Of All Time)
==================================================

Analizza GRB221009A, il GRB più brillante mai osservato
con energia massima ~300 GeV

Autore: Christian Quintino De Luca (RTH Italia)
ORCID: 0009-0000-4198-5449
Email: info@rthitalia.com
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy import stats
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurazione matplotlib
plt.style.use('default')
plt.rcParams['figure.figsize'] = (20, 15)
plt.rcParams['font.size'] = 12

def convert_numpy(obj):
    """Converte tipi NumPy in tipi Python standard per JSON"""
    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                        np.int16, np.int32, np.int64, np.uint8,
                        np.uint16, np.int32, np.int64, np.uint8,
                        np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def load_grb221009a_data():
    """Carica dati GRB221009A dal file FITS"""
    
    print("🔍 Caricamento dati GRB221009A (BOAT)...")
    
    # Cerca file disponibili
    ph_files = [f for f in os.listdir('.') if 'L25102020315294ADC46894_PH00.fits' in f]
    
    if not ph_files:
        print("❌ File GRB221009A non trovato!")
        return None
    
    filename = ph_files[0]
    print(f"📁 Caricando: {filename}")
    
    try:
        with fits.open(filename) as hdul:
            print(f"📊 HDUs disponibili: {len(hdul)}")
            
            # Cerca HDU con dati eventi
            events_data = None
            for i, hdu in enumerate(hdul):
                print(f"  HDU {i}: {hdu.name} - {hdu.header.get('EXTNAME', 'No name')}")
                if hdu.data is not None:
                    print(f"    Data shape: {hdu.data.shape}")
                    print(f"    Data type: {hdu.data.dtype}")
                    if hasattr(hdu.data, 'names'):
                        print(f"    Columns: {hdu.data.names[:10]}...")  # Prime 10 colonne
                    
                    # Cerca colonne TIME e ENERGY
                    if hasattr(hdu.data, 'names') and 'TIME' in hdu.data.names and 'ENERGY' in hdu.data.names:
                        events_data = hdu.data
                        print(f"    ✅ Trovato HDU con dati eventi: {hdu.name}")
                        break
            
            if events_data is None:
                print("❌ Nessun HDU con dati eventi trovato!")
                return None
            
            # Estrai colonne principali
            times = events_data['TIME']
            energies = events_data['ENERGY']  # MeV
            
            print(f"📊 Eventi totali: {len(times)}")
            print(f"📊 Range tempo: {times.min():.1f} - {times.max():.1f}")
            print(f"📊 Range energia: {energies.min():.1f} - {energies.max():.1f} MeV")
            print(f"📊 Energia massima: {energies.max():.1f} MeV ({energies.max()/1000:.1f} GeV)")
            
            return {
                'times': times,
                'energies': energies,
                'n_events': len(times),
                'filename': filename,
                'max_energy_gev': energies.max() / 1000.0,
                'grb_name': 'GRB221009A'
            }
            
    except Exception as e:
        print(f"❌ Errore caricamento {filename}: {e}")
        return None

def analyze_grb221009a_qg(data):
    """Analizza GRB221009A per effetti QG"""
    
    print(f"\n🔬 ANALISI QG GRB221009A (BOAT)")
    print("="*50)
    
    times = data['times']
    energies = data['energies']
    
    # Converti energie in GeV
    energies_gev = energies / 1000.0
    
    # Analisi base
    correlation = np.corrcoef(energies_gev, times)[0, 1]
    significance = abs(correlation) * np.sqrt(len(energies) - 2) / np.sqrt(1 - correlation**2)
    p_value = 2 * (1 - stats.norm.cdf(significance))
    
    print(f"📊 Correlazione base: {correlation:.4f}")
    print(f"📊 Significatività base: {significance:.2f}σ")
    print(f"📊 P-value: {p_value:.6f}")
    
    # Analisi Spearman e Kendall
    spearman_corr, spearman_p = stats.spearmanr(energies_gev, times)
    spearman_sig = abs(stats.norm.ppf(spearman_p/2))
    
    kendall_corr, kendall_p = stats.kendalltau(energies_gev, times)
    kendall_sig = abs(stats.norm.ppf(kendall_p/2))
    
    print(f"📊 Spearman: {spearman_sig:.2f}σ (p={spearman_p:.6f})")
    print(f"📊 Kendall: {kendall_sig:.2f}σ (p={kendall_p:.6f})")
    
    # Analisi per filtri energetici
    print(f"\n🔍 ANALISI FILTRI ENERGETICI:")
    energy_filters = [0.1, 0.5, 1.0, 10.0, 50.0, 100.0, 200.0, 300.0]  # GeV
    
    filter_results = {}
    for filter_gev in energy_filters:
        filter_mev = filter_gev * 1000
        mask = energies >= filter_mev
        
        if np.sum(mask) > 20:  # Almeno 20 fotoni
            filtered_times = times[mask]
            filtered_energies = energies_gev[mask]
            
            if len(np.unique(filtered_energies)) > 1 and len(np.unique(filtered_times)) > 1:
                corr = np.corrcoef(filtered_energies, filtered_times)[0, 1]
                sig = abs(corr) * np.sqrt(len(filtered_energies) - 2) / np.sqrt(1 - corr**2)
                
                filter_results[f'filter_{filter_gev}_gev'] = {
                    'filter_gev': filter_gev,
                    'n_photons': np.sum(mask),
                    'correlation': corr,
                    'significance': sig
                }
                
                status = "🔥 ALTA" if sig >= 5.0 else "⚡ MEDIA" if sig >= 3.0 else "📊 BASSA"
                print(f"  📊 >{filter_gev} GeV: {sig:.2f}σ ({status}) - {np.sum(mask)} fotoni")
    
    # Analisi ultra-high energy
    print(f"\n🔍 ANALISI ULTRA-HIGH ENERGY:")
    ultra_high_mask = energies >= 100000  # >100 GeV
    
    if np.sum(ultra_high_mask) > 5:
        ultra_times = times[ultra_high_mask]
        ultra_energies = energies_gev[ultra_high_mask]
        
        corr = np.corrcoef(ultra_energies, ultra_times)[0, 1]
        sig = abs(corr) * np.sqrt(len(ultra_energies) - 2) / np.sqrt(1 - corr**2)
        
        print(f"  🔥 >100 GeV: {sig:.2f}σ - {np.sum(ultra_high_mask)} fotoni")
        print(f"  📊 Energia massima: {ultra_energies.max():.1f} GeV")
    else:
        print(f"  ❌ Troppo pochi fotoni >100 GeV: {np.sum(ultra_high_mask)}")
    
    # Analisi temporale
    print(f"\n🔍 ANALISI TEMPORALE:")
    
    # Dividi in 5 finestre temporali
    time_bins = np.linspace(times.min(), times.max(), 6)
    temporal_results = {}
    
    for i in range(5):
        start_time = time_bins[i]
        end_time = time_bins[i+1]
        mask = (times >= start_time) & (times < end_time)
        
        if np.sum(mask) > 20:
            bin_times = times[mask]
            bin_energies = energies_gev[mask]
            
            if len(np.unique(bin_energies)) > 1 and len(np.unique(bin_times)) > 1:
                corr = np.corrcoef(bin_energies, bin_times)[0, 1]
                sig = abs(corr) * np.sqrt(len(bin_energies) - 2) / np.sqrt(1 - corr**2)
                
                temporal_results[f'window_{i+1}'] = {
                    'window': i+1,
                    'start_time': start_time,
                    'end_time': end_time,
                    'n_photons': np.sum(mask),
                    'correlation': corr,
                    'significance': sig
                }
                
                status = "🔥 ALTA" if sig >= 5.0 else "⚡ MEDIA" if sig >= 3.0 else "📊 BASSA"
                print(f"  📊 Finestra {i+1}: {sig:.2f}σ ({status}) - {np.sum(mask)} fotoni")
    
    # Bootstrap test
    print(f"\n🔍 BOOTSTRAP TEST:")
    n_bootstrap = 1000
    bootstrap_results = []
    
    for i in range(n_bootstrap):
        # Campiona con replacement
        indices = np.random.choice(len(energies), size=len(energies), replace=True)
        boot_energies = energies_gev[indices]
        boot_times = times[indices]
        
        corr = np.corrcoef(boot_energies, boot_times)[0, 1]
        sig = abs(corr) * np.sqrt(len(boot_energies) - 2) / np.sqrt(1 - corr**2)
        bootstrap_results.append(sig)
    
    bootstrap_mean = np.mean(bootstrap_results)
    bootstrap_std = np.std(bootstrap_results)
    bootstrap_ci = np.percentile(bootstrap_results, [2.5, 97.5])
    
    print(f"  📊 Bootstrap: {bootstrap_mean:.2f}σ ± {bootstrap_std:.2f}σ")
    print(f"  📊 95% CI: [{bootstrap_ci[0]:.2f}, {bootstrap_ci[1]:.2f}]σ")
    
    # Compila risultati
    results = {
        'timestamp': datetime.now().isoformat(),
        'grb_name': 'GRB221009A',
        'grb_type': 'BOAT (Brightest Of All Time)',
        'filename': data['filename'],
        'n_events': data['n_events'],
        'max_energy_gev': data['max_energy_gev'],
        'base_correlation': correlation,
        'base_significance': significance,
        'p_value': p_value,
        'spearman_correlation': spearman_corr,
        'spearman_significance': spearman_sig,
        'spearman_p_value': spearman_p,
        'kendall_correlation': kendall_corr,
        'kendall_significance': kendall_sig,
        'kendall_p_value': kendall_p,
        'energy_filter_results': filter_results,
        'temporal_results': temporal_results,
        'bootstrap_results': {
            'n_bootstrap': n_bootstrap,
            'mean_significance': bootstrap_mean,
            'std_significance': bootstrap_std,
            'ci_95': bootstrap_ci.tolist()
        },
        'summary': {
            'anomaly_detected': significance >= 3.0,
            'significance': f"{significance:.2f}σ",
            'max_significance': max(significance, spearman_sig, kendall_sig),
            'analysis_status': 'GRB221009A analysis completed',
            'message': 'Review results for QG evidence in BOAT'
        }
    }
    
    return results

def create_grb221009a_plots(data, results):
    """Crea grafici per GRB221009A"""
    
    print(f"\n📊 Creazione grafici GRB221009A...")
    
    times = data['times']
    energies = data['energies'] / 1000.0  # GeV
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 15))
    
    # Plot 1: Energy vs Time scatter
    ax1 = axes[0, 0]
    scatter = ax1.scatter(times, energies, c=energies, cmap='viridis', alpha=0.6, s=20)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Energy (GeV)')
    ax1.set_title(f'GRB221009A (BOAT): Energy vs Time\n{results["n_events"]} events, Max E = {results["max_energy_gev"]:.1f} GeV')
    ax1.set_yscale('log')
    plt.colorbar(scatter, ax=ax1, label='Energy (GeV)')
    
    # Plot 2: Energy distribution
    ax2 = axes[0, 1]
    ax2.hist(energies, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    ax2.set_xlabel('Energy (GeV)')
    ax2.set_ylabel('Count')
    ax2.set_title('Energy Distribution')
    ax2.set_xscale('log')
    
    # Plot 3: Significance by energy filter
    ax3 = axes[1, 0]
    if results['energy_filter_results']:
        filters = []
        significances = []
        for key, value in results['energy_filter_results'].items():
            filters.append(value['filter_gev'])
            significances.append(value['significance'])
        
        ax3.plot(filters, significances, 'bo-', linewidth=2, markersize=8)
        ax3.axhline(y=3, color='red', linestyle='--', label='3σ Threshold')
        ax3.axhline(y=5, color='darkred', linestyle='--', label='5σ Threshold')
        ax3.set_xlabel('Energy Filter (GeV)')
        ax3.set_ylabel('Significance (σ)')
        ax3.set_title('Significance vs Energy Filter')
        ax3.set_xscale('log')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # Plot 4: Temporal analysis
    ax4 = axes[1, 1]
    if results['temporal_results']:
        windows = []
        sigs = []
        for key, value in results['temporal_results'].items():
            windows.append(value['window'])
            sigs.append(value['significance'])
        
        ax4.bar(windows, sigs, alpha=0.7, color='lightcoral')
        ax4.axhline(y=3, color='red', linestyle='--', label='3σ Threshold')
        ax4.axhline(y=5, color='darkred', linestyle='--', label='5σ Threshold')
        ax4.set_xlabel('Time Window')
        ax4.set_ylabel('Significance (σ)')
        ax4.set_title('Significance vs Time Window')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('grb221009a_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici GRB221009A creati: grb221009a_analysis.png")

def main():
    """Funzione principale per analisi GRB221009A"""
    
    print("="*70)
    print("ANALISI GRB221009A - BOAT (Brightest Of All Time)")
    print("Il GRB più brillante mai osservato")
    print("="*70)
    
    # Carica dati
    data = load_grb221009a_data()
    if data is None:
        print("❌ Impossibile caricare dati GRB221009A")
        return
    
    # Analizza QG
    results = analyze_grb221009a_qg(data)
    
    # Crea grafici
    create_grb221009a_plots(data, results)
    
    # Salva risultati
    with open('grb221009a_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto finale
    print(f"\n{'='*70}")
    print("🎯 RIASSUNTO ANALISI GRB221009A (BOAT)")
    print(f"{'='*70}")
    
    print(f"🎯 GRB: {results['grb_name']} ({results['grb_type']})")
    print(f"🎯 Eventi: {results['n_events']}")
    print(f"🎯 Energia massima: {results['max_energy_gev']:.1f} GeV")
    print(f"🎯 Correlazione base: {results['base_correlation']:.4f}")
    print(f"🎯 Significatività base: {results['base_significance']:.2f}σ")
    print(f"🎯 Spearman: {results['spearman_significance']:.2f}σ")
    print(f"🎯 Kendall: {results['kendall_significance']:.2f}σ")
    print(f"🎯 P-value: {results['p_value']:.6f}")
    
    # Analisi finale
    max_sig = results['summary']['max_significance']
    if max_sig >= 5.0:
        status = "🔥 ALTA SIGNIFICATIVITÀ"
        anomaly = "✅ ANOMALIA RILEVATA"
    elif max_sig >= 3.0:
        status = "⚡ MEDIA SIGNIFICATIVITÀ"
        anomaly = "⚠️ ANOMALIA POSSIBILE"
    else:
        status = "📊 BASSA SIGNIFICATIVITÀ"
        anomaly = "❌ NESSUNA ANOMALIA"
    
    print(f"\n🔍 ANALISI FINALE:")
    print(f"  📊 Significatività massima: {max_sig:.2f}σ ({status})")
    print(f"  📊 {anomaly}")
    
    if max_sig >= 3.0:
        print(f"\n🚨 GRB221009A MOSTRA SEGNALE POTENZIALE!")
        print(f"🚨 Confronta con GRB090902 per pattern comuni!")
    
    print(f"\n{'='*70}")
    print("✅ Analisi GRB221009A completata!")
    print("📊 Risultati salvati: grb221009a_analysis.json")
    print("📈 Grafici salvati: grb221009a_analysis.png")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()

