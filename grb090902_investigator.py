#!/usr/bin/env python3
"""
GRB090902B Property Investigator
Analyzes what makes GRB090902B special and unique
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.cosmology import Planck18
import json
from datetime import datetime
import seaborn as sns

class GRB090902BInvestigator:
    def __init__(self):
        self.grb_name = "GRB090902B"
        self.filename = "L251020161615F357373F52_EV00.fits"
        self.results = {}
        
        print(f"🔍 GRB090902B Property Investigator")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
    def load_data(self):
        """Load GRB090902B data"""
        print("📊 Loading GRB090902B data...")
        
        try:
            with fits.open(self.filename) as hdul:
                events_data = hdul['EVENTS'].data
                
            self.times = events_data['TIME']
            self.energies = events_data['ENERGY'] / 1000.0  # Convert to GeV
            self.zenith = events_data['ZENITH_ANGLE']
            # Check if AZIMUTH_ANGLE exists, if not create dummy data
            if 'AZIMUTH_ANGLE' in events_data.dtype.names:
                self.azimuth = events_data['AZIMUTH_ANGLE']
            else:
                self.azimuth = np.random.uniform(0, 360, len(self.times))
                print("   ⚠️  AZIMUTH_ANGLE not found, using random values")
            
            print(f"✅ Data loaded successfully")
            print(f"   📊 Total photons: {len(self.times)}")
            print(f"   📊 Energy range: {self.energies.min():.3f} - {self.energies.max():.1f} GeV")
            print(f"   📊 Time range: {self.times.min():.1f} - {self.times.max():.1f} s")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def analyze_basic_properties(self):
        """Analyze basic GRB properties"""
        print("\n🔬 Analyzing basic GRB properties...")
        
        # Basic statistics
        n_photons = len(self.times)
        energy_max = self.energies.max()
        energy_min = self.energies.min()
        time_span = self.times.max() - self.times.min()
        
        # Energy distribution
        energy_percentiles = np.percentile(self.energies, [10, 25, 50, 75, 90, 95, 99])
        
        # High energy photons
        photons_1gev = np.sum(self.energies >= 1.0)
        photons_10gev = np.sum(self.energies >= 10.0)
        photons_30gev = np.sum(self.energies >= 30.0)
        
        # Time distribution
        time_percentiles = np.percentile(self.times, [10, 25, 50, 75, 90, 95, 99])
        
        # Zenith angle analysis
        zenith_mean = np.mean(self.zenith)
        zenith_std = np.std(self.zenith)
        
        self.results['basic_properties'] = {
            'n_photons': int(n_photons),
            'energy_max_gev': float(energy_max),
            'energy_min_gev': float(energy_min),
            'time_span_s': float(time_span),
            'energy_percentiles_gev': energy_percentiles.tolist(),
            'time_percentiles_s': time_percentiles.tolist(),
            'photons_1gev': int(photons_1gev),
            'photons_10gev': int(photons_10gev),
            'photons_30gev': int(photons_30gev),
            'zenith_mean_deg': float(zenith_mean),
            'zenith_std_deg': float(zenith_std)
        }
        
        print(f"   📊 Photons: {n_photons:,}")
        print(f"   📊 Max energy: {energy_max:.1f} GeV")
        print(f"   📊 Time span: {time_span:.1f} s")
        print(f"   📊 >1 GeV: {photons_1gev} ({100*photons_1gev/n_photons:.1f}%)")
        print(f"   📊 >10 GeV: {photons_10gev} ({100*photons_10gev/n_photons:.1f}%)")
        print(f"   📊 >30 GeV: {photons_30gev} ({100*photons_30gev/n_photons:.1f}%)")
        
    def analyze_energy_time_correlation(self):
        """Analyze energy-time correlation in detail"""
        print("\n🔬 Analyzing energy-time correlation...")
        
        # Calculate correlation
        correlation = np.corrcoef(self.energies, self.times)[0, 1]
        
        # Calculate significance
        n = len(self.energies)
        t_stat = correlation * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
        significance = abs(t_stat)
        
        # Spearman correlation
        from scipy.stats import spearmanr
        spearman_corr, spearman_p = spearmanr(self.energies, self.times)
        
        # Energy bins analysis
        energy_bins = np.logspace(np.log10(self.energies.min()), np.log10(self.energies.max()), 10)
        bin_correlations = []
        bin_significances = []
        
        for i in range(len(energy_bins)-1):
            mask = (self.energies >= energy_bins[i]) & (self.energies < energy_bins[i+1])
            if np.sum(mask) > 10:  # Minimum 10 photons per bin
                bin_energies = self.energies[mask]
                bin_times = self.times[mask]
                bin_corr = np.corrcoef(bin_energies, bin_times)[0, 1]
                bin_sig = abs(bin_corr) * np.sqrt(len(bin_energies) - 2) / np.sqrt(1 - bin_corr**2)
                bin_correlations.append(bin_corr)
                bin_significances.append(bin_sig)
            else:
                bin_correlations.append(np.nan)
                bin_significances.append(np.nan)
        
        self.results['energy_time_correlation'] = {
            'pearson_correlation': float(correlation),
            'pearson_significance': float(significance),
            'spearman_correlation': float(spearman_corr),
            'spearman_p_value': float(spearman_p),
            'energy_bin_correlations': bin_correlations,
            'energy_bin_significances': bin_significances
        }
        
        print(f"   📊 Pearson correlation: {correlation:.4f}")
        print(f"   📊 Significance: {significance:.2f}σ")
        print(f"   📊 Spearman correlation: {spearman_corr:.4f}")
        print(f"   📊 Spearman p-value: {spearman_p:.2e}")
        
    def analyze_temporal_structure(self):
        """Analyze temporal structure of the GRB"""
        print("\n🔬 Analyzing temporal structure...")
        
        # Find peaks in light curve
        from scipy.signal import find_peaks
        
        # Create light curve with 1s bins
        time_bins = np.arange(self.times.min(), self.times.max() + 1, 1.0)
        light_curve = np.histogram(self.times, bins=time_bins)[0]
        
        # Find peaks
        peaks, properties = find_peaks(light_curve, height=np.mean(light_curve))
        
        # Analyze pulse structure
        if len(peaks) > 0:
            peak_times = time_bins[peaks]
            peak_heights = light_curve[peaks]
            
            # Calculate pulse properties
            pulse_durations = []
            for i, peak_time in enumerate(peak_times):
                # Find FWHM
                peak_idx = np.argmin(np.abs(time_bins - peak_time))
                peak_height = light_curve[peak_idx]
                half_max = peak_height / 2
                
                # Find left and right edges
                left_idx = peak_idx
                while left_idx > 0 and light_curve[left_idx] > half_max:
                    left_idx -= 1
                
                right_idx = peak_idx
                while right_idx < len(light_curve) - 1 and light_curve[right_idx] > half_max:
                    right_idx += 1
                
                fwhm = time_bins[right_idx] - time_bins[left_idx]
                pulse_durations.append(fwhm)
        else:
            peak_times = []
            peak_heights = []
            pulse_durations = []
        
        # Calculate T90 (time for 90% of counts)
        sorted_times = np.sort(self.times)
        n_90 = int(0.9 * len(sorted_times))
        t90 = sorted_times[n_90] - sorted_times[0]
        
        # Calculate T50 (time for 50% of counts)
        n_50 = int(0.5 * len(sorted_times))
        t50 = sorted_times[n_50] - sorted_times[0]
        
        self.results['temporal_structure'] = {
            'n_peaks': len(peaks),
            'peak_times_s': peak_times.tolist(),
            'peak_heights': peak_heights.tolist(),
            'pulse_durations_s': pulse_durations,
            't90_s': float(t90),
            't50_s': float(t50),
            'mean_count_rate': float(np.mean(light_curve)),
            'max_count_rate': float(np.max(light_curve))
        }
        
        print(f"   📊 Number of peaks: {len(peaks)}")
        print(f"   📊 T90: {t90:.1f} s")
        print(f"   📊 T50: {t50:.1f} s")
        print(f"   📊 Mean count rate: {np.mean(light_curve):.1f} counts/s")
        
    def analyze_spectral_properties(self):
        """Analyze spectral properties"""
        print("\n🔬 Analyzing spectral properties...")
        
        # Energy spectrum
        energy_bins = np.logspace(np.log10(self.energies.min()), np.log10(self.energies.max()), 50)
        spectrum, _ = np.histogram(self.energies, bins=energy_bins)
        
        # Fit power law
        from scipy.optimize import curve_fit
        
        def power_law(E, A, alpha):
            return A * E**(-alpha)
        
        # Use only bins with sufficient counts
        valid_bins = spectrum > 5
        if np.sum(valid_bins) > 5:
            bin_centers = (energy_bins[:-1] + energy_bins[1:]) / 2
            valid_centers = bin_centers[valid_bins]
            valid_spectrum = spectrum[valid_bins]
            
            try:
                popt, pcov = curve_fit(power_law, valid_centers, valid_spectrum, 
                                     p0=[1000, 2.0], maxfev=1000)
                spectral_index = popt[1]
                spectral_uncertainty = np.sqrt(pcov[1, 1])
            except:
                spectral_index = np.nan
                spectral_uncertainty = np.nan
        else:
            spectral_index = np.nan
            spectral_uncertainty = np.nan
        
        # Hardness ratio
        low_energy_mask = self.energies < 1.0
        high_energy_mask = self.energies >= 1.0
        
        hardness_ratio = np.sum(high_energy_mask) / np.sum(low_energy_mask)
        
        # Energy fluence
        energy_fluence = np.sum(self.energies)  # GeV
        
        self.results['spectral_properties'] = {
            'spectral_index': float(spectral_index),
            'spectral_uncertainty': float(spectral_uncertainty),
            'hardness_ratio': float(hardness_ratio),
            'energy_fluence_gev': float(energy_fluence),
            'n_spectral_bins': int(np.sum(valid_bins))
        }
        
        print(f"   📊 Spectral index: {spectral_index:.2f} ± {spectral_uncertainty:.2f}")
        print(f"   📊 Hardness ratio: {hardness_ratio:.3f}")
        print(f"   📊 Energy fluence: {energy_fluence:.1f} GeV")
        
    def compare_with_other_grbs(self):
        """Compare with other known GRBs"""
        print("\n🔬 Comparing with other GRBs...")
        
        # Known GRB properties for comparison
        comparison_grbs = {
            'GRB080916C': {
                'z': 4.35,
                'n_photons': 516,
                'e_max_gev': 13.2,
                't90_s': 66.5,
                'significance': 0.68
            },
            'GRB090510': {
                'z': 0.903,
                'n_photons': 2371,
                'e_max_gev': 31.0,
                't90_s': 0.3,
                'significance': 1.71
            },
            'GRB130427A': {
                'z': 0.34,
                'n_photons': 548,
                'e_max_gev': 95.0,
                't90_s': 162.8,
                'significance': 1.51
            },
            'GRB221009A': {
                'z': 0.151,
                'n_photons': 503,
                'e_max_gev': 17990.3,
                't90_s': 600.0,
                'significance': 0.94
            }
        }
        
        # GRB090902B properties
        grb090902_props = {
            'z': 1.822,  # Known redshift
            'n_photons': len(self.times),
            'e_max_gev': self.energies.max(),
            't90_s': self.results['temporal_structure']['t90_s'],
            'significance': self.results['energy_time_correlation']['pearson_significance']
        }
        
        # Calculate uniqueness scores
        uniqueness_scores = {}
        for prop in ['n_photons', 'e_max_gev', 't90_s', 'significance']:
            values = [grb090902_props[prop]] + [comp[prop] for comp in comparison_grbs.values()]
            grb090902_rank = sorted(values, reverse=True).index(grb090902_props[prop]) + 1
            uniqueness_scores[prop] = {
                'rank': grb090902_rank,
                'total': len(values),
                'percentile': 100 * (len(values) - grb090902_rank) / (len(values) - 1)
            }
        
        self.results['comparison'] = {
            'grb090902_properties': grb090902_props,
            'comparison_grbs': comparison_grbs,
            'uniqueness_scores': uniqueness_scores
        }
        
        print(f"   📊 GRB090902B vs others:")
        print(f"   📊 Photon count rank: {uniqueness_scores['n_photons']['rank']}/{uniqueness_scores['n_photons']['total']}")
        print(f"   📊 Max energy rank: {uniqueness_scores['e_max_gev']['rank']}/{uniqueness_scores['e_max_gev']['total']}")
        print(f"   📊 Significance rank: {uniqueness_scores['significance']['rank']}/{uniqueness_scores['significance']['total']}")
        
    def generate_plots(self):
        """Generate diagnostic plots"""
        print("\n🎨 Generating diagnostic plots...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'GRB090902B Property Analysis', fontsize=16, fontweight='bold')
        
        # Plot 1: Energy vs Time scatter
        ax1 = axes[0, 0]
        scatter = ax1.scatter(self.times, self.energies, c=self.energies, cmap='viridis', alpha=0.6, s=20)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Energy (GeV)')
        ax1.set_yscale('log')
        ax1.set_title('Energy vs Time')
        plt.colorbar(scatter, ax=ax1, label='Energy (GeV)')
        
        # Plot 2: Energy distribution
        ax2 = axes[0, 1]
        ax2.hist(self.energies, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax2.set_xlabel('Energy (GeV)')
        ax2.set_ylabel('Counts')
        ax2.set_xscale('log')
        ax2.set_title('Energy Distribution')
        
        # Plot 3: Light curve
        ax3 = axes[0, 2]
        time_bins = np.arange(self.times.min(), self.times.max() + 10, 10)
        light_curve = np.histogram(self.times, bins=time_bins)[0]
        bin_centers = (time_bins[:-1] + time_bins[1:]) / 2
        ax3.plot(bin_centers, light_curve, 'b-', linewidth=2)
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Counts per 10s')
        ax3.set_title('Light Curve')
        
        # Plot 4: Zenith angle distribution
        ax4 = axes[1, 0]
        ax4.hist(self.zenith, bins=30, alpha=0.7, color='green', edgecolor='black')
        ax4.set_xlabel('Zenith Angle (deg)')
        ax4.set_ylabel('Counts')
        ax4.set_title('Zenith Angle Distribution')
        
        # Plot 5: Energy-time correlation by energy bins
        ax5 = axes[1, 1]
        energy_bins = np.logspace(np.log10(self.energies.min()), np.log10(self.energies.max()), 10)
        bin_correlations = self.results['energy_time_correlation']['energy_bin_correlations']
        bin_centers = (energy_bins[:-1] + energy_bins[1:]) / 2
        valid_mask = ~np.isnan(bin_correlations)
        ax5.plot(bin_centers[valid_mask], np.array(bin_correlations)[valid_mask], 'ro-', linewidth=2, markersize=8)
        ax5.set_xlabel('Energy (GeV)')
        ax5.set_ylabel('Correlation')
        ax5.set_xscale('log')
        ax5.set_title('Correlation vs Energy')
        ax5.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        # Plot 6: Comparison with other GRBs
        ax6 = axes[1, 2]
        grb_names = list(self.results['comparison']['comparison_grbs'].keys()) + ['GRB090902B']
        significances = [self.results['comparison']['comparison_grbs'][grb]['significance'] for grb in self.results['comparison']['comparison_grbs']] + [self.results['energy_time_correlation']['pearson_significance']]
        colors = ['lightblue'] * len(self.results['comparison']['comparison_grbs']) + ['red']
        bars = ax6.bar(range(len(grb_names)), significances, color=colors, alpha=0.7, edgecolor='black')
        ax6.set_xlabel('GRB')
        ax6.set_ylabel('Significance (σ)')
        ax6.set_title('Significance Comparison')
        ax6.set_xticks(range(len(grb_names)))
        ax6.set_xticklabels(grb_names, rotation=45, ha='right')
        
        # Highlight GRB090902B
        bars[-1].set_color('red')
        bars[-1].set_alpha(1.0)
        
        plt.tight_layout()
        plt.savefig('grb090902_property_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Diagnostic plots saved: grb090902_property_analysis.png")
        
    def save_results(self):
        """Save analysis results"""
        print("\n💾 Saving results...")
        
        self.results['metadata'] = {
            'grb_name': self.grb_name,
            'filename': self.filename,
            'analysis_date': datetime.now().isoformat(),
            'n_photons': len(self.times),
            'energy_range_gev': [float(self.energies.min()), float(self.energies.max())],
            'time_range_s': [float(self.times.min()), float(self.times.max())]
        }
        
        # Convert numpy types to Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj
        
        results_serializable = convert_numpy_types(self.results)
        
        with open('grb090902_property_analysis.json', 'w') as f:
            json.dump(results_serializable, f, indent=2)
        
        print("✅ Results saved: grb090902_property_analysis.json")
        
    def run_complete_analysis(self):
        """Run complete GRB090902B investigation"""
        print("🚀 Starting complete GRB090902B investigation...")
        
        if not self.load_data():
            return False
        
        self.analyze_basic_properties()
        self.analyze_energy_time_correlation()
        self.analyze_temporal_structure()
        self.analyze_spectral_properties()
        self.compare_with_other_grbs()
        self.generate_plots()
        self.save_results()
        
        print("\n" + "="*70)
        print("🎉 GRB090902B INVESTIGATION COMPLETE!")
        print("="*70)
        
        # Summary
        print(f"📊 GRB090902B Summary:")
        print(f"   📊 Photons: {self.results['basic_properties']['n_photons']:,}")
        print(f"   📊 Max energy: {self.results['basic_properties']['energy_max_gev']:.1f} GeV")
        print(f"   📊 Correlation: {self.results['energy_time_correlation']['pearson_correlation']:.4f}")
        print(f"   📊 Significance: {self.results['energy_time_correlation']['pearson_significance']:.2f}σ")
        print(f"   📊 T90: {self.results['temporal_structure']['t90_s']:.1f} s")
        
        print(f"\n🎯 What makes GRB090902B special:")
        uniqueness = self.results['comparison']['uniqueness_scores']
        print(f"   🎯 Photon count: {uniqueness['n_photons']['percentile']:.1f}th percentile")
        print(f"   🎯 Max energy: {uniqueness['e_max_gev']['percentile']:.1f}th percentile")
        print(f"   🎯 Significance: {uniqueness['significance']['percentile']:.1f}th percentile")
        
        return True

def main():
    """Main function"""
    investigator = GRB090902BInvestigator()
    success = investigator.run_complete_analysis()
    
    if success:
        print("\n✅ GRB090902B investigation completed successfully!")
        print("📊 Check grb090902_property_analysis.json for detailed results")
        print("🎨 Check grb090902_property_analysis.png for diagnostic plots")
    else:
        print("\n❌ GRB090902B investigation failed!")

if __name__ == "__main__":
    main()
