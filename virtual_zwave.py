from zwave import ZwaveDaemon

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

    daemon = ZwaveDaemon(link=args.link, port=args.port)
    daemon.run()


if __name__ == '__main__':
    main()
