#!/usr/bin/env python3
"""
ALTERNATIVE GRB DATA SOURCES
Multiple ways to find complete GRB datasets when Fermi queries fail
"""

import os
import json
import requests
from datetime import datetime
import webbrowser

def method_1_fermi_catalog():
    """Method 1: Direct Fermi GRB Catalog Download"""
    
    print("METHOD 1: FERMI GRB CATALOG DIRECT DOWNLOAD")
    print("=" * 60)
    
    catalog_urls = {
        '2nd_GRB_Catalog': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/2nd_GRB_catalog/',
        '3rd_GRB_Catalog': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/3rd_GRB_catalog/',
        'LAT_GRB_Catalog': 'https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB_catalog/'
    }
    
    print("Direct download from Fermi GRB Catalogs:")
    for name, url in catalog_urls.items():
        print(f"  {name}: {url}")
    
    print("\nSteps:")
    print("1. Go to catalog page")
    print("2. Download catalog FITS files")
    print("3. Extract GRB data using Fermitools")
    print("4. Convert to analysis format")
    
    return catalog_urls

def method_2_vizier_search():
    """Method 2: VizieR Astronomical Database"""
    
    print("\nMETHOD 2: VIZIER ASTRONOMICAL DATABASE")
    print("=" * 60)
    
    vizier_searches = {
        'Fermi_GRB_Photon_Lists': 'https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJ/706/L138',
        'Fermi_GRB_Catalog': 'https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJS/203/4',
        'GRB_090902B_Data': 'https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJ/706/L138'
    }
    
    print("Search VizieR for published GRB data:")
    for name, url in vizier_searches.items():
        print(f"  {name}: {url}")
    
    print("\nSteps:")
    print("1. Go to VizieR")
    print("2. Search for 'Fermi GRB photon list'")
    print("3. Find Abdo et al. (2009) supplementary data")
    print("4. Download published photon catalogs")
    print("5. Extract GRB data")
    
    return vizier_searches

def method_3_heasarc_archive():
    """Method 3: HEASARC Data Archive"""
    
    print("\nMETHOD 3: HEASARC DATA ARCHIVE")
    print("=" * 60)
    
    heasarc_urls = {
        'Browse_Fermi_LAT': 'https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/w3browse.pl',
        'Fermi_LAT_Archive': 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/',
        'GRB_Search': 'https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/w3browse.pl?mission=Fermi+LAT'
    }
    
    print("Search HEASARC for Fermi GRB data:")
    for name, url in heasarc_urls.items():
        print(f"  {name}: {url}")
    
    print("\nSteps:")
    print("1. Go to HEASARC Browse")
    print("2. Select 'Fermi LAT' mission")
    print("3. Search for GRB observations")
    print("4. Download photon event files")
    print("5. Process with Fermitools")
    
    return heasarc_urls

def method_4_literature_data():
    """Method 4: Literature Supplementary Data"""
    
    print("\nMETHOD 4: LITERATURE SUPPLEMENTARY DATA")
    print("=" * 60)
    
    literature_sources = {
        'arXiv_GRB_Papers': 'https://arxiv.org/search/?query=Fermi+GRB+photon+list&searchtype=all',
        'Abdo_2009_GRB090902B': 'https://arxiv.org/abs/0909.2470',
        'Ackermann_2013_GRB130427A': 'https://arxiv.org/abs/1306.3300',
        'Abdo_2009_GRB080916C': 'https://arxiv.org/abs/0908.1832'
    }
    
    print("Search literature for GRB data:")
    for name, url in literature_sources.items():
        print(f"  {name}: {url}")
    
    print("\nSteps:")
    print("1. Search arXiv for GRB papers")
    print("2. Find papers with supplementary data")
    print("3. Download data files from papers")
    print("4. Extract photon lists")
    print("5. Reconstruct analysis")
    
    return literature_sources

def method_5_github_repositories():
    """Method 5: GitHub Repositories"""
    
    print("\nMETHOD 5: GITHUB REPOSITORIES")
    print("=" * 60)
    
    github_repos = {
        'Fermitools': 'https://github.com/fermi-lat/Fermitools',
        'Fermi_GRB_Analysis': 'https://github.com/search?q=Fermi+GRB+analysis',
        'GRB_Data_Archive': 'https://github.com/search?q=GRB+photon+data',
        'Astronomy_Data': 'https://github.com/search?q=astronomy+data+GRB'
    }
    
    print("Search GitHub for GRB data:")
    for name, url in github_repos.items():
        print(f"  {name}: {url}")
    
    print("\nSteps:")
    print("1. Search GitHub for GRB repositories")
    print("2. Find repositories with GRB data")
    print("3. Download datasets")
    print("4. Extract photon lists")
    print("5. Use for analysis")
    
    return github_repos

def method_6_alternative_observatories():
    """Method 6: Alternative Observatories"""
    
    print("\nMETHOD 6: ALTERNATIVE OBSERVATORIES")
    print("=" * 60)
    
    observatories = {
        'Swift_BAT': 'https://swift.gsfc.nasa.gov/results/batgrbcat/',
        'INTEGRAL': 'https://www.isdc.unige.ch/integral/',
        'HESS': 'https://www.mpi-hd.mpg.de/hfm/HESS/',
        'MAGIC': 'https://magic.mpp.mpg.de/',
        'VERITAS': 'https://veritas.sao.arizona.edu/'
    }
    
    print("Search other observatories for GRB data:")
    for name, url in observatories.items():
        print(f"  {name}: {url}")
    
    print("\nSteps:")
    print("1. Search other observatories")
    print("2. Find GRB observations")
    print("3. Download data")
    print("4. Cross-correlate with Fermi")
    print("5. Use for multi-wavelength analysis")
    
    return observatories

def create_automated_search_script():
    """Create automated search script"""
    
    print("\nMETHOD 7: AUTOMATED SEARCH SCRIPT")
    print("=" * 60)
    
    script_content = '''
#!/usr/bin/env python3
"""
AUTOMATED GRB DATA SEARCH
Search multiple sources automatically for GRB data
"""

import requests
import json
import time
from bs4 import BeautifulSoup

def search_arxiv_grb_data():
    """Search arXiv for GRB data"""
    print("Searching arXiv for GRB data...")
    
    search_terms = [
        "Fermi GRB 090902B photon list",
        "Fermi GRB 130427A photon data", 
        "Fermi GRB 080916C photon catalog",
        "Fermi LAT GRB supplementary data"
    ]
    
    for term in search_terms:
        url = f"https://arxiv.org/search/?query={term.replace(' ', '+')}&searchtype=all"
        print(f"  Searching: {term}")
        print(f"  URL: {url}")
        time.sleep(1)

def search_vizier_grb_data():
    """Search VizieR for GRB data"""
    print("Searching VizieR for GRB data...")
    
    vizier_searches = [
        "Fermi GRB 090902B",
        "Fermi GRB 130427A",
        "Fermi GRB 080916C",
        "Fermi LAT photon list"
    ]
    
    for search in vizier_searches:
        url = f"https://vizier.cds.unistra.fr/viz-bin/VizieR?-source={search.replace(' ', '+')}"
        print(f"  Searching: {search}")
        print(f"  URL: {url}")
        time.sleep(1)

def main():
    """Main function"""
    print("AUTOMATED GRB DATA SEARCH")
    print("=" * 50)
    
    search_arxiv_grb_data()
    search_vizier_grb_data()
    
    print("\\nSearch complete! Check the URLs above.")
    print("Look for supplementary data files in the papers.")

if __name__ == "__main__":
    main()
'''
    
    with open('automated_grb_search.py', 'w') as f:
        f.write(script_content)
    
    print("Created automated search script: automated_grb_search.py")
    print("Run with: python automated_grb_search.py")

def main():
    """Main function"""
    print("ALTERNATIVE GRB DATA SOURCES")
    print("=" * 80)
    print("Multiple ways to find complete GRB datasets...")
    
    # Method 1: Fermi Catalog
    fermi_catalogs = method_1_fermi_catalog()
    
    # Method 2: VizieR
    vizier_sources = method_2_vizier_search()
    
    # Method 3: HEASARC
    heasarc_sources = method_3_heasarc_archive()
    
    # Method 4: Literature
    literature_sources = method_4_literature_data()
    
    # Method 5: GitHub
    github_sources = method_5_github_repositories()
    
    # Method 6: Alternative Observatories
    observatory_sources = method_6_alternative_observatories()
    
    # Method 7: Automated Search
    create_automated_search_script()
    
    # Save all sources
    all_sources = {
        'fermi_catalogs': fermi_catalogs,
        'vizier_sources': vizier_sources,
        'heasarc_sources': heasarc_sources,
        'literature_sources': literature_sources,
        'github_sources': github_sources,
        'observatory_sources': observatory_sources
    }
    
    with open('alternative_grb_sources.json', 'w') as f:
        json.dump(all_sources, f, indent=2)
    
    print(f"\n{'='*80}")
    print("SUMMARY - ALTERNATIVE SOURCES")
    print(f"{'='*80}")
    print("1. ✅ Fermi GRB Catalogs (Direct download)")
    print("2. ✅ VizieR Database (Published data)")
    print("3. ✅ HEASARC Archive (NASA archive)")
    print("4. ✅ Literature Papers (Supplementary data)")
    print("5. ✅ GitHub Repositories (Community data)")
    print("6. ✅ Alternative Observatories (Multi-wavelength)")
    print("7. ✅ Automated Search Script (Created)")
    
    print(f"\n📁 Files created:")
    print(f"  - alternative_grb_sources.json")
    print(f"  - automated_grb_search.py")
    
    print(f"\n🎯 RECOMMENDED ORDER:")
    print(f"  1. Try VizieR first (published data)")
    print(f"  2. Try Fermi GRB Catalog")
    print(f"  3. Try literature papers")
    print(f"  4. Try HEASARC archive")
    print(f"  5. Try GitHub repositories")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"  1. Run: python automated_grb_search.py")
    print(f"  2. Check VizieR for published data")
    print(f"  3. Search arXiv for supplementary files")
    print(f"  4. Try Fermi GRB Catalog direct download")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
