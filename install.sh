#!/bin/bash
mkdir fenixApp
cd fenixApp
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/requirements.txt > requirements.txt
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/main.py > main.py
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/fenixbook_themes.json > fenixbook_themes.json
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/fenixApp.desktop > fenixApp.desktop
curl  https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/fenixAppExec.sh > fenixAppExec.sh
mkdir img
curl https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/img/Logo-FenixBook-elemento.png > ./img/Logo-FenixBook-elemento.png
curl https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/img/Logo-FenixBook-horizontal.png > ./img/Logo-FenixBook-horizontal.png
curl https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/img/logos_ci_ufla_mcom.png > ./img/logos_ci_ufla_mcom.png
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt