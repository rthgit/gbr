"""
BATCH ULTIMATE VALIDATION - TUTTI I GRB
Applica la stessa ultimate validation a tutti i 4 GRB
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr, kendalltau
from astropy.io import fits
import json
from datetime import datetime

print("="*70)
print("BATCH ULTIMATE VALIDATION - MULTI-GRB ANALYSIS")
print("="*70)

# Configurazione GRB
GRBS = {
    'GRB090902': {
        'filename': 'L251020161615F357373F52_EV00.fits',
        'name': 'GRB090902B',
        'type': 'Long'
    },
    'GRB080916C': {
        'filename': 'L251020154246F357373F64_EV00.fits',
        'name': 'GRB080916C',
        'type': 'Long'
    },
    'GRB130427A': {
        'filename': 'L251020164901F357373F96_EV00.fits',
        'name': 'GRB130427A',
        'type': 'Long'
    },
    'GRB090510': {
        'filename': 'L251020161912F357373F19_EV00.fits',
        'name': 'GRB090510',
        'type': 'Short'
    }
}

def analyze_grb_ultimate(filename, grb_name):
    """Analisi ultimate validation per un GRB"""
    print(f"\n{'='*70}")
    print(f"🔬 ULTIMATE VALIDATION: {grb_name}")
    print(f"{'='*70}")
    
    try:
        # Carica dati
        with fits.open(filename) as hdul:
            events_data = hdul['EVENTS'].data
            times = events_data['TIME']
            energies = events_data['ENERGY']
        
        print(f"  📊 Eventi: {len(energies)}")
        print(f"  📊 E_max: {energies.max()/1000:.1f} GeV")
        
        results = {
            'grb_name': grb_name,
            'n_events': len(energies),
            'e_max_gev': energies.max()/1000
        }
        
        # ==============================================
        # 1. CORRELAZIONE BASE (4 METODI)
        # ==============================================
        print(f"\n  🔍 Test correlazione multipli...")
        
        # Pearson
        r_pearson, _ = pearsonr(energies, times)
        sig_pearson = abs(r_pearson) * np.sqrt(len(energies) - 2) / np.sqrt(1 - r_pearson**2)
        
        # Spearman
        r_spearman, p_spearman = spearmanr(energies, times)
        sig_spearman = abs(r_spearman) * np.sqrt(len(energies) - 2) / np.sqrt(1 - r_spearman**2)
        
        # Kendall
        r_kendall, p_kendall = kendalltau(energies, times)
        sig_kendall = abs(r_kendall) * np.sqrt(9 * len(energies) * (len(energies) - 1) / (2 * (2 * len(energies) + 5)))
        
        results['correlations'] = {
            'pearson': {'r': r_pearson, 'sig': sig_pearson},
            'spearman': {'r': r_spearman, 'sig': sig_spearman, 'p': p_spearman},
            'kendall': {'r': r_kendall, 'sig': sig_kendall, 'p': p_kendall}
        }
        
        print(f"    Pearson:  {sig_pearson:.2f}σ")
        print(f"    Spearman: {sig_spearman:.2f}σ (p={p_spearman:.2e})")
        print(f"    Kendall:  {sig_kendall:.2f}σ (p={p_kendall:.2e})")
        
        # ==============================================
        # 2. FILTRI ENERGETICI
        # ==============================================
        print(f"\n  🔍 Test filtri energetici...")
        
        energy_thresholds = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0]  # GeV
        results['energy_filters'] = {}
        
        for e_thr in energy_thresholds:
            mask = energies > e_thr * 1000  # Convert to MeV
            if np.sum(mask) > 50:  # Almeno 50 fotoni
                e_filt = energies[mask]
                t_filt = times[mask]
                
                r, _ = pearsonr(e_filt, t_filt)
                sig = abs(r) * np.sqrt(len(e_filt) - 2) / np.sqrt(1 - r**2)
                
                results['energy_filters'][f'{e_thr:.1f}gev'] = {
                    'n_photons': int(np.sum(mask)),
                    'significance': sig
                }
                
                if sig > 2.0:
                    print(f"    ✅ >{e_thr:.1f} GeV: {sig:.2f}σ ({np.sum(mask)} fotoni)")
                elif sig > 1.0:
                    print(f"    ⚠️ >{e_thr:.1f} GeV: {sig:.2f}σ ({np.sum(mask)} fotoni)")
        
        # ==============================================
        # 3. BANDE TEMPORALI
        # ==============================================
        print(f"\n  🔍 Test bande temporali...")
        
        time_range = times.max() - times.min()
        time_quarters = np.percentile(times, [0, 25, 50, 75, 100])
        
        results['temporal_bands'] = {}
        
        temporal_tests = {
            'early': (times < time_quarters[1]),
            'mid': ((times >= time_quarters[1]) & (times < time_quarters[3])),
            'late': (times >= time_quarters[3])
        }
        
        for band_name, mask in temporal_tests.items():
            if np.sum(mask) > 50:
                e_band = energies[mask]
                t_band = times[mask]
                
                r, _ = pearsonr(e_band, t_band)
                sig = abs(r) * np.sqrt(len(e_band) - 2) / np.sqrt(1 - r**2)
                
                results['temporal_bands'][band_name] = {
                    'n_photons': int(np.sum(mask)),
                    'significance': sig
                }
                
                if sig > 2.0:
                    print(f"    ✅ {band_name.capitalize()}: {sig:.2f}σ ({np.sum(mask)} fotoni)")
                elif sig > 1.0:
                    print(f"    ⚠️ {band_name.capitalize()}: {sig:.2f}σ ({np.sum(mask)} fotoni)")
        
        # ==============================================
        # 4. HIGH-ENERGY SUBSET (>1 GeV)
        # ==============================================
        print(f"\n  🔍 Test high-energy subset...")
        
        mask_high = energies > 1000  # >1 GeV
        if np.sum(mask_high) > 30:
            e_high = energies[mask_high]
            t_high = times[mask_high]
            
            r_high, _ = pearsonr(e_high, t_high)
            sig_high = abs(r_high) * np.sqrt(len(e_high) - 2) / np.sqrt(1 - r_high**2)
            
            results['high_energy'] = {
                'n_photons': int(np.sum(mask_high)),
                'significance': sig_high,
                'correlation': r_high
            }
            
            if sig_high > 2.0:
                print(f"    ✅ >1 GeV: {sig_high:.2f}σ ({np.sum(mask_high)} fotoni)")
            else:
                print(f"    ⚠️ >1 GeV: {sig_high:.2f}σ ({np.sum(mask_high)} fotoni)")
        else:
            print(f"    ❌ >1 GeV: Troppo pochi fotoni ({np.sum(mask_high)})")
            results['high_energy'] = None
        
        # ==============================================
        # 5. BOOTSTRAP TEST (100 iter per velocità)
        # ==============================================
        print(f"\n  🔍 Bootstrap test...")
        
        n_bootstrap = 100
        bootstrap_sigs = []
        
        for _ in range(n_bootstrap):
            idx = np.random.choice(len(energies), size=len(energies), replace=True)
            e_boot = energies[idx]
            t_boot = times[idx]
            
            r, _ = pearsonr(e_boot, t_boot)
            sig = abs(r) * np.sqrt(len(e_boot) - 2) / np.sqrt(1 - r**2)
            bootstrap_sigs.append(sig)
        
        bootstrap_mean = np.mean(bootstrap_sigs)
        bootstrap_std = np.std(bootstrap_sigs)
        
        results['bootstrap'] = {
            'mean': bootstrap_mean,
            'std': bootstrap_std,
            'ci_95': [np.percentile(bootstrap_sigs, 2.5), np.percentile(bootstrap_sigs, 97.5)]
        }
        
        print(f"    Mean: {bootstrap_mean:.2f}σ ± {bootstrap_std:.2f}σ")
        print(f"    95% CI: [{results['bootstrap']['ci_95'][0]:.2f}, {results['bootstrap']['ci_95'][1]:.2f}]σ")
        
        # ==============================================
        # 6. RANDOM DATA TEST (100 iter)
        # ==============================================
        print(f"\n  🔍 Random data test...")
        
        n_random = 100
        random_sigs = []
        
        for _ in range(n_random):
            e_rand = np.random.permutation(energies)
            
            r, _ = pearsonr(e_rand, times)
            sig = abs(r) * np.sqrt(len(e_rand) - 2) / np.sqrt(1 - r**2)
            random_sigs.append(sig)
        
        random_mean = np.mean(random_sigs)
        fp_rate_2sig = np.sum(np.array(random_sigs) > 2) / len(random_sigs)
        fp_rate_3sig = np.sum(np.array(random_sigs) > 3) / len(random_sigs)
        
        results['random_data'] = {
            'mean': random_mean,
            'fp_rate_2sigma': fp_rate_2sig,
            'fp_rate_3sigma': fp_rate_3sig
        }
        
        print(f"    Mean null: {random_mean:.2f}σ")
        print(f"    FP rate 2σ: {fp_rate_2sig*100:.1f}%")
        print(f"    FP rate 3σ: {fp_rate_3sig*100:.1f}%")
        
        # ==============================================
        # SUMMARY
        # ==============================================
        print(f"\n  {'='*66}")
        print(f"  🎯 SUMMARY {grb_name}")
        print(f"  {'='*66}")
        print(f"  Pearson:      {sig_pearson:.2f}σ")
        print(f"  Spearman:     {sig_spearman:.2f}σ")
        print(f"  Bootstrap:    {bootstrap_mean:.2f}σ ± {bootstrap_std:.2f}σ")
        print(f"  Null test:    {random_mean:.2f}σ")
        
        # Determina se c'è anomalia
        anomaly_detected = (
            sig_pearson > 3.0 or 
            sig_spearman > 3.0 or
            bootstrap_mean > 3.0
        )
        
        results['anomaly_detected'] = anomaly_detected
        
        if anomaly_detected:
            print(f"  ✅ ANOMALIA RILEVATA!")
        elif sig_pearson > 2.0 or sig_spearman > 2.0:
            print(f"  ⚠️ SEGNALE MARGINALE")
        else:
            print(f"  ❌ NESSUNA ANOMALIA SIGNIFICATIVA")
        
        return results
        
    except Exception as e:
        print(f"  ❌ Errore: {e}")
        return None

# ==============================================
# ANALISI BATCH
# ==============================================
all_results = {}

for grb_id, grb_info in GRBS.items():
    try:
        result = analyze_grb_ultimate(grb_info['filename'], grb_info['name'])
        if result:
            all_results[grb_id] = result
    except FileNotFoundError:
        print(f"\n❌ File non trovato per {grb_id}: {grb_info['filename']}")

# ==============================================
# CONFRONTO FINALE
# ==============================================
print("\n" + "="*70)
print("🎯 CONFRONTO FINALE - TUTTI I GRB")
print("="*70)

print(f"\n{'GRB':<15} {'Events':<8} {'Pearson':<10} {'Spearman':<10} {'Bootstrap':<12} {'Anomaly':<10}")
print("-"*70)

for grb_id, res in all_results.items():
    if res:
        grb_name = GRBS[grb_id]['name']
        n_events = res['n_events']
        sig_p = res['correlations']['pearson']['sig']
        sig_s = res['correlations']['spearman']['sig']
        boot = f"{res['bootstrap']['mean']:.1f}±{res['bootstrap']['std']:.1f}"
        anomaly = "✅ YES" if res['anomaly_detected'] else "❌ NO"
        
        print(f"{grb_name:<15} {n_events:<8} {sig_p:<10.2f} {sig_s:<10.2f} {boot:<12} {anomaly:<10}")

# Identifica pattern comuni
print(f"\n{'='*70}")
print("🔍 PATTERN ANALYSIS")
print("="*70)

# Check quanti hanno segnale >2σ
n_above_2sigma = sum(1 for res in all_results.values() 
                     if res and (res['correlations']['pearson']['sig'] > 2.0 or 
                                res['correlations']['spearman']['sig'] > 2.0))

print(f"\n📊 GRB con segnale >2σ: {n_above_2sigma}/{len(all_results)}")

# Check correlazione con numero eventi
if len(all_results) >= 3:
    events_list = [res['n_events'] for res in all_results.values() if res]
    sigs_list = [res['correlations']['pearson']['sig'] for res in all_results.values() if res]
    
    if len(events_list) == len(sigs_list):
        r_events_sig = np.corrcoef(events_list, sigs_list)[0, 1]
        print(f"📊 Correlazione (n_eventi vs significatività): r={r_events_sig:.3f}")
        
        if r_events_sig > 0.5:
            print("   ✅ Segnale più forte con più eventi (power-dependent)")
        else:
            print("   ⚠️ Segnale NON dipende fortemente da numero eventi")

# Salva risultati
output = {
    'timestamp': datetime.now().isoformat(),
    'grbs_analyzed': len(all_results),
    'results': all_results
}

with open('batch_ultimate_validation.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n✅ Risultati salvati: batch_ultimate_validation.json")

# ==============================================
# VISUALIZZAZIONE
# ==============================================
print(f"\n📊 Creazione grafici comparativi...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Multi-GRB Ultimate Validation Comparison', fontsize=16, fontweight='bold')

# Plot 1: Significance comparison
ax = axes[0, 0]
grb_names = [GRBS[gid]['name'] for gid in all_results.keys() if all_results[gid]]
pearson_sigs = [all_results[gid]['correlations']['pearson']['sig'] for gid in all_results.keys() if all_results[gid]]
spearman_sigs = [all_results[gid]['correlations']['spearman']['sig'] for gid in all_results.keys() if all_results[gid]]

x = np.arange(len(grb_names))
width = 0.35

ax.bar(x - width/2, pearson_sigs, width, label='Pearson', alpha=0.8)
ax.bar(x + width/2, spearman_sigs, width, label='Spearman', alpha=0.8)
ax.axhline(y=3, color='r', linestyle='--', label='3σ threshold')
ax.axhline(y=5, color='g', linestyle='--', label='5σ threshold')
ax.set_xlabel('GRB')
ax.set_ylabel('Significance (σ)')
ax.set_title('Correlation Significance Comparison')
ax.set_xticks(x)
ax.set_xticklabels(grb_names, rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Bootstrap distributions
ax = axes[0, 1]
for gid in all_results.keys():
    if all_results[gid] and 'bootstrap' in all_results[gid]:
        boot = all_results[gid]['bootstrap']
        ax.errorbar(all_results[gid]['n_events'], boot['mean'], 
                   yerr=boot['std'], fmt='o', markersize=8,
                   label=GRBS[gid]['name'], alpha=0.7)

ax.axhline(y=3, color='r', linestyle='--', alpha=0.5)
ax.set_xlabel('Number of Events')
ax.set_ylabel('Bootstrap Mean Significance (σ)')
ax.set_title('Bootstrap Stability vs Sample Size')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Energy filters
ax = axes[1, 0]
for gid in all_results.keys():
    if all_results[gid] and 'energy_filters' in all_results[gid]:
        filters = all_results[gid]['energy_filters']
        energies_thr = [float(k.replace('gev','')) for k in filters.keys()]
        sigs = [filters[k]['significance'] for k in filters.keys()]
        ax.plot(energies_thr, sigs, marker='o', label=GRBS[gid]['name'], alpha=0.7)

ax.axhline(y=3, color='r', linestyle='--', alpha=0.5)
ax.set_xlabel('Energy Threshold (GeV)')
ax.set_ylabel('Significance (σ)')
ax.set_title('Significance vs Energy Threshold')
ax.set_xscale('log')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Temporal bands
ax = axes[1, 1]
temporal_bands_names = ['early', 'mid', 'late']
for gid in all_results.keys():
    if all_results[gid] and 'temporal_bands' in all_results[gid]:
        bands = all_results[gid]['temporal_bands']
        sigs = [bands[b]['significance'] if b in bands else 0 for b in temporal_bands_names]
        ax.plot(temporal_bands_names, sigs, marker='o', markersize=8,
               label=GRBS[gid]['name'], alpha=0.7)

ax.axhline(y=3, color='r', linestyle='--', alpha=0.5)
ax.set_xlabel('Temporal Band')
ax.set_ylabel('Significance (σ)')
ax.set_title('Temporal Evolution of Signal')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('batch_ultimate_validation.png', dpi=300, bbox_inches='tight')
print(f"✅ Grafici salvati: batch_ultimate_validation.png")

print("\n" + "="*70)
print("✅ BATCH ULTIMATE VALIDATION COMPLETATA!")
print("="*70)
