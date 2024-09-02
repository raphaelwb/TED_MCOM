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
sudo apt install python3-tk  
sudo apt install python3-venv  
sudo apt install python3-pip  
bash <(curl -s https://raw.githubusercontent.com/raphaelwb/TED_MCOM/main/install.sh)  
python3 main.py
## Adicionar ícone no Linux
cd fenixApp para entrar na pasta  
chmod +x fenixAppExec.sh para permitir a execução do arquivo  
sudo mkdir /usr/share/icons/fenixApp para criar uma pasta para adicionar a logo do fenixBook  
sudo cp ~/fenixApp/img/Logo-FenixBook-elemento.png /usr/share/icons/fenixApp/  
sudo mv ~/fenixApp/fenixApp.desktop /usr/share/applications/ para que o ícone do aplicativo fique visível   

# Install Windows
Open terminal and type python, follow instructions   
Download main.py   
Download requirements_win.txt   
Open Terminal and run    
```bash
pip3 install -r requirements_win.txt   
rename main.py main.pyw
```
Double click on the icon to open the application
