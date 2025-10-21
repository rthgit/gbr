#!/usr/bin/env python3
"""
Fix Git push error - create main branch first
"""

import subprocess
import sys

def fix_git_push():
    """Fix Git push by creating main branch"""
    
    print("🔧 Fixing Git push error...")
    
    try:
        # Check current branch
        print("📋 Checking current branch...")
        result = subprocess.run(["git", "branch"], capture_output=True, text=True)
        print(f"Current branches: {result.stdout}")
        
        # Create main branch if it doesn't exist
        print("🌿 Creating main branch...")
        subprocess.run(["git", "checkout", "-b", "main"], check=True)
        
        # Check status
        print("📊 Checking Git status...")
        subprocess.run(["git", "status"], check=True)
        
        # Add all files
        print("📁 Adding all files...")
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit if there are changes
        print("💾 Committing changes...")
        subprocess.run(["git", "commit", "-m", "🚀 Initial commit: Quantum Gravity Analysis in Gamma-Ray Bursts"], check=True)
        
        # Push to GitHub
        print("🚀 Pushing to GitHub...")
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        
        print("✅ Git push successful!")
        print("🌐 Repository URL: https://github.com/rthgit/gbr")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print("💡 Try these commands manually:")
        print("   git checkout -b main")
        print("   git add .")
        print("   git commit -m 'Initial commit'")
        print("   git push -u origin main")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    fix_git_push()

