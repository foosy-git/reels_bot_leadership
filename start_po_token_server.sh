#!/bin/bash
echo "Installing PO Token Server..."
git clone https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git
cd bgutil-ytdlp-pot-provider/server
npm ci
npx tsc
nohup node build/main.js > server.log 2>&1 &
echo "PO Token Server started on port 4416 in the background!"
