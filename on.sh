#!/usr/bin/env sh

source ./venv/bin/activate

# Starts the bot as background service
systemctl start cocobot
systemctl enable cocobot
