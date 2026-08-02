#!/bin/bash
# Source NVM so yt-dlp can find the real Node.js to solve the YouTube JS challenge
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

export NODE_PATH_EXEC=$(which node)
echo "Resolved Node path: $NODE_PATH_EXEC"

# Activate python virtual environment
cd ~/reels_bot_leadership
source venv/bin/activate

# Run the bot
python3 main.py
