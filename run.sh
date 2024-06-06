#!/bin/sh

# Build the command to run the Python script
cmd="python3 meshtastic_exporter.py --host $HOST"

# Add the --verbose flag if VERBOSE is set
if [ -n "$VERBOSE" ]; then
  cmd="$cmd --verbose"
fi

# Run the command and capture its exit code
eval $cmd
exit_code=$?

# If the script exits with a non-zero code, exit the container
if [ $exit_code -ne 0 ]; then
  echo "Script failed with exit code $exit_code, stopping the container."
  exit 1
fi
