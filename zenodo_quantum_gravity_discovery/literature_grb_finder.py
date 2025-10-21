"""
GRB LITERATURE & ANOMALY SEARCH TOOL
Cerca nella letteratura e sul web GRB con pattern simili a GRB090902B

Trova:
- GRB con spectral lags
- Energy-dependent delays
- Time-energy correlations
- Quantum gravity searches
- Anomalie documentate

Autore: Christian Quintino De Luca
RTH Italia - Research & Technology Hub
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
import re

class GRBLiteratureSearcher:
    """
    Cerca GRB con anomalie simili nella letteratura scientifica
    """
    
    def __init__(self):
        self.results = {
            'spectral_lags': [],
            'qg_searches': [],
            'energy_delays': [],
            'anomalies': [],
            'tev_grbs': [],
            'high_energy': []
        }
        
        # GRB090902B reference properties per similarity matching
        self.reference = {
            'grb': 'GRB090902B',
            'z': 1.822,
            'e_max': 80.8,  # GeV
            'correlation': -0.0863,
            'significance': 5.46,
            'keywords': ['spectral lag', 'energy-dependent', 'time delay', 
                        'high energy', 'quantum gravity', 'dispersion']
        }
    
    def search_arxiv(self, query, max_results=50):
        """
        Cerca su arXiv papers rilevanti
        """
        print(f"\n🔍 Searching arXiv: {query}")
        
        base_url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Parse XML response
                papers = self.parse_arxiv_xml(response.text)
                print(f"   ✅ Found {len(papers)} papers")
                return papers
            else:
                print(f"   ❌ Error: {response.status_code}")
                return []
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def parse_arxiv_xml(self, xml_text):
        """
        Parse arXiv XML response (simple regex-based)
        """
        papers = []
        
        # Extract entries
        entries = re.findall(r'<entry>(.*?)</entry>', xml_text, re.DOTALL)
        
        for entry in entries:
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            title = title_match.group(1).strip() if title_match else ""
            
            # Extract authors
            authors = re.findall(r'<name>(.*?)</name>', entry)
            
            # Extract abstract
            abstract_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            abstract = abstract_match.group(1).strip() if abstract_match else ""
            
            # Extract arXiv ID
            id_match = re.search(r'<id>(.*?)</id>', entry)
            arxiv_id = id_match.group(1) if id_match else ""
            
            # Extract GRB names from title + abstract
            grb_names = self.extract_grb_names(title + " " + abstract)
            
            if grb_names:  # Only keep if mentions GRBs
                papers.append({
                    'title': title.replace('\n', ' '),
                    'authors': authors[:3],  # First 3 authors
                    'abstract': abstract.replace('\n', ' ')[:500],  # First 500 chars
                    'arxiv_id': arxiv_id,
                    'grbs': list(set(grb_names))  # Unique GRB names
                })
        
        return papers
    
    def extract_grb_names(self, text):
        """
        Estrae nomi GRB dal testo
        """
        # Pattern: GRB + 6 digits + optional letter
        pattern = r'GRB\s*(\d{6}[A-Z]?)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        # Format as GRByymmddX
        grb_names = []
        for match in matches:
            # Ensure proper format
            digits = re.sub(r'[^0-9A-Z]', '', match)
            if len(digits) >= 6:
                grb_names.append(f"GRB{digits[:6]}{digits[6:7]}")
        
        return grb_names
    
    def search_spectral_lags(self):
        """
        Cerca papers su spectral lags in GRB
        """
        print("\n" + "="*70)
        print("📚 SEARCHING FOR SPECTRAL LAG STUDIES")
        print("="*70)
        
        queries = [
            'gamma-ray burst spectral lag energy dependent',
            'GRB spectral lag Fermi LAT',
            'gamma-ray burst time delay energy',
            'GRB energy-dependent arrival time'
        ]
        
        all_papers = []
        for query in queries:
            papers = self.search_arxiv(query, max_results=30)
            all_papers.extend(papers)
            time.sleep(3)  # Be nice to arXiv
        
        # Extract unique GRBs
        grbs_found = {}
        for paper in all_papers:
            for grb in paper['grbs']:
                if grb not in grbs_found:
                    grbs_found[grb] = []
                grbs_found[grb].append({
                    'paper': paper['title'],
                    'authors': paper['authors'],
                    'arxiv': paper['arxiv_id']
                })
        
        self.results['spectral_lags'] = grbs_found
        
        print(f"\n✅ Found {len(grbs_found)} GRBs mentioned in spectral lag studies")
        if grbs_found:
            print("\n🎯 Top GRBs with spectral lag studies:")
            for grb, papers in sorted(grbs_found.items(), 
                                     key=lambda x: len(x[1]), 
                                     reverse=True)[:10]:
                print(f"   • {grb}: {len(papers)} papers")
    
    def search_qg_studies(self):
        """
        Cerca papers su quantum gravity in GRB
        """
        print("\n" + "="*70)
        print("🔬 SEARCHING FOR QUANTUM GRAVITY STUDIES")
        print("="*70)
        
        queries = [
            'gamma-ray burst quantum gravity Lorentz invariance',
            'GRB quantum gravity energy dependent speed light',
            'Fermi LAT quantum gravity constraints',
            'GRB Planck scale energy dispersion'
        ]
        
        all_papers = []
        for query in queries:
            papers = self.search_arxiv(query, max_results=30)
            all_papers.extend(papers)
            time.sleep(3)
        
        grbs_found = {}
        for paper in all_papers:
            for grb in paper['grbs']:
                if grb not in grbs_found:
                    grbs_found[grb] = []
                grbs_found[grb].append({
                    'paper': paper['title'],
                    'authors': paper['authors'],
                    'arxiv': paper['arxiv_id']
                })
        
        self.results['qg_searches'] = grbs_found
        
        print(f"\n✅ Found {len(grbs_found)} GRBs in QG studies")
        if grbs_found:
            print("\n🎯 Top GRBs in QG searches:")
            for grb, papers in sorted(grbs_found.items(), 
                                     key=lambda x: len(x[1]), 
                                     reverse=True)[:10]:
                print(f"   • {grb}: {len(papers)} papers")
    
    def search_tev_grbs(self):
        """
        Cerca GRB con rilevazioni TeV
        """
        print("\n" + "="*70)
        print("⚡ SEARCHING FOR TeV GRB DETECTIONS")
        print("="*70)
        
        queries = [
            'gamma-ray burst TeV MAGIC H.E.S.S.',
            'GRB very high energy detection',
            'TeV gamma-ray burst Cherenkov'
        ]
        
        all_papers = []
        for query in queries:
            papers = self.search_arxiv(query, max_results=30)
            all_papers.extend(papers)
            time.sleep(3)
        
        grbs_found = {}
        for paper in all_papers:
            for grb in paper['grbs']:
                if grb not in grbs_found:
                    grbs_found[grb] = []
                grbs_found[grb].append({
                    'paper': paper['title'],
                    'authors': paper['authors'],
                    'arxiv': paper['arxiv_id']
                })
        
        self.results['tev_grbs'] = grbs_found
        
        print(f"\n✅ Found {len(grbs_found)} TeV GRBs")
        if grbs_found:
            print("\n🎯 TeV GRBs found:")
            for grb in sorted(grbs_found.keys()):
                print(f"   • {grb}: {len(grbs_found[grb])} papers")
    
    def search_high_energy_grbs(self):
        """
        Cerca GRB con fotoni ad alta energia
        """
        print("\n" + "="*70)
        print("⚡ SEARCHING FOR HIGH-ENERGY GRBs")
        print("="*70)
        
        queries = [
            'Fermi LAT highest energy photon GRB',
            'gamma-ray burst 100 GeV photon',
            'GRB high energy emission LAT'
        ]
        
        all_papers = []
        for query in queries:
            papers = self.search_arxiv(query, max_results=30)
            all_papers.extend(papers)
            time.sleep(3)
        
        grbs_found = {}
        for paper in all_papers:
            for grb in paper['grbs']:
                if grb not in grbs_found:
                    grbs_found[grb] = []
                grbs_found[grb].append({
                    'paper': paper['title'],
                    'authors': paper['authors'],
                    'arxiv': paper['arxiv_id']
                })
        
        self.results['high_energy'] = grbs_found
        
        print(f"\n✅ Found {len(grbs_found)} high-energy GRBs")
        if grbs_found:
            print("\n🎯 High-energy GRBs:")
            for grb, papers in sorted(grbs_found.items(), 
                                     key=lambda x: len(x[1]), 
                                     reverse=True)[:15]:
                print(f"   • {grb}: {len(papers)} papers")
    
    def search_anomalous_grbs(self):
        """
        Cerca GRB con anomalie documentate
        """
        print("\n" + "="*70)
        print("🚨 SEARCHING FOR ANOMALOUS GRBs")
        print("="*70)
        
        queries = [
            'gamma-ray burst anomalous emission unusual',
            'GRB unexpected behavior peculiar',
            'gamma-ray burst anomaly strange'
        ]
        
        all_papers = []
        for query in queries:
            papers = self.search_arxiv(query, max_results=30)
            all_papers.extend(papers)
            time.sleep(3)
        
        grbs_found = {}
        for paper in all_papers:
            for grb in paper['grbs']:
                if grb not in grbs_found:
                    grbs_found[grb] = []
                grbs_found[grb].append({
                    'paper': paper['title'],
                    'authors': paper['authors'],
                    'arxiv': paper['arxiv_id']
                })
        
        self.results['anomalies'] = grbs_found
        
        print(f"\n✅ Found {len(grbs_found)} GRBs with reported anomalies")
        if grbs_found:
            print("\n🎯 Anomalous GRBs:")
            for grb, papers in sorted(grbs_found.items(), 
                                     key=lambda x: len(x[1]), 
                                     reverse=True)[:10]:
                print(f"   • {grb}: {len(papers)} papers")
    
    def create_priority_list(self):
        """
        Crea lista prioritaria di GRB da testare
        """
        print("\n" + "="*70)
        print("🎯 CREATING PRIORITY LIST OF CANDIDATE GRBs")
        print("="*70)
        
        # Collect all GRBs with scores
        grb_scores = {}
        
        # Score based on mentions in different categories
        for grb in self.results['spectral_lags']:
            if grb not in grb_scores:
                grb_scores[grb] = {'score': 0, 'categories': []}
            grb_scores[grb]['score'] += len(self.results['spectral_lags'][grb]) * 3
            grb_scores[grb]['categories'].append('spectral_lag')
        
        for grb in self.results['qg_searches']:
            if grb not in grb_scores:
                grb_scores[grb] = {'score': 0, 'categories': []}
            grb_scores[grb]['score'] += len(self.results['qg_searches'][grb]) * 5
            grb_scores[grb]['categories'].append('qg_search')
        
        for grb in self.results['tev_grbs']:
            if grb not in grb_scores:
                grb_scores[grb] = {'score': 0, 'categories': []}
            grb_scores[grb]['score'] += len(self.results['tev_grbs'][grb]) * 10
            grb_scores[grb]['categories'].append('tev')
        
        for grb in self.results['high_energy']:
            if grb not in grb_scores:
                grb_scores[grb] = {'score': 0, 'categories': []}
            grb_scores[grb]['score'] += len(self.results['high_energy'][grb]) * 2
            grb_scores[grb]['categories'].append('high_energy')
        
        for grb in self.results['anomalies']:
            if grb not in grb_scores:
                grb_scores[grb] = {'score': 0, 'categories': []}
            grb_scores[grb]['score'] += len(self.results['anomalies'][grb]) * 4
            grb_scores[grb]['categories'].append('anomaly')
        
        # Sort by score
        sorted_grbs = sorted(grb_scores.items(), 
                           key=lambda x: x[1]['score'], 
                           reverse=True)
        
        # Create priority list
        priority_list = []
        
        print("\n📋 TOP 30 PRIORITY GRBs TO TEST:")
        print(f"{'Rank':<6} {'GRB':<15} {'Score':<8} {'Categories':<50}")
        print("-"*80)
        
        for rank, (grb, data) in enumerate(sorted_grbs[:30], 1):
            categories = ', '.join(set(data['categories']))
            
            # Priority level
            if data['score'] >= 15:
                priority = "🔴 CRITICAL"
            elif data['score'] >= 8:
                priority = "🟠 HIGH"
            elif data['score'] >= 4:
                priority = "🟡 MEDIUM"
            else:
                priority = "⚪ LOW"
            
            print(f"{rank:<6} {grb:<15} {data['score']:<8} {categories:<50}")
            
            priority_list.append({
                'rank': rank,
                'grb': grb,
                'score': data['score'],
                'priority': priority,
                'categories': list(set(data['categories'])),
                'n_papers': sum([
                    len(self.results.get(cat, {}).get(grb, [])) 
                    for cat in data['categories']
                ])
            })
        
        return priority_list
    
    def save_results(self, priority_list):
        """
        Salva risultati
        """
        output = {
            'search_date': datetime.now().isoformat(),
            'reference_grb': self.reference,
            'categories_searched': list(self.results.keys()),
            'total_grbs_found': len(set(
                list(self.results['spectral_lags'].keys()) +
                list(self.results['qg_searches'].keys()) +
                list(self.results['tev_grbs'].keys()) +
                list(self.results['high_energy'].keys()) +
                list(self.results['anomalies'].keys())
            )),
            'priority_list': priority_list,
            'detailed_results': {
                'spectral_lags': {k: len(v) for k, v in self.results['spectral_lags'].items()},
                'qg_searches': {k: len(v) for k, v in self.results['qg_searches'].items()},
                'tev_grbs': {k: len(v) for k, v in self.results['tev_grbs'].items()},
                'high_energy': {k: len(v) for k, v in self.results['high_energy'].items()},
                'anomalies': {k: len(v) for k, v in self.results['anomalies'].items()}
            }
        }
        
        # Save JSON
        json_file = f"grb_literature_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Results saved: {json_file}")
        
        # Save CSV priority list
        import csv
        csv_file = f"grb_priority_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='') as f:
            if priority_list:
                writer = csv.DictWriter(f, fieldnames=priority_list[0].keys())
                writer.writeheader()
                writer.writerows(priority_list)
        
        print(f"💾 Priority list saved: {csv_file}")
    
    def run_complete_search(self):
        """
        Esegue ricerca completa
        """
        print("="*70)
        print("🚀 GRB LITERATURE & ANOMALY SEARCH")
        print(f"   Reference: {self.reference['grb']}")
        print(f"   Looking for GRBs with similar properties")
        print("="*70)
        
        # Run all searches
        self.search_spectral_lags()
        self.search_qg_studies()
        self.search_tev_grbs()
        self.search_high_energy_grbs()
        self.search_anomalous_grbs()
        
        # Create priority list
        priority_list = self.create_priority_list()
        
        # Save results
        self.save_results(priority_list)
        
        # Summary
        print("\n" + "="*70)
        print("✅ SEARCH COMPLETE!")
        print("="*70)
        print(f"Total unique GRBs found: {len(set(list(self.results['spectral_lags'].keys()) + list(self.results['qg_searches'].keys()) + list(self.results['tev_grbs'].keys()) + list(self.results['high_energy'].keys()) + list(self.results['anomalies'].keys())))}")
        print(f"Priority candidates: {len(priority_list)}")
        
        print("\n🎯 NEXT STEPS:")
        print("   1. Download Fermi LAT data for top 10-20 priority GRBs")
        print("   2. Run your analysis pipeline on each")
        print("   3. Compare results with GRB090902B")
        print("   4. Look for patterns in positive detections")
        
        return priority_list


def main():
    """
    Main execution
    """
    searcher = GRBLiteratureSearcher()
    priority_list = searcher.run_complete_search()
    
    print("\n" + "="*70)
    print("📚 RECOMMENDED READING:")
    print("="*70)
    print("   • Vasileiou et al. 2015 (PRD) - QG constraints from Fermi LAT")
    print("   • Norris et al. 2000 (ApJ) - Spectral lags in BATSE GRBs")
    print("   • Ukwatta et al. 2012 (MNRAS) - Fermi GRB spectral lags")
    print("   • Zhang & Meszaros 2004 (IJMPA) - GRB physics review")
    print("   • Amelino-Camelia 2013 (LRR) - QG phenomenology")


if __name__ == "__main__":
    main()
