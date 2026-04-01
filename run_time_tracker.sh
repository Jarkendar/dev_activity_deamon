#!/bin/bash

# Activate virtual environment and run the dev-tracker daemon

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Run the daemon
python -m daemon.main
