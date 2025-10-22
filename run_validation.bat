@echo off
echo Running GRB130427A validation...
python validate_10sigma_grb130427a.py
echo.
echo Running figure creation...
python create_paper_figures_final.py
echo.
echo All done!
pause

