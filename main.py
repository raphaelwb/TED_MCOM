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
import logging

from PIL.ImageOps import expand


class PrepareData:

    def __init__(self):
        self.config_dir = os.path.join(Path.home(),".mcom")
           
    def addElement(self,ele,set):
        itens = []
        keys = ele.split(",")
        for key in keys:
            set.add(key)
            itens.append(key)
        return itens


    def verifyVersion(self):

        logging.info("Downloading")

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

        logging.info(f"Current Version:{version}")

        self.versionCSVFile = os.path.join(self.config_dir,version+".csv")

        needUpdate = not(os.path.isfile(self.versionCSVFile))

        logging.info(f"Updating:{needUpdate}",)

        return needUpdate
    
    def toText(self,languages):
        #print(languages)
        txt = ""
        for i in range(len(languages)-1):
            txt += languages[i] + ","
        txt += languages[len(languages)-1]
        return txt

    def update(self):
        if ( self.verifyVersion() ):

            logging.info("Creating Database")

            dbFile = os.path.join(self.config_dir,"mcom.db")

            try:
                os.remove(dbFile)
            except OSError as e:
                logging.critical(e, exc_info=True)

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

                self.df.fillna('', inplace=True)
                tutorial = self.df.iloc[l]["Tutorial"]

                content = "B"

                if self.df.iloc[l]["Lógica"] == 'x':
                    content = "L"

                logging.info(self.df.iloc[l]["Código"])
                logging.info(self.df.iloc[l]["Lógica"])
                logging.info(content)

                objects.append({"code":str(self.df.iloc[l]["Código"]),
                            "title":str(self.df.iloc[l]["Título"]),
                            "description":str(self.df.iloc[l]["Descrição"]),
                            "type":type,
                            "data":data,
                            "keys":self.addElement(str(self.df.iloc[l]["Palavras Chave"]),keys),
                            "language":self.addElement(str(self.df.iloc[l]["Idiomas"]),language),
                            "hardware":self.addElement(str(self.df.iloc[l]["Hardware"]),hardware),
                            "tutorial": tutorial,
                            "content": content
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

            sql = "CREATE TABLE data(id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, title TEXT, description TEXT, type INTEGER, data TEXT, languages TEXT, tutorial TEXT, content TEXT)"

            cur.execute(sql)

            keys = list(keys)
            language = list(language)
            hardware = list(hardware)

            for o in objects:
                sql = "INSERT INTO data(code,title,description,type,data,languages,tutorial,content) VALUES('%s','%s','%s','%s','%s','%s','%s','%s')" % (o["code"],o["title"],o["description"],o["type"],o["data"],self.toText(o["language"]),o["tutorial"],o["content"])
                logging.info(sql)
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

            logging.info("Finished")

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
from ttkbootstrap.dialogs import Messagebox
from PIL import Image, ImageTk


class CustomMessagebox:
    def __init__(self, parent, title, text, buttons):
        self.top = ttk.Toplevel(parent)
        self.top.title(title)  
        self.top.style.configure('TButton')
        self.top.resizable(False, False)
        self.top.place_window_center()

        # Criação do texto da mensagem
        label = ttk.Label(self.top, text=text, padding=(10, 10) ,wraplength=360)
        label.pack(pady=5, padx=10)

        # Criação dos botões dinâmicos
        self.result = None
        button_frame = ttk.Frame(self.top)
        button_frame.pack(side=ttk.RIGHT, padx=10, pady=10)
        for button in buttons:
            btn_text, btn_style = button.split(":")
            button = ttk.Button(button_frame, text=btn_text, style=f'{btn_style}.TButton', command=lambda b=btn_text: self.on_button_click(b))
            button.pack(side=ttk.LEFT, padx=2)
        self.top.transient(parent)


    def on_button_click(self, button):
        self.result = button
        self.top.destroy()

    def show(self):
        self.top.grab_set()
        self.top.wait_window()
        return self.result


class MCOMSearch(ttk.Frame):

    data = {}
    searching = False
   
    def __init__(self, master):
        super().__init__(master, padding=[15, 5, 15, 5])

        self.pack(fill=BOTH, expand=YES)
       
        _path = pathlib.Path().absolute().as_posix()
        self.path_var = ttk.StringVar(value=_path)
        #self.term_var = ttk.StringVar(value='Digite o termo da busca')
        self.term_var = ttk.StringVar(value='')
        self.type_var = ttk.StringVar(value='endswidth')

        option_text = "Preencha com os dados da busca"
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=[15, 5, 15, 5])
        self.option_lf.pack(fill=X, expand=YES, anchor=N)

        self.create_term_row()
        self.create_results_view()

        self.progressbar = ttk.Progressbar(
            master=self, 
            mode=INDETERMINATE, 
            bootstyle=(STRIPED, SUCCESS)
        )
        self.progressbar.pack(fill=X, expand=YES)

        logoMcom = Image.open('img/logos_ci_ufla_mcom.png')
        logoMcom = logoMcom.resize((int(logoMcom.size[0] / 4.5), int(logoMcom.size[1] / 4.5)), Image.HAMMING)
        self.logoMcom = ImageTk.PhotoImage(logoMcom)
        self.labelMcom = ttk.Label(self, image=self.logoMcom)
        self.labelMcom.configure(padding=2, border=0)
        self.labelMcom.pack()


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
        term_row.pack(fill=X, expand=YES, pady=10)
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
        term_ent.bind('<Return>', lambda event: self.on_search())

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
    '''
    def showItem(self,a):   
        curItem = self.resultview.focus()
        item = self.resultview.item(curItem)
        code = item['values'][0]
        data= MCOMSearch.data[code]
        logging.info(data)
        title = data["title"]
        description = data["description"]
        languages = data["languages"]
        tutorial = data["tutorial"]

        Text = f"Código: {code}\n"\
            f"Título: {title}\n"\
            f"Descrição: {description}\n"\
            f"Idiomas: {languages}\n"\
            "\n"\
            f"Clique Sim para acessar o conteúdo ..."\

        if tutorial == '':
            mb = Messagebox.show_question(Text, title=code, buttons=['No:secondary', 'Yes:primary'])
        else:
            mb = Messagebox.show_question(Text, title=code, buttons=['Tutorial:dark', 'No:secondary', 'Yes:primary'])
            if mb == "Tutorial":
                cmd = self.data[code]["tutorial"]
                #print(f'valor do tutorial: {tutorial}')
                logging.info(f"Browser:{cmd}")
                webbrowser.open(cmd)

        if ( mb == "Yes" or mb == "Sim" ):
            cmd = self.data[code]["data"]
            if ( item['values'][2] == "Link"):
                logging.info(f"Browser:{cmd}")
                webbrowser.open(cmd)
            else:
                logging.info(f"System: {cmd}")
                os.system(cmd)

    '''

    def showItem(self, a):
        curItem = self.resultview.focus()
        item = self.resultview.item(curItem)
        if not item['values']:
            return
        code = item['values'][0]
        data = self.data[code]
        title = data["title"]
        description = data["description"]
        languages = data["languages"]
        tutorial = data["tutorial"]

        text = f"Código: {code}\n\n" \
               f"Título: {title}\n\n" \
               f"Descrição: {description}\n\n" \
               f"Idiomas: {languages}\n\n" \
               f"Clique Sim para acessar o conteúdo ..."

        if tutorial == '':
            custom_mb = CustomMessagebox(self.master, title=code, text=text, buttons=['Não:secondary', 'Sim:primary'])
        else:
            custom_mb = CustomMessagebox(self.master, title=code, text=text, buttons=['Tutorial:dark', 'Não:secondary', 'Sim:primary'])

        result = custom_mb.show()

        if result == "Tutorial":
            cmd = self.data[code]["tutorial"]
            logging.info(f"Browser: {cmd}")
            webbrowser.open(cmd)

        if result == "Yes" or result == "Sim":
            cmd = self.data[code]["data"]
            if item['values'][2] == "Link":
                logging.info(f"Browser: {cmd}")
                webbrowser.open(cmd)
            else:
                logging.info(f"System: {cmd}")
                os.system(cmd)

    def create_results_view(self):
        self.resultview = ttk.Treeview(
            master=self, 
            bootstyle=PRIMARY,
            columns=[0, 1, 2, 3, 4],
            show=HEADINGS
        )
        self.resultview.pack(fill=BOTH, expand=YES, pady=5)

        self.resultview.heading(0, text='Código', anchor=W)
        self.resultview.heading(1, text='Título', anchor=W)
        self.resultview.heading(2, text='Tipo', anchor=W)

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

        self.resultview.bind('<Double-1>', self.showItem)

    def on_search(self):
        term = self.term_var.get()
        
        if term == '':
            return
        
        logging.info(f"Search:{term}")

        self.search_btn.state(["disabled"]) 
        Thread(
            target=MCOMSearch.search, 
            args=(term,), 
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
            if ( len(self.data) == 0 ):
                #Messagebox.show_info("Nada foi encontrado", "Resultado")
                custom_mb = CustomMessagebox(self.master, title="Resultado", text="Nada foi encontrado.", buttons=[])
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
        logging.info("Opening Database")
        config_dir = str(Path.home())+"/.mcom"
        dbFile = os.path.join(config_dir,"mcom.db")
        propFile = os.path.join(config_dir,"conf.properties")
        props = Properties()

        check_file = os.path.isfile(propFile)

        if ( check_file == False ):
             with open(propFile, 'w') as f:
                f.write('HARDWARE=LINK')
                f.write('\n')
                f.write('SEARCH_TYPE=A')
        
        with open(propFile, 'rb') as config_file:
            props.load(config_file)
        hardware = props["HARDWARE"].data
        type = props["SEARCH_TYPE"].data
        
        logging.info(hardware)
        #TODO resolver o problema de usar multiplas Threads para abrir o DB apenas uma vez
        conn = sqlite3.connect(dbFile)        
        cur = conn.cursor()

        typeFilter = ""
        if ( type != "A" ):
            #Logic
            typeFilter = " and content = '"+type+"'"
      
        if ( hardware == "LINK"):
            sql = "Select * from data,data_keys,keys where data.type = 0 and data_keys.data_id = data.id and data_keys.key_id = keys.id and "\
            "((title like '%"+term+"%' or description like '%"+term+"%') OR "\
            "(data_keys.data_id = data.id and data_keys.key_id = keys.id and keys.text like '%"+term+"%'))"+typeFilter
        elif ( hardware == "ALL"):
            sql = "Select * from data,data_keys,keys where data_keys.data_id = data.id and data_keys.key_id = keys.id and "\
            "((title like '%"+term+"%' or description like '%"+term+"%') OR "\
            "(data_keys.data_id = data.id and data_keys.key_id = keys.id and keys.text like '%"+term+"%'))"+typeFilter
        else:
            sql = "Select * from data,data_keys,keys,data_hardware,hardware where data_keys.data_id = data.id and data_keys.key_id = keys.id and "\
            "data_hardware.hardware_id = hardware.id and data_hardware.data_id = data.id and hardware.text = '"+hardware+"' AND ("\
            "((title like '%"+term+"%' or description like '%"+term+"%') OR "\
            "(data_keys.data_id = data.id and data_keys.key_id = keys.id and keys.text like '%"+term+"%')))"+typeFilter
            
        logging.info(sql)
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            logging.info(row)
            type = "Link"
            if ( row[4] == 1 ):
                type = "App"
            record = {"title":row[2],"type":type,"data":row[5],"description":row[3],"languages":row[6], "tutorial": row[7]}
            MCOMSearch.data[row[1]] = record
        cur.close()
        conn.close()
        MCOMSearch.set_searching(False)
        
    @staticmethod
    def set_searching(state=False):
        MCOMSearch.searching = state


if __name__ == '__main__':

    config_dir = os.path.join(Path.home(),".mcom")
    if os.path.isdir(config_dir) == False:
        os.mkdir(config_dir)

    logging.basicConfig(level=logging.INFO, filename=os.path.join(Path.home(),".mcom","log.txt"), format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        data = PrepareData()
        data.update()
    except Exception as e:
        logging.critical(e, exc_info=True) 

    app = ttk.Window("FenixApp", iconphoto="img/Logo-FenixBook-elemento.png")

    app.place_window_center()
    app.style.load_user_themes('fenixbook_themes.json')
    app.style.theme_use('fenixbooktheme1')

    img = Image.open("img/Logo-FenixBook-horizontal.png")
    img = img.resize((int(img.size[0] / 8), int(img.size[1] / 8)), Image.LANCZOS)
    logo = ImageTk.PhotoImage(img)
    label = ttk.Label(app, image=logo)
    label.configure(padding=15)
    label.pack()

    app.resizable(False, False)
    app.geometry("600x500")
    MCOMSearch(app)
    logging.info("Opening Database")
    config_dir = str(Path.home())+"/.mcom"
    dbFile = os.path.join(config_dir, "mcom.db")
    MCOMSearch.conn = sqlite3.connect(dbFile)
    logging.info("Ready")

    app.mainloop()
