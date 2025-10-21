#!/usr/bin/env python3
"""
CRITICAL ANALYSIS OF 2000+ CASES
Systematic verification of numerical values, GRB IDs, and data integrity
Debugging the anomalies identified in the quantum analysis
"""

import os
import json
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt
from datetime import datetime

def load_all_analysis_results():
    """Load all analysis results for critical verification"""
    
    target_dir = r"C:\Users\PC\Desktop\VELOCITA' DELLA LUCE"
    os.chdir(target_dir)
    
    print("CRITICAL ANALYSIS OF 2000+ CASES")
    print("=" * 60)
    print("Systematic verification of numerical values and data integrity...")
    
    # Load all available results
    results = {}
    
    files_to_check = [
        'super_complete_fermi_qg_analysis_results.csv',
        'quantum_deep_pattern_results.csv',
        'infinite_quantum_exploration_results.csv',
        'final_discovery_results.csv',
        'critical_validation_results.csv'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            try:
                df = pd.read_csv(file)
                results[file] = df
                print(f"Loaded: {file} - {len(df)} sources")
            except Exception as e:
                print(f"Error loading {file}: {e}")
        else:
            print(f"Missing: {file}")
    
    return results

def critical_numerical_verification(results):
    """Critical verification of numerical values"""
    
    print("\nCRITICAL NUMERICAL VERIFICATION")
    print("=" * 60)
    
    verification_report = {}
    
    for filename, df in results.items():
        print(f"\nAnalyzing: {filename}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # 1. Check for infinite values
        infinite_cols = []
        for col in df.select_dtypes(include=[np.number]).columns:
            infinite_count = np.isinf(df[col]).sum()
            if infinite_count > 0:
                infinite_cols.append((col, infinite_count))
        
        if infinite_cols:
            print(f"  INFINITE VALUES FOUND:")
            for col, count in infinite_cols:
                print(f"    - {col}: {count} infinite values")
                # Show examples
                inf_values = df[df[col].apply(np.isinf)][col].head(5)
                print(f"      Examples: {inf_values.tolist()}")
        
        # 2. Check for NaN values
        nan_cols = []
        for col in df.select_dtypes(include=[np.number]).columns:
            nan_count = df[col].isna().sum()
            if nan_count > 0:
                nan_cols.append((col, nan_count))
        
        if nan_cols:
            print(f"  NaN VALUES FOUND:")
            for col, count in nan_cols:
                print(f"    - {col}: {count} NaN values")
        
        # 3. Check numerical ranges for key columns
        key_columns = ['energy', 'time', 'correlation', 'significance', 'E_QG']
        for col in key_columns:
            possible_cols = [c for c in df.columns if col.lower() in c.lower()]
            for possible_col in possible_cols:
                if df[possible_col].dtype in ['float64', 'int64']:
                    values = df[possible_col].dropna()
                    if len(values) > 0:
                        finite_values = values[np.isfinite(values)]
                        if len(finite_values) > 0:
                            print(f"  {possible_col} range:")
                            print(f"    Min: {finite_values.min():.6e}")
                            print(f"    Max: {finite_values.max():.6e}")
                            print(f"    Mean: {finite_values.mean():.6e}")
                            
                            # Check for suspicious values
                            if finite_values.max() > 1e20:
                                print(f"    WARNING: Maximum value {finite_values.max():.6e} is suspiciously large!")
                            if finite_values.min() < -1e20:
                                print(f"    WARNING: Minimum value {finite_values.min():.6e} is suspiciously large!")
        
        # 4. Check for exact ratios (like 1.000)
        ratio_cols = [c for c in df.columns if 'ratio' in c.lower()]
        for col in ratio_cols:
            if df[col].dtype in ['float64', 'int64']:
                unique_ratios = df[col].dropna().unique()
                if len(unique_ratios) < 5:  # Very few unique values
                    print(f"  SUSPICIOUS RATIO: {col} has only {len(unique_ratios)} unique values: {unique_ratios}")
        
        verification_report[filename] = {
            'shape': df.shape,
            'infinite_cols': infinite_cols,
            'nan_cols': nan_cols,
            'suspicious_values': []
        }
    
    return verification_report

def verify_grb_identifiers(results):
    """Verify GRB identifiers vs generic names"""
    
    print("\nGRB IDENTIFIER VERIFICATION")
    print("=" * 60)
    
    identifier_report = {}
    
    for filename, df in results.items():
        print(f"\nAnalyzing identifiers in: {filename}")
        
        # Look for identifier columns
        id_columns = [c for c in df.columns if 'id' in c.lower() or 'source' in c.lower() or 'grb' in c.lower()]
        
        for col in id_columns:
            if df[col].dtype == 'object':  # String column
                unique_ids = df[col].unique()
                print(f"  {col}: {len(unique_ids)} unique identifiers")
                
                # Check for real GRB patterns
                grb_patterns = []
                generic_patterns = []
                
                for id_val in unique_ids[:10]:  # Check first 10
                    id_str = str(id_val)
                    if 'GRB' in id_str.upper():
                        grb_patterns.append(id_str)
                    elif 'Quantum_Source' in id_str or 'Source_' in id_str:
                        generic_patterns.append(id_str)
                
                if grb_patterns:
                    print(f"    Real GRB patterns found: {grb_patterns[:5]}")
                if generic_patterns:
                    print(f"    Generic patterns found: {generic_patterns[:5]}")
                
                identifier_report[filename] = {
                    'column': col,
                    'total_unique': len(unique_ids),
                    'grb_patterns': grb_patterns,
                    'generic_patterns': generic_patterns
                }
    
    return identifier_report

def debug_ratio_calculation(results):
    """Debug the ratio calculation that gives exactly 1.000"""
    
    print("\nDEBUG RATIO CALCULATION")
    print("=" * 60)
    
    for filename, df in results.items():
        print(f"\nDebugging ratios in: {filename}")
        
        # Look for ratio columns
        ratio_cols = [c for c in df.columns if 'ratio' in c.lower()]
        
        for col in ratio_cols:
            if df[col].dtype in ['float64', 'int64']:
                values = df[col].dropna()
                if len(values) > 0:
                    print(f"  {col}:")
                    print(f"    Unique values: {len(values.unique())}")
                    print(f"    Value range: {values.min():.6f} to {values.max():.6f}")
                    print(f"    Mean: {values.mean():.6f}")
                    print(f"    Std: {values.std():.6f}")
                    
                    # Check if all values are exactly 1.0
                    if np.allclose(values, 1.0, atol=1e-10):
                        print(f"    WARNING: All values are exactly 1.0!")
                    
                    # Show distribution
                    unique_vals, counts = np.unique(values, return_counts=True)
                    if len(unique_vals) <= 10:
                        print(f"    Distribution: {dict(zip(unique_vals, counts))}")

def compare_with_baseline_8_grbs():
    """Compare with the baseline 8 GRBs for validation"""
    
    print("\nCOMPARISON WITH BASELINE 8 GRBs")
    print("=" * 60)
    
    # Expected ranges from the 8 GRB analysis
    expected_ranges = {
        'energy_max': (5, 99),  # GeV
        'time_range': (0, 10000),  # seconds
        'correlation': (-1, 1),  # Pearson r
        'significance': (0, 10),  # sigma
        'E_QG_estimate': (1e15, 1e19)  # GeV (Planck scale)
    }
    
    print("Expected ranges from 8 GRB baseline:")
    for param, (min_val, max_val) in expected_ranges.items():
        print(f"  {param}: {min_val} to {max_val}")
    
    return expected_ranges

def generate_critical_report(verification_report, identifier_report, expected_ranges):
    """Generate comprehensive critical report"""
    
    print("\nGENERATING CRITICAL REPORT")
    print("=" * 60)
    
    critical_report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'verification_report': verification_report,
        'identifier_report': identifier_report,
        'expected_ranges': expected_ranges,
        'critical_findings': [],
        'recommendations': []
    }
    
    # Analyze findings
    for filename, report in verification_report.items():
        if report['infinite_cols']:
            critical_report['critical_findings'].append({
                'file': filename,
                'issue': 'infinite_values',
                'details': report['infinite_cols']
            })
        
        if report['nan_cols']:
            critical_report['critical_findings'].append({
                'file': filename,
                'issue': 'nan_values',
                'details': report['nan_cols']
            })
    
    # Add recommendations
    if critical_report['critical_findings']:
        critical_report['recommendations'].extend([
            "Fix infinite value calculations",
            "Verify numerical overflow in quantum calculations",
            "Check unit conversions (GeV vs TeV vs eV)",
            "Validate correlation coefficient calculations",
            "Review significance sigma calculations"
        ])
    
    # Save report
    with open('critical_analysis_report.json', 'w') as f:
        json.dump(critical_report, f, indent=2)
    
    return critical_report

def main():
    """Main function"""
    print("CRITICAL ANALYSIS OF 2000+ CASES")
    print("=" * 70)
    print("Systematic verification of numerical values and data integrity...")
    print("Debugging the anomalies identified in the quantum analysis...")
    
    # Load all analysis results
    results = load_all_analysis_results()
    if not results:
        print("No analysis results found!")
        return
    
    # Critical numerical verification
    verification_report = critical_numerical_verification(results)
    
    # Verify GRB identifiers
    identifier_report = verify_grb_identifiers(results)
    
    # Debug ratio calculation
    debug_ratio_calculation(results)
    
    # Compare with baseline
    expected_ranges = compare_with_baseline_8_grbs()
    
    # Generate critical report
    critical_report = generate_critical_report(verification_report, identifier_report, expected_ranges)
    
    print("\n" + "=" * 70)
    print("CRITICAL ANALYSIS COMPLETED")
    print("=" * 70)
    print(f"Files analyzed: {len(results)}")
    print(f"Critical findings: {len(critical_report['critical_findings'])}")
    print(f"Recommendations: {len(critical_report['recommendations'])}")
    
    if critical_report['critical_findings']:
        print(f"\nCRITICAL ISSUES FOUND:")
        for finding in critical_report['critical_findings']:
            print(f"  - {finding['file']}: {finding['issue']}")
    
    print(f"\nFiles created:")
    print(f"  - critical_analysis_report.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
