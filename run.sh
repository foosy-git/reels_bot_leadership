#!/bin/bash
# Source NVM so yt-dlp can find the real Node.js to solve the YouTube JS challenge
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Activate python virtual environment
cd ~/reels_bot_leadership
source venv/bin/activate

# Run the bot
python3 main.py
