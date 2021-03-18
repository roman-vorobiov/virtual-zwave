from zwave import Daemon

import signal
import asyncio
from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser(description="Emulate Z-Wave controller", allow_abbrev=False)

    parser.add_argument('--link', type=str, required=True,
                        help="symbolic link to the pseudo TTY device")

    parser.add_argument('--port', type=int, default=8765,
                        help="websocket server port")

    return parser.parse_args()


def main():
    args = parse_args()

    daemon = Daemon(args.link, args.port)

    for sig in [signal.SIGINT, signal.SIGTERM]:
        asyncio.get_event_loop().add_signal_handler(sig, daemon.stop)

    asyncio.get_event_loop().run_until_complete(daemon.run())
    asyncio.get_event_loop().close()


if __name__ == '__main__':
    main()
