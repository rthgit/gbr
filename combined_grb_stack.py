"""
COMBINED GRB STACK ANALYSIS
Stack tutti i fotoni insieme per massimizzare potere statistico
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr, kendalltau
from astropy.io import fits
import json

print("="*70)
print("COMBINED GRB STACK ANALYSIS")
print("Massimizza potere statistico combinando tutti i GRB")
print("="*70)

GRBS = {
    'GRB090902': 'L251020161615F357373F52_EV00.fits',
    'GRB080916C': 'L251020154246F357373F64_EV00.fits',
    'GRB130427A': 'L251020164901F357373F96_EV00.fits',
    'GRB090510': 'L251020161912F357373F19_EV00.fits'
}

# ==============================================
# 1. CARICA TUTTI I DATI
# ==============================================
print(f"\n{'='*70}")
print("📥 CARICAMENTO DATI")
print("="*70)

all_energies = []
all_times = []
all_grb_ids = []

grb_stats = {}

for grb_id, filename in GRBS.items():
    try:
        print(f"\n  Loading {grb_id}...", end=" ")
        with fits.open(filename) as hdul:
            events = hdul['EVENTS'].data
            times = events['TIME']
            energies = events['ENERGY']
        
        # Normalizza tempi per ogni GRB (0 = primo fotone)
        times_norm = times - times.min()
        
        all_energies.extend(energies)
        all_times.extend(times_norm)
        all_grb_ids.extend([grb_id] * len(energies))
        
        grb_stats[grb_id] = {
            'n_events': len(energies),
            'e_max_gev': energies.max() / 1000,
            'duration_s': times_norm.max()
        }
        
        print(f"✅ {len(energies)} eventi")
        
    except FileNotFoundError:
        print(f"❌ File non trovato")

# Converti in array numpy
all_energies = np.array(all_energies)
all_times = np.array(all_times)
all_grb_ids = np.array(all_grb_ids)

print(f"\n{'='*70}")
print(f"📊 DATASET COMBINATO")
print(f"{'='*70}")
print(f"  GRB totali: {len(grb_stats)}")
print(f"  Eventi totali: {len(all_energies)}")
print(f"  Range energia: {all_energies.min()/1000:.3f} - {all_energies.max()/1000:.1f} GeV")

# ==============================================
# 2. CORRELAZIONE STACK COMPLETO
# ==============================================
print(f"\n{'='*70}")
print("🔬 ANALISI STACK COMPLETO")
print("="*70)

# Pearson
r_stack, _ = pearsonr(all_energies, all_times)
sig_stack = abs(r_stack) * np.sqrt(len(all_energies) - 2) / np.sqrt(1 - r_stack**2)

# Spearman
r_spear, p_spear = spearmanr(all_energies, all_times)
sig_spear = abs(r_spear) * np.sqrt(len(all_energies) - 2) / np.sqrt(1 - r_spear**2)

# Kendall
r_kend, p_kend = kendalltau(all_energies, all_times)
sig_kend = abs(r_kend) * np.sqrt(9 * len(all_energies) * (len(all_energies) - 1) / (2 * (2 * len(all_energies) + 5)))

print(f"\n  Pearson:  r={r_stack:.4f}, σ={sig_stack:.2f}")
print(f"  Spearman: r={r_spear:.4f}, σ={sig_spear:.2f}, p={p_spear:.2e}")
print(f"  Kendall:  r={r_kend:.4f}, σ={sig_kend:.2f}, p={p_kend:.2e}")

if sig_stack > 3.0 or sig_spear > 3.0:
    print(f"\n  ✅ SEGNALE SIGNIFICATIVO NELLO STACK!")
elif sig_stack > 2.0 or sig_spear > 2.0:
    print(f"\n  ⚠️ SEGNALE MARGINALE NELLO STACK")
else:
    print(f"\n  ❌ Nessun segnale significativo nello stack completo")

# ==============================================
# 3. STACK PER SUBSET ENERGETICO
# ==============================================
print(f"\n{'='*70}")
print("🔬 ANALISI STACK PER ENERGIA")
print("="*70)

energy_thresholds = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]  # GeV

print(f"\n  {'Threshold':<12} {'N_photons':<12} {'Pearson σ':<12} {'Spearman σ':<12}")
print("  " + "-"*50)

energy_results = {}

for e_thr in energy_thresholds:
    mask = all_energies > e_thr * 1000
    n_filt = np.sum(mask)
    
    if n_filt > 50:
        e_filt = all_energies[mask]
        t_filt = all_times[mask]
        
        r_p, _ = pearsonr(e_filt, t_filt)
        sig_p = abs(r_p) * np.sqrt(len(e_filt) - 2) / np.sqrt(1 - r_p**2)
        
        r_s, _ = spearmanr(e_filt, t_filt)
        sig_s = abs(r_s) * np.sqrt(len(e_filt) - 2) / np.sqrt(1 - r_s**2)
        
        energy_results[e_thr] = {
            'n_photons': int(n_filt),
            'sig_pearson': sig_p,
            'sig_spearman': sig_s
        }
        
        icon = "✅" if max(sig_p, sig_s) > 3.0 else "⚠️" if max(sig_p, sig_s) > 2.0 else "  "
        print(f"  {icon} >{e_thr:<10.1f} {n_filt:<12} {sig_p:<12.2f} {sig_s:<12.2f}")

# ==============================================
# 4. STACK HIGH-ENERGY ONLY (>1 GeV)
# ==============================================
print(f"\n{'='*70}")
print("🔬 STACK HIGH-ENERGY (>1 GeV)")
print("="*70)

mask_high = all_energies > 1000
e_high = all_energies[mask_high]
t_high = all_times[mask_high]
grb_high = all_grb_ids[mask_high]

print(f"\n  Eventi >1 GeV: {len(e_high)}")
print(f"  Da {len(np.unique(grb_high))} GRB diversi")

if len(e_high) > 50:
    r_high, _ = pearsonr(e_high, t_high)
    sig_high = abs(r_high) * np.sqrt(len(e_high) - 2) / np.sqrt(1 - r_high**2)
    
    r_high_s, p_high_s = spearmanr(e_high, t_high)
    sig_high_s = abs(r_high_s) * np.sqrt(len(e_high) - 2) / np.sqrt(1 - r_high_s**2)
    
    print(f"\n  Pearson:  {sig_high:.2f}σ")
    print(f"  Spearman: {sig_high_s:.2f}σ (p={p_high_s:.2e})")
    
    if max(sig_high, sig_high_s) > 3.0:
        print(f"  ✅ SEGNALE SIGNIFICATIVO IN HIGH-ENERGY STACK!")
    elif max(sig_high, sig_high_s) > 2.0:
        print(f"  ⚠️ SEGNALE MARGINALE IN HIGH-ENERGY STACK")

# ==============================================
# 5. BOOTSTRAP STACK
# ==============================================
print(f"\n{'='*70}")
print("🔬 BOOTSTRAP STACK ANALYSIS")
print("="*70)

n_bootstrap = 200
bootstrap_sigs = []

print(f"\n  Running {n_bootstrap} bootstrap iterations...", end=" ")

for i in range(n_bootstrap):
    # Resample con replacement
    idx = np.random.choice(len(all_energies), size=len(all_energies), replace=True)
    e_boot = all_energies[idx]
    t_boot = all_times[idx]
    
    r, _ = pearsonr(e_boot, t_boot)
    sig = abs(r) * np.sqrt(len(e_boot) - 2) / np.sqrt(1 - r**2)
    bootstrap_sigs.append(sig)

print("✅")

boot_mean = np.mean(bootstrap_sigs)
boot_std = np.std(bootstrap_sigs)
boot_ci = [np.percentile(bootstrap_sigs, 2.5), np.percentile(bootstrap_sigs, 97.5)]

print(f"\n  Mean: {boot_mean:.2f}σ ± {boot_std:.2f}σ")
print(f"  95% CI: [{boot_ci[0]:.2f}, {boot_ci[1]:.2f}]σ")
print(f"  Original: {sig_stack:.2f}σ")

if sig_stack > boot_ci[1]:
    print(f"  ✅ Original SOPRA 95% CI bootstrap")
elif sig_stack > boot_mean:
    print(f"  ⚠️ Original sopra media ma dentro CI")

# ==============================================
# 6. PERMUTATION TEST
# ==============================================
print(f"\n{'='*70}")
print("🔬 PERMUTATION TEST")
print("="*70)

n_perm = 200
perm_sigs = []

print(f"\n  Running {n_perm} permutations...", end=" ")

for i in range(n_perm):
    e_perm = np.random.permutation(all_energies)
    
    r, _ = pearsonr(e_perm, all_times)
    sig = abs(r) * np.sqrt(len(e_perm) - 2) / np.sqrt(1 - r**2)
    perm_sigs.append(sig)

print("✅")

perm_mean = np.mean(perm_sigs)
p_value = np.sum(np.array(perm_sigs) >= sig_stack) / n_perm

print(f"\n  Null mean: {perm_mean:.2f}σ")
print(f"  P-value: {p_value:.4f}")
print(f"  Original: {sig_stack:.2f}σ")

if p_value < 0.01:
    print(f"  ✅ ALTAMENTE SIGNIFICATIVO (p<0.01)")
elif p_value < 0.05:
    print(f"  ✅ SIGNIFICATIVO (p<0.05)")
else:
    print(f"  ❌ NON significativo")

# ==============================================
# 7. ANALISI PER GRB TYPE
# ==============================================
print(f"\n{'='*70}")
print("🔬 ANALISI PER TIPO GRB")
print("="*70)

# Long vs Short
long_mask = np.isin(all_grb_ids, ['GRB090902', 'GRB080916C', 'GRB130427A'])
short_mask = np.isin(all_grb_ids, ['GRB090510'])

print(f"\n  Long bursts:")
e_long = all_energies[long_mask]
t_long = all_times[long_mask]

if len(e_long) > 50:
    r_long, _ = pearsonr(e_long, t_long)
    sig_long = abs(r_long) * np.sqrt(len(e_long) - 2) / np.sqrt(1 - r_long**2)
    print(f"    Eventi: {len(e_long)}")
    print(f"    Significatività: {sig_long:.2f}σ")

print(f"\n  Short bursts:")
e_short = all_energies[short_mask]
t_short = all_times[short_mask]

if len(e_short) > 50:
    r_short, _ = pearsonr(e_short, t_short)
    sig_short = abs(r_short) * np.sqrt(len(e_short) - 2) / np.sqrt(1 - r_short**2)
    print(f"    Eventi: {len(e_short)}")
    print(f"    Significatività: {sig_short:.2f}σ")

# ==============================================
# SUMMARY E SAVE
# ==============================================
results = {
    'timestamp': str(np.datetime64('now')),
    'n_grbs': len(grb_stats),
    'n_total_events': int(len(all_energies)),
    'stack_full': {
        'pearson_sig': sig_stack,
        'spearman_sig': sig_spear,
        'kendall_sig': sig_kend
    },
    'energy_thresholds': energy_results,
    'high_energy_stack': {
        'n_events': int(len(e_high)) if len(e_high) > 50 else 0,
        'significance': sig_high if len(e_high) > 50 else 0
    },
    'bootstrap': {
        'mean': boot_mean,
        'std': boot_std,
        'ci_95': boot_ci
    },
    'permutation': {
        'p_value': p_value,
        'null_mean': perm_mean
    }
}

with open('combined_grb_stack.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n✅ Risultati salvati: combined_grb_stack.json")

# ==============================================
# VISUALIZZAZIONE
# ==============================================
print(f"\n📊 Creazione grafici...")

fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Plot 1: Scatter plot stack completo
ax1 = fig.add_subplot(gs[0, :2])

# Colora per GRB
colors_map = {
    'GRB090902': 'red',
    'GRB080916C': 'blue',
    'GRB130427A': 'green',
    'GRB090510': 'purple'
}

for grb_id in np.unique(all_grb_ids):
    mask = all_grb_ids == grb_id
    ax1.scatter(all_energies[mask]/1000, all_times[mask], 
               alpha=0.3, s=10, label=grb_id, color=colors_map.get(grb_id, 'gray'))

ax1.set_xlabel('Energy (GeV)')
ax1.set_ylabel('Time (s, normalized)')
ax1.set_xscale('log')
ax1.set_title(f'Combined Stack: All {len(all_energies)} Photons (σ={sig_stack:.2f})')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Significance vs energy threshold
ax2 = fig.add_subplot(gs[0, 2])

thresholds = list(energy_results.keys())
sigs_p = [energy_results[t]['sig_pearson'] for t in thresholds]
sigs_s = [energy_results[t]['sig_spearman'] for t in thresholds]

ax2.plot(thresholds, sigs_p, 'o-', label='Pearson', linewidth=2)
ax2.plot(thresholds, sigs_s, 's-', label='Spearman', linewidth=2)
ax2.axhline(y=3, color='r', linestyle='--', alpha=0.5, label='3σ')
ax2.axhline(y=5, color='g', linestyle='--', alpha=0.5, label='5σ')
ax2.set_xlabel('Energy Threshold (GeV)')
ax2.set_ylabel('Significance (σ)')
ax2.set_xscale('log')
ax2.set_title('Stack Significance vs Energy Cut')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Bootstrap distribution
ax3 = fig.add_subplot(gs[1, 0])

ax3.hist(bootstrap_sigs, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
ax3.axvline(sig_stack, color='red', linestyle='--', linewidth=2, label=f'Original ({sig_stack:.2f}σ)')
ax3.axvline(boot_mean, color='green', linestyle='--', linewidth=2, label=f'Bootstrap mean ({boot_mean:.2f}σ)')
ax3.set_xlabel('Significance (σ)')
ax3.set_ylabel('Frequency')
ax3.set_title(f'Bootstrap Distribution ({n_bootstrap} iterations)')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# Plot 4: Permutation distribution
ax4 = fig.add_subplot(gs[1, 1])

ax4.hist(perm_sigs, bins=30, alpha=0.7, color='coral', edgecolor='black')
ax4.axvline(sig_stack, color='red', linestyle='--', linewidth=2, label=f'Original ({sig_stack:.2f}σ)')
ax4.axvline(perm_mean, color='blue', linestyle='--', linewidth=2, label=f'Null mean ({perm_mean:.2f}σ)')
ax4.set_xlabel('Significance (σ)')
ax4.set_ylabel('Frequency')
ax4.set_title(f'Permutation Test (p={p_value:.4f})')
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

# Plot 5: GRB contributions
ax5 = fig.add_subplot(gs[1, 2])

grb_names = list(grb_stats.keys())
grb_counts = [grb_stats[g]['n_events'] for g in grb_names]

ax5.pie(grb_counts, labels=grb_names, autopct='%1.1f%%', startangle=90)
ax5.set_title('Event Contribution per GRB')

# Plot 6: High-energy scatter
ax6 = fig.add_subplot(gs[2, :2])

if len(e_high) > 0:
    for grb_id in np.unique(grb_high):
        mask = grb_high == grb_id
        ax6.scatter(e_high[mask]/1000, t_high[mask], 
                   alpha=0.5, s=20, label=grb_id, color=colors_map.get(grb_id, 'gray'))
    
    ax6.set_xlabel('Energy (GeV)')
    ax6.set_ylabel('Time (s, normalized)')
    ax6.set_xscale('log')
    ax6.set_title(f'High-Energy Stack (>1 GeV): {len(e_high)} photons (σ={sig_high:.2f})')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

# Plot 7: Summary text
ax7 = fig.add_subplot(gs[2, 2])
ax7.axis('off')

summary = f"""
COMBINED STACK SUMMARY

Total Events: {len(all_energies)}
Total GRBs: {len(grb_stats)}

FULL STACK:
• Pearson:  {sig_stack:.2f}σ
• Spearman: {sig_spear:.2f}σ
• Kendall:  {sig_kend:.2f}σ

HIGH-ENERGY (>1 GeV):
• Events: {len(e_high) if len(e_high) > 0 else 0}
• Significance: {sig_high:.2f}σ

VALIDATION:
• Bootstrap: {boot_mean:.2f}σ ± {boot_std:.2f}σ
• P-value: {p_value:.4f}

STATUS: {'✅ SIGNIFICANT' if max(sig_stack, sig_spear) > 3 else '⚠️ MARGINAL' if max(sig_stack, sig_spear) > 2 else '❌ NOT SIGNIFICANT'}
"""

ax7.text(0.1, 0.5, summary, transform=ax7.transAxes,
        fontsize=10, verticalalignment='center', family='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.suptitle('Combined GRB Stack Analysis - Maximum Statistical Power', 
            fontsize=14, fontweight='bold')

plt.savefig('combined_grb_stack.png', dpi=300, bbox_inches='tight')
print(f"✅ Grafici salvati: combined_grb_stack.png")

print("\n" + "="*70)
print("✅ COMBINED STACK ANALYSIS COMPLETATA!")
print("="*70)
