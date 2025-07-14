#!/usr/bin/env python3
"""
Setup script for Reddit User Persona Analyzer
Handles installation and configuration
"""

import os
import sys
import subprocess
import nltk
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("Downloading NLTK data...")
    try:
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✓ NLTK data downloaded successfully")
    except Exception as e:
        print(f"✗ Error downloading NLTK data: {e}")
        return False
    return True

def create_config_file():
    """Create configuration file from template"""
    config_path = Path("config.py")
    example_path = Path("config.example.py")
    
    if config_path.exists():
        print("✓ Config file already exists")
        return True
    
    if not example_path.exists():
        print("✗ config.example.py not found")
        return False
    
    try:
        # Copy example to config
        with open(example_path, 'r') as f:
            content = f.read()
        
        with open(config_path, 'w') as f:
            f.write(content)
        
        print("✓ Config file created from template")
        print("  Please edit config.py with your Reddit API credentials")
        return True
    except Exception as e:
        print(f"✗ Error creating config file: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['samples', 'output', 'logs']
    
    for dir_name in directories:
        path = Path(dir_name)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {dir_name}")
        else:
            print(f"✓ Directory already exists: {dir_name}")

def test_installation():
    """Test if installation works"""
    print("Testing installation...")
    try:
        import praw
        import textblob
        import nltk
        from nltk.sentiment import SentimentIntensityAnalyzer
        
        # Test NLTK data
        analyzer = SentimentIntensityAnalyzer()
        test_result = analyzer.polarity_scores("This is a test")
        
        print("✓ All imports successful")
        print("✓ NLTK sentiment analyzer working")
        return True
    except Exception as e:
        print(f"✗ Installation test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("Reddit User Persona Analyzer Setup")
    print("=" * 40)
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Download NLTK data
    if not download_nltk_data():
        success = False
    
    # Create config file
    if not create_config_file():
        success = False
    
    # Create directories
    create_directories()
    
    # Test installation
    if not test_installation():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit config.py with your Reddit API credentials")
        print("2. Get Reddit API credentials from: https://www.reddit.com/prefs/apps")
        print("3. Run: python reddit_persona_analyzer.py <reddit_user_url>")
    else:
        print("✗ Setup completed with errors")
        print("Please check the error messages above and try again")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)