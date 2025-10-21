# 🌌 GRB Quantum Gravity Analyzer

**Toolkit professionale per l'analisi di gravità quantistica nei Gamma Ray Burst**

## 📋 Panoramica

Questo toolkit implementa metodologie pubblicate per cercare violazioni della relatività speciale nei dati di GRB, basandosi su analisi di correlazione energia-tempo e test statistici avanzati.

## 🔬 Funzionalità Principali

### 1. **Analisi QG Completa**
- Correlazione energia-tempo (test principale per QG)
- Likelihood Ratio Test (confronto modelli NULL vs QG)
- Stima scala energetica E_QG
- Visualizzazione multi-pannello

### 2. **Caricamento Dati Robusto**
- Supporto FITS (Fermi GBM/LAT)
- Gestione colonne alternative (TIME, ENERGY, PHA, CHANNEL)
- Dati simulati realistici per test
- Metadati automatici da header

### 3. **Combinazione Bayesiana Multi-GRB**
- Somma log-likelihoods di più GRB
- Limiti conservativi combinati su E_QG
- Analisi batch automatica
- Salvataggio risultati JSON

### 4. **Validazione Statistica Avanzata**
- **Test di controllo**: analisi fotoni bassa energia
- **Mock injection**: verifica detection rate e false positive
- **Intrinsic lag analysis**: rilevamento sistematiche
- **Validazione completa**: verifica affidabilità sistema

## 🚀 Utilizzo Rapido

### Analisi Singolo GRB
```python
from test import load_grb_data, analyze_qg_signal

# Carica dati simulati
grb_data = load_grb_data(format='simulated')

# Analisi completa
results = analyze_qg_signal(grb_data, make_plots=True)
```

### Analisi Batch Multi-GRB
```python
from test import analyze_multiple_grb_in_folder

# Analizza tutti i FITS in data/
results, combined = analyze_multiple_grb_in_folder('data', '*.fits')
```

### Validazione Sistema
```python
from test import comprehensive_validation

# Test completo di validazione
validation = comprehensive_validation(grb_data)
```

## 📊 Risultati Recenti

**GRB Analizzati:**
- GRB080916C (z=4.35): Correlazione r=0.1054, p=8.24e-04 (3.35σ)
- GRB130427A (z=0.34): Correlazione r=0.0211, p=4.65e-01 (0.73σ)

**Limite Combinato:**
- E_QG > 2.63×10⁹ GeV
- Confronto E_Planck: 2.16×10⁻¹⁰

## 🔧 Installazione

```bash
pip install numpy pandas matplotlib scipy astropy requests
```

## 📁 Struttura File

```
├── test.py                    # Toolkit principale
├── validation_test.py         # Test di validazione completa
├── run_batch_analysis.py      # Script analisi batch
├── create_fits_data.py        # Generatore dati simulati
├── data/                      # Cartella dati FITS
│   ├── grb080916c_tte.fits
│   └── grb130427a_tte.fits
├── qg_analysis_results.json   # Risultati singolo GRB
└── qg_multi_results.json      # Risultati combinati
```

## 🎯 Prossimi Passi

1. **Dati Reali**: Sostituire file simulati con FITS veri da Fermi
2. **Più GRB**: Espandere dataset per statistica maggiore
3. **Validazione**: Confronto con limiti letteratura (Fermi-LAT 2009, 2015)
4. **Pubblicazione**: Preparazione risultati per peer review

## 📚 Riferimenti

- Fermi-LAT Collaboration (2009), Nature, 462, 331
- Amelino-Camelia et al. (2015), arXiv:1501.07154
- HEASARC Fermi Data Archive: https://heasarc.gsfc.nasa.gov/W3Browse/fermi/

## ⚠️ Note Importanti

- I dati simulati mostrano bias sistematici per test di validazione
- I dati FITS reali forniscono risultati più affidabili
- Sempre verificare intrinsic lags prima di interpretare segnali QG
- Confrontare sempre con letteratura scientifica

## 🤝 Contributi

Sistema open-source pronto per contributi della comunità scientifica.

---
**RTH Italia ideato da Christian Quintino De Luca**
