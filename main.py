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
            
import pathlib
from queue import Queue
from threading import Thread
from tkinter.filedialog import askdirectory
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import utility
import time
import json
import webbrowser
import os
import sqlite3
from pathlib import Path
from jproperties import Properties

class MCOMSearch(ttk.Frame):

    data = {}
    searching = False
   
    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)

        _path = pathlib.Path().absolute().as_posix()
        self.path_var = ttk.StringVar(value=_path)
        #self.term_var = ttk.StringVar(value='Digite o termo da busca')
        self.term_var = ttk.StringVar(value='code')
        self.type_var = ttk.StringVar(value='endswidth')

        option_text = "Preencha com os dados da busca"
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.create_term_row()
        self.create_results_view()

        self.progressbar = ttk.Progressbar(
            master=self, 
            mode=INDETERMINATE, 
            bootstyle=(STRIPED, SUCCESS)
        )
        self.progressbar.pack(fill=X, expand=YES)

    def create_path_row(self):
        path_row = ttk.Frame(self.option_lf)
        path_row.pack(fill=X, expand=YES)
        path_lbl = ttk.Label(path_row, text="Path", width=8)
        path_lbl.pack(side=LEFT, padx=(15, 0))
        path_ent = ttk.Entry(path_row, textvariable=self.path_var)
        path_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        browse_btn = ttk.Button(
            master=path_row, 
            text="Browse", 
            command=self.on_browse, 
            width=8
        )
        browse_btn.pack(side=LEFT, padx=5)

    def create_term_row(self):
        term_row = ttk.Frame(self.option_lf)
        term_row.pack(fill=X, expand=YES, pady=15)
        term_lbl = ttk.Label(term_row, text="Termos", width=8)
        term_lbl.pack(side=LEFT, padx=(15, 0))
        term_ent = ttk.Entry(term_row, textvariable=self.term_var)
        term_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        search_btn = ttk.Button(
            master=term_row, 
            text="Procurar", 
            command=self.on_search, 
            bootstyle=OUTLINE, 
            width=8
        )
        search_btn.pack(side=LEFT, padx=5)
        self.search_btn = search_btn
        
    def create_type_row(self):
        type_row = ttk.Frame(self.option_lf)
        type_row.pack(fill=X, expand=YES)
        type_lbl = ttk.Label(type_row, text="Type", width=8)
        type_lbl.pack(side=LEFT, padx=(15, 0))

        contains_opt = ttk.Radiobutton(
            master=type_row, 
            text="Contém", 
            variable=self.type_var, 
            value="contains"
        )
        contains_opt.pack(side=LEFT)

        startswith_opt = ttk.Radiobutton(
            master=type_row, 
            text="Começa com", 
            variable=self.type_var, 
            value="startswith"
        )
        startswith_opt.pack(side=LEFT, padx=15)

        endswith_opt = ttk.Radiobutton(
            master=type_row, 
            text="Acaba Com", 
            variable=self.type_var, 
            value="endswith"
        )
        endswith_opt.pack(side=LEFT)
        endswith_opt.invoke()

    def selectItem(self,a):
        curItem = self.resultview.focus()
        item = self.resultview.item(curItem)
        cmd = self.data[item['values'][0]]["data"]
        if ( item['values'][2] == "Link"):
            print("Browser:",cmd)
            webbrowser.open(cmd)
        else:
            print("System:",cmd)
            os.system(cmd)

    def create_results_view(self):
        self.resultview = ttk.Treeview(
            master=self, 
            bootstyle=INFO, 
            columns=[0, 1, 2, 3, 4],
            show=HEADINGS
        )
        self.resultview.pack(fill=BOTH, expand=YES, pady=10)

        self.resultview.heading(0, text='Código', anchor=W)
        self.resultview.heading(1, text='Título', anchor=W)
        self.resultview.heading(2, text='Tipo', anchor=W)
        #TODO: Colocar uma bandeirinha com os idiomas
        self.resultview.column(
            column=0, 
            anchor=W, 
            width=utility.scale_size(self, 100), 
            stretch=False
        )
        self.resultview.column(
            column=1, 
            anchor=W, 
            width=utility.scale_size(self, 300), 
            stretch=False
        )
        self.resultview.column(
            column=2, 
            anchor=W, 
            width=utility.scale_size(self, 100), 
            stretch=False
        )

        self.resultview.bind('<Double-1>', self.selectItem)

    def on_search(self):
        search_term = self.term_var.get()
        print(search_term)
      
        if search_term == '':
            return

        self.search_btn.state(["disabled"]) 
        Thread(
            target=MCOMSearch.search, 
            args=(search_term,), 
            daemon=True
        ).start()
        self.progressbar.start(10)
        self.after(100, lambda: self.check_queue())
        

    def check_queue(self):
        if self.searching == False:
            for i in self.resultview.get_children():
                self.resultview.delete(i)
            for i in self.data.keys():
                info = self.data[i]
                self.insert_row(i,info["title"],info["type"])
            self.search_btn.state(["!disabled"])
            self.progressbar.stop()
        else:
            self.after(100, lambda: self.check_queue())
         

    def insert_row(self, code, title, type):
        try:
            iid = self.resultview.insert(
                parent='', 
                index=END, 
                values=(code, title, type)
            )
            self.resultview.selection_set(iid)
            self.resultview.see(iid)
        except OSError:
            return

    @staticmethod
    def search(term):
        MCOMSearch.set_searching(True)
        MCOMSearch.data = {}
        print("Opening Database")
        config_dir = str(Path.home())+"/.mcom"
        dbFile = os.path.join(config_dir,"mcom.db")
        propFile = os.path.join(config_dir,"conf.properties")
        props = Properties()
        try:
            with open(propFile, 'rb') as config_file:
                props.load(config_file)
            hardware = props["HARDWARE"].data
        except:
            hardware = "ALL"
        
        print(hardware)
        #TODO resolver o problema de usar multiplas Threads para abrir o DB apenas uma vez
        conn = sqlite3.connect(dbFile)        
        cur = conn.cursor()

        if ( hardware != "ALL"):
            sql = "Select * from data,data_keys,keys,data_hardware,hardware where data_keys.data_id = data.id and data_keys.key_id = keys.id and "\
            "data_hardware.hardware_id = hardware.id and data_hardware.data_id = data.id and hardware.text = '"+hardware+"' AND ("\
            "(title like '%"+term+"%' or description like '%"+term+"%') OR "\
            "(data_keys.data_id = data.id and data_keys.key_id = keys.id and keys.text like '%"+term+"%'))"
        else:
            sql = "Select * from data,data_keys,keys where data_keys.data_id = data.id and data_keys.key_id = keys.id and "\
            "(title like '%"+term+"%' or description like '%"+term+"%') OR "\
            "(data_keys.data_id = data.id and data_keys.key_id = keys.id and keys.text like '%"+term+"%')"

        print(sql)
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            print(row)
            type = "Link"
            if ( row[4] == 1 ):
                type = "App"
            record = {"title":row[2],"type":type,"data":row[5]}
            MCOMSearch.data[row[1]] = record
        cur.close()
        conn.close()
        MCOMSearch.set_searching(False)
        
    @staticmethod
    def set_searching(state=False):
        MCOMSearch.searching = state

if __name__ == '__main__':

    try:
        data = PrepareData()
        data.update()
    except:
        print("Error Updating - Verify Internet")
    
    app = ttk.Window("TVBox - TED MCOM", "journal")
    app.resizable(False,False)
    app.geometry("600x400")
    MCOMSearch(app)
    print("Opening Database")
    config_dir = str(Path.home())+"/.mcom"
    dbFile = os.path.join(config_dir,"mcom.db")
    MCOMSearch.conn = sqlite3.connect(dbFile)
    print("Ready")
    app.mainloop()