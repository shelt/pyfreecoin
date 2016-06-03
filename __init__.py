import os

_VERSION_ = 2
MINING_REWARD = 100

# Storage
if os.name == 'nt':
    DIR_STORAGE = os.path.join(os.getenv('APPDATA'), "freecoin/")
else:
    DIR_STORAGE = os.path.join(os.getenv('HOME'), ".freecoin/")
DIR_BLOCKS      = os.path.join(DIR_STORAGE, "blocks/")
DIR_TXINDEX     = os.path.join(DIR_STORAGE, "txindex/")
DIR_KEYS        = os.path.join(DIR_STORAGE, "private/")
DIR_HEADS       = os.path.join(DIR_STORAGE, "heads/")

# Classes
from freecoin.classes.block       import Block
from freecoin.classes.transaction import Tx
from freecoin.classes.transaction import TxInput
from freecoin.classes.transaction import TxOutput
from freecoin.classes.miner       import Miner
from freecoin.classes.key         import Key
from freecoin.classes.net         import Network
from freecoin.classes.net         import Peer

# Source files
import freecoin.chain
import freecoin.logger
import freecoin.net
import freecoin.admin




def init():
    for dir in [DIR_STORAGE, DIR_BLOCKS, DIR_TXINDEX, DIR_KEYS, DIR_HEADS]:
        os.makedirs(dir, exist_ok=True)