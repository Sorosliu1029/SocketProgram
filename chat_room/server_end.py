#!/usr/bin/python
# encoding: utf-8
from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore
__author__ = 'liuyang'


# EndSession error class
class EndSession(Exception):
    """self define the exception when the session ended"""
    pass


# command interpreter class
class CommandHandler:
    """
    to handle the command, e.g. login, query for online users, send message
    """
    def unknown(self, session, cmd):
        """response for unknown command"""
        session.push('Unknown command: %s\n' % cmd)

    def handle(self, session, line):
        """handle the command"""
        if not line.strip():
            return
        parts = line.split(' ', 1)
        cmd = parts[0]
        try:
            line = parts[1].strip()
        except IndexError:
            line = ''
        meth = getattr(self, 'do_' + cmd, None)
        try:
            meth(session, line)
        except TypeError:
            self.unknown(session, cmd)


# room class (abstract class)
class Room(CommandHandler):
    """
    including environment for multiple user.
    responsible for basic command handle and broadcast
    """
    def __init__(self, server):
        self.server = server
        self.sessions = []

    def add(self, session):
        """an user enter the room"""
        self.sessions.append(session)

    def remove(self, session):
        """an user leave the room"""
        self.sessions.remove(session)

    def broadcast(self, line):
        """broadcast a certain message to all users"""
        for session in self.sessions:
            session.push(line)

    def do_logout(self, session, line):
        """leave the room"""
        raise EndSession


class LoginRoom(Room):
    """
    room for user who has just login
    """
    def add(self, session):
        """response when user connect successful"""
        Room.add(self, session)
        session.push('Connect Success')

    def do_login(self, session, line):
        """handle the login command"""
        name = line.strip()
        if not name:
            session.push('User Name Empty!')
        elif name in self.server.users:
            session.push('User Name Exist!')
        else:
            session.name = name
            session.enter(self.server.main_room)


class ChatRoom(Room):
    """
    room for chatting
    """
    def add(self, session):
        """broadcast that there is a new user entering"""
        session.push('Login Success')
        self.broadcast(session.name + ' has entered the room.\n')
        self.server.users[session.name] = session
        Room.add(self, session)

    def remove(self, session):
        """broadcast that there is someone leaved"""
        Room.remove(self, session)
        self.broadcast(session.name + ' has left the room.\n')

    def do_say(self, session, line):
        """client send message"""
        self.broadcast(session.name + ' : ' + line + '\n')

    def do_look(self, session, line):
        """query for the online users"""
        session.push('Online Users:\n')
        for user in self.sessions:
            session.push(user.name + '\n')


class LogoutRoom(Room):
    """
    room for user who will leave
    """
    def add(self, session):
        """remove from the server"""
        try:
            del self.server.users[session.name]
        except KeyError:
            pass


# session class
class ChatSession(async_chat):
    """
    responsible for communicating with a single user
    """
    def __init__(self, server, sock):
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator('\n')
        self.data = []
        self.name = None
        self.enter(LoginRoom(server))

    def enter(self, room):
        """remove self from current rooms, then add to the new room"""
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data):
        """receive data from client"""
        self.data.append(data)

    def found_terminator(self):
        """when one piece of data from client has been ended"""
        line = ''.join(self.data)
        self.data = []
        try:
            self.room.handle(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        async_chat.handle_close(self)
        self.enter(LogoutRoom(self.server))


# server class
class ChatServer(dispatcher):
    """
    chatting server
    """
    def __init__(self, port):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(5)
        self.users = {}
        self.main_room = ChatRoom(self)

    def handle_accept(self):
        conn, addr = self.accept()
        ChatSession(self, conn)


PORT = 8888
if __name__ == '__main__':
    s = ChatServer(PORT)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print()