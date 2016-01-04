import os,socket,threading,time
import subprocess

allow_delete = True
#local_ip = socket.gethostbyname(socket.gethostname())
local_ip = "127.0.0.1"
local_port = 8000
currdir=os.path.abspath('.')


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

    def QUIT(self,cmd):
        self.conn.send('221 Goodbye.\r\n')
    
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

    def CWD(self,cmd):
        if self.flagu==1 and self.flagp==1:
            chwd=cmd[4:-2]
            if chwd=='/':
                self.cwd=self.basewd
            elif chwd[0]=='/':
                self.cwd=os.path.join(self.basewd,chwd[1:])
            else:
                self.cwd=os.path.join(self.cwd,chwd)
            self.conn.send('250 OK.\r\n')
        else:
            self.conn.send('Masukan Username dan Password dahulu')

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
    ftp=FTPserver()
    ftp.daemon=True
    ftp.start()
    print 'On', local_ip, ':', local_port
    raw_input('Enter to end...\n')
    ftp.stop()
