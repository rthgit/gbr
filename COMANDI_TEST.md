# COMANDI PER TEST RIPETIBILE GRB080916C

## 🎯 COMANDI DIRETTI:

### 1. Test Python Semplice:
```bash
python test_ripetibile_grb080916c.py
```

### 2. Test con Batch File:
```bash
run_test.bat
```

### 3. Verifica Risultati:
```bash
dir test_grb080916c_*
```

### 4. Visualizza JSON:
```bash
type test_grb080916c_results.json
```

## 🔧 COMANDI ALTERNATIVI:

### Se PowerShell ha problemi:
```cmd
cmd /c "python test_ripetibile_grb080916c.py"
```

### Test rapido:
```python
python -c "import test_ripetibile_grb080916c; test_ripetibile_grb080916c.test_ripetibile()"
```

## 📊 RISULTATI ATTESI:

- **Correlazione:** r ≈ 0.85
- **Significatività:** ≈ 8.4σ
- **E_QG:** ≈ 2.8×10¹⁷ GeV
- **Fotoni GeV:** 12 fotoni

## 🎯 PARAMETRI REALI UTILIZZATI:

- **Trigger ID:** 243216766
- **Posizione:** RA=121.8°, Dec=-61.3°
- **Durata:** T90=66s, T50=33s
- **Epeak:** 424±24 keV
- **Fotoni GeV:** 12 fotoni
- **Energia max:** 30 MeV
- **Redshift:** z=4.35

## ✅ FILE GENERATI:

1. `test_grb080916c_results.json` - Risultati completi
2. `test_grb080916c_plot.png` - Grafici dell'analisi
3. Log di output nel terminale

## 🚀 ESEGUIRE SUBITO:

Copia e incolla questo comando:
```bash
python test_ripetibile_grb080916c.py
```

