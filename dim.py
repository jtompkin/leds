#!/usr/bin/env python3
import time
import board
import argparse
import neopixel

# pyright: basic

SAMPLE_RATE = 1


def dim(pixels: neopixel.NeoPixel, duration: int, start: int, end: int) -> None:
    for i in range(len(pixels)):
        imap = {0: (70, 0, 0), 1: (0, 70, 0), 2: (0, 0, 70)}
        pixels[i] = imap[i % 3]
    prop = 1
    delta = 1 / duration
    for _ in range(duration):
        prop -= delta
        pixels.brightness = prop
        pixels.show()
        time.sleep(1 / SAMPLE_RATE)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="dim.py", description="Dim led lights over time."
    )
    parser.add_argument(
        "-t",
        "--time",
        type=float,
        help="Time in minutes for the dimming to last.",
    )
    parser.add_argument(
        "-s",
        "--start",
        type=int,
        default=255,
        help="Set the brightness of the pixels to the value given. Must be between 0 and 255.",
    )
    parser.add_argument(
        "-e",
        "--end",
        type=int,
        default=0,
        help="End value for brightness. Must be between 0 and 255 and less than -s.",
    )
    args = parser.parse_args(argv)
    duration = int(args.time * 60) * SAMPLE_RATE
    if duration <= 0:
        raise ValueError("-t, --time must be greater than 0.")
    if not 0 <= args.start <= 255:
        raise ValueError("-s, --start must be between 0 and 255.")
    if not 0 <= args.end <= 255:
        raise ValueError("-e, --end must be between 0 and 255.")
    if args.end > args.start:
        raise ValueError("-e, --end must be less than -s.")
    start = time.time()
    with neopixel.NeoPixel(board.D18, 60, auto_write=False) as pixels:  # pyright: ignore
        dim(pixels, duration, args.start, args.end)
    print(f"duration: {time.time()-start}")


if __name__ == "__main__":
    main()
