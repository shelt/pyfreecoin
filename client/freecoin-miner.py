import sys
import freecoin

if __name__ == "__main__":
    freecoin.init()
    if len(sys.argv) is not 2:
        sys.exit("Usage: %s <address>" % sys.argv[0])

    net = freecoin.Network()
    net.serve()

    miner = freecoin.Miner(net)
    try:
        miner.slow_mine(sys.argv[1])
    except KeyboardInterrupt:
        net.shutdown()