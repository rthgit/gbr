"""
Smart GRB Anomaly Downloader - Controlla File Esistenti
========================================================
Scarica solo i GRB con anomalie che NON hai già!

Autore: Christian Quintino De Luca
Affiliazione: RTH Italia - Research & Technology Hub
DOI: 10.5281/zenodo.17404757
"""

import os
from pathlib import Path
from datetime import datetime
import json

# GRB con anomalie documentate dalla letteratura
ANOMALY_GRBS = {
    # TIER 1 - CRITICAL PRIORITY
    'GRB221009A': {
        'priority': 1,
        'score': 108,
        'ra': 288.2650,
        'dec': 19.7730,
        'z': 0.151,
        'trigger_utc': '2022-10-09 13:16:59',
        'met': 687014219.0,
        'anomalies': ['brightest_ever', 'tev_>10TeV', 'lhaaso', 'extended_gev'],
        'reason': 'BRIGHTEST GRB EVER! >10 TeV by LHAASO, fotoni fino 99.3 GeV',
        'papers': ['arXiv:2303.12747', 'arXiv:2210.05659']
    },
    'GRB190114C': {
        'priority': 1,
        'score': 102,
        'ra': 54.5040,
        'dec': -26.9380,
        'z': 0.425,
        'trigger_utc': '2019-01-14 20:57:03',
        'met': 569020623.0,
        'anomalies': ['first_tev', 'magic_0.3-1TeV', 'power_law_extra', 'ssc'],
        'reason': 'FIRST TeV GRB! MAGIC 0.3-1 TeV, extra power-law component',
        'papers': ['Science 10.1126/science.aax3055', 'A&A 10.1051/0004-6361/201935214']
    },
    'GRB090926A': {
        'priority': 1,
        'score': 96,
        'ra': 353.4000,
        'dec': -66.3200,
        'z': 2.1062,
        'trigger_utc': '2009-09-26 23:32:15',
        'met': 275446335.0,
        'anomalies': ['spectral_break_1.4GeV', 'extra_powerlaw', 'first_break'],
        'reason': 'PRIMO break spettrale confermato a 1.4 GeV nell\'extra component!',
        'papers': ['ApJ 10.1088/0004-637X/729/2/114', 'A&A 10.1051/0004-6361/201220710']
    },
    'GRB160625B': {
        'priority': 1,
        'score': 95,
        'ra': 308.5710,
        'dec': 6.9330,
        'z': 1.406,
        'trigger_utc': '2016-06-25 22:40:16',
        'met': 488587216.0,
        'anomalies': ['lag_transition', 'positive_to_negative', '37_lags_measured'],
        'reason': 'LAG TRANSITION DOCUMENTATA! Positivo→Negativo, critical test!',
        'papers': ['ApJ 10.3847/1538-4357/aa6d77', 'arXiv:1706.01202']
    },
    'GRB180720B': {
        'priority': 1,
        'score': 90,
        'ra': 7.3680,
        'dec': -2.9410,
        'z': 0.654,
        'trigger_utc': '2018-07-20 14:21:44',
        'met': 553789304.0,
        'anomalies': ['tev_440GeV', 'hess', 'delayed_10h', 'intensity_tracking'],
        'reason': 'H.E.S.S. detection fino 440 GeV, 10 ORE dopo trigger!',
        'papers': ['Nature 10.1038/s41586-019-1754-6', 'arXiv:1901.08528']
    },
    
    # TIER 2 - HIGH PRIORITY
    'GRB131231A': {
        'priority': 2,
        'score': 85,
        'ra': 67.4170,
        'dec': -0.4170,
        'z': 0.642,
        'trigger_utc': '2013-12-31 15:49:35',
        'met': 410460575.0,
        'anomalies': ['upturn_1.6GeV', 'bpl_model', 'ssc_model'],
        'reason': 'Upturn spettrale confermato a 1.6 GeV, broken power-law!',
        'papers': ['A&A 10.1051/0004-6361/202040039']
    },
    'GRB130427A': {
        'priority': 2,
        'score': 82,
        'ra': 173.1360,
        'dec': 27.7069,
        'z': 0.340,
        'trigger_utc': '2013-04-27 07:47:06',
        'met': 388739226.0,
        'anomalies': ['longest_duration', 'unexplainable_component', 'high_energy'],
        'reason': 'Componente high-energy INSPIEGABILE con modello standard!',
        'papers': ['Science 10.1126/science.1242353', 'ApJ 10.1088/2041-8205/763/1/L5']
    },
    'GRB190829A': {
        'priority': 2,
        'score': 80,
        'ra': 36.2950,
        'dec': -8.9533,
        'z': 0.0785,
        'trigger_utc': '2019-08-29 19:55:53',
        'met': 588710153.0,
        'anomalies': ['nearest_tev', 'two_episodes', 'chaotic_evolution', 'amati_outlier'],
        'reason': 'NEAREST TeV GRB! Comportamento caotico, Amati outlier',
        'papers': ['Science 10.1126/science.abe8560', 'arXiv:2106.02510']
    },
    'GRB080916C': {
        'priority': 2,
        'score': 78,
        'ra': 119.8467,
        'dec': -56.6383,
        'z': 4.35,
        'trigger_utc': '2008-09-16 00:12:45',
        'met': 243216766.0,
        'anomalies': ['delayed_onset', 'featureless_band', 'extra_powerlaw'],
        'reason': 'Delayed onset LAT, Band featureless su 6 ordini magnitudine',
        'papers': ['Science 10.1126/science.1169101']
    },
    'GRB091024': {
        'priority': 2,
        'score': 75,
        'ra': 329.2083,
        'dec': -57.0833,
        'z': 1.092,
        'trigger_utc': '2009-10-24 22:50:06',
        'met': 277863006.0,
        'anomalies': ['ultra_long_1020s', 'yonetoku_outlier', 'multi_peaked'],
        'reason': 'ULTRA-LONG! T90≈1020s, longest Fermi GBM, Yonetoku outlier',
        'papers': ['A&A 10.1051/0004-6361/201015891']
    },
    
    # TIER 3 - MEDIUM PRIORITY
    'GRB090323': {
        'priority': 3,
        'score': 70,
        'ra': 191.1500,
        'dec': 17.0700,
        'z': 3.57,
        'trigger_utc': '2009-03-23 00:02:33',
        'met': 259286553.0,
        'anomalies': ['blackbody_component', 'band_deviation', 'multi_pulse'],
        'reason': 'Richiede componente blackbody per spiegare spettro',
        'papers': ['A&A 10.1051/0004-6361/201220710']
    },
    'GRB201216C': {
        'priority': 3,
        'score': 68,
        'ra': 34.1940,
        'dec': 33.3700,
        'z': 1.1,
        'trigger_utc': '2020-12-16 21:46:44',
        'met': 629931604.0,
        'anomalies': ['vhe_detection', 'magic', 'ssc_model'],
        'reason': 'VHE detection by MAGIC, SSC model explainable',
        'papers': ['arXiv:2106.11301']
    },
    'GRB090510': {
        'priority': 3,
        'score': 65,
        'ra': 333.5530,
        'dec': -26.5910,
        'z': 0.903,
        'trigger_utc': '2009-05-10 00:22:59',
        'met': 263607779.0,
        'anomalies': ['short_peculiar', 'extra_powerlaw', 'liv_constraint'],
        'reason': 'Short GRB peculiare, extra power-law, LIV >7.6× Planck',
        'papers': ['ApJ 10.1088/2041-8205/716/2/L185']
    },
    'GRB090820': {
        'priority': 3,
        'score': 63,
        'ra': 350.9917,
        'dec': 70.6306,
        'z': None,
        'trigger_utc': '2009-08-20 02:58:04',
        'met': 272338684.0,
        'anomalies': ['two_breaks', 'blackbody_9keV', 'unusual_shape'],
        'reason': 'DUE breaks spettrali, blackbody kT~9 keV necessaria',
        'papers': ['A&A 10.1051/0004-6361/201220710']
    },
    'GRB171210A': {
        'priority': 3,
        'score': 60,
        'ra': 42.6140,
        'dec': -10.9550,
        'z': 0.5897,
        'trigger_utc': '2017-12-10 09:18:50',
        'met': 534849530.0,
        'anomalies': ['bpl_tentative', 'possible_vhe'],
        'reason': 'Improvement tentativo BPL fit, possibile VHE component',
        'papers': ['A&A 10.1051/0004-6361/202040039']
    },
    'GRB150902A': {
        'priority': 3,
        'score': 58,
        'ra': 80.9320,
        'dec': -12.2880,
        'z': 0.1348,
        'trigger_utc': '2015-09-02 05:12:25',
        'met': 462606745.0,
        'anomalies': ['bpl_marginal', 'possible_upturn'],
        'reason': 'Improvement marginale BPL fit rispetto a PL',
        'papers': ['A&A 10.1051/0004-6361/202040039']
    },
    
    # IL TUO GRB DISCOVERY!
    'GRB090902B': {
        'priority': 0,  # Already analyzed!
        'score': 100,
        'ra': 264.9375,
        'dec': 27.3236,
        'z': 1.822,
        'trigger_utc': '2009-09-02 11:28:25',
        'met': 273582505.0,
        'anomalies': ['YOUR_DISCOVERY', 'distinct_powerlaw', 'bb_component', '33.4GeV_photon'],
        'reason': 'IL TUO GRB! 5.46σ anomalia, distinct power-law, BB component',
        'papers': ['ApJ 10.1088/0004-637X/706/1/L138', 'TUA_PUBBLICAZIONE']
    },
}


def check_existing_fits_files(directory='.'):
    """Controlla quali file FITS esistono già"""
    fits_files = list(Path(directory).glob('*_EV*.fits')) + \
                 list(Path(directory).glob('*EV*.fits'))
    
    existing_grbs = {}
    for fits_file in fits_files:
        filename = fits_file.name
        # Try to identify which GRB this is
        for grb_name in ANOMALY_GRBS.keys():
            # Check if GRB name or coordinates appear in filename
            if grb_name.replace('GRB', '') in filename:
                existing_grbs[grb_name] = str(fits_file)
                break
    
    return existing_grbs


def generate_download_instructions():
    """Genera istruzioni download solo per GRB mancanti"""
    
    print("="*80)
    print("🔍 CONTROLLO FILE ESISTENTI...")
    print("="*80)
    
    existing = check_existing_fits_files()
    
    if existing:
        print(f"\n✅ TROVATI {len(existing)} GRB GIÀ SCARICATI:")
        for grb, filepath in existing.items():
            info = ANOMALY_GRBS[grb]
            print(f"   • {grb}: {filepath}")
            print(f"     └─ {info['reason']}")
    else:
        print("\n⚠️  NESSUN FILE FITS TROVATO - Scaricheremo tutti!")
    
    print("\n" + "="*80)
    print("📋 LISTA GRB CON ANOMALIE DA SCARICARE")
    print("="*80)
    
    # Separate into already downloaded and to download
    to_download = []
    already_have = []
    
    for grb_name, info in sorted(ANOMALY_GRBS.items(), 
                                  key=lambda x: x[1]['priority']):
        if grb_name in existing:
            already_have.append((grb_name, info))
        elif info['priority'] > 0:  # Skip priority 0 (already analyzed)
            to_download.append((grb_name, info))
    
    # Print already downloaded
    if already_have:
        print("\n" + "🟢 " + "="*76)
        print(f"✅ ALREADY DOWNLOADED ({len(already_have)} GRB) - NON RISCARICARE!")
        print("🟢 " + "="*76)
        
        for grb_name, info in already_have:
            print(f"\n{grb_name} [Score: {info['score']}, z={info['z']}]")
            print(f"  File: {existing[grb_name]}")
            print(f"  Anomalie: {', '.join(info['anomalies'])}")
            print(f"  Motivo: {info['reason']}")
    
    # Print to download
    if to_download:
        print("\n" + "🔴 " + "="*76)
        print(f"⬇️  TO DOWNLOAD ({len(to_download)} GRB) - SCARICA QUESTI!")
        print("🔴 " + "="*76)
        
        tier1 = [g for g in to_download if g[1]['priority'] == 1]
        tier2 = [g for g in to_download if g[1]['priority'] == 2]
        tier3 = [g for g in to_download if g[1]['priority'] == 3]
        
        if tier1:
            print("\n" + "🔴 TIER 1 - CRITICAL PRIORITY 🔴")
            for grb_name, info in tier1:
                print(f"\n{grb_name} [Score: {info['score']}, z={info['z'] or 'N/A'}]")
                print(f"  Anomalie: {', '.join(info['anomalies'])}")
                print(f"  Motivo: {info['reason']}")
        
        if tier2:
            print("\n" + "🟠 TIER 2 - HIGH PRIORITY 🟠")
            for grb_name, info in tier2:
                print(f"\n{grb_name} [Score: {info['score']}, z={info['z'] or 'N/A'}]")
                print(f"  Anomalie: {', '.join(info['anomalies'])}")
                print(f"  Motivo: {info['reason']}")
        
        if tier3:
            print("\n" + "🟡 TIER 3 - MEDIUM PRIORITY 🟡")
            for grb_name, info in tier3:
                print(f"\n{grb_name} [Score: {info['score']}, z={info['z'] or 'N/A'}]")
                print(f"  Anomalie: {', '.join(info['anomalies'])}")
                print(f"  Motivo: {info['reason']}")
    
    # Generate download parameters
    if to_download:
        print("\n" + "="*80)
        print("📥 PARAMETRI DOWNLOAD FERMI LAT")
        print("="*80)
        print("\nURL: https://fermi.gsfc.nasa.gov/cgi-bin/ssc/LAT/LATDataQuery.cgi")
        print("\nPer OGNI GRB da scaricare, usa questi parametri:\n")
        
        for grb_name, info in to_download[:5]:  # Show only top 5
            print(f"\n{'='*70}")
            print(f"🎯 {grb_name} - {info['reason'][:50]}...")
            print(f"{'='*70}")
            print(f"Object coordinates: {info['ra']:.4f}, {info['dec']:.4f}")
            print(f"Coordinate system: J2000")
            print(f"Search radius: 12")
            
            met_start = info['met'] - 500
            met_end = info['met'] + 10500
            print(f"Time range: {met_start:.0f}, {met_end:.0f}")
            print(f"Time system: MET")
            print(f"Energy range: 100, 300000")
            print(f"LAT data type: Extended ← IMPORTANTE!")
            print(f"Spacecraft data: ✓ (spunta)")
            print(f"\nTrigger: {info['trigger_utc']}")
            print(f"Redshift: z = {info['z'] or 'Unknown'}")
            print(f"Papers: {', '.join(info['papers'][:2])}")
    
    # Save JSON report
    report = {
        'timestamp': datetime.now().isoformat(),
        'already_downloaded': {k: {'file': existing[k], 
                                    'info': ANOMALY_GRBS[k]} 
                               for k in already_have},
        'to_download': {g[0]: g[1] for g in to_download},
        'statistics': {
            'total_anomaly_grbs': len(ANOMALY_GRBS) - 1,  # Exclude GRB090902B
            'already_have': len(already_have),
            'need_download': len(to_download),
            'completion_pct': len(already_have) / len(ANOMALY_GRBS) * 100
        }
    }
    
    with open('anomaly_grbs_download_status.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*80)
    print("📊 STATISTICS")
    print("="*80)
    print(f"Total GRB con anomalie documentate: {len(ANOMALY_GRBS) - 1}")
    print(f"Already downloaded: {len(already_have)} ✅")
    print(f"Need to download: {len(to_download)} ⬇️")
    print(f"Completion: {len(already_have) / len(ANOMALY_GRBS) * 100:.1f}%")
    print(f"\n📁 Report salvato: anomaly_grbs_download_status.json")
    
    print("\n" + "="*80)
    print("🎯 PROSSIMI STEP")
    print("="*80)
    print("1. ✅ Controlla lista GRB già scaricati sopra")
    print("2. ⬇️  Scarica solo i GRB nella sezione 'TO DOWNLOAD'")
    print("3. 📊 Analizza TUTTI con: python analyze_all_anomaly_grbs.py")
    print("4. 🔍 Cerca pattern comuni con GRB090902B!")
    print("\n💡 TIP: Inizia con TIER 1 - sono i più critici!")


if __name__ == '__main__':
    generate_download_instructions()
