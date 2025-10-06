#!/usr/bin/env python3
"""
Test script for the French Verb Extraction Tool

This script demonstrates how to use the VerbExtractor class
with sample French text.
"""

import sys
from pathlib import Path

# Add the current directory to path to import our module
sys.path.append(str(Path(__file__).parent))

try:
    from app import FrenchVerbExtractor
except ImportError as e:
    print(f"❌ Error importing app module: {e}")
    print("Make sure spaCy and the French model are installed.")
    print("Run: python setup.py")
    sys.exit(1)


def test_simple_text():
    """Test with simple French sentences."""
    print("🧪 Testing with simple French text")
    print("-" * 40)

    # Sample French text with various verb tenses
    test_text = """
    Je mange une pomme. Tu mangeais du pain hier. 
    Il mangera demain. Nous avons mangé ce matin.
    Vous auriez mangé si vous aviez eu faim.
    Qu'ils mangent! Il faut que je mange.
    Ayant mangé, il partit. Manger est nécessaire.
    """

    # Initialize extractor
    extractor = FrenchVerbExtractor()

    # Extract verbs
    verbs = extractor.extract_verbs(test_text)

    # Print results
    extractor.print_summary(verbs)

    return verbs


def test_file_analysis():
    """Test with the text file in data directory."""
    print("\n🧪 Testing with data/text.txt")
    print("-" * 40)

    # Initialize extractor
    extractor = FrenchVerbExtractor()

    # Analyze file
    data_file = Path("data") / "text.txt"
    verbs = extractor.analyze_file(data_file)

    if verbs:
        print(f"Found {len(verbs)} verbs in the file.")

        # Show first 10 verbs as example
        print("\n📝 First 10 verbs found:")
        for i, verb in enumerate(verbs[:10], 1):
            print(f"{i:2d}. {verb.text:<12} ({verb.lemma}) - {verb.tense}")

    return verbs


def main():
    """Main test function."""
    print("🚀 French Verb Extraction Tool - Test Suite")
    print("=" * 60)

    try:
        # Test 1: Simple text
        simple_verbs = test_simple_text()

        # Test 2: File analysis
        file_verbs = test_file_analysis()

        print(f"\n✅ Tests completed successfully!")
        print(f"Simple text: {len(simple_verbs)} verbs")
        print(f"File analysis: {len(file_verbs)} verbs")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
