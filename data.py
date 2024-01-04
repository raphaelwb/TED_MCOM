'''
No Google Drive selecionar a Planilha >> Compartilhar >> Publicar na WEB > (Valores Separados por Vírgulas (.csv) 

Formato:

Código	Título	Descrição	Palavras Chave	Idiomas	Link	Executável	Hardware
001EX	Code ORG	Site para aprender Codificação	programação	Português, Inglês, Espanhol	https://code.org/		H6+,H65
002BC	Calculadora	Calculadora do Linux	matemática	Português		/bin/gnome-calculator	H6+,H65
'''

import requests
import pandas as pnd
import sqlite3
import os
import json
import math 
import sys
from pathlib import Path

class PrepareData:

    def __init__(self):
        self.config_dir = str(Path.home())+"/.mcom"
        if os.path.isdir(self.config_dir) == False:
            os.mkdir(self.config_dir)
       

    def addElement(self,ele,set):
        itens = []
        keys = ele.split(",")
        for key in keys:
            set.add(key)
            itens.append(key)
        return itens


    def verifyVersion(self):

        print("Downloading")

        url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTpv6TQ8wL0mbc0bxCBbvY4_rVllkFQoTyfPozXGHDCPpj-w193UES9oBGgjlxRbccb-jKIDAVPDSzF/pub?output=csv'
        
        self.dataTempCVSFile = os.path.join(self.config_dir,"dataTemp.csv")

        r = requests.get(url, allow_redirects=True)

        try:
            os.remove(self.dataTempCVSFile)
        except OSError:
            pass

        with open(self.dataTempCVSFile, 'wb') as f:
            f.write(r.content)

        self.df = pnd.read_csv(self.dataTempCVSFile)

        version = str(self.df.iloc[0]["Versão"])
        version = version.replace(".","_")

        print("Current Version:",version)

        self.versionCSVFile = os.path.join(self.config_dir,version+".csv")

        needUpdate = not(os.path.isfile(self.versionCSVFile))

        print("Updating:",needUpdate)

        return needUpdate

    def update(self):

        if ( self.verifyVersion() ):

            print("Creating Database")

            dbFile = os.path.join(self.config_dir,"mcom.db")

            try:
                os.remove(dbFile)
            except OSError:
                pass

            keys = set()
            language = set()
            hardware = set()
            objects = []

            row, col = self.df.shape

            for l in range(row):

                type = 1
                #print(self.df.iloc[l])
                data = self.df.iloc[l]["Data"]

                if ( "http" in data ):
                    type = 0

                objects.append({"code":str(self.df.iloc[l]["Código"]),
                            "title":str(self.df.iloc[l]["Título"]),
                            "description":str(self.df.iloc[l]["Descrição"]),
                            "type":type,
                            "data":data,
                            "keys":self.addElement(str(self.df.iloc[l]["Palavras Chave"]),keys),
                            "language":self.addElement(str(self.df.iloc[l]["Idiomas"]),language),
                            "hardware":self.addElement(str(self.df.iloc[l]["Hardware"]),hardware)
                            })


            con = sqlite3.connect(dbFile)
            cur = con.cursor()

            cur.execute("CREATE TABLE keys(id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT)")
            for key in keys:
                sql = "INSERT INTO keys (text) VALUES ('%s')"%(key,)
                cur.execute(sql)

            cur.execute("CREATE TABLE language(id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT)")
            for lan in language:
                sql = "INSERT INTO language (text) VALUES ('%s')"%(lan,)
                cur.execute(sql)

            cur.execute("CREATE TABLE hardware(id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT)")
            for hard in hardware:
                sql = "INSERT INTO hardware (text) VALUES ('%s')"%(hard,)
                cur.execute(sql)

            sql = "CREATE TABLE data_keys (id INTEGER PRIMARY KEY AUTOINCREMENT, data_id INTEGER, key_id INTEGER, FOREIGN KEY(data_id) REFERENCES data(id), FOREIGN KEY(key_id) REFERENCES keys(id))"
            cur.execute(sql)

            sql = "CREATE TABLE data_language (id INTEGER PRIMARY KEY AUTOINCREMENT, data_id INTEGER, language_id INTEGER, FOREIGN KEY(data_id) REFERENCES data(id), FOREIGN KEY(language_id) REFERENCES language(id))"
            cur.execute(sql)

            sql = "CREATE TABLE data_hardware (id INTEGER PRIMARY KEY AUTOINCREMENT, data_id INTEGER, hardware_id INTEGER, FOREIGN KEY(data_id) REFERENCES data(id), FOREIGN KEY(hardware_id) REFERENCES hardware(id))"
            cur.execute(sql)

            sql = "CREATE TABLE data(id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, title TEXT, description TEXT, type INTEGER, data TEXT)"

            cur.execute(sql)

            keys = list(keys)
            language = list(language)
            hardware = list(hardware)

            for o in objects:
                sql = "INSERT INTO data(code,title,description,type,data) VALUES('%s','%s','%s','%s','%s')" % (o["code"],o["title"],o["description"],o["type"],o["data"])
                cur.execute(sql)
                data_id = cur.lastrowid
                
                for k in o["keys"]:
                    id = keys.index(k)+1
                    sql = "INSERT INTO data_keys(data_id,key_id) VALUES (%d,%d)" %(data_id,id)
                    cur.execute(sql)

                for k in o["language"]:
                    id = language.index(k)+1
                    sql = "INSERT INTO data_language(data_id,language_id) VALUES (%d,%d)" %(data_id,id)
                    cur.execute(sql)

                for k in o["hardware"]:
                    id = hardware.index(k)+1
                    sql = "INSERT INTO data_hardware(data_id,hardware_id) VALUES (%d,%d)" %(data_id,id)
                    cur.execute(sql)

            con.commit()
            con.close()

            print("Finished")

            os.rename(self.dataTempCVSFile, self.versionCSVFile)

#pd = PrepareData()
#pd.update()