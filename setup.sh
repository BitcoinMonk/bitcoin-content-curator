#!/bin/bash
# Setup script for Bitcoin Content Curator

set -e

echo "Setting up Bitcoin Content Curator..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create data directory
mkdir -p data

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set your API key: export ANTHROPIC_API_KEY='your-key'"
echo "2. Edit config.py to customize feeds and settings"
echo "3. Run a test: python curator.py --dry-run"
echo "4. Run for real: python curator.py"
echo ""
