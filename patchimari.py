#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datexport import *
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import argparse
import os.path
import sys
import logging
import GlobalVars as gl

def PATCH_IT(patch_file, dat_file):
	logging.info(u"Начало применения патча..!")
	if not os.path.exists(patch_file):
		gl.wnd.ErrorMessage(u'Не найден файл патча!')
		return #raise Exception('patch_file not found!')
		
	logging.info('Найден файл патча...')
	if not os.path.exists(dat_file):
		gl.wnd.ErrorMessage(u'Не найден файл client_local_English.dat!')		
		return #raise Exception('dat_file not found!')
	
	logging.info('Найден файл client_local_English.dat')
	
	text_files_check = "SELECT name FROM sqlite_master WHERE type='table' and name='text_files'"
	other_files_check = "SELECT name FROM sqlite_master WHERE type='table' and name='other_files'"

	db = sqlite3.connect(patch_file)
	db_cursor = db.cursor()

	handle = 0
	if OpenDatFile(handle, dat_file, 130) != handle:
		db.close()
		logging.error(u'Ошибка открытия файла .dat!!!')
		gl.wnd.ErrorMessage(u'Ошибка открытия файла .dat!!!')
		return #raise Exception('OpenDatFile error!' + dat_file)
	
	logging.info(u'Открыт .dat файл...')
	
	num_files = GetNumSubfiles(handle)
	if num_files == 0 and log_file:
		pass
	
	files_dat = GetSubfileSizes_dict(handle, 0, num_files)
	
	if db_cursor.execute(text_files_check).fetchone():
		current_file_id = -1
		current_subby = None
		KOL = 0			
		
		for file_id, fragment_id, fragment_data, args_order in db_cursor.execute('SELECT * FROM text_files ORDER BY file_id ASC'):
			KOL = KOL + 1
			if not is_text_file(file_id):
				CloseDatFile(handle)
				db.close()
				gl.wnd.ErrorMessage(u'text_files table contains non-text files! (file_id != 0x25XXXXXX)')
				return #raise Exception('text_files table contains non-text files! (file_id != 0x25XXXXXX)\n')
			
			if len(args_order):
				try:
					args_order = [int(n) - 1 for n in args_order.split('-')]
				except:
					gl.wnd.ErrorMessage(u'Ошибка! Некорректный порядок аргументов!')
					return
			else:
				args_order = []
			
			if file_id not in files_dat:
				continue
			
			
			if file_id != current_file_id:
				if current_file_id != -1:        
					data_new = current_subby.get_data()
					PurgeSubfileData(handle, current_file_id)
					#open('s_data', 'a+b').write(data_new)
					PutSubfileData(handle, current_file_id, data_new, current_subby.version, files_dat[current_file_id][1])
					
				try:
					current_file_id = file_id
					current_subby = SubFile(current_file_id)
					data_old, current_subby.version = GetSubfileData(handle, current_file_id, files_dat[current_file_id][0])
					current_subby.build_from_data(data_old)
					
					if fragment_id in current_subby.fragments:
						current_subby.fragments[fragment_id].pieces = fragment_data[1:-1].split(u'<--DO_NOT_TOUCH!-->')			
				except:
					gl.wnd.ErrorMessage(u"Ошибка!!! Не удалось корректно прочитать файл " + str(file_id) + ", пропускаю его!")
					current_file_id = -1
					current_subby = None					
					continue
			    
				
		if current_file_id != -1 and current_subby is not None:
			data_new = current_subby.get_data(args_order, file_id, fragment_id)
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
	logging.info('Patched successfully ' + str(KOL) + ' texts')
	os.remove(gl.patchpath)    