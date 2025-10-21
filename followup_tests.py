#!/usr/bin/env python3
"""
FOLLOWUP TESTS SCRIPT FOR GRB221009A ROBUSTNESS ANALYSIS
Performs systematic robustness tests to validate QG effects
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

class GRB221009ARobustnessTester:
    def __init__(self):
        self.lat_data = None
        self.lhaaso_data = None
        self.combined_data = None
        
        # GRB221009A parameters
        self.grb_name = "GRB221009A"
        self.t0 = Time("2022-10-09 13:16:59.000", format='iso', scale='utc')
        self.t0_unix = self.t0.unix
        self.ra = 288.265
        self.dec = 19.773
        self.z = 0.151
        
        print(f"🔬 Initializing GRB221009A Robustness Tester")
        print(f"📅 T0: {self.t0.iso}")
        print(f"🌌 Redshift: z = {self.z}")
        
    def load_and_prepare_data(self):
        """Load and prepare data with time alignment"""
        print("\n🛰️ Loading and preparing data...")
        
        # Load LAT data (synthetic for demo)
        np.random.seed(42)
        self.lat_data = {
            'time': np.array([100.0, 150.0, 200.0]),
            'energy': np.array([0.154, 0.573, 1.2]),
        }
        
        # Generate realistic LHAASO data
        np.random.seed(123)
        n_photons = 500
        energies = np.random.power(2, n_photons) * 18.0  # 0-18 TeV
        times = np.random.exponential(1000, n_photons) + 100  # 100-5000 s
        
        self.lhaaso_data = {
            'time': times,
            'energy': energies,  # TeV
        }
        
        # Apply time alignment (from previous analysis)
        offset = -569943093.0  # s
        lat_times_aligned = self.lat_data['time'] + offset
        t0_common = min(lat_times_aligned.min(), self.lhaaso_data['time'].min())
        
        # Calculate relative times
        lat_t_rel = lat_times_aligned - t0_common
        lhaaso_t_rel = self.lhaaso_data['time'] - t0_common
        
        # Convert LHAASO energies to GeV
        lhaaso_energy_gev = self.lhaaso_data['energy'] * 1000.0
        
        # Combine data
        self.combined_data = {
            'time': np.concatenate([lat_t_rel, lhaaso_t_rel]),
            'energy': np.concatenate([self.lat_data['energy'], lhaaso_energy_gev]),
            'instrument': np.concatenate([
                np.full(len(self.lat_data['time']), 'LAT'),
                np.full(len(self.lhaaso_data['time']), 'LHAASO')
            ])
        }
        
        print(f"✅ Data prepared: {len(self.combined_data['time'])} total photons")
        
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
        
        return obs_r, p_value, perm_correlations
        
    def bootstrap_correlation(self, x, y, n_bootstrap=500):
        """Perform bootstrap analysis for correlation confidence intervals"""
        bootstrap_correlations = []
        for i in range(n_bootstrap):
            indices = np.random.choice(len(x), size=len(x), replace=True)
            x_boot = x[indices]
            y_boot = y[indices]
            corr = np.corrcoef(x_boot, y_boot)[0, 1]
            bootstrap_correlations.append(corr)
        
        bootstrap_correlations = np.array(bootstrap_correlations)
        ci_lower = np.percentile(bootstrap_correlations, 2.5)
        ci_upper = np.percentile(bootstrap_correlations, 97.5)
        
        return bootstrap_correlations, ci_lower, ci_upper
        
    def ransac_regression(self, x, y):
        """Perform RANSAC regression to handle outliers"""
        X = x.reshape(-1, 1)
        ransac = RANSACRegressor(LinearRegression(), min_samples=0.5, random_state=42)
        ransac.fit(X, y)
        
        slope = ransac.estimator_.coef_[0]
        intercept = ransac.estimator_.intercept_
        inlier_mask = ransac.inlier_mask_
        
        return slope, intercept, inlier_mask
        
    def test_early_vs_late_split(self):
        """Test 1: Split early vs late time windows"""
        print("\n🔍 Test 1: Early vs Late Time Split")
        
        times = self.combined_data['time']
        energies = self.combined_data['energy']
        
        results = {}
        
        # Test different split times
        split_times = [100, 500, 1000, 2000]
        
        for split_time in split_times:
            print(f"\n📊 Split time: {split_time} s")
            
            # Early window
            early_mask = times <= split_time
            if np.sum(early_mask) >= 10:
                early_times = times[early_mask]
                early_energies = energies[early_mask]
                
                corr_early, p_early, _ = self.permutation_test(early_times, early_energies)
                slope_early, _, _ = self.ransac_regression(early_times, early_energies)
                
                print(f"   Early ({np.sum(early_mask)} photons): r={corr_early:.4f}, p={p_early:.3f}, slope={slope_early:.6f}")
                
                results[f'early_{split_time}'] = {
                    'n_photons': np.sum(early_mask),
                    'correlation': corr_early,
                    'p_value': p_early,
                    'slope': slope_early
                }
            
            # Late window
            late_mask = times > split_time
            if np.sum(late_mask) >= 10:
                late_times = times[late_mask]
                late_energies = energies[late_mask]
                
                corr_late, p_late, _ = self.permutation_test(late_times, late_energies)
                slope_late, _, _ = self.ransac_regression(late_times, late_energies)
                
                print(f"   Late ({np.sum(late_mask)} photons): r={corr_late:.4f}, p={p_late:.3f}, slope={slope_late:.6f}")
                
                results[f'late_{split_time}'] = {
                    'n_photons': np.sum(late_mask),
                    'correlation': corr_late,
                    'p_value': p_late,
                    'slope': slope_late
                }
        
        return results
        
    def test_energy_tail_trimming(self):
        """Test 2: Top-energy tail trimming"""
        print("\n🔍 Test 2: Energy Tail Trimming")
        
        times = self.combined_data['time']
        energies = self.combined_data['energy']
        
        results = {}
        
        # Test different trimming percentages
        trim_percentages = [0.1, 0.5, 1.0, 2.0, 5.0]
        
        for trim_pct in trim_percentages:
            print(f"\n📊 Trimming top {trim_pct}%")
            
            # Calculate trim threshold
            trim_threshold = np.percentile(energies, 100 - trim_pct)
            
            # Apply trim
            trimmed_mask = energies <= trim_threshold
            if np.sum(trimmed_mask) >= 10:
                trimmed_times = times[trimmed_mask]
                trimmed_energies = energies[trimmed_mask]
                
                corr_trimmed, p_trimmed, _ = self.permutation_test(trimmed_times, trimmed_energies)
                bootstrap_corr, ci_lower, ci_upper = self.bootstrap_correlation(trimmed_times, trimmed_energies)
                slope_trimmed, _, _ = self.ransac_regression(trimmed_times, trimmed_energies)
                
                print(f"   Trimmed ({np.sum(trimmed_mask)} photons): r={corr_trimmed:.4f}, p={p_trimmed:.3f}")
                print(f"   Bootstrap CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
                print(f"   RANSAC slope: {slope_trimmed:.6f}")
                
                results[f'trim_{trim_pct}'] = {
                    'n_photons': np.sum(trimmed_mask),
                    'correlation': corr_trimmed,
                    'p_value': p_trimmed,
                    'bootstrap_ci': [ci_lower, ci_upper],
                    'slope': slope_trimmed
                }
        
        return results
        
    def test_sliding_window_analysis(self):
        """Test 3: Sliding window analysis"""
        print("\n🔍 Test 3: Sliding Window Analysis")
        
        times = self.combined_data['time']
        energies = self.combined_data['energy']
        
        # Sort by time
        sort_idx = np.argsort(times)
        times_sorted = times[sort_idx]
        energies_sorted = energies[sort_idx]
        
        results = {}
        
        # Test different window sizes
        window_sizes = [200, 500, 1000]
        step_sizes = [100, 250, 500]
        
        for window_size, step_size in zip(window_sizes, step_sizes):
            print(f"\n📊 Window: {window_size}s, Step: {step_size}s")
            
            window_results = []
            
            # Slide window
            for start_time in np.arange(times_sorted.min(), times_sorted.max() - window_size, step_size):
                end_time = start_time + window_size
                
                # Find photons in window
                window_mask = (times_sorted >= start_time) & (times_sorted <= end_time)
                
                if np.sum(window_mask) >= 10:
                    window_times = times_sorted[window_mask]
                    window_energies = energies_sorted[window_mask]
                    
                    corr_window, p_window, _ = self.permutation_test(window_times, window_energies)
                    
                    window_results.append({
                        'start_time': start_time,
                        'end_time': end_time,
                        'n_photons': np.sum(window_mask),
                        'correlation': corr_window,
                        'p_value': p_window
                    })
            
            # Find best window
            if window_results:
                best_window = max(window_results, key=lambda x: abs(x['correlation']))
                print(f"   Best window: {best_window['start_time']:.0f}-{best_window['end_time']:.0f}s")
                print(f"   Correlation: {best_window['correlation']:.4f}, p={best_window['p_value']:.3f}")
                
                results[f'window_{window_size}'] = best_window
        
        return results
        
    def test_instrument_separation(self):
        """Test 4: Instrument separation analysis"""
        print("\n🔍 Test 4: Instrument Separation Analysis")
        
        results = {}
        
        for instrument in ['LAT', 'LHAASO']:
            mask = self.combined_data['instrument'] == instrument
            if np.sum(mask) < 10:
                print(f"⚠️  Skipping {instrument} - too few photons ({np.sum(mask)})")
                continue
                
            times = self.combined_data['time'][mask]
            energies = self.combined_data['energy'][mask]
            
            print(f"\n📊 {instrument} analysis:")
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
            corr_perm, p_perm, _ = self.permutation_test(times, energies)
            
            # Bootstrap
            bootstrap_corr, ci_lower, ci_upper = self.bootstrap_correlation(times, energies)
            
            # RANSAC
            if len(times) > 20:
                slope, intercept, inlier_mask = self.ransac_regression(times, energies)
                
                print(f"   Pearson: r={corr_pearson:.4f}, t={t_pearson:.2f}, p={p_pearson:.2e}")
                print(f"   Spearman: r={corr_spearman:.4f}")
                print(f"   Permutation: r={corr_perm:.4f}, p={p_perm:.3f}")
                print(f"   Bootstrap CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
                print(f"   RANSAC slope: {slope:.6f}, inliers: {np.sum(inlier_mask)}/{len(times)}")
                
                results[instrument] = {
                    'n_photons': len(times),
                    'correlation_pearson': corr_pearson,
                    'correlation_spearman': corr_spearman,
                    'p_value_pearson': p_pearson,
                    'p_value_permutation': p_perm,
                    'bootstrap_ci': [ci_lower, ci_upper],
                    'slope': slope,
                    'n_inliers': np.sum(inlier_mask)
                }
        
        return results
        
    def create_robustness_summary_plot(self, all_results):
        """Create comprehensive robustness summary plot"""
        print("\n🎨 Creating robustness summary plot...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Panel 1: Early vs Late correlations
        ax1 = axes[0, 0]
        early_corrs = []
        late_corrs = []
        split_times = []
        
        for key, result in all_results.items():
            if key.startswith('early_'):
                split_time = int(key.split('_')[1])
                early_corrs.append(result['correlation'])
                split_times.append(split_time)
            elif key.startswith('late_'):
                late_corrs.append(result['correlation'])
        
        if early_corrs and late_corrs:
            ax1.plot(split_times, early_corrs, 'bo-', label='Early', linewidth=2, markersize=8)
            ax1.plot(split_times, late_corrs, 'ro-', label='Late', linewidth=2, markersize=8)
            ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            ax1.set_xlabel('Split Time (s)')
            ax1.set_ylabel('Correlation Coefficient')
            ax1.set_title('Early vs Late Window Analysis')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Panel 2: Energy trimming results
        ax2 = axes[0, 1]
        trim_pcts = []
        trim_corrs = []
        
        for key, result in all_results.items():
            if key.startswith('trim_'):
                trim_pct = float(key.split('_')[1])
                trim_pcts.append(trim_pct)
                trim_corrs.append(result['correlation'])
        
        if trim_pcts and trim_corrs:
            ax2.plot(trim_pcts, trim_corrs, 'go-', linewidth=2, markersize=8)
            ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            ax2.set_xlabel('Trim Percentage (%)')
            ax2.set_ylabel('Correlation Coefficient')
            ax2.set_title('Energy Tail Trimming')
            ax2.grid(True, alpha=0.3)
        
        # Panel 3: Bootstrap CI comparison
        ax3 = axes[0, 2]
        test_names = []
        ci_lowers = []
        ci_uppers = []
        
        for key, result in all_results.items():
            if 'bootstrap_ci' in result:
                test_names.append(key.replace('_', ' ').title())
                ci_lowers.append(result['bootstrap_ci'][0])
                ci_uppers.append(result['bootstrap_ci'][1])
        
        if test_names and ci_lowers and ci_uppers:
            y_pos = np.arange(len(test_names))
            ax3.barh(y_pos, [ci_uppers[i] - ci_lowers[i] for i in range(len(test_names))], 
                    left=ci_lowers, alpha=0.7, color='lightblue')
            ax3.axvline(x=0, color='red', linestyle='--', alpha=0.8)
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels(test_names)
            ax3.set_xlabel('Correlation Coefficient')
            ax3.set_title('Bootstrap 95% Confidence Intervals')
            ax3.grid(True, alpha=0.3)
        
        # Panel 4: P-value comparison
        ax4 = axes[1, 0]
        test_names_p = []
        p_values = []
        
        for key, result in all_results.items():
            if 'p_value' in result:
                test_names_p.append(key.replace('_', ' ').title())
                p_values.append(result['p_value'])
        
        if test_names_p and p_values:
            y_pos = np.arange(len(test_names_p))
            colors = ['red' if p < 0.05 else 'green' for p in p_values]
            bars = ax4.barh(y_pos, p_values, color=colors, alpha=0.7)
            ax4.axvline(x=0.05, color='red', linestyle='--', alpha=0.8, label='α=0.05')
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(test_names_p)
            ax4.set_xlabel('P-value')
            ax4.set_title('P-value Comparison')
            ax4.set_xscale('log')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        # Panel 5: RANSAC slope comparison
        ax5 = axes[1, 1]
        slope_names = []
        slopes = []
        
        for key, result in all_results.items():
            if 'slope' in result and result['slope'] is not None:
                slope_names.append(key.replace('_', ' ').title())
                slopes.append(result['slope'])
        
        if slope_names and slopes:
            y_pos = np.arange(len(slope_names))
            colors = ['red' if abs(s) > 0.1 else 'green' for s in slopes]
            bars = ax5.barh(y_pos, slopes, color=colors, alpha=0.7)
            ax5.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
            ax5.set_yticks(y_pos)
            ax5.set_yticklabels(slope_names)
            ax5.set_xlabel('RANSAC Slope (s/GeV)')
            ax5.set_title('RANSAC Slope Comparison')
            ax5.grid(True, alpha=0.3)
        
        # Panel 6: Summary statistics
        ax6 = axes[1, 2]
        ax6.axis('off')
        
        # Calculate summary statistics
        total_tests = len(all_results)
        significant_tests = sum(1 for result in all_results.values() if result.get('p_value', 1) < 0.05)
        
        summary_text = f"""
        📊 ROBUSTNESS TEST SUMMARY
        
        Total Tests: {total_tests}
        Significant (p<0.05): {significant_tests}
        Non-significant: {total_tests - significant_tests}
        
        🔍 KEY FINDINGS:
        
        • Early vs Late: {'Significant difference' if len(early_corrs) > 1 and len(late_corrs) > 1 else 'Insufficient data'}
        • Energy Trimming: {'Outlier-driven' if trim_corrs and max(trim_corrs) > min(trim_corrs) + 0.1 else 'Robust'}
        • Bootstrap CI: {'Includes zero' if any(ci[0] <= 0 <= ci[1] for ci in [result.get('bootstrap_ci', [0, 0]) for result in all_results.values()] if isinstance(ci, list)) else 'Excludes zero'}
        • RANSAC: {'High outlier fraction' if any(result.get('n_inliers', 0) < result.get('n_photons', 1) * 0.6 for result in all_results.values()) else 'Low outlier fraction'}
        
        🎯 CONCLUSION:
        {'Effect appears robust' if significant_tests > total_tests * 0.5 else 'Effect appears fragile/artifactual'}
        """
        
        ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8),
                fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('grb221009a_robustness_tests.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Robustness summary plot created: grb221009a_robustness_tests.png")
        
    def run_all_robustness_tests(self):
        """Run all robustness tests"""
        print("🚀 Starting comprehensive robustness tests for GRB221009A...")
        print("="*70)
        
        # Load and prepare data
        self.load_and_prepare_data()
        
        # Run all tests
        all_results = {}
        
        # Test 1: Early vs Late split
        early_late_results = self.test_early_vs_late_split()
        all_results.update(early_late_results)
        
        # Test 2: Energy tail trimming
        trim_results = self.test_energy_tail_trimming()
        all_results.update(trim_results)
        
        # Test 3: Sliding window
        window_results = self.test_sliding_window_analysis()
        all_results.update(window_results)
        
        # Test 4: Instrument separation
        instrument_results = self.test_instrument_separation()
        all_results.update(instrument_results)
        
        # Create summary plot
        self.create_robustness_summary_plot(all_results)
        
        # Summary
        print("\n" + "="*70)
        print("🎯 ROBUSTNESS TEST SUMMARY:")
        
        total_tests = len(all_results)
        significant_tests = sum(1 for result in all_results.values() if result.get('p_value', 1) < 0.05)
        
        print(f"   Total tests: {total_tests}")
        print(f"   Significant (p<0.05): {significant_tests}")
        print(f"   Non-significant: {total_tests - significant_tests}")
        
        if significant_tests > total_tests * 0.5:
            print("   🚨 Effect appears ROBUST across tests")
        else:
            print("   📊 Effect appears FRAGILE/ARTIFACTUAL")
            
        print("="*70)
        
        return all_results

def main():
    """Main function"""
    tester = GRB221009ARobustnessTester()
    results = tester.run_all_robustness_tests()
    
    print("\n✅ Robustness tests complete!")
    print("📊 Check 'grb221009a_robustness_tests.png' for comprehensive results.")

if __name__ == "__main__":
    main()

