# COMANDI PER ANALISI MULTI-GRB

## 🎯 ANALISI RAPIDA MULTI-GRB

### **1. VERIFICA FILE DISPONIBILI:**
```bash
python -c "
import os
files = ['L251020154246F357373F64_EV00.fits', 'L251020161443F357373F97_EV00.fits', 'L251020161531F357373F51_EV00.fits', 'L251020161615F357373F52_EV00.fits']
print('VERIFICA FILE FITS:')
for f in files:
    exists = os.path.exists(f)
    print(f'{f}: {\"✅\" if exists else \"❌\"}')
"
```

### **2. ANALISI GRB080916C (già fatto):**
```bash
python -c "
import numpy as np
from astropy.io import fits
print('GRB080916C - RISULTATO:')
with fits.open('L251020154246F357373F64_EV00.fits') as hdul:
    events_data = hdul['EVENTS'].data
    times = events_data['TIME'] - 243216266.0
    energies = events_data['ENERGY'] / 1000.0
    quality_cuts = (energies > 0.1) & (times >= 0) & (times <= 2500)
    times_filtered = times[quality_cuts]
    energies_filtered = energies[quality_cuts]
    correlation = np.corrcoef(energies_filtered, times_filtered)[0,1] if len(times_filtered) > 2 else 0.0
    significance = abs(correlation) * np.sqrt(len(times_filtered) - 2) / np.sqrt(1 - correlation**2) if len(times_filtered) > 2 else 0.0
    print(f'  Fotoni: {len(times_filtered)}, GeV: {np.sum(energies_filtered > 1.0)}')
    print(f'  Correlazione: r = {correlation:.3f}, σ = {significance:.2f}')
"
```

### **3. ANALISI GRB130427A (95 GeV!):**
```bash
python -c "
import numpy as np
from astropy.io import fits
print('GRB130427A - ANALISI:')
with fits.open('L251020161443F357373F97_EV00.fits') as hdul:
    events_data = hdul['EVENTS'].data
    times = events_data['TIME'] - 388798843.0
    energies = events_data['ENERGY'] / 1000.0
    quality_cuts = (energies > 0.1) & (times >= 0) & (times <= 2500)
    times_filtered = times[quality_cuts]
    energies_filtered = energies[quality_cuts]
    print(f'  Eventi totali: {len(events_data)}')
    print(f'  Eventi filtrati: {len(times_filtered)}')
    print(f'  Range energie: {energies_filtered.min():.3f} - {energies_filtered.max():.1f} GeV')
    print(f'  Fotoni GeV: {np.sum(energies_filtered > 1.0)}')
    print(f'  Fotoni >10 GeV: {np.sum(energies_filtered > 10.0)}')
    if len(times_filtered) > 2:
        correlation = np.corrcoef(energies_filtered, times_filtered)[0,1]
        significance = abs(correlation) * np.sqrt(len(times_filtered) - 2) / np.sqrt(1 - correlation**2)
        print(f'  Correlazione: r = {correlation:.3f}, σ = {significance:.2f}')
"
```

### **4. ANALISI GRB090510 (Short burst):**
```bash
python -c "
import numpy as np
from astropy.io import fits
print('GRB090510 - ANALISI:')
with fits.open('L251020161531F357373F51_EV00.fits') as hdul:
    events_data = hdul['EVENTS'].data
    times = events_data['TIME'] - 263607281.0
    energies = events_data['ENERGY'] / 1000.0
    quality_cuts = (energies > 0.1) & (times >= 0) & (times <= 2500)
    times_filtered = times[quality_cuts]
    energies_filtered = energies[quality_cuts]
    print(f'  Eventi totali: {len(events_data)}')
    print(f'  Eventi filtrati: {len(times_filtered)}')
    print(f'  Range energie: {energies_filtered.min():.3f} - {energies_filtered.max():.1f} GeV')
    print(f'  Fotoni GeV: {np.sum(energies_filtered > 1.0)}')
    print(f'  Fotoni >10 GeV: {np.sum(energies_filtered > 10.0)}')
    if len(times_filtered) > 2:
        correlation = np.corrcoef(energies_filtered, times_filtered)[0,1]
        significance = abs(correlation) * np.sqrt(len(times_filtered) - 2) / np.sqrt(1 - correlation**2)
        print(f'  Correlazione: r = {correlation:.3f}, σ = {significance:.2f}')
"
```

### **5. ANALISI GRB090902:**
```bash
python -c "
import numpy as np
from astropy.io import fits
print('GRB090902 - ANALISI:')
with fits.open('L251020161615F357373F52_EV00.fits') as hdul:
    events_data = hdul['EVENTS'].data
    times = events_data['TIME'] - 273581808.0
    energies = events_data['ENERGY'] / 1000.0
    quality_cuts = (energies > 0.1) & (times >= 0) & (times <= 2500)
    times_filtered = times[quality_cuts]
    energies_filtered = energies[quality_cuts]
    print(f'  Eventi totali: {len(events_data)}')
    print(f'  Eventi filtrati: {len(times_filtered)}')
    print(f'  Range energie: {energies_filtered.min():.3f} - {energies_filtered.max():.1f} GeV')
    print(f'  Fotoni GeV: {np.sum(energies_filtered > 1.0)}')
    print(f'  Fotoni >10 GeV: {np.sum(energies_filtered > 10.0)}')
    if len(times_filtered) > 2:
        correlation = np.corrcoef(energies_filtered, times_filtered)[0,1]
        significance = abs(correlation) * np.sqrt(len(times_filtered) - 2) / np.sqrt(1 - correlation**2)
        print(f'  Correlazione: r = {correlation:.3f}, σ = {significance:.2f}')
"
```

### **6. ANALISI COMBINATA COMPLETA:**
```bash
python -c "
import numpy as np
from astropy.io import fits
import json
from datetime import datetime

print('ANALISI MULTI-GRB COMPLETA')
print('='*50)

# Configurazione GRB
grb_configs = [
    {'name': 'GRB080916C', 'file': 'L251020154246F357373F64_EV00.fits', 'trigger': 243216266.0, 'z': 4.35},
    {'name': 'GRB130427A', 'file': 'L251020161443F357373F97_EV00.fits', 'trigger': 388798843.0, 'z': 0.34},
    {'name': 'GRB090510', 'file': 'L251020161531F357373F51_EV00.fits', 'trigger': 263607281.0, 'z': 0.903},
    {'name': 'GRB090902', 'file': 'L251020161615F357373F52_EV00.fits', 'trigger': 273581808.0, 'z': 1.822}
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
                    'E_QG': float(E_QG)
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

1. **Esegui i comandi** in sequenza
2. **Verifica** che tutti i file FITS siano presenti
3. **Analizza** ogni GRB individualmente
4. **Combina** i risultati con l'ultimo comando
5. **Controlla** il file `multi_grb_results.json`

## 📊 RISULTATO ATTESO

Con 4 GRB reali, ci aspettiamo:
- **Statistica migliorata** (più fotoni totali)
- **Correlazione combinata** debole
- **Significatività bassa** (< 2σ)
- **Nessuna evidenza QG** (normale)

Questo confermerebbe la robustezza del nostro toolkit su un campione più grande!

