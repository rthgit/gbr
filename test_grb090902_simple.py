#!/usr/bin/env python3
"""
Simple test for GRB090902B analysis
"""

import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt

def test_grb090902():
    """Test GRB090902B analysis"""
    print("🔍 Testing GRB090902B analysis...")
    
    try:
        # Load data
        filename = "L251020161615F357373F52_EV00.fits"
        with fits.open(filename) as hdul:
            events_data = hdul['EVENTS'].data
            
        times = events_data['TIME']
        energies = events_data['ENERGY'] / 1000.0  # Convert to GeV
        zenith = events_data['ZENITH_ANGLE']
        
        # Check available columns
        print(f"Available columns: {events_data.dtype.names}")
        
        # Create dummy azimuth if not available
        if 'AZIMUTH_ANGLE' in events_data.dtype.names:
            azimuth = events_data['AZIMUTH_ANGLE']
        else:
            azimuth = np.random.uniform(0, 360, len(times))
            print("⚠️  AZIMUTH_ANGLE not found, using random values")
        
        print(f"✅ Data loaded successfully")
        print(f"   📊 Total photons: {len(times)}")
        print(f"   📊 Energy range: {energies.min():.3f} - {energies.max():.1f} GeV")
        print(f"   📊 Time range: {times.min():.1f} - {times.max():.1f} s")
        
        # Calculate correlation
        correlation = np.corrcoef(energies, times)[0, 1]
        n = len(energies)
        significance = abs(correlation) * np.sqrt(n - 2) / np.sqrt(1 - correlation**2)
        
        print(f"   📊 Correlation: {correlation:.4f}")
        print(f"   📊 Significance: {significance:.2f}σ")
        
        # Create simple plot
        plt.figure(figsize=(12, 8))
        
        # Plot 1: Energy vs Time
        plt.subplot(2, 2, 1)
        plt.scatter(times, energies, c=energies, cmap='viridis', alpha=0.6, s=20)
        plt.xlabel('Time (s)')
        plt.ylabel('Energy (GeV)')
        plt.yscale('log')
        plt.title('GRB090902B: Energy vs Time')
        plt.colorbar(label='Energy (GeV)')
        
        # Plot 2: Energy distribution
        plt.subplot(2, 2, 2)
        plt.hist(energies, bins=50, alpha=0.7, color='blue', edgecolor='black')
        plt.xlabel('Energy (GeV)')
        plt.ylabel('Counts')
        plt.xscale('log')
        plt.title('Energy Distribution')
        
        # Plot 3: Light curve
        plt.subplot(2, 2, 3)
        time_bins = np.arange(times.min(), times.max() + 10, 10)
        light_curve = np.histogram(times, bins=time_bins)[0]
        bin_centers = (time_bins[:-1] + time_bins[1:]) / 2
        plt.plot(bin_centers, light_curve, 'b-', linewidth=2)
        plt.xlabel('Time (s)')
        plt.ylabel('Counts per 10s')
        plt.title('Light Curve')
        
        # Plot 4: Zenith angle distribution
        plt.subplot(2, 2, 4)
        plt.hist(zenith, bins=30, alpha=0.7, color='green', edgecolor='black')
        plt.xlabel('Zenith Angle (deg)')
        plt.ylabel('Counts')
        plt.title('Zenith Angle Distribution')
        
        plt.tight_layout()
        plt.savefig('grb090902_simple_test.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Simple test completed successfully!")
        print("🎨 Plot saved: grb090902_simple_test.png")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_grb090902()
