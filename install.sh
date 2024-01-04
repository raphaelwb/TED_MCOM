#!/bin/bash
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/requeriments.txt > requeriments.txt
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/main.py > main.py
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt