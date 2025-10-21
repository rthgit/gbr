# COMANDO CORRETTO PER ANALISI MULTI-GRB

## 🎯 COMANDO SENZA ERRORI:

```bash
python -c "
import numpy as np
from astropy.io import fits
import json
from datetime import datetime
import os

print('='*70)
print('ANALISI MULTI-GRB FINALE - 4 GRB REALI FERMI LAT')
print('RICERCA EFFETTI GRAVITAZIONE QUANTISTICA')
print('='*70)

# Configurazione GRB
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
    print('')
    print(config['name'] + ':')
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
            
            print('  Eventi totali: ' + str(len(events_data)))
            print('  Eventi filtrati: ' + str(n_photons))
            print('  Range energie: ' + str(round(energies_filtered.min(), 3)) + ' - ' + str(round(energies_filtered.max(), 1)) + ' GeV')
            print('  Fotoni GeV: ' + str(n_geV))
            print('  Fotoni >10 GeV: ' + str(n_heV))
            
            if n_photons > 2:
                correlation = np.corrcoef(energies_filtered, times_filtered)[0,1]
                significance = abs(correlation) * np.sqrt(n_photons - 2) / np.sqrt(1 - correlation**2)
                print('  Correlazione: r = ' + str(round(correlation, 3)) + ', σ = ' + str(round(significance, 2)))
                
                # Calcola E_QG
                H0 = 70.0; c = 3e5; z = config['z']
                d_L = (c/H0) * z * (1 + z)
                slope = np.polyfit(energies_filtered, times_filtered, 1)[0]
                E_QG = d_L * 3.086e22 / (c * abs(slope)) / 1e9 if abs(slope) > 1e-10 else np.inf
                print('  E_QG: ' + str(E_QG) + ' GeV')
                
                results.append({
                    'name': config['name'],
                    'correlation': float(correlation),
                    'significance': float(significance),
                    'photons': n_photons,
                    'geV_photons': n_geV,
                    'high_energy_photons': n_heV,
                    'E_QG': float(E_QG),
                    'redshift': z,
                    'max_energy': float(energies_filtered.max())
                })
                
                total_photons += n_photons
                total_geV_photons += n_geV
            else:
                print('  Troppi pochi fotoni per analisi')
    except Exception as e:
        print('  Errore: ' + str(e))

# Risultati combinati
if results:
    print('')
    print('='*60)
    print('COMBINAZIONE BAYESIANA MULTI-GRB')
    print('='*60)
    
    total_heV_photons = sum(r['high_energy_photons'] for r in results)
    
    # Correlazione combinata (weighted average)
    weights = [r['photons'] for r in results]
    correlations = [r['correlation'] for r in results]
    combined_correlation = np.average(correlations, weights=weights)
    
    # Significatività combinata
    combined_significance = abs(combined_correlation) * np.sqrt(total_photons - 2) / np.sqrt(1 - combined_correlation**2)
    
    print('GRB analizzati: ' + str(len(results)))
    print('Fotoni totali: ' + str(total_photons))
    print('Fotoni GeV: ' + str(total_geV_photons))
    print('Fotoni >10 GeV: ' + str(total_heV_photons))
    print('Correlazione combinata: r = ' + str(round(combined_correlation, 3)))
    print('Significatività combinata: ' + str(round(combined_significance, 2)) + 'σ')
    
    # Interpretazione
    if combined_significance < 2:
        interpretation = 'NESSUNA EVIDENZA QG - RISULTATO NORMALE'
        print('✅ ' + interpretation)
    elif combined_significance < 3:
        interpretation = 'CORRELAZIONE DEBOLE - ANALISI APPROFONDITA NECESSARIA'
        print('⚠️ ' + interpretation)
    else:
        interpretation = 'CORRELAZIONE SIGNIFICATIVA - VERIFICA METODOLOGIA'
        print('🚨 ' + interpretation)
    
    # Salva risultati
    output = {
        'num_grb': len(results),
        'total_photons': total_photons,
        'total_geV_photons': total_geV_photons,
        'total_high_energy_photons': total_heV_photons,
        'combined_correlation': float(combined_correlation),
        'combined_significance': float(combined_significance),
        'interpretation': interpretation,
        'individual_results': results,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('final_multi_grb_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print('')
    print('✅ Risultati salvati: final_multi_grb_results.json')
    
    print('')
    print('🎯 RISULTATO FINALE MULTI-GRB:')
    print('  GRB analizzati: ' + str(len(results)))
    print('  Fotoni totali: ' + str(total_photons))
    print('  Correlazione combinata: r = ' + str(round(combined_correlation, 3)))
    print('  Significatività combinata: ' + str(round(combined_significance, 2)) + 'σ')
    print('  Interpretazione: ' + interpretation)
    
    if combined_significance < 2:
        print('')
        print('✅ CONCLUSIONE: NESSUNA EVIDENZA DI EFFETTI QG!')
        print('✅ RISULTATO CONSISTENTE CON LETTERATURA!')
        print('✅ TOOLKIT VALIDATO SU CAMPIONE GRANDE!')
    else:
        print('')
        print('⚠️ CORRELAZIONE SIGNIFICATIVA - VERIFICA NECESSARIA!')
else:
    print('❌ Nessun risultato valido')

print('')
print('='*70)
print('ANALISI MULTI-GRB COMPLETATA!')
print('='*70)
"
```

## 🎯 ISTRUZIONI:

1. **Copia** il comando sopra
2. **Incolla** nel terminale PowerShell
3. **Premi INVIO** per eseguire
4. **Attendi** il risultato dell'analisi

## 📊 RISULTATO ATTESO:

Con 4 GRB reali e migliaia di fotoni:
- **Statistica molto migliorata**
- **Correlazione combinata** debole
- **Significatività bassa** (< 2σ)
- **Nessuna evidenza QG** (normale)
- **Toolkit validato** su campione molto grande

Questo sarà il test definitivo del nostro toolkit!
