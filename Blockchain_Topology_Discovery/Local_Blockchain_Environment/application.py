"""
User-level application (stub).

NB: Feel free to extend or modify.
"""

import argparse
import termios
import tty


from keychain.store import *


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def main(arguments):
    storage = allocate_application(arguments)

    storage.start()

    while storage.is_alive():
        char = getch()

        if char == "q":
            break

    storage.join()

    os.system("clear")


def allocate_application(arguments):
    application = Storage(
        src_ip=arguments.src_ip,
        src_port=arguments.src_port,
        src_service=arguments.src_service,
        network=arguments.network,
        bootstrap=arguments.bootstrap,
        miner=arguments.miner,
        difficulty=arguments.difficulty,
        monitor=arguments.monitor,
        time_before_transaction_distribution=arguments.time_before_transaction_distribution)

    return application


def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")

    parser.add_argument("--src_ip", type=str, required=True, nargs='?',
                        const=True, help="IP Address of the peer.")

    parser.add_argument("--src_port", type=int, default=8000, nargs='?',
                        const=True, help="Port of the peer.")

    parser.add_argument("--src_service", type=int, default=Protocol.Protocol_Constant.NODE_NETWORK, nargs='?',
                        const=True, help="Service provided by the peer to the network.")

    parser.add_argument("--network", type=str, default="mainnet", nargs='?',
                        const=True, help="Network on which the peer will be active.")

    parser.add_argument("--time_before_transaction_distribution", type=int, default=[10, 100], nargs=2,
                        help="Parameters of the log-normal probability distribution of the "
                             "time_to_crawl before a transaction is added to the blockchain.")

    parser.add_argument("--miner", type=bool, default=False, nargs='?',
                        const=True, help="Starts the mining procedure.")

    parser.add_argument("--monitor", type=bool, default=False, nargs='?',
                        const=True, help="Start the monitoring procedure.")

    parser.add_argument("--bootstrap", type=str, default=[], nargs='+',
                        help="Sets the address of the bootstrap node.")

    parser.add_argument("--difficulty", type=int, default=5,
                        help="Sets the difficulty of Proof of Work, only has "
                             "an effect with the `--miner` flag has been set.")

    arguments, _ = parser.parse_known_args()

    return arguments


if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
