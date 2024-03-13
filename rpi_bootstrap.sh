#!/bin/bash

set -e

sudo apt-get update
sudo apt-get install -y git

sudo chown $USER: /opt/fetap
python -m venv /opt/fetap/autoupdater-venv

/opt/fetap/autoupdater-venv/bin/pip --no-cache-dir install autoupdater==0.21.0
sudo cp /opt/fetap/fetap.service /lib/systemd/system/fetap.service
sudo systemctl enable fetap.service
sudo systemctl start fetap
