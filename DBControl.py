#!/usr/bin/python
# -*- encoding:utf-8 -*-

import os,sys
import sqlite3
import base64
from random import randint
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
				id INTEGER PRIMARY KEY AUTOINCREMENT,\
				key not null UNIQUE,\
				path not null\
			);')
		self.db.commit()
		self.cur.close()
	
	def add_new_path(self,i_path,force=False):
		md5x=md5()
		md5x.update(i_path)
		encode_path=md5x.hexdigest()[8:-8]
		encode_path='T_'+encode_path
		
		try:
			self.insertIntoIndex(i_path,encode_path)
		except:
			print 'Musik Path:'+i_path+' is already in the index.'
		#print self.table_exists(encode_path)
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
				if(ext in ['mp3','m4a','wma','aac']):
					self.insertDB(encode_path,root+'/'+item)
		self.db.commit()
		self.cur.close()
		print 'Add_new_path OK!'
		
	def create_table(self,table_name):
		self.cur=self.db.cursor()
		self.cur.execute(\
			'CREATE TABLE IF NOT EXISTS '+table_name+\
			'(\
				musik_path TEXT NOT NULL,\
				UNIQUE (\'musik_path\')\
			);')
		self.db.commit()
		self.cur.close()
	
	def drop_table(self,table_name):
		self.cur=self.db.cursor()
		self.cur.execute('DROP TABLE \''+table_name+'\'')
		self.cur.close()
	
	def table_exists(self,table_name):
		self.cur=self.db.cursor()
		self.cur.execute(\
			'SELECT COUNT(*) FROM sqlite_master \
				where type=\'table\' and name=\''+table_name+'\';')
		num=self.cur.fetchone()[0]
		self.cur.close()
		return True if num>0 else False
		
	def insertIntoIndex(self,table_path,table_hash):
		table_path_base64=base64.encodestring(table_path)[:-1]
		self.cur=self.db.cursor()
		self.cur.execute('INSERT INTO musik_index (key,path) VALUES ('+ "\""+table_hash+"\", "+"\""+table_path_base64+"\");")
		self.db.commit()
		self.cur.close()
		
		
	def insertDB(self,table_name,value):
		value=base64.encodestring(value)
		self.cur=self.db.cursor()
		self.cur.execute('INSERT INTO '+ '\"' +table_name + '\"' + ' (musik_path) VALUES '+'(\"'+value+'\");')
	
	def sync_view(self):
		self.cur=self.db.cursor()
		self.cur.execute('Drop View If Exists musik_view;')
		self.db.commit()
		
		self.cur.execute('Select * From musik_index')
		musik_index=self.cur.fetchall()
		
		command = 'Create View musik_view As\n'
		flag_first=True
		
		for item in musik_index:
			print item[1]
			if(flag_first): flag_first=False
			else:
				command+='\n Union All\n'
			command += 'Select * from '+item[1]
		command+=';'
		#print command
		self.cur.execute(command)
		self.cur.close()
	
	def fetch_random_one(self):
		self.cur=self.db.cursor()
		self.cur.execute("Select Count(*) from musik_view;")
		musik_num=int(self.cur.fetchone()[0])
		ptr=randint(0,musik_num-1)
		self.cur.execute("Select * from musik_view limit 1 offset "+str(ptr)+'; ')
		musik_name=self.cur.fetchone()[0]
		self.cur.close()
		return base64.decodestring(musik_name)
	
	def __del__(self):
		self.db.close()


if(__name__=='__main__'):
	db=DBControl()
	db.add_new_path('/media/sda2/Musik',force=True)
	db.sync_view()
	#print db.fetch_random_one()
