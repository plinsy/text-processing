# Text Processing Tasks

## ✅ Completed Tasks

### 1. Verb Extraction with Precise Tense Analysis
- [x] Extraire tous les verbes, préciser leurs temps: Infinitif, Présent de l'indicatif, etc…
- **Implementation**: `app.py` - Comprehensive French verb extraction tool
- **Features**:
  - Extracts all verbs with precise tense identification
  - Supports all French tenses (Indicatif, Subjonctif, Conditionnel, Impératif, etc.)
  - Provides morphological analysis (person, number, voice)
  - Includes sentence context for each verb
  - Outputs results in JSON format

## 🔄 Pending Tasks

### 2. Bag-of-Words Extraction
- [ ] Extraire tous les mots qui sont considérés comme importants dans le texte sans redondance (Bag-of-words)

### 3. Noun Phrase Extraction  
- [ ] Extraire tous les groupes nominaux: Considérez les formes simples et moyennes: article + nom, article + nom + adjectif attribut, article + adjectif épithète + nom, article + adjectif épithète + nom + adjectif attribut (Utiliser exclusivement Spacy [Tips: Rule-Based Matching])

## 🚀 Getting Started

### Setup
1. Install dependencies: `python setup.py`
2. Run the main script: `python app.py`
3. Run tests: `python test_verb_extraction.py`

### Files Structure
- `app.py` - Main verb extraction tool
- `setup.py` - Dependency installation script
- `test_verb_extraction.py` - Test suite
- `requirements.txt` - Python dependencies
- `data/text.txt` - Input text file
- `verb_analysis_results.json` - Output results (generated)xtraire tous les verbes, préciser leurs temps: Infinitif, Présent de l’indicatif, etc…
- Extraire tous les mots qui sont considérés comme importants dans le texte sans redondance (Bag-of-words)
- Extraire tous les groupes nominaux: Considérez les formes simples et moyennes: article + nom, article + nom + adjectif attribut, article + adjectif épithète + nom, article + adjectif épithète + nom + adjectif attribut (Utiliser exclusivement Spacy [Tips: Rule-Based Matching])
