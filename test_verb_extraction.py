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
    from app import FrenchVerbExtractor, BagOfWordsExtractor, FrenchNounPhraseExtractor
except ImportError as e:
    print(f"Error importing app module: {e}")
    print("Make sure spaCy and the French model are installed.")
    print("Run: python setup.py")
    sys.exit(1)


def test_simple_text():
    """Test with simple French sentences."""
    print("Testing with simple French text")
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
    print("\nTesting with data/text.txt")
    print("-" * 40)

    # Initialize extractor
    extractor = FrenchVerbExtractor()

    # Analyze file
    data_file = Path("data") / "text.txt"
    verbs = extractor.analyze_file(data_file)

    if verbs:
        print(f"Found {len(verbs)} verbs in the file.")

        # Show first 10 verbs as example
        print("\nFirst 10 verbs found:")
        for i, verb in enumerate(verbs[:10], 1):
            print(f"{i:2d}. {verb.text:<12} ({verb.lemma}) - {verb.tense}")

    return verbs


def test_bag_of_words_simple():
    """Test Bag-of-Words with simple French text."""
    print("\nTesting Bag-of-Words with simple French text")
    print("-" * 40)

    # Sample French text with various important words
    test_text = """
    L'intelligence artificielle transforme notre société moderne.
    Les algorithmes d'apprentissage automatique analysent des données complexes.
    La technologie numérique révolutionne l'industrie et la santé.
    Les robots intelligents optimisent la production industrielle.
    """

    # Initialize extractor
    extractor = BagOfWordsExtractor()

    # Extract important words
    words = extractor.extract_bag_of_words(test_text, min_frequency=1, max_words=20)

    # Print results
    extractor.print_summary(words)

    return words


def test_bag_of_words_file():
    """Test Bag-of-Words with the main data file."""
    print("\nTesting Bag-of-Words with data file")
    print("-" * 40)

    # Initialize extractor
    extractor = BagOfWordsExtractor()

    # Test with file
    data_file = Path("data/text.txt")
    if data_file.exists():
        words = extractor.analyze_file(data_file, min_frequency=2, max_words=30)
        extractor.print_summary(words)
        return words
    else:
        print(f"Data file not found: {data_file}")
        return []


def test_noun_phrases_simple():
    """Test noun phrase extraction with simple French sentences."""
    print("Testing noun phrase extraction with simple French text")
    print("-" * 40)

    # Sample French text with various noun phrase patterns
    test_text = """
    Le petit chat noir mange la belle pomme rouge.
    Une grande maison blanche se trouve dans le joli jardin fleuri.
    Les étudiants français étudient la grammaire difficile.
    Cette nouvelle voiture rapide appartient au professeur intelligent.
    L'ancienne église gothique du village médiéval est magnifique.
    """

    print(f"Text to analyze: {test_text.strip()}")
    print()

    # Initialize extractor
    extractor = FrenchNounPhraseExtractor()

    # Extract noun phrases
    noun_phrases = extractor.extract_noun_phrases(test_text)

    if noun_phrases:
        print(f"Found {len(noun_phrases)} noun phrases:")
        print("-" * 30)
        for i, np in enumerate(noun_phrases, 1):
            print(f"{i}. '{np.text}' [{np.pattern_type}]")
            print(
                f"   Components: {', '.join(f'{k}: {v}' for k, v in np.components.items())}"
            )
            print()

        # Test saving to JSON
        extractor.save_to_json(noun_phrases, "test_noun_phrases.json")
        print("Results saved to test_noun_phrases.json")
    else:
        print("No noun phrases found in the text.")

    return noun_phrases


def test_noun_phrases_file():
    """Test noun phrase extraction with file analysis."""
    print("Testing noun phrase extraction with file")
    print("-" * 40)

    # Check if test file exists
    test_file = Path("data/text.txt")
    if not test_file.exists():
        print(f"Test file {test_file} not found. Skipping file test.")
        return []

    print(f"Analyzing file: {test_file}")

    # Initialize extractor
    extractor = FrenchNounPhraseExtractor()

    try:
        # Read file content
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"File content length: {len(content)} characters")

        # Extract noun phrases
        noun_phrases = extractor.extract_noun_phrases(content)

        if noun_phrases:
            print(f"Found {len(noun_phrases)} noun phrases in file")

            # Show summary
            extractor.print_summary(noun_phrases)

            # Save results
            extractor.save_to_json(noun_phrases, "test_file_noun_phrases.json")
            print("File analysis results saved to test_file_noun_phrases.json")
        else:
            print("No noun phrases found in the file.")

        return noun_phrases

    except Exception as e:
        print(f"Error analyzing file: {e}")
        return []


def main():
    """Main test function."""
    print("French Text Processing Tool - Test Suite")
    print("=" * 60)

    try:
        # Verb Extraction Tests
        print("\nVERB EXTRACTION TESTS")
        print("=" * 40)

        # Test 1: Simple text
        simple_verbs = test_simple_text()

        # Test 2: File analysis
        file_verbs = test_file_analysis()

        # Bag-of-Words Tests
        print("\n\n💡 BAG-OF-WORDS TESTS")
        print("=" * 40)

        # Test 3: Simple bag-of-words
        simple_words = test_bag_of_words_simple()

        # Test 4: File bag-of-words
        file_words = test_bag_of_words_file()

        # Noun Phrase Tests
        print("\n\n🏛️ NOUN PHRASE EXTRACTION TESTS")
        print("=" * 40)

        # Test 5: Simple noun phrases
        simple_noun_phrases = test_noun_phrases_simple()

        # Test 6: File noun phrases
        file_noun_phrases = test_noun_phrases_file()

        print(f"\nAll tests completed successfully!")
        print("=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Simple text verbs: {len(simple_verbs)}")
        print(f"File verbs: {len(file_verbs)}")
        print(f"Simple text words: {len(simple_words)}")
        print(f"File words: {len(file_words)}")
        print(f"Simple text noun phrases: {len(simple_noun_phrases)}")
        print(f"File noun phrases: {len(file_noun_phrases)}")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
