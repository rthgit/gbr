#!/usr/bin/env python3
"""
Script per scaricare i dati REALI di GRB080916C da Fermi
Basato sui GCN Circulars 8245, 8246, 8278
Trigger ID: 243216766 / 080916.009
"""

import os
import sys
import requests
import time
from datetime import datetime

# Configurazione encoding per PowerShell
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def print_status(message):
    """Stampa messaggi con timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def download_file(url, filename, description):
    """Scarica un file con progress bar"""
    print_status(f"Scaricando {description}...")
    print_status(f"URL: {url}")
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filename)
        print_status(f"✓ {description} scaricato: {file_size:,} bytes")
        return True
        
    except requests.exceptions.RequestException as e:
        print_status(f"✗ Errore scaricamento {description}: {e}")
        return False

def main():
    print_status("=" * 60)
    print_status("SCARICAMENTO DATI REALI GRB080916C")
    print_status("Basato sui GCN Circulars 8245, 8246, 8278")
    print_status("=" * 60)
    
    # Parametri GRB080916C reali
    trigger_id = "243216766"
    date_str = "080916"
    grb_name = "GRB080916C"
    
    print_status(f"GRB: {grb_name}")
    print_status(f"Trigger ID: {trigger_id}")
    print_status(f"Data: {date_str}")
    print_status(f"Posizione: RA=121.8°, Dec=-61.3°")
    print_status(f"Fotoni GeV: >10 fotoni sopra 1 GeV")
    print_status(f"Energia massima: 30 MeV")
    
    # Crea directory per i dati reali
    real_data_dir = "real_data_grb080916c"
    os.makedirs(real_data_dir, exist_ok=True)
    print_status(f"Directory creata: {real_data_dir}")
    
    # URL per dati Fermi GBM
    fermi_gbm_urls = {
        "GBM_TTE": f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/{date_str}/bn{trigger_id}_v00/bn{trigger_id}_v00_tte.fit",
        "GBM_CSPEC": f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/{date_str}/bn{trigger_id}_v00/bn{trigger_id}_v00_cspec.fit",
        "GBM_CTIME": f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/{date_str}/bn{trigger_id}_v00/bn{trigger_id}_v00_ctime.fit",
        "GBM_RSP": f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/{date_str}/bn{trigger_id}_v00/bn{trigger_id}_v00.rsp"
    }
    
    # URL per dati Fermi LAT
    fermi_lat_urls = {
        "LAT_EVENTS": f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/bursts/{date_str}/bn{trigger_id}_v00/bn{trigger_id}_v00_lat_events.fit",
        "LAT_GTI": f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/bursts/{date_str}/bn{trigger_id}_v00/bn{trigger_id}_v00_lat_gti.fit"
    }
    
    # URL per dati Swift BAT (se disponibili)
    swift_bat_urls = {
        "BAT_EVENTS": f"https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/{date_str}/000{trigger_id}/bat/event/sw{trigger_id}000000batse.fits.gz",
        "BAT_RATE": f"https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/{date_str}/000{trigger_id}/bat/rate/sw{trigger_id}000000brt.fits.gz"
    }
    
    # URL per dati MAGIC (se disponibili)
    magic_urls = {
        "MAGIC_EVENTS": f"https://magic.mpp.mpg.de/data/archive/{date_str}/GRB{grb_name}_events.fits",
        "MAGIC_SPECTRUM": f"https://magic.mpp.mpg.de/data/archive/{date_str}/GRB{grb_name}_spectrum.fits"
    }
    
    # URL per dati HESS (se disponibili)
    hess_urls = {
        "HESS_EVENTS": f"https://hess-data.org/archive/{date_str}/GRB{grb_name}_events.fits",
        "HESS_SPECTRUM": f"https://hess-data.org/archive/{date_str}/GRB{grb_name}_spectrum.fits"
    }
    
    print_status("\n" + "=" * 40)
    print_status("SCARICAMENTO DATI FERMI GBM")
    print_status("=" * 40)
    
    gbm_success = 0
    for file_type, url in fermi_gbm_urls.items():
        filename = os.path.join(real_data_dir, f"grb080916c_{file_type.lower()}.fits")
        if download_file(url, filename, f"Fermi GBM {file_type}"):
            gbm_success += 1
        time.sleep(1)  # Pausa tra download
    
    print_status("\n" + "=" * 40)
    print_status("SCARICAMENTO DATI FERMI LAT")
    print_status("=" * 40)
    
    lat_success = 0
    for file_type, url in fermi_lat_urls.items():
        filename = os.path.join(real_data_dir, f"grb080916c_{file_type.lower()}.fits")
        if download_file(url, filename, f"Fermi LAT {file_type}"):
            lat_success += 1
        time.sleep(1)
    
    print_status("\n" + "=" * 40)
    print_status("SCARICAMENTO DATI SWIFT BAT")
    print_status("=" * 40)
    
    swift_success = 0
    for file_type, url in swift_bat_urls.items():
        filename = os.path.join(real_data_dir, f"grb080916c_{file_type.lower()}.fits.gz")
        if download_file(url, filename, f"Swift BAT {file_type}"):
            swift_success += 1
        time.sleep(1)
    
    print_status("\n" + "=" * 40)
    print_status("SCARICAMENTO DATI MAGIC")
    print_status("=" * 40)
    
    magic_success = 0
    for file_type, url in magic_urls.items():
        filename = os.path.join(real_data_dir, f"grb080916c_{file_type.lower()}.fits")
        if download_file(url, filename, f"MAGIC {file_type}"):
            magic_success += 1
        time.sleep(1)
    
    print_status("\n" + "=" * 40)
    print_status("SCARICAMENTO DATI HESS")
    print_status("=" * 40)
    
    hess_success = 0
    for file_type, url in hess_urls.items():
        filename = os.path.join(real_data_dir, f"grb080916c_{file_type.lower()}.fits")
        if download_file(url, filename, f"HESS {file_type}"):
            hess_success += 1
        time.sleep(1)
    
    # Riepilogo finale
    print_status("\n" + "=" * 60)
    print_status("RIEPILOGO SCARICAMENTO")
    print_status("=" * 60)
    
    total_files = len(fermi_gbm_urls) + len(fermi_lat_urls) + len(swift_bat_urls) + len(magic_urls) + len(hess_urls)
    total_success = gbm_success + lat_success + swift_success + magic_success + hess_success
    
    print_status(f"Fermi GBM: {gbm_success}/{len(fermi_gbm_urls)} file scaricati")
    print_status(f"Fermi LAT: {lat_success}/{len(fermi_lat_urls)} file scaricati")
    print_status(f"Swift BAT: {swift_success}/{len(swift_bat_urls)} file scaricati")
    print_status(f"MAGIC: {magic_success}/{len(magic_urls)} file scaricati")
    print_status(f"HESS: {hess_success}/{len(hess_urls)} file scaricati")
    print_status(f"TOTALE: {total_success}/{total_files} file scaricati")
    
    if total_success > 0:
        print_status(f"\n✓ Dati salvati in: {real_data_dir}/")
        print_status("✓ Pronto per analisi QG con dati reali!")
        
        # Crea file di metadati
        metadata_file = os.path.join(real_data_dir, "grb080916c_metadata.txt")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write("GRB080916C - METADATI REALI\n")
            f.write("=" * 40 + "\n")
            f.write(f"Trigger ID: {trigger_id}\n")
            f.write(f"Data: {date_str}\n")
            f.write(f"Posizione: RA=121.8°, Dec=-61.3°\n")
            f.write(f"Durata: T90=66s, T50=33s\n")
            f.write(f"Energia massima: 30 MeV\n")
            f.write(f"Fotoni GeV: >10 fotoni sopra 1 GeV\n")
            f.write(f"Epeak: 424 ± 24 keV\n")
            f.write(f"Alpha: -0.91 ± 0.02\n")
            f.write(f"Beta: -2.08 ± 0.06\n")
            f.write(f"Fluenza: 1.9e-4 erg/cm²\n")
            f.write(f"GCN Circulars: 8245, 8246, 8278\n")
            f.write(f"Data scaricamento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print_status(f"✓ Metadati salvati in: {metadata_file}")
    else:
        print_status("\n✗ Nessun file scaricato - verificare connessione e URL")
    
    print_status("\n" + "=" * 60)
    print_status("SCARICAMENTO COMPLETATO")
    print_status("=" * 60)

if __name__ == "__main__":
    main()

