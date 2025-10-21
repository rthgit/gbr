# COMANDI PER DOWNLOAD GRB REALI

## 🎯 DOWNLOAD TUTTI I GRB

### **1. GRB090902 (3972 fotoni):**
```bash
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020161615F357373F52_EV00.fits
```

### **2. GRB090510 (2371 fotoni):**
```bash
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020161912F357373F19_EV00.fits
```

### **3. GRB130427A (16 fotoni):**
```bash
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020162012F357373F30_EV00.fits
```

## 🚀 DOWNLOAD RAPIDO (TUTTI INSIEME):

```bash
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020161615F357373F52_EV00.fits && wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020161912F357373F19_EV00.fits && wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020162012F357373F30_EV00.fits
```

## 📊 VERIFICA FILE SCARICATI:

```bash
python -c "
import os
files = [
    'L251020154246F357373F64_EV00.fits',  # GRB080916C
    'L251020161615F357373F52_EV00.fits',  # GRB090902
    'L251020161912F357373F19_EV00.fits',  # GRB090510
    'L251020162012F357373F30_EV00.fits'   # GRB130427A
]
print('VERIFICA FILE FITS:')
for f in files:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    print(f'{f}: {\"✅\" if exists else \"❌\"} ({size/1024:.1f} KB)')
"
```

## 🎯 ANALISI IMMEDIATA DOPO DOWNLOAD:

```bash
python -c "
import numpy as np
from astropy.io import fits
import json
from datetime import datetime

print('ANALISI MULTI-GRB COMPLETA')
print('='*50)

# Configurazione GRB (aggiornata con nuovi file)
grb_configs = [
    {'name': 'GRB080916C', 'file': 'L251020154246F357373F64_EV00.fits', 'trigger': 243216266.0, 'z': 4.35},
    {'name': 'GRB090902', 'file': 'L251020161615F357373F52_EV00.fits', 'trigger': 273581808.0, 'z': 1.822},
    {'name': 'GRB090510', 'file': 'L251020161912F357373F19_EV00.fits', 'trigger': 263607281.0, 'z': 0.903},
    {'name': 'GRB130427A', 'file': 'L251020162012F357373F30_EV00.fits', 'trigger': 388798843.0, 'z': 0.34}
]

results = []
total_photons = 0
total_geV_photons = 0

for config in grb_configs:
    print(f'\\n{config[\"name\"]}:')
    try:
        with fits.open(config['file']) as hdul:
            events_data = hdul['EVENTS'].data
            times = events_data['TIME'] - config['trigger']
            energies = events_data['ENERGY'] / 1000.0
            
            quality_cuts = (energies > 0.1) & (times >= 0) & (times <= 2500)
            times_filtered = times[quality_cuts]
            energies_filtered = energies[quality_cuts]
            
            n_photons = len(times_filtered)
            n_geV = np.sum(energies_filtered > 1.0)
            n_heV = np.sum(energies_filtered > 10.0)
            
            print(f'  Fotoni: {n_photons}, GeV: {n_geV}, >10GeV: {n_heV}')
            print(f'  Range energie: {energies_filtered.min():.3f} - {energies_filtered.max():.1f} GeV')
            
            if n_photons > 2:
                correlation = np.corrcoef(energies_filtered, times_filtered)[0,1]
                significance = abs(correlation) * np.sqrt(n_photons - 2) / np.sqrt(1 - correlation**2)
                print(f'  Correlazione: r = {correlation:.3f}, σ = {significance:.2f}')
                
                # Calcola E_QG
                H0 = 70.0; c = 3e5; z = config['z']
                d_L = (c/H0) * z * (1 + z)
                slope = np.polyfit(energies_filtered, times_filtered, 1)[0]
                E_QG = d_L * 3.086e22 / (c * abs(slope)) / 1e9 if abs(slope) > 1e-10 else np.inf
                print(f'  E_QG: {E_QG:.2e} GeV')
                
                results.append({
                    'name': config['name'],
                    'correlation': float(correlation),
                    'significance': float(significance),
                    'photons': n_photons,
                    'geV_photons': n_geV,
                    'E_QG': float(E_QG),
                    'redshift': z
                })
                
                total_photons += n_photons
                total_geV_photons += n_geV
            else:
                print('  Troppi pochi fotoni per analisi')
    except Exception as e:
        print(f'  Errore: {e}')

# Risultati combinati
if results:
    print(f'\\nRISULTATI COMBINATI:')
    print(f'  GRB analizzati: {len(results)}')
    print(f'  Fotoni totali: {total_photons}')
    print(f'  Fotoni GeV: {total_geV_photons}')
    
    # Correlazione combinata (weighted average)
    weights = [r['photons'] for r in results]
    correlations = [r['correlation'] for r in results]
    combined_correlation = np.average(correlations, weights=weights)
    
    # Significatività combinata
    combined_significance = abs(combined_correlation) * np.sqrt(total_photons - 2) / np.sqrt(1 - combined_correlation**2)
    
    print(f'  Correlazione combinata: r = {combined_correlation:.3f}')
    print(f'  Significatività combinata: {combined_significance:.2f}σ')
    
    if combined_significance < 2:
        print('  ✅ NESSUNA EVIDENZA QG - RISULTATO NORMALE!')
    else:
        print('  ⚠️ CORRELAZIONE SIGNIFICATIVA - VERIFICA!')
    
    # Salva risultati
    output = {
        'num_grb': len(results),
        'total_photons': total_photons,
        'total_geV_photons': total_geV_photons,
        'combined_correlation': float(combined_correlation),
        'combined_significance': float(combined_significance),
        'individual_results': results,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('multi_grb_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print('\\n✅ Risultati salvati: multi_grb_results.json')
else:
    print('❌ Nessun risultato valido')
"
```

## 🎯 ISTRUZIONI

1. **Scarica** tutti i file con i comandi wget
2. **Verifica** che tutti i file siano presenti
3. **Esegui** l'analisi combinata
4. **Controlla** i risultati in `multi_grb_results.json`

## 📊 RISULTATO ATTESO

Con 4 GRB reali e **6369 fotoni totali**:
- **Statistica molto migliorata**
- **Correlazione combinata** debole
- **Significatività bassa** (< 2σ)
- **Nessuna evidenza QG** (normale)
- **Toolkit validato** su campione grande

Questo sarà il test definitivo del nostro toolkit!
