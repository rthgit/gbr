#!/usr/bin/env python3
"""
Quick test for GRB090902B analysis - bypasses PowerShell issues
"""

import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import json
from datetime import datetime

def quick_grb090902_test():
    """Quick test for GRB090902B"""
    print("🔍 Quick GRB090902B Test")
    print("="*50)
    
    try:
        # Load GRB090902B data
        filename = "L251020161615F357373F52_EV00.fits"
        print(f"📊 Loading {filename}...")
        
        with fits.open(filename) as hdul:
            events_data = hdul['EVENTS'].data
            
        times = events_data['TIME']
        energies = events_data['ENERGY'] / 1000.0  # Convert to GeV
        zenith = events_data['ZENITH_ANGLE']
        
        # Check available columns
        print(f"📊 Available columns: {list(events_data.dtype.names)}")
        
        # Create dummy azimuth if not available
        if 'AZIMUTH_ANGLE' in events_data.dtype.names:
            azimuth = events_data['AZIMUTH_ANGLE']
        else:
            azimuth = np.random.uniform(0, 360, len(times))
            print("⚠️  AZIMUTH_ANGLE not found, using random values")
        
        print(f"✅ Data loaded successfully")
        print(f"   📊 Total photons: {len(times):,}")
        print(f"   📊 Energy range: {energies.min():.3f} - {energies.max():.1f} GeV")
        print(f"   📊 Time range: {times.min():.1f} - {times.max():.1f} s")
        
        # Calculate basic statistics
        correlation = np.corrcoef(energies, times)[0, 1]
        n = len(energies)
        significance = abs(correlation) * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
        
        print(f"\n📊 GRB090902B Analysis Results:")
        print(f"   📊 Correlation: {correlation:.4f}")
        print(f"   📊 Significance: {significance:.2f}σ")
        print(f"   📊 P-value: {2 * (1 - stats.norm.cdf(significance)):.2e}")
        
        # Energy statistics
        photons_1gev = np.sum(energies >= 1.0)
        photons_10gev = np.sum(energies >= 10.0)
        photons_30gev = np.sum(energies >= 30.0)
        
        print(f"\n📊 Energy Statistics:")
        print(f"   📊 >1 GeV: {photons_1gev} ({100*photons_1gev/n:.1f}%)")
        print(f"   📊 >10 GeV: {photons_10gev} ({100*photons_10gev/n:.1f}%)")
        print(f"   📊 >30 GeV: {photons_30gev} ({100*photons_30gev/n:.1f}%)")
        
        # Create simple diagnostic plot
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Energy vs Time scatter
        plt.subplot(2, 3, 1)
        scatter = plt.scatter(times, energies, c=energies, cmap='viridis', alpha=0.6, s=20)
        plt.xlabel('Time (s)')
        plt.ylabel('Energy (GeV)')
        plt.yscale('log')
        plt.title(f'GRB090902B: Energy vs Time\nCorrelation: {correlation:.4f}')
        plt.colorbar(scatter, label='Energy (GeV)')
        
        # Plot 2: Energy distribution
        plt.subplot(2, 3, 2)
        plt.hist(energies, bins=50, alpha=0.7, color='blue', edgecolor='black')
        plt.xlabel('Energy (GeV)')
        plt.ylabel('Counts')
        plt.xscale('log')
        plt.title('Energy Distribution')
        
        # Plot 3: Light curve
        plt.subplot(2, 3, 3)
        time_bins = np.arange(times.min(), times.max() + 10, 10)
        light_curve = np.histogram(times, bins=time_bins)[0]
        bin_centers = (time_bins[:-1] + time_bins[1:]) / 2
        plt.plot(bin_centers, light_curve, 'b-', linewidth=2)
        plt.xlabel('Time (s)')
        plt.ylabel('Counts per 10s')
        plt.title('Light Curve')
        
        # Plot 4: Zenith angle distribution
        plt.subplot(2, 3, 4)
        plt.hist(zenith, bins=30, alpha=0.7, color='green', edgecolor='black')
        plt.xlabel('Zenith Angle (deg)')
        plt.ylabel('Counts')
        plt.title('Zenith Angle Distribution')
        
        # Plot 5: Correlation by energy bins
        plt.subplot(2, 3, 5)
        energy_bins = np.logspace(np.log10(energies.min()), np.log10(energies.max()), 8)
        bin_correlations = []
        bin_centers = []
        
        for i in range(len(energy_bins)-1):
            mask = (energies >= energy_bins[i]) & (energies < energy_bins[i+1])
            if np.sum(mask) > 20:
                bin_energies = energies[mask]
                bin_times = times[mask]
                bin_corr = np.corrcoef(bin_energies, bin_times)[0, 1]
                bin_correlations.append(bin_corr)
                bin_centers.append((energy_bins[i] + energy_bins[i+1]) / 2)
        
        if bin_correlations:
            plt.plot(bin_centers, bin_correlations, 'ro-', linewidth=2, markersize=8)
            plt.xlabel('Energy (GeV)')
            plt.ylabel('Correlation')
            plt.xscale('log')
            plt.title('Correlation vs Energy')
            plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        # Plot 6: Summary statistics
        plt.subplot(2, 3, 6)
        stats_text = f"""GRB090902B Summary
        
Photons: {len(times):,}
Max Energy: {energies.max():.1f} GeV
Time Span: {times.max()-times.min():.0f} s
Correlation: {correlation:.4f}
Significance: {significance:.2f}σ

Energy Stats:
>1 GeV: {photons_1gev} ({100*photons_1gev/n:.1f}%)
>10 GeV: {photons_10gev} ({100*photons_10gev/n:.1f}%)
>30 GeV: {photons_30gev} ({100*photons_30gev/n:.1f}%)

Status: {'HIGHLY SIGNIFICANT' if significance > 5 else 'SIGNIFICANT' if significance > 3 else 'NOT SIGNIFICANT'}
"""
        plt.text(0.05, 0.95, stats_text, transform=plt.gca().transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        plt.axis('off')
        plt.title('Analysis Summary')
        
        plt.tight_layout()
        plt.savefig('grb090902_quick_test.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save results
        results = {
            'grb_name': 'GRB090902B',
            'analysis_date': datetime.now().isoformat(),
            'n_photons': int(n),
            'energy_range_gev': [float(energies.min()), float(energies.max())],
            'time_range_s': [float(times.min()), float(times.max())],
            'correlation': float(correlation),
            'significance': float(significance),
            'photons_1gev': int(photons_1gev),
            'photons_10gev': int(photons_10gev),
            'photons_30gev': int(photons_30gev),
            'status': 'HIGHLY_SIGNIFICANT' if significance > 5 else 'SIGNIFICANT' if significance > 3 else 'NOT_SIGNIFICANT'
        }
        
        with open('grb090902_quick_test.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Quick test completed successfully!")
        print(f"🎨 Plot saved: grb090902_quick_test.png")
        print(f"📊 Results saved: grb090902_quick_test.json")
        print(f"📊 Status: {results['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    from scipy import stats
    quick_grb090902_test()

