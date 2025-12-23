# 🎭 Sentimetric - Modern Sentiment Analysis

[![PyPI version](https://badge.fury.io/py/sentimetric.svg)](https://badge.fury.io/py/sentimetric)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sentimetric is a modern, fast, and accurate sentiment analysis library with optional LLM support for complex emotions, sarcasm, and nuanced context.

## ✨ Features

- 🚀 Fast Rule-Based Analysis
- 🧠 Multi-LLM Support (OpenAI, Google Gemini, Anthropic Claude, Cohere, Hugging Face)
- 💰 Cost-Aware Model Selection with automatic fallback to cheaper models
- 📊 Batch Processing with parallel execution
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

### Multi-LLM Usage

Sentimetric now supports multiple LLM providers! Choose from OpenAI, Google Gemini, Anthropic Claude, Cohere, or Hugging Face.

#### Installation with LLM Support

```bash
# Install with all LLM providers
pip install "sentimetric[all]"

# Or install specific providers
pip install "sentimetric[openai]"      # For OpenAI
pip install "sentimetric[google]"      # For Google Gemini
pip install "sentimetric[anthropic]"   # For Anthropic Claude
pip install "sentimetric[cohere]"      # For Cohere
pip install "sentimetric[huggingface]" # For Hugging Face
```

#### Basic LLM Usage

```python
from sentimetric import LLMAnalyzer

# Auto-selects the best available provider
analyzer = LLMAnalyzer()  # Automatically detects available API keys

# Or specify a provider
analyzer = LLMAnalyzer(provider="openai", model="gpt-3.5-turbo")
# analyzer = LLMAnalyzer(provider="google", model="gemini-1.5-flash")
# analyzer = LLMAnalyzer(provider="anthropic", model="claude-3-haiku-20240307")
# analyzer = LLMAnalyzer(provider="cohere", model="command")
# analyzer = LLMAnalyzer(provider="huggingface", model="mistralai/Mixtral-8x7B-Instruct-v0.1")

result = analyzer.analyze("Oh great, another bug 🙄")
print(result.category)  # 'negative' (catches sarcasm)
print(result.reasoning) # Explanation from the LLM
```

#### Environment Variables

Set your API keys as environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-key"

# Google Gemini
export GOOGLE_API_KEY="your-google-key"

# Anthropic Claude
export ANTHROPIC_API_KEY="your-anthropic-key"

# Cohere
export COHERE_API_KEY="your-cohere-key"

# Hugging Face
export HUGGINGFACE_API_KEY="your-hf-key"
```

#### Cost-Aware Features

```python
# Auto-select cheapest model
analyzer = LLMAnalyzer(provider="openai", model="auto")  # Uses gpt-3.5-turbo

# Fallback to cheaper models on failure
analyzer = LLMAnalyzer(
    provider="openai",
    model="gpt-4",
    fallback_to_cheaper=True  # Falls back to gpt-3.5-turbo if gpt-4 fails
)
```

## 📚 Examples

See `examples.py` for comprehensive usage examples. Use `python examples.py` to run them locally.

## 🛠️ API Reference

### Core Functions
- `analyze(text, method='auto')` - Quick sentiment analysis
- `analyze_batch(texts, method='rule')` - Batch sentiment analysis
- `compare_methods(text, api_key=None)` - Compare rule-based vs LLM analysis

### Classes
- `Analyzer` - Fast rule-based sentiment analyzer
- `LLMAnalyzer` - Multi-provider LLM analyzer (OpenAI, Google, Anthropic, Cohere, Hugging Face)
- `SentimentResult` - Result container with polarity, category, confidence, reasoning, emotions, tone
- `Benchmark` - Accuracy testing and comparison utilities

### LLMAnalyzer Constructor Parameters
- `provider` - LLM provider ('openai', 'google', 'anthropic', 'cohere', 'huggingface', or 'auto')
- `model` - Model name or 'auto' for cheapest available
- `api_key` - API key (optional, uses environment variables)
- `fallback_to_cheaper` - Whether to fall back to cheaper models if requested model fails (default: True)

## 📞 Support

- Author: Abel Peter
- Email: peterabel791@gmail.com
- Issues: https://github.com/peter-abel/sentimetric/issues

---

Made with ❤️ by Abel Peter
