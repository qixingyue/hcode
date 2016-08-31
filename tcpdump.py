#! /usr/bin/python  

import re
import select
import subprocess, fcntl, os  
from optparse import OptionParser

"""
one tool help to capture http data
"""

parser = OptionParser()
parser.add_option("-i",dest="interface",help="interface to listen",metavar="interface",default="eth0")
parser.add_option("-p",dest="port",help="port to listen",metavar="port",default="80")

(options,args) = parser.parse_args()

def tcpdump():  
	# sudo tcpdump -i eth0 -n -s 0 -w - | strings "  
	cmd1 = ['tcpdump','-i', options.interface, '-n','-B', '4096','-s', '0', '-w', '-','port ' + options.port]  
	cmd2 = ['strings']
	p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)  
	p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stdin=p1.stdout)  

	flags = fcntl.fcntl(p2.stdout.fileno(), fcntl.F_GETFL)  
	fcntl.fcntl(p2.stdout.fileno(), fcntl.F_SETFL, (flags | os.O_NDELAY | os.O_NONBLOCK))  
	return p2  


def poll_tcpdump(proc):  
	txt = None  
	while True:  
		# wait 1/10 second   
		readReady, _, _ = select.select([proc.stdout.fileno()], [], [], 0.1)  
		if not len(readReady):  
			break  
		try:  
			line = proc.stdout.readline()
			#for line in iter(proc.stdout.readline, ""):  
			if txt is None:  
				txt = ''  
			txt += line  
		except IOError:  
			pass  
		break  
	return txt  

def filterLines(text):
	pattern_strings = [
			"GET.*",
			"POST.*",
			"^[A-Za-z\-]+\s*\:.*$",
			"HTTP\/1\.1.*",
			"[a-zA-Z_\-]+\=.*"
			]
	for str in pattern_strings:
		pattern = re.compile(str)
		if pattern.match(text):
			if "GET.*" == str or "POST.*" == str or "HTTP\/1\.1.*" == str:
				print ""
			print text,
			break


def main():
	proc = tcpdump()  
	while True:  
		text = poll_tcpdump(proc) 
		if text :  
			filterLines(text)

def pre_check():
	path_arr = os.environ.get("PATH").split(":")
	cmds = ["tcpdump","strings"]
	results = {}
	for cmd in cmds:
		results[cmd] = False
		for path in path_arr:
			if os.path.isfile(path + "/" + cmd):
				results[cmd]=True
				break
	if results['tcpdump'] == True and results['strings'] == True:
		pass
	else:
		print "need tcpdump and strings, install them and run again."


if __name__ == "__main__":
	pre_check()
	main()
