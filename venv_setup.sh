#!/usr/bin/env bash

# This script sets up a Python virtual environment for AI codebase work.
# It is NOT for running the MCP server, but for enabling an AI agent to install
# code analysis, linting, and refactoring tools to work on your codebase.

echo "Setting up Python virtual environment for codebase tooling..."

# Check if Python 3 is installed
if ! command -v python3 >/dev/null 2>&1
then
    echo "Python 3 could not be found."
    echo "Attempting to install Python 3..."

    # Detect OS and install Python 3 accordingly
    case "$OSTYPE" in
        linux-gnu*)
            if command -v apt-get >/dev/null 2>&1; then
                sudo apt-get update
                sudo apt-get install -y python3 python3-venv python3-pip
            elif command -v yum >/dev/null 2>&1; then
                sudo yum install -y python3 python3-venv python3-pip
            else
                echo "Unsupported Linux distribution. Please install Python 3 manually."
                exit 1
            fi
            ;;
        darwin*)
            # macOS
            if command -v brew >/dev/null 2>&1; then
                brew install python
            else
                echo "Homebrew not found. Please install Homebrew and rerun this script, or install Python 3 manually."
                exit 1
            fi
            ;;
        msys*|win32*)
            echo "Please install Python 3 manually from https://www.python.org/downloads/windows/"
            exit 1
            ;;
        *)
            echo "Unknown OS. Please install Python 3 manually."
            exit 1
            ;;
    esac

    # Re-check if Python 3 is now available
    if ! command -v python3 >/dev/null 2>&1
    then
        echo "Python 3 installation failed or not found in PATH. Please install manually."
        exit 1
    fi
fi

# Create a virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in ./.venv"
    python3 -m venv .venv
else
    echo "Virtual environment already exists in ./.venv"
fi

# Activate the virtual environment (Unix-like)
echo "Activating virtual environment..."
source .venv/bin/activate

# If requirements.txt does not exist, create a minimal one with common code tools
if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt not found. Creating a minimal one for code tooling..."
    cat > requirements.txt <<EOF
black
flake8
pytest
mypy
pylint
jedi
autopep8
isort
EOF
fi

# Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Virtual environment setup complete."
echo "To activate it in your shell:"
echo "  On Linux/macOS:   source .venv/bin/activate"
echo "  On Windows (cmd): .venv\\Scripts\\activate.bat"
echo "  On Windows (PS):  .venv\\Scripts\\Activate.ps1"
echo "To deactivate, run: deactivate"
