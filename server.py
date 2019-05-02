#Mateusz Pabian TCS
import socket
import sys
import threading
import cryptography
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from stegano import lsb
import cv2
from sewar.full_ref import psnr
import os

def parse(x):
    if(x.count(';')>=4):
        tmp=x.split(';')
        if(tmp[0]=='msg'):
            return (('msg',tmp[1],tmp[2],tmp[3],tmp[4]),';'.join(tmp[4:],))
        elif tmp[0]=='usr':
            return (('usr',tmp[3].split(',')),';'.join(tmp[4:],))
        elif tmp[0]=='login':
            return (('login',tmp[3]),';'.join(tmp[4:],))  
        elif tmp[0]=='logout':
            return (('logout',tmp[3]),';'.join(tmp[4:],))
        elif tmp[0]=='password':
            return (('password',tmp[1],tmp[2],tmp[3]),';'.join(tmp[4:],))    

    else:
        return (None,x)

class EchoServer:
    def __init__(self, host, port):
        self.clients = []
        self.clientsLocks={}
        self.users={}
        self.open_socket(host, port)
        self.userLock=threading.Lock()
        self.clientsLock=threading.Lock()
    
    
    def open_socket(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind( (host, port) ) 
        self.server.listen(5)


    def run(self):
        try:
            while True:         
                clientSocket, clientAddr = self.server.accept()

                self.clients.append(clientSocket)
                self.clientsLocks[clientSocket]=threading.Lock()

                Client(clientSocket, clientAddr, self).start()
        finally:
            pass
    
    def clean_client(self, client):
        if client in self.clients:
            try:
                self.userLock.acquire()
                self.clientsLock.acquire()
                self.clients.remove(client)
                for x in list(self.users.keys()):
                    if self.users[x]==client:
                        del self.users[x]
                self.clientsLocks[client].acquire()
                del self.clientsLocks[client]
                client.close()
            except:
                pass
            finally:
                self.userLock.release()
                self.clientsLock.release()
    
    def clean_clients(self, err):
        for client in err:
            self.clean_client(client)
            

class Client(threading.Thread):

    def __init__(self, clientSocket, clientAddr, server):
        super().__init__(daemon=True)
        self.clientSocket = clientSocket;
        self.clientAddr = clientAddr;
        self.server = server
        self.buff = ''
    
    def userUpdate(self):
        err = []
        try:
            self.server.userLock.acquire()
            s='usr;;;'+','.join(self.server.users.keys())+';'
            echodata = bytes(s,'UTF-8')
            for user in self.server.users.values():
                try:
                    self.server.clientsLocks[user].acquire()
                    user.send(echodata)                          
                except:
                    err.append(user)
                finally:
                    self.server.clientsLocks[user].release()   
        finally:
            self.server.userLock.release()
        self.server.clean_clients(err) 

    def run(self):
        encrypted=None
        running = True
        while running:
            data = ''
            try:
                if self.buff.count(';')>=4:
                    data=self.buff                   
                else:
                    data = self.clientSocket.recv(1024);
                    if len(data)>0:
                        data = data.decode('UTF-8')
                        data = self.buff + data
                    else:
                        data=''
                if data:                             
                    tmp = parse(data)
                    self.buff=tmp[1]
                    tmp=tmp[0]
                    err = []
                    if tmp[0]!=None:
                        if tmp[0]=='login':
                            try:
                                self.server.userLock.acquire()
                                s='logok;;;;'
                                if tmp[1] in self.server.users:
                                    s='logfail;;;;'
                                else:
                                    self.server.users[tmp[1]]=self.clientSocket
                                echodata = bytes(s,'UTF-8')
                                self.server.clientsLocks[self.clientSocket].acquire()
                                self.clientSocket.send(echodata)
                            except:
                                err.append(self.clientSocket)
                            finally:
                                self.server.userLock.release()
                                self.server.clientsLocks[self.clientSocket].release()

                            if s == 'logok;;;;':
                                self.userUpdate()

                        elif tmp[0]=='msg':
                            secret1 = lsb.hide("/Users/SalmaOssama/Desktop/1.png", tmp[3])
                            secret1.save("/Users/SalmaOssama/Desktop/hidden.png")
                            st=None

                            with open("/Users/SalmaOssama/Desktop/hidden.png", "rb") as imageFile:
                                st = base64.b64encode(imageFile.read())
                            i1 = cv2.imread("/Users/SalmaOssama/Desktop/1.png")
                            i2 = cv2.imread("/Users/SalmaOssama/Desktop/hidden.png")
                            fidelity = psnr(i1,i2)
                            print("Fidelity")
                            print(fidelity)  
                            print (os.stat('/Users/SalmaOssama/Desktop/1.png').st_size) 
                            capacity=  (os.stat('/Users/SalmaOssama/Desktop/1.png').st_size)/ ((os.stat('/Users/SalmaOssama/Desktop/1.png').st_size)*8)
                            print('Capacity')
                            print(capacity)
                            s='msg;'+tmp[1]+';'+tmp[2]+';'+tmp[3]+';' +'!##!'
                            echodata = bytes(s,'UTF-8') +st +bytes('##endoffile##','UTF-8')
                            if tmp[2]=='ALL':
                                for user in self.server.users.values():
                                    try:
                                        self.server.clientsLocks[user].acquire()
                                        user.send(echodata)                          
                                    except:
                                        err.append(user)
                                    finally:
                                        self.server.clientsLocks[user].release()
                            else:
                                try:
                                    self.server.clientsLocks[self.server.users[tmp[1]]].acquire()
                                    self.server.users[tmp[1]].send(echodata)
                                except:
                                    err.append(self.server.users[tmp[1]])
                                finally:
                                    self.server.clientsLocks[self.server.users[tmp[1]]].release()
                                if tmp[1]!=tmp[2]:                              
                                    try:
                                        self.server.clientsLocks[self.server.users[tmp[2]]].acquire()
                                        self.server.users[tmp[2]].send(echodata)
                                    except:
                                        err.append(self.server.users[tmp[2]])
                                    finally:
                                        self.server.clientsLocks[self.server.users[tmp[2]]].release()

                        elif tmp[0]=='logout':
                            running = False
                            self.server.clean_client(self.clientSocket)
                            self.userUpdate()
                            break
                        elif tmp[0]=='password':
                            key= (tmp[1][2:len(tmp[1])-1]).encode()
                            encrypted= ((tmp[2][2:]) + (tmp[3][:len(tmp[3])-1])).encode()

         

                            f = Fernet(key)
                            decrypted = f.decrypt(encrypted)

 
                                      
                    if len(err):
                        self.server.clean_clients(err)  
                        self.userUpdate()
                                    
                else:
                    running = False
                    self.server.clean_client(self.clientSocket)
                    self.userUpdate()
                    break
                    
            except:
                self.server.clean_client(self.clientSocket)
                self.userUpdate()
                running = False
                break

server = EchoServer('',12345)
server.run()
