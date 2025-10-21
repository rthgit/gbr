#!/usr/bin/env python3
"""
DOWNLOADER DATI REALI GRB
=========================

Downloader per dati reali di GRB da archivi ufficiali:
- Fermi LAT/GBM
- H.E.S.S.
- MAGIC
- Swift BAT

Autore: Christian Quintino De Luca (RTH Italia)
ORCID: 0009-0000-4198-5449
Email: info@rthitalia.com
"""

import os
import requests
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def convert_numpy(obj):
    """Converte tipi NumPy in tipi Python standard per JSON"""
    if isinstance(obj, (int, float, str, bool, list, dict)):
        return obj
    elif hasattr(obj, 'tolist'):
        return obj.tolist()
    else:
        return str(obj)

def get_grb_download_info():
    """Ottieni informazioni per download GRB reali"""
    
    grb_info = {
        # TIER 1: GRB STELLARI (5 stelle)
        'GRB160625B': {
            'tier': 1,
            'stars': 5,
            'trigger': 488587166,
            'redshift': 1.406,
            'special': 'Long burst con fotoni TeV, ottimo per cosmologia',
            'fermi_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2016/bn160625b/',
            'lat_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/2016/bn160625b/',
            'hess_url': 'https://www.mpi-hd.mpg.de/hfm/HESS/pages/home/som/2016/07/',
            'priority': 'HIGH'
        },
        'GRB170817A': {
            'tier': 1,
            'stars': 5,
            'trigger': 524666471,
            'redshift': 0.0099,
            'special': 'GRB + onde gravitazionali, kilonova associata',
            'fermi_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2017/bn170817a/',
            'lat_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/2017/bn170817a/',
            'ligo_url': 'https://www.gw-openscience.org/events/GW170817/',
            'priority': 'HIGH'
        },
        'GRB180720B': {
            'tier': 1,
            'stars': 5,
            'trigger': 554620103,
            'redshift': 0.654,
            'special': 'Rilevato da H.E.S.S. (TeV), emission prolungata',
            'fermi_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2018/bn180720b/',
            'lat_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/2018/bn180720b/',
            'hess_url': 'https://www.mpi-hd.mpg.de/hfm/HESS/pages/home/som/2018/07/',
            'priority': 'HIGH'
        },
        'GRB090902B': {
            'tier': 1,
            'stars': 4,
            'trigger': 273581808,
            'redshift': 1.822,
            'special': 'Anomalia 3.32σ nota, più numeroso fotoni',
            'fermi_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2009/bn090902b/',
            'lat_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/2009/bn090902b/',
            'priority': 'HIGH'
        },
        'GRB150314A': {
            'tier': 1,
            'stars': 4,
            'trigger': 437950656,
            'redshift': 1.758,
            'special': 'Long burst brillante, buona statistica',
            'fermi_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2015/bn150314a/',
            'lat_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/2015/bn150314a/',
            'priority': 'HIGH'
        },
        
        # TIER 2: GRB MOLTO INTERESSANTI (4 stelle)
        'GRB140810A': {
            'tier': 2,
            'stars': 4,
            'trigger': 429447091,
            'redshift': 3.29,
            'special': 'Long burst, z=3.29 (lontano)',
            'fermi_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2014/bn140810a/',
            'lat_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/2014/bn140810a/',
            'priority': 'MEDIUM'
        },
        'GRB131108A': {
            'tier': 2,
            'stars': 4,
            'trigger': 375417743,
            'redshift': 2.40,
            'special': 'Long burst, z=2.40',
            'fermi_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2013/bn131108a/',
            'lat_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/2013/bn131108a/',
            'priority': 'MEDIUM'
        },
        'GRB141028A': {
            'tier': 2,
            'stars': 4,
            'trigger': 435812555,
            'redshift': 2.33,
            'special': 'Long burst, z=2.33',
            'fermi_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2014/bn141028a/',
            'lat_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/2014/bn141028a/',
            'priority': 'MEDIUM'
        },
        'GRB160509A': {
            'tier': 2,
            'stars': 4,
            'trigger': 484170214,
            'redshift': 1.17,
            'special': 'Short burst raro con LAT',
            'fermi_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2016/bn160509a/',
            'lat_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/2016/bn160509a/',
            'priority': 'MEDIUM'
        },
        'GRB190829A': {
            'tier': 2,
            'stars': 4,
            'trigger': 588411836,
            'redshift': 0.0785,
            'special': 'Rilevato da H.E.S.S., emission TeV tardiva',
            'fermi_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/2019/bn190829a/',
            'lat_url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/2019/bn190829a/',
            'hess_url': 'https://www.mpi-hd.mpg.de/hfm/HESS/pages/home/som/2019/08/',
            'priority': 'MEDIUM'
        }
    }
    
    return grb_info

def create_download_instructions():
    """Crea istruzioni per download dati reali"""
    
    grb_info = get_grb_download_info()
    
    instructions = {
        'timestamp': datetime.now().isoformat(),
        'total_grb': len(grb_info),
        'tier1_grb': len([g for g in grb_info.values() if g['tier'] == 1]),
        'tier2_grb': len([g for g in grb_info.values() if g['tier'] == 2]),
        'download_instructions': {
            'fermi_lat': {
                'description': 'Fermi LAT Data Archive',
                'url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/',
                'registration_required': False,
                'direct_download': True,
                'file_types': ['.fits', '.evt', '.ph1', '.ph2']
            },
            'fermi_gbm': {
                'description': 'Fermi GBM Data Archive',
                'url': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/',
                'registration_required': False,
                'direct_download': True,
                'file_types': ['.fits', '.tte', '.ctime']
            },
            'hess': {
                'description': 'H.E.S.S. Data Archive',
                'url': 'https://www.mpi-hd.mpg.de/hfm/HESS/',
                'registration_required': True,
                'direct_download': False,
                'contact': 'hess-data@mpi-hd.mpg.de'
            },
            'magic': {
                'description': 'MAGIC Data Archive',
                'url': 'https://magic.mpp.mpg.de/',
                'registration_required': True,
                'direct_download': False,
                'contact': 'magic-data@mpp.mpg.de'
            }
        },
        'grb_details': grb_info,
        'download_commands': [],
        'registration_emails': []
    }
    
    # Genera comandi download per Fermi
    for grb_name, grb_data in grb_info.items():
        if grb_data['priority'] == 'HIGH':
            # Comandi wget per Fermi LAT
            lat_files = [
                f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/{grb_name.lower()[:4]}/{grb_name.lower()}/current/lat_photon_merged.fits",
                f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/triggers/{grb_name.lower()[:4]}/{grb_name.lower()}/current/lat_spacecraft_merged.fits"
            ]
            
            for file_url in lat_files:
                instructions['download_commands'].append({
                    'grb': grb_name,
                    'command': f"wget -O {grb_name.lower()}_lat_data.fits '{file_url}'",
                    'description': f'Download LAT data for {grb_name}'
                })
    
    # Genera email per registrazione H.E.S.S. e MAGIC
    for grb_name, grb_data in grb_info.items():
        if 'hess_url' in grb_data:
            instructions['registration_emails'].append({
                'grb': grb_name,
                'collaboration': 'H.E.S.S.',
                'email': 'hess-data@mpi-hd.mpg.de',
                'subject': f'Data Request for {grb_name}',
                'body': f"""Dear H.E.S.S. Collaboration,

I am requesting access to the {grb_name} data for quantum gravity research.

GRB Details:
- Trigger: {grb_data['trigger']}
- Redshift: {grb_data['redshift']}
- Special: {grb_data['special']}

Research Purpose: Quantum Gravity Detection in Gamma-Ray Bursts
Institution: RTH Italia
Researcher: Christian Quintino De Luca
ORCID: 0009-0000-4198-5449
Email: info@rthitalia.com

Thank you for your consideration.

Best regards,
Christian Quintino De Luca
RTH Italia"""
            })
        
        if 'magic_url' in grb_data:
            instructions['registration_emails'].append({
                'grb': grb_name,
                'collaboration': 'MAGIC',
                'email': 'magic-data@mpp.mpg.de',
                'subject': f'Data Request for {grb_name}',
                'body': f"""Dear MAGIC Collaboration,

I am requesting access to the {grb_name} data for quantum gravity research.

GRB Details:
- Trigger: {grb_data['trigger']}
- Redshift: {grb_data['redshift']}
- Special: {grb_data['special']}

Research Purpose: Quantum Gravity Detection in Gamma-Ray Bursts
Institution: RTH Italia
Researcher: Christian Quintino De Luca
ORCID: 0009-0000-4198-5449
Email: info@rthitalia.com

Thank you for your consideration.

Best regards,
Christian Quintino De Luca
RTH Italia"""
            })
    
    return instructions

def create_download_scripts():
    """Crea script per download automatico"""
    
    instructions = create_download_instructions()
    
    # Script per download Fermi
    fermi_script = """#!/bin/bash
# Fermi LAT Data Download Script
# Generated automatically for GRB analysis

echo "Downloading Fermi LAT data for priority GRBs..."

"""
    
    for command in instructions['download_commands']:
        fermi_script += f"# {command['description']}\n"
        fermi_script += f"{command['command']}\n"
        fermi_script += f"echo 'Downloaded {command['grb']} LAT data'\n\n"
    
    fermi_script += """
echo "Fermi LAT download completed!"
echo "Files downloaded:"
ls -la *.fits

echo "Ready for analysis!"
"""
    
    # Salva script
    with open('download_fermi_data.sh', 'w') as f:
        f.write(fermi_script)
    
    # Script PowerShell per Windows
    powershell_script = """# Fermi LAT Data Download Script (PowerShell)
# Generated automatically for GRB analysis

Write-Host "Downloading Fermi LAT data for priority GRBs..." -ForegroundColor Green

"""
    
    for command in instructions['download_commands']:
        powershell_script += f"# {command['description']}\n"
        powershell_script += f"Invoke-WebRequest -Uri \"{command['command'].split(\"'\")[1]}\" -OutFile \"{command['command'].split(' ')[2]}\"\n"
        powershell_script += f"Write-Host 'Downloaded {command['grb']} LAT data' -ForegroundColor Yellow\n\n"
    
    powershell_script += """
Write-Host "Fermi LAT download completed!" -ForegroundColor Green
Write-Host "Files downloaded:" -ForegroundColor Cyan
Get-ChildItem *.fits | Format-Table

Write-Host "Ready for analysis!" -ForegroundColor Green
"""
    
    # Salva script PowerShell
    with open('download_fermi_data.ps1', 'w') as f:
        f.write(powershell_script)
    
    return instructions

def main():
    """Funzione principale per downloader dati reali"""
    
    print("="*70)
    print("DOWNLOADER DATI REALI GRB")
    print("Preparazione per download dati reali da archivi ufficiali")
    print("="*70)
    
    # Crea istruzioni download
    print("\n📥 Creazione istruzioni download...")
    instructions = create_download_instructions()
    
    # Crea script download
    print("\n📥 Creazione script download...")
    create_download_scripts()
    
    # Salva istruzioni
    with open('real_grb_download_instructions.json', 'w') as f:
        json.dump(instructions, f, indent=2, default=convert_numpy)
    
    # Stampa riassunto
    print("\n" + "="*70)
    print("🎯 ISTRUZIONI DOWNLOAD DATI REALI")
    print("="*70)
    
    print(f"🎯 GRB Totali: {instructions['total_grb']}")
    print(f"🎯 Tier 1 (5⭐): {instructions['tier1_grb']}")
    print(f"🎯 Tier 2 (4⭐): {instructions['tier2_grb']}")
    print(f"🎯 Comandi Download: {len(instructions['download_commands'])}")
    print(f"🎯 Email Registrazione: {len(instructions['registration_emails'])}")
    
    print(f"\n📥 COMANDI DOWNLOAD FERMI:")
    for command in instructions['download_commands']:
        print(f"  {command['command']}")
    
    print(f"\n📧 EMAIL REGISTRAZIONE:")
    for email in instructions['registration_emails']:
        print(f"  {email['collaboration']}: {email['email']}")
        print(f"    Subject: {email['subject']}")
    
    print(f"\n📁 FILE CREATI:")
    print(f"  ✅ real_grb_download_instructions.json")
    print(f"  ✅ download_fermi_data.sh")
    print(f"  ✅ download_fermi_data.ps1")
    
    print(f"\n🚀 PROSSIMI PASSI:")
    print(f"  1. Esegui download_fermi_data.ps1 per dati Fermi")
    print(f"  2. Invia email per registrazione H.E.S.S./MAGIC")
    print(f"  3. Analizza dati reali con metodologie robuste")
    
    print("\n" + "="*70)
    print("✅ Downloader dati reali preparato!")
    print("📊 Istruzioni salvate: real_grb_download_instructions.json")
    print("📁 Script creati: download_fermi_data.sh, download_fermi_data.ps1")
    print("="*70)

if __name__ == "__main__":
    main()