# French Verb Extraction and Tense Analysis Tool

A comprehensive Python script that extracts all verbs with their precise tense from French text using advanced Natural Language Processing techniques.

## 🌟 Features

- **Comprehensive Verb Detection**: Identifies all verbs (main verbs and auxiliary verbs)
- **Precise Tense Analysis**: Determines exact tense for each verb including:
  - Indicatif (Présent, Imparfait, Passé Simple, Futur)
  - Subjonctif (Présent, Imparfait)
  - Conditionnel
  - Impératif
  - Infinitif
  - Participe (Présent, Passé)
- **Morphological Analysis**: Extracts person, number, voice information
- **Context Preservation**: Includes sentence context for each verb
- **Multiple Output Formats**: Console display and JSON export
- **Robust Error Handling**: Comprehensive logging and error management
- **Best Coding Practices**: Clean, documented, and maintainable code

## 📋 Requirements

- Python 3.8+
- spaCy >= 3.7.0
- French language model (fr_core_news_sm)

## 🚀 Quick Start

### 1. Installation

Run the setup script to install all dependencies:

```bash
python setup.py
```

This will automatically:
- Install spaCy and required packages
- Download the French language model

### 2. Manual Installation (Alternative)

```bash
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
```

### 3. Usage

#### Basic Usage
```bash
python app.py
```

This will analyze the text in `data/text.txt` and display results.

#### Test the Tool
```bash
python test_verb_extraction.py
```

## 📖 Code Structure

### Main Classes

#### `VerbInfo`
Data class that stores comprehensive verb information:
- `text`: Original verb form
- `lemma`: Base form of the verb
- `tense`: Precise tense identification
- `mood`: Grammatical mood
- `person`: Grammatical person (1st, 2nd, 3rd)
- `number`: Singular/Plural
- `voice`: Active/Passive
- `sentence_context`: Surrounding text context

#### `FrenchVerbExtractor`
Main class for verb extraction and analysis:

```python
from app import FrenchVerbExtractor

# Initialize the extractor
extractor = FrenchVerbExtractor()

# Extract verbs from text
verbs = extractor.extract_verbs("Je mange une pomme.")

# Analyze a file
verbs = extractor.analyze_file(Path("data/text.txt"))

# Print summary
extractor.print_summary(verbs)

# Save results
extractor.save_results(verbs, Path("results.json"))
```

### Key Methods

- `extract_verbs(text: str)`: Extract verbs from text string
- `analyze_file(file_path: Path)`: Analyze verbs in a text file
- `print_summary(verbs: List[VerbInfo])`: Display analysis results
- `save_results(verbs: List[VerbInfo], output_file: Path)`: Save to JSON

## 🎯 Example Output

```
📊 VERB ANALYSIS SUMMARY
============================================================
Total verbs found: 45

🎯 Verbs by Tense:
  • Indicatif Présent: 18
  • Infinitif: 12
  • Indicatif Imparfait: 6
  • Participe Passé: 5
  • Conditionnel: 3
  • Subjonctif Présent: 1

📝 Detailed Verb List:
------------------------------------------------------------
 1. est            | être           | Indicatif Présent
    └── Personne: 3 | Nombre: Sing
    Context: ...L'intelligence artificielle (IA) **est** aujourd'hui au cœur de nombreuses...

 2. fait           | faire          | Indicatif Présent
    └── Personne: 3 | Nombre: Sing
    Context: ...nos sociétés, que ce soit dans le domaine de la santé...
```

## 🔧 Configuration

### Custom spaCy Model
```python
extractor = FrenchVerbExtractor(model_name="fr_core_news_md")
```

### Custom Logging
The tool uses Python's logging module. Logs are saved to `verb_extraction.log`.

## 📁 File Structure

```
text-processing/
├── app.py                      # Main extraction tool
├── setup.py                    # Dependency installer
├── test_verb_extraction.py     # Test suite
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── TODO.md                     # Project tasks
├── data/
│   └── text.txt               # Input text file
├── verb_analysis_results.json  # Output results (generated)
└── verb_extraction.log         # Log file (generated)
```

## 🧪 Testing

The project includes comprehensive tests:

```bash
python test_verb_extraction.py
```

Tests include:
- Simple French sentences with various tenses
- Analysis of the provided text file
- Error handling verification

## 🔍 Advanced Usage

### Batch Processing
```python
from pathlib import Path
from app import FrenchVerbExtractor

extractor = FrenchVerbExtractor()
text_files = Path("texts").glob("*.txt")

for file_path in text_files:
    verbs = extractor.analyze_file(file_path)
    output_file = file_path.with_suffix(".json")
    extractor.save_results(verbs, output_file)
```

### Custom Analysis
```python
# Extract specific information
verbs = extractor.extract_verbs(text)
present_tense_verbs = [v for v in verbs if "Présent" in v.tense]
infinitive_verbs = [v for v in verbs if v.tense == "Infinitif"]
```

## 🐛 Troubleshooting

### Common Issues

1. **spaCy model not found**
   ```
   python -m spacy download fr_core_news_sm
   ```

2. **Permission errors on Windows**
   - Run PowerShell as Administrator
   - Or use: `pip install --user -r requirements.txt`

3. **Encoding issues**
   - Ensure text files are saved in UTF-8 encoding

## 🤝 Contributing

Feel free to contribute by:
- Adding support for more tenses
- Improving tense detection accuracy
- Adding new features
- Reporting bugs

## 📄 License

This project is available for educational and research purposes.

## 🏆 Best Practices Implemented

- **Clean Code**: Well-structured, readable code with clear naming
- **Documentation**: Comprehensive docstrings and comments
- **Error Handling**: Robust exception handling and logging
- **Type Hints**: Full type annotation for better code clarity
- **Modular Design**: Separate concerns with classes and methods
- **Testing**: Included test suite for validation
- **Configuration**: Flexible configuration options
- **Logging**: Comprehensive logging for debugging and monitoring
