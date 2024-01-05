# TED_MCOM
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
# Configuration
Se quiser filtrar pelo harware na busca, configurar o arquivo conf.properties e copiar para o diretório   
```bash
mkdir ~/.mcom
cp conf.properties ~/.mcom
```

# Install Linux
bash <(curl -s https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/install.sh)   
python3 main.py

# Install Windows
Install python3   
Download main.py   
Download requirements_win.txt   
Open Terminal and run    
```bash
pip3 install -r requirements_win.txt   
python3 main.py
```