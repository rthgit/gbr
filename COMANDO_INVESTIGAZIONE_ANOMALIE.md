# 🚀 COMANDO PER INVESTIGAZIONE ANOMALIE

## 📋 **INVESTIGAZIONE ANOMALIE SPECIFICHE:**

### **🔍 Test per Investigare le Anomalie Rilevate:**
```bash
python anomaly_investigation_test.py
```

---

## 🎯 **COSA FA L'INVESTIGAZIONE:**

### **🔬 1. TEST ROBUSTEZZA ANOMALIE:**
- **Dati null** (nessun QG) vs **QG iniettato noto**
- **Multiple realizzazioni** per testare consistenza
- **Confronto metodologie** su dati identici

### **🔬 2. TEST CALIBRAZIONE ANOMALIE:**
- **Diversi livelli QG** (0.0, 0.0001, 0.0005, 0.001, 0.002, 0.005)
- **Curva di calibrazione** per ogni metodologia
- **Soglia detection** ottimale

### **🔬 3. ANALISI ANOMALIE SPECIFICHE:**
- **Ensemble Methods**: 6.37σ (anomalia più alta)
- **Bayesian Optimization**: 3.04σ (significativa)
- **Power Law Lag Model**: 4.04σ (alta)
- **Quadratic Lag Model**: 3.34σ (significativa)

---

## 📊 **RISULTATI ATTESI:**

### **✅ Output Files:**
- `anomaly_investigation_test_results.json`
- `anomaly_investigation_test_results.png`

### **🎯 Risultati Chiave:**
- **Robustezza** delle anomalie su dati null vs QG
- **Calibrazione** delle metodologie
- **Distinzione** tra segnale reale e bias
- **Raccomandazioni** per metodologia ottimale

---

## 🚀 **ESEGUI SUBITO:**

**COMANDO PRINCIPALE:**
```bash
python anomaly_investigation_test.py
```

**🎯 QUESTO TEST SPIEGHERÀ SE LE ANOMALIE SONO REALI O BIAS!**

**🎯 IDENTIFICHERÀ LA METODOLOGIA PIÙ AFFIDABILE!**

**🎯 FORNIRÀ RACCOMANDAZIONI PER DATI REALI!**

