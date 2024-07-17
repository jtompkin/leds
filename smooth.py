#!/usr/bin/env python3
import datetime
import argparse
import logging.config
from time import sleep

import board
import neopixel

# pyright: basic

logger = logging.getLogger("smooth")

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s|%(asctime)s: %(message)s"},
        "detailed": {
            "format": "[%(levelname)s|L%(lineno)d] %(asctime)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/smooth.log",
            "maxBytes": 1024 * 1024 * 8,
            "backupCount": 3,
        },
    },
    "loggers": {"root": {"level": "DEBUG", "handlers": ["file", "stdout"]}},
}


class Pixels:
    def __init__(
        self, pixels: neopixel.NeoPixel, min: int, max: int, duration: int
    ) -> None:
        self.pixels = pixels
        self.min = min
        self.max = max
        self.duration = duration

    def dim(self):
        logger.info("Beginning dusk")
        self.pixels.fill((self.max, self.max, self.max))
        proportion = 1
        delta = (1 / self.duration) * (1 - self.min / (self.max + 1))
        for _ in range(self.duration):
            proportion -= delta
            c = self.max * proportion
            self.pixels.fill((c, c, c))
            logger.debug(c)
            sleep(1)
        self.pixels.fill((self.min, self.min, self.min))
        logger.info("Dusk complete")

    def brighten(self):
        logger.info("Beginning dawn")
        self.pixels.fill((self.min, self.min, self.min))
        proportion = 0
        delta = (1 / self.duration) * (1 - self.min / (self.max + 1))
        for _ in range(self.duration):
            proportion += delta
            c = self.min + self.max * proportion
            self.pixels.fill((c, c, c))
            logger.debug(c)
            sleep(1)
        self.pixels.fill((self.max, self.max, self.max))
        logger.info("Dawn complete")


def loop(pixels: Pixels, dawn_time: datetime.datetime, duration: int) -> None:
    day = 1
    while True:
        logger.info(f"starting day {day}")
        now = datetime.datetime.now()
        logger.info(f"current time set to {now}")
        dawn = datetime.datetime(
            now.year, now.month, now.day, dawn_time.hour, dawn_time.minute
        )
        if now.timestamp() > dawn.timestamp():
            dawn += datetime.timedelta(1)
        logger.info(f"dawn will occur at {dawn}")
        dusk = dawn - datetime.timedelta(hours=12)
        if now.timestamp() > dusk.timestamp():
            dusk += datetime.timedelta(1)
        logger.info(f"dusk will occur at {dusk}")
        until_dawn = dawn - now
        logger.info(f"time until dawn {until_dawn}")
        until_dusk = dusk - now
        logger.info(f"time until dusk {until_dusk}")
        if until_dawn < until_dusk:
            pixels.pixels.fill((pixels.min, pixels.min, pixels.min))
            logger.info(f"sleeping {until_dawn.seconds} seconds until dawn")
            sleep(until_dawn.seconds)
            pixels.brighten()
            logger.info(
                f"dusk will occur at {datetime.datetime.now() + datetime.timedelta(seconds=(until_dusk - until_dawn).seconds - duration)}"
            )
            logger.info(
                f"sleeping {(until_dusk - until_dawn).seconds - duration} seconds until dusk"
            )
            sleep((until_dusk - until_dawn).seconds - duration)
            pixels.dim()
        else:
            pixels.pixels.fill((pixels.max, pixels.max, pixels.max))
            logger.info(f"sleeping {until_dusk.seconds} seconds until dusk")
            sleep(until_dusk.seconds)
            pixels.dim()
            logger.info(
                f"dawn will occur at {datetime.datetime.now() + datetime.timedelta((until_dawn - until_dusk).seconds - duration)}"
            )
            logger.info(
                f"sleeping {(until_dawn - until_dusk).seconds - duration} seconds until dawn"
            )
            sleep((until_dawn - until_dusk).seconds - duration)
            pixels.brighten()
        day += 1


def brightness(arg: str) -> int:
    val = int(arg)
    if not 0 <= val <= 255:
        raise argparse.ArgumentTypeError("value must be between 0 and 255")
    return val


def minutes(arg: str) -> int:
    val = float(arg)
    if not 0 <= val <= 720:
        raise argparse.ArgumentTypeError("value must be between 0 and 720")
    return int(val * 60)


def time(arg: str) -> datetime.datetime:
    return datetime.datetime.strptime(arg, "%H:%M")


def positive_int(arg: str) -> int:
    val = int(arg)
    if val < 1:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return val


def main(argv: list[str] | None = None) -> None:
    logging.config.dictConfig(config=logging_config)
    parser = argparse.ArgumentParser(
        description="Begin circadian cycle with smooth dimming and brightening of LEDs."
    )
    parser.add_argument(
        "--dawn",
        type=time,
        default="06:00",
        metavar="H:M",
        help="Time to start brightening lights. Dusk will be set to 12 hours after dawn. Default is 06:00.",
    )
    parser.add_argument(
        "--duration",
        type=minutes,
        default=120,
        metavar="minutes",
        help="Duration in minutes for dimming and brightening lights. Must be an integer between 0 and 720. Default is 120.",
    )
    parser.add_argument(
        "--max",
        type=brightness,
        default=255,
        metavar="brightness",
        help="Maximum brightness for LEDs. Must be an integer between 0 and 255 and greater than --min. Default is 255.",
    )
    parser.add_argument(
        "--min",
        type=brightness,
        default=0,
        metavar="brightness",
        help="Minimum brightness for LEDs. Must be an integer between 0 and 255 and less than --max. Default is 0.",
    )
    parser.add_argument(
        "-n",
        "--num-pixels",
        dest="num_pixels",
        type=int,
        default=60,
        metavar="int",
        help="Number of led pixels to use. Must be an integer greater than 0. Default is 60.",
    )
    args = parser.parse_args(argv)

    if args.min >= args.max:
        parser.error("--max must be greater than --min")

    with neopixel.NeoPixel(board.D18, args.num_pixels) as raw_pixels:  # pyright: ignore
        pixels = Pixels(raw_pixels, args.min, args.max, args.duration)
        try:
            loop(pixels, args.dawn, args.duration)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
    logger.info("Dimming cycle ended")


if __name__ == "__main__":
    main()
