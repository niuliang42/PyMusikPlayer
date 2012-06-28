#!/usr/bin/python
# -*- encoding:utf-8 -*-
import os,sys
import time
import random
import threading
import tty,termios
import subprocess
import signal
from DBControl import DBControl
import gtk,gobject

import pygst
pygst.require("0.10")
import gst

cmd=''

class LimitStack:
	def __init__(self,i_size):
		self._queue=[]
		self._size=i_size
	def empty(self):
		return not self._queue
	def pop(self):
		if(not self.empty()):
			return self._queue.pop()
		else:
			return None
	def push(self,i_item):
		self._queue.append(i_item)
		if(len(self._queue)>self._size):
			del self._queue[0]
	def size(self):
		return len(self._queue)
	def show_all(self):
		for item in self._queue:
			print item
			
class screen_control:
	def refresh(self,i_musik):
		os.system('clear')
		music_info=i_musik.split('/')
		sys.stdout.write("Now Playing...\r\n")
		sys.stdout.write("%s\r\n" % music_info[-3])
		sys.stdout.write("%s\r\n" % music_info[-2])
		sys.stdout.write("%s\r\n" % music_info[-1])


class MrWatcher(threading.Thread):
	def __init__(self,i_player):
		threading.Thread.__init__(self)
		self.player=i_player
		self.thread_stop = False
	def run(self):
		while self.player.playing != -1:
			#print self.player.playing
			time.sleep(1)
		self.stop()
	
	def stop(self):
		self.thread_stop = True

class MrAdmin(threading.Thread):
	def __init__(self,i_player):  
		threading.Thread.__init__(self)
		self.player=i_player
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
				self.player.stop_song()
				cmd='MUSIC_NEXT'
				break
			elif(ch=='j'):
				self.player.pre_song()
				cmd='MUSIC_PREVIOUS'
			elif(ch=='q'):
				self.player.stop_song()
				cmd='QUIT'
				break
			elif(ch==' '):
				if(pause):
					self.player.play_song()
					pause=False
				else:
					self.player.pause_song()
					pause=True
		self.stop()
			
	def stop(self):  
		self.thread_stop = True  

class GstPlayer:
	def __init__(self):
		self.playing=-1
		self.stack=LimitStack(48)
		self.musik_path=''
		self.sc=screen_control()
		
		self.main = gobject.MainLoop()
		gobject.threads_init()
		#print 'hello'
		self.player =  gst.element_factory_make('playbin', 'player')
		fakesink = gst.element_factory_make("fakesink", "fakesink")
		self.player.set_property("video-sink", fakesink)
		bus = self.player.get_bus()
		bus.add_signal_watch()
		bus.connect("message", self.on_message)
		threading.Thread(target=self.main.run).start()
		'''
		playing ==-1  -> Stop
		playing == 0  -> Pause
		playing == 1  -> Playing
		'''
		
	def load(self,i_path):
		self.musik_path=i_path
						
	def on_message(self, bus, message):
		t = message.type
		if t == gst.MESSAGE_EOS:
			self.player.set_state(gst.STATE_NULL)
			self.playing=-1
		elif t == gst.MESSAGE_ERROR:
			self.player.set_state(gst.STATE_NULL)
			err, debug = message.parse_error()
			print "Error: %s" % err, debug
			self.playing=-1
	
	def play_song(self):
		if os.path.isfile(self.musik_path):
			if(self.playing==-1):
				self.player.set_property("uri", "file://" + self.musik_path)
			self.player.set_state(gst.STATE_PLAYING)
			self.playing=1
			self.stack.push(self.musik_path)
			#self.stack.show_all()
			#print(self.musik_path)
			self.sc.refresh(self.musik_path)
			
		else:
			print '%s : File Error' % self.musik_path
	
	def pause_song(self):
		if(self.playing==1):
			self.player.set_state(gst.STATE_PAUSED)
			self.playing=0
	
	def pre_song(self):
		if(self.stack.size()>1):
			self.stack.pop()
			self.load(self.stack.pop())
			self.stop_song()
			self.play_song()
	
	def stop_song(self):
		if(self.playing!=-1):
			self.player.set_state(gst.STATE_NULL)
			self.playing=-1
			

if(__name__=='__main__'):
	status=''
	db=DBControl()
	Player=GstPlayer()
	while True:
		if Player.playing==-1: #If the player is stoped.
			
			music=db.fetch_random_one()
			
			Player.load(music)
			Player.play_song()
			admin=MrAdmin(Player)
			watcher=MrWatcher(Player)
			while Player.playing != -1:
				admin.start()
				watcher.start()
				watcher.join()
				admin.stop()
		if(cmd=='QUIT'):
			break
	print('Bye~')
	exit()
