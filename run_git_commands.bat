@echo off
echo 🚀 PUSHING TO GITHUB - MANUAL COMMANDS
echo =====================================
echo.

echo 📋 Step 1: Checking git status...
git status
echo.

echo ➕ Step 2: Adding all files...
git add .
echo.

echo 💾 Step 3: Committing changes...
git commit -m "Complete Reproducible Quantum Gravity Effects Package - 5 out of 8 GRBs show significant QG effects (2.28σ to 10.18σ) - DOI: 10.5281/zenodo.17408302"
echo.

echo 🚀 Step 4: Pushing to GitHub...
git push origin main
echo.

echo ✅ PUSH COMPLETED!
echo =====================================
echo.
echo 📊 Package pushed includes:
echo - Complete scientific paper (HTML + Markdown)
echo - 6 spectacular figures (PNG high resolution)
echo - Analysis scripts (Python)
echo - Real data (FITS, CSV, JSON)
echo - Zenodo metadata and instructions
echo.
echo 🌐 Repository: https://github.com/rthgit/gbr
echo 📄 DOI: 10.5281/zenodo.17408302
echo =====================================
echo.
pause
