@echo off
echo Running final energy correction...
python final_energy_correction.py
echo.
echo Running GRB090926A correction...
python correct_grb090926a_test.py
echo.
echo All corrections completed!
pause

