# 🎭 Sentimetric - Modern Sentiment Analysis

[![PyPI version](https://badge.fury.io/py/sentimetric.svg)](https://badge.fury.io/py/sentimetric)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sentimetric is a modern, fast, and accurate sentiment analysis library with optional LLM support for complex emotions, sarcasm, and nuanced context.

## ✨ Features

- 🚀 Fast Rule-Based Analysis
- 🧠 LLM-Powered Analysis (optional)
- 📊 Batch Processing
- 🎯 High Accuracy with modern slang & emojis
- 🔧 Simple API: `from sentimetric import analyze`

## 🚀 Quick Start

### Installation

```bash
pip install sentimetric
```

### Basic Usage

```python
from sentimetric import analyze

# Quick analysis
result = analyze("This is amazing!")
print(result)
# Example output: SentimentResult(polarity=+0.90, category='positive', confidence=0.85)
```

### LLM Usage

Set your Anthropic API key in the environment to use LLM features:

```python
import os
os.environ['ANTHROPIC_API_KEY'] = 'your-key-here'

from sentimetric import LLMAnalyzer
analyzer = LLMAnalyzer()
result = analyzer.analyze("Oh great, another bug 🙄")
print(result.category)
```

## 📚 Examples

See `examples.py` for comprehensive usage examples. Use `python examples.py` to run them locally.

## 🛠️ API Reference

- `from sentimetric import analyze`
- `from sentimetric import analyze_batch, compare_methods`
- Classes: `Analyzer`, `LLMAnalyzer`, `SentimentResult`, `Benchmark`

## 📞 Support

- Author: Abel Peter
- Email: peterabel791@gmail.com
- Issues: https://github.com/yourusername/sentimetric/issues

---

Made with ❤️ by Abel Peter
