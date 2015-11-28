#!/usr/bin/python
# encoding:utf-8
"""

"""

import socket
from time import sleep
import wx
import thread
from datetime import datetime
from http import Request, Response

__author__ = 'liuyang'


def handleResponse(raw_response):
    http_response = Response()
    http_response.unpack(raw_response)
    return http_response


def generateRequest(method, uri, generalHeaderDict, requestHeaderDict, entityHeaderDict, entity, http_version='HTTP/1.1'):
    http_request = Request()
    http_request.set_method(method)
    http_request.set_uri(uri)
    http_request.set_entity(entity)
    http_request.generalHeader.set_value({'Datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    http_request.requestHeader.set_value(requestHeaderDict)
    entityHeaderDict['Content_Length'] = str(len(entity))
    http_request.entityHeader.set_value(entityHeaderDict)
    return http_request

def set_userName(userName):
    requestHeaderDict['User_Agent'] = userName


class LoginFrame(wx.Frame):
    """

    """
    def __init__(self, parent, id, title, size):
        """..."""
        wx.Frame.__init__(self, parent, id, title,
                          style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX))
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
        self.name = None
        self.Show()

    def login(self, event):
        """..."""
        try:
            if not client.connected:
                # serverHost = str(self.serverHost.GetLineText(0).strip())
                # serverPort = int(self.serverPort.GetLineText(0).strip())
                # client.open(serverHost, serverPort)
                client.open(HOST, PORT)
                raw_response = client.receive()
                print(raw_response)
                http_response = handleResponse(raw_response)
                if http_response.status_code != '202':
                    self.showDialog('Connect Failed!', 'Error')
                    return
            self.name = str(self.userName.GetLineText(0))
            if not self.name.strip():
                self.showDialog('User name cannot be empty', 'Error')
                return
            if ' ' in self.name:
                self.showDialog('User name cannot contain space', 'Error')
                return
            set_userName(self.name)
            raw_request = generateRequest('ADD', HOST, None, requestHeaderDict, entityHeaderDict,
                                          '').pack()
            client.sendall(raw_request)
            # client.sendall('liuyang login')
            # self.name = 'liuyang'
            raw_response = client.receive()
            print(raw_response)
            http_response = handleResponse(raw_response)
            if http_response.status_code in ['400', '401', '500']:
                self.showDialog(http_response.reason, 'Error')
            elif http_response.status_code == '200':
                self.Close()
                ChatFrame(None, -2, self.name, title='**** Chatting Room ****', size=(510, 400))
            else:
                print(http_response.status_code + ': ' + http_response.reason)
                raise Exception
        except socket.error:
            self.showDialog('Server Error', 'Error')
        except Exception:
            self.showDialog('Unknown Error', 'Error')
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
    def __init__(self, parent, id, userName, title, size):
        wx.Frame.__init__(self, parent, id, title,
                          style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX))
        self.SetSize(size)
        self.Center()
        self.chatFrame = wx.TextCtrl(self, pos=(5, 5), size=(500, 310),
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.messageLabel = wx.StaticText(self, label='Please Enter: ', pos=(5, 320), size=(150 ,25))
        self.message = wx.TextCtrl(self, pos=(5, 350), size=(300, 25))
        self.sendButton = wx.Button(self, label='Send', pos=(310, 345), size=(58, 25))
        self.usersButton = wx.Button(self, label='Users', pos=(373, 345), size=(58, 25))
        self.closeButton = wx.Button(self, label='Close', pos=(436, 345), size=(58, 25))
        self.sendButton.Bind(wx.EVT_BUTTON, self.sendMsg)
        self.usersButton.Bind(wx.EVT_BUTTON, self.queryUsers)
        self.closeButton.Bind(wx.EVT_BUTTON, self.close)
        self.name = userName
        thread.start_new_thread(self.receiveMsg, ())
        self.Show()

    def sendMsg(self, event):
        """..."""
        message = str(self.message.GetLineText(0).strip())
        if message != '':
            raw_request = generateRequest('POST', HOST, None, requestHeaderDict, entityHeaderDict,
                                          (message + '\n')).pack()
            client.sendall(raw_request)
            self.message.Clear()

    def queryUsers(self, event):
        """..."""
        raw_request = generateRequest('GET', HOST, None, requestHeaderDict, entityHeaderDict,
                                      '').pack()
        client.sendall(raw_request)

    def close(self, event):
        """..."""
        raw_request = generateRequest('DELETE', HOST, None, requestHeaderDict, entityHeaderDict,
                                      '').pack()
        client.sendall(raw_request)
        client.close()
        self.Close()

    def receiveMsg(self):
        """"..."""
        while True:
            sleep(0.5)
            try:
                raw_response = client.receive()
                print(raw_response)
                http_response = handleResponse(raw_response)
            except socket.error:
                continue
            if http_response.entity != '':
                self.chatFrame.AppendText(http_response.entity)

class ChatClient(socket.socket):
    def __init__(self):
        socket.socket.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def loop(self):
        while True:
            data = raw_input('>>>')
            self.sock.sendall(data)
            print(self.sock.recv(4096))

    def open(self, host, port, timeout=10):
        self.sock.connect((host, port))
        self.sock.settimeout(timeout)
        self.connected = True

    def close(self):
        self.sock.close()
        self.connected = False

    def receive(self):
        return self.sock.recv(4096)

    def sendall(self, msg):
        self.sock.sendall(msg)


HOST = '127.0.0.1'
PORT = 9994
requestHeaderDict = {'Accept': 'text', 'Accept_Language': 'en', 'Accept_Encoding': 'utf-8',
                     'Host': HOST, 'User_Agent': None}
entityHeaderDict = {'Content_Encoding': 'utf-8', 'Content_Language': 'en',
                    'Content_Length': None, 'Content_Type': 'text'}

if __name__ == '__main__':
    app = wx.App()
    client = ChatClient()
    LoginFrame(None, -1, title='Login', size=(280, 200))
    app.MainLoop()