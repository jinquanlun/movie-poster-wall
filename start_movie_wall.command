#!/bin/bash

echo "Starting Movie Poster Wall Application..."
echo "----------------------------------------"
echo "To quit the application:"
echo "1. Press Ctrl+C in this window"
echo "2. Or close this Terminal window"
echo "----------------------------------------"
echo ""

# Change to the application directory
cd "$(dirname "$0")"

# Open the browser (wait a bit for the server to start)
(sleep 2 && open http://localhost:3000) &

# Activate Python environment and run the app
python3 app.py

# Keep the terminal window open if there's an error
read -p "Press [Enter] key to exit..."
