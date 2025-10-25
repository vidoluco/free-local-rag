#!/bin/bash

# Essential RAG System - Setup Script
# One-command setup for new deployments

set -e  # Exit on error

echo "=================================="
echo "Essential RAG System - Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes on first run..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

# Create necessary directories
echo "Creating directory structure..."
mkdir -p data/client_content
mkdir -p data/sample
mkdir -p data/examples
mkdir -p indices
mkdir -p docs
echo "✓ Directories created"
echo ""

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Setting up .env file..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ .env file created from .env.example"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your PERPLEXITY_API_KEY"
    else
        echo "⚠️  Warning: .env.example not found"
    fi
else
    echo "✓ .env file already exists"
fi
echo ""

# Check if config.yaml exists
if [ ! -f "config.yaml" ]; then
    echo "⚠️  Warning: config.yaml not found"
    echo "Please create config.yaml with your settings"
else
    echo "✓ config.yaml found"
fi
echo ""

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Edit .env and add your PERPLEXITY_API_KEY"
echo ""
echo "3. Edit config.yaml with your company information"
echo ""
echo "4. Add your documents to data/client_content/"
echo ""
echo "5. Build the index:"
echo "   python3 scripts/build_index.py"
echo ""
echo "6. Run the web interface:"
echo "   streamlit run app.py"
echo ""
echo "   Or run the CLI chatbot:"
echo "   python3 scripts/run_chatbot.py"
echo ""
echo "For detailed instructions, see CLIENT_GUIDE.md"
echo "=================================="
