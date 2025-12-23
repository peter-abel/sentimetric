"""
Sentimetric - Example Usage (updated imports)
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


# Other examples similarly updated to import from sentimetric
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


if __name__ == "__main__":
    basic_example()
    slang_example()
