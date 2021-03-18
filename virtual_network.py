from network import Daemon

import asyncio
from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser(description="Emulate Z-Wave network", allow_abbrev=False)

    parser.add_argument('--port', type=int, default=8765,
                        help="websocket server port")

    return parser.parse_args()


def main():
    args = parse_args()

    daemon = Daemon(args.port)

    asyncio.run(daemon.run())


if __name__ == '__main__':
    main()
