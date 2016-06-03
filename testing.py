from binascii import hexlify,unhexlify
import freecoin as fc


def conv_txs():
    input = fc.TxInput()
    input.out_index = 0
    input.ref_tx = b"\xff\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\x32\xff"
    input.pubkey      = b"\xff\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\xff"
    input.sig      = b"\xff\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\x48\xff"
    
    output = fc.TxOutput()
    output.out_addr = b"\xff\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\xff"
    output.amount   = 42
    
    tx = fc.Tx()
    tx.version   = 2
    tx.lock_time = 0
    tx.ins       = [input]
    tx.outs      = [output]
    
    print(tx.to_bytes() == fc.Tx.from_bytes(tx.to_bytes()).to_bytes())
    

    
def all():
    conv_txs()