
TX_FEE_THRESHOLD = 1000

SIZE_TX_HEADER = 10
SIZE_TX_INPUT  = 130
SIZE_TX_OUTPUT = 37

def required_surplus(size):
    return int(2**(size/TX_FEE_THRESHOLD)) - 1