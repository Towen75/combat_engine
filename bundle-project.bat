@echo off
REM Combat Engine Code Bundle Script (Windows)
REM Uses optimized settings from .clinerules/bundle-config.json

echo 🎯 Bundling Combat Engine Project...
echo 📋 Using optimized settings from .clinerules/bundle-config.json

node .clinerules/workflows/bundle-code.js --include ".py" ".md" ".toml" ".txt" ".csv" ".json" --exclude-dirs "venv" "__pycache__" ".git" ".mypy_cache" ".pytest_cache" ".clinerules" "node_modules" "tests/__pycache__" --output "all-project-code.txt"

echo ✅ Bundle complete: all-project-code.txt
echo 📊 Configuration saved in .clinerules/bundle-config.json
pause
