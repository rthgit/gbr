#!/usr/bin/env python3
"""
DOWNLOAD REAL OBSERVATORY DATA
==============================

Download dati REALI da tutti gli osservatori globali disponibili.
LIGO/Virgo, IceCube, MAGIC, HESS, VERITAS, CTA, AGILE, INTEGRAL, Konus-Wind, BATSE, BeppoSAX.

Autore: Christian Quintino De Luca
Affiliazione: RTH Italia - Research & Technology Hub
DOI: 10.5281/zenodo.17404757
"""

import numpy as np
import pandas as pd
import json
import requests
import os
from datetime import datetime
from scipy import stats
from sklearn.linear_model import RANSACRegressor
from sklearn.utils import resample
import astropy.io.fits as fits
from astropy.table import Table
import urllib.request
import tarfile
import zipfile

def download_ligo_virgo_data():
    """
    Download dati REALI da LIGO/Virgo
    """
    print("🛰️ Downloading REAL LIGO/Virgo data...")
    
    # URL per dati LIGO/Virgo
    ligo_urls = {
        'GW170817': 'https://www.gw-openscience.org/eventapi/html/GWTC-1-confident/GW170817/v3/',
        'GW190425': 'https://www.gw-openscience.org/eventapi/html/GWTC-2/GW190425/v3/',
        'GW190814': 'https://www.gw-openscience.org/eventapi/html/GWTC-2/GW190814/v3/',
        'GW200224_222234': 'https://www.gw-openscience.org/eventapi/html/GWTC-3/GW200224_222234/v3/'
    }
    
    ligo_data = {}
    
    for event, url in ligo_urls.items():
        print(f"   📊 Downloading {event}...")
        try:
            # Download dati LIGO
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                ligo_data[event] = response.json()
                print(f"   ✅ {event} downloaded successfully")
            else:
                print(f"   ❌ Error downloading {event}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading {event}: {e}")
            continue
    
    # Salva dati LIGO
    with open('real_data/ligo_virgo_data.json', 'w') as f:
        json.dump(ligo_data, f, indent=2)
    
    print(f"✅ LIGO/Virgo data downloaded: {len(ligo_data)} events")
    return ligo_data

def download_icecube_data():
    """
    Download dati REALI da IceCube
    """
    print("🛰️ Downloading REAL IceCube data...")
    
    # URL per dati IceCube
    icecube_urls = {
        'GRB221009A': 'https://icecube.wisc.edu/data-releases/2022/10/icecube-detects-gamma-ray-burst-grb-221009a/',
        'GRB170817A': 'https://icecube.wisc.edu/data-releases/2017/08/icecube-detects-gamma-ray-burst-grb-170817a/'
    }
    
    icecube_data = {}
    
    for event, url in icecube_urls.items():
        print(f"   📊 Downloading {event}...")
        try:
            # Download dati IceCube
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                icecube_data[event] = response.text
                print(f"   ✅ {event} downloaded successfully")
            else:
                print(f"   ❌ Error downloading {event}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading {event}: {e}")
            continue
    
    # Salva dati IceCube
    with open('real_data/icecube_data.json', 'w') as f:
        json.dump(icecube_data, f, indent=2)
    
    print(f"✅ IceCube data downloaded: {len(icecube_data)} events")
    return icecube_data

def download_magic_data():
    """
    Download dati REALI da MAGIC
    """
    print("🛰️ Downloading REAL MAGIC data...")
    
    # URL per dati MAGIC
    magic_urls = {
        'GRB221009A': 'https://magic.mpp.mpg.de/data/GRB221009A/',
        'GRB190114C': 'https://magic.mpp.mpg.de/data/GRB190114C/'
    }
    
    magic_data = {}
    
    for event, url in magic_urls.items():
        print(f"   📊 Downloading {event}...")
        try:
            # Download dati MAGIC
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                magic_data[event] = response.text
                print(f"   ✅ {event} downloaded successfully")
            else:
                print(f"   ❌ Error downloading {event}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading {event}: {e}")
            continue
    
    # Salva dati MAGIC
    with open('real_data/magic_data.json', 'w') as f:
        json.dump(magic_data, f, indent=2)
    
    print(f"✅ MAGIC data downloaded: {len(magic_data)} events")
    return magic_data

def download_hess_data():
    """
    Download dati REALI da HESS
    """
    print("🛰️ Downloading REAL HESS data...")
    
    # URL per dati HESS
    hess_urls = {
        'GRB221009A': 'https://www.mpi-hd.mpg.de/hfm/HESS/data/GRB221009A/',
        'GRB190114C': 'https://www.mpi-hd.mpg.de/hfm/HESS/data/GRB190114C/'
    }
    
    hess_data = {}
    
    for event, url in hess_urls.items():
        print(f"   📊 Downloading {event}...")
        try:
            # Download dati HESS
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                hess_data[event] = response.text
                print(f"   ✅ {event} downloaded successfully")
            else:
                print(f"   ❌ Error downloading {event}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading {event}: {e}")
            continue
    
    # Salva dati HESS
    with open('real_data/hess_data.json', 'w') as f:
        json.dump(hess_data, f, indent=2)
    
    print(f"✅ HESS data downloaded: {len(hess_data)} events")
    return hess_data

def download_agile_data():
    """
    Download dati REALI da AGILE
    """
    print("🛰️ Downloading REAL AGILE data...")
    
    # URL per dati AGILE
    agile_urls = {
        'GRB090902B': 'https://agile.ssdc.asi.it/grb/GRB090902B/',
        'GRB080916C': 'https://agile.ssdc.asi.it/grb/GRB080916C/',
        'GRB090510': 'https://agile.ssdc.asi.it/grb/GRB090510/',
        'GRB130427A': 'https://agile.ssdc.asi.it/grb/GRB130427A/'
    }
    
    agile_data = {}
    
    for event, url in agile_urls.items():
        print(f"   📊 Downloading {event}...")
        try:
            # Download dati AGILE
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                agile_data[event] = response.text
                print(f"   ✅ {event} downloaded successfully")
            else:
                print(f"   ❌ Error downloading {event}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading {event}: {e}")
            continue
    
    # Salva dati AGILE
    with open('real_data/agile_data.json', 'w') as f:
        json.dump(agile_data, f, indent=2)
    
    print(f"✅ AGILE data downloaded: {len(agile_data)} events")
    return agile_data

def download_integral_data():
    """
    Download dati REALI da INTEGRAL
    """
    print("🛰️ Downloading REAL INTEGRAL data...")
    
    # URL per dati INTEGRAL
    integral_urls = {
        'GRB090902B': 'https://www.esa.int/Science_Exploration/Space_Science/Integral/GRB090902B',
        'GRB080916C': 'https://www.esa.int/Science_Exploration/Space_Science/Integral/GRB080916C',
        'GRB090510': 'https://www.esa.int/Science_Exploration/Space_Science/Integral/GRB090510',
        'GRB130427A': 'https://www.esa.int/Science_Exploration/Space_Science/Integral/GRB130427A'
    }
    
    integral_data = {}
    
    for event, url in integral_urls.items():
        print(f"   📊 Downloading {event}...")
        try:
            # Download dati INTEGRAL
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                integral_data[event] = response.text
                print(f"   ✅ {event} downloaded successfully")
            else:
                print(f"   ❌ Error downloading {event}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading {event}: {e}")
            continue
    
    # Salva dati INTEGRAL
    with open('real_data/integral_data.json', 'w') as f:
        json.dump(integral_data, f, indent=2)
    
    print(f"✅ INTEGRAL data downloaded: {len(integral_data)} events")
    return integral_data

def download_konus_wind_data():
    """
    Download dati REALI da Konus-Wind
    """
    print("🛰️ Downloading REAL Konus-Wind data...")
    
    # URL per dati Konus-Wind
    konus_urls = {
        'GRB090902B': 'https://gcn.gsfc.nasa.gov/konus/GRB090902B/',
        'GRB080916C': 'https://gcn.gsfc.nasa.gov/konus/GRB080916C/',
        'GRB090510': 'https://gcn.gsfc.nasa.gov/konus/GRB090510/',
        'GRB130427A': 'https://gcn.gsfc.nasa.gov/konus/GRB130427A/'
    }
    
    konus_data = {}
    
    for event, url in konus_urls.items():
        print(f"   📊 Downloading {event}...")
        try:
            # Download dati Konus-Wind
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                konus_data[event] = response.text
                print(f"   ✅ {event} downloaded successfully")
            else:
                print(f"   ❌ Error downloading {event}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading {event}: {e}")
            continue
    
    # Salva dati Konus-Wind
    with open('real_data/konus_wind_data.json', 'w') as f:
        json.dump(konus_data, f, indent=2)
    
    print(f"✅ Konus-Wind data downloaded: {len(konus_data)} events")
    return konus_data

def download_batse_data():
    """
    Download dati REALI da BATSE
    """
    print("🛰️ Downloading REAL BATSE data...")
    
    # URL per dati BATSE
    batse_urls = {
        'GRB090902B': 'https://gammaray.nsstc.nasa.gov/batse/grb/GRB090902B/',
        'GRB080916C': 'https://gammaray.nsstc.nasa.gov/batse/grb/GRB080916C/',
        'GRB090510': 'https://gammaray.nsstc.nasa.gov/batse/grb/GRB090510/',
        'GRB130427A': 'https://gammaray.nsstc.nasa.gov/batse/grb/GRB130427A/'
    }
    
    batse_data = {}
    
    for event, url in batse_urls.items():
        print(f"   📊 Downloading {event}...")
        try:
            # Download dati BATSE
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                batse_data[event] = response.text
                print(f"   ✅ {event} downloaded successfully")
            else:
                print(f"   ❌ Error downloading {event}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading {event}: {e}")
            continue
    
    # Salva dati BATSE
    with open('real_data/batse_data.json', 'w') as f:
        json.dump(batse_data, f, indent=2)
    
    print(f"✅ BATSE data downloaded: {len(batse_data)} events")
    return batse_data

def download_bepposax_data():
    """
    Download dati REALI da BeppoSAX
    """
    print("🛰️ Downloading REAL BeppoSAX data...")
    
    # URL per dati BeppoSAX
    bepposax_urls = {
        'GRB090902B': 'https://www.asdc.asi.it/bepposax/GRB090902B/',
        'GRB080916C': 'https://www.asdc.asi.it/bepposax/GRB080916C/',
        'GRB090510': 'https://www.asdc.asi.it/bepposax/GRB090510/',
        'GRB130427A': 'https://www.asdc.asi.it/bepposax/GRB130427A/'
    }
    
    bepposax_data = {}
    
    for event, url in bepposax_urls.items():
        print(f"   📊 Downloading {event}...")
        try:
            # Download dati BeppoSAX
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                bepposax_data[event] = response.text
                print(f"   ✅ {event} downloaded successfully")
            else:
                print(f"   ❌ Error downloading {event}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading {event}: {e}")
            continue
    
    # Salva dati BeppoSAX
    with open('real_data/bepposax_data.json', 'w') as f:
        json.dump(bepposax_data, f, indent=2)
    
    print(f"✅ BeppoSAX data downloaded: {len(bepposax_data)} events")
    return bepposax_data

def download_real_observatory_data():
    """
    Download dati REALI da tutti gli osservatori
    """
    print("🚀 DOWNLOAD REAL OBSERVATORY DATA")
    print("=" * 60)
    print("Autore: Christian Quintino De Luca")
    print("Affiliazione: RTH Italia - Research & Technology Hub")
    print("DOI: 10.5281/zenodo.17404757")
    print("=" * 60)
    
    # Crea directory per dati reali
    os.makedirs('real_data', exist_ok=True)
    
    # Download dati da tutti gli osservatori
    all_data = {}
    
    print("🛰️ Downloading REAL data from ALL observatories...")
    
    # Download LIGO/Virgo
    ligo_data = download_ligo_virgo_data()
    all_data['ligo_virgo'] = ligo_data
    
    # Download IceCube
    icecube_data = download_icecube_data()
    all_data['icecube'] = icecube_data
    
    # Download MAGIC
    magic_data = download_magic_data()
    all_data['magic'] = magic_data
    
    # Download HESS
    hess_data = download_hess_data()
    all_data['hess'] = hess_data
    
    # Download AGILE
    agile_data = download_agile_data()
    all_data['agile'] = agile_data
    
    # Download INTEGRAL
    integral_data = download_integral_data()
    all_data['integral'] = integral_data
    
    # Download Konus-Wind
    konus_data = download_konus_wind_data()
    all_data['konus_wind'] = konus_data
    
    # Download BATSE
    batse_data = download_batse_data()
    all_data['batse'] = batse_data
    
    # Download BeppoSAX
    bepposax_data = download_bepposax_data()
    all_data['bepposax'] = bepposax_data
    
    # Salva tutti i dati
    with open('real_data/all_observatory_data.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print("=" * 60)
    print("🎉 REAL OBSERVATORY DATA DOWNLOAD COMPLETE!")
    print("📊 Check 'real_data/' directory for ALL real data")
    print("=" * 60)

if __name__ == "__main__":
    download_real_observatory_data()
