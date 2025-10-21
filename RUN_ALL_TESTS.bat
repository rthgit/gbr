@echo off
echo ======================================================================
echo ESECUZIONE TUTTI I TEST CRITICI
echo ======================================================================
echo.

echo Test 1: Critical Validation Tests...
python critical_validation_tests.py
echo.

echo Test 2: Independent GRB Validation...
python independent_grb_validation.py
echo.

echo Test 3: Blind Analysis Test...
python blind_analysis_test.py
echo.

echo ======================================================================
echo TUTTI I TEST COMPLETATI!
echo ======================================================================
echo.
pause
