import atexit
import socketserver
import threading

import freecoin as fc
from freecoin.net import *

# P2P network connection
class Network():
    def __init__(self):
        self.server = _Server(self, ("localhost",PORT), _ServerHandler)
        self.peers = []
        atexit.register(self.shutdown)

    def serve(self):
        thread = threading.Thread(target=self.server.serve_forever)
        thread.daemon = True
        thread.start()

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
        fc.logger.verbose("New peer: %s" % (self.addr))
        try:
            while True:
                data = self.sock.recv(MAX_MSG_SIZE)
                if data == b"":
                    break

                vers = int.from_bytes(data[2:4], byteorder='big')
                if vers != fc._VERSION_:
                    self.send_reject(ERR_BAD_VERSION)
                    continue

                ctype = int.from_bytes(data[4], byteorder='big')
                if ctype not in processors:
                    self.send_reject(ERR_UNKNOWN_CTYPE)
                    continue

                self.receivers[ctype](data[5:])
        except Exception as e:
            self.shutdown()
            fc.logger.error("Peer death: " + str(e))


    def recv_reject(self, data):
        if len(data) > 0:
            e_type = data[0]
            e_str = data[1:]
            print("reject receive: [%d] %s" % (e_type, e_str))
        else:
            print("reject receive: [untitled]")
    
    def recv_gethighest(self, data):
        self.send_inv(DTYPE_BLOCK, [fc.chain.get_highest_chained_hash()])

    def recv_getchain(self, data):
        if len(data) < 33:
            self.send_reject(ERR_MESSAGE_MALFORMED, info="getchain")
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
        self.send_inv(DTYPE_TX, [tx.compute_hash() for tx in self.network.mempool.keys()])

    def recv_inv(self, data):
        dtype = data[0]
        count = data[1]
        hashl = data[2:]
        if len(hashl) > 32*255:
            return # TODO resp with error
        if len(hashl) % 32 is not 0:
            return # TODO resp with error
        hashes = fc.util.divide(hashl, 32)
        
        if dtype is DTYPE_BLOCK:
            blacklisted = lambda h: fc.is_block_blacklisted(h)
            dirname   = fc.DIR_BLOCKS
        elif dtype is DTYPE_TX:
            blacklisted = lambda h: False # TODO: Txs should not be blacklisted
            dirname   = fc.DIR_TX
        else:
            return #TODO resp with error
        
            for hash in hashes:
                if blacklisted(hash):
                    continue
                if hash not in os.listdir(dirname):
                    needed.append(hash)
        
        self.send_getdata(dtype, needed)
        

    def recv_getdata(self, data):
        dtype = data[0]
        count = data[1]
        hashl = data[2:]
        
        if dtype is DTYPE_PEER:
            for peer in self.network.peers:
                self.send_peer(peer)
            return
        
        if len(hashes) > 32*255:
            return # TODO resp with error
        if len(hashes) % 32 is not 0:
            return # TODO resp with error
        hashes = fc.util.divide(hashl,32)
        
        if dtype is DTYPE_BLOCK:
            for hash in hashes:
                block = fc.Block.load(hash)
                if block is not None:
                    self.send_block(block)
        elif dtype is DTYPE_TX:
            for hash in hashes:
                tx = fc.Tx.load(hash)
                if tx is not None:
                    self.send_tx(tx)
        else:
            return #TODO resp with error
        
    def recv_block(self, data):
        block = Block.from_bytes(data)
        if block is None:
            return #TODO resp with error
        if fc.is_block_blacklisted(block.compute_hash()):
            return #TODO resp with error
        if not block.is_pseudo_valid():
            return #TODO resp with error
        else:
            tc.chain.enchain(block)

    def recv_tx(self, data):
        tx = Tx.from_bytes(data)
        if tx is None:
            return #TODO resp with error
        if not tx.is_pseudo_valid():
            return #TODO resp with error
        hash = tx.compute_hash()
        if hash not in self.network.mempool:
            self.network.mempool[tx.compute_hash()] = tx

    def recv_peer(self, data):
        pass#TODO

    def recv_alert(self, data):
        pass#TODO

    def recv_ping(self, data):
        pass#TODO

    def recv_pong(self, data):
        pass#TODO

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
        with open(os.path.join(DIR_STORAGE, "admin_secret")) as f:
            adminkey = ecdsa.SigningKey.generate().from_pem(f.read())
        doc = atype.to_bytes(1, byteorder='big')  + \
              otype.to_bytes(1, byteorder='big')  + \
              int(time()).to_bytes(4, byteorder='big') + \
              msg.encode("ascii")
        self.send(CTYPE_ALERT, len(msg).to_bytes(1, byteorder='big') + adminkey.sign(doc) + doc)

    def send_ping(self, data):
        self.send(CTYPE_PING, "")
        pass

    def send_pong(self, data):
        self.send(CTYPE_PONG, "")
        pass
