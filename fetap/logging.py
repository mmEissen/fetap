import logging


def configure() -> None:
    logging.basicConfig(format="{threadName}: {message}", style="{", level=logging.DEBUG, force=True)