#!/bin/bash

cd /home/botuser/cocobot
git pull origin ci
source venv/bin/activate
pip install -r requirements.txt
systemctl restart cocobot