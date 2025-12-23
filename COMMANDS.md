# 🚀 Quick Reference - Common Commands (sentimetric)

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
python test_deployment.py
```

## Building

```bash
# Build package
python -m build

# Check package
twine check dist/*
```

## Testing on TestPyPI

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ sentimetric
```

## Production Deployment

```bash
# Upload to PyPI
twine upload dist/*

# Install from PyPI
pip install sentimetric

# Verify
python -c "import sentimetric; print(sentimetric.__version__)"
```
