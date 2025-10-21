@echo off
echo 🔍 Running GRB090902B Analysis...
echo =====================================

echo.
echo 📊 Testing simple GRB090902B analysis...
python test_grb090902_simple.py

echo.
echo 🧪 Testing QG discriminator tests...
python qg_discriminator_tests.py

echo.
echo 📚 Testing literature search...
python literature_search_grb090902.py

echo.
echo 📊 Testing catalog analyzer...
python catalog_analyzer_2flgc.py

echo.
echo ⚡ Testing batch analyzer...
python batch_grb_analyzer.py

echo.
echo =====================================
echo 🎉 Analysis complete!
pause

