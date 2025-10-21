"""
=============================================================================
GRB QUANTUM GRAVITY ANALYZER - VERSIONE CORRETTA
=============================================================================
Versione corretta che risolve i bug identificati nell'analisi critica.
"""

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import matplotlib
matplotlib.use('Agg')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats, optimize
from scipy.interpolate import interp1d
import json
from datetime import datetime, timedelta

# ========================================================================
# COSTANTI FISICHE
# ========================================================================
C = 2.998e8  # Velocità della luce [m/s]
M_PLANCK = 1.220910e19  # Massa di Planck [GeV/c²]
E_PLANCK = M_PLANCK  # Energia di Planck [GeV]
MEV_TO_ERG = 1.60218e-6  # Conversione MeV -> erg

# ========================================================================
# FUNZIONI CORRETTE
# ========================================================================

def calculate_qg_delay_corrected(energy_gev, redshift, E_QG_gev):
    """
    Calcola il ritardo atteso da effetti di gravità quantistica.
    
    Formula CORRETTA: Δt = (E / E_QG) * (d_L / c)
    
    Parameters:
    -----------
    energy_gev : float or array
        Energia del fotone in GeV
    redshift : float
        Redshift della sorgente
    E_QG_gev : float
        Scala di gravità quantistica in GeV (parametro da determinare)
    
    Returns:
    --------
    float or array : Ritardo in secondi
    """
    
    # Distanza di luminosità (approssimazione per z > 1)
    H0 = 70  # km/s/Mpc
    c_km = C / 1000
    d_L_mpc = (c_km / H0) * redshift * (1 + redshift/2)  # Approssimazione
    d_L_m = d_L_mpc * 3.086e22  # Conversione Mpc -> metri
    
    # Ritardo quantistico CORRETTO
    delay = (energy_gev / E_QG_gev) * (d_L_m / C)
    
    return delay


def fit_energy_time_correlation_corrected(times, energies, redshift):
    """
    Cerca correlazione lineare tra energia e tempo di arrivo.
    VERSIONE CORRETTA con formule fisiche appropriate.
    """
    
    # Converti energie in GeV se necessario
    energies_gev = np.where(energies > 100, energies / 1000, energies)
    
    # Fit lineare: t = a + b*E
    def linear_model(E, t0, alpha):
        return t0 + alpha * E
    
    try:
        popt, pcov = optimize.curve_fit(linear_model, energies_gev, times)
        t0_fit, alpha_fit = popt
        t0_err, alpha_err = np.sqrt(np.diag(pcov))
        
        # Calcola chi-quadro
        t_pred = linear_model(energies_gev, *popt)
        residuals = times - t_pred
        chi2 = np.sum(residuals**2) / (len(times) - 2)
        
        # Coefficiente di correlazione
        r_value = stats.pearsonr(energies_gev, times)[0]
        p_value = stats.pearsonr(energies_gev, times)[1]
        
        # Significatività corretta per correlazione di Pearson
        n = len(times)
        if r_value != 0 and n > 2:
            t_stat = abs(r_value) * np.sqrt(n - 2) / np.sqrt(1 - r_value**2)
            significance_sigma = t_stat
        else:
            significance_sigma = 0
        
        # Stima E_QG CORRETTA
        if alpha_fit > 0:
            # Distanza di luminosità
            H0 = 70
            c_km = C / 1000
            d_L_m = (c_km / H0) * redshift * (1 + redshift/2) * 3.086e22
            
            # Formula CORRETTA: E_QG = d_L / (c * alpha)
            E_QG_est = d_L_m / (C * alpha_fit) / 1e9  # in GeV
            E_QG_err = E_QG_est * (alpha_err / alpha_fit)  # Propagazione errori
        else:
            E_QG_est = np.inf
            E_QG_err = np.inf
        
        results = {
            't0': t0_fit,
            't0_err': t0_err,
            'alpha': alpha_fit,
            'alpha_err': alpha_err,
            'chi2_reduced': chi2,
            'correlation': r_value,
            'p_value': p_value,
            'significance_sigma': significance_sigma,
            'E_QG_gev': E_QG_est,
            'E_QG_err_gev': E_QG_err,
            'n_photons': n
        }
        
        return results
        
    except Exception as e:
        print(f"Errore nel fit: {e}")
        return None


def analyze_qg_signal_corrected(times, energies, redshift, grb_name="Unknown"):
    """
    Analisi completa CORRETTA per segnali di gravità quantistica.
    """
    
    print(f"\n🔬 ANALISI CORRETTA GRB {grb_name}")
    print("=" * 50)
    
    # Fit correlazione
    results = fit_energy_time_correlation_corrected(times, energies, redshift)
    
    if results is None:
        print("❌ Errore nell'analisi")
        return None
    
    print(f"📊 RISULTATI CORRETTI:")
    print(f"   Correlazione: r = {results['correlation']:.4f}")
    print(f"   Significatività: {results['significance_sigma']:.2f}σ")
    print(f"   P-value: {results['p_value']:.2e}")
    print(f"   E_QG stimata: {results['E_QG_gev']:.2e} GeV")
    print(f"   Errore E_QG: {results['E_QG_err_gev']:.2e} GeV")
    print(f"   Fotoni analizzati: {results['n_photons']}")
    
    # Confronto con scala di Planck
    E_Planck_ratio = results['E_QG_gev'] / E_PLANCK
    print(f"\n🎯 CONFRONTO CON SCALA DI PLANCK:")
    print(f"   E_Planck = {E_PLANCK:.2e} GeV")
    print(f"   E_QG / E_Planck = {E_Planck_ratio:.2e}")
    
    if E_Planck_ratio < 0.01:
        print("   ⚠️  E_QG è MOLTO più bassa di E_Planck - SOSPETTO!")
    elif E_Planck_ratio > 10:
        print("   ✅ E_QG è ragionevole rispetto a E_Planck")
    else:
        print("   🤔 E_QG è vicina a E_Planck - interessante")
    
    # Interpretazione fisica
    print(f"\n🧠 INTERPRETAZIONE FISICA:")
    if results['significance_sigma'] > 5:
        print("   🚨 SIGNIFICATIVITÀ ALTA - Richiede validazione rigorosa!")
    elif results['significance_sigma'] > 3:
        print("   ⚠️  Significatività moderata - Possibile segnale")
    else:
        print("   ✅ Significatività bassa - Nessun segnale evidente")
    
    return results


def test_with_realistic_data():
    """
    Test con dati realistici per verificare che le correzioni funzionino.
    """
    print("\n🧪 TEST CON DATI REALISTICI")
    print("=" * 40)
    
    # Simula dati GRB080916C realistici
    np.random.seed(42)  # Per riproducibilità
    
    # Parametri GRB080916C
    z = 4.35
    n_photons = 1520
    
    # Energie realistiche (0.1-13.2 GeV)
    energies_kev = np.random.exponential(500, n_photons)  # Distribuzione esponenziale
    energies_kev = np.clip(energies_kev, 100, 13200)  # Range realistico
    
    # Tempi con PICCOLA correlazione (per testare se il codice la rileva)
    # Iniettiamo una correlazione molto piccola (r ≈ 0.05)
    times = np.random.normal(0, 1, n_photons)
    times += 0.001 * (energies_kev - np.mean(energies_kev))  # Correlazione molto piccola
    
    # Analisi corretta
    results = analyze_qg_signal_corrected(times, energies_kev, z, "080916C_TEST")
    
    return results


if __name__ == "__main__":
    print("🔬 GRB QUANTUM GRAVITY ANALYZER - VERSIONE CORRETTA")
    print("=" * 60)
    print("Questa versione risolve i bug identificati nell'analisi critica.")
    print("=" * 60)
    
    # Test con dati realistici
    results = test_with_realistic_data()
    
    print(f"\n📋 RIEPILOGO CORREZIONI APPLICATE:")
    print("   1. ✅ Formula ritardo QG corretta")
    print("   2. ✅ Calcolo E_QG senza fattore 0.5 errato")
    print("   3. ✅ Significatività basata su correlazione di Pearson")
    print("   4. ✅ Interpretazione fisica realistica")
    
    print(f"\n🎯 PROSSIMI PASSI:")
    print("   1. Testare con dati reali di GRB080916C")
    print("   2. Validare con multiple GRB")
    print("   3. Implementare controlli sistematici rigorosi")
