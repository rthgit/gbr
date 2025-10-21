#!/usr/bin/env python3
"""
Downloader GRATUITO per dati astronomici reali
Fermi GBM/LAT, Swift BAT, MAGIC - API pubbliche gratuite
"""

import sys
import os
import requests
import json
import time
from datetime import datetime, timedelta
import numpy as np

# Fix encoding per PowerShell
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

class FreeAPIDownloader:
    """Downloader gratuito per dati astronomici reali"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QG-Analysis-Toolkit/1.0 (Scientific Research)'
        })
        
        # API endpoints GRATUITI
        self.apis = {
            'fermi_gbm': {
                'base_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/',
                'free': True,
                'description': 'Fermi GBM TTE data (NASA)'
            },
            'swift_bat': {
                'base_url': 'https://swift.gsfc.nasa.gov/archive/grb_table/',
                'free': True,
                'description': 'Swift BAT catalog (NASA)'
            },
            'magic_public': {
                'base_url': 'https://magic.mpp.mpg.de/public/results/magic/',
                'free': True,
                'description': 'MAGIC public results'
            },
            'hess_public': {
                'base_url': 'https://www.mpi-hd.mpg.de/hfm/HESS/',
                'free': True,
                'description': 'HESS public data'
            }
        }
    
    def check_api_availability(self):
        """Verifica disponibilità API gratuite"""
        print("VERIFICA DISPONIBILITÀ API GRATUITE")
        print("="*50)
        
        available_apis = {}
        
        for name, api in self.apis.items():
            print(f"\n{name.upper()}:")
            print(f"  URL: {api['base_url']}")
            print(f"  Gratuito: {'✅ SÌ' if api['free'] else '❌ NO'}")
            print(f"  Descrizione: {api['description']}")
            
            # Test connessione
            try:
                response = self.session.get(api['base_url'], timeout=10)
                if response.status_code == 200:
                    print(f"  Stato: ✅ ONLINE")
                    available_apis[name] = api
                else:
                    print(f"  Stato: ⚠️ HTTP {response.status_code}")
            except Exception as e:
                print(f"  Stato: ❌ OFFLINE ({str(e)[:50]}...)")
        
        return available_apis
    
    def download_fermi_catalog(self):
        """Scarica catalogo Fermi GRB (GRATUITO)"""
        print("\n" + "="*60)
        print("DOWNLOAD CATALOGO FERMI GRB (GRATUITO)")
        print("="*60)
        
        # URL catalogo Fermi pubblico
        catalog_url = "https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/"
        
        try:
            print("Connessione a Fermi GBM catalog...")
            response = self.session.get(catalog_url, timeout=30)
            
            if response.status_code == 200:
                print("✅ Catalogo Fermi accessibile")
                
                # Salva informazioni catalogo
                catalog_info = {
                    'url': catalog_url,
                    'status': 'accessible',
                    'timestamp': datetime.now().isoformat(),
                    'description': 'Fermi GBM burst catalog - NASA HEASARC'
                }
                
                with open('free_apis/fermi_catalog_info.json', 'w') as f:
                    json.dump(catalog_info, f, indent=2)
                
                print("📁 Informazioni catalogo salvate in 'free_apis/fermi_catalog_info.json'")
                return True
            else:
                print(f"❌ Errore HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Errore connessione: {e}")
            return False
    
    def download_swift_catalog(self):
        """Scarica catalogo Swift GRB (GRATUITO)"""
        print("\n" + "="*60)
        print("DOWNLOAD CATALOGO SWIFT GRB (GRATUITO)")
        print("="*60)
        
        # URL catalogo Swift pubblico
        catalog_url = "https://swift.gsfc.nasa.gov/archive/grb_table/"
        
        try:
            print("Connessione a Swift BAT catalog...")
            response = self.session.get(catalog_url, timeout=30)
            
            if response.status_code == 200:
                print("✅ Catalogo Swift accessibile")
                
                # Salva informazioni catalogo
                catalog_info = {
                    'url': catalog_url,
                    'status': 'accessible',
                    'timestamp': datetime.now().isoformat(),
                    'description': 'Swift BAT GRB catalog - NASA'
                }
                
                with open('free_apis/swift_catalog_info.json', 'w') as f:
                    json.dump(catalog_info, f, indent=2)
                
                print("📁 Informazioni catalogo salvate in 'free_apis/swift_catalog_info.json'")
                return True
            else:
                print(f"❌ Errore HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Errore connessione: {e}")
            return False
    
    def download_magic_public_data(self):
        """Scarica dati pubblici MAGIC (GRATUITO)"""
        print("\n" + "="*60)
        print("DOWNLOAD DATI PUBBLICI MAGIC (GRATUITO)")
        print("="*60)
        
        # URL dati pubblici MAGIC
        public_url = "https://magic.mpp.mpg.de/public/results/magic/"
        
        try:
            print("Connessione a MAGIC public data...")
            response = self.session.get(public_url, timeout=30)
            
            if response.status_code == 200:
                print("✅ Dati MAGIC pubblici accessibili")
                
                # Salva informazioni
                magic_info = {
                    'url': public_url,
                    'status': 'accessible',
                    'timestamp': datetime.now().isoformat(),
                    'description': 'MAGIC public results - MPI Munich',
                    'note': 'Dati pubblici disponibili dopo embargo 1-2 anni'
                }
                
                with open('free_apis/magic_public_info.json', 'w') as f:
                    json.dump(magic_info, f, indent=2)
                
                print("📁 Informazioni MAGIC salvate in 'free_apis/magic_public_info.json'")
                return True
            else:
                print(f"❌ Errore HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Errore connessione: {e}")
            return False
    
    def create_download_instructions(self):
        """Crea istruzioni dettagliate per download manuale"""
        
        instructions = """# ISTRUZIONI DOWNLOAD DATI GRATUITI

## 🆓 TUTTI I DATI SONO GRATUITI PER RICERCA SCIENTIFICA

### 1. FERMI GBM/LAT (NASA)
**URL:** https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/
**Costo:** GRATUITO
**Registrazione:** Opzionale (solo per download massivi)

**GRB Target:**
- GRB080916C: 2008/090916/
- GRB130427A: 2013/130427/
- GRB090510: 2009/090510/

**File da scaricare:**
- glg_tte_n0_[GRB]_v00.fit (TTE data)
- glg_tte_n1_[GRB]_v00.fit (TTE data)
- glg_cspec_[GRB]_v00.pha (Spectrum)

### 2. SWIFT BAT (NASA)
**URL:** https://swift.gsfc.nasa.gov/archive/grb_table/
**Costo:** GRATUITO
**Registrazione:** Non richiesta

**Dati disponibili:**
- BAT event files
- Light curves
- Spectra
- Position data

### 3. MAGIC (MPI Munich)
**URL:** https://magic.mpp.mpg.de/public/results/magic/
**Costo:** GRATUITO
**Registrazione:** Non richiesta

**Dati disponibili:**
- Public results
- Published FITS files
- Analysis results

### 4. HESS (MPI Heidelberg)
**URL:** https://www.mpi-hd.mpg.de/hfm/HESS/
**Costo:** GRATUITO
**Registrazione:** Non richiesta

## 📋 PROCEDURA DOWNLOAD

### Step 1: Crea cartelle
```
mkdir free_data/fermi
mkdir free_data/swift
mkdir free_data/magic
mkdir free_data/hess
```

### Step 2: Download manuale
1. Vai agli URL sopra
2. Naviga alle cartelle GRB specifici
3. Scarica file FITS
4. Salva in cartelle appropriate

### Step 3: Analisi automatica
```python
python test.py  # Analizza dati scaricati
```

## 💡 SUGGERIMENTI

1. **Inizia con Fermi:** Più facile da scaricare
2. **Usa browser:** Per navigazione catalogo
3. **Verifica FITS:** Controlla che file siano validi
4. **Backup dati:** Salva copie locali

## 🔗 LINK UTILI

- [Fermi GBM Catalog](https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/)
- [Swift GRB Table](https://swift.gsfc.nasa.gov/archive/grb_table/)
- [MAGIC Results](https://magic.mpp.mpg.de/public/results/magic/)
- [HESS Data](https://www.mpi-hd.mpg.de/hfm/HESS/)

---
*Tutti i dati sono gratuiti per uso scientifico e educativo*
"""
        
        with open('free_apis/DOWNLOAD_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print("📋 Istruzioni dettagliate salvate in 'free_apis/DOWNLOAD_INSTRUCTIONS.md'")
    
    def generate_cost_analysis(self):
        """Genera analisi costi per implementazione completa"""
        
        cost_analysis = {
            'data_acquisition': {
                'fermi_gbm': {'cost': 0, 'currency': 'EUR', 'note': 'Gratuito - NASA'},
                'swift_bat': {'cost': 0, 'currency': 'EUR', 'note': 'Gratuito - NASA'},
                'magic_public': {'cost': 0, 'currency': 'EUR', 'note': 'Gratuito - MPI'},
                'hess_public': {'cost': 0, 'currency': 'EUR', 'note': 'Gratuito - MPI'}
            },
            'storage': {
                'local_storage': {'cost': 0, 'currency': 'EUR', 'note': 'Disco locale'},
                'cloud_storage': {'cost': 5, 'currency': 'EUR/month', 'note': 'Opzionale - AWS/Azure'}
            },
            'processing': {
                'local_cpu': {'cost': 0, 'currency': 'EUR', 'note': 'Computer locale'},
                'cloud_compute': {'cost': 10, 'currency': 'EUR/month', 'note': 'Opzionale - HPC'}
            },
            'total_monthly': {
                'minimum': 0,
                'recommended': 15,
                'premium': 50,
                'currency': 'EUR'
            }
        }
        
        with open('free_apis/cost_analysis.json', 'w') as f:
            json.dump(cost_analysis, f, indent=2)
        
        print("💰 Analisi costi salvata in 'free_apis/cost_analysis.json'")
        return cost_analysis

def main():
    """Esegue downloader API gratuite"""
    print("""
    ================================================================
    DOWNLOADER API GRATUITE - DATI ASTRONOMICI
    ================================================================
    Fermi, Swift, MAGIC, HESS - TUTTO GRATUITO!
    ================================================================
    """)
    
    # Crea cartelle
    os.makedirs('free_apis', exist_ok=True)
    os.makedirs('free_data', exist_ok=True)
    
    downloader = FreeAPIDownloader()
    
    # 1. Verifica API disponibili
    available_apis = downloader.check_api_availability()
    
    # 2. Test download cataloghi
    print("\n" + "="*60)
    print("TEST DOWNLOAD CATALOGHI GRATUITI")
    print("="*60)
    
    fermi_ok = downloader.download_fermi_catalog()
    swift_ok = downloader.download_swift_catalog()
    magic_ok = downloader.download_magic_public_data()
    
    # 3. Crea istruzioni dettagliate
    downloader.create_download_instructions()
    
    # 4. Analisi costi
    cost_analysis = downloader.generate_cost_analysis()
    
    # Riepilogo finale
    print("\n" + "="*80)
    print("RIEPILOGO API GRATUITE")
    print("="*80)
    print(f"✅ Fermi GBM: {'Disponibile' if fermi_ok else 'Non disponibile'}")
    print(f"✅ Swift BAT: {'Disponibile' if swift_ok else 'Non disponibile'}")
    print(f"✅ MAGIC: {'Disponibile' if magic_ok else 'Non disponibile'}")
    print(f"💰 Costo totale: {cost_analysis['total_monthly']['minimum']} EUR/mese")
    print("\n📁 File generati in 'free_apis/':")
    print("   - DOWNLOAD_INSTRUCTIONS.md")
    print("   - cost_analysis.json")
    print("   - fermi_catalog_info.json")
    print("   - swift_catalog_info.json")
    print("   - magic_public_info.json")
    print("="*80)

if __name__ == "__main__":
    main()
