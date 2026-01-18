#!/bin/bash

# Loan Assessment Backend - Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "================================================"
echo "Loan Assessment Backend - Setup"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 not found"; exit 1; }
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo ""

# Generate encryption key if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env

    echo ""
    echo "Generating encryption key..."
    ENCRYPTION_KEY=$(python3 scripts/generate_encryption_key.py | grep "ENCRYPTION_KEY=" | cut -d'=' -f2)

    # Update .env with generated key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
    else
        # Linux
        sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
    fi

    echo ""
    echo "================================================"
    echo "IMPORTANT: Configure your API keys in .env file"
    echo "================================================"
    echo "You need to add:"
    echo "  - GEMINI_API_KEY (from Google AI Studio)"
    echo "  - PLAID_CLIENT_ID (from Plaid Dashboard)"
    echo "  - PLAID_SECRET (from Plaid Dashboard)"
    echo "  - GOOGLE_MAPS_API_KEY (from Google Cloud Console)"
    echo "  - GOOGLE_PLACES_API_KEY (from Google Cloud Console)"
    echo ""
else
    echo ".env file already exists, skipping generation"
    echo ""
fi

# Initialize database
echo "Initializing database..."
python3 -c "
import asyncio
from app.database.base import Base
from app.database.session import engine

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Database initialized successfully')

asyncio.run(init_db())
"
echo ""

# Run tests
echo "Running tests..."
python3 -m pytest tests/ -v --tb=short
echo ""

echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Configure API keys in .env file"
echo "2. Run the development server:"
echo "   source venv/bin/activate"
echo "   python3 app/main.py"
echo ""
echo "API Documentation will be available at:"
echo "   http://localhost:8000/docs"
echo ""
echo "================================================"
