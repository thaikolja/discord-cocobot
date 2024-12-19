#!/usr/bin/env sh

source ./venv/bin/activate

# Stops the bot as background service
systemctl stop cocobot
systemctl disable cocobot
