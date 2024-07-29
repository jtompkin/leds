#!/usr/bin/env python3
import argparse

import board
import neopixel


Color = tuple[int, int, int] | int

PIN = board.D18


def fill(pixels: neopixel.NeoPixel, color: Color) -> None:
    pixels.fill(color)
    input("Press enter to reset LEDs. ")


def _color(arg: str) -> int:
    val = int(arg)
    if not 0 <= val <= 255:
        raise argparse.ArgumentTypeError("value must be between 0 and 255")
    return val


def _color_val(arg: str) -> int:
    val = int(arg.lstrip("#"), 16)
    if not 0 <= val <= 0xFFFFFF:
        raise argparse.ArgumentTypeError("value must be between 0 and #FFFFFF")
    return val


def _pos_int(arg: str) -> int:
    val = int(arg)
    if val < 0:
        raise argparse.ArgumentTypeError(
            "value must be greater than or equal to 0"
        )
    return val


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Fill leds with given color")
    color = parser.add_mutually_exclusive_group()
    color.add_argument(
        "--rgb",
        nargs=3,
        type=_color,
        help="Color as RGB values. Separate values by space. (default 255 255 255)",
    )
    color.add_argument(
        "--color",
        type=_color_val,
        default=0xFFFFFF,
        help="Color as hexadecimal value. (default #FFFFFF)",
    )
    parser.add_argument(
        "-n",
        "--num-pixels",
        dest="num_pixels",
        type=_pos_int,
        default=60,
        help="Number of pixels to fill. (default 60)",
    )
    args = parser.parse_args(argv)
    c = args.rgb
    if c is None:
        c = args.color
    with neopixel.NeoPixel(PIN, args.num_pixels) as pixels:  # pyright: ignore
        fill(pixels, c)


if __name__ == "__main__":
    main()
