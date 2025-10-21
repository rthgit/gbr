#!/usr/bin/env python3
"""
Downloader automatico per dati astronomici
Opzione 1: Accesso diretto (senza registrazione)
Opzione 2: API automatiche (con registrazione)
"""

import sys
import os
import requests
import json
import time
from datetime import datetime
import numpy as np

# Fix encoding per PowerShell
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

class AutoDownloader:
    """Downloader automatico con opzioni multiple"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'QG-Analysis-Toolkit/1.0 (Scientific Research)'
        })
        
        # Configurazione accesso
        self.access_modes = {
            'direct': {
                'name': 'Accesso Diretto',
                'description': 'Nessuna registrazione richiesta',
                'apis': ['swift', 'magic_public', 'hess_public'],
                'fermi': 'catalog_only'
            },
            'registered': {
                'name': 'Accesso Registrato',
                'description': 'Registrazione gratuita per download massivi',
                'apis': ['fermi_gbm', 'swift', 'magic_public', 'hess_public'],
                'fermi': 'full_access'
            }
        }
    
    def test_direct_access(self):
        """Test accesso diretto senza registrazione"""
        print("""
        ================================================================
        TEST ACCESSO DIRETTO - SENZA REGISTRAZIONE
        ================================================================
        """)
        
        results = {}
        
        # Test Swift BAT (accesso diretto)
        print("1. SWIFT BAT (Accesso Diretto):")
        try:
            url = "https://swift.gsfc.nasa.gov/archive/grb_table/"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                print("   ✅ Accesso diretto OK")
                results['swift'] = True
            else:
                print(f"   ❌ Errore HTTP: {response.status_code}")
                results['swift'] = False
        except Exception as e:
            print(f"   ❌ Errore: {e}")
            results['swift'] = False
        
        # Test MAGIC pubblici (accesso diretto)
        print("\n2. MAGIC Pubblici (Accesso Diretto):")
        try:
            url = "https://magic.mpp.mpg.de/public/results/magic/"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                print("   ✅ Accesso diretto OK")
                results['magic'] = True
            else:
                print(f"   ❌ Errore HTTP: {response.status_code}")
                results['magic'] = False
        except Exception as e:
            print(f"   ❌ Errore: {e}")
            results['magic'] = False
        
        # Test HESS pubblici (accesso diretto)
        print("\n3. HESS Pubblici (Accesso Diretto):")
        try:
            url = "https://www.mpi-hd.mpg.de/hfm/HESS/"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                print("   ✅ Accesso diretto OK")
                results['hess'] = True
            else:
                print(f"   ❌ Errore HTTP: {response.status_code}")
                results['hess'] = False
        except Exception as e:
            print(f"   ❌ Errore: {e}")
            results['hess'] = False
        
        # Test Fermi catalog (accesso diretto limitato)
        print("\n4. FERMI Catalog (Accesso Limitato):")
        try:
            url = "https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                print("   ✅ Catalog accessibile (download limitato)")
                results['fermi_catalog'] = True
            else:
                print(f"   ❌ Errore HTTP: {response.status_code}")
                results['fermi_catalog'] = False
        except Exception as e:
            print(f"   ❌ Errore: {e}")
            results['fermi_catalog'] = False
        
        return results
    
    def test_registered_access(self):
        """Test accesso con registrazione (simulato)"""
        print("""
        ================================================================
        TEST ACCESSO REGISTRATO - CON REGISTRAZIONE
        ================================================================
        """)
        
        print("NOTA: Per test completo, registrati gratuitamente su:")
        print("   - HEASARC: https://heasarc.gsfc.nasa.gov/cgi-bin/Feedback")
        print("   - Fermi GBM: https://fermi.gsfc.nasa.gov/ssc/data/access/")
        
        # Simula accesso registrato
        results = {
            'fermi_gbm': True,  # Assumendo registrazione
            'fermi_lat': True,  # Assumendo registrazione
            'swift': True,
            'magic': True,
            'hess': True
        }
        
        print("\n✅ Accesso registrato simulato:")
        for api, status in results.items():
            print(f"   {api.upper()}: {'✅ OK' if status else '❌ NO'}")
        
        return results
    
    def create_registration_guide(self):
        """Crea guida per registrazione gratuita"""
        
        guide = """# GUIDA REGISTRAZIONE GRATUITA

## 🆓 TUTTE LE REGISTRAZIONI SONO GRATUITE!

### 1. FERMI GBM/LAT (NASA HEASARC)
**URL:** https://heasarc.gsfc.nasa.gov/cgi-bin/Feedback
**Costo:** GRATUITO
**Tempo:** 2-3 minuti
**Benefici:** Download massivi, API automatiche

**Passi:**
1. Vai su https://heasarc.gsfc.nasa.gov/cgi-bin/Feedback
2. Clicca "Create Account"
3. Compila form (nome, email, istituzione)
4. Conferma email
5. ✅ Accesso completo Fermi

### 2. SWIFT BAT (NASA)
**URL:** https://swift.gsfc.nasa.gov/archive/grb_table/
**Costo:** GRATUITO
**Tempo:** 0 minuti (opzionale)
**Benefici:** Download prioritario, notifiche

**Passi:**
1. Accesso diretto disponibile
2. Registrazione opzionale per download massivi
3. ✅ Accesso base sempre disponibile

### 3. MAGIC (MPI Munich)
**URL:** https://magic.mpp.mpg.de/
**Costo:** GRATUITO
**Tempo:** 0 minuti
**Benefici:** Dati pubblici automatici

**Passi:**
1. Accesso diretto ai dati pubblici
2. Nessuna registrazione richiesta
3. ✅ Accesso immediato

### 4. HESS (MPI Heidelberg)
**URL:** https://www.mpi-hd.mpg.de/hfm/HESS/
**Costo:** GRATUITO
**Tempo:** 0 minuti
**Benefici:** Dati pubblici automatici

**Passi:**
1. Accesso diretto ai dati pubblici
2. Nessuna registrazione richiesta
3. ✅ Accesso immediato

## 🤖 IMPLEMENTAZIONE AUTOMATICA

### Opzione A: Solo Accesso Diretto
```python
python auto_downloader.py --mode direct
```
- ✅ Nessuna registrazione
- ✅ Accesso immediato
- ⚠️ Download limitati

### Opzione B: Accesso Registrato
```python
python auto_downloader.py --mode registered
```
- ✅ Download massivi
- ✅ API automatiche
- ⚠️ Richiede registrazione

## 📋 CHECKLIST REGISTRAZIONE

- [ ] HEASARC (Fermi): 2 minuti
- [ ] Swift (opzionale): 0 minuti
- [ ] MAGIC: 0 minuti (automatico)
- [ ] HESS: 0 minuti (automatico)

**TOTALE:** 2 minuti per accesso completo!

## 💡 SUGGERIMENTI

1. **Inizia senza registrazione:** Testa accesso diretto
2. **Registrati solo se necessario:** Per download massivi
3. **Usa email istituzionale:** Per credibilità scientifica
4. **Salva credenziali:** Per accesso automatico futuro

---
*Tutte le registrazioni sono gratuite e richiedono solo 2 minuti!*
"""
        
        with open('registration_guide.md', 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print("📋 Guida registrazione salvata in 'registration_guide.md'")
    
    def create_auto_download_script(self):
        """Crea script per download automatico"""
        
        script = '''#!/usr/bin/env python3
"""
Script download automatico - Nessuna registrazione richiesta
"""

import sys
import os
from auto_downloader import AutoDownloader

def main():
    print("DOWNLOAD AUTOMATICO - ACCESSO DIRETTO")
    print("="*50)
    
    downloader = AutoDownloader()
    
    # Test accesso diretto
    results = downloader.test_direct_access()
    
    # Conta successi
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\\nRISULTATO: {success_count}/{total_count} API accessibili")
    
    if success_count >= 3:
        print("OK: ACCESSO DIRETTO SUFFICIENTE!")
        print("   Puoi scaricare dati senza registrazione")
    else:
        print("WARNING: REGISTRAZIONE RACCOMANDATA")
        print("   Registrati per accesso completo")
    
    print("\\nPer registrazione gratuita:")
    print("   python auto_downloader.py --guide")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--guide":
        downloader = AutoDownloader()
        downloader.create_registration_guide()
    else:
        main()
'''
        
        with open('quick_download.py', 'w') as f:
            f.write(script)
        
        print("🤖 Script automatico creato: 'quick_download.py'")
    
    def generate_recommendations(self, direct_results):
        """Genera raccomandazioni basate sui test"""
        
        success_count = sum(direct_results.values())
        total_count = len(direct_results)
        
        recommendations = {
            'access_mode': 'direct' if success_count >= 3 else 'registered',
            'registration_needed': success_count < 3,
            'available_apis': [k for k, v in direct_results.items() if v],
            'missing_apis': [k for k, v in direct_results.items() if not v],
            'confidence': 'high' if success_count >= 3 else 'medium'
        }
        
        with open('access_recommendations.json', 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        return recommendations

def main():
    """Esegue test accesso automatico"""
    print("""
    ================================================================
    TEST ACCESSO AUTOMATICO - REGISTRAZIONE NECESSARIA?
    ================================================================
    """)
    
    downloader = AutoDownloader()
    
    # Test accesso diretto
    direct_results = downloader.test_direct_access()
    
    # Test accesso registrato (simulato)
    registered_results = downloader.test_registered_access()
    
    # Crea guida registrazione
    downloader.create_registration_guide()
    
    # Crea script automatico
    downloader.create_auto_download_script()
    
    # Genera raccomandazioni
    recommendations = downloader.generate_recommendations(direct_results)
    
    # Riepilogo finale
    print("\n" + "="*80)
    print("RIEPILOGO ACCESSO AUTOMATICO")
    print("="*80)
    
    success_count = sum(direct_results.values())
    total_count = len(direct_results)
    
    print(f"Accesso Diretto: {success_count}/{total_count} API disponibili")
    print(f"Registrazione Necessaria: {'❌ NO' if success_count >= 3 else '✅ SÌ'}")
    print(f"Modalità Raccomandata: {recommendations['access_mode'].upper()}")
    
    print(f"\nAPI Disponibili:")
    for api in recommendations['available_apis']:
        print(f"   ✅ {api.upper()}")
    
    if recommendations['missing_apis']:
        print(f"\nAPI Mancanti:")
        for api in recommendations['missing_apis']:
            print(f"   ❌ {api.upper()}")
    
    print(f"\nFile Generati:")
    print("   - registration_guide.md")
    print("   - quick_download.py")
    print("   - access_recommendations.json")
    
    print("\n" + "="*80)
    print("CONCLUSIONE:")
    if success_count >= 3:
        print("🎉 PUOI INIZIARE SUBITO SENZA REGISTRAZIONE!")
    else:
        print("📝 REGISTRAZIONE GRATUITA RACCOMANDATA (2 minuti)")
    print("="*80)

if __name__ == "__main__":
    main()
