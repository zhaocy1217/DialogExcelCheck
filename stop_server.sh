#!/bin/bash

# Define the name of your Python script.
# IMPORTANT: If test1.py is not in the same directory as this shell script,
# or not in your system's PATH, you should provide the full path to it.
# For example: PYTHON_SCRIPT="/Users/YourUser/Scripts/test1.py"
PYTHON_SCRIPT="simple_server.py"

# Define the Python interpreter to use.
# On macOS, 'python3' is generally recommended for Python 3 scripts.
PYTHON_INTERPRETER="python3"

echo "--- Managing '$PYTHON_SCRIPT' Process ---"

# --- Step 1: Stop any existing '$PYTHON_SCRIPT' processes ---
echo "Attempting to stop any existing '$PYTHON_SCRIPT' processes..."

# Find the Process IDs (PIDs) of any running Python processes
# that include the script name in their command line.
# `pgrep -f`: Searches the full command line for the pattern.
# `xargs -r kill`: Sends a termination signal to each found PID.
#                  `-r` ensures `kill` is not run if `pgrep` finds no PIDs.
# `> /dev/null 2>&1`: Redirects all standard output and standard error
#                     to /dev/null, making the operation silent.
pgrep -f "${PYTHON_INTERPRETER}.*${PYTHON_SCRIPT}" | xargs -r kill > /dev/null 2>&1

# Give a brief moment for processes to terminate gracefully
sleep 1

echo "Existing processes stopped (if any)."
