#!/usr/bin/env python3
"""
Batch GRB Analyzer for Multiple GRB Candidates
Analyzes multiple GRBs using the same methodology as GRB090902B
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.cosmology import Planck18
import json
from datetime import datetime
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit
import os
import glob

class BatchGRBAnalyzer:
    def __init__(self):
        self.results = {}
        self.analysis_methods = [
            'energy_time_correlation',
            'permutation_test',
            'bootstrap_analysis',
            'ransac_regression',
            'spectral_lag_analysis'
        ]
        
        print(f"⚡ Batch GRB Analyzer for Multiple Candidates")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
    def load_grb_list(self):
        """Load list of GRBs to analyze"""
        print("\n📋 Loading GRB list...")
        
        # Define GRB candidates (in real implementation, this would come from catalog analysis)
        self.grb_candidates = [
            {
                'name': 'GRB090902B',
                'filename': 'L251020161615F357373F52_EV00.fits',
                'z': 1.822,
                'priority': 'HIGH',
                'expected_significance': 5.46
            },
            {
                'name': 'GRB150403A',
                'filename': 'L251020154246F357373F64_EV00.fits',  # Using available file
                'z': 2.06,
                'priority': 'HIGH',
                'expected_significance': 0.68
            },
            {
                'name': 'GRB090510',
                'filename': 'L251020161912F357373F19_EV00.fits',
                'z': 0.903,
                'priority': 'MEDIUM',
                'expected_significance': 1.71
            },
            {
                'name': 'GRB130427A',
                'filename': 'L251020164901F357373F96_EV00.fits',
                'z': 0.34,
                'priority': 'MEDIUM',
                'expected_significance': 1.51
            },
            {
                'name': 'GRB221009A',
                'filename': 'L25102020315294ADC46894_PH00.fits',
                'z': 0.151,
                'priority': 'HIGH',
                'expected_significance': 0.94
            }
        ]
        
        print(f"✅ Loaded {len(self.grb_candidates)} GRB candidates")
        for grb in self.grb_candidates:
            print(f"   📊 {grb['name']}: z={grb['z']}, priority={grb['priority']}")
        
        return True
        
    def analyze_single_grb(self, grb_info):
        """Analyze a single GRB"""
        print(f"\n🔬 Analyzing {grb_info['name']}...")
        
        try:
            # Load data
            if not os.path.exists(grb_info['filename']):
                print(f"   ❌ File not found: {grb_info['filename']}")
                return None
            
            with fits.open(grb_info['filename']) as hdul:
                events_data = hdul['EVENTS'].data
                
            times = events_data['TIME']
            energies = events_data['ENERGY'] / 1000.0  # Convert to GeV
            zenith = events_data['ZENITH_ANGLE']
            
            print(f"   📊 Loaded {len(times)} photons")
            print(f"   📊 Energy range: {energies.min():.3f} - {energies.max():.1f} GeV")
            
            # Perform analysis
            analysis_results = {}
            
            # 1. Energy-time correlation
            correlation = np.corrcoef(energies, times)[0, 1]
            n = len(energies)
            significance = abs(correlation) * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
            
            analysis_results['energy_time_correlation'] = {
                'correlation': float(correlation),
                'significance': float(significance),
                'n_photons': n
            }
            
            # 2. Permutation test
            n_permutations = 1000
            perm_correlations = []
            for _ in range(n_permutations):
                perm_times = np.random.permutation(times)
                perm_corr = np.corrcoef(energies, perm_times)[0, 1]
                perm_correlations.append(perm_corr)
            
            perm_p_value = np.sum(np.abs(perm_correlations) >= abs(correlation)) / n_permutations
            
            analysis_results['permutation_test'] = {
                'p_value': float(perm_p_value),
                'n_permutations': n_permutations,
                'perm_correlations_mean': float(np.mean(perm_correlations)),
                'perm_correlations_std': float(np.std(perm_correlations))
            }
            
            # 3. Bootstrap analysis
            n_bootstrap = 1000
            bootstrap_correlations = []
            for _ in range(n_bootstrap):
                indices = np.random.choice(len(energies), size=len(energies), replace=True)
                boot_energies = energies[indices]
                boot_times = times[indices]
                boot_corr = np.corrcoef(boot_energies, boot_times)[0, 1]
                bootstrap_correlations.append(boot_corr)
            
            bootstrap_mean = np.mean(bootstrap_correlations)
            bootstrap_std = np.std(bootstrap_correlations)
            bootstrap_ci = np.percentile(bootstrap_correlations, [2.5, 97.5])
            
            analysis_results['bootstrap_analysis'] = {
                'mean_correlation': float(bootstrap_mean),
                'std_correlation': float(bootstrap_std),
                'confidence_interval': bootstrap_ci.tolist(),
                'n_bootstrap': n_bootstrap
            }
            
            # 4. RANSAC regression
            from sklearn.linear_model import RANSACRegressor, LinearRegression
            
            X = energies.reshape(-1, 1)
            y = times
            
            ransac = RANSACRegressor(random_state=42)
            ransac.fit(X, y)
            
            inlier_mask = ransac.inlier_mask_
            outlier_mask = ~inlier_mask
            
            n_inliers = np.sum(inlier_mask)
            n_outliers = np.sum(outlier_mask)
            
            if n_inliers > 0:
                inlier_correlation = np.corrcoef(energies[inlier_mask], times[inlier_mask])[0, 1]
            else:
                inlier_correlation = 0
            
            analysis_results['ransac_regression'] = {
                'n_inliers': int(n_inliers),
                'n_outliers': int(n_outliers),
                'inlier_fraction': float(n_inliers / len(energies)),
                'inlier_correlation': float(inlier_correlation),
                'slope': float(ransac.estimator_.coef_[0]) if hasattr(ransac.estimator_, 'coef_') else 0
            }
            
            # 5. Spectral lag analysis
            # Calculate lag in different energy bins
            energy_bins = np.logspace(np.log10(energies.min()), np.log10(energies.max()), 5)
            lag_results = []
            
            for i in range(len(energy_bins)-1):
                mask = (energies >= energy_bins[i]) & (energies < energy_bins[i+1])
                if np.sum(mask) > 10:
                    bin_energies = energies[mask]
                    bin_times = times[mask]
                    bin_corr = np.corrcoef(bin_energies, bin_times)[0, 1]
                    lag_results.append({
                        'energy_center': (energy_bins[i] + energy_bins[i+1]) / 2,
                        'correlation': bin_corr,
                        'n_photons': np.sum(mask)
                    })
            
            analysis_results['spectral_lag_analysis'] = {
                'lag_results': lag_results,
                'n_energy_bins': len(lag_results)
            }
            
            # Overall assessment
            overall_significance = analysis_results['energy_time_correlation']['significance']
            overall_p_value = analysis_results['permutation_test']['p_value']
            
            if overall_significance > 5.0 and overall_p_value < 0.001:
                assessment = 'HIGHLY_SIGNIFICANT'
            elif overall_significance > 3.0 and overall_p_value < 0.01:
                assessment = 'SIGNIFICANT'
            elif overall_significance > 2.0 and overall_p_value < 0.05:
                assessment = 'MARGINALLY_SIGNIFICANT'
            else:
                assessment = 'NOT_SIGNIFICANT'
            
            analysis_results['overall_assessment'] = {
                'significance': float(overall_significance),
                'p_value': float(overall_p_value),
                'assessment': assessment,
                'n_photons': n,
                'energy_range': [float(energies.min()), float(energies.max())],
                'time_range': [float(times.min()), float(times.max())]
            }
            
            print(f"   📊 Correlation: {correlation:.4f}")
            print(f"   📊 Significance: {significance:.2f}σ")
            print(f"   📊 P-value: {perm_p_value:.2e}")
            print(f"   📊 Assessment: {assessment}")
            
            return analysis_results
            
        except Exception as e:
            print(f"   ❌ Error analyzing {grb_info['name']}: {e}")
            return None
    
    def run_batch_analysis(self):
        """Run analysis on all GRB candidates"""
        print("\n🚀 Running batch analysis...")
        
        batch_results = {}
        successful_analyses = 0
        
        for grb_info in self.grb_candidates:
            print(f"\n{'='*50}")
            print(f"Analyzing {grb_info['name']}")
            print(f"{'='*50}")
            
            analysis_result = self.analyze_single_grb(grb_info)
            
            if analysis_result is not None:
                batch_results[grb_info['name']] = {
                    'grb_info': grb_info,
                    'analysis': analysis_result,
                    'status': 'SUCCESS'
                }
                successful_analyses += 1
            else:
                batch_results[grb_info['name']] = {
                    'grb_info': grb_info,
                    'analysis': None,
                    'status': 'FAILED'
                }
        
        self.results['batch_analysis'] = batch_results
        self.results['summary'] = {
            'total_grbs': len(self.grb_candidates),
            'successful_analyses': successful_analyses,
            'failed_analyses': len(self.grb_candidates) - successful_analyses,
            'analysis_date': datetime.now().isoformat()
        }
        
        print(f"\n📊 Batch Analysis Summary:")
        print(f"   📊 Total GRBs: {len(self.grb_candidates)}")
        print(f"   📊 Successful: {successful_analyses}")
        print(f"   📊 Failed: {len(self.grb_candidates) - successful_analyses}")
        
        return successful_analyses > 0
    
    def analyze_results_patterns(self):
        """Analyze patterns in the results"""
        print("\n🔍 Analyzing result patterns...")
        
        successful_results = {k: v for k, v in self.results['batch_analysis'].items() 
                            if v['status'] == 'SUCCESS'}
        
        if len(successful_results) == 0:
            print("   ❌ No successful analyses to analyze")
            return
        
        # Collect statistics
        significances = []
        p_values = []
        correlations = []
        n_photons = []
        assessments = []
        
        for grb_name, result in successful_results.items():
            analysis = result['analysis']
            significances.append(analysis['overall_assessment']['significance'])
            p_values.append(analysis['overall_assessment']['p_value'])
            correlations.append(analysis['energy_time_correlation']['correlation'])
            n_photons.append(analysis['overall_assessment']['n_photons'])
            assessments.append(analysis['overall_assessment']['assessment'])
        
        # Pattern analysis
        pattern_analysis = {
            'n_grbs_analyzed': len(successful_results),
            'significance_stats': {
                'mean': float(np.mean(significances)),
                'std': float(np.std(significances)),
                'min': float(np.min(significances)),
                'max': float(np.max(significances)),
                'median': float(np.median(significances))
            },
            'p_value_stats': {
                'mean': float(np.mean(p_values)),
                'std': float(np.std(p_values)),
                'min': float(np.min(p_values)),
                'max': float(np.max(p_values)),
                'median': float(np.median(p_values))
            },
            'correlation_stats': {
                'mean': float(np.mean(correlations)),
                'std': float(np.std(correlations)),
                'min': float(np.min(correlations)),
                'max': float(np.max(correlations)),
                'median': float(np.median(correlations))
            },
            'assessment_counts': {
                'HIGHLY_SIGNIFICANT': assessments.count('HIGHLY_SIGNIFICANT'),
                'SIGNIFICANT': assessments.count('SIGNIFICANT'),
                'MARGINALLY_SIGNIFICANT': assessments.count('MARGINALLY_SIGNIFICANT'),
                'NOT_SIGNIFICANT': assessments.count('NOT_SIGNIFICANT')
            }
        }
        
        # Find GRBs with significant results
        significant_grbs = []
        for grb_name, result in successful_results.items():
            assessment = result['analysis']['overall_assessment']['assessment']
            if assessment in ['HIGHLY_SIGNIFICANT', 'SIGNIFICANT']:
                significant_grbs.append({
                    'grb_name': grb_name,
                    'significance': result['analysis']['overall_assessment']['significance'],
                    'p_value': result['analysis']['overall_assessment']['p_value'],
                    'correlation': result['analysis']['energy_time_correlation']['correlation'],
                    'assessment': assessment
                })
        
        pattern_analysis['significant_grbs'] = significant_grbs
        
        self.results['pattern_analysis'] = pattern_analysis
        
        print(f"   📊 GRBs analyzed: {pattern_analysis['n_grbs_analyzed']}")
        print(f"   📊 Mean significance: {pattern_analysis['significance_stats']['mean']:.2f}σ")
        print(f"   📊 Significant GRBs: {len(significant_grbs)}")
        print(f"   📊 Assessment breakdown: {pattern_analysis['assessment_counts']}")
        
        if significant_grbs:
            print(f"   📊 Significant GRBs:")
            for grb in significant_grbs:
                print(f"      - {grb['grb_name']}: {grb['significance']:.2f}σ ({grb['assessment']})")
    
    def generate_batch_plots(self):
        """Generate plots for batch analysis results"""
        print("\n🎨 Generating batch analysis plots...")
        
        successful_results = {k: v for k, v in self.results['batch_analysis'].items() 
                            if v['status'] == 'SUCCESS'}
        
        if len(successful_results) == 0:
            print("   ❌ No successful analyses to plot")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Batch GRB Analysis Results', fontsize=16, fontweight='bold')
        
        # Prepare data
        grb_names = list(successful_results.keys())
        significances = [result['analysis']['overall_assessment']['significance'] 
                        for result in successful_results.values()]
        p_values = [result['analysis']['overall_assessment']['p_value'] 
                   for result in successful_results.values()]
        correlations = [result['analysis']['energy_time_correlation']['correlation'] 
                       for result in successful_results.values()]
        n_photons = [result['analysis']['overall_assessment']['n_photons'] 
                    for result in successful_results.values()]
        
        # Plot 1: Significance comparison
        ax1 = axes[0, 0]
        bars = ax1.bar(range(len(grb_names)), significances, color='blue', alpha=0.7)
        ax1.set_xlabel('GRB')
        ax1.set_ylabel('Significance (σ)')
        ax1.set_title('Significance Comparison')
        ax1.set_xticks(range(len(grb_names)))
        ax1.set_xticklabels(grb_names, rotation=45, ha='right')
        ax1.axhline(y=3, color='red', linestyle='--', alpha=0.7, label='3σ threshold')
        ax1.axhline(y=5, color='darkred', linestyle='--', alpha=0.7, label='5σ threshold')
        ax1.legend()
        
        # Add significance values on bars
        for i, (bar, sig) in enumerate(zip(bars, significances)):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{sig:.1f}', ha='center', va='bottom', fontsize=9)
        
        # Plot 2: P-value comparison
        ax2 = axes[0, 1]
        bars = ax2.bar(range(len(grb_names)), p_values, color='green', alpha=0.7)
        ax2.set_xlabel('GRB')
        ax2.set_ylabel('P-value')
        ax2.set_title('P-value Comparison')
        ax2.set_xticks(range(len(grb_names)))
        ax2.set_xticklabels(grb_names, rotation=45, ha='right')
        ax2.set_yscale('log')
        ax2.axhline(y=0.05, color='red', linestyle='--', alpha=0.7, label='p=0.05')
        ax2.axhline(y=0.01, color='darkred', linestyle='--', alpha=0.7, label='p=0.01')
        ax2.legend()
        
        # Plot 3: Correlation vs Photon Count
        ax3 = axes[0, 2]
        scatter = ax3.scatter(n_photons, correlations, s=100, alpha=0.7, c=significances, cmap='viridis')
        ax3.set_xlabel('Photon Count')
        ax3.set_ylabel('Correlation')
        ax3.set_title('Correlation vs Photon Count')
        ax3.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        plt.colorbar(scatter, ax=ax3, label='Significance (σ)')
        
        # Plot 4: Significance distribution
        ax4 = axes[1, 0]
        ax4.hist(significances, bins=10, alpha=0.7, color='purple', edgecolor='black')
        ax4.set_xlabel('Significance (σ)')
        ax4.set_ylabel('Count')
        ax4.set_title('Significance Distribution')
        ax4.axvline(np.mean(significances), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(significances):.2f}σ')
        ax4.legend()
        
        # Plot 5: Assessment breakdown
        ax5 = axes[1, 1]
        assessments = [result['analysis']['overall_assessment']['assessment'] 
                      for result in successful_results.values()]
        assessment_counts = pd.Series(assessments).value_counts()
        colors = ['red', 'orange', 'yellow', 'green']
        bars = ax5.bar(assessment_counts.index, assessment_counts.values, color=colors[:len(assessment_counts)])
        ax5.set_xlabel('Assessment')
        ax5.set_ylabel('Count')
        ax5.set_title('Assessment Breakdown')
        ax5.tick_params(axis='x', rotation=45)
        
        # Plot 6: GRB properties comparison
        ax6 = axes[1, 2]
        redshifts = [result['grb_info']['z'] for result in successful_results.values()]
        scatter = ax6.scatter(redshifts, significances, s=100, alpha=0.7, c=correlations, cmap='coolwarm')
        ax6.set_xlabel('Redshift (z)')
        ax6.set_ylabel('Significance (σ)')
        ax6.set_title('Redshift vs Significance')
        plt.colorbar(scatter, ax=ax6, label='Correlation')
        
        plt.tight_layout()
        plt.savefig('batch_grb_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Batch analysis plots saved: batch_grb_analysis.png")
    
    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        print("\n📝 Generating analysis report...")
        
        successful_results = {k: v for k, v in self.results['batch_analysis'].items() 
                            if v['status'] == 'SUCCESS'}
        
        report = f"""
# Batch GRB Analysis Report

**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total GRBs Analyzed:** {len(self.grb_candidates)}
**Successful Analyses:** {len(successful_results)}

## Executive Summary

This report presents the results of batch analysis of {len(self.grb_candidates)} GRB candidates 
using the same methodology applied to GRB090902B. The analysis includes energy-time correlation 
analysis, permutation tests, bootstrap analysis, RANSAC regression, and spectral lag analysis.

## Key Findings

"""
        
        if 'pattern_analysis' in self.results:
            pattern = self.results['pattern_analysis']
            report += f"""
- **Mean Significance:** {pattern['significance_stats']['mean']:.2f}σ
- **Significant GRBs:** {len(pattern['significant_grbs'])}
- **Assessment Breakdown:** {pattern['assessment_counts']}

## Individual GRB Results

"""
            
            for grb_name, result in successful_results.items():
                analysis = result['analysis']
                assessment = analysis['overall_assessment']
                
                report += f"""
### {grb_name}

- **Significance:** {assessment['significance']:.2f}σ
- **P-value:** {assessment['p_value']:.2e}
- **Correlation:** {analysis['energy_time_correlation']['correlation']:.4f}
- **Photons:** {assessment['n_photons']:,}
- **Assessment:** {assessment['assessment']}

"""
        
        report += f"""
## Recommendations

1. **Focus on Significant GRBs:** Prioritize analysis of GRBs with significance > 3σ
2. **Pattern Analysis:** Look for common properties among significant GRBs
3. **Follow-up Analysis:** Apply more detailed analysis to promising candidates
4. **Literature Comparison:** Compare results with published studies

## Next Steps

1. Analyze patterns in significant GRBs
2. Apply advanced discrimination tests
3. Compare with theoretical predictions
4. Prepare publication-ready results

---
*Report generated by Batch GRB Analyzer*
"""
        
        # Save report
        with open('batch_grb_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("✅ Analysis report saved: batch_grb_analysis_report.md")
    
    def save_results(self):
        """Save batch analysis results"""
        print("\n💾 Saving results...")
        
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
        
        with open('batch_grb_analysis.json', 'w') as f:
            json.dump(results_serializable, f, indent=2)
        
        print("✅ Results saved: batch_grb_analysis.json")
    
    def run_complete_batch_analysis(self):
        """Run complete batch analysis"""
        print("🚀 Starting complete batch GRB analysis...")
        
        if not self.load_grb_list():
            return False
        
        if not self.run_batch_analysis():
            return False
        
        self.analyze_results_patterns()
        self.generate_batch_plots()
        self.generate_analysis_report()
        self.save_results()
        
        print("\n" + "="*70)
        print("🎉 BATCH GRB ANALYSIS COMPLETE!")
        print("="*70)
        
        # Summary
        if 'pattern_analysis' in self.results:
            pattern = self.results['pattern_analysis']
            print(f"📊 Batch Analysis Summary:")
            print(f"   📊 GRBs analyzed: {pattern['n_grbs_analyzed']}")
            print(f"   📊 Mean significance: {pattern['significance_stats']['mean']:.2f}σ")
            print(f"   📊 Significant GRBs: {len(pattern['significant_grbs'])}")
            print(f"   📊 Assessment breakdown: {pattern['assessment_counts']}")
        
        return True

def main():
    """Main function"""
    analyzer = BatchGRBAnalyzer()
    success = analyzer.run_complete_batch_analysis()
    
    if success:
        print("\n✅ Batch GRB analysis completed successfully!")
        print("📊 Check batch_grb_analysis.json for detailed results")
        print("🎨 Check batch_grb_analysis.png for analysis plots")
        print("📝 Check batch_grb_analysis_report.md for comprehensive report")
    else:
        print("\n❌ Batch GRB analysis failed!")

if __name__ == "__main__":
    main()
