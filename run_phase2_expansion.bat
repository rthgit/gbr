@echo off
echo 🚀 FASE 2: ESPANSIONE E VALIDAZIONE SCIENTIFICA
echo ================================================
echo.

echo 📊 Step 1: Running QG-Analyzer 2.0...
echo ----------------------------------------
python QG_Analyzer_2.0.py
echo.

echo 🌌 Step 2: Running DEUT 2.0 Quantum Layer...
echo ---------------------------------------------
python DEUT_2.0_Quantum_Layer.py
echo.

echo ✅ FASE 2 COMPLETATA!
echo ================================================
echo.
echo 📁 Files created:
echo   - QG_Analyzer_2.0_Results.csv
echo   - QG_Analyzer_2.0_Summary.json
echo   - QG_Analyzer_2.0_Log.txt
echo   - QG_Analyzer_2.0_Multi_GRB_Results.png
echo   - DEUT_2.0_Theoretical_Paper.md
echo   - DEUT_2.0_Parameters.json
echo   - DEUT_2.0_Quantum_Layer_Integration.png
echo.
echo 🎯 Next steps:
echo   1. Review results and validate findings
echo   2. Prepare Paper 2 (observational)
echo   3. Prepare Paper 3 (theoretical)
echo   4. Plan Phase 3: Automation and tools
echo.
pause
