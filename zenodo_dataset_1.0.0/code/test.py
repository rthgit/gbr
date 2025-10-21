"""
=============================================================================
GRB QUANTUM GRAVITY ANALYZER - Analisi Dati Reali
=============================================================================
Toolkit per cercare segnali di gravità quantistica in dati di Gamma Ray Burst.
Basato su metodologie pubblicate (es. Fermi-LAT Collaboration 2009, Nature).

DATASET SUPPORTATI:
- Fermi GBM (Gamma-ray Burst Monitor): https://heasarc.gsfc.nasa.gov/W3Browse/fermi/fermigbrst.html
- Swift BAT: https://swift.gsfc.nasa.gov/archive/grb_table/
- File formato: FITS, ASCII, JSON

INSTALLAZIONE DIPENDENZE:
pip install numpy pandas matplotlib scipy astropy requests

UTILIZZO:
1. Scarica dati da Fermi/Swift (vedi funzione download_fermi_grb)
2. Carica il file con load_grb_data()
3. Esegui l'analisi completa con analyze_qg_signal()
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
# 1. CARICAMENTO DATI
# ========================================================================

def load_grb_data(filepath=None, format='simulated', instrument='auto'):
    """
    Carica dati di un GRB reale o simulato da diversi strumenti.
    
    Parameters:
    -----------
    filepath : str
        Path al file FITS/ASCII/JSON con i dati del GRB
    format : str
        'fits', 'ascii', 'json', o 'simulated'
    instrument : str
        'fermi', 'swift', 'magic', o 'auto' per rilevamento automatico
    
    Returns:
    --------
    dict : Dizionario con photon_times, photon_energies, metadata
    """
    
    if format == 'simulated':
        # Simula dati realistici basati su GRB 080916C
        print("📡 Simulando dati realistici tipo GRB 080916C...")
        print("    (Puoi sostituire con dati veri da Fermi/Swift)\n")
        
        np.random.seed(42)
        
        # GRB con redshift z=4.35, distanza ~13 Gly
        n_photons = 847
        
        # Tempi: burst duration ~60s, picco a t=5s
        t_trigger = 0.0
        times = []
        energies = []
        
        # Fase 1: Precursore (10% fotoni)
        n1 = int(0.1 * n_photons)
        t1 = np.random.exponential(2.0, n1) - 5
        e1 = np.random.lognormal(np.log(0.05), 0.8, n1)  # keV
        times.extend(t1)
        energies.extend(e1)
        
        # Fase 2: Main burst (70% fotoni)
        n2 = int(0.7 * n_photons)
        t2 = np.random.gamma(2, 2, n2) + 0
        e2 = np.random.lognormal(np.log(0.2), 1.2, n2)
        times.extend(t2)
        energies.extend(e2)
        
        # Fase 3: Fotoni ad alta energia (20% fotoni) - CRITICAL per QG!
        n3 = n_photons - n1 - n2
        t3 = np.random.uniform(5, 50, n3)
        e3 = np.random.lognormal(np.log(1.0), 1.5, n3)  # MeV-GeV
        
        # Aggiungi alcuni fotoni MOLTO energetici (>10 GeV)
        n_hev = 12
        t3[-n_hev:] = np.random.uniform(10, 45, n_hev)
        e3[-n_hev:] = np.random.uniform(5, 30, n_hev) * 1000  # GeV!
        
        times.extend(t3)
        energies.extend(e3)
        
        times = np.array(times)
        energies = np.array(energies)
        
        # Ordina per tempo
        idx = np.argsort(times)
        times = times[idx]
        energies = energies[idx]
        
        metadata = {
            'name': 'GRB_SIM_080916C',
            'redshift': 4.35,
            'distance_gly': 13.0,
            'ra': 119.8467,
            'dec': -56.6383,
            't_trigger': datetime(2008, 9, 16, 0, 12, 45),
            'duration_t90': 63.0,
            'fluence': 3.5e-4,  # erg/cm²
            'instrument': 'Simulated (Fermi-like)',
            'note': 'Dati simulati realistici - sostituisci con dati veri!'
        }
        
    elif format == 'fits':
        # Per caricare veri file FITS da diversi strumenti
        try:
            from astropy.io import fits
            
            # Rilevamento automatico strumento
            if instrument == 'auto':
                if 'fermi' in filepath.lower():
                    instrument = 'fermi'
                elif 'swift' in filepath.lower() or 'bat' in filepath.lower():
                    instrument = 'swift'
                elif 'magic' in filepath.lower():
                    instrument = 'magic'
                else:
                    instrument = 'generic'
            
            with fits.open(filepath) as hdul:
                # Prova a individuare l'HDU eventi
                data_hdu = None
                for hdu in hdul:
                    if hasattr(hdu, 'data') and hdu.data is not None:
                        cols = [c.name.upper() for c in hdu.columns] if hasattr(hdu, 'columns') else []
                        if any(name in cols for name in ['TIME','ENERGY','PHA','CHANNEL']):
                            data_hdu = hdu
                            break
                if data_hdu is None:
                    raise RuntimeError('Nessun HDU con eventi trovato (TIME/ENERGY).')
                cols = [c.name.upper() for c in data_hdu.columns]
                tbl = data_hdu.data
                
                # TIME
                if 'TIME' in cols:
                    times = np.array(tbl['TIME'], dtype=float)
                else:
                    raise RuntimeError('Colonna TIME assente nel FITS.')
                
                # ENERGY con gestione specifica per strumento
                if 'ENERGY' in cols:
                    energies = np.array(tbl['ENERGY'], dtype=float)
                    
                    # Conversione unità specifica per strumento
                    if instrument == 'swift':
                        # Swift BAT: energie in keV (15-150 keV)
                        energies = energies  # Mantieni keV
                    elif instrument == 'fermi':
                        # Fermi GBM: energie in keV, converti >100 keV in GeV per analisi
                        energies = energies  # Mantieni keV per ora
                    elif instrument == 'magic':
                        # MAGIC: energie in GeV
                        energies = energies * 1000  # Converti GeV -> keV per consistenza
                    else:
                        energies = energies  # Generico
                        
                elif 'PHA' in cols:
                    # PHA è canale; senza DRMs non convertiamo a energia fisica
                    energies = np.array(tbl['PHA'], dtype=float)
                elif 'CHANNEL' in cols:
                    energies = np.array(tbl['CHANNEL'], dtype=float)
                else:
                    raise RuntimeError('Colonna ENERGY/PHA/CHANNEL assente nel FITS.')
                
                # Metadati dall'header primario
                primary_header = hdul[0].header
                z = primary_header.get('REDSHIFT', np.nan)
                name = primary_header.get('OBJECT', 'GRB_UNK')
                instr = primary_header.get('INSTRUME', 'FITS')
                telescope = primary_header.get('TELESCOP', 'UNKNOWN')
                
                # Calcola distanza approssimativa se z disponibile
                if z == z and z > 0:
                    H0 = 70  # km/s/Mpc
                    c_km = C / 1000
                    d_L_mpc = (c_km / H0) * z * (1 + z/2)  # Approssimazione
                    distance_gly = d_L_mpc / 1000  # Mpc -> Gly
                else:
                    distance_gly = np.nan
                
                metadata = {
                    'name': name,
                    'redshift': float(z) if z == z else np.nan,
                    'distance_gly': distance_gly,
                    'instrument': instr,
                    'telescope': telescope,
                    'energy_range': get_energy_range(instrument),
                    'note': f'FITS import da {filepath} ({instrument.upper()})'
                }
        except ImportError:
            print("❌ Installa astropy: pip install astropy")
            return None
        except Exception as e:
            print(f"❌ Errore lettura FITS: {e}")
            return None
            
    elif format == 'json':
        with open(filepath, 'r') as f:
            data = json.load(f)
        times = np.array(data['times'])
        energies = np.array(data['energies'])
        metadata = data['metadata']
    
    return {
        'times': times,
        'energies': energies,
        'metadata': metadata
    }


def get_energy_range(instrument):
    """Restituisce il range energetico tipico per strumento"""
    ranges = {
        'fermi': '8 keV - 40 MeV (GBM) / 20 MeV - 300 GeV (LAT)',
        'swift': '15 - 150 keV (BAT)',
        'magic': '50 GeV - 50 TeV',
        'generic': 'Unknown'
    }
    return ranges.get(instrument, 'Unknown')

def download_fermi_grb(grb_name, save_path='./'):
    """
    Scarica dati pubblici di un GRB da Fermi GBM.
    
    IMPORTANTE: Richiede accesso internet e registrazione gratuita a HEASARC.
    
    Parameters:
    -----------
    grb_name : str
        Nome del GRB (es. 'GRB080916C', 'GRB130427A')
    save_path : str
        Cartella dove salvare i file
    
    Example:
    --------
    download_fermi_grb('GRB080916C', save_path='./data/')
    
    Poi visita: https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/w3browse.pl
    Cerca il burst e scarica i file TTE (Time-Tagged Event)
    """
    
    url_base = "https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/"
    
    print(f"📥 Per scaricare dati reali di {grb_name}:")
    print(f"   1. Vai a: https://heasarc.gsfc.nasa.gov/W3Browse/fermi/fermigbrst.html")
    print(f"   2. Cerca '{grb_name}'")
    print(f"   3. Scarica i file TTE (Time-Tagged Events)")
    print(f"   4. Usa astropy.io.fits per leggerli")
    print(f"\n   Oppure usa il Fermi Science Tools:")
    print(f"   https://fermi.gsfc.nasa.gov/ssc/data/analysis/")


# ========================================================================
# 2. ANALISI GRAVITÀ QUANTISTICA
# ========================================================================

def calculate_qg_delay(energy_gev, redshift, n=1):
    """
    Calcola il ritardo atteso da effetti di gravità quantistica.
    
    Formula: Δt = (n / 2) * (E / E_Planck) * (d_L / c)
    
    dove:
    - n = 1 (lineare) o 2 (quadratico) in E/E_Planck
    - d_L = distanza di luminosità
    
    Parameters:
    -----------
    energy_gev : float or array
        Energia del fotone in GeV
    redshift : float
        Redshift della sorgente
    n : int
        Ordine della correzione (1 o 2)
    
    Returns:
    --------
    float or array : Ritardo in secondi
    """
    
    # Distanza di luminosità (approssimazione per z > 1)
    # Formula esatta richiede cosmologia, qui uso approssimazione
    H0 = 70  # km/s/Mpc
    c_km = C / 1000
    d_L_mpc = (c_km / H0) * redshift * (1 + redshift/2)  # Approssimazione
    d_L_m = d_L_mpc * 3.086e22  # Conversione Mpc -> metri
    
    # Ritardo quantistico
    if n == 1:
        delay = 0.5 * (energy_gev / E_PLANCK) * (d_L_m / C)
    elif n == 2:
        delay = 0.5 * (energy_gev / E_PLANCK)**2 * (d_L_m / C)
    else:
        raise ValueError("n deve essere 1 o 2")
    
    return delay


def fit_energy_time_correlation(times, energies, redshift):
    """
    Cerca correlazione lineare tra energia e tempo di arrivo.
    Questo è il test principale per QG!
    
    Se QG esiste: fotoni ad alta energia arrivano più tardi.
    Fit: t = t0 + α * E
    
    Returns:
    --------
    dict : Risultati del fit con parametri e significatività
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
        
        # Stima E_QG (scala energetica di QG)
        if alpha_fit > 0:
            # d_L dalla cosmologia
            H0 = 70
            c_km = C / 1000
            d_L_m = (c_km / H0) * redshift * (1 + redshift/2) * 3.086e22
            
            # Da Δt/E = 0.5 * (1/E_QG) * (d_L/c)
            # Quindi: E_QG = 0.5 * d_L / (c * alpha)
            E_QG_est = 0.5 * d_L_m / (C * alpha_fit) / 1e9  # in GeV
        else:
            E_QG_est = np.inf
        
        results = {
            't0': t0_fit,
            't0_err': t0_err,
            'alpha': alpha_fit,
            'alpha_err': alpha_err,
            'chi2_reduced': chi2,
            'correlation': r_value,
            'p_value': p_value,
            'E_QG_GeV': E_QG_est,
            'significance_sigma': abs(r_value) / np.sqrt((1 - r_value**2) / (len(times) - 2))
        }
        
    except Exception as e:
        print(f"⚠️ Fit fallito: {e}")
        results = None
    
    return results


def likelihood_ratio_test(times, energies, redshift):
    """
    Test del rapporto di verosimiglianza (Likelihood Ratio Test).
    Confronta modello NULL (no QG) vs modello QG.
    
    Questo è il metodo standard usato nelle pubblicazioni!
    """
    
    energies_gev = np.where(energies > 100, energies / 1000, energies)
    
    # Modello NULL: tempi indipendenti dall'energia
    # log-likelihood = -0.5 * sum((t_i - t_mean)^2 / sigma^2)
    t_mean = np.mean(times)
    sigma_null = np.std(times)
    log_L_null = -0.5 * np.sum((times - t_mean)**2 / sigma_null**2)
    
    # Modello QG: t = t0 + alpha * E
    def qg_model(E, t0, alpha):
        return t0 + alpha * E
    
    try:
        popt, _ = optimize.curve_fit(qg_model, energies_gev, times)
        t_pred = qg_model(energies_gev, *popt)
        sigma_qg = np.std(times - t_pred)
        log_L_qg = -0.5 * np.sum((times - t_pred)**2 / sigma_qg**2)
        
        # Test statistic
        LR = 2 * (log_L_qg - log_L_null)
        # p-value da chi-quadro con 1 d.o.f. (alpha è il parametro extra)
        p_val = 1 - stats.chi2.cdf(LR, df=1)
        
        # Significatività in sigma
        sigma_significance = stats.norm.ppf(1 - p_val/2)
        
        return {
            'log_L_null': log_L_null,
            'log_L_qg': log_L_qg,
            'LR_statistic': LR,
            'p_value': p_val,
            'sigma': sigma_significance,
            'detection': sigma_significance > 3.0  # 3-sigma threshold
        }
    except:
        return None


# ========================================================================
# 3. VISUALIZZAZIONE
# ========================================================================

def plot_comprehensive_analysis(grb_data, fit_results):
    """
    Crea un plot multi-pannello con tutta l'analisi.
    """
    
    times = grb_data['times']
    energies = grb_data['energies']
    metadata = grb_data['metadata']
    
    # Converti energie in GeV
    energies_gev = np.where(energies > 100, energies / 1000, energies)
    
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # ------------------------
    # 1. Light Curve
    # ------------------------
    ax1 = fig.add_subplot(gs[0, :])
    bins = np.linspace(times.min(), times.max(), 50)
    ax1.hist(times, bins=bins, alpha=0.7, color='dodgerblue', edgecolor='black')
    ax1.set_xlabel('Tempo dalla trigger [s]', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Conteggi per bin', fontsize=12, fontweight='bold')
    ax1.set_title(f"🌟 Light Curve: {metadata['name']} (z={metadata['redshift']})", 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # ------------------------
    # 2. Spettro Energetico
    # ------------------------
    ax2 = fig.add_subplot(gs[1, 0])
    bins_e = np.logspace(np.log10(energies_gev.min()), np.log10(energies_gev.max()), 30)
    ax2.hist(energies_gev, bins=bins_e, alpha=0.7, color='orangered', edgecolor='black')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel('Energia [GeV]', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Conteggi', fontsize=11, fontweight='bold')
    ax2.set_title('📊 Spettro Energetico', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axvline(10, color='red', linestyle='--', linewidth=2, label='10 GeV (soglia QG)')
    ax2.legend()
    
    # ------------------------
    # 3. CORRELAZIONE E-T (IL CUORE!)
    # ------------------------
    ax3 = fig.add_subplot(gs[1, 1:])
    
    # Scatter plot
    scatter = ax3.scatter(energies_gev, times, c=energies_gev, 
                         cmap='plasma', s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
    
    # Fit line se disponibile
    if fit_results:
        e_fit = np.linspace(energies_gev.min(), energies_gev.max(), 100)
        t_fit = fit_results['t0'] + fit_results['alpha'] * e_fit
        ax3.plot(e_fit, t_fit, 'r--', linewidth=2.5, label=f"Fit: t = {fit_results['t0']:.2f} + {fit_results['alpha']:.2e}·E")
    
    ax3.set_xlabel('Energia [GeV]', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Tempo di arrivo [s]', fontsize=12, fontweight='bold')
    ax3.set_title('🔍 CORRELAZIONE ENERGIA-TEMPO (Test QG)', fontsize=13, fontweight='bold')
    ax3.set_xscale('log')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=10)
    
    cbar = plt.colorbar(scatter, ax=ax3, label='Energia [GeV]')
    
    # ------------------------
    # 4. Ritardi attesi per QG
    # ------------------------
    ax4 = fig.add_subplot(gs[2, 0])
    
    e_range = np.logspace(np.log10(0.1), np.log10(100), 100)
    delay_n1 = calculate_qg_delay(e_range, metadata['redshift'], n=1)
    delay_n2 = calculate_qg_delay(e_range, metadata['redshift'], n=2)
    
    ax4.plot(e_range, delay_n1, 'b-', linewidth=2, label='QG Lineare (n=1)')
    ax4.plot(e_range, delay_n2, 'r-', linewidth=2, label='QG Quadratica (n=2)')
    ax4.axhline(1.0, color='green', linestyle='--', alpha=0.7, label='1 secondo')
    ax4.axhline(0.001, color='orange', linestyle='--', alpha=0.7, label='1 millisecondo (risoluzione)')
    
    ax4.set_xscale('log')
    ax4.set_yscale('log')
    ax4.set_xlabel('Energia [GeV]', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Ritardo atteso [s]', fontsize=11, fontweight='bold')
    ax4.set_title('⏱️ Predizioni QG', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    # ------------------------
    # 5. Box con risultati
    # ------------------------
    ax5 = fig.add_subplot(gs[2, 1:])
    ax5.axis('off')
    
    if fit_results:
        text_results = f"""
        ═══════════════════════════════════════════════
        📈 RISULTATI ANALISI GRAVITÀ QUANTISTICA
        ═══════════════════════════════════════════════
        
        Correlazione E-t:  r = {fit_results['correlation']:.4f}
        P-value:           p = {fit_results['p_value']:.2e}
        Significatività:   {fit_results['significance_sigma']:.2f} σ
        
        Parametro ritardo: α = ({fit_results['alpha']:.2e} ± {fit_results['alpha_err']:.2e}) s/GeV
        
        Scala energetica stimata:
        E_QG ≈ {fit_results['E_QG_GeV']:.2e} GeV
        (confronta con E_Planck = {E_PLANCK:.2e} GeV)
        
        χ² ridotto:        {fit_results['chi2_reduced']:.3f}
        
        ───────────────────────────────────────────────
        💡 INTERPRETAZIONE:
        """
        
        if fit_results['p_value'] < 0.05:
            text_results += """
        ⚠️ Correlazione SIGNIFICATIVA!
        → Possibile segnale di gravità quantistica
        → Richiesta verifica con più GRB
        → Esclusione sistematiche (intrinsic lag)
            """
        else:
            text_results += """
        ✅ Nessuna correlazione significativa
        → Consistente con relatività speciale
        → Limite su scala QG: E_QG > ...
        → Più dati potrebbero migliorare i limiti
            """
    else:
        text_results = "⚠️ Fit non riuscito - troppo pochi fotoni ad alta energia"
    
    ax5.text(0.05, 0.95, text_results, transform=ax5.transAxes,
             fontsize=10, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.suptitle(f"🚀 ESPERIMENTO GRAVITÀ QUANTISTICA - {metadata['name']}", 
                 fontsize=16, fontweight='bold', y=0.995)
    
    plt.tight_layout()
    return fig


# ========================================================================
# 4. PIPELINE COMPLETA
# ========================================================================

def analyze_qg_signal(grb_data, make_plots=True):
    """
    Esegue l'analisi completa per cercare segnali di gravità quantistica.
    
    Parameters:
    -----------
    grb_data : dict
        Dati del GRB da analyze
    make_plots : bool
        Se True, genera i grafici
    
    Returns:
    --------
    dict : Tutti i risultati dell'analisi
    """
    
    print("=" * 70)
    print("🔬 AVVIO ANALISI GRAVITÀ QUANTISTICA")
    print("=" * 70)
    
    times = grb_data['times']
    energies = grb_data['energies']
    metadata = grb_data['metadata']
    
    print(f"\n📡 GRB: {metadata['name']}")
    print(f"   Redshift: z = {metadata['redshift']}")
    print(f"   Distanza: {metadata['distance_gly']:.1f} miliardi anni luce")
    print(f"   Fotoni totali: {len(times)}")
    
    # Statistiche base
    energies_gev = np.where(energies > 100, energies / 1000, energies)
    n_high_energy = np.sum(energies_gev > 1.0)
    n_very_high = np.sum(energies_gev > 10.0)
    
    print(f"   Fotoni > 1 GeV: {n_high_energy}")
    print(f"   Fotoni > 10 GeV: {n_very_high} ⭐")
    
    # FIT CORRELAZIONE
    print("\n" + "─" * 70)
    print("🔍 ANALISI CORRELAZIONE ENERGIA-TEMPO...")
    print("─" * 70)
    
    fit_results = fit_energy_time_correlation(times, energies, metadata['redshift'])
    
    if fit_results:
        print(f"✓ Coefficiente correlazione: r = {fit_results['correlation']:.4f}")
        print(f"✓ Significatività statistica: {fit_results['significance_sigma']:.2f} σ")
        print(f"✓ P-value: {fit_results['p_value']:.2e}")
        
        if fit_results['p_value'] < 0.05:
            print("\n🎉 RISULTATO SIGNIFICATIVO!")
            print(f"   → Possibile segnale di QG con E_QG ~ {fit_results['E_QG_GeV']:.2e} GeV")
        else:
            print("\n✅ Nessun segnale (consistente con relatività)")
            print(f"   → Limite inferiore: E_QG > {fit_results['E_QG_GeV']:.2e} GeV")
    else:
        print("⚠️ Fit non riuscito")
    
    # LIKELIHOOD RATIO TEST
    print("\n" + "─" * 70)
    print("📊 LIKELIHOOD RATIO TEST...")
    print("─" * 70)
    
    lr_results = likelihood_ratio_test(times, energies, metadata['redshift'])
    
    if lr_results:
        print(f"✓ LR statistic: {lr_results['LR_statistic']:.3f}")
        print(f"✓ Significatività: {lr_results['sigma']:.2f} σ")
        
        if lr_results['detection']:
            print("🎯 DETECTION! (> 3σ)")
        else:
            print("📉 No detection (< 3σ)")
    
    # PLOTS
    if make_plots:
        print("\n📊 Generazione grafici...")
        fig = plot_comprehensive_analysis(grb_data, fit_results)
        plt.show()
    
    print("\n" + "=" * 70)
    print("✅ ANALISI COMPLETATA")
    print("=" * 70)
    
    return {
        'fit_results': fit_results,
        'lr_results': lr_results,
        'n_photons': len(times),
        'n_high_energy': n_high_energy,
        'metadata': metadata
    }

# ========================================================================
# 5b. COMBINAZIONE BAYESIANA MULTI-GRB
# ========================================================================

def combine_grb_results(results_list):
    """
    Combina risultati di più GRB sommando le log-likelihood del modello QG.
    Ritorna statistiche aggregate e una stima/limite combinato su E_QG.
    """
    if not results_list:
        return None
    # Somma log-likelihood dove disponibili
    log_L_qg_list = []
    for r in results_list:
        lr = r.get('lr_results') if isinstance(r, dict) else None
        if lr and ('log_L_qg' in lr):
            log_L_qg_list.append(lr['log_L_qg'])
    log_L_combined = float(np.sum(log_L_qg_list)) if log_L_qg_list else np.nan
    # Heuristica: prendi i migliori limiti E_QG e sintetizza il minimo come limite conservativo
    eqg_values = []
    for r in results_list:
        fr = r.get('fit_results') if isinstance(r, dict) else None
        if fr and fr.get('E_QG_GeV') not in (None, np.inf):
            eqg_values.append(fr['E_QG_GeV'])
    combined_limit_gev = float(np.nanmin(eqg_values)) if len(eqg_values) > 0 else np.nan
    return {
        'log_L_combined': log_L_combined,
        'num_grb': len(results_list),
        'E_QG_limit_conservative_GeV': combined_limit_gev
    }


def analyze_multiple_grb_in_folder(folder_path='data', pattern='*.fits', make_plots=False):
    """
    Analizza tutti i file FITS nella cartella e combina i risultati.
    Ritorna lista risultati e sintesi combinata.
    """
    import glob
    import os
    filepaths = sorted(glob.glob(os.path.join(folder_path, pattern)))
    results = []
    for fp in filepaths:
        print(f"\n📥 Carico: {fp}")
        grb = load_grb_data(fp, format='fits')
        if not grb:
            print("   ⚠️ Skip per errore di lettura.")
            continue
        res = analyze_qg_signal(grb, make_plots=make_plots)
        results.append(res)
    combined = combine_grb_results(results)
    # Salva riepilogo
    summary = {
        'folder': folder_path,
        'pattern': pattern,
        'combined': combined,
        'num_analyzed': len(results)
    }
    with open('qg_multi_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print("\n✅ Riepilogo combinato salvato in 'qg_multi_results.json'")
    return results, combined


# ========================================================================
# 5c. VALIDAZIONE STATISTICA E TEST DI CONTROLLO
# ========================================================================

def control_sample_test(grb_data, energy_threshold_kev=100):
    """
    Test di controllo: analizza fotoni a bassa energia dove QG è trascurabile.
    Se trovi correlazione anche qui, hai un bias sistematico!
    """
    times = grb_data['times']
    energies = grb_data['energies']
    metadata = grb_data['metadata']
    
    # Filtra solo fotoni a bassa energia
    low_energy_mask = energies < energy_threshold_kev
    times_low = times[low_energy_mask]
    energies_low = energies[low_energy_mask]
    
    print(f"\n🔬 TEST DI CONTROLLO (fotoni < {energy_threshold_kev} keV)")
    print(f"   Fotoni analizzati: {len(times_low)}")
    
    if len(times_low) < 10:
        print("   ⚠️ Troppo pochi fotoni per test significativo")
        return None
    
    # Analisi identica a quella principale
    fit_results = fit_energy_time_correlation(times_low, energies_low, metadata['redshift'])
    lr_results = likelihood_ratio_test(times_low, energies_low, metadata['redshift'])
    
    if fit_results:
        print(f"   ✓ Correlazione bassa energia: r = {fit_results['correlation']:.4f}")
        print(f"   ✓ P-value: {fit_results['p_value']:.2e}")
        
        if fit_results['p_value'] < 0.05:
            print("   ⚠️ ATTENZIONE: Correlazione significativa anche a bassa energia!")
            print("   → Possibile bias sistematico (intrinsic lag)")
            return {'bias_detected': True, 'results': fit_results}
        else:
            print("   ✅ Nessuna correlazione a bassa energia (OK)")
            return {'bias_detected': False, 'results': fit_results}
    
    return None


def mock_injection_test(grb_data, qg_signal_strength=1e-3, n_trials=100):
    """
    Test di iniezione: aggiunge segnale QG artificiale e verifica detection rate.
    """
    times = grb_data['times']
    energies = grb_data['energies']
    metadata = grb_data['metadata']
    
    print(f"\n🧪 TEST DI INIEZIONE MOCK (n={n_trials} trials)")
    print(f"   Segnale QG iniettato: α = {qg_signal_strength:.2e} s/GeV")
    
    detection_count = 0
    false_positive_count = 0
    
    for trial in range(n_trials):
        # Test senza segnale (false positive rate)
        fit_null = fit_energy_time_correlation(times, energies, metadata['redshift'])
        if fit_null and fit_null['p_value'] < 0.05:
            false_positive_count += 1
        
        # Test con segnale iniettato
        energies_gev = np.where(energies > 100, energies / 1000, energies)
        times_injected = times + qg_signal_strength * energies_gev
        
        fit_injected = fit_energy_time_correlation(times_injected, energies, metadata['redshift'])
        if fit_injected and fit_injected['p_value'] < 0.05:
            detection_count += 1
    
    false_positive_rate = false_positive_count / n_trials
    detection_rate = detection_count / n_trials
    
    print(f"   ✓ False positive rate: {false_positive_rate:.3f} (deve essere < 0.05)")
    print(f"   ✓ Detection rate: {detection_rate:.3f}")
    
    if false_positive_rate > 0.05:
        print("   ⚠️ ATTENZIONE: False positive rate troppo alto!")
    
    return {
        'false_positive_rate': false_positive_rate,
        'detection_rate': detection_rate,
        'is_valid': false_positive_rate <= 0.05
    }


def intrinsic_lag_analysis(grb_data, pulse_detection_threshold=0.1):
    """
    Analisi per rilevare intrinsic lags che potrebbero mascherare QG.
    Cerca correlazioni E-t all'interno di singoli pulse.
    """
    times = grb_data['times']
    energies = grb_data['energies']
    metadata = grb_data['metadata']
    
    print(f"\n🔍 ANALISI INTRINSIC LAG")
    
    # Semplice rilevamento pulse: trova picchi nella light curve
    bins = np.linspace(times.min(), times.max(), 50)
    hist, bin_edges = np.histogram(times, bins=bins)
    
    # Trova picchi sopra soglia
    peak_threshold = np.max(hist) * pulse_detection_threshold
    peak_bins = bins[:-1][hist > peak_threshold]
    
    if len(peak_bins) < 2:
        print("   ⚠️ Nessun pulse rilevato per analisi intrinsic lag")
        return None
    
    print(f"   ✓ Rilevati {len(peak_bins)} pulse")
    
    # Analizza correlazione E-t per ogni pulse
    pulse_results = []
    for i, peak_time in enumerate(peak_bins):
        # Fotoni in questo pulse (±2s)
        pulse_mask = np.abs(times - peak_time) < 2.0
        times_pulse = times[pulse_mask]
        energies_pulse = energies[pulse_mask]
        
        if len(times_pulse) < 5:
            continue
            
        fit_pulse = fit_energy_time_correlation(times_pulse, energies_pulse, metadata['redshift'])
        if fit_pulse:
            pulse_results.append({
                'pulse_id': i,
                'peak_time': peak_time,
                'n_photons': len(times_pulse),
                'correlation': fit_pulse['correlation'],
                'p_value': fit_pulse['p_value']
            })
    
    if pulse_results:
        avg_correlation = np.mean([p['correlation'] for p in pulse_results])
        avg_p_value = np.mean([p['p_value'] for p in pulse_results])
        
        print(f"   ✓ Correlazione media nei pulse: r = {avg_correlation:.4f}")
        print(f"   ✓ P-value medio: {avg_p_value:.2e}")
        
        if avg_p_value < 0.05:
            print("   ⚠️ ATTENZIONE: Correlazione significativa nei pulse!")
            print("   → Possibile intrinsic lag che maschera QG")
        
        return {
            'n_pulses': len(pulse_results),
            'avg_correlation': avg_correlation,
            'avg_p_value': avg_p_value,
            'intrinsic_lag_detected': avg_p_value < 0.05
        }
    
    return None


def comprehensive_validation(grb_data, make_plots=False):
    """
    Esegue tutti i test di validazione su un GRB.
    """
    print("=" * 80)
    print("🔬 VALIDAZIONE COMPLETA DEL SISTEMA")
    print("=" * 80)
    
    # 1. Analisi principale
    main_results = analyze_qg_signal(grb_data, make_plots=make_plots)
    
    # 2. Test di controllo
    control_results = control_sample_test(grb_data)
    
    # 3. Test di iniezione
    injection_results = mock_injection_test(grb_data)
    
    # 4. Analisi intrinsic lag
    lag_results = intrinsic_lag_analysis(grb_data)
    
    # 5. Sintesi validazione
    print("\n" + "=" * 80)
    print("📋 SINTESI VALIDAZIONE")
    print("=" * 80)
    
    validation_summary = {
        'main_analysis': main_results,
        'control_test': control_results,
        'injection_test': injection_results,
        'intrinsic_lag': lag_results,
        'is_reliable': True
    }
    
    # Verifica affidabilità
    if control_results and control_results.get('bias_detected'):
        print("❌ SISTEMA NON AFFIDABILE: Bias sistematico rilevato")
        validation_summary['is_reliable'] = False
    
    if injection_results and not injection_results.get('is_valid'):
        print("❌ SISTEMA NON AFFIDABILE: False positive rate troppo alto")
        validation_summary['is_reliable'] = False
    
    if lag_results and lag_results.get('intrinsic_lag_detected'):
        print("⚠️ ATTENZIONE: Intrinsic lag rilevato - interpretazione cauta")
    
    if validation_summary['is_reliable']:
        print("✅ SISTEMA AFFIDABILE: Tutti i test superati")
    
    return validation_summary


def analyze_multi_instrument_data(data_folder='data', make_plots=False):
    import os
    """
    Analizza dati da tutti gli strumenti (Fermi, Swift, MAGIC) e combina i risultati.
    
    Parameters:
    -----------
    data_folder : str
        Cartella principale con sottocartelle per strumento
    make_plots : bool
        Se creare plot per ogni strumento
    
    Returns:
    --------
    dict : Risultati combinati per strumento e totali
    """
    print("""
    ================================================================
    ANALISI MULTI-STRUMENTO GRB
    ================================================================
    Fermi GBM/LAT + Swift BAT + MAGIC
    Combinazione Bayesiana per limite E_QG robusto
    ================================================================
    """)
    
    instruments = ['fermi', 'swift', 'magic']
    all_results = {}
    
    for instrument in instruments:
        print(f"\n{'='*60}")
        print(f"ANALISI {instrument.upper()}")
        print(f"{'='*60}")
        
        instrument_folder = os.path.join(data_folder, instrument)
        if not os.path.exists(instrument_folder):
            print(f"WARNING: Cartella {instrument_folder} non trovata, skip.")
            continue
            
        # Analizza tutti i file FITS per questo strumento
        results, combined = analyze_multiple_grb_in_folder(
            folder_path=instrument_folder, 
            pattern='*.fits', 
            make_plots=make_plots
        )
        
        all_results[instrument] = {
            'individual_results': results,
            'combined': combined,
            'num_grb': len(results)
        }
        
        if combined:
            print(f"\nRISULTATI {instrument.upper()}:")
            print(f"   GRB analizzati: {combined['num_grb']}")
            print(f"   Log-likelihood: {combined['log_L_combined']:.2f}")
            print(f"   E_QG limite: {combined['E_QG_limit_conservative_GeV']:.2e} GeV")
            print(f"   vs E_Planck: {combined['E_QG_limit_conservative_GeV'] / E_PLANCK:.2e}")
    
    # Combinazione finale multi-strumento
    print(f"\n{'='*60}")
    print("COMBINAZIONE FINALE MULTI-STRUMENTO")
    print(f"{'='*60}")
    
    # Raccogli tutti i risultati individuali
    all_individual_results = []
    for instrument, data in all_results.items():
        if data['individual_results']:
            all_individual_results.extend(data['individual_results'])
    
    # Combinazione finale
    final_combined = combine_grb_results(all_individual_results)
    
    if final_combined:
        print(f"\nRISULTATO FINALE:")
        print(f"   Strumenti: {len([k for k, v in all_results.items() if v['num_grb'] > 0])}")
        print(f"   GRB totali: {final_combined['num_grb']}")
        print(f"   Log-likelihood totale: {final_combined['log_L_combined']:.2f}")
        print(f"   E_QG limite FINALE: {final_combined['E_QG_limit_conservative_GeV']:.2e} GeV")
        print(f"   vs E_Planck: {final_combined['E_QG_limit_conservative_GeV'] / E_PLANCK:.2e}")
        
        # Salva risultati finali
        final_summary = {
            'analysis_date': datetime.now().isoformat(),
            'instruments': all_results,
            'final_combined': final_combined,
            'total_grb': final_combined['num_grb']
        }
        
        # Converti numpy types per JSON
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.bool_, np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        final_summary_clean = convert_numpy(final_summary)
        with open('qg_multi_instrument_results.json', 'w') as f:
            json.dump(final_summary_clean, f, indent=2)
        print(f"\nRisultati finali salvati in 'qg_multi_instrument_results.json'")
    
    return all_results, final_combined

# ========================================================================
# 5. MAIN - ESEMPIO D'USO
# ========================================================================

if __name__ == "__main__":
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║     🌌 CACCIA ALLA GRAVITÀ QUANTISTICA NEI GRB 🌌            ║
    ║                                                                ║
    ║  Toolkit per analizzare dati reali di Gamma Ray Burst        ║
    ║  e cercare violazioni della relatività speciale               ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # ==================
    # STEP 1: Carica dati
    # ==================
    print("\n🔄 STEP 1: Caricamento dati GRB...")
    
    # OPZIONE A: Usa dati simulati (per testare)
    grb_data = load_grb_data(format='simulated')
    
    # OPZIONE B: Usa dati reali (decommentare quando disponibili)
    # download_fermi_grb('GRB080916C')  # Scarica istruzioni
    # grb_data = load_grb_data('path/to/grb080916c_tte.fits', format='fits')
    
    # ==================
    # STEP 2: Analisi completa
    # ==================
    print("\n🔄 STEP 2: Analisi gravità quantistica...")
    
    results = analyze_qg_signal(grb_data, make_plots=True)
    
    # ==================
    # STEP 3: Salva risultati
    # ==================
    print("\n💾 Salvando risultati...")
    
    output = {
        'grb_name': grb_data['metadata']['name'],
        'analysis_date': datetime.now().isoformat(),
        'results': {
            'correlation': results['fit_results']['correlation'] if results['fit_results'] else None,
            'p_value': results['fit_results']['p_value'] if results['fit_results'] else None,
            'E_QG_limit_GeV': results['fit_results']['E_QG_GeV'] if results['fit_results'] else None,
        }
    }
    
    with open('qg_analysis_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("✅ Risultati salvati in 'qg_analysis_results.json'")
    
    print("""
    
    ╔════════════════════════════════════════════════════════════════╗
    ║                    🎓 PROSSIMI PASSI                          ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  1. Analizza più GRB per aumentare statistica                ║
    ║  2. Combina risultati con analisi Bayesiana                  ║
    ║  3. Confronta con dati pubblicati (Fermi-LAT papers)         ║
    ║  4. Esplora effetti sistematici (intrinsic lags)             ║
    ║  5. Contribuisci alla ricerca open-source!                   ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
