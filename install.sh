#!/bin/bash
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/requirements.txt > requirements.txt
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/main.py > main.py
curl  https://github.com/raphaelwb/TED_MCOM/blob/main/fenixbook_themes.json > fenixbook_themes.json
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt