#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datexport import *
import sqlite3
import argparse
import os.path
import sys
import GlobalVars as gl

def AddLogStr(str):
        gl.wnd.AddToLog(str)

def PATCH_IT(patch_file, dat_file):
	AddLogStr(u"Применение патча..!\n")
	if not os.path.exists(patch_file):
		AddLogStr(u'Ошибка! Не найден файл патча!\n')
		return #raise Exception('patch_file not found!')
		
	AddLogStr('Найден файл патча...\n')
	if not os.path.exists(dat_file):
		AddLogStr('Ошибка! Не найден файл client_local_English.dat!\n')
		return #raise Exception('dat_file not found!')
	AddLogStr('Найден файл client_local_English.dat\n')
	text_files_check = "SELECT name FROM sqlite_master WHERE type='table' and name='text_files'"
	other_files_check = "SELECT name FROM sqlite_master WHERE type='table' and name='other_files'"


	db = sqlite3.connect(patch_file)
	db_cursor = db.cursor()

	handle = 0
	if OpenDatFile(handle, dat_file, 130) != handle:
		db.close()
		AddLogStr('ERROR: Ошибка открытия файла .dat!!!\n')
		return #raise Exception('OpenDatFile error!' + dat_file)
	AddLogStr('Открыт .dat файл...\n')
	num_files = GetNumSubfiles(handle)
	if num_files == 0 and log_file:
		pass
		
	files_dat = GetSubfileSizes_dict(handle, 0, num_files)

	'''
	if db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name='patch_files'").fetchone():
		for file_id, data in db_cursor.execute('SELECT * FROM patch_files'):
			if file_id not in files_dat:
				continue
				
			if is_text_file(file_id):
				subby_patch = SubFile(file_id, files_dat[file_id][1])
				subby_patch.build_from_data(data)
				
				data_original, version = GetSubfileData(handle, file_id, files_dat[file_id][0])
				subby_original = SubFile(file_id, files_dat[file_id][1])
				subby_original.build_from_data(data_original)
				
				for fragment_id in subby_patch.fragments:
					if fragment_id in subby_original.fragments:
						subby_original.fragments[fragment_id] = subby_patch.fragments[fragment_id]
				
				data_new = subby_original.get_data()
				PurgeSubfileData(handle, file_id)
				PutSubfileData(handle, file_id, data_new, version, subby_original.iteration)
			else:
				version = GetSubfileVersion(handle, file_id)
				PurgeSubfileData(handle, file_id)
				PutSubfileData(handle, file_id, data, version, files_dat[file_id][1])
	'''
	KOL = 0				
	if db_cursor.execute(text_files_check).fetchone():
		current_file_id = -1
		current_fragments = []
		current_subby = None
		for file_id, fragment_id, fragment_data, args_order in db_cursor.execute('SELECT * FROM text_files ORDER BY file_id ASC'):
			KOL = KOL + 1
			if not is_text_file(file_id):
				CloseDatFile(handle)
				db.close()
				AddLogStr('ERROR: text_files table contains non-text files! (file_id != 0x25XXXXXX)\n')
				return #raise Exception('text_files table contains non-text files! (file_id != 0x25XXXXXX)\n')
			if len(args_order):
				args_order = [int(n) - 1 for n in args_order.split('-')]
			else:
				args_order = []
			if file_id not in files_dat:
				continue
			
			if file_id != current_file_id:
				if current_file_id != -1:        
					data_new = current_subby.get_data(args_order)
					PurgeSubfileData(handle, current_file_id)
					#open('s_data', 'a+b').write(data_new)
					PutSubfileData(handle, current_file_id, data_new, current_subby.version, files_dat[current_file_id][1])
					
				current_file_id = file_id
				current_fragments = []
				current_subby = SubFile(current_file_id)
				data_old, current_subby.version = GetSubfileData(handle, current_file_id, files_dat[current_file_id][0])
				current_subby.build_from_data(data_old)
			
			if fragment_id in current_subby.fragments:
				current_subby.fragments[fragment_id].pieces = fragment_data[1:-1].split(u'<--DO_NOT_TOUCH!-->')
				
		if current_file_id != -1 and current_subby is not None:
			data_new = current_subby.get_data(args_order, fragment_id)
			PurgeSubfileData(handle, current_file_id)
			#open('s_data', 'a+b').write(data_new)
			PutSubfileData(handle, current_file_id, data_new, current_subby.version, files_dat[current_file_id][1])

	if db_cursor.execute(other_files_check).fetchone():
		for file_id, data in db_cursor.execute('SELECT * FROM other_files'):
			if file_id not in files_dat:
				continue
			
			version = GetSubfileVersion(handle, file_id)
			PurgeSubfileData(handle, file_id)
			PutSubfileData(handle, file_id, data, version, files_dat[file_id][1])
	
	Flush(handle)
	CloseDatFile(handle)
	db.commit()
	db.close()
	AddLogStr('Patched successfully ' + str(KOL) + ' texts\n####################\n')
	os.remove(gl.patchpath)    