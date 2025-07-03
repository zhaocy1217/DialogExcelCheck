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

# --- Step 2: Start a new instance of '$PYTHON_SCRIPT' silently in the background ---
echo "Starting '$PYTHON_SCRIPT' silently in the background..."

# `nohup`: Ensures the command continues to run even if the terminal is closed.
# `${PYTHON_INTERPRETER} "${PYTHON_SCRIPT}"`: Executes your Python script.
# `> /dev/null 2>&1`: Redirects all output (stdout and stderr) to /dev/null for silence.
# `&`: Runs the command in the background.
nohup "${PYTHON_INTERPRETER}" "${PYTHON_SCRIPT}" > /dev/null 2>&1 &

echo "'$PYTHON_SCRIPT' started successfully in the background."

# --- Verification (Optional) ---
echo "You can verify the process is running using:"
echo "pgrep -f \"${PYTHON_INTERPRETER}.*${PYTHON_SCRIPT}\""
echo "--- Done ---"