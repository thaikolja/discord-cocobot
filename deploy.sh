#!/bin/bash

# shellcheck disable=SC2164
cd /home/botuser/cocobot

git pull

source venv/bin/activate

pip install -r requirements.txt

systemctl start discord-cocobot
systemctl enable discord-cocobot
