import sys
import freecoin

def genaddr():
    key = freecoin.Key()
    key.to_file()
    freecoin.logger.info("New address [%s]" % key.addr)


if __name__ == "__main__":
    freecoin.init()

    if len(sys.argv) < 2:
        sys.exit("Usage: %s <command> [parameters..] [options..]" % sys.argv[0])

    cmd = sys.argv[1]
    if cmd not in globals():
        sys.exit("Unknown command: %s" % cmd)

    eval(cmd)(*sys.argv[2:])
