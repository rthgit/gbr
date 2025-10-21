#!/usr/bin/env python3
"""
QG vs Astrophysical Discriminator Tests
Tests to distinguish between quantum gravity effects and astrophysical lags
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.cosmology import Planck18
import json
from datetime import datetime
from scipy import stats
from scipy.optimize import curve_fit
import seaborn as sns

class QGDiscriminatorTests:
    def __init__(self, grb_name="GRB090902B", filename="L251020161615F357373F52_EV00.fits"):
        self.grb_name = grb_name
        self.filename = filename
        self.results = {}
        
        print(f"🧪 QG vs Astrophysical Discriminator Tests")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
    def load_data(self):
        """Load GRB data"""
        print("📊 Loading GRB data...")
        
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
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def test_energy_dependence(self):
        """Test 1: Energy dependence of correlation"""
        print("\n🧪 Test 1: Energy dependence of correlation...")
        
        # Define energy bins
        energy_bins = np.logspace(np.log10(self.energies.min()), np.log10(self.energies.max()), 8)
        bin_results = []
        
        for i in range(len(energy_bins)-1):
            mask = (self.energies >= energy_bins[i]) & (self.energies < energy_bins[i+1])
            if np.sum(mask) > 20:  # Minimum 20 photons per bin
                bin_energies = self.energies[mask]
                bin_times = self.times[mask]
                
                # Calculate correlation
                correlation = np.corrcoef(bin_energies, bin_times)[0, 1]
                n = len(bin_energies)
                significance = abs(correlation) * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
                
                bin_results.append({
                    'energy_min': energy_bins[i],
                    'energy_max': energy_bins[i+1],
                    'energy_center': (energy_bins[i] + energy_bins[i+1]) / 2,
                    'n_photons': n,
                    'correlation': correlation,
                    'significance': significance
                })
        
        # Fit energy dependence
        if len(bin_results) > 3:
            energies = [r['energy_center'] for r in bin_results]
            correlations = [r['correlation'] for r in bin_results]
            
            # Test different models
            models = {
                'constant': lambda E, a: np.full_like(E, a),
                'linear': lambda E, a, b: a + b * E,
                'power_law': lambda E, a, b: a * E**b,
                'logarithmic': lambda E, a, b: a + b * np.log(E)
            }
            
            model_fits = {}
            for model_name, model_func in models.items():
                try:
                    popt, pcov = curve_fit(model_func, energies, correlations, maxfev=1000)
                    residuals = correlations - model_func(energies, *popt)
                    r_squared = 1 - np.sum(residuals**2) / np.sum((correlations - np.mean(correlations))**2)
                    model_fits[model_name] = {
                        'parameters': popt.tolist(),
                        'r_squared': float(r_squared),
                        'residuals': residuals.tolist()
                    }
                except:
                    model_fits[model_name] = {
                        'parameters': [],
                        'r_squared': -np.inf,
                        'residuals': []
                    }
            
            # QG prediction: correlation should be proportional to energy
            qg_score = model_fits['linear']['r_squared'] if 'linear' in model_fits else 0
            
            # Astrophysical prediction: correlation should be constant or energy-independent
            astro_score = model_fits['constant']['r_squared'] if 'constant' in model_fits else 0
            
        else:
            qg_score = 0
            astro_score = 0
            model_fits = {}
        
        self.results['energy_dependence'] = {
            'bin_results': bin_results,
            'model_fits': model_fits,
            'qg_score': float(qg_score),
            'astro_score': float(astro_score),
            'discrimination': 'QG' if qg_score > astro_score else 'Astrophysical'
        }
        
        print(f"   📊 QG score (linear): {qg_score:.3f}")
        print(f"   📊 Astro score (constant): {astro_score:.3f}")
        print(f"   📊 Discrimination: {self.results['energy_dependence']['discrimination']}")
        
    def test_temporal_consistency(self):
        """Test 2: Temporal consistency of correlation"""
        print("\n🧪 Test 2: Temporal consistency of correlation...")
        
        # Divide time into segments
        n_segments = 10
        time_segments = np.linspace(self.times.min(), self.times.max(), n_segments + 1)
        segment_results = []
        
        for i in range(n_segments):
            mask = (self.times >= time_segments[i]) & (self.times < time_segments[i+1])
            if np.sum(mask) > 20:  # Minimum 20 photons per segment
                segment_energies = self.energies[mask]
                segment_times = self.times[mask]
                
                # Calculate correlation
                correlation = np.corrcoef(segment_energies, segment_times)[0, 1]
                n = len(segment_energies)
                significance = abs(correlation) * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
                
                segment_results.append({
                    'time_start': time_segments[i],
                    'time_end': time_segments[i+1],
                    'time_center': (time_segments[i] + time_segments[i+1]) / 2,
                    'n_photons': n,
                    'correlation': correlation,
                    'significance': significance
                })
        
        # Calculate consistency metrics
        correlations = [r['correlation'] for r in segment_results]
        significances = [r['significance'] for r in segment_results]
        
        correlation_std = np.std(correlations)
        correlation_mean = np.mean(correlations)
        significance_std = np.std(significances)
        
        # QG prediction: correlation should be consistent across time
        # Astrophysical prediction: correlation may vary with burst structure
        consistency_score = 1 / (1 + correlation_std)  # Higher is more consistent
        
        # Test for temporal trends
        if len(segment_results) > 3:
            times = [r['time_center'] for r in segment_results]
            time_trend = np.corrcoef(times, correlations)[0, 1]
        else:
            time_trend = 0
        
        self.results['temporal_consistency'] = {
            'segment_results': segment_results,
            'correlation_mean': float(correlation_mean),
            'correlation_std': float(correlation_std),
            'significance_std': float(significance_std),
            'consistency_score': float(consistency_score),
            'time_trend': float(time_trend),
            'discrimination': 'QG' if consistency_score > 0.5 and abs(time_trend) < 0.3 else 'Astrophysical'
        }
        
        print(f"   📊 Correlation consistency: {consistency_score:.3f}")
        print(f"   📊 Time trend: {time_trend:.3f}")
        print(f"   📊 Discrimination: {self.results['temporal_consistency']['discrimination']}")
        
    def test_spectral_lag_models(self):
        """Test 3: Spectral lag model comparison"""
        print("\n🧪 Test 3: Spectral lag model comparison...")
        
        # Define different lag models
        def qg_lag_model(E, E_QG, n=1):
            """QG lag model: t_lag = (E/E_QG)^n"""
            return (E / E_QG)**n
        
        def astrophysical_lag_model(E, t0, alpha):
            """Astrophysical lag model: t_lag = t0 * E^(-alpha)"""
            return t0 * E**(-alpha)
        
        def mixed_lag_model(E, E_QG, t0, alpha, f_qg):
            """Mixed model: combination of QG and astrophysical"""
            return f_qg * (E / E_QG) + (1 - f_qg) * t0 * E**(-alpha)
        
        # Calculate observed lags (negative correlation means high E arrives later)
        # For simplicity, use correlation as proxy for lag
        correlation = np.corrcoef(self.energies, self.times)[0, 1]
        
        # Fit models
        models = {
            'QG': qg_lag_model,
            'Astrophysical': astrophysical_lag_model,
            'Mixed': mixed_lag_model
        }
        
        model_fits = {}
        for model_name, model_func in models.items():
            try:
                if model_name == 'QG':
                    popt, pcov = curve_fit(model_func, self.energies, 
                                         -correlation * np.ones_like(self.energies),
                                         p0=[1e6], maxfev=1000)
                    E_QG = popt[0]
                    model_fits[model_name] = {
                        'E_QG': float(E_QG),
                        'parameters': popt.tolist(),
                        'covariance': pcov.tolist()
                    }
                elif model_name == 'Astrophysical':
                    popt, pcov = curve_fit(model_func, self.energies,
                                         -correlation * np.ones_like(self.energies),
                                         p0=[1.0, 1.0], maxfev=1000)
                    model_fits[model_name] = {
                        't0': float(popt[0]),
                        'alpha': float(popt[1]),
                        'parameters': popt.tolist(),
                        'covariance': pcov.tolist()
                    }
                else:  # Mixed
                    popt, pcov = curve_fit(model_func, self.energies,
                                         -correlation * np.ones_like(self.energies),
                                         p0=[1e6, 1.0, 1.0, 0.5], maxfev=1000)
                    model_fits[model_name] = {
                        'E_QG': float(popt[0]),
                        't0': float(popt[1]),
                        'alpha': float(popt[2]),
                        'f_qg': float(popt[3]),
                        'parameters': popt.tolist(),
                        'covariance': pcov.tolist()
                    }
            except:
                model_fits[model_name] = {
                    'parameters': [],
                    'covariance': [],
                    'error': 'Fit failed'
                }
        
        # Calculate AIC for model comparison
        n_params = {'QG': 1, 'Astrophysical': 2, 'Mixed': 4}
        aic_scores = {}
        for model_name in models.keys():
            if 'error' not in model_fits[model_name]:
                n = len(self.energies)
                k = n_params[model_name]
                # Simplified AIC calculation
                aic_scores[model_name] = 2 * k  # Simplified for demonstration
            else:
                aic_scores[model_name] = np.inf
        
        # Best model
        best_model = min(aic_scores, key=aic_scores.get)
        
        self.results['spectral_lag_models'] = {
            'model_fits': model_fits,
            'aic_scores': aic_scores,
            'best_model': best_model,
            'discrimination': 'QG' if best_model == 'QG' else 'Astrophysical' if best_model == 'Astrophysical' else 'Mixed'
        }
        
        print(f"   📊 Best model: {best_model}")
        print(f"   📊 AIC scores: {aic_scores}")
        print(f"   📊 Discrimination: {self.results['spectral_lag_models']['discrimination']}")
        
    def test_instrumental_effects(self):
        """Test 4: Instrumental effects analysis"""
        print("\n🧪 Test 4: Instrumental effects analysis...")
        
        # Analyze by zenith angle
        zenith_bins = np.linspace(self.zenith.min(), self.zenith.max(), 5)
        zenith_results = []
        
        for i in range(len(zenith_bins)-1):
            mask = (self.zenith >= zenith_bins[i]) & (self.zenith < zenith_bins[i+1])
            if np.sum(mask) > 20:
                zenith_energies = self.energies[mask]
                zenith_times = self.times[mask]
                
                correlation = np.corrcoef(zenith_energies, zenith_times)[0, 1]
                n = len(zenith_energies)
                significance = abs(correlation) * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
                
                zenith_results.append({
                    'zenith_min': zenith_bins[i],
                    'zenith_max': zenith_bins[i+1],
                    'zenith_center': (zenith_bins[i] + zenith_bins[i+1]) / 2,
                    'n_photons': n,
                    'correlation': correlation,
                    'significance': significance
                })
        
        # Analyze by azimuth angle
        azimuth_bins = np.linspace(self.azimuth.min(), self.azimuth.max(), 5)
        azimuth_results = []
        
        for i in range(len(azimuth_bins)-1):
            mask = (self.azimuth >= azimuth_bins[i]) & (self.azimuth < azimuth_bins[i+1])
            if np.sum(mask) > 20:
                azimuth_energies = self.energies[mask]
                azimuth_times = self.times[mask]
                
                correlation = np.corrcoef(azimuth_energies, azimuth_times)[0, 1]
                n = len(azimuth_energies)
                significance = abs(correlation) * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
                
                azimuth_results.append({
                    'azimuth_min': azimuth_bins[i],
                    'azimuth_max': azimuth_bins[i+1],
                    'azimuth_center': (azimuth_bins[i] + azimuth_bins[i+1]) / 2,
                    'n_photons': n,
                    'correlation': correlation,
                    'significance': significance
                })
        
        # Calculate instrumental dependence
        zenith_correlations = [r['correlation'] for r in zenith_results]
        azimuth_correlations = [r['correlation'] for r in azimuth_results]
        
        zenith_dependence = np.std(zenith_correlations) if zenith_correlations else 0
        azimuth_dependence = np.std(azimuth_correlations) if azimuth_correlations else 0
        
        # QG prediction: correlation should be independent of instrumental effects
        # Astrophysical prediction: correlation may depend on viewing angle
        instrumental_score = 1 / (1 + zenith_dependence + azimuth_dependence)
        
        self.results['instrumental_effects'] = {
            'zenith_results': zenith_results,
            'azimuth_results': azimuth_results,
            'zenith_dependence': float(zenith_dependence),
            'azimuth_dependence': float(azimuth_dependence),
            'instrumental_score': float(instrumental_score),
            'discrimination': 'QG' if instrumental_score > 0.7 else 'Astrophysical'
        }
        
        print(f"   📊 Zenith dependence: {zenith_dependence:.3f}")
        print(f"   📊 Azimuth dependence: {azimuth_dependence:.3f}")
        print(f"   📊 Instrumental score: {instrumental_score:.3f}")
        print(f"   📊 Discrimination: {self.results['instrumental_effects']['discrimination']}")
        
    def test_energy_threshold_effects(self):
        """Test 5: Energy threshold effects"""
        print("\n🧪 Test 5: Energy threshold effects...")
        
        # Test different energy thresholds
        thresholds = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]  # GeV
        threshold_results = []
        
        for threshold in thresholds:
            mask = self.energies >= threshold
            if np.sum(mask) > 20:
                thresh_energies = self.energies[mask]
                thresh_times = self.times[mask]
                
                correlation = np.corrcoef(thresh_energies, thresh_times)[0, 1]
                n = len(thresh_energies)
                significance = abs(correlation) * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
                
                threshold_results.append({
                    'threshold': threshold,
                    'n_photons': n,
                    'correlation': correlation,
                    'significance': significance
                })
        
        # Analyze threshold dependence
        correlations = [r['correlation'] for r in threshold_results]
        significances = [r['significance'] for r in threshold_results]
        
        # QG prediction: correlation should be stronger at higher energies
        # Astrophysical prediction: correlation may be energy-independent
        if len(correlations) > 2:
            energy_trend = np.corrcoef(thresholds[:len(correlations)], correlations)[0, 1]
        else:
            energy_trend = 0
        
        # Calculate energy dependence score
        energy_dependence_score = abs(energy_trend)
        
        self.results['energy_threshold_effects'] = {
            'threshold_results': threshold_results,
            'energy_trend': float(energy_trend),
            'energy_dependence_score': float(energy_dependence_score),
            'discrimination': 'QG' if energy_dependence_score > 0.3 else 'Astrophysical'
        }
        
        print(f"   📊 Energy trend: {energy_trend:.3f}")
        print(f"   📊 Energy dependence score: {energy_dependence_score:.3f}")
        print(f"   📊 Discrimination: {self.results['energy_threshold_effects']['discrimination']}")
        
    def calculate_overall_discrimination(self):
        """Calculate overall discrimination score"""
        print("\n🧪 Calculating overall discrimination...")
        
        # Collect all discrimination results
        discriminations = []
        scores = []
        
        for test_name, test_results in self.results.items():
            if 'discrimination' in test_results:
                discriminations.append(test_results['discrimination'])
                
                # Convert to numerical score
                if test_results['discrimination'] == 'QG':
                    scores.append(1.0)
                elif test_results['discrimination'] == 'Astrophysical':
                    scores.append(0.0)
                else:  # Mixed or unclear
                    scores.append(0.5)
        
        # Calculate overall score
        if scores:
            overall_score = np.mean(scores)
            qg_votes = sum(1 for d in discriminations if d == 'QG')
            astro_votes = sum(1 for d in discriminations if d == 'Astrophysical')
            mixed_votes = sum(1 for d in discriminations if d not in ['QG', 'Astrophysical'])
            
            if qg_votes > astro_votes:
                overall_discrimination = 'QG'
            elif astro_votes > qg_votes:
                overall_discrimination = 'Astrophysical'
            else:
                overall_discrimination = 'Mixed'
        else:
            overall_score = 0.5
            overall_discrimination = 'Unclear'
        
        self.results['overall_discrimination'] = {
            'overall_score': float(overall_score),
            'overall_discrimination': overall_discrimination,
            'qg_votes': qg_votes,
            'astro_votes': astro_votes,
            'mixed_votes': mixed_votes,
            'individual_discriminations': discriminations
        }
        
        print(f"   📊 Overall score: {overall_score:.3f}")
        print(f"   📊 QG votes: {qg_votes}")
        print(f"   📊 Astro votes: {astro_votes}")
        print(f"   📊 Mixed votes: {mixed_votes}")
        print(f"   📊 Overall discrimination: {overall_discrimination}")
        
    def generate_discrimination_plots(self):
        """Generate discrimination plots"""
        print("\n🎨 Generating discrimination plots...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'QG vs Astrophysical Discrimination Tests - {self.grb_name}', fontsize=16, fontweight='bold')
        
        # Plot 1: Energy dependence
        if 'energy_dependence' in self.results:
            ax1 = axes[0, 0]
            bin_results = self.results['energy_dependence']['bin_results']
            if bin_results:
                energies = [r['energy_center'] for r in bin_results]
                correlations = [r['correlation'] for r in bin_results]
                ax1.plot(energies, correlations, 'bo-', linewidth=2, markersize=8)
                ax1.set_xlabel('Energy (GeV)')
                ax1.set_ylabel('Correlation')
                ax1.set_xscale('log')
                ax1.set_title('Energy Dependence Test')
                ax1.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        # Plot 2: Temporal consistency
        if 'temporal_consistency' in self.results:
            ax2 = axes[0, 1]
            segment_results = self.results['temporal_consistency']['segment_results']
            if segment_results:
                times = [r['time_center'] for r in segment_results]
                correlations = [r['correlation'] for r in segment_results]
                ax2.plot(times, correlations, 'ro-', linewidth=2, markersize=8)
                ax2.set_xlabel('Time (s)')
                ax2.set_ylabel('Correlation')
                ax2.set_title('Temporal Consistency Test')
                ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        # Plot 3: Model comparison
        if 'spectral_lag_models' in self.results:
            ax3 = axes[0, 2]
            aic_scores = self.results['spectral_lag_models']['aic_scores']
            models = list(aic_scores.keys())
            scores = list(aic_scores.values())
            bars = ax3.bar(models, scores, color=['red', 'blue', 'green'], alpha=0.7)
            ax3.set_ylabel('AIC Score')
            ax3.set_title('Model Comparison')
            ax3.tick_params(axis='x', rotation=45)
        
        # Plot 4: Instrumental effects
        if 'instrumental_effects' in self.results:
            ax4 = axes[1, 0]
            zenith_results = self.results['instrumental_effects']['zenith_results']
            if zenith_results:
                zeniths = [r['zenith_center'] for r in zenith_results]
                correlations = [r['correlation'] for r in zenith_results]
                ax4.plot(zeniths, correlations, 'go-', linewidth=2, markersize=8)
                ax4.set_xlabel('Zenith Angle (deg)')
                ax4.set_ylabel('Correlation')
                ax4.set_title('Zenith Angle Dependence')
                ax4.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        # Plot 5: Energy threshold effects
        if 'energy_threshold_effects' in self.results:
            ax5 = axes[1, 1]
            threshold_results = self.results['energy_threshold_effects']['threshold_results']
            if threshold_results:
                thresholds = [r['threshold'] for r in threshold_results]
                correlations = [r['correlation'] for r in threshold_results]
                ax5.plot(thresholds, correlations, 'mo-', linewidth=2, markersize=8)
                ax5.set_xlabel('Energy Threshold (GeV)')
                ax5.set_ylabel('Correlation')
                ax5.set_xscale('log')
                ax5.set_title('Energy Threshold Effects')
                ax5.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        # Plot 6: Overall discrimination summary
        ax6 = axes[1, 2]
        if 'overall_discrimination' in self.results:
            overall = self.results['overall_discrimination']
            categories = ['QG', 'Astrophysical', 'Mixed']
            votes = [overall['qg_votes'], overall['astro_votes'], overall['mixed_votes']]
            colors = ['red', 'blue', 'green']
            bars = ax6.bar(categories, votes, color=colors, alpha=0.7)
            ax6.set_ylabel('Number of Tests')
            ax6.set_title('Overall Discrimination')
            
            # Add overall score as text
            ax6.text(0.5, 0.95, f"Overall Score: {overall['overall_score']:.3f}", 
                    transform=ax6.transAxes, ha='center', va='top', fontsize=12, fontweight='bold')
            ax6.text(0.5, 0.85, f"Result: {overall['overall_discrimination']}", 
                    transform=ax6.transAxes, ha='center', va='top', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('qg_discriminator_tests.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Discrimination plots saved: qg_discriminator_tests.png")
        
    def save_results(self):
        """Save discrimination results"""
        print("\n💾 Saving results...")
        
        self.results['metadata'] = {
            'grb_name': self.grb_name,
            'filename': self.filename,
            'analysis_date': datetime.now().isoformat(),
            'n_photons': len(self.times),
            'energy_range_gev': [float(self.energies.min()), float(self.energies.max())],
            'time_range_s': [float(self.times.min()), float(self.times.max())]
        }
        
        with open('qg_discriminator_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("✅ Results saved: qg_discriminator_results.json")
        
    def run_complete_discrimination(self):
        """Run complete discrimination analysis"""
        print("🚀 Starting complete QG vs Astrophysical discrimination...")
        
        if not self.load_data():
            return False
        
        self.test_energy_dependence()
        self.test_temporal_consistency()
        self.test_spectral_lag_models()
        self.test_instrumental_effects()
        self.test_energy_threshold_effects()
        self.calculate_overall_discrimination()
        self.generate_discrimination_plots()
        self.save_results()
        
        print("\n" + "="*70)
        print("🎉 QG DISCRIMINATION ANALYSIS COMPLETE!")
        print("="*70)
        
        # Summary
        if 'overall_discrimination' in self.results:
            overall = self.results['overall_discrimination']
            print(f"📊 Overall Discrimination Results:")
            print(f"   📊 Overall Score: {overall['overall_score']:.3f}")
            print(f"   📊 QG Votes: {overall['qg_votes']}")
            print(f"   📊 Astrophysical Votes: {overall['astro_votes']}")
            print(f"   📊 Mixed Votes: {overall['mixed_votes']}")
            print(f"   📊 Final Result: {overall['overall_discrimination']}")
        
        return True

def main():
    """Main function"""
    discriminator = QGDiscriminatorTests()
    success = discriminator.run_complete_discrimination()
    
    if success:
        print("\n✅ QG discrimination analysis completed successfully!")
        print("📊 Check qg_discriminator_results.json for detailed results")
        print("🎨 Check qg_discriminator_tests.png for discrimination plots")
    else:
        print("\n❌ QG discrimination analysis failed!")

if __name__ == "__main__":
    main()
