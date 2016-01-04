import os,socket,threading,time
import subprocess

allow_delete = True
#local_ip = socket.gethostbyname(socket.gethostname())
local_ip = "127.0.0.1"
local_port = 8000
currdir=os.path.abspath('.')

class Server:
    def __init__(self):
        self.host = 'localhost'
        self.port = 8000
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []

    def open_socket(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host,self.port))
        self.server.listen(5)
    
    def run(self):
        self.open_socket()
        input = [self.server, sys.stdin]
        running = 1
        print 'aaaa'
        while running:
            inputready,outputready,exceptready = select.select(input,[],[])
            #self.conn.send('Masuk Fungsi Run!\r\n')
            print "mlebu"
            for s in inputready:
                if s == self.server:
                    # handle the server socket
                    c = FTPserverThread(self.server.accept())
                    print s
                    #self.conn.send('Masuk Fungsi Run1!\r\n')
                    c.start()
                    #self.conn.send('Masuk Fungsi Run2!\r\n')
                    self.threads.append(c)
                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    running = 0
        # close all threads
        self.server.close()
        for c in self.threads:
            c.join()

class FTPserverThread(threading.Thread):
    def __init__(self,(conn,addr)):
        self.conn=conn
        self.addr=addr
        self.basewd=currdir
        self.cwd=self.basewd
        self.rest=True
        self.pasv_mode=True
        threading.Thread.__init__(self)
        self.flagu = 0
        self.flagp = 0

    def run(self):
        self.conn.send('220 Welcome!\r\n')
        while True:
            cmd=self.conn.recv(512)
            if not cmd: break
            else:
                print 'Recieved:',cmd
                try:
                    func=getattr(self,cmd[:4].strip().upper())
                    func(cmd)
                except Exception,e:
                    print 'ERROR:',e
                    self.conn.send('500 Sorry.\r\n')

    def USER(self,cmd):
        user=cmd.strip().split()[1]
        if user == "joke":
            self.flagu = 1
            self.conn.send('331 OK.\r\n')
        else:
            self.conn.send('530 sorry.\r\n Masukan Username yang benar.\r\n')
            #raise SystemExit

    def PASS(self,cmd):
        password=cmd.strip().split()[1]
        if password == "fun":
            self.flagp = 1
            self.conn.send('331 OK.\r\n')
        else:
            self.conn.send('530 sorry.\r\n Masukan Password yang benar.\r\n')
            #raise SystemExit

    
    def QUIT(self,cmd):
        self.conn.send('221 Goodbye.\r\n')
        # self.conn.close()

    def PWD(self,cmd):
        if self.flagu==1 and self.flagp==1:
            cwd=os.path.relpath(self.cwd,self.basewd)
            if cwd=='.':
                cwd='/'
            else:
                cwd='/'+cwd
            self.conn.send('257 \"%s\"\r\n' % cwd)
        else:
            self.conn.send('Masukan Username dan Password dahulu')
   
    def CWD(self,cmd):
        if self.flagu==1 and self.flagp==1:
            chwd=cmd[4:-2]
            if chwd=='/':
                self.cwd=self.basewd
                self.conn.send('250 OK.\r\n')
            elif chwd[0]=='/':
                self.cwd=os.path.join(self.basewd,chwd[1:])
                self.conn.send('250 OK.\r\n')
            else:
                self.cwd=os.path.join(self.cwd,chwd)
                self.conn.send('530 GAGAL.\r\n')
        else:
            self.conn.send('Masukan Username dan Password dahulu')

    def LIST(self,cmd):
        if self.flagu==1 and self.flagp==1:
            data = "\n"
            for filename in os.listdir(self.cwd):
                # print filename
                data = data + filename + "\n"
            self.conn.send(data)
        else:
            self.conn.send('Masukan Username dan Password dahulu')
	
    def MKD(self,cmd):
        if self.flagu==1 and self.flagp==1:
            dn=os.path.join(self.cwd,cmd[4:-2])
            os.mkdir(dn)
            self.conn.send('257 Directory created.\r\n')
        else:
            self.conn.send('Masukan Username dan Password dahulu')

    def RMD(self,cmd):
        if self.flagu==1 and self.flagp==1:
            dn=os.path.join(self.cwd,cmd[4:-2])
            if allow_delete:
                os.rmdir(dn)
                self.conn.send('250 Directory deleted.\r\n')
            else:
                self.conn.send('450 Not allowed.\r\n')
        else:
            self.conn.send('Masukan Username dan Password dahulu')


    def DELE(self,cmd):
        if self.flagu==1 and self.flagp==1:
            fn=os.path.join(self.cwd,cmd[5:-2])
            if allow_delete:
                os.remove(fn)
                self.conn.send('250 File deleted.\r\n')
            else:
                self.conn.send('450 Not allowed.\r\n')
        else:
            self.conn.send('Masukan Username dan Password dahulu')

    def RNFR(self,cmd):
        if self.flagu==1 and self.flagp==1:
            self.rnfn=os.path.join(self.cwd,cmd[5:-2])
            self.conn.send('350 Ready.\r\n')
        else:
            self.conn.send('Masukan Username dan Password dahulu')

    def RNTO(self,cmd):
        if self.flagu==1 and self.flagp==1:
            fn=os.path.join(self.cwd,cmd[5:-2])
            os.rename(self.rnfn,fn)
            self.conn.send('250 File renamed.\r\n')
        else:
            self.conn.send('Masukan Username dan Password dahulu')

    def RETR(self,cmd):
        cmd1=cmd.split("\r\n")
        name=cmd1[0].split("RETR ")[1]
        file_path = os.path.join(os.getcwd(),name.strip())
        print 'Downloading:',file_path
        size = str(os.path.getsize(file_path))        
        self.conn.send(size)
        fileopen = open(name,"rb")
        data = fileopen.read(1024)
        while (1):
            if not data:
                break
            self.conn.send(data)
            data = fileopen.read(1024)
        fileopen.close()
        print 'done\r\n'
        self.conn.send('226 Transfer complete.\r\n')

    def STOR(self,cmd):
        if self.flagu==1 and self.flagp==1:
            cmd1=cmd.split("\r\n")
            name=cmd1[0].split("STOR ")
            fn=os.path.join(self.cwd,name[1])
            print 'Uplaoding:',fn
            fileopen=open(fn,'wb')
            size=int(cmd.split("\r\n")[1])
            data = ""
            while True:
                if len(data)==size:
                    break
                else:
                    data+=self.conn.recv(1024)
            fileopen.write(data)
            fileopen.close()
            self.conn.send('226 Transfer complete.\r\n')
        else:
            self.conn.send('Masukan Username dan Password dahulu')

    def HELP(self,cmd):
        cmdlist = ( "CWD    --  Mengubah direktori aktif\n"
                    "QUIT   --  Keluar aplikasi\n"
                    "RETR   --  Mengunduh file\n"
                    "STOR   --  Mengunggah file\n"
                    "RNFR   --  Mengganti nama file\n"
                    "RNTO   --  Mengganti nama file\n"
                    "DELE   --  Menghapus file\n"
                    "RMD    --  Menghapus direktori\n"
                    "MKD    --  Membuat direktori\n"
                    "PWD    --  Mencetak direktori aktif\n"
                    "LIST   --  Mendaftar file dan direktori\n"
                    "HELP   --  Menampilkan daftar perintah\n")
        self.conn.send(cmdlist)


class FTPserver(threading.Thread):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((local_ip,local_port))
        threading.Thread.__init__(self)

    def run(self):
        self.sock.listen(5)
        while True:
            th=FTPserverThread(self.sock.accept())
            th.daemon=True
            th.start()

    def stop(self):
        self.sock.close()

if __name__=='__main__':
    s = Server()
    s.run()

'''
    ftp=FTPserver()
    ftp.daemon=True
    ftp.start()
    
    print 'On', local_ip, ':', local_port
    raw_input('Enter to end...\n')
    ftp.stop()
'''