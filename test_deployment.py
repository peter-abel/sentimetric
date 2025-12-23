#!/usr/bin/env python3
"""
Quick deployment test script (updated for sentimetric)
"""

import sys
import os
from pathlib import Path


def check_file(filepath, description):
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False


def check_structure():
    print("\n" + "=" * 60)
    print("📦 PACKAGE STRUCTURE CHECK")
    print("=" * 60)
    
    files = {
        'setup.py': 'Setup file',
        'pyproject.toml': 'Project configuration',
        'README.md': 'README file',
        'LICENSE': 'License file',
        'MANIFEST.in': 'Manifest file',
        'sentimetric/__init__.py': 'Package __init__',
        'sentimetric/sentiment.py': 'Main module',
    }
    
    all_good = True
    for filepath, desc in files.items():
        if not check_file(filepath, desc):
            all_good = False
    
    return all_good


def check_imports():
    print("\n" + "=" * 60)
    print("🔍 IMPORT CHECK")
    print("=" * 60)
    
    try:
        sys.path.insert(0, '.')
        import sentimetric
        print(f"✅ Package imported successfully")
        print(f"   Version: {sentimetric.__version__}")
        print(f"   Available: {', '.join(sentimetric.__all__)}")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_basic_functionality():
    print("\n" + "=" * 60)
    print("🧪 FUNCTIONALITY TEST")
    print("=" * 60)
    
    try:
        from sentimetric import analyze, analyze_batch, Analyzer
        
        result = analyze("This is amazing!")
        print(f"✅ Basic analysis: {result}")
        
        results = analyze_batch(["Good", "Bad"])
        print(f"✅ Batch analysis: {len(results)} results")
        
        analyzer = Analyzer()
        result2 = analyzer.analyze("Great work!")
        print(f"✅ Analyzer class: {result2}")
        
        return True
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def check_readme():
    print("\n" + "=" * 60)
    print("📄 README CHECK")
    print("=" * 60)
    
    try:
        with open('README.md', 'r') as f:
            content = f.read()
        
        checks = {
            '# ': 'Has title',
            'pip install': 'Has installation instructions',
            '```python': 'Has code examples',
            'from sentimetric import': 'Shows import statement',
            'License': 'Mentions license',
        }
        
        all_good = True
        for check, desc in checks.items():
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"⚠️  {desc} - not found")
                all_good = False
        
        print(f"\n   README length: {len(content)} characters")
        return all_good
        
    except Exception as e:
        print(f"❌ README check failed: {e}")
        return False


def test_build():
    print("\n" + "=" * 60)
    print("🔨 BUILD TEST")
    print("=" * 60)
    
    try:
        import subprocess
        
        for dir in ['build', 'dist', 'sentimetric.egg-info', 'sentimetric-1.0.0.dist-info']:
            if Path(dir).exists():
                import shutil
                shutil.rmtree(dir)
        
        print("   Building package...")
        result = subprocess.run(
            ['python', '-m', 'build'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Build successful!")
            dist_files = list(Path('dist').glob('*'))
            print(f"   Created {len(dist_files)} distribution files:")
            for f in dist_files:
                print(f"   - {f.name}")
            return True
        else:
            print(f"❌ Build failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"⚠️  Build test skipped (install 'build' package): {e}")
        return None


def print_summary(results):
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")
    
    if failed == 0:
        print("\n🎉 All checks passed! Ready to deploy!")
    else:
        print("\n⚠️  Fix the issues above before deploying")


def main():
    print("🚀 Sentimetric - Pre-deployment Check")
    
    results = {
        'structure': check_structure(),
        'imports': check_imports(),
        'functionality': test_basic_functionality(),
        #'readme': check_readme(),
        'build': test_build(),
    }
    
    print_summary(results)


if __name__ == "__main__":
    main()
