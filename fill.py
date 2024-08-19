#!/usr/bin/env python3
import argparse

import board
import neopixel


Color = tuple[int, int, int] | int

PIN = board.D18


def fill(pixels: neopixel.NeoPixel, color: Color) -> None:
    pixels.fill(color)
    input("Press enter to reset LEDs. ")


def get_color(args: list[str], parser: argparse.ArgumentParser) -> Color:
    if len(args) == 1:
        val = int(args[0].lstrip("#"), 16)
        if not 0x000000 <= val <= 0xFFFFFF:
            parser.error("value must be between 0x000000 and 0xFFFFFF")
        return val
    if len(args) == 3:
        vals: list[int] = []
        for arg in args:
            val = int(arg)
            if not 0 <= val <= 255:
                parser.error("value must be between 0 and 255")
            vals.append(val)
        return (vals[0], vals[1], vals[2])
    parser.error(
        "color must be a single hexadecimal value or an RGB color code"
    )


def _pos_int(arg: str) -> int:
    val = int(arg)
    if val < 1:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return val


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Fill leds with given color")
    parser.add_argument(
        "color",
        nargs="*",
        default=["FFFFFF"],
        help="specifies the color to set LEDs to. The value must be a single hexadecimal integer between 0x000000 and 0xFFFFFF, or 3 integers between 0 and 255 for an RGB color code. (default 0xFFFFFF)",
    )
    parser.add_argument(
        "-n",
        "--num-pixels",
        dest="num_pixels",
        type=_pos_int,
        default=60,
        help="specifies the number of pixels to use. The value must be an integer greater than 0. (default 60)",
    )
    args = parser.parse_args(argv)
    with neopixel.NeoPixel(PIN, args.num_pixels) as pixels:  # pyright: ignore
        fill(pixels, get_color(args.color, parser))


if __name__ == "__main__":
    main()
