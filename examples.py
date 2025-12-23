"""
Sentimetric - Example Usage with Multi-LLM Support
"""

# Example 1: Basic Usage
def basic_example():
    from sentimetric import analyze

    print("=" * 60)
    print("Example 1: Basic Sentiment Analysis")
    print("=" * 60)
    
    texts = [
        "I love this product! It's amazing! 😍",
        "This is terrible. Waste of money. 😡",
        "It's okay, I guess. Nothing special.",
        "Best purchase ever! Highly recommend! ⭐⭐⭐⭐⭐"
    ]
    
    for text in texts:
        result = analyze(text)
        print(f"\nText: {text}")
        print(f"  Category: {result.category}")
        print(f"  Polarity: {result.polarity:+.2f}")
        print(f"  Confidence: {result.confidence:.2f}")


# Example 2: Modern Slang & Emojis
def slang_example():
    from sentimetric import analyze
    
    print("\n" + "=" * 60)
    print("Example 2: Modern Slang & Emojis")
    print("=" * 60)
    
    modern_texts = [
        "This slaps so hard 🔥🔥🔥",
        "Bro this is sick! Thanks!",
        "Not gonna lie, this is fire",
        "This is insane! OMG thank you!",
        "Bruh that's lit af 💯"
    ]
    
    for text in modern_texts:
        result = analyze(text)
        print(f"\n{text} → {result.category.upper()}")
        print(f"  Polarity: {result.polarity:+.2f}")


# Example 3: Multi-LLM Comparison
def multi_llm_example():
    from sentimetric import LLMAnalyzer, compare_methods
    
    print("\n" + "=" * 60)
    print("Example 3: Multi-LLM Provider Comparison")
    print("=" * 60)
    
    test_texts = [
        "Oh great, another bug 🙄",  # Sarcasm
        "This is actually pretty decent!",  # Positive with qualifier
        "I'm not sure how I feel about this",  # Ambiguous
    ]
    
    # Note: These examples will only work if you have the corresponding API keys
    # and packages installed
    
    providers_to_try = ['openai', 'google', 'anthropic', 'cohere', 'huggingface']
    
    for text in test_texts:
        print(f"\n📝 Text: '{text}'")
        print("-" * 40)
        
        # Try each provider (will fail gracefully if not configured)
        for provider in providers_to_try:
            try:
                analyzer = LLMAnalyzer(provider=provider, model="auto")
                result = analyzer.analyze(text)
                print(f"  {provider.upper():12} → {result.category:8} (conf: {result.confidence:.2f})")
                if result.reasoning:
                    print(f"    Reasoning: {result.reasoning[:60]}...")
            except Exception as e:
                print(f"  {provider.upper():12} → Not configured")


# Example 4: Cost-Aware Features
def cost_aware_example():
    from sentimetric import LLMAnalyzer
    
    print("\n" + "=" * 60)
    print("Example 4: Cost-Aware Model Selection")
    print("=" * 60)
    
    text = "The service was okay but could be better"
    
    print(f"\nText: '{text}'")
    
    # Example 1: Auto-select cheapest model
    print("\n1. Auto-selecting cheapest model:")
    try:
        analyzer = LLMAnalyzer(provider="openai", model="auto")
        result = analyzer.analyze(text)
        print(f"   Model used: {analyzer.model}")
        print(f"   Result: {result.category} (confidence: {result.confidence:.2f})")
    except Exception as e:
        print(f"   OpenAI not configured: {e}")
    
    # Example 2: Fallback to cheaper model
    print("\n2. With fallback to cheaper model:")
    try:
        analyzer = LLMAnalyzer(
            provider="openai", 
            model="gpt-4",  # Expensive model
            fallback_to_cheaper=True
        )
        result = analyzer.analyze(text)
        print(f"   Model used: {analyzer.model}")
        print(f"   Result: {result.category} (method: {result.method})")
    except Exception as e:
        print(f"   OpenAI not configured: {e}")


# Example 5: Batch Processing
def batch_example():
    from sentimetric import analyze_batch, LLMAnalyzer
    
    print("\n" + "=" * 60)
    print("Example 5: Batch Processing")
    print("=" * 60)
    
    texts = [
        "Absolutely love this!",
        "Meh, it's okay",
        "Worst experience ever",
        "Pretty good overall",
        "Not bad at all"
    ]
    
    print("\n1. Rule-based batch analysis (fast):")
    results = analyze_batch(texts, method='rule')
    for i, (text, result) in enumerate(zip(texts, results), 1):
        print(f"   {i}. '{text}' → {result.category}")
    
    print("\n2. LLM batch analysis (accurate, requires API):")
    try:
        analyzer = LLMAnalyzer()
        results = analyzer.analyze_batch(texts, max_workers=3)
        for i, (text, result) in enumerate(zip(texts, results), 1):
            print(f"   {i}. '{text}' → {result.category} (method: {result.method})")
    except Exception as e:
        print(f"   LLM not available: {e}")


if __name__ == "__main__":
    basic_example()
    slang_example()
    multi_llm_example()
    cost_aware_example()
    batch_example()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nNote: LLM examples require:")
    print("  1. Corresponding API keys set as environment variables")
    print("  2. Optional dependencies installed:")
    print("     pip install sentimetric[openai] sentimetric[google] sentimetric[anthropic] sentimetric[cohere] sentimetric[huggingface]")
    print("  or: pip install sentimetric[all]")
