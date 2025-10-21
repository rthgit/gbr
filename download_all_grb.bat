@echo off
echo ===============================================
echo DOWNLOAD TUTTI I GRB REALI FERMI LAT
echo ===============================================

echo Scaricando GRB090902 (3972 fotoni)...
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020161615F357373F52_EV00.fits

echo.
echo Scaricando GRB090510 (2371 fotoni)...
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020161912F357373F19_EV00.fits

echo.
echo Scaricando GRB130427A (16 fotoni)...
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/L251020162012F357373F30_EV00.fits

echo.
echo ===============================================
echo DOWNLOAD COMPLETATO!
echo ===============================================
pause
