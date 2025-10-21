#!/usr/bin/env python3
"""
Test semplice per scaricare dati reali GRB080916C
"""

import os
import requests

def test_download():
    print("Test scaricamento dati GRB080916C...")
    
    # Crea directory
    os.makedirs("real_data_test", exist_ok=True)
    
    # URL di test per GRB080916C
    test_urls = [
        "https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/080916/bn243216766_v00/bn243216766_v00_tte.fit",
        "https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/080916/bn243216766_v00/bn243216766_v00_cspec.fit"
    ]
    
    for i, url in enumerate(test_urls):
        print(f"Test {i+1}: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                filename = f"real_data_test/test_{i+1}.fits"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✓ File salvato: {filename}")
            else:
                print(f"✗ Errore: {response.status_code}")
        except Exception as e:
            print(f"✗ Errore: {e}")
        print()

if __name__ == "__main__":
    test_download()
