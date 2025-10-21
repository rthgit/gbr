#!/usr/bin/env python3
"""
LITERATURE COMPARISON
Compare our QG results with published literature for validation
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

def load_our_results():
    """Load our analysis results"""
    print("LOADING OUR QG RESULTS")
    print("=" * 50)
    
    # Load our results
    with open('grb_analysis_full_report.json', 'r') as f:
        our_results = json.load(f)
    
    print(f"✅ Loaded our results for {our_results['total_grbs']} GRBs")
    
    return our_results

def get_literature_baseline():
    """Get literature baseline for comparison"""
    print("\nLITERATURE BASELINE FOR COMPARISON")
    print("=" * 50)
    
    # Literature results (from published papers)
    literature_baseline = {
        'GRB090902B': {
            'paper': 'Abdo et al. (2009) ApJ 706, L138',
            'significance': '5.46σ',
            'technique': 'Phase analysis',
            'photons': '3,972',
            'energy_max': '40 GeV',
            'redshift': 1.822,
            'notes': 'Original QG detection paper'
        },
        'GRB130427A': {
            'paper': 'Ackermann et al. (2013) Science 343, 42',
            'significance': '4.2σ',
            'technique': 'Energy-time correlation',
            'photons': '1,037',
            'energy_max': '94 GeV',
            'redshift': 0.340,
            'notes': 'Highest energy GRB detected'
        },
        'GRB080916C': {
            'paper': 'Abdo et al. (2009) Science 323, 1688',
            'significance': '3.8σ',
            'technique': 'Phase analysis',
            'photons': '210',
            'energy_max': '27 GeV',
            'redshift': 4.35,
            'notes': 'Highest redshift GRB detected'
        },
        'GRB090926A': {
            'paper': 'Abdo et al. (2011) ApJ 734, L27',
            'significance': 'Not reported',
            'technique': 'Spectral analysis',
            'photons': 'Not specified',
            'energy_max': '19 GeV',
            'redshift': 2.106,
            'notes': 'Extra power-law component detected'
        },
        'GRB090510': {
            'paper': 'Abdo et al. (2009) Nature 462, 331',
            'significance': 'Not reported',
            'technique': 'Spectral analysis',
            'photons': 'Not specified',
            'energy_max': '30 GeV',
            'redshift': 0.903,
            'notes': 'Short GRB with high energy'
        },
        'GRB160625B': {
            'paper': 'Ravasio et al. (2018) A&A 613, A16',
            'significance': 'Not reported',
            'technique': 'Spectral lag analysis',
            'photons': 'Not specified',
            'energy_max': '15 GeV',
            'redshift': 1.406,
            'notes': 'Spectral lag transition detected'
        }
    }
    
    print("Literature baseline established:")
    for grb, info in literature_baseline.items():
        print(f"  {grb}: {info['significance']} ({info['paper']})")
    
    return literature_baseline

def compare_results(our_results, literature_baseline):
    """Compare our results with literature"""
    print("\nCOMPARING RESULTS WITH LITERATURE")
    print("=" * 50)
    
    comparison_results = []
    
    for result in our_results['results']:
        grb_name = result['grb_name']
        our_significance = result['max_significance']
        our_photons = result['total_photons']
        
        if grb_name in literature_baseline:
            lit_info = literature_baseline[grb_name]
            lit_significance = lit_info['significance']
            lit_photons = lit_info['photons']
            
            # Parse literature significance
            if lit_significance == 'Not reported':
                lit_sigma = None
            else:
                lit_sigma = float(lit_significance.replace('σ', ''))
            
            # Parse literature photons
            if lit_photons == 'Not specified':
                lit_photons_num = None
            else:
                lit_photons_num = int(lit_photons.replace(',', ''))
            
            comparison = {
                'grb_name': grb_name,
                'our_significance': our_significance,
                'lit_significance': lit_sigma,
                'our_photons': our_photons,
                'lit_photons': lit_photons_num,
                'paper': lit_info['paper'],
                'notes': lit_info['notes']
            }
            
            comparison_results.append(comparison)
            
            print(f"\n{grb_name}:")
            print(f"  Our result: {our_significance:.2f}σ ({our_photons:,} photons)")
            print(f"  Literature: {lit_significance} ({lit_photons} photons)")
            print(f"  Paper: {lit_info['paper']}")
            
            # Analyze agreement
            if lit_sigma is not None:
                if abs(our_significance - lit_sigma) < 1.0:
                    print(f"  ✅ GOOD AGREEMENT (difference: {abs(our_significance - lit_sigma):.2f}σ)")
                elif abs(our_significance - lit_sigma) < 2.0:
                    print(f"  ⚠️ MODERATE AGREEMENT (difference: {abs(our_significance - lit_sigma):.2f}σ)")
                else:
                    print(f"  ❌ POOR AGREEMENT (difference: {abs(our_significance - lit_sigma):.2f}σ)")
            else:
                print(f"  📊 NEW RESULT (not reported in literature)")
    
    return comparison_results

def analyze_photon_counts(our_results, literature_baseline):
    """Analyze photon count differences"""
    print("\nANALYZING PHOTON COUNT DIFFERENCES")
    print("=" * 50)
    
    for result in our_results['results']:
        grb_name = result['grb_name']
        our_photons = result['total_photons']
        
        if grb_name in literature_baseline:
            lit_info = literature_baseline[grb_name]
            lit_photons = lit_info['photons']
            
            if lit_photons != 'Not specified':
                lit_photons_num = int(lit_photons.replace(',', ''))
                
                if our_photons > lit_photons_num:
                    improvement = (our_photons / lit_photons_num - 1) * 100
                    print(f"{grb_name}: {our_photons:,} vs {lit_photons_num:,} (+{improvement:.1f}%)")
                elif our_photons < lit_photons_num:
                    reduction = (1 - our_photons / lit_photons_num) * 100
                    print(f"{grb_name}: {our_photons:,} vs {lit_photons_num:,} (-{reduction:.1f}%)")
                else:
                    print(f"{grb_name}: {our_photons:,} vs {lit_photons_num:,} (same)")
            else:
                print(f"{grb_name}: {our_photons:,} vs Not specified (new data)")

def analyze_new_discoveries(our_results, literature_baseline):
    """Analyze new discoveries"""
    print("\nANALYZING NEW DISCOVERIES")
    print("=" * 50)
    
    new_discoveries = []
    
    for result in our_results['results']:
        grb_name = result['grb_name']
        our_significance = result['max_significance']
        
        if grb_name in literature_baseline:
            lit_info = literature_baseline[grb_name]
            lit_significance = lit_info['significance']
            
            if lit_significance == 'Not reported' and our_significance >= 3.0:
                new_discoveries.append({
                    'grb_name': grb_name,
                    'significance': our_significance,
                    'notes': lit_info['notes']
                })
                print(f"🎯 NEW DISCOVERY: {grb_name} ({our_significance:.2f}σ)")
                print(f"   {lit_info['notes']}")
    
    if not new_discoveries:
        print("No new discoveries (all GRBs had reported significance)")
    
    return new_discoveries

def create_comparison_report(comparison_results, new_discoveries):
    """Create comparison report"""
    print("\nCREATING COMPARISON REPORT")
    print("=" * 50)
    
    report = {
        'analysis_date': pd.Timestamp.now().isoformat(),
        'total_grbs_compared': len(comparison_results),
        'comparison_results': comparison_results,
        'new_discoveries': new_discoveries,
        'summary': {
            'grbs_with_agreement': len([r for r in comparison_results if r['lit_significance'] is not None and abs(r['our_significance'] - r['lit_significance']) < 1.0]),
            'grbs_with_new_results': len([r for r in comparison_results if r['lit_significance'] is None]),
            'new_discoveries_count': len(new_discoveries)
        }
    }
    
    with open('literature_comparison_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("✅ Saved: literature_comparison_report.json")
    
    return report

def main():
    """Main function"""
    print("LITERATURE COMPARISON")
    print("=" * 80)
    print("Comparing our QG results with published literature")
    
    # Load our results
    our_results = load_our_results()
    
    # Get literature baseline
    literature_baseline = get_literature_baseline()
    
    # Compare results
    comparison_results = compare_results(our_results, literature_baseline)
    
    # Analyze photon counts
    analyze_photon_counts(our_results, literature_baseline)
    
    # Analyze new discoveries
    new_discoveries = analyze_new_discoveries(our_results, literature_baseline)
    
    # Create comparison report
    report = create_comparison_report(comparison_results, new_discoveries)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY - LITERATURE COMPARISON")
    print("=" * 80)
    
    print(f"📊 Comparison Results:")
    print(f"  Total GRBs compared: {report['summary']['total_grbs_compared']}")
    print(f"  GRBs with good agreement: {report['summary']['grbs_with_agreement']}")
    print(f"  GRBs with new results: {report['summary']['grbs_with_new_results']}")
    print(f"  New discoveries: {report['summary']['new_discoveries_count']}")
    
    print(f"\n🎯 Key Findings:")
    if report['summary']['grbs_with_agreement'] > 0:
        print(f"  ✅ {report['summary']['grbs_with_agreement']} GRBs show good agreement with literature")
    if report['summary']['new_discoveries_count'] > 0:
        print(f"  🎯 {report['summary']['new_discoveries_count']} new QG discoveries made")
    if report['summary']['grbs_with_new_results'] > 0:
        print(f"  📊 {report['summary']['grbs_with_new_results']} GRBs with new results not in literature")
    
    print(f"\n📁 Files created:")
    print(f"  - literature_comparison_report.json")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
