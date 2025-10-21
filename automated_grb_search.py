#!/usr/bin/env python3
"""
AUTOMATED GRB DATA SEARCH
Search multiple sources automatically for GRB data
"""

import webbrowser
import time
import json

def search_arxiv_grb_data():
    """Search arXiv for GRB data"""
    print("SEARCHING ARXIV FOR GRB DATA")
    print("=" * 50)
    
    search_terms = [
        "Fermi GRB 090902B photon list",
        "Fermi GRB 130427A photon data", 
        "Fermi GRB 080916C photon catalog",
        "Fermi LAT GRB supplementary data"
    ]
    
    arxiv_urls = []
    
    for term in search_terms:
        url = f"https://arxiv.org/search/?query={term.replace(' ', '+')}&searchtype=all"
        arxiv_urls.append(url)
        print(f"  Searching: {term}")
        print(f"  URL: {url}")
        time.sleep(1)
    
    return arxiv_urls

def search_vizier_grb_data():
    """Search VizieR for GRB data"""
    print("\nSEARCHING VIZIER FOR GRB DATA")
    print("=" * 50)
    
    vizier_searches = [
        "Fermi GRB 090902B",
        "Fermi GRB 130427A",
        "Fermi GRB 080916C",
        "Fermi LAT photon list"
    ]
    
    vizier_urls = []
    
    for search in vizier_searches:
        url = f"https://vizier.cds.unistra.fr/viz-bin/VizieR?-source={search.replace(' ', '+')}"
        vizier_urls.append(url)
        print(f"  Searching: {search}")
        print(f"  URL: {url}")
        time.sleep(1)
    
    return vizier_urls

def search_fermi_catalog():
    """Search Fermi GRB Catalog"""
    print("\nSEARCHING FERMI GRB CATALOG")
    print("=" * 50)
    
    catalog_urls = [
        "https://fermi.gsfc.nasa.gov/ssc/data/access/lat/2nd_GRB_catalog/",
        "https://fermi.gsfc.nasa.gov/ssc/data/access/lat/3rd_GRB_catalog/",
        "https://fermi.gsfc.nasa.gov/ssc/data/access/lat/GRB_catalog/"
    ]
    
    for url in catalog_urls:
        print(f"  Catalog: {url}")
    
    return catalog_urls

def search_heasarc_archive():
    """Search HEASARC Archive"""
    print("\nSEARCHING HEASARC ARCHIVE")
    print("=" * 50)
    
    heasarc_urls = [
        "https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/w3browse.pl",
        "https://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/",
        "https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/w3browse.pl?mission=Fermi+LAT"
    ]
    
    for url in heasarc_urls:
        print(f"  Archive: {url}")
    
    return heasarc_urls

def main():
    """Main function"""
    print("AUTOMATED GRB DATA SEARCH")
    print("=" * 80)
    print("Searching multiple sources for GRB data...")
    
    # Search arXiv
    arxiv_urls = search_arxiv_grb_data()
    
    # Search VizieR
    vizier_urls = search_vizier_grb_data()
    
    # Search Fermi Catalog
    catalog_urls = search_fermi_catalog()
    
    # Search HEASARC
    heasarc_urls = search_heasarc_archive()
    
    # Save all URLs
    all_urls = {
        'arxiv_urls': arxiv_urls,
        'vizier_urls': vizier_urls,
        'catalog_urls': catalog_urls,
        'heasarc_urls': heasarc_urls
    }
    
    with open('grb_search_urls.json', 'w') as f:
        json.dump(all_urls, f, indent=2)
    
    print(f"\n{'='*80}")
    print("SEARCH COMPLETE!")
    print(f"{'='*80}")
    print("Generated search URLs for:")
    print(f"  - arXiv: {len(arxiv_urls)} searches")
    print(f"  - VizieR: {len(vizier_urls)} searches")
    print(f"  - Fermi Catalog: {len(catalog_urls)} catalogs")
    print(f"  - HEASARC: {len(heasarc_urls)} archives")
    
    print(f"\n📁 Files created:")
    print(f"  - grb_search_urls.json")
    
    print(f"\n🎯 RECOMMENDED ORDER:")
    print(f"  1. Try VizieR first (most likely to succeed)")
    print(f"  2. Try arXiv for supplementary data")
    print(f"  3. Try Fermi GRB Catalog")
    print(f"  4. Try HEASARC archive")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"  1. Open VizieR URLs in browser")
    print(f"  2. Search for 'Fermi GRB 090902B photon list'")
    print(f"  3. Download supplementary data")
    print(f"  4. Extract photon lists")
    print(f"  5. Run analysis with complete data")
    
    # Ask to open URLs
    print(f"\n{'='*80}")
    response = input("Open VizieR search URLs in browser? (y/n): ")
    if response.lower() in ['y', 'yes']:
        print("Opening VizieR URLs...")
        for url in vizier_urls[:2]:  # Open first 2 URLs
            webbrowser.open(url)
            time.sleep(2)
        print("✅ Opened VizieR search URLs")
    
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
