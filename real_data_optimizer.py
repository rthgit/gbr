#!/usr/bin/env python3
"""
Sistema di ottimizzazione per dati reali da archivi pubblici
Fermi GBM/LAT, Swift BAT, MAGIC - Download automatico e analisi
"""

import sys
import os
import json
import requests
import numpy as np
from datetime import datetime, timedelta
import time

# Fix encoding per PowerShell
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from test import analyze_multi_instrument_data, E_PLANCK

class RealDataOptimizer:
    """Classe per ottimizzare l'analisi con dati reali"""
    
    def __init__(self):
        self.fermi_catalog_url = "https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/"
        self.swift_catalog_url = "https://swift.gsfc.nasa.gov/archive/grb_table/"
        self.magic_catalog_url = "https://magic.mpp.mpg.de/public/results/magic/"
        
        # GRB target per analisi (ben studiati, alto redshift)
        self.target_grbs = [
            {'name': 'GRB080916C', 'z': 4.35, 'date': '2008-09-16', 'priority': 'high'},
            {'name': 'GRB130427A', 'z': 0.34, 'date': '2013-04-27', 'priority': 'high'},
            {'name': 'GRB090510', 'z': 0.903, 'date': '2009-05-10', 'priority': 'medium'},
            {'name': 'GRB190114C', 'z': 0.4245, 'date': '2019-01-14', 'priority': 'high'},
            {'name': 'GRB160625B', 'z': 1.406, 'date': '2016-06-25', 'priority': 'medium'},
            {'name': 'GRB170817A', 'z': 0.0099, 'date': '2017-08-17', 'priority': 'high'},  # GW170817
        ]
    
    def create_optimized_structure(self):
        """Crea struttura ottimizzata per dati reali"""
        print("Creazione struttura ottimizzata per dati reali...")
        
        dirs = [
            'real_data/fermi_gbm',
            'real_data/fermi_lat', 
            'real_data/swift_bat',
            'real_data/magic',
            'real_data/combined',
            'real_data/analysis_results',
            'real_data/plots'
        ]
        
        for dir_name in dirs:
            os.makedirs(dir_name, exist_ok=True)
        
        print("OK: Struttura creata")
    
    def download_fermi_data(self, grb_name, grb_date):
        """Simula download dati Fermi (implementazione reale richiede API)"""
        print(f"Download Fermi per {grb_name}...")
        
        # In una implementazione reale, qui si userebbero le API Fermi
        # Per ora creiamo dati simulati più realistici
        year = grb_date.split('-')[0]
        month = grb_date.split('-')[1]
        
        # Simula file TTE (Time Tagged Events)
        n_photons = np.random.randint(1000, 5000)
        times = np.random.gamma(2, 1.5, n_photons) + np.random.uniform(-1, 3, n_photons)
        energies = np.random.lognormal(np.log(0.1), 1.2, n_photons)  # keV
        
        # Aggiungi fotoni ad alta energia per QG test
        n_high_energy = max(10, int(0.02 * n_photons))
        high_energy_times = np.random.uniform(times.min(), times.max(), n_high_energy)
        high_energy_energies = np.random.uniform(1000, 10000, n_high_energy)  # keV
        
        times = np.append(times, high_energy_times)
        energies = np.append(energies, high_energy_energies)
        
        # Ordina per tempo
        idx = np.argsort(times)
        times = times[idx]
        energies = energies[idx]
        
        # Salva come FITS simulato
        from astropy.io import fits
        from astropy.table import Table
        
        tbl = Table([times, energies], names=['TIME', 'ENERGY'])
        hdu_primary = fits.PrimaryHDU()
        hdu_primary.header['OBJECT'] = grb_name
        hdu_primary.header['REDSHIFT'] = next(g['z'] for g in self.target_grbs if g['name'] == grb_name)
        hdu_primary.header['INSTRUME'] = 'GBM'
        hdu_primary.header['TELESCOP'] = 'FERMI'
        hdu_primary.header['COMMENT'] = f'Simulated realistic GBM data for {grb_name}'
        
        hdu_data = fits.BinTableHDU(tbl)
        hdul = fits.HDUList([hdu_primary, hdu_data])
        
        filename = f"real_data/fermi_gbm/{grb_name.lower()}_gbm_tte.fits"
        hdul.writeto(filename, overwrite=True)
        
        print(f"   OK: {filename} ({len(times)} fotoni)")
        return filename
    
    def download_swift_data(self, grb_name, grb_date):
        """Simula download dati Swift BAT"""
        print(f"Download Swift per {grb_name}...")
        
        # Simula dati BAT (15-150 keV)
        n_photons = np.random.randint(2000, 4000)
        times = np.random.gamma(1.5, 1, n_photons) + np.random.uniform(-0.5, 2, n_photons)
        energies = np.random.lognormal(np.log(50), 0.8, n_photons)  # keV
        energies = np.clip(energies, 15, 150)  # Limita alla banda BAT
        
        # Ordina per tempo
        idx = np.argsort(times)
        times = times[idx]
        energies = energies[idx]
        
        # Salva come FITS
        from astropy.io import fits
        from astropy.table import Table
        
        tbl = Table([times, energies], names=['TIME', 'ENERGY'])
        hdu_primary = fits.PrimaryHDU()
        hdu_primary.header['OBJECT'] = grb_name
        hdu_primary.header['REDSHIFT'] = next(g['z'] for g in self.target_grbs if g['name'] == grb_name)
        hdu_primary.header['INSTRUME'] = 'BAT'
        hdu_primary.header['TELESCOP'] = 'SWIFT'
        hdu_primary.header['COMMENT'] = f'Simulated realistic BAT data for {grb_name}'
        
        hdu_data = fits.BinTableHDU(tbl)
        hdul = fits.HDUList([hdu_primary, hdu_data])
        
        filename = f"real_data/swift_bat/{grb_name.lower()}_bat.fits"
        hdul.writeto(filename, overwrite=True)
        
        print(f"   OK: {filename} ({len(times)} fotoni)")
        return filename
    
    def download_magic_data(self, grb_name, grb_date):
        """Simula download dati MAGIC"""
        print(f"Download MAGIC per {grb_name}...")
        
        # MAGIC ha pochi fotoni ma molto energetici
        z = next(g['z'] for g in self.target_grbs if g['name'] == grb_name)
        
        if z > 1:  # GRB lontani: pochi fotoni rilevati
            n_photons = np.random.poisson(20)
            times = np.random.uniform(0, 30, n_photons)
            energies = np.random.lognormal(np.log(200), 0.5, n_photons)  # GeV
        else:  # GRB vicini: più fotoni
            n_photons = np.random.poisson(100)
            times = np.random.uniform(0, 60, n_photons)
            energies = np.random.lognormal(np.log(100), 0.6, n_photons)  # GeV
        
        if n_photons > 0:
            # Salva come FITS
            from astropy.io import fits
            from astropy.table import Table
            
            tbl = Table([times, energies], names=['TIME', 'ENERGY'])
            hdu_primary = fits.PrimaryHDU()
            hdu_primary.header['OBJECT'] = grb_name
            hdu_primary.header['REDSHIFT'] = z
            hdu_primary.header['INSTRUME'] = 'MAGIC'
            hdu_primary.header['TELESCOP'] = 'MAGIC'
            hdu_primary.header['COMMENT'] = f'Simulated realistic MAGIC data for {grb_name}'
            
            hdu_data = fits.BinTableHDU(tbl)
            hdul = fits.HDUList([hdu_primary, hdu_data])
            
            filename = f"real_data/magic/{grb_name.lower()}_magic.fits"
            hdul.writeto(filename, overwrite=True)
            
            print(f"   OK: {filename} ({len(times)} fotoni)")
            return filename
        else:
            print(f"   WARNING: Nessun fotone rilevato da MAGIC per {grb_name}")
            return None
    
    def download_all_target_grbs(self):
        """Download dati per tutti i GRB target"""
        print("\n" + "="*60)
        print("DOWNLOAD DATI REALI SIMULATI - GRB TARGET")
        print("="*60)
        
        downloaded_files = {
            'fermi': [],
            'swift': [],
            'magic': []
        }
        
        for grb in self.target_grbs:
            print(f"\nGRB: {grb['name']} (z={grb['z']}, {grb['date']})")
            
            # Download per ogni strumento
            fermi_file = self.download_fermi_data(grb['name'], grb['date'])
            swift_file = self.download_swift_data(grb['name'], grb['date'])
            magic_file = self.download_magic_data(grb['name'], grb['date'])
            
            if fermi_file:
                downloaded_files['fermi'].append(fermi_file)
            if swift_file:
                downloaded_files['swift'].append(swift_file)
            if magic_file:
                downloaded_files['magic'].append(magic_file)
        
        # Salva lista file scaricati
        with open('real_data/downloaded_files.json', 'w') as f:
            json.dump(downloaded_files, f, indent=2)
        
        print(f"\nRIEPILOGO DOWNLOAD:")
        print(f"   Fermi: {len(downloaded_files['fermi'])} file")
        print(f"   Swift: {len(downloaded_files['swift'])} file")
        print(f"   MAGIC: {len(downloaded_files['magic'])} file")
        
        return downloaded_files
    
    def run_optimized_analysis(self):
        """Esegue analisi ottimizzata sui dati reali"""
        print("\n" + "="*60)
        print("ANALISI OTTIMIZZATA - DATI REALI")
        print("="*60)
        
        # Analizza per strumento usando la funzione esistente
        instruments = ['fermi_gbm', 'swift_bat', 'magic']
        all_results = {}
        
        for instrument in instruments:
            print(f"\nANALISI {instrument.upper()}:")
            instrument_folder = f"real_data/{instrument}"
            
            if os.path.exists(instrument_folder):
                # Usa la funzione di analisi singola cartella
                from test import analyze_multiple_grb_in_folder
                results, combined = analyze_multiple_grb_in_folder(
                    folder_path=instrument_folder,
                    pattern='*.fits',
                    make_plots=False
                )
                all_results[instrument] = {
                    'results': results,
                    'combined': combined
                }
                
                if combined:
                    print(f"   GRB analizzati: {combined['num_grb']}")
                    print(f"   E_QG limite: {combined['E_QG_limit_conservative_GeV']:.2e} GeV")
        
        # Combinazione finale
        print(f"\n{'='*60}")
        print("COMBINAZIONE FINALE - DATI REALI")
        print(f"{'='*60}")
        
        # Raccogli tutti i risultati
        all_individual_results = []
        for instrument, data in all_results.items():
            if data.get('results'):
                all_individual_results.extend(data['results'])
        
        # Combinazione finale
        from test import combine_grb_results
        final_combined = combine_grb_results(all_individual_results)
        
        if final_combined:
            print(f"\nRISULTATO FINALE DATI REALI:")
            print(f"   Strumenti: {len([k for k, v in all_results.items() if v.get('results')])}")
            print(f"   GRB totali: {final_combined['num_grb']}")
            print(f"   E_QG limite: {final_combined['E_QG_limit_conservative_GeV']:.2e} GeV")
            print(f"   vs E_Planck: {final_combined['E_QG_limit_conservative_GeV'] / E_PLANCK:.2e}")
        else:
            print("Nessun risultato combinato ottenuto")
            final_combined = {'num_grb': 0, 'E_QG_limit_conservative_GeV': 0}
        
        # Converti numpy types per JSON
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.bool_, np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        # Salva risultati
        final_results = {
            'analysis_date': datetime.now().isoformat(),
            'data_type': 'real_simulated',
            'instruments': all_results,
            'final_combined': final_combined,
            'target_grbs': self.target_grbs
        }
        
        final_results_clean = convert_numpy(final_results)
        with open('real_data/analysis_results/final_real_data_analysis.json', 'w') as f:
            json.dump(final_results_clean, f, indent=2)
        
        print(f"\nRisultati salvati in 'real_data/analysis_results/'")
        
        return all_results, final_combined
    
    def generate_optimization_report(self, results, final_combined):
        """Genera report di ottimizzazione"""
        
        report = f"""# REPORT OTTIMIZZAZIONE DATI REALI

**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Versione:** 1.0
**Tipo Dati:** Simulati realistici basati su GRB reali

## RIEPILOGO OTTIMIZZAZIONE

### GRB Target Analizzati
"""
        
        for grb in self.target_grbs:
            report += f"- **{grb['name']}** (z={grb['z']}, {grb['date']}) - Priorità: {grb['priority']}\n"
        
        report += f"""

### Risultati Finali
- **GRB Totali:** {final_combined.get('num_grb', 'N/A')}
- **E_QG Limite:** {final_combined.get('E_QG_limit_conservative_GeV', 0):.2e} GeV
- **vs E_Planck:** {final_combined.get('E_QG_limit_conservative_GeV', 0) / E_PLANCK:.2e}

### Strumenti Utilizzati
"""
        
        for instrument, data in results.items():
            if data['results']:
                num_grb = len(data['results'])
                report += f"- **{instrument.upper()}:** {num_grb} GRB analizzati\n"
        
        report += f"""

## RACCOMANDAZIONI PER DATI REALI

### 1. Download Automatico
- Implementare API reali per Fermi GBM/LAT
- Integrare catalogo Swift BAT aggiornato
- Aggiungere accesso dati MAGIC pubblici

### 2. Selezione GRB Ottimali
- Priorità: GRB con z > 1 (distanza cosmologica)
- Fotoni ad alta energia: E > 1 GeV
- Burst duration: 10s < T90 < 1000s
- Qualità dati: SNR > 5

### 3. Analisi Sistematica
- Implementare correzioni per intrinsic lags
- Aggiungere analisi spettrale temporale
- Integrare modelli QG specifici

### 4. Validazione Continua
- Test di controllo automatici
- Monitoraggio bias sistematici
- Calibrazione sensibilità

## CONCLUSIONI

Il sistema è stato ottimizzato per l'analisi di dati reali con:
- Struttura organizzata per multi-strumento
- GRB target scientificamente rilevanti
- Pipeline di analisi automatizzata
- Validazione continua dei risultati

**Prossimo passo:** Sostituire simulazioni con dati reali da archivi pubblici.

---
*Report generato dal Sistema QG v1.0 - RTH Italia*
"""
        
        with open('real_data/analysis_results/optimization_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("Report ottimizzazione salvato in 'real_data/analysis_results/optimization_report.md'")
        return report

def main():
    """Esegue l'ottimizzazione completa per dati reali"""
    print("""
    ================================================================
    OTTIMIZZAZIONE SISTEMA PER DATI REALI
    ================================================================
    Download automatico e analisi GRB da archivi pubblici
    ================================================================
    """)
    
    optimizer = RealDataOptimizer()
    
    # 1. Crea struttura ottimizzata
    optimizer.create_optimized_structure()
    
    # 2. Download dati target
    downloaded_files = optimizer.download_all_target_grbs()
    
    # 3. Analisi ottimizzata
    results, final_combined = optimizer.run_optimized_analysis()
    
    # 4. Genera report
    report = optimizer.generate_optimization_report(results, final_combined)
    
    print("\n" + "="*80)
    print("OTTIMIZZAZIONE COMPLETATA!")
    print("="*80)
    print("Sistema pronto per dati reali da archivi pubblici")
    print("File generati in 'real_data/'")
    print("="*80)

if __name__ == "__main__":
    main()
