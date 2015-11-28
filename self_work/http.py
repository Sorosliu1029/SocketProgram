# encoding: utf-8
# -*- Mode: Python -*-
# Author: Soros Liu <soros.liu1029@gmail.com>

# ============================================================================
# Copyright 2015 by Soros Liu
#
#                                             All Rights Reserved

"""
用来实现类HTTP协议
参照HTTP/1.1, 适当增减了HTTP请求报文的方法和HTTP响应报文的状态码
由于该协议主要服务于简单的聊天室, 所以该协议的其他部分为HTTP/1.1的精简版
"""
__author__ = 'liuyang'

# 该协议的HTTP请求报文的主要方法
# |-----------|------------|------------|-------------|
# |    GET    |     POST   |     ADD    |    DELETE   |
# |-----------|------------|------------|-------------|
# | 查询在线用户| 提交聊天内容|  加入群聊   |  退出群聊    |
# |-----------|------------|------------|-------------|
methods = ['GET', 'POST', 'ADD', 'DELETE']

# 该协议的HTTP响应报文的状态码
# |-----------|------------|------------|-------------|--------------|
# |    200    |    202     |    400     |     401     |     500      |
# |-----------|------------|------------|-------------|--------------|
# |    成功    |   已接受   |  不正确请求  | 用户名已存在 | 内部服务器错误 |
# |-----------|------------|------------|-------------|--------------|
responses = {'200': 'OK',
             '202': 'Accept',
             '400': 'Bad Request',
             '401': 'User Name Exist',
             '500': 'Internal Server Error'}


class ChatHTTP:
    """
    HTTP报文的超类
    """
    def __init__(self):
        self.http_version = 'HTTP/1.1'
        self.generalHeader = GeneralHeader()
        self.entityHeader = EntityHeader()
        self.entity = None

    def set_entity(self, entity):
        self.entity = entity

    # 用于将HTTP报文的信息打包为一个字符串进行传输
    def pack(self):
        pass

    # 用于将接收到的HTTP报文段解析为HTTP类
    def unpack(self, raw_content):
        pass



class Header:
    """
    HTTP头部字段的超类
    """
    def __init__(self):
        self.key_value = dict()

    # 用于将头部字段的键值对打包为一个字符串
    def pack(self):
        result = ''
        for key, value in self.key_value.iteritems():
            result += (str(key) + ': ' + str(value) + '\n')
        return result

    # 用于将表示头部字段的字符串解析为键值对
    def unpack(self, lines):
        for line in lines:
            parts = line.split(': ', 1)
            self.key_value[parts[0]] = parts[1]


class GeneralHeader(Header):
    """
    HTTP报文段的通用头部
    该协议中通用头部包含:
        HTTP报文的生成时间: Datetime
    """
    def __init__(self):
        Header.__init__(self)
        self.key_value['Datetime'] = None

    def set_value(self, dict):
        self.key_value = dict

class RequestHeader(Header):
    """
    HTTP报文段的请求头部
    该协议中请求头部包含:
        客户端接受的信息类型: Accept
        客户端接受的自然语言: Accept_Language
        客户端接受的内容编码: Accept_Encoding
        指定被请求资源的主机: Host
        客户端对应的用户名:  User_Agent
    """
    def __init__(self):
        Header.__init__(self)
        self.key_value['Accept'] = None
        self.key_value['Accept_Language'] = None
        self.key_value['Accept_Encoding'] = None
        self.key_value['Host'] = None
        self.key_value['User_Agent'] = None

    def set_value(self, dict):
        self.key_value = dict

class ResponseHeader(Header):
    """
    HTTP报文段的响应头部
    该协议中响应头部包含:
        服务器的类型信息: Server
        服务器的开发者:   Developer
    """
    def __init__(self):
        Header.__init__(self)
        self.key_value['Server'] = None
        self.key_value['Developer'] = None

    def set_value(self, dict):
        self.key_value = dict


class EntityHeader(Header):
    """
    HTTP报文段的实体头部
    该协议中实体头部包含:
        实体正文的内容编码: Content_Encoding
        实体正文的自然语言: Content_Language
        实体正文的长度:     Content_Length
        实体正文的信息类型: Content_Type
    """
    def __init__(self):
        Header.__init__(self)
        self.key_value['Content_Encoding'] = None
        self.key_value['Content_Language'] = None
        self.key_value['Content_Length'] = None
        self.key_value['Content_Type'] = None

    def set_value(self, dict):
        self.key_value = dict


class Response(ChatHTTP):
    """
    HTTP响应报文段
    """
    def __init__(self):
        ChatHTTP.__init__(self)
        self.status_code = None
        self.reason = None
        self.responseHeader = ResponseHeader()

    def set_status(self, code):
        self.status_code = code
        self.reason = responses[code]

    def pack(self):
        package = ''
        package += (self.http_version + ' ')
        package += (self.status_code + ' ')
        package += (self.reason + '\n')
        package += self.generalHeader.pack()
        package += self.responseHeader.pack()
        package += self.entityHeader.pack()
        package += ('\n' + self.entity)
        return package

    def unpack(self, raw_content):
        lines = raw_content.split('\n')
        response_line = lines[0].split(' ')
        self.http_version = response_line[0]
        self.status_code = response_line[1]
        self.reason = response_line[2]
        self.generalHeader.unpack((lines[1],))
        self.responseHeader.unpack(lines[2:3])
        self.entityHeader.unpack(lines[4:7])
        self.entity = '\n'.join(lines[9:])


class Request(ChatHTTP):
    """
    HTTP请求报文段
    """
    def __init__(self):
        ChatHTTP.__init__(self)
        self.method = None
        self.URI = None
        self.requestHeader = RequestHeader()

    def set_method(self, method):
        self.method = method

    def set_uri(self, uri):
        self.URI = uri

    def pack(self):
        package = ''
        package += (self.method + ' ')
        package += (self.URI + ' ')
        package += (self.http_version + '\n')
        package += self.generalHeader.pack()
        package += self.requestHeader.pack()
        package += self.entityHeader.pack()
        package += ('\n' + self.entity)
        return package

    def unpack(self, raw_content):
        lines = raw_content.split('\n')
        request_line = lines[0].split(' ')
        self.method = request_line[0]
        self.URI = request_line[1]
        self.http_version = request_line[2]
        self.generalHeader.unpack((lines[1],))
        self.requestHeader.unpack(lines[2:6])
        self.entityHeader.unpack(lines[7:10])
        self.entity = ''.join(lines[11:])

