# 🚀 COMANDI PER INVESTIGAZIONE ANOMALIA

## 📋 **INVESTIGAZIONE SCOMPARSA ANOMALIA:**

### **🔍 Investigazione Anomalia:**
```bash
python anomaly_investigation.py
```

---

## 🎯 **COSA FA L'INVESTIGAZIONE:**

### **🔬 1. INVESTIGAZIONE SCOMPARSA ANOMALIA:**
- **Confronto metodologie** originali vs validazione
- **Analisi parametri** che causano la scomparsa
- **Test con dati identici** ma metodologie diverse
- **Identificazione causa root** della scomparsa

### **🔬 2. TEST SENSIBILITÀ PARAMETRI:**
- **qg_strength**: [0.0005, 0.001, 0.0015, 0.002, 0.0025]
- **noise_level**: [0.05, 0.1, 0.15, 0.2, 0.25]
- **intrinsic_lag_strength**: [0.05, 0.1, 0.15, 0.2, 0.25]
- **n_photons**: [1000, 2000, 3000, 4000, 5000]

### **🔬 3. CONFRONTO METODOLOGIE:**
- **Metodologia Originale**: Correlazione diretta (3.32σ)
- **Metodologia Validazione**: Modelli lag avanzati (0.05-0.60σ)
- **Metodologia Ibrida**: Originale + validazione
- **Metodologia Semplificata**: Solo correlazione base

---

## 📊 **RISULTATI ATTESI:**

### **✅ Output Files:**
- `anomaly_investigation_results.json`
- `anomaly_investigation_results.png`

### **🎯 Risultati Chiave:**
- **Significatività Originale**: 3.32σ
- **Significatività Validazione**: 0.05-0.60σ
- **Perdita Significatività**: 2.7-3.3σ
- **Cause Identificate**: Metodologia troppo conservativa

---

## 🚀 **ESEGUI SUBITO:**

**COMANDO PRINCIPALE:**
```bash
python anomaly_investigation.py
```

**🎯 QUESTO TEST SPIEGHERÀ PERCHÉ L'ANOMALIA È SCOMPARSA!**
