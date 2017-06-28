# -*- coding: utf-8 -*-
import sys
import sqlite3
import argparse
import os.path
from patchimari import PATCH_IT
import wx
import GlobalVars as gl
import threading 

reload(sys)  
sys.setdefaultencoding('utf8')

def updateContent(str):
    str = str.replace('"', '\'')
    str = str.replace('\\\\', '\\')    
    return str

def PatchOneString(file_id, gossip_id, content, args_order, dat_file):
    content = updateContent(content)
    if args_order == "Null":
        args_order = ''
    if (os.path.exists(gl.patchpath)):
        os.remove(gl.patchpath)
    con = sqlite3.connect(gl.patchpath)
    cur = con.cursor()
    cur.execute('CREATE TABLE text_files (file_id INTEGER, gossip_id INTEGER, content TEXT, args_order TEXT)')
    con.commit()
    cur.execute('INSERT INTO text_files (file_id, gossip_id, content, args_order) VALUES("' + file_id + '", "' + gossip_id + '", "' + content + '", "' + args_order + '")')
    con.commit()
    con.close()
    PatchFile(dat_file)
    
def PatchFile(dat_file):
    PATCH_IT(gl.patchpath, dat_file)
    #try:
        #t = threading.Thread(target=PATCH_IT, args=(gl.patchpath, dat_file))
        #t.daemon = True
        #t.start()
    #except:
        #gl.wnd.WarningMessage(u"Ошибка создания потока патча!")
        #return
def AddOneStringToPatch(file_id, gossip_id, content, args_order):
    content = updateContent(content)
    
    if args_order == "Null":
        args_order = ''    
    if not os.path.exists(gl.patchpath):
        con = sqlite3.connect(gl.patchpath)
        cur = con.cursor()            
        cur.execute('CREATE TABLE text_files (file_id INTEGER, gossip_id INTEGER, content TEXT, args_order TEXT)')
        con.commit()      
    else:
        con = sqlite3.connect(gl.patchpath)
        cur = con.cursor()    
    try:
        cur.execute('INSERT INTO text_files (file_id, gossip_id, content, args_order) VALUES("' + file_id + '", "' + gossip_id + '", "' + content + '", "' + args_order + '")') 
        con.commit()
        con.close()    
    except:
        print('INSERT INTO text_files (file_id, gossip_id, content, args_order) VALUES("' + file_id + '", "' + gossip_id + '", "' + ''.join(content) + '", "' + args_order + '")')
        print("\nERROR:" + str(file_id) + " " + str(gossip_id) + ''.join(content))
        print(args_order)
        
def parseConfig(name):
    if not os.path.isfile(name):
        writeBaseConfig()
    fin = open(name, 'r')
    line = fin.readline()
    res = dict()
    while (line):
        if ('=' in line):
            line = line.split('=')
            res[line[0]] = line[1][:-1]
        line = fin.readline()
    fin.close()
    return res

def enhash(str):
    import hashlib
    return hashlib.md5(str.encode("utf-8")).hexdigest()

def writeConfig(mdict, name):
    fout = open(name, 'w')
    for pair in mdict.items():
        fout.write(str(pair[0]) + '=' + str(pair[1]) + '\n')
    fout.close()
    
def writeBaseConfig():
    if not os.path.exists(os.getenv("APPDATA") + "\\Cenchanced"):
            os.makedirs(os.getenv("APPDATA") + "\\Cenchanced")    
    mdict = dict()
    mdict["Version"] = "NULL"
    mdict["DatPath"] = "NULL"
    mdict["UserName"] = "NULL"
    mdict["UserNick"] = "NULL"
    mdict["LoginTime"] = "NULL"
    mdict["UserGroup"] = "NULL"
    mdict["LastUpdateTime"] = "1000000"
    writeConfig(mdict, gl.path)
