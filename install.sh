#!/bin/bash
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/requirements.txt > requirements.txt
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/main.py > main.py
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/fenixbook_themes.json > fenixbook_themes.json
curl https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/Logo-FenixBook-elemento.png > Logo-FenixBook-elemento.png
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt