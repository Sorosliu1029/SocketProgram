"""

"""


__author__ = 'liuyang'

methods = ['GET', 'POST', 'ADD', 'DELETE']

responses = {'200': 'OK', '202': 'Accept', '400': 'Bad_Request',
             '401': 'User Name Exist', '500': 'Internal Server Error'}


class ChatHTTP:
    """

    """
    def __init__(self):
        self.http_version = 'HTTP/1.1'
        self.generalHeader = GeneralHeader()
        self.entityHeader = EntityHeader()
        self.entity = None

    def set_entity(self, entity):
        self.entity = entity

    def pack(self):
        pass

    def unpack(self, raw_content):
        pass



class Header:
    """

    """
    def __init__(self):
        self.key_value = dict()

    def pack(self):
        result = ''
        for key, value in self.key_value.iteritems():
            result += (str(key) + ': ' + str(value) + '\n')
        return result

    def unpack(self, lines):
        for line in lines:
            parts = line.split(': ', 1)
            self.key_value[parts[0]] = parts[1]


class GeneralHeader(Header):
    """

    """
    def __init__(self):
        Header.__init__(self)
        self.key_value['Datetime'] = None

    def set_value(self, dict):
        self.key_value = dict

class RequestHeader(Header):
    """

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

    """
    def __init__(self):
        Header.__init__(self)
        self.key_value['Server'] = None
        self.key_value['Developer'] = None

    def set_value(self, dict):
        self.key_value = dict


class EntityHeader(Header):
    """

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

