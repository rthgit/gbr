#!/usr/bin/env python3
"""
ANALISI DATI REALI SCARICATI
============================

Analisi dei dati FITS reali scaricati da Fermi:
- Caricamento e verifica file FITS
- Estrazione dati eventi e spacecraft
- Analisi QG con metodologie robuste
- Confronto con risultati simulati

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
import glob
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurazione matplotlib
plt.style.use('default')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

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

def find_downloaded_fits_files():
    """Trova tutti i file FITS scaricati"""
    
    # Cerca file FITS nella directory corrente
    fits_files = glob.glob("*.fits")
    
    # Separa file EV00 e SC00
    ev_files = [f for f in fits_files if "_EV00.fits" in f]
    sc_files = [f for f in fits_files if "_SC00.fits" in f]
    
    return fits_files, ev_files, sc_files

def analyze_fits_file(filename):
    """Analizza un singolo file FITS"""
    
    try:
        with fits.open(filename) as hdul:
            print(f"  📁 File: {filename}")
            print(f"  📊 HDUs: {len(hdul)}")
            
            for i, hdu in enumerate(hdul):
                print(f"    HDU {i}: {hdu.name} - {hdu.header.get('EXTNAME', 'No name')}")
                if hasattr(hdu, 'data') and hdu.data is not None:
                    print(f"      Data shape: {hdu.data.shape}")
                    if hasattr(hdu.data, 'dtype'):
                        print(f"      Data type: {hdu.data.dtype}")
                        if len(hdu.data.dtype.names) > 0:
                            print(f"      Columns: {hdu.data.dtype.names[:5]}...")  # Prime 5 colonne
            
            return {
                'filename': filename,
                'n_hdus': len(hdul),
                'hdus_info': [
                    {
                        'index': i,
                        'name': hdu.name,
                        'extname': hdu.header.get('EXTNAME', 'No name'),
                        'data_shape': hdu.data.shape if hasattr(hdu, 'data') and hdu.data is not None else None,
                        'columns': list(hdu.data.dtype.names) if hasattr(hdu, 'data') and hdu.data is not None and hasattr(hdu.data, 'dtype') and len(hdu.data.dtype.names) > 0 else None
                    }
                    for i, hdu in enumerate(hdul)
                ]
            }
    except Exception as e:
        print(f"  ❌ Errore analisi {filename}: {e}")
        return None

def extract_events_data(ev_filename):
    """Estrae dati eventi da file EV00"""
    
    try:
        with fits.open(ev_filename) as hdul:
            # Cerca HDU con dati eventi
            events_hdu = None
            for hdu in hdul:
                if hasattr(hdu, 'data') and hdu.data is not None:
                    if 'TIME' in str(hdu.data.dtype.names) or 'ENERGY' in str(hdu.data.dtype.names):
                        events_hdu = hdu
                        break
            
            if events_hdu is None:
                print(f"  ❌ Nessun HDU con dati eventi trovato in {ev_filename}")
                return None
            
            data = events_hdu.data
            print(f"  📊 Dati eventi: {len(data)} eventi")
            print(f"  📊 Colonne: {data.dtype.names}")
            
            # Estrai colonne principali
            result = {
                'filename': ev_filename,
                'n_events': len(data),
                'columns': list(data.dtype.names)
            }
            
            # Cerca colonne tempo ed energia
            time_cols = [col for col in data.dtype.names if 'TIME' in col.upper()]
            energy_cols = [col for col in data.dtype.names if 'ENERGY' in col.upper() or 'ENERG' in col.upper()]
            
            if time_cols:
                result['time_column'] = time_cols[0]
                result['times'] = data[time_cols[0]]
            
            if energy_cols:
                result['energy_column'] = energy_cols[0]
                result['energies'] = data[energy_cols[0]]
            
            # Cerca altre colonne utili
            if 'RA' in data.dtype.names:
                result['ra'] = data['RA']
            if 'DEC' in data.dtype.names:
                result['dec'] = data['DEC']
            if 'ZENITH_ANGLE' in data.dtype.names:
                result['zenith_angle'] = data['ZENITH_ANGLE']
            
            return result
            
    except Exception as e:
        print(f"  ❌ Errore estrazione eventi {ev_filename}: {e}")
        return None

def perform_qg_analysis(events_data):
    """Esegue analisi QG sui dati eventi"""
    
    if not events_data or 'times' not in events_data or 'energies' not in events_data:
        return None
    
    times = events_data['times']
    energies = events_data['energies']
    
    if len(times) < 10:
        print(f"  ❌ Troppi pochi eventi per analisi QG: {len(times)}")
        return None
    
    print(f"  🔬 Analisi QG: {len(times)} eventi")
    
    # Filtra dati validi
    valid_mask = (energies > 0) & (times > 0) & np.isfinite(energies) & np.isfinite(times)
    times_valid = times[valid_mask]
    energies_valid = energies[valid_mask]
    
    if len(times_valid) < 10:
        print(f"  ❌ Troppi pochi eventi validi: {len(times_valid)}")
        return None
    
    print(f"  📊 Eventi validi: {len(times_valid)}")
    print(f"  📊 Range energia: {energies_valid.min():.3f} - {energies_valid.max():.3f}")
    print(f"  📊 Range tempo: {times_valid.min():.3f} - {times_valid.max():.3f}")
    
    # Analisi QG robusta
    correlation = np.corrcoef(energies_valid, times_valid)[0, 1]
    significance = abs(correlation) * np.sqrt(len(energies_valid) - 2) / np.sqrt(1 - correlation**2)
    
    # Fit lineare
    slope, intercept = np.polyfit(energies_valid, times_valid, 1)
    
    # Test di permutazione
    n_permutations = 100
    permuted_significances = []
    
    for _ in range(n_permutations):
        permuted_times = np.random.permutation(times_valid)
        perm_corr = np.corrcoef(energies_valid, permuted_times)[0, 1]
        perm_sig = abs(perm_corr) * np.sqrt(len(energies_valid) - 2) / np.sqrt(1 - perm_corr**2)
        permuted_significances.append(perm_sig)
    
    p_value = np.sum(np.array(permuted_significances) >= significance) / n_permutations
    
    # Analisi per bin energetici
    n_bins = min(10, len(energies_valid) // 50)
    if n_bins > 1:
        energy_bins = np.linspace(energies_valid.min(), energies_valid.max(), n_bins + 1)
        bin_correlations = []
        
        for i in range(n_bins):
            bin_mask = (energies_valid >= energy_bins[i]) & (energies_valid < energy_bins[i + 1])
            if np.sum(bin_mask) > 5:
                bin_energies = energies_valid[bin_mask]
                bin_times = times_valid[bin_mask]
                bin_corr = np.corrcoef(bin_energies, bin_times)[0, 1]
                bin_correlations.append(bin_corr)
        
        avg_bin_corr = np.mean(bin_correlations) if bin_correlations else 0
    else:
        avg_bin_corr = correlation
    
    return {
        'n_events': len(times_valid),
        'energy_range': [float(energies_valid.min()), float(energies_valid.max())],
        'time_range': [float(times_valid.min()), float(times_valid.max())],
        'correlation': correlation,
        'significance': significance,
        'slope': slope,
        'intercept': intercept,
        'p_value': p_value,
        'bin_correlation': avg_bin_corr,
        'n_energy_bins': n_bins,
        'permuted_significances_mean': np.mean(permuted_significances),
        'permuted_significances_std': np.std(permuted_significances)
    }

def analyze_all_downloaded_data():
    """Analizza tutti i dati scaricati"""
    
    print("🔍 Analisi Dati Reali Scaricati...")
    
    # Trova file FITS
    all_files, ev_files, sc_files = find_downloaded_fits_files()
    
    print(f"📊 File FITS trovati: {len(all_files)}")
    print(f"📊 File eventi (EV00): {len(ev_files)}")
    print(f"📊 File spacecraft (SC00): {len(sc_files)}")
    
    # Analizza struttura file
    print("\n🔍 Analisi Struttura File...")
    file_analysis = []
    
    for filename in all_files:
        analysis = analyze_fits_file(filename)
        if analysis:
            file_analysis.append(analysis)
    
    # Analizza dati eventi
    print("\n🔍 Analisi Dati Eventi...")
    events_analysis = []
    
    for ev_file in ev_files:
        print(f"\n📁 Analizzando {ev_file}...")
        events_data = extract_events_data(ev_file)
        if events_data:
            qg_result = perform_qg_analysis(events_data)
            if qg_result:
                events_analysis.append({
                    'filename': ev_file,
                    'events_data': events_data,
                    'qg_analysis': qg_result
                })
    
    return {
        'all_files': all_files,
        'ev_files': ev_files,
        'sc_files': sc_files,
        'file_analysis': file_analysis,
        'events_analysis': events_analysis
    }

def create_real_data_plots(analysis_results):
    """Crea grafici per dati reali"""
    
    events_analysis = analysis_results['events_analysis']
    
    if not events_analysis:
        print("❌ Nessun dato evento disponibile per grafici")
        return
    
    n_files = len(events_analysis)
    n_cols = min(3, n_files)
    n_rows = (n_files + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
    if n_files == 1:
        axes = [axes]
    elif n_rows == 1:
        axes = axes.reshape(1, -1)
    
    fig.suptitle('Real Downloaded GRB Data Analysis', fontsize=16, fontweight='bold')
    
    for i, result in enumerate(events_analysis):
        if i >= n_rows * n_cols:
            break
            
        row = i // n_cols
        col = i % n_cols
        ax = axes[row, col] if n_rows > 1 else axes[col]
        
        events_data = result['events_data']
        qg_analysis = result['qg_analysis']
        
        # Plot energia vs tempo
        times = events_data['times']
        energies = events_data['energies']
        
        valid_mask = (energies > 0) & (times > 0) & np.isfinite(energies) & np.isfinite(times)
        times_valid = times[valid_mask]
        energies_valid = energies[valid_mask]
        
        scatter = ax.scatter(energies_valid, times_valid, alpha=0.6, s=1)
        ax.set_xlabel('Energy')
        ax.set_ylabel('Time')
        ax.set_title(f"{result['filename'][:20]}...\n"
                    f"Significance: {qg_analysis['significance']:.2f}σ")
        ax.grid(True, alpha=0.3)
    
    # Rimuovi assi vuoti
    for i in range(n_files, n_rows * n_cols):
        row = i // n_cols
        col = i % n_cols
        ax = axes[row, col] if n_rows > 1 else axes[col]
        ax.remove()
    
    plt.tight_layout()
    plt.savefig('real_downloaded_data_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("✅ Grafici dati reali creati: real_downloaded_data_analysis.png")

def main():
    """Funzione principale per analisi dati reali"""
    
    print("="*70)
    print("ANALISI DATI REALI SCARICATI")
    print("Analisi dei file FITS reali scaricati da Fermi")
    print("="*70)
    
    # Analizza tutti i dati scaricati
    analysis_results = analyze_all_downloaded_data()
    
    # Crea grafici
    print("\n📊 Creazione grafici dati reali...")
    create_real_data_plots(analysis_results)
    
    # Compila risultati
    results = {
        'timestamp': datetime.now().isoformat(),
        'analysis_results': analysis_results,
        'summary': {
            'total_fits_files': len(analysis_results['all_files']),
            'ev_files': len(analysis_results['ev_files']),
            'sc_files': len(analysis_results['sc_files']),
            'analyzed_files': len(analysis_results['events_analysis']),
            'high_significance_files': sum(1 for r in analysis_results['events_analysis'] if r['qg_analysis']['significance'] > 3.0),
            'low_p_value_files': sum(1 for r in analysis_results['events_analysis'] if r['qg_analysis']['p_value'] < 0.01)
        }
    }
    
    # Salva risultati
    with open('real_downloaded_data_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto
    print("\n" + "="*70)
    print("🎯 RISULTATI ANALISI DATI REALI")
    print("="*70)
    
    print(f"🎯 File FITS Totali: {results['summary']['total_fits_files']}")
    print(f"🎯 File Eventi: {results['summary']['ev_files']}")
    print(f"🎯 File Spacecraft: {results['summary']['sc_files']}")
    print(f"🎯 File Analizzati: {results['summary']['analyzed_files']}")
    print(f"🎯 File Alta Significatività: {results['summary']['high_significance_files']}")
    print(f"🎯 File P-Value Basso: {results['summary']['low_p_value_files']}")
    
    print(f"\n🔍 Risultati per File:")
    for result in analysis_results['events_analysis']:
        qg_analysis = result['qg_analysis']
        print(f"  {result['filename']}: {qg_analysis['significance']:.2f}σ (p={qg_analysis['p_value']:.3f})")
    
    print("\n" + "="*70)
    print("✅ Analisi dati reali completata!")
    print("📊 Risultati salvati: real_downloaded_data_analysis.json")
    print("📈 Grafici salvati: real_downloaded_data_analysis.png")
    print("="*70)

if __name__ == "__main__":
    main()
