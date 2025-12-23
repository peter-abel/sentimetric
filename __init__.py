"""
Sentimetric - A modern sentiment analysis library

Simple, fast, and accurate sentiment analysis with optional LLM support.
"""

__version__ = "1.0.0"
__author__ = "Abel Peter"
__email__ = "peterabel791@gmail.com"

# Import main components from the implementation module
from .sentiment import (
    analyze,
    analyze_batch,
    compare_methods,
    SentimentResult,
    Analyzer,
    LLMAnalyzer,
    Benchmark,
)

__all__ = [
    'analyze',
    'analyze_batch',
    'compare_methods',
    'SentimentResult',
    'Analyzer',
    'LLMAnalyzer',
    'Benchmark',
]
