#!/usr/bin/python
# encoding:utf-8
"""

"""

import socket
from time import sleep
import wx
import thread

__author__ = 'liuyang'


class LoginFrame(wx.Frame):
    """

    """
    def __init__(self, parent, id, title, size):
        """..."""
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.serverHostLabel = wx.StaticText(self, label='Host: ', pos=(10, 30), size=(80, 50))
        self.serverPortLabel = wx.StaticText(self, label='Port: ', pos=(10, 60), size=(40, 50))
        self.userNameLabel = wx.StaticText(self, label='User Name:', pos=(10, 90), size=(100, 50))
        self.serverHost = wx.TextCtrl(self, pos=(100, 30), size=(150, 25))
        self.serverPort = wx.TextCtrl(self, pos=(100, 60), size=(150, 25))
        self.userName = wx.TextCtrl(self, pos=(100, 90), size=(150, 25))
        self.loginButton = wx.Button(self, label='Login', pos=(80, 145), size=(130, 30))
        self.loginButton.Bind(wx.EVT_BUTTON, self.login)
        self.Show()

    def login(self, event):
        """..."""
        try:
            # serverHost = str(self.serverHost.GetLineText(0).strip())
            # serverPort = int(self.serverPort.GetLineText(0).strip())
            # client.open(serverHost, serverPort)
            client.open('127.0.0.1', 8888)
            response = client.receive()
            if response != 'Connect Success':
                self.showDialog('Connect Failed!', 'Error')
                return
            # client.sendall('login ' + str(self.userName.GetLineText(0)) + '\n')
            client.sendall('login liuyang\n')
            response = client.receive()
            if response in ['User Name Empty!', 'User Name Exist!']:
                self.showDialog(response, 'Error')
            else:
                self.Close()
                ChatFrame(None, -2, title='**** Chatting Room ****', size=(500, 400))
        except Exception:
            self.showDialog('Unknow Error', 'Error')
            raise

    def showDialog(self, content, title):
        """..."""
        dialog = wx.MessageDialog(self, content, title, wx.OK | wx.CANCEL | wx.ICON_ERROR)
        dialog.Center()
        if dialog.ShowModal() == wx.ID_OK:
            dialog.Destroy()


class ChatFrame(wx.Frame):
    """

    """
    def __init__(self, parent, id, title, size):
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.chatFrame = wx.TextCtrl(self, pos=(5, 5), size=(490, 310),
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.message = wx.TextCtrl(self, pos=(5, 320), size=(300, 25))
        self.sendButton = wx.Button(self, label='Send', pos=(310, 320), size=(58, 25))
        self.usersButton = wx.Button(self, label='Users', pos=(373, 320), size=(58, 25))
        self.closeButton = wx.Button(self, label='Close', pos=(436, 320), size=(58, 25))
        self.sendButton.Bind(wx.EVT_BUTTON, self.sendMsg)
        self.usersButton.Bind(wx.EVT_BUTTON, self.queryUsers)
        self.closeButton.Bind(wx.EVT_BUTTON, self.close)
        thread.start_new_thread(self.receiveMsg, ())
        self.Show()

    def sendMsg(self, event):
        """..."""
        message = str(self.message.GetLineText(0).strip())
        if message != '':
            client.sendall('say ' + message + '\n')
            self.message.Clear()

    def queryUsers(self, event):
        """..."""
        client.sendall('query\n')

    def close(self, event):
        """..."""
        client.sendall('logout\n')
        client.close()
        self.Close()

    def receiveMsg(self):
        """"..."""
        while True:
            sleep(0.5)
            print(client.sock.gettimeout())
            try:
                result = client.receive()
            except socket.error:
                continue
            if result != '':
                self.chatFrame.AppendText(result)

class ChatClient(socket.socket):
    def __init__(self):
        socket.socket.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.connect((host, port))
        # self.sock.settimeout(3)

    def loop(self):
        while True:
            data = raw_input('>>>')
            self.sock.sendall(data)
            print(self.sock.recv(4096))

    def open(self, host, port, timeout=10):
        self.sock.connect((host, port))
        self.sock.settimeout(timeout)

    def close(self):
        self.sock.close()

    def receive(self):
        return self.sock.recv(4096)

    def sendall(self, msg):
        self.sock.sendall(msg)


# HOST = '127.0.0.1'
# PORT = 8888
if __name__ == '__main__':
    app = wx.App()
    client = ChatClient()
    LoginFrame(None, -1, title='Login', size=(280, 200))
    app.MainLoop()
    # try:
    #     client.loop()
    # except KeyboardInterrupt:
    #     print('Client down...')
    # finally:
    #     client.sock.close()
    #     client.close()