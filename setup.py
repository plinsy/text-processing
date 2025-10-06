#!/usr/bin/env python3
"""
Setup script for the French Verb Extraction Tool

This script installs all necessary dependencies including spaCy
and the French language model.
"""

import subprocess
import sys


def run_command(command: str):
    """Run a shell command and handle errors."""
    try:
        print(f"Running: {command}")
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.output}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up French Verb Extraction Tool")
    print("=" * 50)

    # Install requirements
    print("\n📦 Installing Python packages...")
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt"):
        print("❌ Failed to install requirements")
        return False

    # Download spaCy French model
    print("\n🇫🇷 Downloading French language model...")
    if not run_command(f"{sys.executable} -m spacy download fr_core_news_sm"):
        print("❌ Failed to download French model")
        return False

    print("\n✅ Setup complete! You can now run the verb extraction tool.")
    print("Run: python app.py")


if __name__ == "__main__":
    main()
