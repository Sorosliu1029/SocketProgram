#!/usr/bin/python
# encoding:utf-8
# -*- Mode: Python -*-
# Author: Soros Liu <soros.liu1029@gmail.com>

# ==================================================================================================
# Copyright 2015 by Soros Liu
#
#                                                                          All Rights Reserved

"""
实现简单聊天室的服务器
该聊天室面向所有连接到服务器的用户, 是一个群聊聊天室
提供的功能包含:
    支持多用户同时在线
    支持客户端查询在线用户的请求
    将某用户的聊天内容广播到其他用户客户端
"""
import socket
import sys
import thread
from datetime import datetime
from http import Response, Request

__author__ = 'liuyang'


# 根据情况生成响应报文的类实例
def generateResponse(status, entity):
    http_response = Response()
    http_response.set_status(status)
    http_response.set_entity(entity)
    entityHeaderDict['Content_Length'] = str(len(entity))
    http_response.generalHeader.set_value({'Datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    http_response.responseHeader.set_value(responseHeaderDict)
    http_response.entityHeader.set_value(entityHeaderDict)
    return http_response


# 处理客户端发过来的请求报文字符串, 返回成请求报文的类实例
def handleRequest(raw_request):
    http_request = Request()
    http_request.unpack(raw_request)
    return http_request


class ChatServer(socket.socket):
    """
    服务器端的Socket, 用来接收客户端的连接请求
    socket基于IPv4, TCP连接
    """
    def __init__(self, host, port):
        """
        创建socket ----> 绑定到指定IP地址和端口 ----> 开始监听
        通过users字典维护 (用户, 客户端socket连接) 的对应关系
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created...')
        try:
            self.sock.bind((host, port))
            print('Socket bind complete...')
        except socket.error, e:
            print('Bind Failed.\nError Code: ' +
                  str(e[0]) + ' Message: ' + e[1])
            sys.exit(0)
        self.sock.listen(5)
        print('Socket now listening...')
        self.users = {}

    # 服务器用来处理客户端的连接请求, 并创建新的线程用处理这个客户端连接.
    # 使用多线程实现多用户同时在线的功能
    def handle_accept(self):
        while True:
            conn, addr = self.sock.accept()
            thread.start_new_thread(self.singleConnect, (conn, addr))

    # 用来处理单个客户端的连接请求
    # 连接成功则返回成功('202')的响应报文
    # 并进入循环接收状态
    # 将接收到的请求报文预处理, 根据请求报文的method方法, 转换成服务器命令, 提交给命令处理器(cmdHandle)
    def singleConnect(self, conn, addr):
        print('Accept new connection from: %s, %s' % addr)

        raw_response = generateResponse('202', 'test').pack()

        conn.sendall(raw_response)
        while True:
            raw_request = conn.recv(4096)
            if not raw_request:
                continue
            print(raw_request)
            http_request = handleRequest(raw_request)
            self.cmdHandle(conn, http_request.requestHeader.key_value['User_Agent'],
                           http_method2server_command[http_request.method], http_request.entity)
        conn.close()

    # 根据服务器命令符, 通过类属性获取得到对应的命令处理方法
    def cmdHandle(self, conn, userName, cmd, content):
        method = getattr(self, 'do_' + cmd, None)
        try:
            method(conn, userName, content)
        except TypeError:
            raw_response = generateResponse('400', 'Unknown...TAT').pack()
            conn.sendall(raw_response)

    # 处理客户端登陆请求
    def do_login(self, conn, userName, content):
        name = userName.strip()
        # 查询用户名是否已存在
        if name in server.users:
            raw_response = generateResponse('401', 'Error...T.T').pack()
            conn.sendall(raw_response)
        else:
            self.users[name] = conn
            raw_response = generateResponse('200', 'OK...^.^').pack()
            conn.sendall(raw_response)
            # 向所有其他用户广播, 有新的用户加入聊天室
            raw_response = generateResponse('200',
                                            userName + ' has just entered the chat room...\n').pack()
            self.broadcast(userName, raw_response)

    # 处理客户端发送聊天信息的请求
    def do_say(self, conn, userName, content):
        # 向该用户返回所发送的聊天信息
        entity = ('[ ' + userName + ' ] : ' + content + '\n')
        raw_response = generateResponse('200', entity).pack()
        conn.sendall(raw_response)
        # 向所有其他用户广播该用户的聊天信息
        raw_response = generateResponse('200', '[ ' + userName + ' ] : ' + content + '\n').pack()
        self.broadcast(userName, raw_response)

    # 处理客户端查询当前在线用户的请求
    def do_query(self, conn, userName, content):
        result = 'Online users:\n'
        for key in self.users.keys():
            result += (key + '\n')
        raw_response = generateResponse('200', result).pack()
        conn.sendall(raw_response)

    # 处理客户端退出聊天室的请求
    def do_logout(self, conn, userName, content):
        self.users.pop(userName)
        print('Connection from %s ended...' % userName)
        # 向所有其他用户广播, 该用户已经退出聊天室
        raw_response = generateResponse('200',
                                        userName + ' has just left the chat room...\n').pack()
        self.broadcast(userName, raw_response)

    # 向所有其他用户广播
    def broadcast(self, userName, content):
        for name, conn in self.users.items():
            if name != userName:
                conn.sendall(content)

# IP和端口需要启动服务器前先设置
HOST = '127.0.0.1'
PORT = 9994

# 聊天室只用于英语的纯文本聊天, 故HTTP报文头部某些至设为固定值
# 响应头部的固定值
responseHeaderDict = {'Server': 'Python Socket Server', 'Developer': 'Soros_Liu'}

# 实体头部的固定值
entityHeaderDict = {'Content_Encoding': 'utf-8', 'Content_Language': 'en',
                    'Content_Length': None, 'Content_Type': 'text'}

# HTTP请求报文的方法 到 服务器命令 的转换映射
http_method2server_command = {'ADD': 'login', 'POST': 'say', 'GET': 'query', 'DELETE': 'logout'}


if __name__ == '__main__':
    # 创建服务器主socket
    server = ChatServer(HOST, PORT)
    try:
        # 服务器死循环, 接受客户端连接请求
        server.handle_accept()
    except KeyboardInterrupt:
        print('Server shutdown...Done')
    finally:
        server.close()