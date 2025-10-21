#!/bin/bash
# FERMI LAT BATCH DOWNLOAD SCRIPT
# After submitting queries on Fermi website, update QUERY_IDs below
# Then run: bash download_all_grbs.sh

# Create download directory
mkdir -p fermi_grb_data
cd fermi_grb_data

# ===== TOP 10 PRIORITY GRBs =====

# GRB221009A (Priority 1)
QUERY_ID_221009A="YOUR_QUERY_ID_HERE"
echo "Downloading GRB221009A..."
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_221009A}_EV00.fits
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_221009A}_SC00.fits

# GRB190114C (Priority 2)
QUERY_ID_190114C="YOUR_QUERY_ID_HERE"
echo "Downloading GRB190114C..."
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_190114C}_EV00.fits
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_190114C}_SC00.fits

# GRB090510 (Priority 3)
QUERY_ID_090510="YOUR_QUERY_ID_HERE"
echo "Downloading GRB090510..."
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_090510}_EV00.fits
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_090510}_SC00.fits

# GRB180720B (Priority 4)
QUERY_ID_180720B="YOUR_QUERY_ID_HERE"
echo "Downloading GRB180720B..."
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_180720B}_EV00.fits
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_180720B}_SC00.fits

# GRB080916C (Priority 5)
QUERY_ID_080916C="YOUR_QUERY_ID_HERE"
echo "Downloading GRB080916C..."
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_080916C}_EV00.fits
wget https://fermi.gsfc.nasa.gov/FTP/fermi/data/lat/queries/${QUERY_ID_080916C}_SC00.fits

# Add more as needed...

echo "Download complete!"
echo "Files saved in: fermi_grb_data/"
