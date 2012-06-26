#!/usr/bin/python
# -*- encoding:utf-8 -*-
import pygame
import os,sys
import time
import random
import threading
import tty,termios
import signal
import subprocess
from DBControl import DBControl

cmd=''

class MrWatcher(threading.Thread):
	def __init__(self,i_pyMusic):
		threading.Thread.__init__(self)
		self.pyMusic=i_pyMusic
		self.thread_stop = False
	def run(self):
		while self.pyMusic.get_busy() == True:
			time.sleep(0.5)
		self.stop()
	
	def stop(self):
		self.thread_stop = True

class MrAdmin(threading.Thread):
	def __init__(self,i_pyMusic):  
		threading.Thread.__init__(self)
		self.pyMusic=i_pyMusic
		self.thread_stop = False
   
	def run(self): #Overwrite run() method, put what you want the thread do here  
		global cmd
		pause=False
		while True:
			fd = sys.stdin.fileno()
			old_settings = termios.tcgetattr(fd)
			try:
				tty.setraw(sys.stdin.fileno())
				ch = sys.stdin.read(1)
			finally:
				termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
			if(ch=='i'):
				subprocess.call(['amixer','sset','Master','1+'],stdout=subprocess.PIPE)
			elif(ch=='k'):
				subprocess.call(['amixer','sset','Master','1-'],stdout=subprocess.PIPE)
			elif(ch=='l'):
				self.pyMusic.stop()
				cmd='MUSIC_NEXT'
				break
			elif(ch=='j'):
				self.pyMusic.stop()
				cmd='MUSIC_PREVIOUS'
				break
			elif(ch=='q'):
				self.pyMusic.stop()
				cmd='QUIT'
				break
			elif(ch==' '):
				if(pause):
					self.pyMusic.unpause()
					pause=False
				else:
					self.pyMusic.pause()
					pause=True
		self.stop()
			
	def stop(self):  
		self.thread_stop = True  

if(__name__=='__main__'):
	pygame.init()
	status=''
	db=DBControl()
	while True:
		if pygame.mixer.music.get_busy() == False:
			os.system('clear')
			music=db.fetch_random_one()
			music_info=music.split('/')
			sys.stdout.write("Now Playing...\r\n")
			sys.stdout.write("%s\r\n" % music_info[-3])
			sys.stdout.write("%s\r\n" % music_info[-2])
			sys.stdout.write("%s\r\n" % music_info[-1])
			pygame.mixer.music.load(music)
			pygame.mixer.music.play()
			admin=MrAdmin(pygame.mixer.music)
			watcher=MrWatcher(pygame.mixer.music)
			while pygame.mixer.music.get_busy() == True:
				admin.start()
				watcher.start()
				watcher.join()
				admin.stop()
		if(cmd=='QUIT'):
			break
	print('Bye~')
	exit()
