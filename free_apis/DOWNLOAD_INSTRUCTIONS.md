# ISTRUZIONI DOWNLOAD DATI GRATUITI

## 🆓 TUTTI I DATI SONO GRATUITI PER RICERCA SCIENTIFICA

### 1. FERMI GBM/LAT (NASA)
**URL:** https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/
**Costo:** GRATUITO
**Registrazione:** Opzionale (solo per download massivi)

**GRB Target:**
- GRB080916C: 2008/090916/
- GRB130427A: 2013/130427/
- GRB090510: 2009/090510/

**File da scaricare:**
- glg_tte_n0_[GRB]_v00.fit (TTE data)
- glg_tte_n1_[GRB]_v00.fit (TTE data)
- glg_cspec_[GRB]_v00.pha (Spectrum)

### 2. SWIFT BAT (NASA)
**URL:** https://swift.gsfc.nasa.gov/archive/grb_table/
**Costo:** GRATUITO
**Registrazione:** Non richiesta

**Dati disponibili:**
- BAT event files
- Light curves
- Spectra
- Position data

### 3. MAGIC (MPI Munich)
**URL:** https://magic.mpp.mpg.de/public/results/magic/
**Costo:** GRATUITO
**Registrazione:** Non richiesta

**Dati disponibili:**
- Public results
- Published FITS files
- Analysis results

### 4. HESS (MPI Heidelberg)
**URL:** https://www.mpi-hd.mpg.de/hfm/HESS/
**Costo:** GRATUITO
**Registrazione:** Non richiesta

## 📋 PROCEDURA DOWNLOAD

### Step 1: Crea cartelle
```
mkdir free_data/fermi
mkdir free_data/swift
mkdir free_data/magic
mkdir free_data/hess
```

### Step 2: Download manuale
1. Vai agli URL sopra
2. Naviga alle cartelle GRB specifici
3. Scarica file FITS
4. Salva in cartelle appropriate

### Step 3: Analisi automatica
```python
python test.py  # Analizza dati scaricati
```

## 💡 SUGGERIMENTI

1. **Inizia con Fermi:** Più facile da scaricare
2. **Usa browser:** Per navigazione catalogo
3. **Verifica FITS:** Controlla che file siano validi
4. **Backup dati:** Salva copie locali

## 🔗 LINK UTILI

- [Fermi GBM Catalog](https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/)
- [Swift GRB Table](https://swift.gsfc.nasa.gov/archive/grb_table/)
- [MAGIC Results](https://magic.mpp.mpg.de/public/results/magic/)
- [HESS Data](https://www.mpi-hd.mpg.de/hfm/HESS/)

---
*Tutti i dati sono gratuiti per uso scientifico e educativo*
