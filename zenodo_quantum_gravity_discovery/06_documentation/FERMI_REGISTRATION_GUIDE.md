# 🔬 GUIDA REGISTRAZIONE FERMI SCIENCE SUPPORT CENTER

## 🎯 OBIETTIVO: Scaricare dati FITS reali di GRB080916C

---

## 📋 STEP 1: REGISTRAZIONE

### **1.1 Vai al sito Fermi Science Support Center**
**URL:** https://fermi.gsfc.nasa.gov/cgi-bin/ssc/LAT/LATDataQuery.cgi

### **1.2 Clicca su "Register" o "Create Account"**
- **Nome:** Christian Quintino De Luca
- **Email:** info@rthitalia.com
- **Affiliation:** RTH Italia (Independent Research)
- **Country:** Italy
- **Research Interest:** Quantum Gravity phenomenology in Gamma-Ray Bursts

### **1.3 Attendi email di conferma**
- Controlla spam
- Clicca link di attivazione

---

## 📋 STEP 2: QUERY DATI GRB080916C

### **2.1 Parametri di Ricerca:**
```
Search Center (RA,Dec): 119.88, -56.59
Time Range: 243216266, 243217466 (MET)
Energy Range: 100, 300000 (MeV)
Radius: 12 (degrees)
Event Class: Transient (CLASS >= 128)
```

### **2.2 Filtri Qualità:**
```
Zenith Angle: < 90 degrees
Event Class: >= 128 (Transient)
Energy: > 100 MeV
```

### **2.3 Output:**
- **File FITS:** `GRB080916C_LAT_events.fits`
- **Dimensione:** ~10-50 MB
- **Formato:** FITS standard

---

## 📋 STEP 3: DOWNLOAD E VERIFICA

### **3.1 Download File**
- Clicca su "Download"
- Salva in directory locale

### **3.2 Verifica File**
```bash
# Controlla dimensione file
dir GRB080916C_LAT_events.fits

# Dovrebbe essere > 1 MB
```

---

## 📋 STEP 4: PREPARAZIONE ANALISI

### **4.1 Struttura File FITS**
```
GRB080916C_LAT_events.fits
├── EVENTS (Primary HDU)
│   ├── TIME (tempi di arrivo)
│   ├── ENERGY (energie in MeV)
│   ├── EVENT_CLASS (qualità eventi)
│   ├── ZENITH_ANGLE (angolo zenit)
│   └── ...
└── GTI (Good Time Intervals)
```

### **4.2 Dati Attesi**
- **~100-1000 fotoni** sopra 100 MeV
- **~10-50 fotoni** sopra 1 GeV
- **Tempi:** 0-1200 secondi dal trigger
- **Energie:** 100 MeV - 300 GeV

---

## 🎯 RISULTATI ATTESI

### **Con dati reali, probabilmente troveremo:**
- **Correlazione:** r ≈ 0.05-0.15 (compatibile con zero)
- **Significatività:** σ < 2 (nessuna evidenza)
- **E_QG limite:** > 10^17 GeV (conferma letteratura)

### **Questo è OK! Significa:**
- ✅ La nostra metodologia è corretta
- ✅ Confermiamo risultati Fermi-LAT 2009
- ✅ Pubblicazione valida su rivista

---

## 🚀 PROSSIMI PASSI

1. **Registrati** al Fermi Science Support Center
2. **Scarica** dati GRB080916C
3. **Adatta** il codice per FITS
4. **Analizza** dati reali
5. **Confronta** con letteratura
6. **Pubblica** risultati

---

## 📞 SUPPORTO

**Se hai problemi:**
- **Email Fermi:** fermi-help@slac.stanford.edu
- **Documentazione:** https://fermi.gsfc.nasa.gov/ssc/data/analysis/
- **Forum:** https://fermi.gsfc.nasa.gov/ssc/data/analysis/user/
