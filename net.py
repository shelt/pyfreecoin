#!/usr/bin/env python
import atexit
import socketserver
import threading

from freecoin.util import _VERSION_
from freecoin import logger

MAX_MSG_SIZE = 1024*1024
PORT         = 64720 # hex:fcd0

CTYPE_REJECT    = 0
CTYPE_GETBLOCKS = 1
CTYPE_MEMPOOL   = 2
CTYPE_INV       = 3
CTYPE_GETDATA   = 4
CTYPE_BLOCK     = 5
CTYPE_TX        = 6
CTYPE_PEER      = 7
CTYPE_ALERT     = 8
CTYPE_PING      = 9
CTYPE_PONG      = 10

DTYPE_BLOCK = 0
DTYPE_TX    = 1
DTYPE_PEERS = 2

OTYPE_WARNUSER    = 0 # Display a warning to the user, visible at all times.
OTYPE_FORCEUPDATE = 1 # Do not allow user to do anything until the client is updated.

# P2P network connection
class Network():
    def __init__(self):
        self.server = _Server(self, ("localhost",PORT), _ServerHandler)
        self.peers = []
        atexit.register(self.shutdown)

    def serve(self):
        threading.Thread(target=self.server.serve_forever).start()

    def shutdown(self):
        for peer in self.peers:
            peer.sock.close()
        self.peers = []
        self.server.shutdown()

    def connect(self, addr, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((addr,port)) #TODO try block and handle failure
        peer = peer(sock, addr, port)
        peer.handle()
        peers.append(peer)

# Server handler
class _ServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        peer = Peer(self.request, self.client_address[0], 0)
        self.server.network.peers.append(peer)
        peer.handle()

# Server
class _Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, network, inet_addr, handler):
        super().__init__(inet_addr, handler)
        self.network = network

# Peer
class Peer:
    def __init__(self, sock, addr, port):
        self.sock = sock
        self.addr = addr
        self.port = port
        self.queue = []

        self.receivers = {
            0:self.recv_reject,
            1:self.recv_getblocks,
            2:self.recv_mempool,
            3:self.recv_inv,
            4:self.recv_getdata,
            5:self.recv_block,
            6:self.recv_tx,
            7:self.recv_peer,
            8:self.recv_alert,
            9:self.recv_ping,
            10:self.recv_pong
        }

    def shutdown(self):
        self.sock.close()

    def handle(self):
        logger.verbose("New peer: %s" % (self.addr))
        try:
            while True:
                data = self.sock.recv(MAX_MSG_SIZE)
                if data == b"":
                    break

                vers = int.from_bytes(data[2:4], byteorder='big')
                if vers != _VERSION_:
                    self.send_reject(ERR_BAD_VERSION)
                    continue

                ctype = int.from_bytes(data[4], byteorder='big')
                if ctype not in processors:
                    self.send_reject(ERR_UNKNOWN_CTYPE)
                    continue

                self.receivers[ctype](data[5:])
        except Exception as e:
            self.shutdown()
            logger.error("Peer death: " + str(e))


    def recv_reject(self, data):
        if len(data) > 0:
            e_type = data[0]
            e_str = data[1:]
            print("reject receive: [%d] %s" % (e_type, e_str))
        else:
            print("reject receive: [untitled]")

    def recv_getblocks(self, data):
        if len(data) < 33:
            self.send_reject(ERR_MESSAGE_MALFORMED, info="getblocks")
            return
        
        start = data[0:32]
        count = data[32]
        
        block = tc.Block.load(start)
        i = 0
        while block is not None and i<count:
            self.send_block(block)
            block = tc.Block.load(block.prev_hash)
            i += 1

    def recv_mempool(self, data):
        self.network.mempool.

    def recv_inv(self, data):
        pass

    def recv_getdata(self, data):
        pass

    def recv_block(self, data):
        pass

    def recv_tx(self, data):
        pass

    def recv_peer(self, data):
        pass

    def recv_alert(self, data):
        pass

    def recv_ping(self, data):
        pass

    def recv_pong(self, data):
        pass

    # Send methods
    
    def send_reject(self, etype, info=""):
        self.send(CTYPE_REJECT, etype.to_bytes(1, byteorder='big') + info.encode("ascii"))

    def send_getblocks(self, block_hash, count):
        self.send(CTYPE_GETBLOCKS, block_hash + count.to_bytes(1, byteorder='big'))

    def send_mempool(self):
        self.send(CTYPE_MEMPOOL, "")

    def send_inv(self, dtype, ids):
        self.send(CTYPE_INV, dtype.to_bytes(1, byteorder='big').join([id.encode("ascii") for id in ids]))

    def send_getdata(self, dtype, ids):
        self.send(CTYPE_GETDATA, dtype.to_bytes(1, byteorder='big').join([id.encode("ascii") for id in ids]))

    def send_block(self, block):
        bytes = block.serialize()
        self.send(CTYPE_BLOCK, len(bytes).to_bytes(1, byteorder='big') + bytes)

    def send_tx(self, tx):
        bytes = tx.serialize()
        self.send(CTYPE_TX, len(bytes).to_bytes(1, byteorder='big') + bytes)

    def send_peer(self, peer):
        bytes = peer.serialize()
        self.send(CTYPE_PEER, len(bytes).to_bytes(1, byteorder='big') + bytes)

    def send_alert(self, atype, otype, time, msg):
        with open(os.path.join(DIR_STORAGE, "adminkey")) as f:
            adminkey = ecdsa.SigningKey.generate().from_pem(f.read())
        doc = atype.to_bytes(1, byteorder='big')  +
              otype.to_bytes(1, byteorder='big')  + 
              time().to_bytes(4, byteorder='big') + 
              msg.encode("ascii")
        self.send(CTYPE_ALERT, len(msg).to_bytes(1, byteorder='big') + adminkey.sign(doc) + doc)

    def send_ping(self, data):
        self.send(CTYPE_PING, "")
        pass

    def send_pong(self, data):
        self.send(CTYPE_PONG, "")
        pass
