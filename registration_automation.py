#!/usr/bin/env python3
"""
=============================================================================
REGISTRATION AUTOMATION - Automazione Registrazione Archivi
=============================================================================
Script per automatizzare la registrazione agli archivi astronomici ufficiali.
Genera link diretti e template email per facilitare la registrazione.

AUTORE: Christian Quintino De Luca (RTH Italia)
DATA: 2025-10-20
"""

import webbrowser
import os
import sys
from datetime import datetime

# Configurazione encoding per Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

class RegistrationAutomation:
    """Automazione per registrazione archivi astronomici."""
    
    def __init__(self):
        self.registration_urls = {
            'nasa_heasarc': 'https://heasarc.gsfc.nasa.gov/',
            'fermi_data': 'https://fermi.gsfc.nasa.gov/ssc/data/',
            'swift_data': 'https://swift.gsfc.nasa.gov/archive/',
            'magic_contact': 'data@magic.mpp.mpg.de',
            'hess_contact': 'hess-data@mpi-hd.mpg.de'
        }
        
        self.researcher_info = {
            'name': 'Christian Quintino De Luca',
            'email': 'info@rthitalia.com',
            'affiliation': 'RTH Italia (Independent Research)',
            'research_focus': 'Quantum Gravity phenomenology in GRB'
        }
        
        print("🔐 REGISTRATION AUTOMATION INIZIALIZZATO")
        print("=" * 50)
        print(f"👤 Ricercatore: {self.researcher_info['name']}")
        print(f"📧 Email: {self.researcher_info['email']}")
        print(f"🏢 Affiliazione: {self.researcher_info['affiliation']}")
    
    def open_registration_pages(self):
        """Apre le pagine di registrazione nei browser."""
        print("\n🌐 APERTURA PAGINE REGISTRAZIONE")
        print("=" * 40)
        
        pages = [
            ('NASA HEASARC', self.registration_urls['nasa_heasarc']),
            ('Fermi Data Access', self.registration_urls['fermi_data']),
            ('Swift Archive', self.registration_urls['swift_data'])
        ]
        
        for name, url in pages:
            try:
                print(f"🔍 Aprendo {name}: {url}")
                webbrowser.open(url)
                print(f"   ✅ Aperto nel browser")
            except Exception as e:
                print(f"   ❌ Errore: {e}")
    
    def generate_email_templates(self):
        """Genera template email per registrazione."""
        print("\n📧 GENERAZIONE TEMPLATE EMAIL")
        print("=" * 40)
        
        # Template per MAGIC
        magic_email = f"""
Subject: Data Access Request - GRB190114C for Quantum Gravity Research

Dear MAGIC Collaboration,

I am writing to request access to GRB190114C data for research on quantum gravity phenomenology.

Researcher: {self.researcher_info['name']}
Affiliation: {self.researcher_info['affiliation']}
Email: {self.researcher_info['email']}

Research Objective: 
- Analysis of photon time-of-flight delays
- Search for quantum gravity effects at TeV energies
- Comparison with theoretical predictions

I am particularly interested in:
- Time-tagged event data
- Energy spectra
- Temporal profiles

Please let me know the procedure for data access.

Best regards,
{self.researcher_info['name']}
"""
        
        # Template per HESS
        hess_email = f"""
Subject: Data Access Request - GRB Observations for QG Research

Dear HESS Collaboration,

I am requesting access to GRB data for quantum gravity phenomenology research.

Researcher: {self.researcher_info['name']}
Affiliation: {self.researcher_info['affiliation']}
Email: {self.researcher_info['email']}

Research Focus:
- Quantum gravity effects in gamma-ray bursts
- Photon time-of-flight analysis
- Lorentz invariance violation tests

I would appreciate information about:
- Available GRB datasets
- Access procedures
- Data formats

Thank you for your consideration.

Best regards,
{self.researcher_info['name']}
"""
        
        # Salva template
        with open('magic_registration_email.txt', 'w', encoding='utf-8') as f:
            f.write(magic_email)
        
        with open('hess_registration_email.txt', 'w', encoding='utf-8') as f:
            f.write(hess_email)
        
        print("   ✅ Template salvati:")
        print("      📄 magic_registration_email.txt")
        print("      📄 hess_registration_email.txt")
        
        return magic_email, hess_email
    
    def create_registration_checklist(self):
        """Crea checklist per registrazione."""
        print("\n📋 CREAZIONE CHECKLIST REGISTRAZIONE")
        print("=" * 45)
        
        checklist_content = f"""
# ✅ CHECKLIST REGISTRAZIONE ARCHIVI ASTRONOMICI

**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Ricercatore:** {self.researcher_info['name']}
**Email:** {self.researcher_info['email']}

## 🌐 NASA HEASARC (Fermi + Swift)
- [ ] Registrato su https://heasarc.gsfc.nasa.gov/
- [ ] Account verificato via email
- [ ] Accesso a Fermi data granted
- [ ] Accesso a Swift data granted
- [ ] Scaricato GRB080916C data
- [ ] Scaricato GRB130427A data
- [ ] Scaricato GRB090510 data
- [ ] Scaricato GRB190114C data

## 🔭 MAGIC (MPP Munich)
- [ ] Email inviata a data@magic.mpp.mpg.de
- [ ] Risposta ricevuta
- [ ] Credenziali fornite
- [ ] Accesso a GRB190114C data
- [ ] Dati scaricati

## 🌟 HESS (MPI Heidelberg)
- [ ] Email inviata a hess-data@mpi-hd.mpg.de
- [ ] Risposta ricevuta
- [ ] Accesso accordato
- [ ] Dati scaricati

## 📊 DATI OTTENUTI
- [ ] Fermi GBM: GRB080916C, GRB130427A, GRB090510, GRB190114C
- [ ] Fermi LAT: GRB080916C, GRB130427A, GRB090510, GRB190114C
- [ ] Swift BAT: GRB130427A
- [ ] MAGIC: GRB190114C

## 🔬 ANALISI
- [ ] Dati caricati nel sistema
- [ ] Analisi QG eseguita
- [ ] Risultati validati
- [ ] Paper preparato

## 📝 PUBBLICAZIONE
- [ ] Paper scritto
- [ ] Peer review
- [ ] Sottomesso a rivista
- [ ] Pubblicato

---
*Checklist generata automaticamente per {self.researcher_info['name']}*
"""
        
        with open('REGISTRATION_CHECKLIST.md', 'w', encoding='utf-8') as f:
            f.write(checklist_content)
        
        print("   ✅ Checklist salvata: REGISTRATION_CHECKLIST.md")
        
        return checklist_content
    
    def generate_download_script(self):
        """Genera script per download automatico dopo registrazione."""
        print("\n📥 GENERAZIONE SCRIPT DOWNLOAD")
        print("=" * 35)
        
        download_script = f'''#!/usr/bin/env python3
"""
Script per download automatico dati GRB dopo registrazione.
Da eseguire dopo aver ottenuto le credenziali.
"""

import requests
import os
from datetime import datetime

class GRBDataDownloader:
    def __init__(self):
        self.base_dir = 'official_grb_data'
        os.makedirs(self.base_dir, exist_ok=True)
        
        # GRB target
        self.target_grbs = {{
            'GRB080916C': {{
                'trigger_id': '080916409',
                'date': '2008-09-16',
                'redshift': 4.35,
                'max_energy': 13.2
            }},
            'GRB130427A': {{
                'trigger_id': '130427324', 
                'date': '2013-04-27',
                'redshift': 0.34,
                'max_energy': 95.0
            }},
            'GRB090510': {{
                'trigger_id': '090510016',
                'date': '2009-05-10', 
                'redshift': 0.903,
                'max_energy': 31.0
            }},
            'GRB190114C': {{
                'trigger_id': '190114873',
                'date': '2019-01-14',
                'redshift': 0.4245,
                'max_energy': 1000.0
            }}
        }}
    
    def download_fermi_data(self, grb_name):
        """Scarica dati Fermi dopo registrazione."""
        print(f"📡 Scaricando dati Fermi per {{grb_name}}...")
        # Implementa download con credenziali
        
    def download_magic_data(self, grb_name):
        """Scarica dati MAGIC dopo registrazione."""
        print(f"🔭 Scaricando dati MAGIC per {{grb_name}}...")
        # Implementa download con credenziali
        
    def download_all_data(self):
        """Scarica tutti i dati dopo registrazione."""
        for grb_name in self.target_grbs.keys():
            self.download_fermi_data(grb_name)
            if grb_name == 'GRB190114C':
                self.download_magic_data(grb_name)

if __name__ == "__main__":
    print("📥 GRB DATA DOWNLOADER")
    print("Esegui questo script dopo aver ottenuto le credenziali!")
    
    downloader = GRBDataDownloader()
    downloader.download_all_data()
'''
        
        with open('official_grb_downloader.py', 'w', encoding='utf-8') as f:
            f.write(download_script)
        
        print("   ✅ Script salvato: official_grb_downloader.py")
        
        return download_script
    
    def run_full_registration_process(self):
        """Esegue il processo completo di registrazione."""
        print("\n🚀 PROCESSO REGISTRAZIONE COMPLETO")
        print("=" * 45)
        
        # Apri pagine
        self.open_registration_pages()
        
        # Genera template email
        magic_email, hess_email = self.generate_email_templates()
        
        # Crea checklist
        self.create_registration_checklist()
        
        # Genera script download
        self.generate_download_script()
        
        print(f"\n🎉 REGISTRAZIONE AUTOMATIZZATA COMPLETATA!")
        print(f"📁 File generati:")
        print(f"   📄 REGISTRATION_CHECKLIST.md")
        print(f"   📄 magic_registration_email.txt")
        print(f"   📄 hess_registration_email.txt")
        print(f"   📄 official_grb_downloader.py")
        
        print(f"\n📋 PROSSIMI PASSI:")
        print(f"   1. Registrati sui siti aperti nel browser")
        print(f"   2. Invia email template a MAGIC e HESS")
        print(f"   3. Attendi conferme e credenziali")
        print(f"   4. Esegui official_grb_downloader.py")
        print(f"   5. Segui REGISTRATION_CHECKLIST.md")


def main():
    """Funzione principale."""
    print("🔐 REGISTRATION AUTOMATION")
    print("=" * 50)
    print("Autore: Christian Quintino De Luca (RTH Italia)")
    print("Data: 2025-10-20")
    print("=" * 50)
    
    # Inizializza automazione
    automation = RegistrationAutomation()
    
    # Esegui processo completo
    automation.run_full_registration_process()


if __name__ == "__main__":
    main()

