import datetime, threading, time
from functions import *
from threading import Thread
from Console import Console

def foo():
    next_call = time.time()
    while True:
        print datetime.datetime.now()
        next_call = next_call+.1;
        time.sleep(next_call - time.time())
def bar():
	print time.time()
	
	
class clockThread(Thread):
	def __init__(self, function, period):
		Thread.__init__(self)
		self.function=function
		self.period=period
		self.iterations=0
		self.daemon=True
		self.paused=True
		self.state=threading.Condition()
		
	def run(self):
		self.resume()
		while True:
			with self.state:
				if self.paused:
					self.state.wait()
			threadTimer(self.function, self.period)
			self.iterations += 1
			
	def resume(self):
		with self.state:
			self.paused=False
			self.state.notify()
			
	def pause(self):
		with self.state:
			self.paused - True  


c=Console()
serverThread=Thread(target=c.socketServer)
serverThread.daemon=True
#serverThread.start()
timerThread = clockThread(bar, .1)
timerThread.daemon = True
timerThread.start()
fooThread = Thread(target=foo)
fooThread.daemon = True
#fooThread.start()
while True:
	time.sleep(1)
	print '				**************** ', time.time()
