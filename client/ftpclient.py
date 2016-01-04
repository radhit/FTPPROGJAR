import sys
import os,socket,threading,time

server_address = ('127.0.0.1', 8000)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(server_address)

data = ""
data = client.recv(1024)
print data
user = ""
password = ""

while(1):
	cmd = raw_input(">>")

	if "USER" in cmd:
		user = cmd.split(" ")[1]
		cmd = client.send(cmd+"\r\n")
		data = client.recv(1024)
		print data
	
	elif "PASS" in cmd:
		password = cmd.split(" ")[1]
		cmd = client.send(cmd+"\r\n")
		data = client.recv(1024)
		print data
	
	elif "RNFR" in cmd:
		cmd = client.send(cmd+"\r\n")
		data = client.recv(1024)
		print data
	
	elif "RNTO" in cmd:
		cmd = client.send(cmd+"\r\n")
		data = client.recv(1024)
		print data

	elif "HELP" in cmd:
		cmd = client.send(cmd+"\r\n")
		data=client.recv(1024)
		print data	
	
	elif "QUIT" in cmd:
		cmd = client.send(cmd+"\r\n")
		data = client.recv(1024)
		print data
		client.close()
		exit()
	
	elif "DELE" in cmd:
		cmd = client.send(cmd+"\r\n")
		data = client.recv(1024)
		print data
	
	elif "CWD" in cmd:
		cmd = client.send(cmd+"\r\n")
		data = client.recv(1024)
		print data
	
	elif "PWD" in cmd:
		cmd = client.send(cmd+"\r\n")
		data = client.recv(1024)
		print data

	elif "RETR" in cmd:
		name = cmd.split("RETR ")[1]
		print name
		cmd = client.send(cmd+"\r\n")
		size = client.recv(1024)
		fileopen = open(name,'wb')
		isi = ""
		while (1):
			if (len(isi))>=int(size):
				break
			else:
				isi+=client.recv(1024)
		fileopen.write(isi)
		fileopen.close()
		data = client.recv(1024)
		print data

	elif "STOR" in cmd:
		name = cmd.split("STOR ")[1]
		file_path = os.path.join(os.getcwd(),name.strip())
		size = str(os.path.getsize(file_path))
		cmd = client.send(cmd+"\r\n"+size)
		fileopen = open(name,"rb")
		data = fileopen.read(4096)
		while (1):
			if not data:
				break
			upload = client.send(data)
			data = fileopen.read(4096)
		fileopen.close()
		data = client.recv(1024)
		print data
	
	elif "RMD" in cmd:
		cmd = client.send(cmd+"\r\n")
		data = client.recv(1024)
		print data
	
	elif "MKD" in cmd:
		cmd = client.send(cmd+"\r\n")
		data = client.recv(1024)
		print data
		
	elif "LIST" in cmd:
		cmd = client.send(cmd+"\r\n")
		data = client.recv(1024)
		print data




