#!/usr/bin/env python3
"""
Crea paper completo con autori, ORCID, grafici e tutto
"""

import os
import datetime

def create_complete_paper():
    """Crea paper completo con tutto"""
    
    # Leggi paper base
    with open('QUANTUM_GRAVITY_DISCOVERY_PAPER_COMPLETE.md', 'r', encoding='utf-8') as f:
        paper_content = f.read()
    
    # Aggiungi sezione grafici
    figures_section = """

## 6. Figures

### Figure 1: Energy-Time Correlation
![Energy-Time Correlation](figures/figure1_energy_time_correlation.png)
*Energy vs time correlation for GRB090902B showing the 5.46σ quantum gravity effect.*

### Figure 2: Significance vs Photon Count
![Significance vs Photons](figures/figure2_significance_vs_photons.png)
*Statistical significance as a function of photon count, demonstrating the robustness of the discovery.*

### Figure 3: QG Model Comparison
![QG Models](figures/figure3_qg_models.png)
*Comparison of different quantum gravity models showing the best fit to the data.*

### Figure 4: Validation Test Results
![Validation Tests](figures/figure4_validation_tests.png)
*Comprehensive validation tests confirming the reliability of the quantum gravity detection.*

### Figure 5: Multi-GRB Comparison
![Multi-GRB Comparison](figures/figure5_multi_grb_comparison.png)
*Comparison across multiple GRBs showing the uniqueness of GRB090902B.*

### Figure 6: Spectacular Summary
![Spectacular Summary](figures/figure6_spectacular_summary.png)
*Complete overview of the quantum gravity discovery with all key results.*

"""
    
    # Aggiungi sezione grafici al paper
    complete_paper = paper_content + figures_section
    
    # Salva paper completo
    with open('QUANTUM_GRAVITY_DISCOVERY_PAPER_COMPLETE.md', 'w', encoding='utf-8') as f:
        f.write(complete_paper)
    
    print("✅ Paper completo con grafici creato!")
    
    # Crea HTML
    try:
        import markdown
        from bs4 import BeautifulSoup
        
        # Converti a HTML
        html_content = markdown.markdown(complete_paper)
        
        # Aggiungi stile
        styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Quantum Gravity Discovery - GRB090902B</title>
    <style>
        body {{ 
            font-family: 'Times New Roman', serif; 
            margin: 40px; 
            line-height: 1.6; 
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{ 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db; 
            text-align: center;
            font-size: 2.5em;
        }}
        h2 {{ 
            color: #34495e; 
            border-bottom: 2px solid #ecf0f1; 
            margin-top: 30px;
        }}
        h3 {{ 
            color: #7f8c8d; 
            margin-top: 25px;
        }}
        .authors {{ 
            background: #f8f9fa; 
            padding: 25px; 
            border: 3px solid #007bff; 
            border-radius: 10px; 
            margin: 30px 0;
            text-align: center;
        }}
        .authors h2 {{ 
            color: #007bff; 
            border-bottom: 3px solid #007bff; 
            margin-top: 0;
            font-size: 1.8em;
        }}
        .authors p {{ 
            margin: 12px 0; 
            font-size: 1.2em; 
            font-weight: 500;
        }}
        .authors strong {{ 
            color: #2c3e50; 
            font-weight: 700; 
            font-size: 1.1em;
        }}
        .abstract {{ 
            background: #e8f5e8; 
            padding: 25px; 
            border-left: 5px solid #27ae60; 
            margin: 30px 0;
            font-size: 1.1em;
        }}
        .results {{ 
            background: #fff3cd; 
            padding: 20px; 
            border-left: 5px solid #ffc107; 
            margin: 20px 0;
        }}
        .conclusions {{ 
            background: #d1ecf1; 
            padding: 20px; 
            border-left: 5px solid #17a2b8; 
            margin: 20px 0;
        }}
        img {{ 
            max-width: 100%; 
            height: auto; 
            display: block; 
            margin: 20px auto; 
            border: 2px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .figure-caption {{
            text-align: center; 
            font-style: italic; 
            color: #666; 
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .footer {{
            background: #2c3e50; 
            color: white; 
            padding: 20px; 
            text-align: center; 
            margin-top: 50px;
            border-radius: 8px;
        }}
        .footer p {{
            margin: 5px 0;
            font-size: 1.1em;
        }}
        .footer strong {{
            color: #3498db;
        }}
    </style>
</head>
<body>
{html_content}
<div class="footer">
    <p><strong>RTH Italia - Research & Technology Hub</strong></p>
    <p>Independent Research Laboratory</p>
    <p>Email: info@rthitalia.com | ORCID: 0009-0000-4198-5449</p>
    <p>© 2025 Christian Quintino De Luca. All rights reserved.</p>
</div>
</body>
</html>
"""
        
        with open('QUANTUM_GRAVITY_DISCOVERY_PAPER_COMPLETE.html', 'w', encoding='utf-8') as f:
            f.write(styled_html)
        
        print("✅ Paper HTML completo creato!")
        
    except ImportError:
        print("⚠️  markdown/BeautifulSoup non disponibili, solo Markdown generato")
    
    print("🎉 Paper completo con autori, ORCID e grafici creato!")

if __name__ == "__main__":
    create_complete_paper()

