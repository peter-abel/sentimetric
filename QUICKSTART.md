# 🚀 QUICK START GUIDE (sentimetric)

## Get Started in 3 Steps!

### 1️⃣ Customize Your Package (5 minutes)

Replace these in **ALL** files if needed:
- `Your Name` → Abel Peter
- `your.email@example.com` → peterabel791@gmail.com
- `yourusername` → your GitHub username
- `sentiment-analyzer` → `sentimetric` (package name used here)

### 2️⃣ Test Your Package (2 minutes)

```bash
# Navigate to the package directory
cd sentiment-package

# Run the test script
python test_deployment.py
```

### 3️⃣ Deploy to PyPI (10 minutes)

```bash
pip install --upgrade build twine
python -m build
twine upload --repository testpypi dist/*
twine upload dist/*
```

## ⚡ Quick Commands

```bash
# Test locally
pip install -e .
python -c "from sentimetric import analyze; print(analyze('Great!'))"

# Build
rm -rf dist/ build/ *.egg-info
python -m build
```
