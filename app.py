"""
This script extracts all verbs with their precise tense from French text
and implements Bag-of-Words extraction for important terms.
It uses spaCy for natural language processing and provides detailed
morphological analysis of verbs and important word extraction.

Author: @plinsy
Date: 2025-10-07
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import logging
from dataclasses import dataclass, asdict
import json
from collections import Counter
import re

try:
    import spacy
    from spacy.tokens import Token
except ImportError:
    print("spaCy is not installed. Please run: pip install spacy")
    print("Also download the French model: python -m spacy download fr_core_news_sm")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("verb_extraction.log"), logging.StreamHandler()],
)


@dataclass
class VerbInfo:
    """Data class to store verb information."""

    text: str
    lemma: str
    pos: str
    tag: str
    tense: str
    mood: str
    person: Optional[str]
    number: Optional[str]
    voice: Optional[str]
    sentence_context: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ImportantWord:
    """Data class to store important word information."""

    text: str
    lemma: str
    pos: str
    frequency: int
    importance_score: float
    context_examples: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class FrenchVerbExtractor:
    """
    A comprehensive French verb extractor that identifies verbs and their tenses.

    This class uses spaCy's French language model to perform morphological
    analysis and extract detailed information about verbs in French text.
    """

    # French tense mappings based on spaCy tags
    TENSE_MAPPINGS = {
        "Ind": "Indicatif",
        "Cnd": "Conditionnel",
        "Sub": "Subjonctif",
        "Imp": "Impératif",
        "Part": "Participe",
        "Inf": "Infinitif",
    }

    DETAILED_TENSE_MAPPINGS = {
        "Pres": "Présent",
        "Imp": "Imparfait",
        "Past": "Passé Simple",
        "Fut": "Futur",
        "Cnd": "Conditionnel",
    }

    def __init__(self, model_name: str = "fr_core_news_sm"):
        """
        Initialize the verb extractor.

        Args:
            model_name: Name of the spaCy French model to use
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.nlp = self._load_model()

    def _load_model(self) -> spacy.language.Language:
        """Load the spaCy French model."""
        try:
            nlp = spacy.load(self.model_name)
            self.logger.info(f"Successfully loaded spaCy model: {self.model_name}")
            return nlp
        except OSError:
            self.logger.error(f"Model '{self.model_name}' not found.")
            self.logger.error(
                "Please install it with: python -m spacy download fr_core_news_sm"
            )
            sys.exit(1)

    def _parse_morphology(self, token: Token) -> Dict[str, str]:
        """
        Parse morphological features from spaCy token.

        Args:
            token: spaCy token object

        Returns:
            Dictionary containing morphological features
        """
        morph_dict = {}

        if token.morph:
            for feature in token.morph:
                key, value = feature.split("=", 1)
                morph_dict[key] = value

        return morph_dict

    def _determine_tense(self, token: Token, morph_features: Dict[str, str]) -> str:
        """
        Determine the precise tense of a verb.

        Args:
            token: spaCy token object
            morph_features: Morphological features dictionary

        Returns:
            String describing the verb tense
        """
        mood = morph_features.get("Mood", "")
        tense = morph_features.get("Tense", "")
        aspect = morph_features.get("Aspect", "")

        # Handle different moods and tenses
        if mood == "Ind":  # Indicative
            if tense == "Pres":
                return "Indicatif Présent"
            elif tense == "Imp":
                return "Indicatif Imparfait"
            elif tense == "Past":
                return "Indicatif Passé Simple"
            elif tense == "Fut":
                return "Indicatif Futur"
            else:
                return f"Indicatif {tense}" if tense else "Indicatif"

        elif mood == "Cnd":  # Conditional
            return "Conditionnel"

        elif mood == "Sub":  # Subjunctive
            if tense == "Pres":
                return "Subjonctif Présent"
            elif tense == "Imp":
                return "Subjonctif Imparfait"
            else:
                return f"Subjonctif {tense}" if tense else "Subjonctif"

        elif mood == "Imp":  # Imperative
            return "Impératif"

        elif token.tag_ == "VINF":  # Infinitive
            return "Infinitif"

        elif token.tag_.startswith("VPP"):  # Past Participle
            return "Participe Passé"

        elif token.tag_.startswith("VPR"):  # Present Participle
            return "Participe Présent"

        # Fallback using tag information
        if "VINF" in token.tag_:
            return "Infinitif"
        elif "VPP" in token.tag_:
            return "Participe Passé"
        elif "VPR" in token.tag_:
            return "Participe Présent"

        return f"Temps non identifié ({token.tag_})"

    def _get_sentence_context(self, token: Token, window: int = 10) -> str:
        """
        Get sentence context around the verb.

        Args:
            token: spaCy token object
            window: Number of words before and after the token

        Returns:
            String containing the sentence context
        """
        doc = token.doc
        start = max(0, token.i - window)
        end = min(len(doc), token.i + window + 1)

        context_tokens = []
        for i in range(start, end):
            if i == token.i:
                context_tokens.append(f"**{doc[i].text}**")
            else:
                context_tokens.append(doc[i].text)

        return " ".join(context_tokens)

    def extract_verbs(self, text: str) -> List[VerbInfo]:
        """
        Extract all verbs with their tense information from text.

        Args:
            text: Input text to analyze

        Returns:
            List of VerbInfo objects containing verb details
        """
        self.logger.info("Starting verb extraction...")

        # Process text with spaCy
        doc = self.nlp(text)
        verbs = []

        for token in doc:
            # Check if token is a verb
            if token.pos_ == "VERB" or token.pos_ == "AUX":
                morph_features = self._parse_morphology(token)

                # Determine precise tense
                tense = self._determine_tense(token, morph_features)

                # Extract other morphological information
                mood = morph_features.get("Mood", "Non spécifié")
                person = morph_features.get("Person", None)
                number = morph_features.get("Number", None)
                voice = morph_features.get("Voice", None)

                # Get sentence context
                context = self._get_sentence_context(token)

                verb_info = VerbInfo(
                    text=token.text,
                    lemma=token.lemma_,
                    pos=token.pos_,
                    tag=token.tag_,
                    tense=tense,
                    mood=mood,
                    person=person,
                    number=number,
                    voice=voice,
                    sentence_context=context,
                )

                verbs.append(verb_info)

        self.logger.info(f"Found {len(verbs)} verbs in the text")
        return verbs

    def analyze_file(self, file_path: Path) -> List[VerbInfo]:
        """
        Analyze verbs in a text file.

        Args:
            file_path: Path to the text file

        Returns:
            List of VerbInfo objects
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            self.logger.info(f"Analyzing file: {file_path}")
            return self.extract_verbs(text)

        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            return []
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return []

    def save_results(self, verbs: List[VerbInfo], output_file: Path) -> None:
        """
        Save verb analysis results to a JSON file.

        Args:
            verbs: List of VerbInfo objects
            output_file: Output file path
        """
        try:
            data = [verb.to_dict() for verb in verbs]

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            self.logger.info(f"Results saved to: {output_file}")

        except Exception as e:
            self.logger.error(f"Error saving results: {e}")

    def print_summary(self, verbs: List[VerbInfo]) -> None:
        """
        Print a summary of verb analysis results.

        Args:
            verbs: List of VerbInfo objects
        """
        if not verbs:
            print("No verbs found in the text.")
            return

        print(f"\nVERB ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Total verbs found: {len(verbs)}")

        # Count verbs by tense
        tense_counts = {}
        for verb in verbs:
            tense_counts[verb.tense] = tense_counts.get(verb.tense, 0) + 1

        print("\nVerbs by Tense:")
        for tense, count in sorted(tense_counts.items()):
            print(f"  • {tense}: {count}")

        print("\nDetailed Verb List:")
        print("-" * 60)

        for i, verb in enumerate(verbs, 1):
            print(f"{i:2d}. {verb.text:<15} | {verb.lemma:<15} | {verb.tense}")
            if verb.person or verb.number:
                details = []
                if verb.person:
                    details.append(f"Personne: {verb.person}")
                if verb.number:
                    details.append(f"Nombre: {verb.number}")
                print(f"    └── {' | '.join(details)}")
            print(f"    Context: ...{verb.sentence_context[:60]}...")
            print()


class BagOfWordsExtractor:
    """
    A comprehensive Bag-of-Words extractor that identifies important terms
    in French text without redundancy.

    This class uses spaCy for natural language processing and implements
    various filtering strategies to extract meaningful words.
    """

    # French stop words (common words to exclude)
    FRENCH_STOP_WORDS = {
        "le",
        "de",
        "un",
        "à",
        "être",
        "et",
        "en",
        "avoir",
        "que",
        "pour",
        "dans",
        "ce",
        "il",
        "une",
        "sur",
        "avec",
        "ne",
        "se",
        "pas",
        "tout",
        "plus",
        "par",
        "grand",
        "ce",
        "comme",
        "mais",
        "du",
        "des",
        "les",
        "au",
        "aux",
        "la",
        "cette",
        "ces",
        "son",
        "sa",
        "ses",
        "leur",
        "leurs",
        "mon",
        "ma",
        "mes",
        "ton",
        "ta",
        "tes",
        "notre",
        "nos",
        "votre",
        "vos",
        "je",
        "tu",
        "nous",
        "vous",
        "ils",
        "elles",
        "qui",
        "quoi",
        "où",
        "quand",
        "comment",
        "pourquoi",
        "dont",
        "si",
        "car",
        "donc",
        "or",
        "ni",
        "mais",
        "ou",
        "et",
        "aussi",
        "très",
        "bien",
        "encore",
        "déjà",
        "toujours",
        "jamais",
        "souvent",
        "parfois",
        "puis",
        "alors",
        "ainsi",
        "donc",
        "cependant",
        "néanmoins",
        "toutefois",
        "pourtant",
        "malgré",
        "grâce",
        "selon",
        "pendant",
        "durant",
        "après",
        "avant",
        "depuis",
        "jusqu",
        "vers",
        "chez",
        "sans",
        "sous",
        "entre",
        "parmi",
        "contre",
        "malgré",
        "sauf",
        "except",
    }

    # Important POS tags for content words
    IMPORTANT_POS = {"NOUN", "ADJ", "VERB", "ADV", "PROPN"}

    def __init__(self, model_name: str = "fr_core_news_sm"):
        """
        Initialize the Bag-of-Words extractor.

        Args:
            model_name: Name of the spaCy French model to use
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.nlp = self._load_model()

    def _load_model(self) -> spacy.language.Language:
        """Load the spaCy French model."""
        try:
            nlp = spacy.load(self.model_name)
            self.logger.info(f"Successfully loaded spaCy model: {self.model_name}")
            return nlp
        except OSError:
            self.logger.error(f"Model '{self.model_name}' not found.")
            self.logger.error(
                "Please install it with: python -m spacy download fr_core_news_sm"
            )
            sys.exit(1)

    def _is_important_word(self, token) -> bool:
        """
        Determine if a token represents an important word.

        Args:
            token: spaCy token object

        Returns:
            Boolean indicating if the word is important
        """
        # Skip if it's a stop word
        if token.lemma_.lower() in self.FRENCH_STOP_WORDS:
            return False

        # Skip if it's punctuation, space, or symbol
        if token.is_punct or token.is_space or token.pos_ in {"PUNCT", "SPACE", "SYM"}:
            return False

        # Skip very short words (less than 3 characters)
        if len(token.text) < 3:
            return False

        # Skip if it's a number or contains only digits
        if token.like_num or token.text.isdigit():
            return False

        # Only keep words with important POS tags
        if token.pos_ not in self.IMPORTANT_POS:
            return False

        # Skip words that are mostly punctuation or special characters
        if not re.search(r"[a-zA-ZàâäéèêëîïôöùûüÿçÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÇ]", token.text):
            return False

        return True

    def _calculate_importance_score(
        self, word_data: Dict, total_words: int, doc_length: int
    ) -> float:
        """
        Calculate importance score based on frequency and other factors.

        Args:
            word_data: Dictionary containing word information
            total_words: Total number of important words
            doc_length: Total length of document

        Returns:
            Float representing importance score
        """
        frequency = word_data["frequency"]

        # TF (Term Frequency) - normalized by document length
        tf = frequency / doc_length

        # Simple importance score based on frequency and length
        # Longer words tend to be more meaningful
        length_bonus = min(len(word_data["lemma"]) / 10, 1.0)

        # POS bonus - nouns and proper nouns are generally more important
        pos_bonus = 1.0
        if word_data["pos"] == "PROPN":  # Proper nouns
            pos_bonus = 1.5
        elif word_data["pos"] == "NOUN":  # Common nouns
            pos_bonus = 1.3
        elif word_data["pos"] == "ADJ":  # Adjectives
            pos_bonus = 1.1
        elif word_data["pos"] == "VERB":  # Verbs
            pos_bonus = 1.0

        # Calculate final score
        importance_score = tf * length_bonus * pos_bonus

        return round(importance_score, 4)

    def _get_context_examples(
        self, lemma: str, doc, max_examples: int = 3
    ) -> List[str]:
        """
        Get context examples for a word.

        Args:
            lemma: The lemmatized form of the word
            doc: spaCy document object
            max_examples: Maximum number of context examples

        Returns:
            List of context strings
        """
        examples = []
        found = 0

        for token in doc:
            if found >= max_examples:
                break

            if token.lemma_.lower() == lemma.lower():
                # Get surrounding context
                sent_start = token.sent.start
                sent_end = token.sent.end

                # Extract sentence and highlight the word
                sentence_tokens = []
                for i in range(sent_start, sent_end):
                    if i == token.i:
                        sentence_tokens.append(f"**{doc[i].text}**")
                    else:
                        sentence_tokens.append(doc[i].text)

                context = " ".join(sentence_tokens)
                examples.append(context)
                found += 1

        return examples

    def extract_bag_of_words(
        self, text: str, min_frequency: int = 1, max_words: Optional[int] = None
    ) -> List[ImportantWord]:
        """
        Extract important words (Bag-of-Words) from text without redundancy.

        Args:
            text: Input text to analyze
            min_frequency: Minimum frequency for a word to be included
            max_words: Maximum number of words to return (None for no limit)

        Returns:
            List of ImportantWord objects containing word details
        """
        self.logger.info("Starting Bag-of-Words extraction...")

        # Process text with spaCy
        doc = self.nlp(text)

        # Dictionary to store word information by lemma
        word_data = {}

        # Extract important words
        for token in doc:
            if self._is_important_word(token):
                lemma = token.lemma_.lower()

                if lemma not in word_data:
                    word_data[lemma] = {
                        "text": token.text,
                        "lemma": token.lemma_,
                        "pos": token.pos_,
                        "frequency": 0,
                        "tokens": [],
                    }

                word_data[lemma]["frequency"] += 1
                word_data[lemma]["tokens"].append(token)

        # Filter by minimum frequency
        filtered_words = {
            k: v for k, v in word_data.items() if v["frequency"] >= min_frequency
        }

        # Calculate importance scores
        doc_length = len([token for token in doc if not token.is_space])
        important_words = []

        for lemma, data in filtered_words.items():
            importance_score = self._calculate_importance_score(
                data, len(filtered_words), doc_length
            )
            context_examples = self._get_context_examples(lemma, doc)

            important_word = ImportantWord(
                text=data["text"],
                lemma=data["lemma"],
                pos=data["pos"],
                frequency=data["frequency"],
                importance_score=importance_score,
                context_examples=context_examples,
            )

            important_words.append(important_word)

        # Sort by importance score (descending)
        important_words.sort(key=lambda x: x.importance_score, reverse=True)

        # Limit number of words if specified
        if max_words:
            important_words = important_words[:max_words]

        self.logger.info(f"Found {len(important_words)} important words in the text")
        return important_words

    def analyze_file(
        self, file_path: Path, min_frequency: int = 1, max_words: Optional[int] = None
    ) -> List[ImportantWord]:
        """
        Analyze important words in a text file.

        Args:
            file_path: Path to the text file
            min_frequency: Minimum frequency for a word to be included
            max_words: Maximum number of words to return

        Returns:
            List of ImportantWord objects
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            self.logger.info(f"Analyzing file for Bag-of-Words: {file_path}")
            return self.extract_bag_of_words(text, min_frequency, max_words)

        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            return []
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return []

    def save_results(self, words: List[ImportantWord], output_file: Path) -> None:
        """
        Save Bag-of-Words analysis results to a JSON file.

        Args:
            words: List of ImportantWord objects
            output_file: Output file path
        """
        try:
            data = [word.to_dict() for word in words]

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            self.logger.info(f"Bag-of-Words results saved to: {output_file}")

        except Exception as e:
            self.logger.error(f"Error saving Bag-of-Words results: {e}")

    def print_summary(self, words: List[ImportantWord]) -> None:
        """
        Print a summary of Bag-of-Words analysis results.

        Args:
            words: List of ImportantWord objects
        """
        if not words:
            print("No important words found in the text.")
            return

        print(f"\nBAG-OF-WORDS ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Total important words found: {len(words)}")

        # Count words by POS
        pos_counts = {}
        for word in words:
            pos_counts[word.pos] = pos_counts.get(word.pos, 0) + 1

        print("\nWords by Part-of-Speech:")
        for pos, count in sorted(pos_counts.items()):
            pos_name = {
                "NOUN": "Noms",
                "ADJ": "Adjectifs",
                "VERB": "Verbes",
                "ADV": "Adverbes",
                "PROPN": "Noms propres",
            }.get(pos, pos)
            print(f"  • {pos_name}: {count}")

        print("\nTop Important Words (by importance score):")
        print("-" * 60)

        for i, word in enumerate(words[:20], 1):  # Show top 20
            print(
                f"{i:2d}. {word.text:<20} | {word.lemma:<20} | Score: {word.importance_score:<6}"
            )
            print(f"    Fréquence: {word.frequency} | POS: {word.pos}")
            if word.context_examples:
                print(f"    Exemple: {word.context_examples[0][:80]}...")
            print()


def main():
    """Main function to run the text processing tools."""
    print("French Text Processing Suite")
    print("=" * 60)
    print("1. Verb Extraction with Tense Analysis")
    print("2. Bag-of-Words Extraction")
    print("=" * 60)

    # Define paths
    data_dir = Path("data")
    input_file = data_dir / "text.txt"
    verb_output_file = Path("verb_analysis_results.json")
    bow_output_file = Path("bag_of_words_results.json")

    # Check if input file exists
    if not input_file.exists():
        print(f"Input file not found: {input_file}")
        print("Please ensure the text file exists in the data directory.")
        return

    # Initialize extractors
    verb_extractor = FrenchVerbExtractor()
    bow_extractor = BagOfWordsExtractor()

    # 1. Verb Extraction
    print("\nSTARTING VERB EXTRACTION...")
    print("-" * 40)
    verbs = verb_extractor.analyze_file(input_file)

    if verbs:
        verb_extractor.print_summary(verbs)
        verb_extractor.save_results(verbs, verb_output_file)
        print(f"Verb analysis complete! Results saved to {verb_output_file}")
    else:
        print("No verbs were extracted from the text.")

    # 2. Bag-of-Words Extraction
    print("\n\nSTARTING BAG-OF-WORDS EXTRACTION...")
    print("-" * 40)
    important_words = bow_extractor.analyze_file(
        input_file, min_frequency=1, max_words=50
    )

    if important_words:
        bow_extractor.print_summary(important_words)
        bow_extractor.save_results(important_words, bow_output_file)
        print(f"Bag-of-Words analysis complete! Results saved to {bow_output_file}")
    else:
        print("No important words were extracted from the text.")

    # Final summary
    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Input file: {input_file}")
    print(f"Verbs extracted: {len(verbs) if verbs else 0}")
    print(
        f"Important words extracted: {len(important_words) if important_words else 0}"
    )
    print(f"Verb results: {verb_output_file}")
    print(f"Bag-of-Words results: {bow_output_file}")
    print("\nAll analyses completed successfully!")


if __name__ == "__main__":
    main()
