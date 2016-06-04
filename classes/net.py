import os,sys
import atexit
import socket
import socketserver
import threading
from binascii import hexlify
import freecoin as fc
from freecoin.net import *

# P2P network connection
class Network():
    def __init__(self,port=PORT):
        self.server = _Server(self, ("localhost",port), _ServerHandler)
        self.peers = []
        self.mempool = {}
        atexit.register(self.shutdown)

    def serve(self):
        thread = threading.Thread(target=self.server.serve_forever)
        thread.daemon = True
        thread.start()
        
        # Initial peer
        if len(self.peers) == 0:
            with open(fc.FILE_KNOWNPEERS) as f:
                known = [s.strip().split(":") for s in f.read().split("\n")]
        for addr,port in known:
            if self.connect(addr, int(port)):
                return

    def shutdown(self):
        for peer in self.peers:
            peer.sock.close()
        self.peers = []
        self.server.shutdown()

    def connect(self, addr, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((addr,port)) #TODO try block and handle failure
            peer = Peer(self, sock, addr, port)
            thread = threading.Thread(target=peer.handle)
            thread.daemon = True
            thread.start()
            self.peers.append(peer)
            return True
        except TimeoutError:
            fc.logger.error("net: connecting timed out by %s:%d" % (addr,port))
            sock.close()
            return False
        except ConnectionRefusedError:
            fc.logger.error("net: connecting refused by %s:%d" % (addr,port))
            sock.close()
            return False
    
    def is_stable(self):
        return len(self.peers) >= 4

# Server handler
class _ServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        peer = Peer(self.server.network, self.request, self.client_address[0], 0)
        self.server.network.peers.append(peer)
        peer.handle()

# Server
class _Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, network, inet_addr, handler):
        super().__init__(inet_addr, handler)
        self.network = network

# Peer
class Peer:
    def __init__(self, network, sock, addr, port):
        self.network = network
        self.sock = sock
        self.addr = addr
        self.port = port
        self.queue = []

        self.receivers = {
            0:self.recv_reject,
            1:self.recv_gethighest,
            2:self.recv_getchain,
            3:self.recv_mempool,
            4:self.recv_inv,
            5:self.recv_getdata,
            6:self.recv_block,
            7:self.recv_tx,
            8:self.recv_peer,
            9:self.recv_alert,
            10:self.recv_ping,
            11:self.recv_pong
        }

    def shutdown(self):
        self.sock.close()
    
    def to_bytes(self):
        addr = self.addr.encode("ascii")
        bytes = b""
        bytes += self.port.to_bytes(2, byteorder='big')
        bytes += len(addr).to_bytes(1, byteorder='big')
        bytes += addr
        return bytes
    
    @staticmethod
    def from_bytes(bytes):
        port = int.from_bytes(bytes[:2], byteorder='big')
        size = int.from_bytes(bytes[2:3], byteorder='big')
        addr = bytes[3:3+size].decode("ascii")
        return (addr,port)
        

    def handle(self):
        fc.logger.verbose("net: New peer: %s:%d" % (self.addr,self.port))
        self.send_getdata(DTYPE_PEER, [])
        try:
            while True:
                data = self.sock.recv(MAX_MSG_SIZE)
                if data == b"":
                    break
                
                vers = int.from_bytes(data[4:6], byteorder='big')
                if vers != fc._VERSION_:
                    self.send_reject(ERR_BAD_VERSION)
                    continue

                ctype = int.from_bytes(data[6:7], byteorder='big')
                if ctype not in self.receivers:
                    self.send_reject(ERR_BAD_CTYPE)
                    continue
                else:
                    self.receivers[ctype](data[7:])
        except ConnectionResetError as e:
            self.shutdown()
            fc.logger.error("Peer death: " + str(e))


    def recv_reject(self, data):
        if len(data) == 0:
            fc.logger.verbose("net: recieve <reject>")
        else:
            e_type = data[0]
            e_str = data[1:]
            fc.logger.warn("net: recieve <reject> [%d] \"%s\"" % (e_type, e_str.decode("ascii")))
    
    def recv_gethighest(self, data):
        fc.logger.verbose("net: recieve <gethighest>")
        self.send_inv(DTYPE_BLOCK, [fc.chain.get_highest_chained_hash()])

    def recv_getchain(self, data):
        fc.logger.verbose("net: recieve <getchain>")
        if len(data) < 33:
            self.send_reject(ERR_MESSAGE_MALFORMED, info="getchain too short")
            return
        
        start = data[0:32]
        count = data[32]
        
        block = tc.Block.from_file(start)
        i = 0
        while block is not None and i<count:
            self.send_block(block)
            block = tc.Block.from_file(block.prev_hash)
            i += 1

    def recv_mempool(self, data):
        fc.logger.verbose("net: recieve <mempool>")
        self.send_inv(DTYPE_TX, [tx.compute_hash() for tx in self.network.mempool.keys()])

    def recv_inv(self, data):
        fc.logger.verbose("net: recieve <inv>")
        if len(data) < 34:
            self.send_reject(ERR_MESSAGE_MALFORMED, info="inv too short")
            return
        dtype = data[0]
        count = data[1]
        hashl = data[2:]
        if len(hashl) > 32*255:
            return # TODO resp with error
        if len(hashl) % 32 != 0:
            return # TODO resp with error
        hashes = fc.util.divide(hashl, 32)
        
        if dtype == DTYPE_BLOCK:
            #blacklisted = lambda h: fc.is_block_blacklisted(h) TODO
            dirname   = fc.DIR_BLOCKS
        elif dtype == DTYPE_TX:
            #blacklisted = lambda h: False # TODO: Txs should not be blacklisted
            dirname   = fc.DIR_TX
        else:
            return #TODO resp with error
        
        needed = []
        for hash in hashes:
            #if blacklisted(hash):
            #    continue
            if hexlify(hash).decode("ascii") not in os.listdir(dirname):
                needed.append(hash)
        
        if len(needed) > 0:
            self.send_getdata(dtype, needed)
        

    def recv_getdata(self, data):
        fc.logger.verbose("net: recieve <getdata>")
        if len(data) == 0:
            self.send_reject(ERR_MESSAGE_MALFORMED, info="getdata without dtype")
            return
        elif data[0] == DTYPE_PEER:
            for peer in self.network.peers:
                self.send_peer(peer)
            return
        elif len(data) < 34:
            self.send_reject(ERR_MESSAGE_MALFORMED, info="getdata too short")
            return
        dtype = data[0]
        count = data[1]
        hashl = data[2:]
        
        if len(hashl) > 32*255:
            return # TODO resp with error
        if (len(hashl) % 32) != 0:
            return # TODO resp with error
        hashes = fc.util.divide(hashl,32)
        
        if dtype == DTYPE_BLOCK:
            for hash in hashes:
                block = fc.Block.from_file(hash)
                if block is not None:
                    self.send_block(block)
        elif dtype == DTYPE_TX:
            for hash in hashes:
                tx = fc.Tx.from_file(hash)
                if tx is not None:
                    self.send_tx(tx)
        else:
            return #TODO resp with error
        
    def recv_block(self, data):
        fc.logger.verbose("net: recieve <block>")
        block = fc.Block.from_bytes(data)
        if block is None:
            return #TODO resp with error
        if fc.is_block_blacklisted(block.compute_hash()):
            return #TODO resp with error
        if not block.is_pseudo_valid():
            return #TODO resp with error
        else:
            tc.chain.enchain(block)

    def recv_tx(self, data):
        fc.logger.verbose("net: recieve <tx>")
        tx = Tx.from_bytes(data)
        if tx is None:
            return #TODO resp with error
        if not tx.is_pseudo_valid():
            return #TODO resp with error
        hash = tx.compute_hash()
        if hash not in self.network.mempool:
            self.network.mempool[tx.compute_hash()] = tx

    def recv_peer(self, data):
        fc.logger.warn("Recieved <peer>, please implement functionality") #TODO

    def recv_alert(self, data):
        fc.logger.warn("Recieved <alert>, please implement functionality") #TODO

    def recv_ping(self, data):
        fc.logger.warn("Recieved <ping>, please implement functionality") #TODO

    def recv_pong(self, data):
        fc.logger.warn("Recieved <pong>, please implement functionality") #TODO

    # Send methods
    
    def send_reject(self, etype, info=""):
        self.send(CTYPE_REJECT, etype.to_bytes(1, byteorder='big') + info.encode("ascii"))

    def send_gethighest(self):
        self.send(CTYPE_GETHIGHEST, b"")
        
    def send_getchain(self, block_hash, count):
        self.send(CTYPE_GETCHAIN, block_hash + count.to_bytes(1, byteorder='big'))

    def send_mempool(self):
        self.send(CTYPE_MEMPOOL, b"")

    def send_inv(self, dtype, ids):
        self.send(CTYPE_INV, dtype.to_bytes(1, byteorder='big') + len(ids).to_bytes(1, byteorder='big') + b"".join([id.encode("ascii") if type(id) is str else id for id in ids]))

    def send_getdata(self, dtype, ids):
        self.send(CTYPE_GETDATA, dtype.to_bytes(1, byteorder='big') + len(ids).to_bytes(1, byteorder='big') + b"".join([id.encode("ascii") if type(id) is str else id for id in ids]))

    def send_block(self, block):
        bytes = block.to_bytes()
        self.send(CTYPE_BLOCK, len(bytes).to_bytes(1, byteorder='big') + bytes)

    def send_tx(self, tx):
        bytes = tx.to_bytes()
        self.send(CTYPE_TX, len(bytes).to_bytes(1, byteorder='big') + bytes)

    def send_peer(self, peer):
        bytes = peer.to_bytes()
        self.send(CTYPE_PEER, len(bytes).to_bytes(1, byteorder='big') + bytes)

    def send_alert(self, atype, otype, time, msg):
        with open(os.path.join(DIR_STORAGE, "admin_secret")) as f:
            adminkey = ecdsa.SigningKey.generate().from_pem(f.read())
        doc = atype.to_bytes(1, byteorder='big')  + \
              otype.to_bytes(1, byteorder='big')  + \
              int(time()).to_bytes(4, byteorder='big') + \
              msg.encode("ascii")
        self.send(CTYPE_ALERT, len(msg).to_bytes(1, byteorder='big') + adminkey.sign(doc) + doc)

    def send_ping(self, data):
        self.send(CTYPE_PING, b"")
        pass

    def send_pong(self, data):
        self.send(CTYPE_PONG, b"")
        pass

    def send(self, ctype, body):
        bytes = b""
        bytes += len(body).to_bytes(4, byteorder='big')
        bytes += fc._VERSION_.to_bytes(2, byteorder='big')
        bytes += ctype.to_bytes(1, byteorder='big')
        bytes += body
        self.sock.sendall(bytes)