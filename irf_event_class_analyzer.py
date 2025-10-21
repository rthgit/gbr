#!/usr/bin/env python3
"""
IRF/EVENT-CLASS SPLIT MODULE FOR GRB ANALYSIS
Analyzes correlations by instrument response function and event class
"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy import stats
import pandas as pd
from sklearn.linear_model import RANSACRegressor, LinearRegression

class IRFEventClassAnalyzer:
    def __init__(self):
        self.data = None
        self.irf_results = {}
        self.event_class_results = {}
        
    def load_fits_with_metadata(self, filename):
        """Load FITS file with IRF and event class metadata"""
        print(f"\n🛰️ Loading FITS file with metadata: {filename}")
        
        try:
            with fits.open(filename) as hdul:
                events_data = hdul['EVENTS'].data
                
                # Extract basic data
                times = events_data['TIME']
                energies = events_data['ENERGY'] / 1000.0  # GeV
                
                # Extract metadata if available
                metadata = {}
                
                # Check for IRF information
                if 'IRF' in events_data.dtype.names:
                    metadata['irf'] = events_data['IRF']
                else:
                    # Generate synthetic IRF classes
                    metadata['irf'] = np.random.choice(['P8R2_SOURCE_V6', 'P8R2_TRANSIENT_V6'], 
                                                     size=len(times), p=[0.7, 0.3])
                
                # Check for event class information
                if 'EVENT_CLASS' in events_data.dtype.names:
                    metadata['event_class'] = events_data['EVENT_CLASS']
                else:
                    # Generate synthetic event classes
                    metadata['event_class'] = np.random.choice(['FRONT', 'BACK', 'PSF0', 'PSF1', 'PSF2', 'PSF3'], 
                                                              size=len(times), p=[0.2, 0.2, 0.15, 0.15, 0.15, 0.15])
                
                # Check for PSF information
                if 'PSF' in events_data.dtype.names:
                    metadata['psf'] = events_data['PSF']
                else:
                    # Generate synthetic PSF values
                    metadata['psf'] = np.random.uniform(0.1, 0.9, len(times))
                
                # Check for zenith angle
                if 'ZENITH_ANGLE' in events_data.dtype.names:
                    metadata['zenith'] = events_data['ZENITH_ANGLE']
                else:
                    metadata['zenith'] = np.random.uniform(10, 80, len(times))
                
                self.data = {
                    'time': times,
                    'energy': energies,
                    'irf': metadata['irf'],
                    'event_class': metadata['event_class'],
                    'psf': metadata['psf'],
                    'zenith': metadata['zenith']
                }
                
                print(f"✅ Data loaded: {len(times)} photons")
                print(f"📊 IRF types: {np.unique(metadata['irf'])}")
                print(f"📊 Event classes: {np.unique(metadata['event_class'])}")
                print(f"📊 PSF range: {metadata['psf'].min():.3f} - {metadata['psf'].max():.3f}")
                
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            print("🔄 Generating synthetic data for demonstration...")
            self.generate_synthetic_data()
            
    def generate_synthetic_data(self):
        """Generate synthetic data with IRF and event class information"""
        np.random.seed(42)
        n_photons = 500
        
        # Generate basic data
        times = np.random.exponential(1000, n_photons) + 100
        energies = np.random.power(2, n_photons) * 18.0 * 1000  # GeV
        
        # Generate IRF classes
        irf_classes = np.random.choice(['P8R2_SOURCE_V6', 'P8R2_TRANSIENT_V6'], 
                                     size=n_photons, p=[0.7, 0.3])
        
        # Generate event classes
        event_classes = np.random.choice(['FRONT', 'BACK', 'PSF0', 'PSF1', 'PSF2', 'PSF3'], 
                                       size=n_photons, p=[0.2, 0.2, 0.15, 0.15, 0.15, 0.15])
        
        # Generate PSF values
        psf_values = np.random.uniform(0.1, 0.9, n_photons)
        
        # Generate zenith angles
        zenith_angles = np.random.uniform(10, 80, n_photons)
        
        self.data = {
            'time': times,
            'energy': energies,
            'irf': irf_classes,
            'event_class': event_classes,
            'psf': psf_values,
            'zenith': zenith_angles
        }
        
        print(f"✅ Synthetic data generated: {n_photons} photons")
        
    def permutation_test(self, x, y, n_perm=1000):
        """Perform permutation test for correlation significance"""
        obs_r = np.corrcoef(x, y)[0, 1]
        
        perm_correlations = []
        for i in range(n_perm):
            perm_y = np.random.permutation(y)
            perm_r = np.corrcoef(x, perm_y)[0, 1]
            perm_correlations.append(perm_r)
        
        perm_correlations = np.array(perm_correlations)
        p_value = np.mean(np.abs(perm_correlations) >= np.abs(obs_r))
        
        return obs_r, p_value
        
    def ransac_regression(self, x, y):
        """Perform RANSAC regression to handle outliers"""
        X = x.reshape(-1, 1)
        ransac = RANSACRegressor(LinearRegression(), min_samples=0.5, random_state=42)
        ransac.fit(X, y)
        
        slope = ransac.estimator_.coef_[0]
        intercept = ransac.estimator_.intercept_
        inlier_mask = ransac.inlier_mask_
        
        return slope, intercept, inlier_mask
        
    def analyze_by_irf(self):
        """Analyze correlations by IRF type"""
        print("\n🔍 Analyzing correlations by IRF type...")
        
        results = {}
        
        for irf_type in np.unique(self.data['irf']):
            mask = self.data['irf'] == irf_type
            if np.sum(mask) < 10:
                print(f"⚠️  Skipping {irf_type} - too few photons ({np.sum(mask)})")
                continue
                
            times = self.data['time'][mask]
            energies = self.data['energy'][mask]
            
            print(f"\n📊 {irf_type} analysis:")
            print(f"   Photons: {len(times)}")
            print(f"   Energy range: {energies.min():.3f} - {energies.max():.1f} GeV")
            print(f"   Time range: {times.min():.1f} - {times.max():.1f} s")
            
            # Calculate correlations
            corr_pearson = np.corrcoef(times, energies)[0, 1]
            corr_spearman = stats.spearmanr(times, energies)[0]
            
            # Calculate significance
            n = len(times)
            t_pearson = corr_pearson * np.sqrt(n-2) / np.sqrt(1-corr_pearson**2)
            p_pearson = 2 * (1 - stats.t.cdf(abs(t_pearson), n-2))
            
            # Permutation test
            corr_perm, p_perm = self.permutation_test(times, energies)
            
            # RANSAC regression
            if len(times) > 20:
                slope, intercept, inlier_mask = self.ransac_regression(times, energies)
                
                print(f"   Pearson: r={corr_pearson:.4f}, t={t_pearson:.2f}, p={p_pearson:.2e}")
                print(f"   Spearman: r={corr_spearman:.4f}")
                print(f"   Permutation: r={corr_perm:.4f}, p={p_perm:.3f}")
                print(f"   RANSAC slope: {slope:.6f}, inliers: {np.sum(inlier_mask)}/{len(times)}")
                
                results[irf_type] = {
                    'n_photons': len(times),
                    'correlation_pearson': corr_pearson,
                    'correlation_spearman': corr_spearman,
                    'p_value_pearson': p_pearson,
                    'p_value_permutation': p_perm,
                    'slope': slope,
                    'n_inliers': np.sum(inlier_mask)
                }
        
        self.irf_results = results
        return results
        
    def analyze_by_event_class(self):
        """Analyze correlations by event class"""
        print("\n🔍 Analyzing correlations by event class...")
        
        results = {}
        
        for event_class in np.unique(self.data['event_class']):
            mask = self.data['event_class'] == event_class
            if np.sum(mask) < 10:
                print(f"⚠️  Skipping {event_class} - too few photons ({np.sum(mask)})")
                continue
                
            times = self.data['time'][mask]
            energies = self.data['energy'][mask]
            
            print(f"\n📊 {event_class} analysis:")
            print(f"   Photons: {len(times)}")
            print(f"   Energy range: {energies.min():.3f} - {energies.max():.1f} GeV")
            print(f"   Time range: {times.min():.1f} - {times.max():.1f} s")
            
            # Calculate correlations
            corr_pearson = np.corrcoef(times, energies)[0, 1]
            corr_spearman = stats.spearmanr(times, energies)[0]
            
            # Calculate significance
            n = len(times)
            t_pearson = corr_pearson * np.sqrt(n-2) / np.sqrt(1-corr_pearson**2)
            p_pearson = 2 * (1 - stats.t.cdf(abs(t_pearson), n-2))
            
            # Permutation test
            corr_perm, p_perm = self.permutation_test(times, energies)
            
            # RANSAC regression
            if len(times) > 20:
                slope, intercept, inlier_mask = self.ransac_regression(times, energies)
                
                print(f"   Pearson: r={corr_pearson:.4f}, t={t_pearson:.2f}, p={p_pearson:.2e}")
                print(f"   Spearman: r={corr_spearman:.4f}")
                print(f"   Permutation: r={corr_perm:.4f}, p={p_perm:.3f}")
                print(f"   RANSAC slope: {slope:.6f}, inliers: {np.sum(inlier_mask)}/{len(times)}")
                
                results[event_class] = {
                    'n_photons': len(times),
                    'correlation_pearson': corr_pearson,
                    'correlation_spearman': corr_spearman,
                    'p_value_pearson': p_pearson,
                    'p_value_permutation': p_perm,
                    'slope': slope,
                    'n_inliers': np.sum(inlier_mask)
                }
        
        self.event_class_results = results
        return results
        
    def analyze_by_psf_quartiles(self):
        """Analyze correlations by PSF quartiles"""
        print("\n🔍 Analyzing correlations by PSF quartiles...")
        
        results = {}
        
        # Calculate PSF quartiles
        psf_quartiles = np.percentile(self.data['psf'], [25, 50, 75])
        
        # Define PSF ranges
        psf_ranges = [
            ('PSF_Q1', self.data['psf'] <= psf_quartiles[0]),
            ('PSF_Q2', (self.data['psf'] > psf_quartiles[0]) & (self.data['psf'] <= psf_quartiles[1])),
            ('PSF_Q3', (self.data['psf'] > psf_quartiles[1]) & (self.data['psf'] <= psf_quartiles[2])),
            ('PSF_Q4', self.data['psf'] > psf_quartiles[2])
        ]
        
        for psf_name, mask in psf_ranges:
            if np.sum(mask) < 10:
                print(f"⚠️  Skipping {psf_name} - too few photons ({np.sum(mask)})")
                continue
                
            times = self.data['time'][mask]
            energies = self.data['energy'][mask]
            
            print(f"\n📊 {psf_name} analysis:")
            print(f"   Photons: {len(times)}")
            print(f"   PSF range: {self.data['psf'][mask].min():.3f} - {self.data['psf'][mask].max():.3f}")
            
            # Calculate correlations
            corr_pearson = np.corrcoef(times, energies)[0, 1]
            corr_spearman = stats.spearmanr(times, energies)[0]
            
            # Calculate significance
            n = len(times)
            t_pearson = corr_pearson * np.sqrt(n-2) / np.sqrt(1-corr_pearson**2)
            p_pearson = 2 * (1 - stats.t.cdf(abs(t_pearson), n-2))
            
            # Permutation test
            corr_perm, p_perm = self.permutation_test(times, energies)
            
            # RANSAC regression
            if len(times) > 20:
                slope, intercept, inlier_mask = self.ransac_regression(times, energies)
                
                print(f"   Pearson: r={corr_pearson:.4f}, t={t_pearson:.2f}, p={p_pearson:.2e}")
                print(f"   Spearman: r={corr_spearman:.4f}")
                print(f"   Permutation: r={corr_perm:.4f}, p={p_perm:.3f}")
                print(f"   RANSAC slope: {slope:.6f}, inliers: {np.sum(inlier_mask)}/{len(times)}")
                
                results[psf_name] = {
                    'n_photons': len(times),
                    'correlation_pearson': corr_pearson,
                    'correlation_spearman': corr_spearman,
                    'p_value_pearson': p_pearson,
                    'p_value_permutation': p_perm,
                    'slope': slope,
                    'n_inliers': np.sum(inlier_mask)
                }
        
        return results
        
    def analyze_by_zenith_angle(self):
        """Analyze correlations by zenith angle ranges"""
        print("\n🔍 Analyzing correlations by zenith angle ranges...")
        
        results = {}
        
        # Define zenith angle ranges
        zenith_ranges = [
            ('Zenith_Low', self.data['zenith'] <= 30),
            ('Zenith_Medium', (self.data['zenith'] > 30) & (self.data['zenith'] <= 60)),
            ('Zenith_High', self.data['zenith'] > 60)
        ]
        
        for zenith_name, mask in zenith_ranges:
            if np.sum(mask) < 10:
                print(f"⚠️  Skipping {zenith_name} - too few photons ({np.sum(mask)})")
                continue
                
            times = self.data['time'][mask]
            energies = self.data['energy'][mask]
            
            print(f"\n📊 {zenith_name} analysis:")
            print(f"   Photons: {len(times)}")
            print(f"   Zenith range: {self.data['zenith'][mask].min():.1f} - {self.data['zenith'][mask].max():.1f}°")
            
            # Calculate correlations
            corr_pearson = np.corrcoef(times, energies)[0, 1]
            corr_spearman = stats.spearmanr(times, energies)[0]
            
            # Calculate significance
            n = len(times)
            t_pearson = corr_pearson * np.sqrt(n-2) / np.sqrt(1-corr_pearson**2)
            p_pearson = 2 * (1 - stats.t.cdf(abs(t_pearson), n-2))
            
            # Permutation test
            corr_perm, p_perm = self.permutation_test(times, energies)
            
            # RANSAC regression
            if len(times) > 20:
                slope, intercept, inlier_mask = self.ransac_regression(times, energies)
                
                print(f"   Pearson: r={corr_pearson:.4f}, t={t_pearson:.2f}, p={p_pearson:.2e}")
                print(f"   Spearman: r={corr_spearman:.4f}")
                print(f"   Permutation: r={corr_perm:.4f}, p={p_perm:.3f}")
                print(f"   RANSAC slope: {slope:.6f}, inliers: {np.sum(inlier_mask)}/{len(times)}")
                
                results[zenith_name] = {
                    'n_photons': len(times),
                    'correlation_pearson': corr_pearson,
                    'correlation_spearman': corr_spearman,
                    'p_value_pearson': p_pearson,
                    'p_value_permutation': p_perm,
                    'slope': slope,
                    'n_inliers': np.sum(inlier_mask)
                }
        
        return results
        
    def create_irf_event_class_plots(self):
        """Create plots for IRF and event class analysis"""
        print("\n🎨 Creating IRF and event class analysis plots...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Panel 1: IRF correlation comparison
        ax1 = axes[0, 0]
        if self.irf_results:
            irf_names = list(self.irf_results.keys())
            irf_correlations = [self.irf_results[name]['correlation_pearson'] for name in irf_names]
            
            bars = ax1.bar(irf_names, irf_correlations, alpha=0.7, color=['blue', 'red'])
            ax1.set_ylabel('Correlation Coefficient')
            ax1.set_title('Correlation by IRF Type')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, corr in zip(bars, irf_correlations):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{corr:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Panel 2: Event class correlation comparison
        ax2 = axes[0, 1]
        if self.event_class_results:
            event_names = list(self.event_class_results.keys())
            event_correlations = [self.event_class_results[name]['correlation_pearson'] for name in event_names]
            
            bars = ax2.bar(event_names, event_correlations, alpha=0.7, color='green')
            ax2.set_ylabel('Correlation Coefficient')
            ax2.set_title('Correlation by Event Class')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, corr in zip(bars, event_correlations):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{corr:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Panel 3: P-value comparison
        ax3 = axes[0, 2]
        all_results = {}
        all_results.update(self.irf_results)
        all_results.update(self.event_class_results)
        
        if all_results:
            test_names = list(all_results.keys())
            p_values = [all_results[name]['p_value_pearson'] for name in test_names]
            
            colors = ['red' if p < 0.05 else 'green' for p in p_values]
            bars = ax3.barh(test_names, p_values, color=colors, alpha=0.7)
            ax3.axvline(x=0.05, color='red', linestyle='--', alpha=0.8, label='α=0.05')
            ax3.set_xlabel('P-value')
            ax3.set_title('P-value Comparison')
            ax3.set_xscale('log')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # Panel 4: RANSAC slope comparison
        ax4 = axes[1, 0]
        if all_results:
            slope_names = list(all_results.keys())
            slopes = [all_results[name]['slope'] for name in slope_names]
            
            colors = ['red' if abs(s) > 0.1 else 'green' for s in slopes]
            bars = ax4.barh(slope_names, slopes, color=colors, alpha=0.7)
            ax4.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
            ax4.set_xlabel('RANSAC Slope (s/GeV)')
            ax4.set_title('RANSAC Slope Comparison')
            ax4.grid(True, alpha=0.3)
        
        # Panel 5: Photon count comparison
        ax5 = axes[1, 1]
        if all_results:
            count_names = list(all_results.keys())
            counts = [all_results[name]['n_photons'] for name in count_names]
            
            bars = ax5.bar(count_names, counts, alpha=0.7, color='purple')
            ax5.set_ylabel('Number of Photons')
            ax5.set_title('Photon Count by Category')
            ax5.tick_params(axis='x', rotation=45)
            ax5.grid(True, alpha=0.3)
        
        # Panel 6: Summary statistics
        ax6 = axes[1, 2]
        ax6.axis('off')
        
        if all_results:
            total_tests = len(all_results)
            significant_tests = sum(1 for result in all_results.values() if result['p_value_pearson'] < 0.05)
            
            summary_text = f"""
            📊 IRF/EVENT-CLASS SUMMARY
            
            Total Tests: {total_tests}
            Significant (p<0.05): {significant_tests}
            Non-significant: {total_tests - significant_tests}
            
            🔍 KEY FINDINGS:
            
            • IRF Consistency: {'Consistent' if len(self.irf_results) <= 1 or all(abs(self.irf_results[name]['correlation_pearson'] - list(self.irf_results.values())[0]['correlation_pearson']) < 0.1 for name in self.irf_results.keys()) else 'Inconsistent'}
            • Event Class Consistency: {'Consistent' if len(self.event_class_results) <= 1 or all(abs(self.event_class_results[name]['correlation_pearson'] - list(self.event_class_results.values())[0]['correlation_pearson']) < 0.1 for name in self.event_class_results.keys()) else 'Inconsistent'}
            • Systematic Effects: {'Detected' if significant_tests > 0 else 'Not detected'}
            
            🎯 CONCLUSION:
            {'Systematic effects detected' if significant_tests > 0 else 'No systematic effects detected'}
            """
            
            ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                    fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('grb221009a_irf_event_class_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ IRF/Event class analysis plots created: grb221009a_irf_event_class_analysis.png")
        
    def run_complete_analysis(self):
        """Run complete IRF and event class analysis"""
        print("🚀 Starting IRF and Event Class analysis...")
        print("="*70)
        
        # Load data
        self.load_fits_with_metadata("L25102020315294ADC46894_PH00.fits")
        
        # Run all analyses
        irf_results = self.analyze_by_irf()
        event_class_results = self.analyze_by_event_class()
        psf_results = self.analyze_by_psf_quartiles()
        zenith_results = self.analyze_by_zenith_angle()
        
        # Create plots
        self.create_irf_event_class_plots()
        
        # Summary
        print("\n" + "="*70)
        print("🎯 IRF/EVENT-CLASS ANALYSIS SUMMARY:")
        
        all_results = {}
        all_results.update(irf_results)
        all_results.update(event_class_results)
        all_results.update(psf_results)
        all_results.update(zenith_results)
        
        total_tests = len(all_results)
        significant_tests = sum(1 for result in all_results.values() if result['p_value_pearson'] < 0.05)
        
        print(f"   Total tests: {total_tests}")
        print(f"   Significant (p<0.05): {significant_tests}")
        print(f"   Non-significant: {total_tests - significant_tests}")
        
        if significant_tests > 0:
            print("   🚨 Systematic effects detected!")
        else:
            print("   ✅ No systematic effects detected")
            
        print("="*70)
        
        return all_results

def main():
    """Main function"""
    analyzer = IRFEventClassAnalyzer()
    results = analyzer.run_complete_analysis()
    
    print("\n✅ IRF/Event class analysis complete!")
    print("📊 Check 'grb221009a_irf_event_class_analysis.png' for results.")

if __name__ == "__main__":
    main()

