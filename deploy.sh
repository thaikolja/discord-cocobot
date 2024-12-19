#!/bin/bash

# shellcheck disable=SC2164
cd /home/api/cocobot

git pull

source venv/bin/activate

pip install -r requirements.txt

systemctl start cocobot
systemctl enable cocobot
