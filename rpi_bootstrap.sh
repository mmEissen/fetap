#!/bin/bash

set -e

sudo apt-get update
sudo apt-get install -y git python3-venv python3-setuptools python3-dev

sudo chown $USER: /opt/fetap
python -m venv /opt/fetap/autoupdater-venv

/opt/fetap/autoupdater-venv/bin/pip --no-cache-dir install autoupdater
sudo cp /opt/fetap/fetap.service /lib/systemd/system/fetap.service
sudo systemctl enable fetap.service
sudo systemctl start fetap
