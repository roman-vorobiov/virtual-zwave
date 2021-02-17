from zwave import Daemon

from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser(description="Emulate Z-Wave controller", allow_abbrev=False)

    parser.add_argument('--link', type=str, required=True,
                        help="symbolic link to the pseudo TTY device")

    return parser.parse_args()


def main():
    args = parse_args()

    daemon = Daemon(args.link)
    daemon.run()


if __name__ == '__main__':
    main()
