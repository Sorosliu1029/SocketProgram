__author__ = 'liuyang'
'''
An event-driven approach to serving several client with poll().
'''

import launcelot
import select

listen_sock = launcelot.setup()
sockets = {listen_sock.fileno() : listen_sock}
requests = {}
responses = {}

poll = select.poll()
poll.register(listen_sock, select.POLLIN)

while True:
    for fd, event in poll.poll():
        sock = sockets[fd]
        # remove closed sockets from our list
        if event & (select.POLIHUP | select.POLIERR | select.POLINVAL):
            poll.unregister(fd)
            del sockets[fd]
            requests.pop(sock, None)
            responses.pop(sock, None)

        # accept connection from new sockets
        elif sock is listen_sock:
            newsock, sockname = sock.accept()
            newsock.setblocking(False)
            fd = newsock.fileno()
            sockets[fd] = newsock
            poll.register(fd, select.POLLIN)
            requests[newsock] = ''

        # collect incoming data until it forms a question
        elif event & select.POLLIN:
            data = sock.recv(4096)
            if not data:
                sock.close()
                continue
            requests[sock] += data.replace('\r\n', '')
            if '?' in requests[sock]:
                question = requests.pop(sock)
                answer = dict(launcelot.qa)[question]
                poll.modify(sock, select.POLLOUT)
                responses[sock] = answer

        # send out pieces of each reply until they are all sent
        elif event & select.POLLOUT:
            response = responses.pop(sock)
            n = sock.send(response)
            if n < len(response):
                responses[sock] = response[n:]
            else:
                poll.modify(sock, select.POLLIN)
                requests[sock] = ''


