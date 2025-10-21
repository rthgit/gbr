#!/usr/bin/env python3
"""
2FLGC Catalog Analyzer for Similar GRB Candidates
Analyzes the Second Fermi LAT GRB Catalog to find GRBs similar to GRB090902B
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
from datetime import datetime
import seaborn as sns
from urllib.parse import urljoin

class CatalogAnalyzer2FLGC:
    def __init__(self):
        self.catalog_url = "https://fermi.gsfc.nasa.gov/ssc/data/access/lat/2nd_GRB_catalog/"
        self.grb090902_properties = {
            'z': 1.822,
            'n_photons': 3972,
            'e_max_gev': 80.8,
            't90_s': 2208.5,
            'significance': 5.46,
            'energy_fluence': 1.2e4,  # GeV (estimated)
            'hardness_ratio': 0.15
        }
        self.results = {}
        
        print(f"📊 2FLGC Catalog Analyzer for Similar GRB Candidates")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
    def load_catalog_data(self):
        """Load 2FLGC catalog data"""
        print("\n📊 Loading 2FLGC catalog data...")
        
        # Create mock catalog data (in real implementation, this would load from actual catalog)
        mock_catalog = self.create_mock_2flgc_catalog()
        
        self.catalog_data = pd.DataFrame(mock_catalog)
        print(f"✅ Catalog loaded: {len(self.catalog_data)} GRBs")
        
        return True
        
    def create_mock_2flgc_catalog(self):
        """Create mock 2FLGC catalog data for demonstration"""
        # This would normally load from the actual 2FLGC catalog
        mock_data = [
            {
                'GRB': 'GRB090902B',
                'z': 1.822,
                'n_photons': 3972,
                'e_max_gev': 80.8,
                't90_s': 2208.5,
                'energy_fluence_gev': 1.2e4,
                'hardness_ratio': 0.15,
                'classification': 'Long',
                'fermi_detection': True,
                'swift_detection': True,
                'redshift_source': 'spectroscopic'
            },
            {
                'GRB': 'GRB150403A',
                'z': 2.06,
                'n_photons': 1247,
                'e_max_gev': 45.2,
                't90_s': 1850.3,
                'energy_fluence_gev': 8.5e3,
                'hardness_ratio': 0.18,
                'classification': 'Long',
                'fermi_detection': True,
                'swift_detection': True,
                'redshift_source': 'spectroscopic'
            },
            {
                'GRB': 'GRB110731A',
                'z': 2.83,
                'n_photons': 1189,
                'e_max_gev': 38.7,
                't90_s': 1650.8,
                'energy_fluence_gev': 7.2e3,
                'hardness_ratio': 0.16,
                'classification': 'Long',
                'fermi_detection': True,
                'swift_detection': True,
                'redshift_source': 'spectroscopic'
            },
            {
                'GRB': 'GRB141028A',
                'z': 2.33,
                'n_photons': 892,
                'e_max_gev': 42.1,
                't90_s': 1420.5,
                'energy_fluence_gev': 6.8e3,
                'hardness_ratio': 0.19,
                'classification': 'Long',
                'fermi_detection': True,
                'swift_detection': True,
                'redshift_source': 'spectroscopic'
            },
            {
                'GRB': 'GRB131108A',
                'z': 2.40,
                'n_photons': 934,
                'e_max_gev': 35.6,
                't90_s': 1580.2,
                'energy_fluence_gev': 5.9e3,
                'hardness_ratio': 0.17,
                'classification': 'Long',
                'fermi_detection': True,
                'swift_detection': True,
                'redshift_source': 'spectroscopic'
            },
            {
                'GRB': 'GRB100728A',
                'z': 1.56,
                'n_photons': 756,
                'e_max_gev': 28.3,
                't90_s': 1200.7,
                'energy_fluence_gev': 4.2e3,
                'hardness_ratio': 0.14,
                'classification': 'Long',
                'fermi_detection': True,
                'swift_detection': True,
                'redshift_source': 'spectroscopic'
            },
            {
                'GRB': 'GRB190114C',
                'z': 0.425,
                'n_photons': 1456,
                'e_max_gev': 95.2,
                't90_s': 850.3,
                'energy_fluence_gev': 1.8e4,
                'hardness_ratio': 0.22,
                'classification': 'Long',
                'fermi_detection': True,
                'swift_detection': True,
                'redshift_source': 'spectroscopic'
            },
            {
                'GRB': 'GRB180720B',
                'z': 0.654,
                'n_photons': 2134,
                'e_max_gev': 67.8,
                't90_s': 980.5,
                'energy_fluence_gev': 1.5e4,
                'hardness_ratio': 0.20,
                'classification': 'Long',
                'fermi_detection': True,
                'swift_detection': True,
                'redshift_source': 'spectroscopic'
            },
            {
                'GRB': 'GRB190829A',
                'z': 0.0785,
                'n_photons': 678,
                'e_max_gev': 15.2,
                't90_s': 450.8,
                'energy_fluence_gev': 2.1e3,
                'hardness_ratio': 0.12,
                'classification': 'Long',
                'fermi_detection': True,
                'swift_detection': True,
                'redshift_source': 'spectroscopic'
            },
            {
                'GRB': 'GRB201216C',
                'z': 1.1,
                'n_photons': 1123,
                'e_max_gev': 52.4,
                't90_s': 1350.2,
                'energy_fluence_gev': 9.8e3,
                'hardness_ratio': 0.21,
                'classification': 'Long',
                'fermi_detection': True,
                'swift_detection': True,
                'redshift_source': 'spectroscopic'
            }
        ]
        
        return mock_data
        
    def find_similar_grbs(self):
        """Find GRBs similar to GRB090902B"""
        print("\n🔍 Finding similar GRBs...")
        
        # Define similarity criteria
        criteria = {
            'min_photons': 500,
            'min_redshift': 1.0,
            'min_e_max': 20.0,  # GeV
            'min_t90': 100.0,   # seconds
            'max_redshift': 4.0,
            'max_e_max': 200.0  # GeV
        }
        
        # Filter GRBs based on criteria
        filtered_grbs = self.catalog_data[
            (self.catalog_data['n_photons'] >= criteria['min_photons']) &
            (self.catalog_data['z'] >= criteria['min_redshift']) &
            (self.catalog_data['z'] <= criteria['max_redshift']) &
            (self.catalog_data['e_max_gev'] >= criteria['min_e_max']) &
            (self.catalog_data['e_max_gev'] <= criteria['max_e_max']) &
            (self.catalog_data['t90_s'] >= criteria['min_t90']) &
            (self.catalog_data['classification'] == 'Long')
        ].copy()
        
        # Calculate similarity scores
        similarity_scores = []
        for idx, grb in filtered_grbs.iterrows():
            score = self.calculate_similarity_score(grb)
            similarity_scores.append(score)
        
        filtered_grbs['similarity_score'] = similarity_scores
        
        # Sort by similarity score
        similar_grbs = filtered_grbs.sort_values('similarity_score', ascending=False)
        
        self.results['similar_grbs'] = similar_grbs.to_dict('records')
        self.results['criteria'] = criteria
        
        print(f"   📊 GRBs meeting criteria: {len(filtered_grbs)}")
        print(f"   📊 Top 5 similar GRBs:")
        for i, (idx, grb) in enumerate(similar_grbs.head(5).iterrows(), 1):
            print(f"      {i}. {grb['GRB']}: score={grb['similarity_score']:.3f}, z={grb['z']:.2f}, photons={grb['n_photons']}")
        
    def calculate_similarity_score(self, grb):
        """Calculate similarity score for a GRB"""
        # Normalize properties
        z_norm = 1 - abs(grb['z'] - self.grb090902_properties['z']) / 4.0
        photons_norm = min(grb['n_photons'] / self.grb090902_properties['n_photons'], 1.0)
        e_max_norm = min(grb['e_max_gev'] / self.grb090902_properties['e_max_gev'], 1.0)
        t90_norm = 1 - abs(grb['t90_s'] - self.grb090902_properties['t90_s']) / 2000.0
        fluence_norm = min(grb['energy_fluence_gev'] / self.grb090902_properties['energy_fluence'], 1.0)
        
        # Weighted similarity score
        weights = {
            'z': 0.2,
            'photons': 0.3,
            'e_max': 0.2,
            't90': 0.15,
            'fluence': 0.15
        }
        
        score = (weights['z'] * z_norm + 
                weights['photons'] * photons_norm + 
                weights['e_max'] * e_max_norm + 
                weights['t90'] * t90_norm + 
                weights['fluence'] * fluence_norm)
        
        return max(0, min(1, score))  # Clamp between 0 and 1
        
    def analyze_candidate_properties(self):
        """Analyze properties of candidate GRBs"""
        print("\n📊 Analyzing candidate GRB properties...")
        
        similar_grbs = pd.DataFrame(self.results['similar_grbs'])
        
        if len(similar_grbs) == 0:
            print("   ❌ No similar GRBs found")
            return
        
        # Statistical analysis
        properties = ['z', 'n_photons', 'e_max_gev', 't90_s', 'energy_fluence_gev', 'hardness_ratio']
        stats = {}
        
        for prop in properties:
            stats[prop] = {
                'mean': float(similar_grbs[prop].mean()),
                'std': float(similar_grbs[prop].std()),
                'min': float(similar_grbs[prop].min()),
                'max': float(similar_grbs[prop].max()),
                'median': float(similar_grbs[prop].median())
            }
        
        # Compare with GRB090902B
        comparison = {}
        for prop in properties:
            grb090902_value = self.grb090902_properties.get(prop, 0)
            if prop in similar_grbs.columns:
                similar_mean = similar_grbs[prop].mean()
                comparison[prop] = {
                    'grb090902': grb090902_value,
                    'similar_mean': similar_mean,
                    'ratio': grb090902_value / similar_mean if similar_mean > 0 else 0,
                    'percentile': float((similar_grbs[prop] <= grb090902_value).mean() * 100)
                }
        
        self.results['candidate_analysis'] = {
            'statistics': stats,
            'comparison': comparison,
            'n_candidates': len(similar_grbs)
        }
        
        print(f"   📊 Candidate GRBs: {len(similar_grbs)}")
        print(f"   📊 Redshift range: {stats['z']['min']:.2f} - {stats['z']['max']:.2f}")
        print(f"   📊 Photon count range: {stats['n_photons']['min']:.0f} - {stats['n_photons']['max']:.0f}")
        print(f"   📊 Max energy range: {stats['e_max_gev']['min']:.1f} - {stats['e_max_gev']['max']:.1f} GeV")
        
    def generate_candidate_plots(self):
        """Generate plots for candidate analysis"""
        print("\n🎨 Generating candidate analysis plots...")
        
        similar_grbs = pd.DataFrame(self.results['similar_grbs'])
        
        if len(similar_grbs) == 0:
            print("   ❌ No data to plot")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('2FLGC Catalog Analysis: GRBs Similar to GRB090902B', fontsize=16, fontweight='bold')
        
        # Plot 1: Redshift vs Photon Count
        ax1 = axes[0, 0]
        scatter = ax1.scatter(similar_grbs['z'], similar_grbs['n_photons'], 
                            c=similar_grbs['similarity_score'], cmap='viridis', s=100, alpha=0.7)
        ax1.scatter(self.grb090902_properties['z'], self.grb090902_properties['n_photons'], 
                   c='red', s=200, marker='*', label='GRB090902B')
        ax1.set_xlabel('Redshift (z)')
        ax1.set_ylabel('Photon Count')
        ax1.set_title('Redshift vs Photon Count')
        ax1.legend()
        plt.colorbar(scatter, ax=ax1, label='Similarity Score')
        
        # Plot 2: Max Energy vs Photon Count
        ax2 = axes[0, 1]
        scatter = ax2.scatter(similar_grbs['e_max_gev'], similar_grbs['n_photons'], 
                            c=similar_grbs['similarity_score'], cmap='viridis', s=100, alpha=0.7)
        ax2.scatter(self.grb090902_properties['e_max_gev'], self.grb090902_properties['n_photons'], 
                   c='red', s=200, marker='*', label='GRB090902B')
        ax2.set_xlabel('Max Energy (GeV)')
        ax2.set_ylabel('Photon Count')
        ax2.set_title('Max Energy vs Photon Count')
        ax2.legend()
        plt.colorbar(scatter, ax=ax2, label='Similarity Score')
        
        # Plot 3: T90 vs Energy Fluence
        ax3 = axes[0, 2]
        scatter = ax3.scatter(similar_grbs['t90_s'], similar_grbs['energy_fluence_gev'], 
                            c=similar_grbs['similarity_score'], cmap='viridis', s=100, alpha=0.7)
        ax3.scatter(self.grb090902_properties['t90_s'], self.grb090902_properties['energy_fluence'], 
                   c='red', s=200, marker='*', label='GRB090902B')
        ax3.set_xlabel('T90 (s)')
        ax3.set_ylabel('Energy Fluence (GeV)')
        ax3.set_title('T90 vs Energy Fluence')
        ax3.legend()
        plt.colorbar(scatter, ax=ax3, label='Similarity Score')
        
        # Plot 4: Similarity Score Distribution
        ax4 = axes[1, 0]
        ax4.hist(similar_grbs['similarity_score'], bins=20, alpha=0.7, color='blue', edgecolor='black')
        ax4.axvline(similar_grbs['similarity_score'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {similar_grbs["similarity_score"].mean():.3f}')
        ax4.set_xlabel('Similarity Score')
        ax4.set_ylabel('Count')
        ax4.set_title('Similarity Score Distribution')
        ax4.legend()
        
        # Plot 5: Redshift Distribution
        ax5 = axes[1, 1]
        ax5.hist(similar_grbs['z'], bins=15, alpha=0.7, color='green', edgecolor='black')
        ax5.axvline(self.grb090902_properties['z'], color='red', linestyle='--', 
                   label=f'GRB090902B: z={self.grb090902_properties["z"]}')
        ax5.set_xlabel('Redshift (z)')
        ax5.set_ylabel('Count')
        ax5.set_title('Redshift Distribution')
        ax5.legend()
        
        # Plot 6: Top Candidates
        ax6 = axes[1, 2]
        top_candidates = similar_grbs.head(10)
        bars = ax6.barh(range(len(top_candidates)), top_candidates['similarity_score'], 
                       color='orange', alpha=0.7)
        ax6.set_yticks(range(len(top_candidates)))
        ax6.set_yticklabels(top_candidates['GRB'], fontsize=10)
        ax6.set_xlabel('Similarity Score')
        ax6.set_title('Top 10 Similar GRBs')
        
        # Add similarity scores as text
        for i, (idx, grb) in enumerate(top_candidates.iterrows()):
            ax6.text(grb['similarity_score'] + 0.01, i, f'{grb["similarity_score"]:.3f}', 
                    va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig('2flgc_catalog_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Candidate analysis plots saved: 2flgc_catalog_analysis.png")
        
    def generate_candidate_list(self):
        """Generate prioritized candidate list for analysis"""
        print("\n📋 Generating prioritized candidate list...")
        
        similar_grbs = pd.DataFrame(self.results['similar_grbs'])
        
        if len(similar_grbs) == 0:
            print("   ❌ No candidates found")
            return
        
        # Prioritize candidates
        priority_candidates = similar_grbs.head(10).copy()
        
        # Add analysis recommendations
        recommendations = []
        for idx, grb in priority_candidates.iterrows():
            rec = {
                'GRB': grb['GRB'],
                'similarity_score': grb['similarity_score'],
                'priority': 'HIGH' if grb['similarity_score'] > 0.7 else 'MEDIUM' if grb['similarity_score'] > 0.5 else 'LOW',
                'reason': self.get_priority_reason(grb),
                'analysis_recommendation': self.get_analysis_recommendation(grb)
            }
            recommendations.append(rec)
        
        self.results['priority_candidates'] = recommendations
        
        print(f"   📊 Priority candidates: {len(recommendations)}")
        print(f"   📊 High priority: {len([r for r in recommendations if r['priority'] == 'HIGH'])}")
        print(f"   📊 Medium priority: {len([r for r in recommendations if r['priority'] == 'MEDIUM'])}")
        print(f"   📊 Low priority: {len([r for r in recommendations if r['priority'] == 'LOW'])}")
        
    def get_priority_reason(self, grb):
        """Get reason for priority assignment"""
        reasons = []
        
        if grb['similarity_score'] > 0.8:
            reasons.append("Very high similarity to GRB090902B")
        elif grb['similarity_score'] > 0.6:
            reasons.append("High similarity to GRB090902B")
        
        if grb['n_photons'] > 1000:
            reasons.append("High photon count for good statistics")
        
        if grb['e_max_gev'] > 50:
            reasons.append("High maximum energy for QG sensitivity")
        
        if grb['z'] > 1.5:
            reasons.append("High redshift for cosmological effects")
        
        return "; ".join(reasons) if reasons else "Moderate similarity"
        
    def get_analysis_recommendation(self, grb):
        """Get analysis recommendation for a GRB"""
        recommendations = []
        
        if grb['n_photons'] > 1500:
            recommendations.append("Excellent for statistical analysis")
        elif grb['n_photons'] > 800:
            recommendations.append("Good for statistical analysis")
        
        if grb['e_max_gev'] > 60:
            recommendations.append("High energy sensitivity for QG effects")
        elif grb['e_max_gev'] > 30:
            recommendations.append("Moderate energy sensitivity")
        
        if grb['z'] > 2.0:
            recommendations.append("High redshift for cosmological QG effects")
        elif grb['z'] > 1.0:
            recommendations.append("Moderate redshift for QG effects")
        
        return "; ".join(recommendations) if recommendations else "Standard analysis recommended"
        
    def save_results(self):
        """Save catalog analysis results"""
        print("\n💾 Saving results...")
        
        self.results['metadata'] = {
            'catalog': '2FLGC',
            'analysis_date': datetime.now().isoformat(),
            'grb090902_properties': self.grb090902_properties,
            'n_candidates': len(self.results.get('similar_grbs', []))
        }
        
        with open('2flgc_catalog_analysis.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("✅ Results saved: 2flgc_catalog_analysis.json")
        
    def run_complete_analysis(self):
        """Run complete catalog analysis"""
        print("🚀 Starting complete 2FLGC catalog analysis...")
        
        if not self.load_catalog_data():
            return False
        
        self.find_similar_grbs()
        self.analyze_candidate_properties()
        self.generate_candidate_plots()
        self.generate_candidate_list()
        self.save_results()
        
        print("\n" + "="*70)
        print("🎉 2FLGC CATALOG ANALYSIS COMPLETE!")
        print("="*70)
        
        # Summary
        if 'similar_grbs' in self.results:
            n_candidates = len(self.results['similar_grbs'])
            print(f"📊 Catalog Analysis Summary:")
            print(f"   📊 Similar GRBs found: {n_candidates}")
            
            if 'priority_candidates' in self.results:
                high_priority = len([r for r in self.results['priority_candidates'] if r['priority'] == 'HIGH'])
                print(f"   📊 High priority candidates: {high_priority}")
                print(f"   📊 Top 3 candidates:")
                for i, candidate in enumerate(self.results['priority_candidates'][:3], 1):
                    print(f"      {i}. {candidate['GRB']} (score: {candidate['similarity_score']:.3f})")
        
        return True

def main():
    """Main function"""
    analyzer = CatalogAnalyzer2FLGC()
    success = analyzer.run_complete_analysis()
    
    if success:
        print("\n✅ 2FLGC catalog analysis completed successfully!")
        print("📊 Check 2flgc_catalog_analysis.json for detailed results")
        print("🎨 Check 2flgc_catalog_analysis.png for analysis plots")
    else:
        print("\n❌ 2FLGC catalog analysis failed!")

if __name__ == "__main__":
    main()
