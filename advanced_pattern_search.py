"""
ADVANCED PATTERN SEARCH
Cerca anomalie nascoste in subset e combinazioni specifiche
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
from astropy.io import fits
import json

print("="*70)
print("ADVANCED PATTERN SEARCH - ANOMALIE NASCOSTE")
print("="*70)

GRBS = {
    'GRB090902': 'L251020161615F357373F52_EV00.fits',
    'GRB080916C': 'L251020154246F357373F64_EV00.fits',
    'GRB130427A': 'L251020164901F357373F96_EV00.fits',
    'GRB090510': 'L251020161912F357373F19_EV00.fits'
}

def find_hidden_anomalies(filename, grb_name):
    """Cerca pattern nascosti con analisi avanzate"""
    print(f"\n{'='*70}")
    print(f"🔍 PATTERN SEARCH: {grb_name}")
    print(f"{'='*70}")
    
    try:
        with fits.open(filename) as hdul:
            events = hdul['EVENTS'].data
            times = events['TIME']
            energies = events['ENERGY']
        
        results = {
            'grb_name': grb_name,
            'n_total': len(energies),
            'patterns_found': []
        }
        
        # ==============================================
        # 1. ULTRA-HIGH ENERGY SUBSET (>10 GeV)
        # ==============================================
        print(f"\n  🔬 Test 1: Ultra-high energy (>10 GeV)")
        
        mask_ultra = energies > 10000
        n_ultra = np.sum(mask_ultra)
        
        if n_ultra >= 10:
            e_ultra = energies[mask_ultra]
            t_ultra = times[mask_ultra]
            
            r, _ = pearsonr(e_ultra, t_ultra)
            sig = abs(r) * np.sqrt(len(e_ultra) - 2) / np.sqrt(1 - r**2) if len(e_ultra) > 2 else 0
            
            print(f"    Fotoni >10 GeV: {n_ultra}")
            print(f"    Significatività: {sig:.2f}σ")
            
            if sig > 2.0:
                results['patterns_found'].append({
                    'type': 'ultra_high_energy',
                    'threshold': '>10 GeV',
                    'n_photons': int(n_ultra),
                    'significance': sig,
                    'priority': 'HIGH'
                })
                print(f"    ✅ PATTERN TROVATO!")
        else:
            print(f"    ❌ Troppo pochi fotoni: {n_ultra}")
        
        # ==============================================
        # 2. ENERGY BINS FINE (10 bins)
        # ==============================================
        print(f"\n  🔬 Test 2: Energy bins fine")
        
        # Dividi in 10 quantili energetici
        energy_quantiles = np.percentile(energies, np.linspace(0, 100, 11))
        
        max_sig_bin = 0
        best_bin = None
        
        for i in range(len(energy_quantiles) - 1):
            mask = (energies >= energy_quantiles[i]) & (energies < energy_quantiles[i+1])
            
            if np.sum(mask) > 30:
                e_bin = energies[mask]
                t_bin = times[mask]
                
                r, _ = pearsonr(e_bin, t_bin)
                sig = abs(r) * np.sqrt(len(e_bin) - 2) / np.sqrt(1 - r**2)
                
                if sig > max_sig_bin:
                    max_sig_bin = sig
                    best_bin = {
                        'range': f"{energy_quantiles[i]/1000:.2f}-{energy_quantiles[i+1]/1000:.2f} GeV",
                        'n_photons': int(np.sum(mask)),
                        'significance': sig
                    }
        
        print(f"    Massima significatività bin: {max_sig_bin:.2f}σ")
        if best_bin:
            print(f"    Best bin: {best_bin['range']} ({best_bin['n_photons']} fotoni)")
        
        if max_sig_bin > 2.5:
            results['patterns_found'].append({
                'type': 'energy_bin',
                **best_bin,
                'priority': 'MEDIUM'
            })
            print(f"    ✅ PATTERN TROVATO IN BIN SPECIFICO!")
        
        # ==============================================
        # 3. TIME WINDOWS SLIDING
        # ==============================================
        print(f"\n  🔬 Test 3: Sliding time windows")
        
        time_range = times.max() - times.min()
        window_size = time_range / 3  # Finestre da 1/3 della durata totale
        
        max_sig_window = 0
        best_window = None
        
        # Test 5 posizioni sovrapposte
        for i in range(5):
            start = times.min() + i * window_size / 4
            end = start + window_size
            
            mask = (times >= start) & (times <= end)
            
            if np.sum(mask) > 50:
                e_win = energies[mask]
                t_win = times[mask]
                
                r, _ = pearsonr(e_win, t_win)
                sig = abs(r) * np.sqrt(len(e_win) - 2) / np.sqrt(1 - r**2)
                
                if sig > max_sig_window:
                    max_sig_window = sig
                    best_window = {
                        'position': f"Window {i+1}/5",
                        'n_photons': int(np.sum(mask)),
                        'significance': sig
                    }
        
        print(f"    Massima significatività window: {max_sig_window:.2f}σ")
        if best_window:
            print(f"    Best window: {best_window['position']} ({best_window['n_photons']} fotoni)")
        
        if max_sig_window > 2.5:
            results['patterns_found'].append({
                'type': 'time_window',
                **best_window,
                'priority': 'MEDIUM'
            })
            print(f"    ✅ PATTERN TROVATO IN FINESTRA TEMPORALE!")
        
        # ==============================================
        # 4. COMBINAZIONE ENERGY + TIME
        # ==============================================
        print(f"\n  🔬 Test 4: Energy-time subset combination")
        
        # Late time + high energy
        time_median = np.median(times)
        energy_75pct = np.percentile(energies, 75)
        
        mask_combo = (times > time_median) & (energies > energy_75pct)
        
        if np.sum(mask_combo) > 30:
            e_combo = energies[mask_combo]
            t_combo = times[mask_combo]
            
            r, _ = pearsonr(e_combo, t_combo)
            sig = abs(r) * np.sqrt(len(e_combo) - 2) / np.sqrt(1 - r**2)
            
            print(f"    Late+High subset: {np.sum(mask_combo)} fotoni")
            print(f"    Significatività: {sig:.2f}σ")
            
            if sig > 2.5:
                results['patterns_found'].append({
                    'type': 'combo_late_high',
                    'n_photons': int(np.sum(mask_combo)),
                    'significance': sig,
                    'priority': 'HIGH'
                })
                print(f"    ✅ PATTERN IN COMBINAZIONE LATE+HIGH!")
        
        # ==============================================
        # 5. NON-LINEAR PATTERNS (Spearman bin-by-bin)
        # ==============================================
        print(f"\n  🔬 Test 5: Non-linear patterns (Spearman)")
        
        # Dividi in 5 bins temporali
        time_bins = np.percentile(times, [0, 20, 40, 60, 80, 100])
        
        max_spearman = 0
        best_spearman_bin = None
        
        for i in range(len(time_bins) - 1):
            mask = (times >= time_bins[i]) & (times < time_bins[i+1])
            
            if np.sum(mask) > 30:
                e_bin = energies[mask]
                t_bin = times[mask]
                
                r, _ = spearmanr(e_bin, t_bin)
                sig = abs(r) * np.sqrt(len(e_bin) - 2) / np.sqrt(1 - r**2)
                
                if sig > max_spearman:
                    max_spearman = sig
                    best_spearman_bin = {
                        'temporal_bin': f"Bin {i+1}/5",
                        'n_photons': int(np.sum(mask)),
                        'significance': sig
                    }
        
        print(f"    Massima Spearman temporale: {max_spearman:.2f}σ")
        
        if max_spearman > 2.5:
            results['patterns_found'].append({
                'type': 'nonlinear_temporal',
                **best_spearman_bin,
                'priority': 'MEDIUM'
            })
            print(f"    ✅ PATTERN NON-LINEARE TROVATO!")
        
        # ==============================================
        # 6. OUTLIER REMOVAL TEST
        # ==============================================
        print(f"\n  🔬 Test 6: Outlier removal analysis")
        
        # Rimuovi outlier energetici (top 5%)
        energy_95pct = np.percentile(energies, 95)
        mask_no_outlier = energies < energy_95pct
        
        e_clean = energies[mask_no_outlier]
        t_clean = times[mask_no_outlier]
        
        r_clean, _ = pearsonr(e_clean, t_clean)
        sig_clean = abs(r_clean) * np.sqrt(len(e_clean) - 2) / np.sqrt(1 - r_clean**2)
        
        # Calcola originale per confronto
        r_orig, _ = pearsonr(energies, times)
        sig_orig = abs(r_orig) * np.sqrt(len(energies) - 2) / np.sqrt(1 - r_orig**2)
        
        print(f"    Originale: {sig_orig:.2f}σ")
        print(f"    Senza outlier: {sig_clean:.2f}σ")
        print(f"    Differenza: {sig_clean - sig_orig:.2f}σ")
        
        if abs(sig_clean - sig_orig) > 1.0:
            results['patterns_found'].append({
                'type': 'outlier_driven',
                'sig_with_outliers': sig_orig,
                'sig_without_outliers': sig_clean,
                'difference': sig_clean - sig_orig,
                'priority': 'INFO'
            })
            
            if sig_clean > sig_orig + 1.0:
                print(f"    ⚠️ Outlier SOPPRIMONO il segnale!")
            elif sig_orig > sig_clean + 1.0:
                print(f"    ⚠️ Outlier GUIDANO il segnale!")
        
        # ==============================================
        # SUMMARY
        # ==============================================
        print(f"\n  {'='*66}")
        print(f"  🎯 SUMMARY PATTERN SEARCH: {grb_name}")
        print(f"  {'='*66}")
        print(f"  Pattern trovati: {len(results['patterns_found'])}")
        
        if results['patterns_found']:
            print(f"\n  🔥 ANOMALIE RILEVATE:")
            for p in results['patterns_found']:
                priority_icon = "🔴" if p['priority'] == 'HIGH' else "🟡" if p['priority'] == 'MEDIUM' else "🔵"
                print(f"    {priority_icon} {p['type']}: {p.get('significance', 'N/A'):.2f}σ")
        else:
            print(f"  ❌ Nessun pattern nascosto significativo")
        
        return results
        
    except Exception as e:
        print(f"  ❌ Errore: {e}")
        return None

# ==============================================
# ANALISI TUTTI I GRB
# ==============================================
all_patterns = {}

for grb_id, filename in GRBS.items():
    try:
        result = find_hidden_anomalies(filename, grb_id)
        if result:
            all_patterns[grb_id] = result
    except FileNotFoundError:
        print(f"\n❌ File non trovato: {filename}")

# ==============================================
# CONFRONTO PATTERN
# ==============================================
print("\n" + "="*70)
print("🔍 ANALISI COMPARATIVA PATTERN")
print("="*70)

total_patterns = sum(len(r['patterns_found']) for r in all_patterns.values() if r)
print(f"\n📊 Pattern totali trovati: {total_patterns}")

# Conta per tipo
pattern_types = {}
for res in all_patterns.values():
    if res:
        for p in res['patterns_found']:
            ptype = p['type']
            if ptype not in pattern_types:
                pattern_types[ptype] = []
            pattern_types[ptype].append({
                'grb': res['grb_name'],
                'sig': p.get('significance', 0),
                'priority': p['priority']
            })

if pattern_types:
    print(f"\n📊 Pattern per tipo:")
    for ptype, instances in pattern_types.items():
        print(f"\n  {ptype}:")
        for inst in instances:
            print(f"    • {inst['grb']}: {inst['sig']:.2f}σ ({inst['priority']})")

# Identifica GRB con più pattern
print(f"\n📊 GRB per numero di pattern:")
for grb_id, res in sorted(all_patterns.items(), 
                          key=lambda x: len(x[1]['patterns_found']) if x[1] else 0, 
                          reverse=True):
    if res:
        n_patterns = len(res['patterns_found'])
        icon = "🔥" if n_patterns >= 3 else "⚠️" if n_patterns >= 1 else "✓"
        print(f"  {icon} {res['grb_name']}: {n_patterns} pattern")

# Salva risultati
output = {
    'total_grbs': len(all_patterns),
    'total_patterns': total_patterns,
    'patterns_by_type': {k: len(v) for k, v in pattern_types.items()},
    'detailed_results': all_patterns
}

with open('advanced_pattern_search.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n✅ Risultati salvati: advanced_pattern_search.json")

# ==============================================
# VISUALIZZAZIONE
# ==============================================
print(f"\n📊 Creazione grafici pattern...")

fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# Plot 1: Pattern count per GRB
ax1 = fig.add_subplot(gs[0, 0])
grb_names = [r['grb_name'] for r in all_patterns.values() if r]
pattern_counts = [len(r['patterns_found']) for r in all_patterns.values() if r]

colors = ['red' if c >= 3 else 'orange' if c >= 1 else 'green' for c in pattern_counts]
ax1.bar(range(len(grb_names)), pattern_counts, color=colors, alpha=0.7)
ax1.set_xticks(range(len(grb_names)))
ax1.set_xticklabels(grb_names, rotation=45, ha='right')
ax1.set_ylabel('Number of Patterns Found')
ax1.set_title('Hidden Patterns per GRB')
ax1.grid(True, alpha=0.3, axis='y')

# Plot 2: Pattern types distribution
ax2 = fig.add_subplot(gs[0, 1])
if pattern_types:
    types = list(pattern_types.keys())
    counts = [len(v) for v in pattern_types.values()]
    
    ax2.barh(types, counts, alpha=0.7, color='steelblue')
    ax2.set_xlabel('Number of Instances')
    ax2.set_title('Pattern Types Distribution')
    ax2.grid(True, alpha=0.3, axis='x')

# Plot 3: Significance heatmap
ax3 = fig.add_subplot(gs[1, :])
if pattern_types:
    # Crea matrice significatività
    grb_list = list(all_patterns.keys())
    type_list = list(pattern_types.keys())
    
    sig_matrix = np.zeros((len(type_list), len(grb_list)))
    
    for i, ptype in enumerate(type_list):
        for j, grb in enumerate(grb_list):
            res = all_patterns[grb]
            if res:
                for p in res['patterns_found']:
                    if p['type'] == ptype:
                        sig_matrix[i, j] = p.get('significance', 0)
    
    im = ax3.imshow(sig_matrix, cmap='YlOrRd', aspect='auto')
    ax3.set_xticks(range(len(grb_list)))
    ax3.set_xticklabels([all_patterns[g]['grb_name'] for g in grb_list], rotation=45, ha='right')
    ax3.set_yticks(range(len(type_list)))
    ax3.set_yticklabels(type_list)
    ax3.set_title('Pattern Significance Heatmap (σ)')
    
    # Aggiungi valori nelle celle
    for i in range(len(type_list)):
        for j in range(len(grb_list)):
            if sig_matrix[i, j] > 0:
                text = ax3.text(j, i, f'{sig_matrix[i, j]:.1f}',
                              ha="center", va="center", color="black", fontsize=9)
    
    plt.colorbar(im, ax=ax3, label='Significance (σ)')

# Plot 4: Priority distribution
ax4 = fig.add_subplot(gs[2, 0])
priorities = ['HIGH', 'MEDIUM', 'INFO']
priority_counts = {p: 0 for p in priorities}

for res in all_patterns.values():
    if res:
        for pattern in res['patterns_found']:
            priority_counts[pattern['priority']] += 1

colors_priority = ['red', 'orange', 'blue']
ax4.bar(priorities, [priority_counts[p] for p in priorities], 
       color=colors_priority, alpha=0.7)
ax4.set_ylabel('Count')
ax4.set_title('Pattern Priority Distribution')
ax4.grid(True, alpha=0.3, axis='y')

# Plot 5: Summary text
ax5 = fig.add_subplot(gs[2, 1])
ax5.axis('off')

summary_text = f"""
PATTERN SEARCH SUMMARY

Total GRBs analyzed: {len(all_patterns)}
Total patterns found: {total_patterns}

GRBs with HIGH priority: {sum(1 for r in all_patterns.values() 
                               if r and any(p['priority']=='HIGH' 
                               for p in r['patterns_found']))}

Most common pattern: {max(pattern_types.items(), 
                          key=lambda x: len(x[1]))[0] 
                          if pattern_types else 'None'}

GRB with most patterns: {max(all_patterns.items(), 
                            key=lambda x: len(x[1]['patterns_found']) 
                            if x[1] else 0)[0] 
                            if all_patterns else 'None'}
"""

ax5.text(0.1, 0.5, summary_text, transform=ax5.transAxes,
        fontsize=11, verticalalignment='center',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.suptitle('Advanced Pattern Search - Hidden Anomalies Analysis', 
            fontsize=14, fontweight='bold')

plt.savefig('advanced_pattern_search.png', dpi=300, bbox_inches='tight')
print(f"✅ Grafici salvati: advanced_pattern_search.png")

print("\n" + "="*70)
print("✅ ADVANCED PATTERN SEARCH COMPLETATA!")
print("="*70)
