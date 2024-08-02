#!/usr/bin/env python3
import os
import datetime
import argparse
import logging.config
from time import sleep, time

import board
import neopixel

logger = logging.getLogger("cycle")

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(levelname)s|L%(lineno)d] %(asctime)s: %(message)s"
        },
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

RATE = 1
PIN = board.D18


class Pixels:
    def __init__(
        self,
        pixels: neopixel.NeoPixel,
        min: float,
        max: float,
        duration: float,
        log: bool = True,
    ) -> None:
        self.pixels = pixels
        self.min = min
        self.max = max
        self.duration = duration
        self.log = log
        self.events = {
            "dawn": self._setup_gradual(self.min, self.max),
            "dusk": self._setup_gradual(self.max, self.min),
        }

    def _setup_gradual(self, start: float, end: float):
        def gradual():
            self._change_brightness(start)
            brightness = start
            delta = ((end - start) / self.duration) / RATE
            t = time()
            while time() - t < self.duration:
                brightness += delta
                self._change_brightness(brightness)
                if self.log:
                    logger.debug(brightness)
                sleep(1 / RATE)
            self._change_brightness(end)
            if self.log:
                logger.debug(f"duration {time() - t}")

        return gradual

    def set_day(self):
        if self.log:
            logger.debug(f"setting brightness to {self.max}")
        self._change_brightness(self.max)

    def set_night(self):
        if self.log:
            logger.debug(f"setting brightness to {self.min}")
        self._change_brightness(self.min)

    def _change_brightness(self, brightness: float) -> None:
        self.pixels.brightness = brightness
        self.pixels.show()


def loop(
    pixels: Pixels,
    dawn_time: datetime.time,
    dusk_time: datetime.time | None = None,
) -> None:
    day = 1
    while True:
        logging.info(f"beginning day {day}")
        events = get_events(dawn_time, dusk_time)
        if events["dawn"] > events["dusk"]:
            pixels.set_day()
            next_event = "dusk"
        else:
            pixels.set_night()
            next_event = "dawn"
        done = {"dawn": False, "dusk": False}
        logger.info(f"current time is {events['now']}")
        logger.info(f"dawn will occur at {events['dawn']}")
        logger.info(f"dusk will occur at {events['dusk']}")
        while not (done["dawn"] and done["dusk"]):
            logger.info(
                f"next event ({next_event}) will occur at {events[next_event]}"
            )
            while datetime.datetime.now() < events[next_event]:
                try:
                    sleep(0.01)
                except KeyboardInterrupt:
                    logger.info("Received interrupt signal")
                    if input("exit? (y/N) ").lower() == "y":
                        return
            logger.info(f"beginning {next_event}")
            pixels.events[next_event]()
            logger.info(f"{next_event} complete")
            done[next_event] = True
            if next_event == "dusk":
                next_event = "dawn"
            else:
                next_event = "dusk"
        day += 1


def get_events(
    dawn_time: datetime.time, dusk_time: datetime.time | None
) -> dict[str, datetime.datetime]:
    events = {"now": datetime.datetime.now()}
    events["dawn"] = datetime.datetime(
        events["now"].year,
        events["now"].month,
        events["now"].day,
        dawn_time.hour,
        dawn_time.minute,
        dawn_time.second,
    )
    if events["now"] > events["dawn"]:
        events["dawn"] += datetime.timedelta(1)
    if dusk_time is None:
        events["dusk"] = events["dawn"] - datetime.timedelta(hours=12)
    else:
        events["dusk"] = datetime.datetime(
            events["now"].year,
            events["now"].month,
            events["now"].day,
            dusk_time.hour,
            dusk_time.minute,
            dusk_time.second,
        )
    if events["now"] > events["dusk"]:
        events["dusk"] += datetime.timedelta(1)
    return events


def _rgb(arg: str) -> int:
    val = int(arg)
    if not 0 <= val <= 255:
        raise argparse.ArgumentTypeError("all values must be between 0 and 255")
    return val


def _color(arg: str) -> int:
    val = int(arg.lstrip("#"), 16)
    if not 0 <= val <= 0xFFFFFF:
        raise argparse.ArgumentTypeError(
            "value must be between 0x000000 and 0xFFFFFF"
        )
    return val


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
    formats = ("%H:%M:%S", "%H:%M", "%H")
    for format in formats:
        try:
            return datetime.datetime.strptime(arg, format)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"value must fit one of {formats}")


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

    color = parser.add_mutually_exclusive_group()
    color.add_argument(
        "-r",
        "--rgb",
        nargs=3,
        type=_rgb,
        metavar="rgb",
        help="specifies the RGB color code of the color to set the LED pixels to. Each value of -r must be an integer between 0 and 255. Separate values with a space. (default 255 255 255)",
    )
    color.add_argument(
        "-c",
        "--color",
        type=_color,
        metavar="color",
        default=0xFFFFFF,
        help="specifies the hexadecimal value of the color to set the LED pixels to. The value of -c must be between 0x000000 and 0xFFFFFF. (default 0xFFFFFF)",
    )

    parser.add_argument(
        "--dawn",
        type=_time,
        default="06:00:00",
        metavar="H:M:S",
        help="specifies the time of day that the LED pixels will begin to brighten. Dusk will be set to 12 hours after dawn. (default 06:00:00)",
    )
    parser.add_argument(
        "--dusk",
        type=_time,
        metavar="H:M:S",
        help="specifies the time of day that the LED pixels will begin to dim. Do not set this unless you need to; by default, it is set automatically according to --dawn.",
    )
    parser.add_argument(
        "--duration",
        type=_minutes,
        default="120",
        metavar="minutes",
        help="specifies the duration in minutes that dimming and brightening operations will last. The value of --duration must be a number between 0 and 720. (default 120)",
    )
    parser.add_argument(
        "--max",
        type=_brightness,
        default=1,
        metavar="brightness",
        help="specifies the maximum brightness for LED pixels. The value of --max must be a number between 0 and 1. (default 1)",
    )
    parser.add_argument(
        "--min",
        type=_brightness,
        default=0,
        metavar="brightness",
        help="specifies the minimum brightness for LED pixels. The value of --min must be a number between 0 and 1. (default 0)",
    )
    parser.add_argument(
        "-n",
        "--num-pixels",
        dest="num_pixels",
        type=_positive_int,
        default=60,
        metavar="int",
        help="specifies the number of LED pixels that will be used. The value of -n must be an integer greater than 0. (default 60)",
    )
    args = parser.parse_args(argv)

    if args.rgb is None:
        c = args.color
    else:
        c = args.rgb

    if args.min >= args.max:
        parser.error("--max must be greater than --min")

    with neopixel.NeoPixel(
        PIN,  # pyright: ignore
        args.num_pixels,
        auto_write=False,
    ) as raw_pixels:
        pixels = Pixels(raw_pixels, args.min, args.max, args.duration)
        pixels.pixels.fill(c)
        try:
            loop(pixels, args.dawn, args.dusk)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
    logger.info("Dimming cycle ended")


if __name__ == "__main__":
    main()
