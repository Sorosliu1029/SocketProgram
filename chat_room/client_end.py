#!/usr/bin/python
# encoding:utf-8
import telnetlib
import wx
import thread
from time import sleep
__author__ = 'liuyang'


# login frame GUI
class LoginFrame(wx.Frame):
    """
    login window
    """
    def __init__(self, parent, id, title, size):
        """initialize, add widgets and bind to event"""
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.serverAddressLabel = wx.StaticText(self, label='Server Address',
                                                pos=(10, 50), size=(120, 50))
        self.userNameLabel = wx.StaticText(self, label='User Name',
                                           pos=(40, 100), size=(120,25))
        self.serverAddress = wx.TextCtrl(self, pos=(120, 47), size=(150,25))
        self.userName = wx.TextCtrl(self, pos=(120, 97), size=(150,25))
        self.loginButton = wx.Button(self, label='Login', pos=(80,145),size=(130,30))
        self.loginButton.Bind(wx.EVT_BUTTON, self.login)
        self.Show()

    def login(self, event):
        """process the login"""
        try:
            serverAddress = self.serverAddress.GetLineText(0).split(':')
            # con.open(serverAddress[0], port=int(serverAddress[1]), timeout=10)
            con.open('127.0.0.1', port=8888, timeout=10)
            response = con.read_some()
            if response != 'Connect Success':
                self.showDialog('Connect Fail!', 'Error')
                return
            con.write('login ' + str(self.userName.GetLineText(0)) + '\n')
            # con.write('login liuyang\n')
            response = con.read_some()
            if response == 'User Name Empty!':
                self.showDialog('User Name Empty!', 'Error')
            elif response == 'User Name Exist!':
                self.showDialog('User Name Exist!', 'Error')
            else:
                self.Close()
                ChatFrame(None, -2, title='Python Chat Client', size=(500, 400))
        except Exception:
            self.showDialog('Connect Fail!', 'Error')

    def showDialog(self, content, title):
        """show the error info"""
        dialog = wx.MessageDialog(self, content, title, wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        dialog.Center()
        if dialog.ShowModal() == wx.ID_OK:
            dialog.Destroy()


# chat window
class ChatFrame(wx.Frame):
    """
    chatting window
    """
    def __init__(self, parent, id, title, size):
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.chatFrame = wx.TextCtrl(self, pos=(5,5), size=(490,310),
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.message = wx.TextCtrl(self, pos=(5,320), size=(300,25))
        self.sendButton = wx.Button(self, label='Send', pos=(310,320), size=(58,25))
        self.usersButton = wx.Button(self, label='Users', pos=(373,320), size=(58,25))
        self.closeButton = wx.Button(self, label='Close', pos=(436,320), size=(58,25))
        self.sendButton.Bind(wx.EVT_BUTTON, self.send)
        self.usersButton.Bind(wx.EVT_BUTTON, self.lookUsers)
        self.closeButton.Bind(wx.EVT_BUTTON, self.close)
        thread.start_new_thread(self.receive, ())
        self.Show()

    def send(self, event):
        """send message"""
        message = str(self.message.GetLineText(0)).strip()
        if message != '':
            con.write('say ' + message + '\n')
            self.message.Clear()

    def lookUsers(self, event):
        """look for the online users"""
        con.write('look\n')

    def close(self, event):
        """close the window"""
        con.write('logout\n')
        con.close()
        self.Close()

    def receive(self):
        """receive message from the server"""
        while True:
            sleep(0.6)
            result = con.read_very_eager()
            if result != '':
                self.chatFrame.AppendText(result)


if __name__ == '__main__':
    app = wx.App()
    con = telnetlib.Telnet()
    LoginFrame(None, -1, title='Login', size=(280,200))
    app.MainLoop()