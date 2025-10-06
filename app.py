"""
This script extracts all verbs with their precise tense from French text.
It uses spaCy for natural language processing and provides detailed
morphological analysis of verbs.

Author: @plinsy
Date: 2025-10-06
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
from dataclasses import dataclass, asdict
import json

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


def main():
    """Main function to run the verb extraction tool."""
    print("French Verb Extraction and Tense Analysis Tool")
    print("=" * 60)

    # Initialize the extractor
    extractor = FrenchVerbExtractor()

    # Define paths
    data_dir = Path("data")
    input_file = data_dir / "text.txt"
    output_file = Path("verb_analysis_results.json")

    # Check if input file exists
    if not input_file.exists():
        print(f"Input file not found: {input_file}")
        print("Please ensure the text file exists in the data directory.")
        return

    # Extract verbs from file
    verbs = extractor.analyze_file(input_file)

    if verbs:
        # Print summary
        extractor.print_summary(verbs)

        # Save results to JSON
        extractor.save_results(verbs, output_file)

        print(f"\nAnalysis complete! Results saved to {output_file}")
    else:
        print("No verbs were extracted from the text.")


if __name__ == "__main__":
    main()
