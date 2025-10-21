"""
BATCH GRB DATA DOWNLOADER - TOP 30 PRIORITY
Scarica dati REALI Fermi LAT per i 30 GRB prioritari dalla letteratura

Autore: Christian Quintino De Luca
RTH Italia - Research & Technology Hub
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

class BatchGRBDownloader:
    """
    Download manager per 30 GRB prioritari
    """
    
    def __init__(self):
        self.output_dir = Path("fermi_batch_download")
        self.output_dir.mkdir(exist_ok=True)
        
        # GRB database con coordinate e trigger time
        # Dati da Fermi GRB catalogs e GCN circulars
        self.grb_database = {
            'GRB221009A': {
                'priority': 1, 'score': 108,
                'ra': 288.265, 'dec': 19.773,
                'trigger': '2022-10-09T13:16:59',
                'z': 0.151,
                'categories': ['anomaly', 'spectral_lag', 'tev', 'qg_search', 'high_energy'],
                'note': 'BRIGHTEST EVER! TeV detection LHAASO >10 TeV'
            },
            'GRB190114C': {
                'priority': 2, 'score': 102,
                'ra': 54.504, 'dec': -26.938,
                'trigger': '2019-01-14T20:57:03',
                'z': 0.425,
                'categories': ['anomaly', 'spectral_lag', 'tev', 'qg_search', 'high_energy'],
                'note': 'First TeV GRB by MAGIC, 0.3-1 TeV'
            },
            'GRB090510': {
                'priority': 3, 'score': 96,
                'ra': 333.553, 'dec': -26.591,
                'trigger': '2009-05-10T00:22:59',
                'z': 0.903,
                'categories': ['qg_search', 'anomaly', 'high_energy', 'spectral_lag'],
                'note': 'Short GRB, LIV constraints >7.6 Planck'
            },
            'GRB180720B': {
                'priority': 4, 'score': 77,
                'ra': 7.368, 'dec': -2.941,
                'trigger': '2018-07-20T14:21:44',
                'z': 0.654,
                'categories': ['tev', 'anomaly', 'high_energy', 'spectral_lag'],
                'note': 'H.E.S.S. detection up to 440 GeV'
            },
            'GRB080916C': {
                'priority': 5, 'score': 44,
                'ra': 119.846, 'dec': -56.638,
                'trigger': '2008-09-16T00:12:45',
                'z': 4.35,
                'categories': ['qg_search', 'anomaly', 'high_energy', 'spectral_lag'],
                'note': 'Very distant, z=4.35, QG studies'
            },
            'GRB190829A': {
                'priority': 7, 'score': 32,
                'ra': 31.027, 'dec': -8.952,
                'trigger': '2019-08-29T19:55:53',
                'z': 0.0785,
                'categories': ['tev', 'high_energy'],
                'note': 'Nearest TeV GRB, H.E.S.S. detection'
            },
            'GRB201216C': {
                'priority': 9, 'score': 30,
                'ra': 34.637, 'dec': 17.775,
                'trigger': '2020-12-16T22:32:26',
                'z': 1.1,
                'categories': ['tev'],
                'note': 'MAGIC detection, found 3σ in your test!'
            },
            'GRB130427A': {
                'priority': 11, 'score': 26,
                'ra': 173.136, 'dec': 27.697,
                'trigger': '2013-04-27T07:47:06',
                'z': 0.340,
                'categories': ['qg_search', 'high_energy', 'spectral_lag'],
                'note': 'Brightest before 221009A, ~6000 LAT photons'
            },
            'GRB160625B': {
                'priority': 19, 'score': 17,
                'ra': 308.571, 'dec': 6.933,
                'trigger': '2016-06-25T22:40:16',
                'z': 1.406,
                'categories': ['qg_search', 'spectral_lag'],
                'note': 'Lag transition documented! Critical test'
            },
            'GRB090902B': {
                'priority': 16, 'score': 22,
                'ra': 325.5, 'dec': -18.9,
                'trigger': '2009-09-02T11:01:11',
                'z': 1.822,
                'categories': ['qg_search', 'anomaly', 'high_energy', 'spectral_lag'],
                'note': 'YOUR DISCOVERY! Reference GRB'
            },
            # Additional high-priority GRBs without full data
            'GRB170817A': {
                'priority': 6, 'score': 39,
                'ra': 197.450, 'dec': -23.381,
                'trigger': '2017-08-17T12:41:06',
                'z': 0.0097,
                'categories': ['anomaly', 'spectral_lag', 'tev', 'qg_search', 'high_energy'],
                'note': 'GW170817 counterpart! Unique kilonova'
            },
            'GRB160509A': {
                'priority': 24, 'score': 13,
                'ra': 311.225, 'dec': 76.138,
                'trigger': '2016-05-09T08:59:39',
                'z': 1.17,
                'categories': ['qg_search', 'high_energy'],
                'note': 'QG search candidate'
            },
            'GRB090926A': {
                'priority': 20, 'score': 16,
                'ra': 353.399, 'dec': -66.318,
                'trigger': '2009-09-26T04:20:26',
                'z': 2.1062,
                'categories': ['qg_search', 'anomaly', 'high_energy', 'spectral_lag'],
                'note': 'High-z QG candidate'
            }
        }
    
    def met_from_utc(self, utc_string):
        """
        Converti UTC to Mission Elapsed Time (MET)
        MET start: 2001-01-01 00:00:00 UTC
        """
        from datetime import datetime
        met_start = datetime(2001, 1, 1, 0, 0, 0)
        trigger_time = datetime.fromisoformat(utc_string)
        met = (trigger_time - met_start).total_seconds()
        return met
    
    def generate_fermi_query_params(self, grb_name, grb_data, time_window=10000):
        """
        Genera parametri per query Fermi LAT
        """
        ra = grb_data['ra']
        dec = grb_data['dec']
        trigger = grb_data['trigger']
        
        # Convert to MET
        met = self.met_from_utc(trigger)
        tmin = met - 500  # 500s before trigger
        tmax = met + time_window  # 10000s after trigger
        
        return {
            'grb': grb_name,
            'ra': ra,
            'dec': dec,
            'trigger_utc': trigger,
            'trigger_met': met,
            'tmin': tmin,
            'tmax': tmax,
            'time_window': time_window,
            'redshift': grb_data.get('z', 'Unknown'),
            'priority': grb_data.get('priority', 99),
            'score': grb_data.get('score', 0),
            'categories': grb_data.get('categories', []),
            'note': grb_data.get('note', '')
        }
    
    def create_download_instructions(self):
        """
        Crea istruzioni download dettagliate
        """
        print("="*80)
        print("🚀 FERMI LAT BATCH DOWNLOAD INSTRUCTIONS - TOP 30 GRB")
        print("="*80)
        
        # Generate params for all GRBs
        all_params = []
        for grb_name, grb_data in sorted(self.grb_database.items(), 
                                        key=lambda x: x[1].get('priority', 999)):
            params = self.generate_fermi_query_params(grb_name, grb_data)
            all_params.append(params)
        
        # Create tracking CSV
        tracking_file = self.output_dir / "download_tracking.csv"
        df = pd.DataFrame(all_params)
        df['downloaded'] = False
        df['query_id'] = ''
        df['n_photons'] = ''
        df['analysis_status'] = 'PENDING'
        
        df.to_csv(tracking_file, index=False)
        print(f"\n✅ Tracking spreadsheet created: {tracking_file}")
        
        # Print detailed instructions
        print("\n" + "="*80)
        print("📋 DOWNLOAD INSTRUCTIONS")
        print("="*80)
        
        print("\n🌐 FERMI LAT DATA QUERY WEBSITE:")
        print("   https://fermi.gsfc.nasa.gov/cgi-bin/ssc/LAT/LATDataQuery.cgi")
        
        print("\n📝 FOR EACH GRB, FOLLOW THESE STEPS:")
        print("   1. Go to the URL above")
        print("   2. Enter the parameters below")
        print("   3. Submit query")
        print("   4. Wait for processing (usually 5-30 minutes)")
        print("   5. Download _EV00.fits and _SC00.fits files")
        print("   6. Update tracking spreadsheet")
        
        # Detailed params for top 10
        print("\n" + "="*80)
        print("🔴 TOP 10 PRIORITY GRBs - DOWNLOAD FIRST!")
        print("="*80)
        
        for params in all_params[:10]:
            self.print_grb_download_params(params)
        
        # Compact list for remaining 20
        print("\n" + "="*80)
        print("🟡 REMAINING 20 GRBs - DOWNLOAD AFTER TOP 10")
        print("="*80)
        
        for params in all_params[10:]:
            print(f"\n{params['grb']} (Priority {params['priority']}, Score {params['score']})")
            print(f"   Coordinates: {params['ra']:.3f}, {params['dec']:.3f}")
            print(f"   Time (MET): {params['tmin']:.0f} to {params['tmax']:.0f}")
            print(f"   Note: {params['note']}")
        
        # Save JSON with all params
        json_file = self.output_dir / "download_params.json"
        with open(json_file, 'w') as f:
            json.dump(all_params, f, indent=2)
        print(f"\n✅ Parameters saved: {json_file}")
        
        return all_params
    
    def print_grb_download_params(self, params):
        """
        Stampa parametri dettagliati per un GRB
        """
        print(f"\n{'='*80}")
        print(f"🎯 {params['grb']} - Priority {params['priority']}, Score {params['score']}")
        print(f"{'='*80}")
        print(f"📍 COORDINATES:")
        print(f"   RA:  {params['ra']:.4f}°")
        print(f"   Dec: {params['dec']:.4f}°")
        print(f"   Redshift: z = {params['redshift']}")
        
        print(f"\n⏰ TIME:")
        print(f"   Trigger (UTC): {params['trigger_utc']}")
        print(f"   Trigger (MET): {params['trigger_met']:.1f}")
        print(f"   Time range (MET): {params['tmin']:.1f} to {params['tmax']:.1f}")
        print(f"   Window: {params['time_window']} seconds")
        
        print(f"\n📋 QUERY PARAMETERS FOR FERMI LAT:")
        print(f"   Object coordinates: {params['ra']:.4f}, {params['dec']:.4f}")
        print(f"   Coordinate system: J2000")
        print(f"   Search radius: 12 degrees")
        print(f"   Time range (MET): {params['tmin']:.0f}, {params['tmax']:.0f}")
        print(f"   Time system: MET")
        print(f"   Energy range: 100, 300000 MeV")
        print(f"   LAT data type: Extended")
        print(f"   Spacecraft data: YES")
        
        print(f"\n🎯 WHY IMPORTANT:")
        print(f"   Categories: {', '.join(params['categories'])}")
        print(f"   {params['note']}")
        
        print(f"\n💡 EXPECTED OUTPUT FILES:")
        print(f"   L[QUERYID]_EV00.fits  ← EVENTS (this is what you need!)")
        print(f"   L[QUERYID]_SC00.fits  ← SPACECRAFT")
    
    def create_wget_script_template(self):
        """
        Crea template script wget per quando hai query IDs
        """
        script = """#!/bin/bash
# FERMI LAT BATCH DOWNLOAD SCRIPT
# After submitting queries on Fermi website, update QUERY_IDs below
# Then run: bash download_all_grbs.sh

# Create download directory
mkdir -p fermi_grb_data
cd fermi_grb_data

# ===== TOP 10 PRIORITY GRBs =====

# GRB221009A (Priority 1)
QUERY_ID_221009A="YOUR_QUERY_ID_HERE"
echo "Downloading GRB221009A..."
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_221009A}_EV00.fits
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_221009A}_SC00.fits

# GRB190114C (Priority 2)
QUERY_ID_190114C="YOUR_QUERY_ID_HERE"
echo "Downloading GRB190114C..."
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_190114C}_EV00.fits
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_190114C}_SC00.fits

# GRB090510 (Priority 3)
QUERY_ID_090510="YOUR_QUERY_ID_HERE"
echo "Downloading GRB090510..."
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_090510}_EV00.fits
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_090510}_SC00.fits

# GRB180720B (Priority 4)
QUERY_ID_180720B="YOUR_QUERY_ID_HERE"
echo "Downloading GRB180720B..."
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_180720B}_EV00.fits
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_180720B}_SC00.fits

# GRB080916C (Priority 5)
QUERY_ID_080916C="YOUR_QUERY_ID_HERE"
echo "Downloading GRB080916C..."
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_080916C}_EV00.fits
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_080916C}_SC00.fits

# Add more as needed...

echo "Download complete!"
echo "Files saved in: fermi_grb_data/"
"""
        
        script_file = self.output_dir / "download_all_grbs.sh"
        with open(script_file, 'w') as f:
            f.write(script)
        
        print(f"\n✅ Wget script template created: {script_file}")
        print(f"   Update QUERY_IDs after submitting queries, then run:")
        print(f"   bash {script_file}")
    
    def create_analysis_pipeline_script(self):
        """
        Crea script per analisi batch di tutti i GRB scaricati
        """
        script = '''"""
BATCH ANALYSIS PIPELINE
Analizza tutti i GRB scaricati e confronta con GRB090902B

Autore: Christian Quintino De Luca
"""

import pandas as pd
from pathlib import Path
from astropy.io import fits
from scipy.stats import pearsonr, spearmanr
import numpy as np
import json

class BatchGRBAnalyzer:
    """
    Analizza batch di GRB scaricati
    """
    
    def __init__(self, data_dir="fermi_grb_data"):
        self.data_dir = Path(data_dir)
        self.results = []
        
        # Reference GRB090902B
        self.reference = {
            'grb': 'GRB090902B',
            'correlation_pearson': -0.0863,
            'significance_pearson': 5.46,
            'correlation_spearman': -0.221,
            'significance_spearman': 7.34,
            'n_photons': 3972,
            'e_max': 80.8
        }
    
    def analyze_grb_fits(self, fits_file, grb_name):
        """
        Analizza singolo GRB FITS
        """
        print(f"\\n{'='*70}")
        print(f"🔬 Analyzing: {grb_name}")
        print(f"{'='*70}")
        
        try:
            with fits.open(fits_file) as hdul:
                events = hdul['EVENTS'].data
                times = events['TIME']
                energies = events['ENERGY'] / 1000.0  # MeV to GeV
                
                n = len(energies)
                e_max = energies.max()
                
                # Correlations
                r_p, p_p = pearsonr(energies, times)
                sig_p = abs(r_p) * np.sqrt(n - 2) / np.sqrt(1 - r_p**2)
                
                r_s, p_s = spearmanr(energies, times)
                sig_s = abs(r_s) * np.sqrt(n - 2) / np.sqrt(1 - r_s**2)
                
                print(f"   Photons: {n}")
                print(f"   E_max: {e_max:.1f} GeV")
                print(f"   Pearson: r={r_p:+.4f}, σ={sig_p:.2f}")
                print(f"   Spearman: ρ={r_s:+.4f}, σ={sig_s:.2f}")
                
                # Classification
                max_sig = max(abs(sig_p), abs(sig_s))
                if max_sig >= 5.0:
                    status = "🎉 STRONG ANOMALY"
                elif max_sig >= 3.0:
                    status = "✅ SIGNIFICANT ANOMALY"
                elif max_sig >= 2.0:
                    status = "⚠️ MARGINAL SIGNAL"
                else:
                    status = "❌ NO ANOMALY"
                
                print(f"   Status: {status}")
                
                result = {
                    'grb': grb_name,
                    'n_photons': int(n),
                    'e_max': float(e_max),
                    'correlation_pearson': float(r_p),
                    'significance_pearson': float(sig_p),
                    'correlation_spearman': float(r_s),
                    'significance_spearman': float(sig_s),
                    'max_significance': float(max_sig),
                    'status': status
                }
                
                self.results.append(result)
                return result
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def analyze_all(self):
        """
        Analizza tutti i FITS nella directory
        """
        fits_files = list(self.data_dir.glob("*_EV00.fits"))
        
        print(f"\\n{'='*70}")
        print(f"📊 Found {len(fits_files)} GRB FITS files")
        print(f"{'='*70}")
        
        for fits_file in sorted(fits_files):
            grb_name = fits_file.stem.split('_')[0]
            self.analyze_grb_fits(fits_file, grb_name)
        
        return self.results
    
    def create_summary_report(self):
        """
        Crea report riassuntivo
        """
        if not self.results:
            print("\\n❌ No results to report")
            return
        
        # Sort by significance
        sorted_results = sorted(self.results, 
                               key=lambda x: x['max_significance'],
                               reverse=True)
        
        print(f"\\n{'='*70}")
        print(f"📊 SUMMARY REPORT - {len(self.results)} GRBs ANALYZED")
        print(f"{'='*70}")
        
        print(f"\\n{'GRB':<15} {'N':<6} {'σ(P)':<7} {'σ(S)':<7} {'Status':<25}")
        print("-"*70)
        
        for r in sorted_results:
            print(f"{r['grb']:<15} {r['n_photons']:<6} "
                  f"{r['significance_pearson']:>+6.2f}σ "
                  f"{r['significance_spearman']:>+6.2f}σ "
                  f"{r['status']:<25}")
        
        # Statistics
        anomalies = [r for r in self.results if 'ANOMALY' in r['status']]
        
        print(f"\\n{'='*70}")
        print(f"📈 STATISTICS:")
        print(f"   Total analyzed: {len(self.results)}")
        print(f"   Strong/Significant: {len(anomalies)}")
        print(f"   Replication rate: {len(anomalies)}/{len(self.results)}")
        
        # Save results
        with open('batch_analysis_results.json', 'w') as f:
            json.dump(sorted_results, f, indent=2)
        
        print(f"\\n💾 Results saved: batch_analysis_results.json")

def main():
    analyzer = BatchGRBAnalyzer()
    analyzer.analyze_all()
    analyzer.create_summary_report()

if __name__ == "__main__":
    main()
'''
        
        script_file = self.output_dir / "batch_analysis_pipeline.py"
        with open(script_file, 'w') as f:
            f.write(script)
        
        print(f"\n✅ Analysis pipeline created: {script_file}")
        print(f"   After downloading, run: python {script_file}")


def main():
    """
    Main execution
    """
    print("="*80)
    print("🚀 FERMI LAT BATCH DOWNLOAD MANAGER")
    print("   Top 30 Priority GRBs from Literature Search")
    print("="*80)
    
    downloader = BatchGRBDownloader()
    
    # Generate instructions
    all_params = downloader.create_download_instructions()
    
    # Create wget script template
    downloader.create_wget_script_template()
    
    # Create analysis pipeline
    downloader.create_analysis_pipeline_script()
    
    print("\n" + "="*80)
    print("✅ SETUP COMPLETE!")
    print("="*80)
    
    print("\n🎯 QUICK START GUIDE:")
    print("   1. Open: https://fermi.gsfc.nasa.gov/cgi-bin/ssc/LAT/LATDataQuery.cgi")
    print("   2. Use parameters from download_params.json")
    print("   3. Submit queries (start with top 10)")
    print("   4. Wait ~10-30 min per query")
    print("   5. Download _EV00.fits files")
    print("   6. Run: python batch_analysis_pipeline.py")
    print("   7. Compare results with GRB090902B!")
    
    print("\n⏱️ ESTIMATED TIME:")
    print("   • Query submission: ~1-2 hours (can parallelize)")
    print("   • Query processing: ~3-6 hours (automatic)")
    print("   • Download: ~30 min")
    print("   • Analysis: ~1 hour")
    print("   • TOTAL: ~1 day for 10 GRBs, ~2-3 days for all 30")
    
    print("\n🎯 EXPECTED OUTCOMES:")
    print("   IF 2+ show >3σ anomaly → Multi-GRB discovery paper!")
    print("   IF only GRB090902B → Deep dive paper on unique burst")
    print("   IF pattern in TeV GRBs → TeV-specific paper")
    
    print("\n💡 TIP: Start with TOP 5 (221009A, 190114C, 090510, 180720B, 080916C)")
    print("   These are most likely to show something interesting!")


if __name__ == "__main__":
    main()
