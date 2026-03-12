#!/bin/bash
# Wallet Security Check Runner
# Uses virtual environment to avoid system package conflicts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Run: python3 -m venv $VENV_DIR && $VENV_DIR/bin/pip install web3"
    exit 1
fi

# Run the wallet check script with venv python
"$VENV_DIR/bin/python3" "$SCRIPT_DIR/wallet_security_check.py" "$@"
