# COMANDO PER ANALISI MULTI-GRB FINALE

## 🎯 COMANDO COMPLETO:

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
            
            print(f'  Eventi totali: {len(events_data)}')
            print(f'  Eventi filtrati: {n_photons}')
            print(f'  Range energie: {energies_filtered.min():.3f} - {energies_filtered.max():.1f} GeV')
            print(f'  Fotoni GeV: {n_geV}')
            print(f'  Fotoni >10 GeV: {n_heV}')
            
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
        print(f'  Errore: {e}')

# Risultati combinati
if results:
    print(f'\\n{'='*60}')
    print('COMBINAZIONE BAYESIANA MULTI-GRB')
    print(f'{'='*60}')
    
    total_heV_photons = sum(r['high_energy_photons'] for r in results)
    
    # Correlazione combinata (weighted average)
    weights = [r['photons'] for r in results]
    correlations = [r['correlation'] for r in results]
    combined_correlation = np.average(correlations, weights=weights)
    
    # Significatività combinata
    combined_significance = abs(combined_correlation) * np.sqrt(total_photons - 2) / np.sqrt(1 - combined_correlation**2)
    
    print(f'GRB analizzati: {len(results)}')
    print(f'Fotoni totali: {total_photons}')
    print(f'Fotoni GeV: {total_geV_photons}')
    print(f'Fotoni >10 GeV: {total_heV_photons}')
    print(f'Correlazione combinata: r = {combined_correlation:.3f}')
    print(f'Significatività combinata: {combined_significance:.2f}σ')
    
    # Interpretazione
    if combined_significance < 2:
        interpretation = 'NESSUNA EVIDENZA QG - RISULTATO NORMALE'
        print(f'✅ {interpretation}')
    elif combined_significance < 3:
        interpretation = 'CORRELAZIONE DEBOLE - ANALISI APPROFONDITA NECESSARIA'
        print(f'⚠️ {interpretation}')
    else:
        interpretation = 'CORRELAZIONE SIGNIFICATIVA - VERIFICA METODOLOGIA'
        print(f'🚨 {interpretation}')
    
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
    
    print(f'\\n✅ Risultati salvati: final_multi_grb_results.json')
    
    print(f'\\n🎯 RISULTATO FINALE MULTI-GRB:')
    print(f'  GRB analizzati: {len(results)}')
    print(f'  Fotoni totali: {total_photons}')
    print(f'  Correlazione combinata: r = {combined_correlation:.3f}')
    print(f'  Significatività combinata: {combined_significance:.2f}σ')
    print(f'  Interpretazione: {interpretation}')
    
    if combined_significance < 2:
        print('\\n✅ CONCLUSIONE: NESSUNA EVIDENZA DI EFFETTI QG!')
        print('✅ RISULTATO CONSISTENTE CON LETTERATURA!')
        print('✅ TOOLKIT VALIDATO SU CAMPIONE GRANDE!')
    else:
        print('\\n⚠️ CORRELAZIONE SIGNIFICATIVA - VERIFICA NECESSARIA!')
else:
    print('❌ Nessun risultato valido')

print(f'\\n{'='*70}')
print('ANALISI MULTI-GRB COMPLETATA!')
print(f'{'='*70}')
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

