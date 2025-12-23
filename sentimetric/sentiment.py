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
    LLM-powered sentiment analyzer supporting multiple providers
    
    Good for: Complex emotions, sarcasm, nuanced context, mixed feelings
    Supports: OpenAI, Google Gemini, Anthropic Claude, Cohere, Hugging Face
    
    Example:
        >>> analyzer = LLMAnalyzer(provider="openai", model="gpt-3.5-turbo")
        >>> result = analyzer.analyze("Oh great, another bug 🙄")
        >>> print(result.category)  # 'negative' (catches sarcasm)
    """
    
    # Provider configurations
    PROVIDERS = {
        'openai': {
            'name': 'OpenAI',
            'models': ['gpt-4o', 'gpt-4', 'gpt-3.5-turbo'],
            'cheapest': 'gpt-3.5-turbo',
            'env_var': 'OPENAI_API_KEY',
            'package': 'openai',
            'key_prefix': 'sk-'
        },
        'google': {
            'name': 'Google Gemini',
            'models': ['gemini-1.5-pro', 'gemini-1.5-flash'],
            'cheapest': 'gemini-1.5-flash',
            'env_var': 'GOOGLE_API_KEY',
            'package': 'google-generativeai',
            'key_prefix': None
        },
        'anthropic': {
            'name': 'Anthropic Claude',
            'models': ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-haiku-20240307'],
            'cheapest': 'claude-3-haiku-20240307',
            'env_var': 'ANTHROPIC_API_KEY',
            'package': 'anthropic',
            'key_prefix': 'sk-ant-'
        },
        'cohere': {
            'name': 'Cohere',
            'models': ['command-r-plus', 'command-r', 'command'],
            'cheapest': 'command',
            'env_var': 'COHERE_API_KEY',
            'package': 'cohere',
            'key_prefix': None
        },
        'huggingface': {
            'name': 'Hugging Face',
            'models': ['mistralai/Mixtral-8x7B-Instruct-v0.1', 'meta-llama/Llama-2-70b-chat-hf'],
            'cheapest': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
            'env_var': 'HUGGINGFACE_API_KEY',
            'package': 'huggingface_hub',
            'key_prefix': 'hf_'
        }
    }
    
    def __init__(self, provider: str = "auto", model: str = "auto", 
                 api_key: Optional[str] = None, fallback_to_cheaper: bool = True,
                 config_file: Optional[str] = None):
        """
        Initialize LLM analyzer with multi-provider support
        
        Args:
            provider: LLM provider ('openai', 'google', 'anthropic', 'cohere', 'huggingface', or 'auto')
            model: Model name (provider-specific) or 'auto' for cheapest available
            api_key: API key for the provider (optional, uses multiple resolution methods)
            fallback_to_cheaper: Whether to fall back to cheaper models if requested model fails
            config_file: Optional path to configuration file (JSON, YAML, or .env format)
        """
        import os
        
        self.provider = provider.lower() if provider != "auto" else self._detect_best_provider()
        self.fallback_to_cheaper = fallback_to_cheaper
        self._client_initialized = False
        self._client = None
        self._analyze_func = None
        
        if self.provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(self.PROVIDERS.keys())}")
        
        provider_info = self.PROVIDERS[self.provider]
        
        # Get API key using comprehensive resolution
        self.api_key = self._resolve_api_key(api_key, provider_info, config_file)
        
        # Select model
        if model == "auto":
            self.model = provider_info['cheapest']
        elif model in provider_info['models']:
            self.model = model
        else:
            # Try to use the model anyway (might be a valid model not in our list)
            self.model = model
        
        # Common system prompt
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
    
    def _resolve_api_key(self, api_key: Optional[str], provider_info: dict, config_file: Optional[str]) -> Optional[str]:
        """
        Resolve API key using comprehensive priority order:
        1. Direct api_key parameter (supports multiple formats)
        2. Environment variable
        3. Configuration file
        4. Platform-specific keychain/secure storage
        
        Returns:
            API key if found, None otherwise
        """
        import os
        
        # 1. Direct api_key parameter (supports multiple formats)
        if api_key is not None:
            # Parse API key from different formats
            parsed_key = self._parse_api_key(api_key, provider_info)
            if parsed_key:
                if self._validate_api_key(parsed_key, provider_info):
                    return parsed_key
                else:
                    print(f"Warning: Provided API key for {provider_info['name']} may be invalid")
                    return parsed_key  # Still return it, validation is just a warning
        
        # 2. Environment variable
        env_key = os.getenv(provider_info['env_var'])
        if env_key:
            if self._validate_api_key(env_key, provider_info):
                return env_key
            else:
                print(f"Warning: Environment variable {provider_info['env_var']} may contain invalid API key")
                return env_key
        
        # 3. Configuration file
        config_key = self._get_api_key_from_config(provider_info, config_file)
        if config_key:
            if self._validate_api_key(config_key, provider_info):
                return config_key
            else:
                print(f"Warning: API key from config file for {provider_info['name']} may be invalid")
                return config_key
        
        # 4. Platform-specific keychain (future enhancement)
        # keychain_key = self._get_api_key_from_keychain(provider_info)
        # if keychain_key:
        #     return keychain_key
        
        # No API key found
        return None
    
    def _parse_api_key(self, api_key_input, provider_info: dict) -> Optional[str]:
        """
        Parse API key from different input formats
        
        Supports:
        - Direct string: "sk-abc123"
        - Dictionary: {"openai_api_key": "sk-abc123"} or {"api_key": "sk-abc123"}
        - Provider string: "openai:sk-abc123"
        - File path: "@/path/to/key.txt"
        - JSON string: '{"key": "sk-abc123"}'
        
        Args:
            api_key_input: API key input in various formats
            provider_info: Provider configuration
            
        Returns:
            Parsed API key string or None
        """
        import os
        import json
        
        # If it's already a string, return it
        if isinstance(api_key_input, str):
            # Check if it's a file path (starts with @)
            if api_key_input.startswith('@'):
                file_path = api_key_input[1:]
                try:
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            return f.read().strip()
                except:
                    pass
                return None
            
            # Check if it's a provider:key format
            if ':' in api_key_input and not api_key_input.startswith('sk-'):
                parts = api_key_input.split(':', 1)
                if len(parts) == 2:
                    provider_part, key_part = parts
                    if provider_part.lower() == self.provider:
                        return key_part
            
            # Check if it's a JSON string
            if api_key_input.strip().startswith('{'):
                try:
                    data = json.loads(api_key_input)
                    if isinstance(data, dict):
                        # Try to find the key in the dictionary
                        possible_keys = [
                            provider_info['env_var'].lower(),
                            provider_info['env_var'].lower().replace('_api_key', ''),
                            f"{self.provider}_api_key",
                            self.provider,
                            'api_key',
                            'key'
                        ]
                        for key in possible_keys:
                            if key in data:
                                value = data[key]
                                if isinstance(value, str):
                                    return value
                except:
                    pass
            
            # Return the string as-is
            return api_key_input
        
        # If it's a dictionary
        elif isinstance(api_key_input, dict):
            possible_keys = [
                provider_info['env_var'].lower(),
                provider_info['env_var'].lower().replace('_api_key', ''),
                f"{self.provider}_api_key",
                self.provider,
                'api_key',
                'key'
            ]
            for key in possible_keys:
                if key in api_key_input:
                    value = api_key_input[key]
                    if isinstance(value, str):
                        return value
        
        # If it's None, return None
        elif api_key_input is None:
            return None
        
        # Try to convert to string
        try:
            return str(api_key_input)
        except:
            return None
    
    def _validate_api_key(self, api_key: str, provider_info: dict) -> bool:
        """
        Validate API key format
        
        Args:
            api_key: API key to validate
            provider_info: Provider configuration
            
        Returns:
            True if key appears valid, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        key_prefix = provider_info.get('key_prefix')
        if key_prefix and api_key.startswith(key_prefix):
            return True
        
        # If no specific prefix expected, check basic format
        if len(api_key) >= 10:  # Most API keys are at least 10 characters
            return True
        
        return False
    
    def _get_api_key_from_config(self, provider_info: dict, config_file: Optional[str]) -> Optional[str]:
        """
        Get API key from configuration file
        
        Args:
            provider_info: Provider configuration
            config_file: Optional path to config file
            
        Returns:
            API key if found in config, None otherwise
        """
        import os
        import json
        import yaml
        
        # Try default config file locations if not specified
        config_files_to_try = []
        if config_file:
            config_files_to_try.append(config_file)
        else:
            # Default config file locations
            config_files_to_try.extend([
                '.env',
                'config.json',
                'config.yaml',
                'config.yml',
                '~/.sentimetric/config.json',
                '~/.sentimetric/config.yaml',
            ])
        
        for file_path in config_files_to_try:
            try:
                # Expand user directory
                if file_path.startswith('~'):
                    file_path = os.path.expanduser(file_path)
                
                if not os.path.exists(file_path):
                    continue
                
                # Try to parse based on file extension
                if file_path.endswith('.json'):
                    with open(file_path, 'r') as f:
                        config = json.load(f)
                    
                    # Look for API key in various possible locations
                    possible_keys = [
                        provider_info['env_var'].lower(),
                        provider_info['env_var'].lower().replace('_api_key', ''),
                        f"{self.provider}_api_key",
                        self.provider,
                        'api_key'
                    ]
                    
                    for key in possible_keys:
                        if key in config:
                            return str(config[key])
                
                elif file_path.endswith(('.yaml', '.yml')):
                    try:
                        with open(file_path, 'r') as f:
                            config = yaml.safe_load(f)
                        
                        if config:
                            possible_keys = [
                                provider_info['env_var'].lower(),
                                provider_info['env_var'].lower().replace('_api_key', ''),
                                f"{self.provider}_api_key",
                                self.provider,
                                'api_key'
                            ]
                            
                            for key in possible_keys:
                                if key in config:
                                    return str(config[key])
                    except ImportError:
                        # yaml not installed
                        pass
                
                elif file_path.endswith('.env') or os.path.basename(file_path) == '.env':
                    # Parse .env file
                    with open(file_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if '=' in line:
                                    key, value = line.split('=', 1)
                                    key = key.strip()
                                    value = value.strip().strip('"\'')
                                    
                                    if key == provider_info['env_var']:
                                        return value
                
            except Exception as e:
                # Silently continue to next config file
                continue
        
        return None
    
    def _detect_best_provider(self) -> str:
        """Detect the best available provider based on environment variables"""
        import os
        
        # Check for API keys in environment
        for provider, info in self.PROVIDERS.items():
            if os.getenv(info['env_var']):
                return provider
        
        # If no API keys found, check for installed packages
        for provider, info in self.PROVIDERS.items():
            try:
                __import__(info['package'].replace('-', '_'))
                return provider
            except ImportError:
                continue
        
        # Default to anthropic if nothing else (backward compatibility)
        return 'anthropic'
    
    def _init_provider_client(self):
        """Initialize provider-specific client (lazy initialization)"""
        if self._client_initialized:
            return
        
        # Check if API key is available
        if not self.api_key:
            provider_info = self.PROVIDERS[self.provider]
            raise ValueError(
                f"{provider_info['name']} API key required. Available options:\n"
                f"  1. Pass api_key parameter: LLMAnalyzer(provider='{self.provider}', api_key='your-key')\n"
                f"  2. Set environment variable: export {provider_info['env_var']}='your-key'\n"
                f"  3. Create a config file (.env, config.json, or config.yaml) with the key\n"
                f"  4. Use a configuration file: LLMAnalyzer(config_file='path/to/config.yaml')\n\n"
                f"Example with API key:\n"
                f"  analyzer = LLMAnalyzer(provider='{self.provider}', api_key='your-key-here')"
            )
        
        try:
            if self.provider == 'openai':
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
                self._analyze_func = self._analyze_openai
                
            elif self.provider == 'google':
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai
                self._analyze_func = self._analyze_google
                
            elif self.provider == 'anthropic':
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
                self._analyze_func = self._analyze_anthropic
                
            elif self.provider == 'cohere':
                import cohere
                self._client = cohere.Client(self.api_key)
                self._analyze_func = self._analyze_cohere
                
            elif self.provider == 'huggingface':
                from huggingface_hub import InferenceClient
                self._client = InferenceClient(token=self.api_key)
                self._analyze_func = self._analyze_huggingface
                
            self._client_initialized = True
            
        except ImportError as e:
            raise ImportError(
                f"Package required for {self.PROVIDERS[self.provider]['name']}: "
                f"pip install {self.PROVIDERS[self.provider]['package']}\n"
                f"Or install all LLM providers: pip install sentimetric[all]"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize {self.provider} client: {e}")
    
    @property
    def client(self):
        """Lazy client access - initializes client if needed"""
        if not self._client_initialized:
            self._init_provider_client()
        return self._client
    
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
        
        # Ensure client is initialized
        if not self._client_initialized:
            self._init_provider_client()
        
        try:
            return self._analyze_func(text)
        except Exception as e:
            # Try fallback to cheaper model if enabled
            if self.fallback_to_cheaper and self.model != self.PROVIDERS[self.provider]['cheapest']:
                print(f"Model {self.model} failed: {e}. Trying cheaper model...")
                original_model = self.model
                self.model = self.PROVIDERS[self.provider]['cheapest']
                try:
                    # Re-initialize client with new model if needed
                    if self.provider in ['openai', 'anthropic', 'cohere', 'huggingface']:
                        self._client_initialized = False
                        self._init_provider_client()
                    
                    result = self._analyze_func(text)
                    result.method = f'llm_fallback({original_model}->{self.model})'
                    return result
                except Exception as e2:
                    print(f"Cheaper model also failed: {e2}")
            
            # Fallback to rule-based analysis
            print(f"LLM error: {e}. Falling back to rule-based analysis.")
            analyzer = Analyzer()
            result = analyzer.analyze(text)
            result.method = 'rule_based_fallback'
            return result
    
    def _analyze_openai(self, text: str) -> SentimentResult:
        """Analyze using OpenAI"""
        import json
        
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Analyze: {text}"}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        content = content.replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        
        return self._create_result(data)
    
    def _analyze_google(self, text: str) -> SentimentResult:
        """Analyze using Google Gemini"""
        import json
        
        model = self._client.GenerativeModel(self.model)
        response = model.generate_content(
            f"{self.system_prompt}\n\nAnalyze: {text}",
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 500,
            }
        )
        
        content = response.text.strip()
        content = content.replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        
        return self._create_result(data)
    
    def _analyze_anthropic(self, text: str) -> SentimentResult:
        """Analyze using Anthropic Claude"""
        import json
        
        response = self._client.messages.create(
            model=self.model,
            max_tokens=500,
            system=self.system_prompt,
            messages=[{"role": "user", "content": f"Analyze: {text}"}]
        )
        
        content = response.content[0].text.strip()
        content = content.replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        
        return self._create_result(data)
    
    def _analyze_cohere(self, text: str) -> SentimentResult:
        """Analyze using Cohere"""
        import json
        
        response = self._client.chat(
            model=self.model,
            message=f"Analyze: {text}",
            preamble=self.system_prompt,
            temperature=0.1,
            max_tokens=500
        )
        
        content = response.text.strip()
        content = content.replace('```json', '').replace('```', '').strip()
        data = json.loads(content)
        
        return self._create_result(data)
    
    def _analyze_huggingface(self, text: str) -> SentimentResult:
        """Analyze using Hugging Face"""
        import json
        
        prompt = f"{self.system_prompt}\n\nAnalyze: {text}"
        response = self._client.text_generation(
            prompt,
            model=self.model,
            max_new_tokens=500,
            temperature=0.1
        )
        
        # Extract JSON from response
        content = response.strip()
        # Try to find JSON in the response
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            content = content[start_idx:end_idx]
        
        data = json.loads(content)
        
        return self._create_result(data)
    
    def _create_result(self, data: dict) -> SentimentResult:
        """Create SentimentResult from provider response"""
        return SentimentResult(
            polarity=float(data.get('polarity', 0.0)),
            category=data.get('category', 'neutral'),
            confidence=float(data.get('confidence', 0.5)),
            subjectivity=0.8,  # LLM analyses are inherently subjective
            method=f'llm_{self.provider}',
            reasoning=data.get('reasoning'),
            emotions=data.get('emotions'),
            tone=data.get('tone')
        )
    
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
