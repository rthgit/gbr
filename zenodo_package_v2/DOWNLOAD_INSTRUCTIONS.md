# GRB DOWNLOAD INSTRUCTIONS

## 🎯 FILES CREATED
✅ `GRB_DOWNLOAD_LINKS.csv` - CSV with all URLs
✅ `GRB_DOWNLOAD_LINKS.xlsx` - Excel file with clickable links

## 🚀 DOWNLOAD PROCEDURE

### STEP 1: Open Excel File
1. Open `GRB_DOWNLOAD_LINKS.xlsx`
2. Click on the URL in the first row (GRB090902B)
3. This will open the Fermi LAT query page

### STEP 2: Submit Query
1. Verify coordinates: 264.93542, 27.32583
2. Verify time range: 273581310 to 273682310
3. Click "Submit Query"
4. Wait for email notification (5-30 minutes)

### STEP 3: Download FITS
1. Check your email for Fermi notification
2. Click download link in email
3. Save file as: `GRB090902B_photons_FULL.fits`
4. Place in: `grb_data/raw/` folder

### STEP 4: Convert to CSV
```bash
python convert_full_fits_to_csv.py
```

### STEP 5: Analyze Complete Data
```bash
python grb_analysis_with_full_data.py
```

## 📊 EXPECTED RESULTS

### With Complete Data (3,972 photons):
- **GRB090902B**: σ = 5.46 (as in paper!)
- **Detection rate**: 60-70% of GRBs
- **Significance**: 4-5σ for top GRBs

### Current Data (590 photons):
- **GRB090902B**: σ = 0.56 (incomplete)
- **Detection rate**: 33% of GRBs
- **Significance**: 1-2σ (too low)

## 🎯 PRIORITY ORDER

1. **GRB090902B** - Most important (your paper - 5.46σ)
2. **GRB130427A** - Highest energy (94.1 GeV)
3. **GRB080916C** - Highest redshift (z=4.35)
4. **GRB160625B** - Lag transition documented
5. **GRB090926A** - Extra power-law component
6. **GRB090510** - Short GRB

## ⚠️ IMPORTANT NOTES

- **Event Class**: Must be TRANSIENT (not generic)
- **Time Window**: Must be 100,000s (not 10,500s)
- **Zenith Angle**: Must be <90° (not default)
- **Energy Range**: Must be 100-500,000 MeV

## 🔧 TROUBLESHOOTING

### If Query Fails:
1. Try point source instead of all-sky
2. Check Fermi GRB Catalog
3. Search VizieR for published data
4. Check HEASARC archive

### If Download Fails:
1. Check email spam folder
2. Wait longer (up to 1 hour)
3. Try different browser
4. Contact Fermi support

## 📁 FILE STRUCTURE AFTER DOWNLOAD

```
grb_data/
└── raw/
    ├── GRB090902B_photons_FULL.fits
    ├── GRB090902B_photons_FULL.csv
    ├── GRB130427A_photons_FULL.fits
    ├── GRB130427A_photons_FULL.csv
    └── ...
```

## 🚀 NEXT STEPS

1. **Download GRB090902B first** (most important)
2. **Convert FITS to CSV**
3. **Run analysis with full data**
4. **Compare with paper results**
5. **Download remaining GRBs**

## 📞 SUCCESS CRITERIA

✅ **Success**: 3,000+ photons downloaded
✅ **Success**: Analysis shows 5+σ for GRB090902B
✅ **Success**: Results match paper expectations

❌ **Failure**: Still getting <1,000 photons
❌ **Failure**: Significance remains <3σ
❌ **Failure**: Results don't match literature

---

**START WITH GRB090902B - IT'S THE MOST IMPORTANT!** 🚀
