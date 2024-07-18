#!/usr/bin/env python3
import os
import datetime
import argparse
import logging.config
from time import sleep, time

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

SAMPLE_RATE = 1
PIN = board.D18


class Pixels:
    def __init__(
        self, pixels: neopixel.NeoPixel, min: float, max: float, duration: float
    ) -> None:
        self.pixels = pixels
        self.min = min
        self.max = max
        self.duration = duration

    def dim(self):
        logger.info("Beginning dusk")
        self.pixels.brightness = self.max
        self.pixels.show()
        brightness = self.max
        delta = ((self.min - self.max) / self.duration) / SAMPLE_RATE
        t = time()
        while time() - t < self.duration:
            brightness += delta
            self.pixels.brightness = brightness
            self.pixels.show()
            logger.debug(brightness)
            sleep(1 / SAMPLE_RATE)
        self.pixels.brightness = self.min
        self.pixels.show()
        logger.info("Dusk complete")

    def brighten(self):
        logger.info("Beginning dawn")
        self.pixels.brightness = self.min
        self.pixels.show()
        brightness = self.min
        delta = ((self.max - self.min) / self.duration) / SAMPLE_RATE
        t = time()
        while time() - t < self.duration:
            brightness += delta
            self.pixels.brightness = brightness
            self.pixels.show()
            logger.debug(brightness)
            sleep(1 / SAMPLE_RATE)
        self.pixels.brightness = self.max
        self.pixels.show()
        logger.info("Dawn complete")


def loop(
    pixels: Pixels,
    dawn_time: datetime.datetime,
    duration: float,
    dusk_time: datetime.datetime | None = None,
) -> None:
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
        if dusk_time is not None:
            dusk = datetime.datetime(
                now.year, now.month, now.day, dusk_time.hour, dusk_time.minute
            )
        if now.timestamp() > dusk.timestamp():
            dusk += datetime.timedelta(1)
        logger.info(f"dusk will occur at {dusk}")
        until_dawn = dawn - now
        logger.info(f"time until dawn {until_dawn}")
        until_dusk = dusk - now
        logger.info(f"time until dusk {until_dusk}")
        if until_dawn < until_dusk:
            pixels.pixels.brightness = pixels.min
            pixels.pixels.show()
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
            pixels.pixels.brightness = pixels.max
            pixels.pixels.show()
            logger.info(f"sleeping {until_dusk.seconds} seconds until dusk")
            sleep(until_dusk.seconds)
            pixels.dim()
            logger.info(
                f"dawn will occur at {datetime.datetime.now() + datetime.timedelta(seconds=(until_dawn - until_dusk).seconds - duration)}"
            )
            logger.info(
                f"sleeping {(until_dawn - until_dusk).seconds - duration} seconds until dawn"
            )
            sleep((until_dawn - until_dusk).seconds - duration)
            pixels.brighten()
        day += 1


def _brightness(arg: str) -> float:
    val = float(arg)
    if not 0 <= val <= 1:
        raise argparse.ArgumentTypeError("value must be between 0 and 1")
    return val


def _minutes(arg: str) -> float:
    val = float(arg)
    if not 0 <= val <= 720:
        raise argparse.ArgumentTypeError("value must be between 0 and 720")
    return val * 60


def _time(arg: str) -> datetime.datetime:
    return datetime.datetime.strptime(arg, "%H:%M")


def _color(arg: str) -> int:
    val = int(arg)
    if not 0 <= val <= 255:
        raise argparse.ArgumentTypeError("value must be between 0 and 255")
    return val


def _positive_int(arg: str) -> int:
    val = int(arg)
    if val < 1:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return val


def main(argv: list[str] | None = None) -> None:
    os.makedirs("logs", exist_ok=True)
    # So that normal users can view log files when ran with sudo
    os.chmod("logs", 0o777)
    logging.config.dictConfig(config=logging_config)
    parser = argparse.ArgumentParser(
        description="Begin circadian cycle with smooth dimming and brightening of LEDs."
    )
    parser.add_argument(
        "--dawn",
        type=_time,
        default="06:00",
        metavar="H:M",
        help="Time to start brightening lights. Dusk will be set to 12 hours after dawn. Default is 06:00.",
    )
    parser.add_argument(
        "--dusk",
        type=_time,
        metavar="H:M",
        help="Time to start dimming lights. Do not use this unless you need to; it is set automatically according to --dawn.",
    )
    parser.add_argument(
        "--duration",
        type=_minutes,
        default="120",
        metavar="minutes",
        help="Duration in minutes for dimming and brightening lights. Must be a number between 0 and 720. Default is 120.",
    )
    parser.add_argument(
        "-c",
        "--color",
        nargs=3,
        type=_color,
        metavar="val",
        default=[255, 255, 255],
        help="RGB color code of color to set LEDs to. Values must be between 0 and 255. Separate values with a space. Default is 255 255 255",
    )
    parser.add_argument(
        "--max",
        type=_brightness,
        default=1,
        metavar="brightness",
        help="Maximum brightness for LEDs. Must be a number between 0 and 1 and greater than --min. Default is 1.",
    )
    parser.add_argument(
        "--min",
        type=_brightness,
        default=0,
        metavar="brightness",
        help="Minimum brightness for LEDs. Must be a number between 0 and 1 and less than --max. Default is 0.",
    )
    parser.add_argument(
        "-n",
        "--num-pixels",
        dest="num_pixels",
        type=_positive_int,
        default=60,
        metavar="int",
        help="Number of led pixels to use. Must be an integer greater than 0. Default is 60.",
    )
    args = parser.parse_args(argv)

    if args.min >= args.max:
        parser.error("--max must be greater than --min")

    with neopixel.NeoPixel(
        PIN,  # pyright: ignore
        args.num_pixels,
        auto_write=False,
    ) as raw_pixels:
        pixels = Pixels(raw_pixels, args.min, args.max, args.duration)
        pixels.pixels.fill(args.color)
        try:
            loop(pixels, args.dawn, args.duration, args.dusk)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
    logger.info("Dimming cycle ended")


if __name__ == "__main__":
    main()
