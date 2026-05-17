#!/usr/bin/env python3
# encoding: utf-8
"""
Proxy HTTP/SOCKS simple para SSHPLUS BY El NeNe.
Compatible con Python 3. Acepta el puerto como argumento posicional o con -p/--port.
Encamina por defecto a 127.0.0.1:22 y también respeta el header X-Real-Host.
"""
import getopt
import select
import socket
import sys
import threading
import time

LISTENING_ADDR = '0.0.0.0'
try:
    LISTENING_PORT = int(sys.argv[1])
except Exception:
    LISTENING_PORT = 8080

PASS = ''
BUFLEN = 4096 * 4
TIMEOUT = 60
MSG = ''
COR = '<font color="null">'
FTAG = '</font>'
DEFAULT_HOST = '127.0.0.1:1194'
RESPONSE = 'HTTP/1.1 200 ' + str(COR) + str(MSG) + str(FTAG) + '\r\n\r\n'


def to_text(data):
    if isinstance(data, bytes):
        return data.decode('utf-8', 'ignore')
    return data or ''


def to_bytes(data):
    if isinstance(data, bytes):
        return data
    return str(data).encode('utf-8')


class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__(daemon=True)
        self.running = False
        self.host = host
        self.port = int(port)
        self.threads = []
        self.threadsLock = threading.Lock()
        self.logLock = threading.Lock()
        self.soc = None

    def run(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.settimeout(2)
        self.soc.bind((self.host, self.port))
        self.soc.listen(128)
        self.running = True
        try:
            while self.running:
                try:
                    client, addr = self.soc.accept()
                    client.setblocking(True)
                except socket.timeout:
                    continue
                except OSError:
                    break
                conn = ConnectionHandler(client, self, addr)
                conn.start()
                self.addConn(conn)
        finally:
            self.running = False
            try:
                self.soc.close()
            except Exception:
                pass

    def printLog(self, log):
        with self.logLock:
            print(log, flush=True)

    def addConn(self, conn):
        with self.threadsLock:
            if self.running:
                self.threads.append(conn)

    def removeConn(self, conn):
        with self.threadsLock:
            if conn in self.threads:
                self.threads.remove(conn)

    def close(self):
        self.running = False
        with self.threadsLock:
            threads = list(self.threads)
        for conn in threads:
            conn.close()
        try:
            if self.soc:
                self.soc.close()
        except Exception:
            pass


class ConnectionHandler(threading.Thread):
    def __init__(self, socClient, server, addr):
        super().__init__(daemon=True)
        self.clientClosed = False
        self.targetClosed = True
        self.client = socClient
        self.client_buffer = b''
        self.server = server
        self.log = 'Conexión: ' + str(addr)
        self.target = None

    def close(self):
        if not self.clientClosed:
            try:
                self.client.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.client.close()
            except Exception:
                pass
            self.clientClosed = True
        if not self.targetClosed and self.target:
            try:
                self.target.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.target.close()
            except Exception:
                pass
            self.targetClosed = True

    def run(self):
        try:
            self.client_buffer = self.client.recv(BUFLEN)
            head = to_text(self.client_buffer)
            hostPort = self.findHeader(head, 'X-Real-Host') or DEFAULT_HOST
            split = self.findHeader(head, 'X-Split')
            if split:
                self.client.recv(BUFLEN)
            passwd = self.findHeader(head, 'X-Pass')

            if PASS and passwd == PASS:
                self.method_CONNECT(hostPort)
            elif PASS and passwd != PASS:
                self.client.sendall(b'HTTP/1.1 400 WrongPass!\r\n\r\n')
            elif hostPort.startswith(('127.0.0.1', 'localhost', '0.0.0.0')):
                self.method_CONNECT(hostPort)
            else:
                self.client.sendall(b'HTTP/1.1 403 Forbidden!\r\n\r\n')
        except Exception as exc:
            self.log += ' - error: ' + str(exc)
            self.server.printLog(self.log)
        finally:
            self.close()
            self.server.removeConn(self)

    @staticmethod
    def findHeader(head, header):
        prefix = header + ': '
        aux = head.find(prefix)
        if aux == -1:
            return ''
        aux = head.find(':', aux)
        head = head[aux + 2:]
        aux = head.find('\r\n')
        if aux == -1:
            return ''
        return head[:aux].strip()

    def connect_target(self, host):
        if ':' in host:
            hostname, port_text = host.rsplit(':', 1)
            port = int(port_text)
        else:
            hostname = host
            port = 22
        info = socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM)[0]
        family, socktype, proto, _, address = info
        self.target = socket.socket(family, socktype, proto)
        self.targetClosed = False
        self.target.settimeout(15)
        self.target.connect(address)
        self.target.settimeout(None)

    def method_CONNECT(self, path):
        self.log += ' - CONNECT ' + path
        self.connect_target(path)
        self.client.sendall(to_bytes(RESPONSE))
        self.client_buffer = b''
        self.server.printLog(self.log)
        self.doCONNECT()

    def doCONNECT(self):
        sockets = [self.client, self.target]
        idle_count = 0
        while True:
            idle_count += 1
            readable, _, errors = select.select(sockets, [], sockets, 3)
            if errors:
                break
            if readable:
                for sock in readable:
                    try:
                        data = sock.recv(BUFLEN)
                        if not data:
                            return
                        if sock is self.target:
                            self.client.sendall(data)
                        else:
                            self.target.sendall(data)
                        idle_count = 0
                    except Exception:
                        return
            if idle_count >= TIMEOUT:
                break


def print_usage():
    print('Uso: proxy.py <puerto>')
    print('     proxy.py -p <puerto>')
    print('     proxy.py -b 0.0.0.0 -p 80')


def parse_args(argv):
    global LISTENING_ADDR, LISTENING_PORT
    if len(argv) == 1 and argv[0].isdigit():
        LISTENING_PORT = int(argv[0])
        return
    try:
        opts, _ = getopt.getopt(argv, 'hb:p:', ['bind=', 'port='])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit(0)
        if opt in ('-b', '--bind'):
            LISTENING_ADDR = arg
        elif opt in ('-p', '--port'):
            LISTENING_PORT = int(arg)


def main():
    print('\n━━━━━━━━ PROXY OPENVPN SSHPLUS ━━━━━━━━')
    print('IP:    ' + LISTENING_ADDR)
    print('Puerto:' , LISTENING_PORT)
    print('Destino por defecto: ' + DEFAULT_HOST)
    print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n', flush=True)
    server = Server(LISTENING_ADDR, LISTENING_PORT)
    server.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print('\nParando...')
        server.close()


if __name__ == '__main__':
    parse_args(sys.argv[1:])
    main()
