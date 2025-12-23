"""
Sentiment - A modern sentiment analysis library

Simple, fast, and accurate sentiment analysis with optional LLM support.

Basic usage:
    >>> from sentimetric import analyze
    >>> analyzer = analyze("This is amazing!")
    >>> print(analyzer)
    SentimentResult(polarity=0.9, category='positive', confidence=0.85)

LLM usage:
    >>> from sentimetric import LLMAnalyzer
    >>> analyzer = LLMAnalyzer(api_key="your-key")
    >>> result = analyzer.analyze("Oh great, another bug 🙄")
    >>> print(result.category)  # 'negative' (catches sarcasm)
"""


__version__ = "1.0.0"
__all__ = ['analyze', 'analyze_batch', 'SentimentResult', 'Analyzer', 'LLMAnalyzer', 'compare_methods']

import re
from typing import List, Dict, Union, Optional
from dataclasses import dataclass, asdict
from collections import Counter


@dataclass
class SentimentResult:
    """
    Result of sentiment analysis

    
    Attributes:
        polarity: Sentiment score from -1 (negative) to 1 (positive)
        category: Classification as 'positive', 'negative', 'neutral', or 'mixed'
        confidence: Confidence score from 0 to 1
        subjectivity: How subjective the text is (0=objective, 1=subjective)
        method: Analysis method used ('rule_based' or 'llm')
        reasoning: Optional explanation of the classification (LLM only)
        emotions: Optional list of detected emotions (LLM only)
        tone: Optional tone description (LLM only)
    """
    polarity: float
    category: str
    confidence: float
    subjectivity: float
    method: str = 'rule_based'
    reasoning: Optional[str] = None
    emotions: Optional[List[str]] = None
    tone: Optional[str] = None
    
    def __str__(self):
        return f"SentimentResult(polarity={self.polarity:+.2f}, category='{self.category}', confidence={self.confidence:.2f})"
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)
    
    @property
    def is_positive(self) -> bool:
        return self.category == 'positive'
    
    @property
    def is_negative(self) -> bool:
        return self.category == 'negative'
    
    @property
    def is_neutral(self) -> bool:
        return self.category in ['neutral', 'mixed']


class Analyzer:
    """
    Fast rule-based sentiment analyzer
    
    Good for: Quick analysis, batch processing, clear sentiment
    Limitations: May miss sarcasm, complex emotions, subtle context
    """
    
    def __init__(self):
        # Sentiment lexicons with intensity scores
        self.positive_words = {
            'amazing': 0.9, 'awesome': 0.9, 'excellent': 0.9, 'perfect': 0.9,
            'outstanding': 0.9, 'incredible': 0.9, 'fantastic': 0.9, 'brilliant': 0.9,
            'wonderful': 0.9, 'spectacular': 0.9, 'phenomenal': 0.9, 'superb': 0.9,
            'great': 0.7, 'good': 0.6, 'nice': 0.5, 'love': 0.8, 'like': 0.5,
            'enjoy': 0.6, 'helpful': 0.6, 'useful': 0.6, 'cool': 0.6,
            'impressive': 0.7, 'beautiful': 0.7, 'happy': 0.7, 'glad': 0.6,
            'thanks': 0.6, 'thank': 0.6, 'best': 0.8,
        }
        
        self.negative_words = {
            'terrible': -0.9, 'horrible': -0.9, 'awful': -0.9, 'disgusting': -0.9,
            'pathetic': -0.9, 'useless': -0.8, 'waste': -0.8, 'garbage': -0.8,
            'trash': -0.8, 'worst': -0.9, 'hate': -0.8, 'disaster': -0.8,
            'bad': -0.6, 'poor': -0.6, 'wrong': -0.5, 'disappointing': -0.7,
            'disappointed': -0.7, 'boring': -0.6, 'confusing': -0.5, 'confused': -0.5,
            'sucks': -0.7, 'shit': -0.7, 'crap': -0.7,
        }
        
        # Modern slang (positive context)
        self.slang_positive = {
            'insane': 0.8, 'crazy': 0.7, 'sick': 0.8, 'fire': 0.9,
            'lit': 0.8, 'dope': 0.7, 'goat': 0.9, 'beast': 0.8,
            'savage': 0.7, 'slaps': 0.8, 'vibes': 0.6, 'based': 0.6,
        }
        
        self.intensifiers = {
            'very': 1.3, 'really': 1.3, 'extremely': 1.5, 'absolutely': 1.5,
            'incredibly': 1.5, 'so': 1.2, 'super': 1.4, 'ultra': 1.4,
        }
        
        self.diminishers = {
            'slightly': 0.5, 'somewhat': 0.5, 'fairly': 0.6, 'rather': 0.6,
            'pretty': 0.7, 'quite': 0.7, 'kinda': 0.5, 'sorta': 0.5,
        }
        
        self.negations = {
            'not', 'no', 'never', 'neither', 'nobody', 'nothing',
            "don't", "doesn't", "didn't", "can't", "won't", "shouldn't",
            "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't",
            'without', 'lack',
        }
        
        # Emojis
        self.emoji_positive = {
            '😊': 0.7, '😀': 0.7, '😃': 0.7, '😄': 0.7, '😁': 0.7,
            '😍': 0.9, '🥰': 0.9, '😘': 0.8, '❤️': 0.8, '💕': 0.8,
            '👍': 0.7, '👏': 0.7, '🙌': 0.8, '✨': 0.6, '⭐': 0.6,
            '🔥': 0.8, '💯': 0.8, '🎉': 0.7, '😂': 0.6, '🤣': 0.6,
        }
        
        self.emoji_negative = {
            '😢': -0.7, '😭': -0.7, '😞': -0.6, '😔': -0.6, '😠': -0.8,
            '😡': -0.9, '🤬': -0.9, '💔': -0.8, '👎': -0.7, '😒': -0.6,
            '🙄': -0.4,
        }
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with polarity, category, and confidence
        """
        if not text or not text.strip():
            return SentimentResult(0.0, 'neutral', 0.0, 0.0, 'rule_based')
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        sentiment_score = 0.0
        sentiment_count = 0
        negation_active = False
        intensifier_mult = 1.0
        
        for word in words:
            if word in self.negations:
                negation_active = True
                continue
            
            if word in self.intensifiers:
                intensifier_mult = self.intensifiers[word]
                continue
            
            if word in self.diminishers:
                intensifier_mult = self.diminishers[word]
                continue
            
            score = 0.0
            
            # Check slang (if positive context)
            if word in self.slang_positive:
                context_positive = any(ind in text_lower for ind in ['!', 'thank', 'wow', 'omg'])
                if context_positive:
                    score = self.slang_positive[word]
            
            # Check regular words
            elif word in self.positive_words:
                score = self.positive_words[word]
            elif word in self.negative_words:
                score = self.negative_words[word]
            
            if score != 0.0:
                score *= intensifier_mult
                if negation_active:
                    score = -score * 0.8
                
                sentiment_score += score
                sentiment_count += 1
                intensifier_mult = 1.0
                negation_active = False
        
        # Check emojis
        for char in text:
            if char in self.emoji_positive:
                sentiment_score += self.emoji_positive[char]
                sentiment_count += 1
            elif char in self.emoji_negative:
                sentiment_score += self.emoji_negative[char]
                sentiment_count += 1
        
        # Exclamation boost
        if text.count('!') > 0 and sentiment_score != 0:
            boost = min(1 + (text.count('!') * 0.1), 1.3)
            sentiment_score *= boost
        
        # Question mark reduction
        if '?' in text and sentiment_count > 0:
            sentiment_score *= 0.8
        
        # Normalize
        if sentiment_count > 0:
            polarity = max(-1.0, min(1.0, sentiment_score / max(1, sentiment_count * 0.7)))
        else:
            polarity = 0.0
        
        # Subjectivity
        word_count = len(words)
        subjectivity = min(1.0, sentiment_count / max(1, word_count) * 2)
        
        # Category
        if polarity > 0.15:
            category = 'positive'
        elif polarity < -0.15:
            category = 'negative'
        else:
            category = 'neutral'
        
        # Confidence
        confidence = min(1.0, (sentiment_count / max(1, word_count)) * 3)
        confidence = max(0.3, confidence)  # Minimum confidence
        
        return SentimentResult(
            polarity=round(polarity, 4),
            category=category,
            confidence=round(confidence, 4),
            subjectivity=round(subjectivity, 4),
            method='rule_based'
        )
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze multiple texts"""
        return [self.analyze(text) for text in texts]


class LLMAnalyzer:
    """
    LLM-powered sentiment analyzer using Claude API
    
    Good for: Complex emotions, sarcasm, nuanced context, mixed feelings
    Requires: ANTHROPIC_API_KEY environment variable or api_key parameter
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize LLM analyzer
        
        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        import os
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "API key required. Either:\n"
                "  1. Pass api_key parameter: LLMAnalyzer(api_key='your-key')\n"
                "  2. Set environment variable: export ANTHROPIC_API_KEY='your-key'"
            )
        
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"
        
        self.system_prompt = """Analyze sentiment. Respond ONLY with JSON (no markdown):
{
  "polarity": <-1.0 to 1.0>,
  "category": "<positive|negative|neutral|mixed>",
  "confidence": <0.0 to 1.0>,
  "reasoning": "<brief explanation>",
  "emotions": ["<emotion1>", "<emotion2>"],
  "tone": "<enthusiastic|sarcastic|grateful|critical|etc>"
}

Understand: modern slang, sarcasm, emojis, context, mixed emotions."""
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment using LLM
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentResult with detailed analysis
        """
        if not text or not text.strip():
            return SentimentResult(0.0, 'neutral', 0.0, 0.0, 'llm')
        
        try:
            import requests
            import json
            
            response = requests.post(
                self.base_url,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.model,
                    "max_tokens": 500,
                    "system": self.system_prompt,
                    "messages": [{"role": "user", "content": f"Analyze: {text}"}]
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code}")
            
            content = response.json()['content'][0]['text'].strip()
            content = content.replace('```json', '').replace('```', '').strip()
            
            data = json.loads(content)
            
            return SentimentResult(
                polarity=float(data.get('polarity', 0.0)),
                category=data.get('category', 'neutral'),
                confidence=float(data.get('confidence', 0.5)),
                subjectivity=0.8,  # LLM analyses are inherently subjective
                method='llm',
                reasoning=data.get('reasoning'),
                emotions=data.get('emotions'),
                tone=data.get('tone')
            )
            
        except Exception as e:
            # Fallback to rule-based if LLM fails
            print(f"LLM error: {e}. Falling back to rule-based analysis.")
            analyzer = Analyzer()
            result = analyzer.analyze(text)
            result.method = 'rule_based_fallback'
            return result
    
    def analyze_batch(self, texts: List[str], max_workers: int = 5) -> List[SentimentResult]:
        """
        Analyze multiple texts with parallel processing
        
        Args:
            texts: List of texts to analyze
            max_workers: Number of parallel workers
            
        Returns:
            List of SentimentResults
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import time
        
        results = [None] * len(texts)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(self._analyze_delayed, text, i * 0.2): i
                for i, text in enumerate(texts)
            }
            
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                results[idx] = future.result()
        
        return results
    
    def _analyze_delayed(self, text: str, delay: float) -> SentimentResult:
        """Helper for rate limiting"""
        import time
        time.sleep(delay)
        return self.analyze(text)


# Convenience functions
def analyze(text: str, method: str = 'auto') -> SentimentResult:
    """
    Quick sentiment analysis
    
    Args:
        text: Text to analyze
        method: 'rule' (fast), 'llm' (accurate), or 'auto' (rule-based)
        
    Returns:
        SentimentResult
        
    Example:
        >>> result = sentiment.analyze("This is amazing!")
        >>> print(result.category)
        'positive'
    """
    if method == 'llm':
        analyzer = LLMAnalyzer()
        return analyzer.analyze(text)
    else:
        analyzer = Analyzer()
        return analyzer.analyze(text)


def analyze_batch(texts: List[str], method: str = 'rule') -> List[SentimentResult]:
    """
    Batch sentiment analysis
    
    Args:
        texts: List of texts to analyze
        method: 'rule' (fast) or 'llm' (accurate)
        
    Returns:
        List of SentimentResults
    """
    if method == 'llm':
        analyzer = LLMAnalyzer()
        return analyzer.analyze_batch(texts)
    else:
        analyzer = Analyzer()
        return analyzer.analyze_batch(texts)


def compare_methods(text: str, api_key: Optional[str] = None) -> Dict[str, SentimentResult]:
    """
    Compare rule-based vs LLM analysis
    
    Args:
        text: Text to analyze
        api_key: Optional API key for LLM
        
    Returns:
        Dictionary with 'rule_based' and 'llm' results
    """
    rule_analyzer = Analyzer()
    rule_result = rule_analyzer.analyze(text)
    
    try:
        llm_analyzer = LLMAnalyzer(api_key=api_key)
        llm_result = llm_analyzer.analyze(text)
    except Exception as e:
        llm_result = None
        print(f"LLM analysis failed: {e}")
    
    return {
        'rule_based': rule_result,
        'llm': llm_result
    }


# Testing and benchmarking
class Benchmark:
    """Benchmark and compare analyzer accuracy"""
    
    @staticmethod
    def create_test_set() -> List[Dict[str, Union[str, str]]]:
        """
        Create labeled test set
        
        Returns:
            List of dicts with 'text' and 'expected' category
        """
        return [
            # Clear positive
            {"text": "This is amazing! Love it!", "expected": "positive"},
            {"text": "Absolutely fantastic work!", "expected": "positive"},
            {"text": "Thank you so much! 😊", "expected": "positive"},
            
            # Clear negative
            {"text": "This is terrible. Complete waste.", "expected": "negative"},
            {"text": "I hate this so much.", "expected": "negative"},
            {"text": "Worst experience ever 😡", "expected": "negative"},
            
            # Neutral
            {"text": "It is what it is.", "expected": "neutral"},
            {"text": "Okay, I guess.", "expected": "neutral"},
            
            # Sarcasm (challenging)
            {"text": "Oh great, another bug 🙄", "expected": "negative"},
            {"text": "Yeah, real helpful buddy", "expected": "negative"},
            {"text": "Sure, that makes perfect sense", "expected": "negative"},
            
            # Modern slang (challenging)
            {"text": "This is insane! Thank you!", "expected": "positive"},
            {"text": "This slaps so hard 🔥", "expected": "positive"},
            {"text": "Bro this is sick!", "expected": "positive"},
            
            # Mixed emotions
            {"text": "Good but expected more", "expected": "neutral"},
            {"text": "Not bad, actually pretty decent", "expected": "positive"},
            
            # Negation
            {"text": "Not good at all", "expected": "negative"},
            {"text": "Not bad!", "expected": "positive"},
        ]
    
    @staticmethod
    def test_accuracy(analyzer: Union[Analyzer, LLMAnalyzer], test_set: Optional[List] = None) -> Dict:
        """
        Test analyzer accuracy
        
        Args:
            analyzer: Analyzer instance to test
            test_set: Optional custom test set
            
        Returns:
            Accuracy metrics
        """
        if test_set is None:
            test_set = Benchmark.create_test_set()
        
        correct = 0
        total = len(test_set)
        errors = []
        
        for item in test_set:
            result = analyzer.analyze(item['text'])
            
            if result.category == item['expected']:
                correct += 1
            else:
                errors.append({
                    'text': item['text'],
                    'expected': item['expected'],
                    'got': result.category,
                    'polarity': result.polarity,
                    'confidence': result.confidence
                })
        
        accuracy = correct / total
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'errors': errors,
            'method': result.method
        }
    
    @staticmethod
    def compare_analyzers(api_key: Optional[str] = None):
        """
        Compare rule-based vs LLM accuracy
        
        Args:
            api_key: API key for LLM analyzer
        """
        test_set = Benchmark.create_test_set()
        
        print("=" * 70)
        print("SENTIMENT ANALYZER BENCHMARK")
        print("=" * 70)
        
        # Test rule-based
        print("\n📊 Testing Rule-Based Analyzer...")
        rule_analyzer = Analyzer()
        rule_results = Benchmark.test_accuracy(rule_analyzer, test_set)
        
        print(f"\nAccuracy: {rule_results['accuracy']*100:.1f}%")
        print(f"Correct: {rule_results['correct']}/{rule_results['total']}")
        
        if rule_results['errors']:
            print(f"\nErrors ({len(rule_results['errors'])}):")
            for i, err in enumerate(rule_results['errors'][:5], 1):
                print(f"  {i}. \"{err['text']}\"")
                print(f"     Expected: {err['expected']}, Got: {err['got']} (conf: {err['confidence']:.2f})")
        
        # Test LLM
        try:
            print("\n🧠 Testing LLM Analyzer...")
            llm_analyzer = LLMAnalyzer(api_key=api_key)
            llm_results = Benchmark.test_accuracy(llm_analyzer, test_set)
            
            print(f"\nAccuracy: {llm_results['accuracy']*100:.1f}%")
            print(f"Correct: {llm_results['correct']}/{llm_results['total']}")
            
            if llm_results['errors']:
                print(f"\nErrors ({len(llm_results['errors'])}):")
                for i, err in enumerate(llm_results['errors'][:5], 1):
                    print(f"  {i}. \"{err['text']}\"")
                    print(f"     Expected: {err['expected']}, Got: {err['got']} (conf: {err['confidence']:.2f})")
            
            # Comparison
            print("\n" + "=" * 70)
            print("COMPARISON")
            print("=" * 70)
            print(f"Rule-Based: {rule_results['accuracy']*100:.1f}%")
            print(f"LLM:        {llm_results['accuracy']*100:.1f}%")
            print(f"Improvement: {(llm_results['accuracy']-rule_results['accuracy'])*100:+.1f}%")
            
        except Exception as e:
            print(f"\n⚠️  Could not test LLM: {e}")


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'benchmark':
            Benchmark.compare_analyzers()
        else:
            # Analyze provided text
            text = ' '.join(sys.argv[1:])
            
            print(f"\nText: \"{text}\"\n")
            
            # Rule-based
            result = analyze(text, method='rule')
            print(f"Rule-Based: {result}")
            
            # LLM if available
            try:
                result_llm = analyze(text, method='llm')
                print(f"LLM:        {result_llm}")
                if result_llm.reasoning:
                    print(f"Reasoning:  {result_llm.reasoning}")
            except:
                print("LLM:        (not available)")
    else:
        print("Sentiment Analysis Library v1.0.0")
        print("\nUsage:")
        print("  sentiment <text>           # Analyze text")
        print("  sentiment benchmark        # Run accuracy tests")
        print("\nPython usage:")
        print("  import sentiment")
        print("  result = sentiment.analyze('Amazing!')")
        print("  print(result.category)  # 'positive'")


# CLI for testing
if __name__ == "__main__":
    main()
