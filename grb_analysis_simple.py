"""
SIMPLIFIED FERMI LAT GRB QUANTUM GRAVITY ANALYSIS
==================================================
Windows-compatible version without problematic dependencies
No fermipy, no healpy - just core Python libraries!

Author: Simplified QG Analysis Pipeline
Date: 2025
"""

import os
import sys
import json
import warnings
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from astropy.io import fits
from astropy.time import Time
import astropy.units as u
from tqdm import tqdm

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration parameters"""
    
    # Data directories
    DATA_DIR = Path("grb_data")
    RESULTS_DIR = Path("grb_results")
    PLOTS_DIR = Path("grb_plots")
    
    # Analysis parameters
    ENERGY_MIN = 0.1  # GeV
    ENERGY_MAX = 300.0  # GeV
    TIME_WINDOW_PRE = 500  # seconds before trigger
    TIME_WINDOW_POST = 10000  # seconds after trigger
    SEARCH_RADIUS = 12.0  # degrees
    
    # Statistical thresholds
    SIGMA_THRESHOLD_WEAK = 2.0
    SIGMA_THRESHOLD_SIGNIFICANT = 3.0
    SIGMA_THRESHOLD_STRONG = 5.0
    OUTLIER_SIGMA = 3.0
    
    # Bootstrap parameters
    N_BOOTSTRAP = 10000
    CONFIDENCE_LEVEL = 0.95
    
    # Visualization
    DPI = 300
    FIGSIZE = (12, 8)
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories"""
        for dir_path in [cls.DATA_DIR, cls.RESULTS_DIR, cls.PLOTS_DIR]:
            dir_path.mkdir(exist_ok=True)
            for subdir in ['raw', 'processed', 'reports', 'figures']:
                (dir_path / subdir).mkdir(exist_ok=True)

# ============================================================================
# GRB DATABASE
# ============================================================================

GRB_DATABASE = {
    'GRB080916C': {
        'ra': 119.84712, 'dec': -56.63806,
        'trigger_met': 243216766.0,
        'trigger_utc': '2008-09-16 00:12:45',
        'z': 4.35, 'emax': 27.4,
        'priority': 'HIGH',
        'note': 'Highest redshift z=4.35'
    },
    'GRB090510': {
        'ra': 333.55375, 'dec': -26.58194,
        'trigger_met': 263607781.0,
        'trigger_utc': '2009-05-10 00:22:59',
        'z': 0.903, 'emax': 30.0,
        'priority': 'MEDIUM',
        'note': 'Short GRB, high energy'
    },
    'GRB090902B': {
        'ra': 264.93542, 'dec': 27.32583,
        'trigger_met': 273582310.0,
        'trigger_utc': '2009-09-02 11:58:29',
        'z': 1.822, 'emax': 40.0,
        'priority': 'HIGH',
        'note': 'Original paper 5.46sigma, 3972 photons'
    },
    'GRB090926A': {
        'ra': 353.39792, 'dec': -66.32361,
        'trigger_met': 275631628.0,
        'trigger_utc': '2009-09-26 12:40:26',
        'z': 2.106, 'emax': 19.4,
        'priority': 'MEDIUM',
        'note': 'Extra power-law component'
    },
    'GRB130427A': {
        'ra': 173.14083, 'dec': 27.70694,
        'trigger_met': 388595974.0,
        'trigger_utc': '2013-04-27 07:47:06',
        'z': 0.340, 'emax': 94.1,
        'priority': 'HIGH',
        'note': 'Maximum energy record 94.1 GeV'
    },
    'GRB160625B': {
        'ra': 308.56250, 'dec': 6.92722,
        'trigger_met': 488252434.0,
        'trigger_utc': '2016-06-25 22:40:16',
        'z': 1.406, 'emax': 15.3,
        'priority': 'HIGH',
        'note': 'Lag transition documented'
    },
}

# ============================================================================
# DOWNLOAD HELPER
# ============================================================================

class FermiDownloadHelper:
    """Generate download URLs and instructions"""
    
    BASE_URL = "https://fermi.gsfc.nasa.gov/cgi-bin/ssc/LAT/LATDataQuery.cgi"
    
    @staticmethod
    def generate_url(grb_name, params):
        """Generate Fermi FSSC query URL"""
        ra = params['ra']
        dec = params['dec']
        met = params['trigger_met']
        
        tmin = int(met - Config.TIME_WINDOW_PRE)
        tmax = int(met + Config.TIME_WINDOW_POST)
        
        url_params = [
            "destination=query",
            "coordsystem=J2000",
            f"coordinates={ra},{dec}",
            "coordfield=J2000",
            f"radius={Config.SEARCH_RADIUS}",
            f"tmin={tmin}",
            f"tmax={tmax}",
            "timetype=MET",
            f"energymin={int(Config.ENERGY_MIN * 1000)}",
            f"energymax={int(Config.ENERGY_MAX * 1000)}",
            "photonOrExtendedOrNone=Photon",
            "spacecraft=on"
        ]
        
        return f"{FermiDownloadHelper.BASE_URL}?{'&'.join(url_params)}"
    
    @staticmethod
    def print_instructions(grb_name, params):
        """Print download instructions"""
        url = FermiDownloadHelper.generate_url(grb_name, params)
        output_file = Config.DATA_DIR / "raw" / f"{grb_name}_photons.fits"
        
        print(f"\n{'='*80}")
        print(f"DOWNLOAD: {grb_name}")
        print(f"{'='*80}")
        print(f"RA/DEC: {params['ra']:.5f}, {params['dec']:.5f}")
        print(f"Trigger: {params['trigger_utc']}")
        print(f"Redshift: z = {params['z']:.3f}")
        print(f"Max Energy: {params['emax']:.1f} GeV")
        print(f"\n📋 STEPS:")
        print(f"1. Copy this URL:")
        print(f"   {url}")
        print(f"2. Open in browser and submit query")
        print(f"3. Wait for email (5-30 min)")
        print(f"4. Download FITS file")
        print(f"5. Save as: {output_file}")
        print(f"{'='*80}")

# ============================================================================
# DATA PROCESSING
# ============================================================================

class GRBPhotonData:
    """Load and process GRB photon data"""
    
    def __init__(self, grb_name, grb_params):
        self.grb_name = grb_name
        self.params = grb_params
        self.fits_file = Config.DATA_DIR / "raw" / f"{grb_name}_photons.fits"
        
        self.photons = None
        self.energies = None
        self.times = None
        self.n_photons = 0
        
    def load_data(self):
        """Load photon data from FITS file"""
        if not self.fits_file.exists():
            raise FileNotFoundError(f"❌ File not found: {self.fits_file}")
        
        print(f"📂 Loading {self.grb_name}...")
        
        with fits.open(self.fits_file) as hdul:
            events = hdul['EVENTS'].data
            
            # Extract photon properties
            self.energies = events['ENERGY'] / 1000.0  # MeV to GeV
            self.times = events['TIME'] - self.params['trigger_met']
            
            # Create DataFrame
            self.photons = pd.DataFrame({
                'energy': self.energies,
                'time': self.times,
                'ra': events['RA'],
                'dec': events['DEC']
            })
            
            self.n_photons = len(self.photons)
            
        print(f"   ✅ {self.n_photons} photons")
        print(f"   Energy: {self.energies.min():.3f} - {self.energies.max():.3f} GeV")
        print(f"   Time: {self.times.min():.1f} - {self.times.max():.1f} s")
        
        return self
    
    def get_energy_subsets(self):
        """Create energy subsets"""
        q25 = np.percentile(self.energies, 25)
        q50 = np.percentile(self.energies, 50)
        q75 = np.percentile(self.energies, 75)
        p90 = np.percentile(self.energies, 90)
        p95 = np.percentile(self.energies, 95)
        p99 = np.percentile(self.energies, 99)
        
        return {
            'all': self.photons,
            'low_energy': self.photons[self.photons['energy'] < q50],
            'high_energy': self.photons[self.photons['energy'] >= q50],
            'very_high_energy': self.photons[self.photons['energy'] >= q75],
            'ultra_high_energy': self.photons[self.photons['energy'] >= p90],
            'extreme_energy': self.photons[self.photons['energy'] >= p95],
            'maximum_energy': self.photons[self.photons['energy'] >= p99],
        }
    
    def get_temporal_phases(self):
        """Split into temporal phases"""
        time_median = np.median(self.times)
        
        return {
            'early': self.photons[self.photons['time'] < time_median],
            'late': self.photons[self.photons['time'] >= time_median],
        }
    
    def remove_outliers(self, sigma=3.0):
        """Remove outliers"""
        z_time = np.abs(stats.zscore(self.times))
        z_energy = np.abs(stats.zscore(np.log10(self.energies)))
        
        mask = (z_time < sigma) & (z_energy < sigma)
        return self.photons[mask].copy()

# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================

class CorrelationAnalyzer:
    """Statistical correlation analysis"""
    
    @staticmethod
    def pearson_correlation(energies, times):
        """Pearson correlation with bootstrap"""
        if len(energies) < 10:
            return {'r': np.nan, 'p_value': 1.0, 'sigma': 0.0}
        
        r, p_value = stats.pearsonr(energies, times)
        
        # Bootstrap
        n_boot = Config.N_BOOTSTRAP
        boot_r = np.zeros(n_boot)
        
        for i in range(n_boot):
            idx = np.random.choice(len(energies), len(energies), replace=True)
            boot_r[i], _ = stats.pearsonr(energies[idx], times[idx])
        
        sigma = np.abs(r) / np.std(boot_r) if np.std(boot_r) > 0 else 0.0
        
        return {
            'r': r,
            'p_value': p_value,
            'sigma': sigma,
            'boot_std': np.std(boot_r)
        }
    
    @staticmethod
    def spearman_correlation(energies, times):
        """Spearman correlation"""
        if len(energies) < 10:
            return {'rho': np.nan, 'p_value': 1.0, 'sigma': 0.0}
        
        rho, p_value = stats.spearmanr(energies, times)
        
        sigma = stats.norm.ppf(1 - p_value/2) if p_value > 0 else 10.0
        
        return {'rho': rho, 'p_value': p_value, 'sigma': sigma}

# ============================================================================
# MULTI-TECHNIQUE ANALYSIS
# ============================================================================

class MultiTechniqueAnalysis:
    """Complete analysis with all techniques"""
    
    def __init__(self, grb_data):
        self.grb_data = grb_data
        self.results = {}
    
    def analyze_global(self):
        """Global correlation"""
        print(f"\n🔍 Global correlation...")
        
        energies = self.grb_data.energies
        times = self.grb_data.times
        
        pearson = CorrelationAnalyzer.pearson_correlation(energies, times)
        spearman = CorrelationAnalyzer.spearman_correlation(energies, times)
        
        self.results['global'] = {
            'technique': 'global',
            'n_photons': len(energies),
            'pearson_r': pearson['r'],
            'pearson_sigma': pearson['sigma'],
            'spearman_rho': spearman['rho'],
            'spearman_sigma': spearman['sigma'],
            'sigma_max': max(pearson['sigma'], spearman['sigma'])
        }
        
        print(f"   Pearson:  r = {pearson['r']:+.4f}, σ = {pearson['sigma']:.2f}")
        print(f"   Spearman: ρ = {spearman['rho']:+.4f}, σ = {spearman['sigma']:.2f}")
        
        return self.results['global']
    
    def analyze_energy_subsets(self):
        """Energy subsets"""
        print(f"\n🔍 Energy subsets...")
        
        subsets = self.grb_data.get_energy_subsets()
        
        for name, subset in subsets.items():
            if len(subset) < 10:
                continue
            
            energies = subset['energy'].values
            times = subset['time'].values
            
            pearson = CorrelationAnalyzer.pearson_correlation(energies, times)
            
            self.results[f'subset_{name}'] = {
                'technique': f'energy_{name}',
                'n_photons': len(subset),
                'pearson_r': pearson['r'],
                'pearson_sigma': pearson['sigma'],
                'sigma_max': pearson['sigma']
            }
            
            print(f"   {name:20s}: n={len(subset):4d}, σ={pearson['sigma']:.2f}")
        
        return self.results
    
    def analyze_temporal_phases(self):
        """Temporal phases"""
        print(f"\n🔍 Temporal phases...")
        
        phases = self.grb_data.get_temporal_phases()
        
        for name, phase in phases.items():
            if len(phase) < 10:
                continue
            
            energies = phase['energy'].values
            times = phase['time'].values
            
            pearson = CorrelationAnalyzer.pearson_correlation(energies, times)
            
            self.results[f'phase_{name}'] = {
                'technique': f'phase_{name}',
                'n_photons': len(phase),
                'pearson_r': pearson['r'],
                'pearson_sigma': pearson['sigma'],
                'sigma_max': pearson['sigma']
            }
            
            print(f"   {name:20s}: n={len(phase):4d}, σ={pearson['sigma']:.2f}")
        
        return self.results
    
    def analyze_outlier_masked(self):
        """Outlier-masked"""
        print(f"\n🔍 Outlier-masked...")
        
        clean = self.grb_data.remove_outliers()
        
        if len(clean) < 10:
            return self.results
        
        energies = clean['energy'].values
        times = clean['time'].values
        
        pearson = CorrelationAnalyzer.pearson_correlation(energies, times)
        
        self.results['outlier_masked'] = {
            'technique': 'outlier_masked',
            'n_photons': len(clean),
            'pearson_r': pearson['r'],
            'pearson_sigma': pearson['sigma'],
            'sigma_max': pearson['sigma']
        }
        
        print(f"   Outlier-masked: n={len(clean):4d}, σ={pearson['sigma']:.2f}")
        
        return self.results
    
    def run_complete(self):
        """Run all analyses"""
        print(f"\n{'#'*80}")
        print(f"# MULTI-TECHNIQUE ANALYSIS: {self.grb_data.grb_name}")
        print(f"{'#'*80}")
        
        self.analyze_global()
        self.analyze_energy_subsets()
        self.analyze_temporal_phases()
        self.analyze_outlier_masked()
        
        # Find max significance
        sigma_values = [r['sigma_max'] for r in self.results.values() if 'sigma_max' in r]
        sigma_max = max(sigma_values) if sigma_values else 0.0
        
        best = max(self.results.items(), key=lambda x: x[1].get('sigma_max', 0))
        
        print(f"\n{'='*80}")
        print(f"RESULT: Maximum σ = {sigma_max:.2f} ({best[0]})")
        print(f"{'='*80}\n")
        
        return self.results, sigma_max, best[0]

# ============================================================================
# VISUALIZATION
# ============================================================================

class GRBVisualizer:
    """Create plots"""
    
    def __init__(self, grb_name, grb_data, results):
        self.grb_name = grb_name
        self.grb_data = grb_data
        self.results = results
        self.plot_dir = Config.PLOTS_DIR / "figures" / grb_name
        self.plot_dir.mkdir(exist_ok=True, parents=True)
    
    def plot_summary(self, sigma_max):
        """Create summary plot"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'{self.grb_name} - Analysis Summary (σ_max = {sigma_max:.2f})', 
                     fontsize=18, fontweight='bold')
        
        # Energy-Time scatter
        ax = axes[0, 0]
        scatter = ax.scatter(self.grb_data.times, self.grb_data.energies,
                           c=np.log10(self.grb_data.energies), cmap='viridis',
                           alpha=0.6, s=30, edgecolors='black', linewidth=0.5)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Energy (GeV)')
        ax.set_yscale('log')
        ax.set_title('Energy vs Time')
        ax.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax, label='log₁₀(E/GeV)')
        
        # Energy histogram
        ax = axes[0, 1]
        ax.hist(np.log10(self.grb_data.energies), bins=30, alpha=0.7, 
               edgecolor='black', color='blue')
        ax.set_xlabel('log₁₀(Energy/GeV)')
        ax.set_ylabel('Count')
        ax.set_title('Energy Distribution')
        ax.grid(True, alpha=0.3)
        
        # Significance comparison
        ax = axes[1, 0]
        techniques = [k.replace('_', ' ')[:20] for k in list(self.results.keys())[:8]]
        sigmas = [self.results[k].get('sigma_max', 0) for k in list(self.results.keys())[:8]]
        colors = ['green' if s>5 else 'orange' if s>3 else 'gray' for s in sigmas]
        ax.barh(techniques, sigmas, color=colors, alpha=0.7, edgecolor='black')
        ax.axvline(3.0, color='red', linestyle='--', linewidth=2, label='3σ')
        ax.set_xlabel('Significance (σ)')
        ax.set_title('Technique Comparison')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        
        # Stats box
        ax = axes[1, 1]
        ax.axis('off')
        stats_text = f"""
GRB: {self.grb_name}

N photons: {len(self.grb_data.photons)}
E_max: {self.grb_data.energies.max():.1f} GeV
Redshift: z = {self.grb_data.params['z']:.3f}

Maximum σ: {sigma_max:.2f}

Classification:
{'🔥 STRONG (>5σ)' if sigma_max > 5 else 
 '⚠️  SIGNIFICANT (3-5σ)' if sigma_max > 3 else
 '📊 MARGINAL (2-3σ)' if sigma_max > 2 else
 '❌ NO SIGNAL (<2σ)'}
        """
        ax.text(0.1, 0.5, stats_text, fontsize=14, family='monospace',
               verticalalignment='center')
        
        plt.tight_layout()
        plt.savefig(self.plot_dir / f'{self.grb_name}_summary.png', 
                   dpi=Config.DPI, bbox_inches='tight')
        plt.close()
        
        print(f"   ✅ Plot saved: {self.plot_dir / f'{self.grb_name}_summary.png'}")

# ============================================================================
# MAIN PIPELINE
# ============================================================================

class GRBPipeline:
    """Main analysis pipeline"""
    
    def __init__(self):
        Config.setup_directories()
        self.grb_database = GRB_DATABASE
        self.all_results = {}
    
    def check_data(self):
        """Check available data"""
        print(f"\n{'='*80}")
        print(f"CHECKING DATA AVAILABILITY")
        print(f"{'='*80}\n")
        
        available = []
        missing = []
        
        for grb_name in self.grb_database.keys():
            file_path = Config.DATA_DIR / "raw" / f"{grb_name}_photons.fits"
            if file_path.exists():
                available.append(grb_name)
                print(f"✅ {grb_name}: Data available")
            else:
                missing.append(grb_name)
                print(f"❌ {grb_name}: Data missing")
        
        print(f"\n📊 Summary: {len(available)}/{len(self.grb_database)} GRBs have data\n")
        
        return available, missing
    
    def show_download_instructions(self, missing):
        """Show download instructions"""
        if not missing:
            return
        
        print(f"\n{'='*80}")
        print(f"DOWNLOAD INSTRUCTIONS FOR {len(missing)} GRBs")
        print(f"{'='*80}")
        
        for grb_name in missing:
            FermiDownloadHelper.print_instructions(grb_name, self.grb_database[grb_name])
    
    def analyze_grb(self, grb_name):
        """Analyze single GRB"""
        print(f"\n{'█'*80}")
        print(f"█ ANALYZING: {grb_name}")
        print(f"{'█'*80}\n")
        
        try:
            # Load data
            grb_data = GRBPhotonData(grb_name, self.grb_database[grb_name])
            grb_data.load_data()
            
            # Analyze
            analyzer = MultiTechniqueAnalysis(grb_data)
            results, sigma_max, best_technique = analyzer.run_complete()
            
            # Visualize
            visualizer = GRBVisualizer(grb_name, grb_data, results)
            visualizer.plot_summary(sigma_max)
            
            # Store results
            self.all_results[grb_name] = {
                'n_photons': grb_data.n_photons,
                'energy_max': float(grb_data.energies.max()),
                'redshift': self.grb_database[grb_name]['z'],
                'sigma_max': sigma_max,
                'best_technique': best_technique,
                'classification': (
                    'STRONG' if sigma_max > 5 else
                    'SIGNIFICANT' if sigma_max > 3 else
                    'MARGINAL' if sigma_max > 2 else
                    'NO SIGNAL'
                )
            }
            
            print(f"\n✅ {grb_name} complete: σ_max = {sigma_max:.2f}\n")
            
        except Exception as e:
            print(f"\n❌ Error analyzing {grb_name}: {e}\n")
    
    def create_comparison(self):
        """Create comparison report"""
        if not self.all_results:
            return
        
        print(f"\n{'='*80}")
        print(f"MULTI-GRB COMPARISON")
        print(f"{'='*80}\n")
        
        df = pd.DataFrame([
            {
                'GRB': grb,
                'N_Photons': r['n_photons'],
                'E_max': r['energy_max'],
                'z': r['redshift'],
                'σ_max': r['sigma_max'],
                'Class': r['classification']
            }
            for grb, r in self.all_results.items()
        ])
        
        df = df.sort_values('σ_max', ascending=False)
        
        print(df.to_string(index=False))
        
        # Save
        output_file = Config.RESULTS_DIR / 'reports' / 'comparison.csv'
        df.to_csv(output_file, index=False)
        
        print(f"\n✅ Saved: {output_file}")
        
        # Summary stats
        print(f"\n{'='*80}")
        print(f"STATISTICS")
        print(f"{'='*80}")
        print(f"Total: {len(df)}")
        print(f"Strong (>5σ): {len(df[df['σ_max'] > 5])}")
        print(f"Significant (3-5σ): {len(df[(df['σ_max'] > 3) & (df['σ_max'] <= 5)])}")
        print(f"Marginal (2-3σ): {len(df[(df['σ_max'] > 2) & (df['σ_max'] <= 3)])}")
        print(f"Detection rate (≥3σ): {len(df[df['σ_max'] >= 3])/len(df)*100:.1f}%")
        print(f"{'='*80}\n")
    
    def run(self):
        """Run pipeline"""
        print("\n" + "="*80)
        print("FERMI LAT GRB QUANTUM GRAVITY ANALYSIS")
        print("Simplified Windows-Compatible Version")
        print("="*80 + "\n")
        
        # Check data
        available, missing = self.check_data()
        
        if missing:
            self.show_download_instructions(missing)
            
            print(f"\n{'='*80}")
            response = input("Have you downloaded missing data? (yes/no): ").lower()
            if response != 'yes':
                print("\nDownload data and re-run. Exiting...")
                return
        
        # Analyze available GRBs
        if available:
            print(f"\n{'='*80}")
            print(f"ANALYZING {len(available)} GRBs")
            print(f"{'='*80}")
            
            for grb_name in tqdm(available, desc="Progress"):
                self.analyze_grb(grb_name)
            
            # Create comparison
            self.create_comparison()
            
            print(f"\n{'='*80}")
            print(f"✅ ANALYSIS COMPLETE!")
            print(f"{'='*80}")
            print(f"Results: {Config.RESULTS_DIR}")
            print(f"Plots: {Config.PLOTS_DIR}")
            print(f"{'='*80}\n")
        else:
            print("\n❌ No data available. Download data first.\n")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    pipeline = GRBPipeline()
    pipeline.run()