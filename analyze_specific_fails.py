#!/usr/bin/env python3
"""
Analizza esempi specifici di fail per capire perché i pattern non funzionano
"""

import json
import pathlib
from typing import List, Dict, Any

def analyze_latest_results():
    """Analizza i risultati più recenti per capire gli errori specifici"""

    # Trova l'ultimo test
    deliverables_dir = pathlib.Path('deliverables')
    if not deliverables_dir.exists():
        print("❌ Directory deliverables non trovata")
        return

    mmlu_dirs = [d for d in deliverables_dir.glob('MMLU_*') if d.is_dir()]
    if not mmlu_dirs:
        print("❌ Nessuna directory MMLU trovata")
        return

    latest_dir = max(mmlu_dirs, key=lambda d: d.stat().st_mtime)
    print(f"📊 Analizzo: {latest_dir}")

    # Carica i risultati
    samples_file = latest_dir / 'samples.json'
    if not samples_file.exists():
        print("❌ File samples.json non trovato")
        return

    with open(samples_file, 'r', encoding='utf-8') as f:
        samples = json.load(f)

    print(f"🔍 Totale esempi: {len(samples)}")

    # Analizza i fail
    fails = [s for s in samples if not s.get('ok', False)]
    print(f"❌ Fail totali: {len(fails)}")

    # Categorizza i fail per pattern
    pattern_fails = {
        'identify_conclusion': [],
        'translation': [],
        'truth_table': [],
        'immediate_consequence': [],
        'other': []
    }

    for fail in fails:
        question = fail.get('prompt', '').lower()

        if 'identify the conclusion' in question:
            pattern_fails['identify_conclusion'].append(fail)
        elif any(word in question for word in ['translation', 'translate', 'interpretation']):
            pattern_fails['translation'].append(fail)
        elif 'truth table' in question:
            pattern_fails['truth_table'].append(fail)
        elif 'immediate consequence' in question or 'one-step consequence' in question:
            pattern_fails['immediate_consequence'].append(fail)
        else:
            pattern_fails['other'].append(fail)

    # Mostra statistiche
    print("\n📈 Ripartizione dei fail per pattern:")
    for pattern, fails_list in pattern_fails.items():
        if fails_list:
            print(f"  {pattern}: {len(fails_list)} fail")

    # Mostra alcuni esempi specifici
    print("\n🔍 ESEMPI SPECIFICI DEI FAIL:\n")

    for pattern, fails_list in pattern_fails.items():
        if fails_list and len(fails_list) > 0:
            print(f"🎯 Pattern: {pattern.upper()}")
            print("-" * 50)

            # Mostra i primi 2 esempi per pattern
            for i, fail in enumerate(fails_list[:2]):
                print(f"Esempio {i+1}:")
                question = fail.get('prompt', '')
                options = fail.get('options', [])
                correct_answer = fail.get('correct_answer', 'Unknown')
                predicted = fail.get('predicted_answer', 'None')

                print(f"  Domanda: {question[:100]}...")
                print(f"  Opzioni: {options}")
                print(f"  Corretto: {correct_answer}, Predetto: {predicted}")
                print()

    return pattern_fails

if __name__ == "__main__":
    analyze_latest_results()
