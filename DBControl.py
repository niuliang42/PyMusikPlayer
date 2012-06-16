#!/usr/bin/python
# -*- encoding:utf-8 -*-

import os,sys
import sqlite3
import time
try:
    from hashlib import md5
except:
    import md5

class DBControl():
	def __init__(self):
		self.DBNAME=sys.path[0] + "/musik.db"
		self.db=sqlite3.connect(self.DBNAME)
		self.cur=self.db.cursor()
		self.cur.execute(\
			'CREATE TABLE IF NOT EXISTS musik_index\
			(\
				key not null,\
				path not null\
			);')
	def add_new_path(self,i_path,force=False):
		md5x=md5()
		md5x.update(i_path)
		encode_path=md5x.hexdigest()[8:-8]
		print self.table_exists(encode_path)
		if(force):
			if(self.table_exists(encode_path)):
				self.drop_table(encode_path)
		else:
			if(self.table_exists(encode_path)):
				print 'Path already exsits in the database.'
				return

		self.create_table(encode_path)
		for root,dirs,files in os.walk(i_path):
			for item in files:
				ext=item.split('.')[-1]
				if(ext in ['mp3']):
					self.insertDB(encode_path,root+'/'+item)
		print 'Add_new_path OK!'
		
	def create_table(self,table_name):
		self.cur.execute(\
			'CREATE TABLE IF NOT EXISTS '+table_name+\
			'(\
				musik_path TEXT NOT NULL\
			);')
	
	def drop_table(self,table_name):
		self.cur.execute('DROP TABLE \''+table_name+'\'')
	
	def table_exists(self,table_name):
		self.cur.execute(\
			'SELECT COUNT(*) FROM sqlite_master \
				where type=\'table\' and name=\''+table_name+'\';')
		num=self.cur.fetchone()[0]
		return True if num>0 else False
		
	def insertDB(self,table_name,value):
		self.cur.execute('INSERT INTO '+table_name+' (musik_path) VALUES '+'(\"'+value+'\");')


if(__name__=='__main__'):
	db=DBControl()
	db.add_new_path('/home/wizmann/音乐',force=True)

