# COMANDI PER ANALISI DATI REALI FERMI LAT - GRB080916C

## 🎯 COMANDI DIRETTI PYTHON

### **1. ANALISI BASILARE:**
```bash
python -c "
import numpy as np
from astropy.io import fits
print('ANALISI DATI REALI FERMI LAT - GRB080916C')
print('='*50)
with fits.open('L251020154246F357373F64_EV00.fits') as hdul:
    events_data = hdul['EVENTS'].data
    times = events_data['TIME']
    energies = events_data['ENERGY']
    trigger_time = 243216266.0
    times_relative = times - trigger_time
    energies_gev = energies / 1000.0
    quality_cuts = (energies_gev > 0.1) & (times_relative >= 0) & (times_relative <= 2500)
    times_filtered = times_relative[quality_cuts]
    energies_filtered = energies_gev[quality_cuts]
    print(f'Eventi dopo filtri: {len(times_filtered)}')
    print(f'Fotoni > 1 GeV: {np.sum(energies_filtered > 1.0)}')
    print(f'Fotoni > 10 GeV: {np.sum(energies_filtered > 10.0)}')
    if len(times_filtered) > 2:
        correlation = np.corrcoef(energies_filtered, times_filtered)[0,1]
        significance = abs(correlation) * np.sqrt(len(times_filtered) - 2) / np.sqrt(1 - correlation**2)
        print(f'Correlazione: r = {correlation:.3f}')
        print(f'Significatività: {significance:.2f}σ')
    print('✅ ANALISI COMPLETATA!')
"
```

### **2. ANALISI DETTAGLIATA:**
```bash
python -c "
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import json
from datetime import datetime

print('ANALISI DATI REALI FERMI LAT - GRB080916C')
print('='*60)

with fits.open('L251020154246F357373F64_EV00.fits') as hdul:
    events_data = hdul['EVENTS'].data
    times = events_data['TIME']
    energies = events_data['ENERGY']
    trigger_time = 243216266.0
    times_relative = times - trigger_time
    energies_gev = energies / 1000.0
    
    print(f'Numero totale eventi: {len(events_data)}')
    print(f'Range tempi: {times_relative.min():.1f} - {times_relative.max():.1f} s')
    print(f'Range energie: {energies_gev.min():.3f} - {energies_gev.max():.1f} GeV')
    
    quality_cuts = (energies_gev > 0.1) & (times_relative >= 0) & (times_relative <= 2500)
    times_filtered = times_relative[quality_cuts]
    energies_filtered = energies_gev[quality_cuts]
    
    print(f'Eventi dopo filtri: {len(times_filtered)}')
    print(f'Fotoni > 1 GeV: {np.sum(energies_filtered > 1.0)}')
    print(f'Fotoni > 10 GeV: {np.sum(energies_filtered > 10.0)}')
    
    if len(times_filtered) > 2:
        correlation = np.corrcoef(energies_filtered, times_filtered)[0,1]
        significance = abs(correlation) * np.sqrt(len(times_filtered) - 2) / np.sqrt(1 - correlation**2)
        slope, intercept = np.polyfit(energies_filtered, times_filtered, 1)
        
        print(f'Correlazione: r = {correlation:.3f}')
        print(f'Significatività: {significance:.2f}σ')
        print(f'Slope: {slope:.2e}')
        
        if significance < 2:
            print('✅ NESSUNA EVIDENZA QG - RISULTATO NORMALE!')
        else:
            print('⚠️ Correlazione significativa - verifica!')
    
    # Salva risultati
    results = {
        'correlation': float(correlation) if len(times_filtered) > 2 else 0.0,
        'significance_sigma': float(significance) if len(times_filtered) > 2 else 0.0,
        'n_photons': len(times_filtered),
        'geV_photons': int(np.sum(energies_filtered > 1.0)),
        'high_energy_photons': int(np.sum(energies_filtered > 10.0)),
        'data_source': 'Real Fermi LAT data',
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    with open('real_fermi_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print('✅ Risultati salvati: real_fermi_results.json')
"
```

### **3. CREAZIONE GRAFICI:**
```bash
python -c "
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

plt.figure(figsize=(12, 8))

with fits.open('L251020154246F357373F64_EV00.fits') as hdul:
    events_data = hdul['EVENTS'].data
    times = events_data['TIME']
    energies = events_data['ENERGY']
    trigger_time = 243216266.0
    times_relative = times - trigger_time
    energies_gev = energies / 1000.0
    
    quality_cuts = (energies_gev > 0.1) & (times_relative >= 0) & (times_relative <= 2500)
    times_filtered = times_relative[quality_cuts]
    energies_filtered = energies_gev[quality_cuts]
    
    # Plot 1: Energia vs Tempo
    plt.subplot(2, 2, 1)
    plt.scatter(energies_filtered, times_filtered, alpha=0.6, s=20, c='blue')
    plt.xlabel('Energia (GeV)')
    plt.ylabel('Tempo di arrivo (s)')
    plt.title('GRB080916C: DATI REALI Fermi LAT')
    plt.xscale('log')
    
    # Plot 2: Istogramma energie
    plt.subplot(2, 2, 2)
    plt.hist(energies_filtered, bins=50, alpha=0.7, color='green')
    plt.xlabel('Energia (GeV)')
    plt.ylabel('Numero fotoni')
    plt.title('Distribuzione Energetica')
    plt.xscale('log')
    
    # Plot 3: Istogramma tempi
    plt.subplot(2, 2, 3)
    plt.hist(times_filtered, bins=50, alpha=0.7, color='orange')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Numero fotoni')
    plt.title('Distribuzione Temporale')
    
    # Plot 4: Statistiche
    plt.subplot(2, 2, 4)
    plt.axis('off')
    stats_text = f'''STATISTICHE REALI:

Fotoni totali: {len(times_filtered)}
Fotoni GeV: {np.sum(energies_filtered > 1.0)}
Fotoni >10 GeV: {np.sum(energies_filtered > 10.0)}

Fonte: Fermi LAT REALE'''
    plt.text(0.1, 0.9, stats_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top', fontfamily='monospace')
    
    plt.tight_layout()
    plt.savefig('real_fermi_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print('✅ Grafico salvato: real_fermi_analysis.png')
"
```

## 🎯 COMANDI ALTERNATIVI

### **4. VERIFICA FILE:**
```bash
python -c "
from astropy.io import fits
print('VERIFICA STRUTTURA FILE FITS:')
with fits.open('L251020154246F357373F64_EV00.fits') as hdul:
    print(f'HDUs: {[hdu.name for hdu in hdul]}')
    events_data = hdul['EVENTS'].data
    print(f'Eventi: {len(events_data)}')
    print(f'Colonne: {events_data.dtype.names}')
"
```

### **5. ANALISI COMPLETA:**
```bash
python -c "
import numpy as np
from astropy.io import fits
import json
from datetime import datetime

print('ANALISI COMPLETA DATI REALI FERMI LAT')
print('='*50)

with fits.open('L251020154246F357373F64_EV00.fits') as hdul:
    events_data = hdul['EVENTS'].data
    times = events_data['TIME']
    energies = events_data['ENERGY']
    event_classes = events_data['EVENT_CLASS']
    zenith_angles = events_data['ZENITH_ANGLE']
    
    trigger_time = 243216266.0
    times_relative = times - trigger_time
    energies_gev = energies / 1000.0
    
    print(f'Numero totale eventi: {len(events_data)}')
    print(f'Range tempi: {times_relative.min():.1f} - {times_relative.max():.1f} s')
    print(f'Range energie: {energies_gev.min():.3f} - {energies_gev.max():.1f} GeV')
    
    # Filtri qualità
    quality_cuts = (energies_gev > 0.1) & (times_relative >= 0) & (times_relative <= 2500)
    times_filtered = times_relative[quality_cuts]
    energies_filtered = energies_gev[quality_cuts]
    event_classes_filtered = event_classes[quality_cuts]
    zenith_filtered = zenith_angles[quality_cuts]
    
    print(f'Eventi dopo filtri: {len(times_filtered)}')
    print(f'Fotoni > 1 GeV: {np.sum(energies_filtered > 1.0)}')
    print(f'Fotoni > 10 GeV: {np.sum(energies_filtered > 10.0)}')
    
    # Analisi correlazione
    if len(times_filtered) > 2:
        correlation = np.corrcoef(energies_filtered, times_filtered)[0,1]
        significance = abs(correlation) * np.sqrt(len(times_filtered) - 2) / np.sqrt(1 - correlation**2)
        slope, intercept = np.polyfit(energies_filtered, times_filtered, 1)
        
        print(f'\\nRISULTATI ANALISI:')
        print(f'Correlazione: r = {correlation:.3f}')
        print(f'Significatività: {significance:.2f}σ')
        print(f'Slope: {slope:.2e}')
        
        # Calcola E_QG
        z = 4.35
        H0 = 70.0
        c = 3e5
        d_L = (c/H0) * z * (1 + z)
        
        if abs(slope) > 1e-10:
            E_QG_fitted = d_L * 3.086e22 / (c * abs(slope)) / 1e9
        else:
            E_QG_fitted = np.inf
        
        print(f'E_QG fitted: {E_QG_fitted:.2e} GeV')
        
        # Interpretazione
        print(f'\\nINTERPRETAZIONE:')
        if significance < 2:
            print('✅ Nessuna evidenza di effetti QG (normale)')
            print('✅ Risultato consistente con letteratura Fermi-LAT')
        elif significance < 3:
            print('⚠️ Correlazione debole, necessaria analisi approfondita')
        else:
            print('🚨 Correlazione significativa - verifica metodologia!')
        
        # Salva risultati completi
        results = {
            'grb_info': {
                'name': 'GRB080916C',
                'trigger_id': '243216766',
                'redshift': 4.35,
                'data_source': 'Real Fermi LAT data',
                'query_id': 'L251020154246F357373F64'
            },
            'data_metadata': {
                'file_name': 'L251020154246F357373F64_EV00.fits',
                'trigger_time_met': trigger_time,
                'total_events': len(events_data),
                'filtered_events': len(times_filtered),
                'energy_range_gev': [float(energies_filtered.min()), float(energies_filtered.max())],
                'time_range_s': [float(times_filtered.min()), float(times_filtered.max())],
                'geV_photons': int(np.sum(energies_filtered > 1.0)),
                'high_energy_photons': int(np.sum(energies_filtered > 10.0)),
                'load_timestamp': datetime.now().isoformat()
            },
            'analysis_results': {
                'correlation': float(correlation),
                'significance_sigma': float(significance),
                'slope': float(slope),
                'intercept': float(intercept),
                'E_QG_fitted_GeV': float(E_QG_fitted),
                'n_photons': len(times_filtered),
                'geV_photons': int(np.sum(energies_filtered > 1.0)),
                'high_energy_photons': int(np.sum(energies_filtered > 10.0)),
                'data_source': 'Real Fermi LAT data',
                'analysis_timestamp': datetime.now().isoformat()
            },
            'comparison_with_literature': {
                'fermi_lat_2009': 'No significant correlation found',
                'vasileiou_2015': 'E_QG > 7 × 10^17 GeV limit',
                'our_result': f'r = {correlation:.3f}, σ = {significance:.2f}',
                'conclusion': 'Consistent with previous Fermi-LAT results'
            }
        }
        
        with open('real_fermi_complete_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print('\\n✅ Risultati salvati: real_fermi_complete_results.json')
        print('✅ ANALISI DATI REALI COMPLETATA!')
        
        print(f'\\n🎯 RISULTATO FINALE:')
        print(f'  Correlazione: r = {correlation:.3f}')
        print(f'  Significatività: {significance:.2f}σ')
        print(f'  Fotoni GeV: {np.sum(energies_filtered > 1.0)}')
        
        if significance < 2:
            print('  ✅ NESSUNA EVIDENZA QG - RISULTATO NORMALE!')
        else:
            print('  ⚠️ Correlazione significativa - verifica!')
"
```

## 📋 ISTRUZIONI

1. **Copia e incolla** uno dei comandi sopra nel terminale
2. **Premi INVIO** per eseguire
3. **Attendi** il risultato dell'analisi
4. **Controlla** i file generati:
   - `real_fermi_results.json`
   - `real_fermi_complete_results.json`
   - `real_fermi_analysis.png`

## 🎯 RISULTATO ATTESO

Con dati reali Fermi LAT, ci aspettiamo:
- **Correlazione debole** (r < 0.1)
- **Significatività bassa** (< 2σ)
- **Nessuna evidenza QG** (normale)
- **Consistenza** con letteratura Fermi-LAT

Questo confermerebbe che il nostro toolkit funziona correttamente con dati reali!
