#!/usr/bin/env python3
"""
Crea file FITS simulati per GRB080916C e GRB130427A
basati sui parametri pubblicati
"""

import numpy as np
from astropy.io import fits
from astropy.table import Table
import os

def create_grb_fits():
    # Crea dati simulati per GRB080916C (z=4.35, fotone da 13 GeV)
    np.random.seed(42)
    n_photons = 1000
    times_080916c = np.random.gamma(2, 3, n_photons) + np.random.uniform(-2, 5, n_photons)
    energies_080916c = np.random.lognormal(np.log(0.1), 1.0, n_photons)  # keV
    # Aggiungi fotone da 13 GeV
    times_080916c = np.append(times_080916c, [15.0, 20.0, 25.0])
    energies_080916c = np.append(energies_080916c, [13000, 8000, 5000])  # keV

    # Crea dati simulati per GRB130427A (z=0.34, fotone da 95 GeV)
    np.random.seed(123)
    n_photons = 1200
    times_130427a = np.random.gamma(1.5, 4, n_photons) + np.random.uniform(-1, 8, n_photons)
    energies_130427a = np.random.lognormal(np.log(0.2), 1.2, n_photons)  # keV
    # Aggiungi fotone da 95 GeV
    times_130427a = np.append(times_130427a, [10.0, 12.0, 18.0])
    energies_130427a = np.append(energies_130427a, [95000, 60000, 30000])  # keV

    # Salva GRB080916C
    tbl_080916c = Table([times_080916c, energies_080916c], names=['TIME', 'ENERGY'])
    hdu_080916c = fits.PrimaryHDU()
    hdu_080916c.header['OBJECT'] = 'GRB080916C'
    hdu_080916c.header['REDSHIFT'] = 4.35
    hdu_080916c.header['INSTRUME'] = 'GBM'
    hdu_080916c.header['COMMENT'] = 'Simulated TTE data for GRB080916C'
    hdu_data_080916c = fits.BinTableHDU(tbl_080916c)
    hdul_080916c = fits.HDUList([hdu_080916c, hdu_data_080916c])
    hdul_080916c.writeto('data/grb080916c_tte.fits', overwrite=True)

    # Salva GRB130427A
    tbl_130427a = Table([times_130427a, energies_130427a], names=['TIME', 'ENERGY'])
    hdu_130427a = fits.PrimaryHDU()
    hdu_130427a.header['OBJECT'] = 'GRB130427A'
    hdu_130427a.header['REDSHIFT'] = 0.34
    hdu_130427a.header['INSTRUME'] = 'GBM'
    hdu_130427a.header['COMMENT'] = 'Simulated TTE data for GRB130427A'
    hdu_data_130427a = fits.BinTableHDU(tbl_130427a)
    hdul_130427a = fits.HDUList([hdu_130427a, hdu_data_130427a])
    hdul_130427a.writeto('data/grb130427a_tte.fits', overwrite=True)

    print('OK: Creati file FITS simulati per GRB080916C e GRB130427A')
    print(f'   GRB080916C: {len(times_080916c)} fotoni, z={4.35}')
    print(f'   GRB130427A: {len(times_130427a)} fotoni, z={0.34}')

if __name__ == "__main__":
    create_grb_fits()
