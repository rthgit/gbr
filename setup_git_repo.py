#!/usr/bin/env python3
"""
Setup Git repository per RTH Italia GBR project
"""

import subprocess
import os
import sys

def setup_git_repo():
    """Setup Git repository per GitHub"""
    
    print("🚀 Setting up Git repository for RTH Italia GBR project...")
    
    # Repository info
    repo_url = "https://github.com/rthgit/gbr.git"
    email = "info@rthitalia.com"
    name = "Christian Quintino De Luca"
    
    try:
        # Initialize git
        print("📁 Initializing Git repository...")
        subprocess.run(["git", "init"], check=True)
        
        # Configure git user
        print("👤 Configuring Git user...")
        subprocess.run(["git", "config", "user.name", name], check=True)
        subprocess.run(["git", "config", "user.email", email], check=True)
        
        # Add remote origin
        print("🔗 Adding remote origin...")
        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
        
        # Create .gitignore
        print("📝 Creating .gitignore...")
        gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Jupyter Notebook
.ipynb_checkpoints

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Data files (keep structure but not large files)
*.fits
*.zip
*.tar.gz

# Results (keep structure)
results/
output/
plots/
figures/

# Logs
*.log
logs/

# Temporary files
temp/
tmp/
*.tmp
"""
        
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        # Add all files
        print("📁 Adding files to Git...")
        subprocess.run(["git", "add", "."], check=True)
        
        # Create initial commit
        print("💾 Creating initial commit...")
        commit_message = """
🚀 Initial commit: Quantum Gravity Analysis in Gamma-Ray Bursts

- Complete analysis pipeline for GRB090902B
- Statistical validation methodology
- Multi-GRB comparison framework
- Scientific paper with honest assessment
- Open-source toolkit for QG research

Authors: Christian Quintino De Luca, Gregorio De Luca
Affiliation: RTH Italia - Research & Technology Hub
Email: info@rthitalia.com
ORCID: 0009-0000-4198-5449

This repository contains the complete dataset and analysis code 
for investigating anomalous energy-time correlations in GRB090902B, 
documenting a statistically significant (5.46σ) correlation that 
is consistent with quantum gravity predictions but requires 
further investigation to distinguish from astrophysical alternatives.
"""
        
        subprocess.run(["git", "commit", "-m", commit_message.strip()], check=True)
        
        # Push to GitHub
        print("🚀 Pushing to GitHub...")
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        
        print("✅ Git repository setup complete!")
        print(f"🌐 Repository URL: {repo_url}")
        print(f"📧 Contact: {email}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have Git installed and GitHub access configured")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    setup_git_repo()
