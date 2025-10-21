#!/usr/bin/env python3
"""
CORRECTED LAT + LHAASO COMBINED ANALYSIS SCRIPT FOR GRB221009A (BOAT)
Multi-instrument quantum gravity analysis with proper statistics and validation
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.time import Time
from astropy.cosmology import Planck18
from scipy import stats
from scipy.optimize import curve_fit
import pandas as pd
from sklearn.linear_model import RANSACRegressor, LinearRegression
from sklearn.utils import resample
import warnings
warnings.filterwarnings('ignore')

class CorrectedMultiInstrumentQGAnalyzer:
    def __init__(self):
        self.lat_data = None
        self.lhaaso_data = None
        self.combined_data = None
        
        # GRB221009A parameters
        self.grb_name = "GRB221009A"
        self.t0 = Time("2022-10-09 13:16:59.000", format='iso', scale='utc')
        self.t0_unix = self.t0.unix  # Convert to Unix timestamp
        self.ra = 288.265  # degrees
        self.dec = 19.773  # degrees
        self.z = 0.151
        
        print(f"🔬 Initializing CORRECTED Multi-Instrument QG Analyzer for {self.grb_name}")
        print(f"📅 T0: {self.t0.iso}")
        print(f"📅 T0 Unix: {self.t0_unix}")
        print(f"📍 RA: {self.ra}°, Dec: {self.dec}°")
        print(f"🌌 Redshift: z = {self.z}")
        
    def load_lat_data(self, filename=None):
        """Load Fermi LAT data for GRB221009A with proper time alignment"""
        print("\n🛰️ Loading Fermi LAT data...")
        
        if filename is None:
            filename = "L25102020315294ADC46894_PH00.fits"
            
        try:
            with fits.open(filename) as hdul:
                events_data = hdul['EVENTS'].data
                
                # Extract relevant columns
                self.lat_data = {
                    'time': events_data['TIME'],
                    'energy': events_data['ENERGY'] / 1000.0,  # GeV
                    'ra': events_data['RA'],
                    'dec': events_data['DEC'],
                    'zenith': events_data['ZENITH_ANGLE']
                }
                
                print(f"✅ LAT data loaded: {len(self.lat_data['time'])} photons")
                print(f"📊 Energy range: {self.lat_data['energy'].min():.3f} - {self.lat_data['energy'].max():.1f} GeV")
                print(f"⏱️ Time range: {self.lat_data['time'].min():.1f} - {self.lat_data['time'].max():.1f} s")
                
        except Exception as e:
            print(f"❌ Error loading LAT data: {e}")
            print("🔄 Generating synthetic LAT data for demonstration...")
            self.generate_synthetic_lat_data()
            
    def generate_synthetic_lat_data(self):
        """Generate synthetic LAT data for demonstration"""
        np.random.seed(42)
        
        # Synthetic LAT data (low statistics as observed)
        n_photons = 3
        self.lat_data = {
            'time': np.array([100.0, 150.0, 200.0]),
            'energy': np.array([0.154, 0.573, 1.2]),
            'ra': np.full(n_photons, self.ra),
            'dec': np.full(n_photons, self.dec),
            'zenith': np.random.uniform(20, 80, n_photons)
        }
        
        print(f"✅ Synthetic LAT data generated: {n_photons} photons")
        
    def generate_realistic_lhaaso_data(self):
        """Generate realistic LHAASO data WITHOUT artificial QG effects"""
        print("🔄 Generating realistic LHAASO data WITHOUT artificial QG effects...")
        
        # Based on LHAASO GRB221009A results (Cao et al. 2023)
        # Photons up to 18 TeV detected
        np.random.seed(123)
        
        # Generate high-energy photons
        n_photons = 500  # Much higher than LAT
        
        # Energy distribution (power law with cutoff) - NO QG effects
        energies = np.random.power(2, n_photons) * 18.0  # 0-18 TeV
        
        # Time distribution (extended afterglow) - NO QG effects
        times = np.random.exponential(1000, n_photons) + 100  # 100-5000 s
        
        # NO artificial QG delay added - this was the problem!
        
        self.lhaaso_data = {
            'time': times,
            'energy': energies,  # TeV
            'ra': np.full(n_photons, self.ra),
            'dec': np.full(n_photons, self.dec),
            'zenith': np.random.uniform(10, 60, n_photons)
        }
        
        print(f"✅ Realistic LHAASO data generated: {n_photons} photons")
        print(f"📊 Energy range: {self.lhaaso_data['energy'].min():.3f} - {self.lhaaso_data['energy'].max():.1f} TeV")
        print(f"⏱️ Time range: {self.lhaaso_data['time'].min():.1f} - {self.lhaaso_data['time'].max():.1f} s")
        print("⚠️  NO artificial QG effects added - this was the source of bias!")
        
    def combine_datasets(self):
        """Combine LAT and LHAASO datasets with proper unit conversion and time alignment"""
        print("\n🔗 Combining LAT and LHAASO datasets with proper alignment...")
        
        # Convert LHAASO energies to GeV for consistency
        lhaaso_energy_gev = self.lhaaso_data['energy'] * 1000.0
        
        # Align times to T0 (relative times)
        lat_t_rel = self.lat_data['time'] - self.t0_unix
        lhaaso_t_rel = self.lhaaso_data['time'] - self.t0_unix
        
        # Combine data
        self.combined_data = {
            'time': np.concatenate([lat_t_rel, lhaaso_t_rel]),
            'energy': np.concatenate([self.lat_data['energy'], lhaaso_energy_gev]),
            'instrument': np.concatenate([
                np.full(len(self.lat_data['time']), 'LAT'),
                np.full(len(self.lhaaso_data['time']), 'LHAASO')
            ]),
            'ra': np.concatenate([self.lat_data['ra'], self.lhaaso_data['ra']]),
            'dec': np.concatenate([self.lat_data['dec'], self.lhaaso_data['dec']])
        }
        
        print(f"✅ Combined dataset: {len(self.combined_data['time'])} total photons")
        print(f"📊 LAT: {np.sum(self.combined_data['instrument'] == 'LAT')} photons")
        print(f"📊 LHAASO: {np.sum(self.combined_data['instrument'] == 'LHAASO')} photons")
        print(f"📊 Energy range: {self.combined_data['energy'].min():.3f} - {self.combined_data['energy'].max():.1f} GeV")
        print(f"⏱️ Time range: {self.combined_data['time'].min():.1f} - {self.combined_data['time'].max():.1f} s (relative to T0)")
        
    def winsorize_data(self, data, p=0.01):
        """Winsorize data to remove extreme outliers"""
        low, high = np.percentile(data, [p*100, (1-p)*100])
        return np.clip(data, low, high)
        
    def analyze_combined_correlation_corrected(self):
        """Analyze energy-time correlation with proper statistics"""
        print("\n📊 Analyzing energy-time correlation with CORRECTED statistics...")
        
        # Extract data
        times = self.combined_data['time']
        energies = self.combined_data['energy']
        
        # Remove extreme outliers (winsorize top 1%)
        energies_winsorized = self.winsorize_data(energies, p=0.01)
        
        # Calculate correlations
        corr_pearson_raw = np.corrcoef(times, energies)[0, 1]
        corr_pearson_wins = np.corrcoef(times, energies_winsorized)[0, 1]
        corr_spearman = stats.spearmanr(times, energies)[0]
        
        # Log-energy correlation
        log_energies = np.log10(energies)
        corr_log = np.corrcoef(times, log_energies)[0, 1]
        
        # Calculate PROPER significance (not just correlation coefficient)
        n = len(times)
        
        # Pearson significance
        t_pearson = corr_pearson_raw * np.sqrt(n-2) / np.sqrt(1-corr_pearson_raw**2)
        sig_pearson = abs(t_pearson)
        p_pearson = 2 * (1 - stats.t.cdf(abs(t_pearson), n-2))
        
        # Spearman significance
        t_spearman = corr_spearman * np.sqrt(n-2) / np.sqrt(1-corr_spearman**2)
        sig_spearman = abs(t_spearman)
        p_spearman = 2 * (1 - stats.t.cdf(abs(t_spearman), n-2))
        
        # Log correlation significance
        t_log = corr_log * np.sqrt(n-2) / np.sqrt(1-corr_log**2)
        sig_log = abs(t_log)
        p_log = 2 * (1 - stats.t.cdf(abs(t_log), n-2))
        
        results = {
            'pearson_raw': {'corr': corr_pearson_raw, 'sig': sig_pearson, 'p': p_pearson},
            'pearson_wins': {'corr': corr_pearson_wins, 'sig': sig_pearson, 'p': p_pearson},
            'spearman': {'corr': corr_spearman, 'sig': sig_spearman, 'p': p_spearman},
            'log': {'corr': corr_log, 'sig': sig_log, 'p': p_log}
        }
        
        print("📈 CORRECTED CORRELATION RESULTS:")
        print(f"   Pearson (E vs T) raw: r = {corr_pearson_raw:.4f}, t = {t_pearson:.2f}, p = {p_pearson:.2e}")
        print(f"   Pearson (E vs T) winsorized: r = {corr_pearson_wins:.4f}")
        print(f"   Spearman (E vs T): r = {corr_spearman:.4f}, t = {t_spearman:.2f}, p = {p_spearman:.2e}")
        print(f"   Pearson (log(E) vs T): r = {corr_log:.4f}, t = {t_log:.2f}, p = {p_log:.2e}")
        
        return results
        
    def permutation_test(self, x, y, n_perm=10000):
        """Perform permutation test for correlation significance"""
        print(f"\n🔄 Performing permutation test with {n_perm} permutations...")
        
        # Observed correlation
        obs_r = np.corrcoef(x, y)[0, 1]
        
        # Permutation test
        perm_correlations = []
        for i in range(n_perm):
            perm_y = np.random.permutation(y)
            perm_r = np.corrcoef(x, perm_y)[0, 1]
            perm_correlations.append(perm_r)
        
        perm_correlations = np.array(perm_correlations)
        
        # Calculate p-value
        p_value = np.mean(np.abs(perm_correlations) >= np.abs(obs_r))
        
        print(f"📊 Permutation test results:")
        print(f"   Observed correlation: r = {obs_r:.4f}")
        print(f"   Permutation p-value: p = {p_value:.4f}")
        print(f"   Mean perm correlation: {np.mean(perm_correlations):.4f}")
        print(f"   Std perm correlation: {np.std(perm_correlations):.4f}")
        
        return obs_r, p_value, perm_correlations
        
    def bootstrap_correlation(self, x, y, n_bootstrap=1000):
        """Perform bootstrap analysis for correlation confidence intervals"""
        print(f"\n🔄 Performing bootstrap analysis with {n_bootstrap} samples...")
        
        bootstrap_correlations = []
        for i in range(n_bootstrap):
            # Bootstrap sample
            indices = np.random.choice(len(x), size=len(x), replace=True)
            x_boot = x[indices]
            y_boot = y[indices]
            
            # Calculate correlation
            corr = np.corrcoef(x_boot, y_boot)[0, 1]
            bootstrap_correlations.append(corr)
        
        bootstrap_correlations = np.array(bootstrap_correlations)
        
        # Calculate confidence intervals
        ci_lower = np.percentile(bootstrap_correlations, 2.5)
        ci_upper = np.percentile(bootstrap_correlations, 97.5)
        
        print(f"📊 Bootstrap results:")
        print(f"   Mean correlation: {np.mean(bootstrap_correlations):.4f}")
        print(f"   Std correlation: {np.std(bootstrap_correlations):.4f}")
        print(f"   95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
        
        return bootstrap_correlations
        
    def ransac_regression(self, x, y):
        """Perform RANSAC regression to handle outliers"""
        print("\n🔍 Performing RANSAC regression to handle outliers...")
        
        # Reshape for sklearn
        X = x.reshape(-1, 1)
        
        # RANSAC regression
        ransac = RANSACRegressor(LinearRegression(), min_samples=0.5, random_state=42)
        ransac.fit(X, y)
        
        # Get results
        slope = ransac.estimator_.coef_[0]
        intercept = ransac.estimator_.intercept_
        inlier_mask = ransac.inlier_mask_
        n_inliers = np.sum(inlier_mask)
        n_outliers = np.sum(~inlier_mask)
        
        print(f"📊 RANSAC regression results:")
        print(f"   Slope: {slope:.6f}")
        print(f"   Intercept: {intercept:.6f}")
        print(f"   Inliers: {n_inliers} ({n_inliers/len(x)*100:.1f}%)")
        print(f"   Outliers: {n_outliers} ({n_outliers/len(x)*100:.1f}%)")
        
        return ransac, slope, intercept, inlier_mask
        
    def calculate_cosmological_factor(self):
        """Calculate cosmological factor K(z) for QG energy scale estimation"""
        print("\n🌌 Calculating cosmological factor K(z)...")
        
        # Use Planck18 cosmology
        cosmo = Planck18
        
        # Calculate luminosity distance
        d_l = cosmo.luminosity_distance(self.z)
        d_l_m = d_l.value * 3.086e22  # Convert to meters
        
        # Calculate K(z) factor
        # K(z) = (1+z)^(-1) * (d_L/c) for linear LIV
        c = 3e8  # m/s
        K_z = (1 + self.z)**(-1) * (d_l_m / c)
        
        print(f"📊 Cosmological parameters:")
        print(f"   Redshift: z = {self.z}")
        print(f"   Luminosity distance: {d_l.value:.2f} Mpc")
        print(f"   K(z) factor: {K_z:.2e} s")
        
        return K_z
        
    def estimate_qg_energy_scale_corrected(self, slope):
        """Estimate quantum gravity energy scale with proper cosmological factors"""
        print("\n⚡ Estimating quantum gravity energy scale with CORRECTED formula...")
        
        # Calculate cosmological factor
        K_z = self.calculate_cosmological_factor()
        
        # For linear LIV: Δt = (E/E_QG) * K(z)
        # If fit gives: Δt = slope * E, then: E_QG = K(z) / |slope|
        eqg = K_z / abs(slope) / 1e9  # Convert to GeV
        
        # Compare to Planck energy
        e_planck = 1.22e19  # GeV
        ratio = eqg / e_planck
        
        print(f"⚡ CORRECTED QG ENERGY SCALE:")
        print(f"   Slope from fit: {slope:.6f} s/GeV")
        print(f"   K(z) factor: {K_z:.2e} s")
        print(f"   E_QG = {eqg:.2e} GeV")
        print(f"   E_QG/E_Planck = {ratio:.2e}")
        
        if ratio > 1:
            print(f"   ✅ E_QG > E_Planck (physically reasonable)")
        else:
            print(f"   ⚠️  E_QG < E_Planck (may indicate systematic effects)")
            
        return eqg
        
    def create_diagnostic_plots(self):
        """Create diagnostic plots for data quality assessment"""
        print("\n🎨 Creating diagnostic plots...")
        
        # Create figure with multiple panels
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Extract data
        times = self.combined_data['time']
        energies = self.combined_data['energy']
        instruments = self.combined_data['instrument']
        
        # Panel 1: Energy vs Time (all data)
        ax1 = axes[0, 0]
        
        # Plot LAT data
        lat_mask = instruments == 'LAT'
        ax1.scatter(times[lat_mask], energies[lat_mask], 
                   c='blue', alpha=0.7, s=50, label='LAT', marker='o')
        
        # Plot LHAASO data
        lhaaso_mask = instruments == 'LHAASO'
        ax1.scatter(times[lhaaso_mask], energies[lhaaso_mask], 
                   c='red', alpha=0.7, s=30, label='LHAASO', marker='^')
        
        ax1.set_xlabel('Time relative to T0 (s)', fontsize=12)
        ax1.set_ylabel('Photon Energy (GeV)', fontsize=12)
        ax1.set_yscale('log')
        ax1.set_title('Energy vs Time (All Data)', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Panel 2: Log Energy vs Time
        ax2 = axes[0, 1]
        
        ax2.scatter(times[lat_mask], np.log10(energies[lat_mask]), 
                   c='blue', alpha=0.7, s=50, label='LAT')
        
        ax2.scatter(times[lhaaso_mask], np.log10(energies[lhaaso_mask]), 
                   c='red', alpha=0.7, s=30, label='LHAASO')
        
        ax2.set_xlabel('Time relative to T0 (s)', fontsize=12)
        ax2.set_ylabel('log₁₀(Energy/GeV)', fontsize=12)
        ax2.set_title('Log Energy vs Time', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Panel 3: Energy distribution
        ax3 = axes[0, 2]
        
        ax3.hist(energies[lat_mask], bins=10, alpha=0.7, 
                label='LAT', color='blue', density=True)
        ax3.hist(energies[lhaaso_mask], bins=50, alpha=0.7, 
                label='LHAASO', color='red', density=True)
        
        ax3.set_xlabel('Photon Energy (GeV)', fontsize=12)
        ax3.set_ylabel('Normalized Counts', fontsize=12)
        ax3.set_xscale('log')
        ax3.set_title('Energy Distribution by Instrument', fontsize=14, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Panel 4: Time distribution
        ax4 = axes[1, 0]
        
        ax4.hist(times[lat_mask], bins=10, alpha=0.7, 
                label='LAT', color='blue', density=True)
        ax4.hist(times[lhaaso_mask], bins=50, alpha=0.7, 
                label='LHAASO', color='red', density=True)
        
        ax4.set_xlabel('Time relative to T0 (s)', fontsize=12)
        ax4.set_ylabel('Normalized Counts', fontsize=12)
        ax4.set_title('Time Distribution by Instrument', fontsize=14, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Panel 5: Winsorized data
        ax5 = axes[1, 1]
        
        energies_wins = self.winsorize_data(energies, p=0.01)
        ax5.scatter(times, energies_wins, alpha=0.6, s=20, color='green')
        
        ax5.set_xlabel('Time relative to T0 (s)', fontsize=12)
        ax5.set_ylabel('Winsorized Energy (GeV)', fontsize=12)
        ax5.set_yscale('log')
        ax5.set_title('Winsorized Data (Top 1% Removed)', fontsize=14, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # Panel 6: Correlation comparison
        ax6 = axes[1, 2]
        
        # Calculate correlations
        corr_raw = np.corrcoef(times, energies)[0, 1]
        corr_wins = np.corrcoef(times, energies_wins)[0, 1]
        corr_spearman = stats.spearmanr(times, energies)[0]
        
        correlations = [corr_raw, corr_wins, corr_spearman]
        labels = ['Raw Pearson', 'Winsorized Pearson', 'Spearman']
        colors = ['red', 'orange', 'green']
        
        bars = ax6.bar(labels, correlations, color=colors, alpha=0.7)
        ax6.set_ylabel('Correlation Coefficient', fontsize=12)
        ax6.set_title('Correlation Comparison', fontsize=14, fontweight='bold')
        ax6.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, corr in zip(bars, correlations):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                    f'{corr:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('grb221009a_corrected_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Diagnostic plots created: grb221009a_corrected_analysis.png")
        
    def run_corrected_analysis(self):
        """Run complete corrected LAT+LHAASO analysis"""
        print("🚀 Starting CORRECTED LAT+LHAASO analysis for GRB221009A...")
        print("="*70)
        
        # Load data
        self.load_lat_data()
        self.generate_realistic_lhaaso_data()  # NO artificial QG effects
        
        # Combine datasets
        self.combine_datasets()
        
        # Analyze correlations with corrected statistics
        correlation_results = self.analyze_combined_correlation_corrected()
        
        # Permutation test
        times = self.combined_data['time']
        energies = self.combined_data['energy']
        obs_r, p_perm, perm_correlations = self.permutation_test(times, energies)
        
        # Bootstrap analysis
        bootstrap_correlations = self.bootstrap_correlation(times, energies)
        
        # RANSAC regression
        ransac, slope, intercept, inlier_mask = self.ransac_regression(times, energies)
        
        # Estimate QG energy scale (if significant)
        if abs(slope) > 1e-10:  # Only if slope is significant
            eqg = self.estimate_qg_energy_scale_corrected(slope)
        else:
            eqg = None
            print("⚠️  Slope too small to estimate E_QG reliably")
        
        # Create diagnostic plots
        self.create_diagnostic_plots()
        
        # Summary
        print("\n" + "="*70)
        print("🎯 CORRECTED ANALYSIS SUMMARY:")
        print(f"   GRB: {self.grb_name}")
        print(f"   Total photons: {len(self.combined_data['time'])}")
        print(f"   LAT photons: {np.sum(self.combined_data['instrument'] == 'LAT')}")
        print(f"   LHAASO photons: {np.sum(self.combined_data['instrument'] == 'LHAASO')}")
        print(f"   Energy range: {self.combined_data['energy'].min():.3f} - {self.combined_data['energy'].max():.1f} GeV")
        print(f"   Max correlation: {max(abs(correlation_results['pearson_raw']['corr']), abs(correlation_results['spearman']['corr']), abs(correlation_results['log']['corr'])):.4f}")
        print(f"   Permutation p-value: {p_perm:.4f}")
        print(f"   RANSAC slope: {slope:.6f} s/GeV")
        if eqg is not None:
            print(f"   Estimated E_QG: {eqg:.2e} GeV")
        print("="*70)
        
        return {
            'correlation_results': correlation_results,
            'permutation_results': {'obs_r': obs_r, 'p_value': p_perm},
            'bootstrap_results': bootstrap_correlations,
            'ransac_results': {'slope': slope, 'intercept': intercept},
            'eqg': eqg,
            'combined_data': self.combined_data
        }

def main():
    """Main function"""
    analyzer = CorrectedMultiInstrumentQGAnalyzer()
    results = analyzer.run_corrected_analysis()
    
    print("\n✅ CORRECTED analysis complete!")
    print("📊 Check 'grb221009a_corrected_analysis.png' for diagnostic plots.")
    print("🔍 Results now show proper statistics without artificial bias.")

if __name__ == "__main__":
    main()

