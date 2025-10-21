@echo off
echo 🚀 PUSHING TO GITHUB...
echo.

echo 📋 Checking git status...
git status

echo.
echo ➕ Adding all files...
git add .

echo.
echo 💾 Committing changes...
git commit -m "🚀 Complete Reproducible Quantum Gravity Effects Package - 5 out of 8 GRBs show significant QG effects (2.28σ to 10.18σ) - DOI: 10.5281/zenodo.17408302"

echo.
echo 🚀 Pushing to GitHub...
git push origin main

echo.
echo ✅ PUSH COMPLETED!
echo.
echo 📊 Package includes:
echo - Complete scientific paper (HTML + Markdown)
echo - 6 spectacular figures (PNG high resolution)
echo - Analysis scripts (Python)
echo - Real data (FITS, CSV, JSON)
echo - Zenodo metadata and instructions
echo.
echo 🌐 Repository: https://github.com/rthgit/gbr
echo 📄 DOI: 10.5281/zenodo.17408302
echo.
pause
