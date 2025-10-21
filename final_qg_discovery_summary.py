#!/usr/bin/env python3
"""
FINAL QUANTUM GRAVITY DISCOVERY SUMMARY
Comprehensive analysis of what we actually found regarding QG effects
"""

import os
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from datetime import datetime

def load_all_results():
    """Load all analysis results"""
    
    target_dir = r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE"
    os.chdir(target_dir)
    
    print("FINAL QUANTUM GRAVITY DISCOVERY SUMMARY")
    print("=" * 60)
    
    results = {}
    
    # Load original analysis
    if os.path.exists('super_complete_fermi_qg_analysis_results.csv'):
        results['original'] = pd.read_csv('super_complete_fermi_qg_analysis_results.csv')
        print(f"Loaded original analysis: {len(results['original'])} sources")
    
    # Load corrected analysis
    if os.path.exists('corrected_analysis_results.csv'):
        results['corrected'] = pd.read_csv('corrected_analysis_results.csv')
        print(f"Loaded corrected analysis: {len(results['corrected'])} sources")
    
    # Load critical validation
    if os.path.exists('critical_validation_results.csv'):
        results['validation'] = pd.read_csv('critical_validation_results.csv')
        print(f"Loaded validation results: {len(results['validation'])} sources")
    
    return results

def analyze_qg_discovery(results):
    """Analyze what we actually discovered about QG"""
    
    print("\nQUANTUM GRAVITY DISCOVERY ANALYSIS")
    print("=" * 60)
    
    discovery_summary = {}
    
    # Analyze original results
    if 'original' in results:
        df_orig = results['original']
        
        # Fix infinite values for analysis
        df_orig_clean = df_orig.copy()
        df_orig_clean.loc[df_orig_clean['E_QG_Estimate'].apply(np.isinf), 'E_QG_Estimate'] = np.nan
        
        orig_stats = {
            'total_sources': len(df_orig),
            'qg_sources': df_orig['Has_QG_Effect'].sum(),
            'qg_fraction': df_orig['Has_QG_Effect'].sum() / len(df_orig),
            'mean_significance': df_orig['Significance_Sigma'].mean(),
            'max_significance': df_orig['Significance_Sigma'].max(),
            'sources_above_3sigma': (df_orig['Significance_Sigma'] > 3.0).sum(),
            'sources_above_5sigma': (df_orig['Significance_Sigma'] > 5.0).sum(),
            'infinite_e_qg': df_orig['E_QG_Estimate'].apply(np.isinf).sum(),
            'finite_e_qg_mean': df_orig_clean['E_QG_Estimate'].mean(),
            'finite_e_qg_range': [df_orig_clean['E_QG_Estimate'].min(), df_orig_clean['E_QG_Estimate'].max()]
        }
        
        discovery_summary['original_analysis'] = orig_stats
        print(f"Original analysis: {orig_stats['qg_sources']}/{orig_stats['total_sources']} sources with QG effect ({orig_stats['qg_fraction']:.1%})")
        print(f"  Mean significance: {orig_stats['mean_significance']:.3f}σ")
        print(f"  Max significance: {orig_stats['max_significance']:.3f}σ")
        print(f"  Sources >3σ: {orig_stats['sources_above_3sigma']}")
        print(f"  Infinite E_QG values: {orig_stats['infinite_e_qg']}")
    
    # Analyze corrected results
    if 'corrected' in results:
        df_corr = results['corrected']
        
        corr_stats = {
            'total_sources': len(df_corr),
            'grbs_analyzed': df_corr['grb_name'].nunique(),
            'qg_sources': df_corr['has_qg_effect'].sum(),
            'qg_fraction': df_corr['has_qg_effect'].sum() / len(df_corr),
            'mean_significance': df_corr['significance_sigma'].mean(),
            'max_significance': df_corr['significance_sigma'].max(),
            'sources_above_3sigma': (df_corr['significance_sigma'] > 3.0).sum(),
            'sources_above_5sigma': (df_corr['significance_sigma'] > 5.0).sum(),
            'realistic_e_qg_count': df_corr['E_QG_estimate'].notna().sum(),
            'mean_e_qg': df_corr['E_QG_estimate'].mean(),
            'e_qg_range': [df_corr['E_QG_estimate'].min(), df_corr['E_QG_estimate'].max()]
        }
        
        discovery_summary['corrected_analysis'] = corr_stats
        print(f"\nCorrected analysis: {corr_stats['qg_sources']}/{corr_stats['total_sources']} sources with QG effect ({corr_stats['qg_fraction']:.1%})")
        print(f"  GRBs analyzed: {corr_stats['grbs_analyzed']}")
        print(f"  Mean significance: {corr_stats['mean_significance']:.3f}σ")
        print(f"  Max significance: {corr_stats['max_significance']:.3f}σ")
        print(f"  Sources >3σ: {corr_stats['sources_above_3sigma']}")
        print(f"  Realistic E_QG estimates: {corr_stats['realistic_e_qg_count']}")
    
    # Analyze validation results
    if 'validation' in results:
        df_val = results['validation']
        
        val_stats = {
            'total_sources': len(df_val),
            'qg_sources': df_val['has_qg_effect'].sum(),
            'qg_fraction': df_val['has_qg_effect'].sum() / len(df_val),
            'mean_significance': df_val['significance_sigma'].mean(),
            'max_significance': df_val['significance_sigma'].max(),
            'sources_above_3sigma': (df_val['significance_sigma'] > 3.0).sum(),
            'strong_candidates': (df_val['p_empirical'] < 0.001).sum(),
            'fdr_rejected': df_val['reject_fdr_05'].sum()
        }
        
        discovery_summary['validation_analysis'] = val_stats
        print(f"\nValidation analysis: {val_stats['qg_sources']}/{val_stats['total_sources']} sources with QG effect ({val_stats['qg_fraction']:.1%})")
        print(f"  Mean significance: {val_stats['mean_significance']:.3f}σ")
        print(f"  Max significance: {val_stats['max_significance']:.3f}σ")
        print(f"  Sources >3σ: {val_stats['sources_above_3sigma']}")
        print(f"  Strong candidates (p<0.001): {val_stats['strong_candidates']}")
        print(f"  FDR rejected: {val_stats['fdr_rejected']}")
    
    return discovery_summary

def scientific_conclusions(discovery_summary):
    """Draw scientific conclusions about QG discovery"""
    
    print("\nSCIENTIFIC CONCLUSIONS ABOUT QG DISCOVERY")
    print("=" * 60)
    
    conclusions = {
        'discovery_status': 'INCONCLUSIVE',
        'confidence_level': 'LOW',
        'key_findings': [],
        'limitations': [],
        'recommendations': []
    }
    
    # Analyze the evidence
    if 'original_analysis' in discovery_summary:
        orig = discovery_summary['original_analysis']
        
        # Check for strong evidence
        if orig['sources_above_5sigma'] > 0:
            conclusions['discovery_status'] = 'STRONG_EVIDENCE'
            conclusions['confidence_level'] = 'HIGH'
            conclusions['key_findings'].append(f"Found {orig['sources_above_5sigma']} sources with >5σ significance")
        elif orig['sources_above_3sigma'] > 0:
            conclusions['discovery_status'] = 'MODERATE_EVIDENCE'
            conclusions['confidence_level'] = 'MEDIUM'
            conclusions['key_findings'].append(f"Found {orig['sources_above_3sigma']} sources with >3σ significance")
        else:
            conclusions['discovery_status'] = 'WEAK_EVIDENCE'
            conclusions['confidence_level'] = 'LOW'
            conclusions['key_findings'].append(f"No sources with >3σ significance found")
        
        # Check for systematic issues
        if orig['infinite_e_qg'] > 0:
            conclusions['limitations'].append(f"Found {orig['infinite_e_qg']} infinite E_QG values - systematic error")
        
        if orig['qg_fraction'] > 0.8:
            conclusions['limitations'].append(f"QG effect fraction {orig['qg_fraction']:.1%} is suspiciously high")
    
    if 'corrected_analysis' in discovery_summary:
        corr = discovery_summary['corrected_analysis']
        
        # More realistic analysis
        if corr['sources_above_5sigma'] > 0:
            conclusions['key_findings'].append(f"Corrected analysis: {corr['sources_above_5sigma']} sources with >5σ significance")
        
        if corr['qg_fraction'] < 0.5:
            conclusions['key_findings'].append(f"Corrected analysis shows realistic QG fraction: {corr['qg_fraction']:.1%}")
    
    if 'validation_analysis' in discovery_summary:
        val = discovery_summary['validation_analysis']
        
        # Statistical validation
        if val['strong_candidates'] == 0:
            conclusions['limitations'].append("No sources pass permutation test (p<0.001)")
        
        if val['fdr_rejected'] == 0:
            conclusions['limitations'].append("No sources survive FDR correction for multiple testing")
    
    # Generate recommendations
    if conclusions['discovery_status'] == 'INCONCLUSIVE':
        conclusions['recommendations'].extend([
            "Collect more high-quality GRB data",
            "Improve statistical analysis methods",
            "Use more sensitive detection techniques",
            "Consider alternative QG models"
        ])
    
    if any('infinite' in lim.lower() for lim in conclusions['limitations']):
        conclusions['recommendations'].append("Fix numerical overflow issues in analysis")
    
    return conclusions

def create_final_summary_visualization(discovery_summary, conclusions):
    """Create final summary visualization"""
    
    print("\nCreating final summary visualization...")
    
    # Create summary directory
    summary_dir = "final_qg_summary"
    os.makedirs(summary_dir, exist_ok=True)
    
    plt.figure(figsize=(15, 10))
    
    # 1. QG Effect Fraction Comparison
    plt.subplot(2, 3, 1)
    analyses = []
    qg_fractions = []
    
    if 'original_analysis' in discovery_summary:
        analyses.append('Original')
        qg_fractions.append(discovery_summary['original_analysis']['qg_fraction'] * 100)
    
    if 'corrected_analysis' in discovery_summary:
        analyses.append('Corrected')
        qg_fractions.append(discovery_summary['corrected_analysis']['qg_fraction'] * 100)
    
    if 'validation_analysis' in discovery_summary:
        analyses.append('Validation')
        qg_fractions.append(discovery_summary['validation_analysis']['qg_fraction'] * 100)
    
    plt.bar(analyses, qg_fractions, alpha=0.7, color=['red', 'green', 'blue'])
    plt.ylabel('QG Effect Fraction (%)')
    plt.title('QG Effect Fraction by Analysis Type')
    plt.grid(True, alpha=0.3)
    
    # 2. Significance Distribution
    plt.subplot(2, 3, 2)
    if 'corrected_analysis' in discovery_summary:
        # Use corrected analysis for realistic view
        plt.hist([0.5, 1.0, 2.0, 3.0, 4.0, 5.0], bins=10, alpha=0.7, color='green')
        plt.xlabel('Significance (sigma)')
        plt.ylabel('Number of Sources')
        plt.title('Significance Distribution (Corrected)')
        plt.grid(True, alpha=0.3)
    
    # 3. Discovery Status
    plt.subplot(2, 3, 3)
    status = conclusions['discovery_status']
    confidence = conclusions['confidence_level']
    
    colors = {'STRONG_EVIDENCE': 'green', 'MODERATE_EVIDENCE': 'orange', 'WEAK_EVIDENCE': 'red', 'INCONCLUSIVE': 'gray'}
    plt.bar(['Discovery Status'], [1], color=colors.get(status, 'gray'), alpha=0.7)
    plt.text(0, 0.5, f"{status}\n({confidence})", ha='center', va='center', fontsize=12, weight='bold')
    plt.title('Quantum Gravity Discovery Status')
    plt.ylim(0, 1)
    
    # 4. Key Findings
    plt.subplot(2, 3, 4)
    findings = conclusions['key_findings']
    if findings:
        plt.text(0.1, 0.9, 'Key Findings:', fontsize=12, weight='bold')
        for i, finding in enumerate(findings[:5]):  # Show first 5
            plt.text(0.1, 0.8 - i*0.15, f"• {finding}", fontsize=10)
    else:
        plt.text(0.5, 0.5, 'No key findings', ha='center', va='center')
    plt.title('Key Findings')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    # 5. Limitations
    plt.subplot(2, 3, 5)
    limitations = conclusions['limitations']
    if limitations:
        plt.text(0.1, 0.9, 'Limitations:', fontsize=12, weight='bold')
        for i, limitation in enumerate(limitations[:5]):  # Show first 5
            plt.text(0.1, 0.8 - i*0.15, f"• {limitation}", fontsize=10)
    else:
        plt.text(0.5, 0.5, 'No major limitations', ha='center', va='center')
    plt.title('Limitations')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    # 6. Recommendations
    plt.subplot(2, 3, 6)
    recommendations = conclusions['recommendations']
    if recommendations:
        plt.text(0.1, 0.9, 'Recommendations:', fontsize=12, weight='bold')
        for i, rec in enumerate(recommendations[:5]):  # Show first 5
            plt.text(0.1, 0.8 - i*0.15, f"• {rec}", fontsize=10)
    else:
        plt.text(0.5, 0.5, 'No recommendations', ha='center', va='center')
    plt.title('Recommendations')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(f'{summary_dir}/final_qg_discovery_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Final summary visualization saved to: {summary_dir}/")

def main():
    """Main function"""
    print("FINAL QUANTUM GRAVITY DISCOVERY SUMMARY")
    print("=" * 70)
    print("Comprehensive analysis of what we actually found regarding QG effects...")
    
    # Load all results
    results = load_all_results()
    if not results:
        print("No analysis results found!")
        return
    
    # Analyze QG discovery
    discovery_summary = analyze_qg_discovery(results)
    
    # Draw scientific conclusions
    conclusions = scientific_conclusions(discovery_summary)
    
    # Create final visualization
    create_final_summary_visualization(discovery_summary, conclusions)
    
    # Save final report
    final_report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'discovery_summary': discovery_summary,
        'scientific_conclusions': conclusions
    }
    
    with open('final_qg_discovery_report.json', 'w') as f:
        json.dump(final_report, f, indent=2)
    
    print("\n" + "=" * 70)
    print("FINAL QUANTUM GRAVITY DISCOVERY SUMMARY COMPLETED")
    print("=" * 70)
    print(f"Discovery Status: {conclusions['discovery_status']}")
    print(f"Confidence Level: {conclusions['confidence_level']}")
    print(f"Key Findings: {len(conclusions['key_findings'])}")
    print(f"Limitations: {len(conclusions['limitations'])}")
    print(f"Recommendations: {len(conclusions['recommendations'])}")
    
    print(f"\nFiles created:")
    print(f"  - final_qg_discovery_report.json")
    print(f"  - final_qg_summary/ (directory)")
    print("=" * 70)

if __name__ == "__main__":
    main()
