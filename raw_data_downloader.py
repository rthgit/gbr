#!/usr/bin/env python3
"""
=============================================================================
RAW DATA DOWNLOADER - Scaricatore Dati Grezzi Reali
=============================================================================
Scarica DATI GREZZI REALI di GRB da archivi astronomici ufficiali.
Implementa accesso diretto alle API pubbliche di NASA, ESA, e altri osservatori.

ARCHIVI TARGET:
- Fermi GBM: https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/
- Fermi LAT: https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/
- Swift BAT: https://swift.gsfc.nasa.gov/archive/swift/
- MAGIC: https://magic.mpp.mpg.de/data/
- HESS: https://www.mpi-hd.mpg.de/hfm/HESS/

AUTORE: Christian Quintino De Luca (RTH Italia)
DATA: 2025-10-20
"""

import os
import sys
import requests
import numpy as np
from astropy.io import fits
from astropy.table import Table
import json
from datetime import datetime, timedelta
import time
import urllib.parse
from pathlib import Path
import re

# Configurazione encoding per Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

class RawDataDownloader:
    """Scaricatore di dati grezzi reali da archivi astronomici."""
    
    def __init__(self):
        self.base_dir = 'raw_data'
        self.instrument_dirs = {
            'fermi_gbm': os.path.join(self.base_dir, 'fermi_gbm'),
            'fermi_lat': os.path.join(self.base_dir, 'fermi_lat'),
            'swift_bat': os.path.join(self.base_dir, 'swift_bat'),
            'magic': os.path.join(self.base_dir, 'magic'),
            'hess': os.path.join(self.base_dir, 'hess')
        }
        
        # Crea directory
        for dir_path in self.instrument_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # URL degli archivi
        self.archive_urls = {
            'fermi_gbm_base': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/',
            'fermi_lat_base': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/',
            'swift_bat_base': 'https://swift.gsfc.nasa.gov/archive/swift/',
            'magic_base': 'https://magic.mpp.mpg.de/data/',
            'hess_base': 'https://www.mpi-hd.mpg.de/hfm/HESS/'
        }
        
        # Parametri GRB target con trigger ID reali
        self.target_grbs = {
            'GRB080916C': {
                'trigger_id': '080916409',
                'trigger_time': '2008-09-16T00:12:45',
                'date': '2008-09-16',
                'redshift': 4.35,
                'max_energy': 13.2,  # GeV
                'instruments': ['fermi_gbm', 'fermi_lat'],
                'ra': 119.8,
                'dec': -56.6
            },
            'GRB130427A': {
                'trigger_id': '130427324',
                'trigger_time': '2013-04-27T04:57:00',
                'date': '2013-04-27',
                'redshift': 0.34,
                'max_energy': 95.0,  # GeV
                'instruments': ['fermi_gbm', 'fermi_lat', 'swift_bat'],
                'ra': 173.1,
                'dec': 27.7
            },
            'GRB090510': {
                'trigger_id': '090510016',
                'trigger_time': '2009-05-10T00:23:00',
                'date': '2009-05-10',
                'redshift': 0.903,
                'max_energy': 31.0,  # GeV
                'instruments': ['fermi_gbm', 'fermi_lat'],
                'ra': 333.5,
                'dec': -26.6
            },
            'GRB190114C': {
                'trigger_id': '190114873',
                'trigger_time': '2019-01-14T20:57:03',
                'date': '2019-01-14',
                'redshift': 0.4245,
                'max_energy': 1000.0,  # GeV (TeV!)
                'instruments': ['fermi_gbm', 'fermi_lat', 'magic'],
                'ra': 56.5,
                'dec': 70.8
            }
        }
        
        print("🔬 RAW DATA DOWNLOADER INIZIALIZZATO")
        print("=" * 50)
        print(f"📁 Directory base: {self.base_dir}")
        print(f"🎯 GRB target: {list(self.target_grbs.keys())}")
        print("⚠️  ATTENZIONE: Scaricamento dati REALI da archivi ufficiali")
    
    def test_archive_access(self):
        """Testa l'accessibilità degli archivi."""
        print("\n🌐 TEST ACCESSIBILITÀ ARCHIVI")
        print("=" * 40)
        
        results = {}
        
        for archive_name, url in self.archive_urls.items():
            try:
                print(f"🔍 Testando {archive_name}...")
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    print(f"   ✅ {archive_name}: ACCESSIBILE")
                    results[archive_name] = True
                else:
                    print(f"   ❌ {archive_name}: HTTP {response.status_code}")
                    results[archive_name] = False
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ {archive_name}: ERRORE - {str(e)[:50]}...")
                results[archive_name] = False
            
            time.sleep(2)  # Rispetta i server
        
        return results
    
    def download_fermi_gbm_raw_data(self, grb_info):
        """Scarica dati grezzi Fermi GBM."""
        grb_name = grb_info.get('grb_name', 'Unknown')
        trigger_id = grb_info['trigger_id']
        date = grb_info['date']
        
        print(f"\n📡 SCARICANDO FERMI GBM RAW DATA - {grb_name}")
        print("=" * 50)
        
        # Costruisci URL per il trigger specifico
        year = date[:4]
        month = int(date[5:7])
        day = int(date[8:10])
        
        # URL base per dati GBM del giorno
        base_url = f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/{year}/{month:02d}/{day:02d}/"
        
        print(f"🔍 URL base: {base_url}")
        
        # Tipi di file da cercare per GBM
        file_types = [
            'tte',  # Time Tagged Events
            'ctime',  # Continuous Time
            'rsp',  # Response files
            'cat'   # Catalog files
        ]
        
        downloaded_files = []
        
        for file_type in file_types:
            try:
                # Costruisci nome file
                filename = f"glg_{file_type}_all_{year}{month:02d}{day:02d}_v00.fit"
                file_url = base_url + filename
                
                print(f"🔍 Tentando download: {filename}")
                
                # Prova download
                response = requests.get(file_url, timeout=30)
                
                if response.status_code == 200:
                    # Salva file
                    filepath = os.path.join(
                        self.instrument_dirs['fermi_gbm'], 
                        f"{grb_name.lower()}_gbm_{file_type}.fits"
                    )
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    file_size_kb = len(response.content) / 1024
                    print(f"   ✅ Scaricato: {filepath} ({file_size_kb:.1f} KB)")
                    
                    # Verifica che sia un FITS valido
                    try:
                        with fits.open(filepath) as hdul:
                            print(f"   ✅ FITS valido: {len(hdul)} HDUs")
                    except Exception as e:
                        print(f"   ⚠️  FITS non valido: {e}")
                        os.remove(filepath)
                        continue
                    
                    downloaded_files.append(filepath)
                    
                else:
                    print(f"   ❌ File non trovato: HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Errore download: {str(e)[:50]}...")
            
            time.sleep(3)  # Rispetta i server
        
        return downloaded_files
    
    def download_fermi_lat_raw_data(self, grb_info):
        """Scarica dati grezzi Fermi LAT."""
        grb_name = grb_info.get('grb_name', 'Unknown')
        date = grb_info['date']
        
        print(f"\n📡 SCARICANDO FERMI LAT RAW DATA - {grb_name}")
        print("=" * 50)
        
        year = date[:4]
        month = int(date[5:7])
        day = int(date[8:10])
        
        # URL base per dati LAT
        base_url = f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/{year}/{month:02d}/{day:02d}/"
        
        print(f"🔍 URL base: {base_url}")
        
        # Prova a scaricare file LAT
        file_patterns = [
            f"LAT_*_{year}{month:02d}{day:02d}*.fits",
            f"*LAT*{year}{month:02d}{day:02d}*.fits"
        ]
        
        downloaded_files = []
        
        for pattern in file_patterns:
            try:
                print(f"🔍 Cercando pattern: {pattern}")
                
                # In un'implementazione completa, qui faremmo il parsing della directory
                # Per ora simuliamo la ricerca
                print(f"   ℹ️  Pattern richiede parsing HTML avanzato della directory")
                
            except Exception as e:
                print(f"   ❌ Errore ricerca: {e}")
        
        return downloaded_files
    
    def download_swift_bat_raw_data(self, grb_info):
        """Scarica dati grezzi Swift BAT."""
        grb_name = grb_info.get('grb_name', 'Unknown')
        date = grb_info['date']
        
        print(f"\n📡 SCARICANDO SWIFT BAT RAW DATA - {grb_name}")
        print("=" * 50)
        
        year = date[:4]
        month = int(date[5:7])
        day = int(date[8:10])
        
        # URL base per dati Swift
        base_url = f"https://swift.gsfc.nasa.gov/archive/swift/bat/trigger_{year}{month:02d}{day:02d}/"
        
        print(f"🔍 URL base: {base_url}")
        
        # File Swift BAT tipici
        file_types = ['bat', 'evt', 'hkw', 'rate']
        
        downloaded_files = []
        
        for file_type in file_types:
            try:
                print(f"🔍 Cercando file {file_type}...")
                
                # Pattern di ricerca
                pattern = f"sw{year}{month:02d}{day:02d}*_{file_type}_*.fits"
                print(f"   Pattern: {pattern}")
                
                # Simula ricerca (richiederebbe parsing HTML)
                print(f"   ℹ️  Richiede parsing HTML della directory Swift")
                
            except Exception as e:
                print(f"   ❌ Errore ricerca {file_type}: {e}")
        
        return downloaded_files
    
    def download_magic_raw_data(self, grb_info):
        """Scarica dati grezzi MAGIC."""
        grb_name = grb_info.get('grb_name', 'Unknown')
        
        print(f"\n📡 SCARICANDO MAGIC RAW DATA - {grb_name}")
        print("=" * 50)
        
        # MAGIC ha una struttura diversa
        base_url = "https://magic.mpp.mpg.de/data/"
        
        print(f"🔍 URL base: {base_url}")
        
        downloaded_files = []
        
        try:
            print("🔍 Cercando dati MAGIC...")
            
            # MAGIC richiede spesso registrazione e autenticazione
            print("   ℹ️  MAGIC richiede spesso registrazione per dati grezzi")
            print("   ℹ️  Dati pubblici disponibili solo per eventi specifici")
            
        except Exception as e:
            print(f"   ❌ Errore accesso MAGIC: {e}")
        
        return downloaded_files
    
    def download_all_raw_data(self):
        """Scarica tutti i dati grezzi per i GRB target."""
        print("\n🚀 DOWNLOAD COMPLETO DATI GREZZI REALI")
        print("=" * 60)
        
        # Test accessibilità
        archive_status = self.test_archive_access()
        
        all_downloads = {}
        
        for grb_name, grb_info in self.target_grbs.items():
            print(f"\n🎯 PROCESSANDO {grb_name}")
            print("-" * 40)
            
            grb_info['grb_name'] = grb_name
            grb_downloads = {}
            
            for instrument in grb_info['instruments']:
                try:
                    if instrument == 'fermi_gbm' and archive_status.get('fermi_gbm_base', False):
                        files = self.download_fermi_gbm_raw_data(grb_info)
                        grb_downloads['fermi_gbm'] = files
                    elif instrument == 'fermi_lat' and archive_status.get('fermi_lat_base', False):
                        files = self.download_fermi_lat_raw_data(grb_info)
                        grb_downloads['fermi_lat'] = files
                    elif instrument == 'swift_bat' and archive_status.get('swift_bat_base', False):
                        files = self.download_swift_bat_raw_data(grb_info)
                        grb_downloads['swift_bat'] = files
                    elif instrument == 'magic':
                        files = self.download_magic_raw_data(grb_info)
                        grb_downloads['magic'] = files
                        
                except Exception as e:
                    print(f"   ❌ Errore con {instrument}: {e}")
            
            all_downloads[grb_name] = grb_downloads
            
            total_files = sum(len(files) for files in grb_downloads.values())
            print(f"✅ {grb_name}: {total_files} file recovery")
        
        # Salva metadata
        metadata = {
            'download_time': datetime.now().isoformat(),
            'downloads': all_downloads,
            'archive_status': archive_status,
            'target_grbs': self.target_grbs
        }
        
        metadata_file = os.path.join(self.base_dir, 'raw_download_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        print(f"\n📋 RIEPILOGO DOWNLOAD GREZZI:")
        print(f"   📁 Directory: {self.base_dir}/")
        print(f"   📄 Metadata: {metadata_file}")
        print(f"   🎯 GRB processati: {len(all_downloads)}")
        
        total_files = sum(
            sum(len(files) for files in grb_downloads.values())
            for grb_downloads in all_downloads.values()
        )
        print(f"   📊 File totali scaricati: {total_files}")
        
        return all_downloads
    
    def verify_raw_data_quality(self):
        """Verifica la qualità dei dati grezzi scaricati."""
        print("\n🔍 VERIFICA QUALITÀ DATI GREZZI")
        print("=" * 40)
        
        verification_results = {}
        
        for instrument_dir in self.instrument_dirs.values():
            if os.path.exists(instrument_dir):
                instrument_name = os.path.basename(instrument_dir)
                print(f"\n🔍 Verificando {instrument_name}:")
                
                instrument_results = {}
                
                for filename in os.listdir(instrument_dir):
                    if filename.endswith('.fits'):
                        filepath = os.path.join(instrument_dir, filename)
                        
                        try:
                            with fits.open(filepath) as hdul:
                                # Analisi dettagliata del file
                                file_info = {
                                    'file_size_kb': os.path.getsize(filepath) / 1024,
                                    'n_hdus': len(hdul),
                                    'hdu_info': []
                                }
                                
                                for i, hdu in enumerate(hdul):
                                    hdu_info = {
                                        'hdu_index': i,
                                        'hdu_type': hdu.__class__.__name__,
                                        'has_data': hdu.data is not None
                                    }
                                    
                                    if hdu.data is not None:
                                        hdu_info['data_shape'] = hdu.data.shape
                                        hdu_info['data_dtype'] = str(hdu.data.dtype)
                                        
                                        # Cerca colonne di interesse
                                        if hasattr(hdu.data, 'dtype') and hdu.data.dtype.names:
                                            hdu_info['columns'] = list(hdu.data.dtype.names)
                                    
                                    file_info['hdu_info'].append(hdu_info)
                                
                                instrument_results[filename] = file_info
                                print(f"   ✅ {filename}: {file_info['file_size_kb']:.1f} KB, {len(hdul)} HDUs")
                                
                        except Exception as e:
                            instrument_results[filename] = {'error': str(e)}
                            print(f"   ❌ {filename}: ERRORE - {e}")
                
                verification_results[instrument_name] = instrument_results
        
        # Salva risultati verifica
        verification_file = os.path.join(self.base_dir, 'raw_data_verification.json')
        with open(verification_file, 'w') as f:
            json.dump(verification_results, f, indent=2, default=str)
        
        print(f"\n📄 Verifica salvata: {verification_file}")
        
        return verification_results


def main():
    """Funzione principale per download dati grezzi."""
    print("🔬 RAW DATA DOWNLOADER")
    print("=" * 50)
    print("Autore: Christian Quintino De Luca (RTH Italia)")
    print("Data: 2025-10-20")
    print("=" * 50)
    
    # Inizializza downloader
    downloader = RawDataDownloader()
    
    # Scarica tutti i dati grezzi
    all_downloads = downloader.download_all_raw_data()
    
    # Verifica qualità
    verification_results = downloader.verify_raw_data_quality()
    
    print(f"\n🎉 DOWNLOAD GREZZI COMPLETATO!")
    print(f"📁 Controlla la directory '{downloader.base_dir}/' per i file scaricati")
    
    return all_downloads, verification_results


if __name__ == "__main__":
    main()
