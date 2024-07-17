#!/usr/bin/env python3
import time
import board
import argparse
import neopixel

# pyright: basic


def brighten(
    pixels: neopixel.NeoPixel, duration: int, start: int, end: int
) -> None:
    pixels.fill((start, start, start))
    prop = 0
    delta = (1 / duration) * (1 - start / (end + 1))
    for _ in range(duration):
        prop += delta
        c = start + end * prop
        pixels.fill((c, c, c))
        print(c)
        time.sleep(1)
    pixels.fill((end, end, end))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="brighten.py", description="Brighten led lights over time."
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
        default=0,
        help="Set the brightness of the pixels to the value given. Must be between 0 and 255.",
    )
    parser.add_argument(
        "-e",
        "--end",
        type=int,
        default=255,
        help="End value for brightness. Must be between 0 and 255 and greater than -s.",
    )
    args = parser.parse_args(argv)
    duration = int(args.time * 60) * 1
    if duration <= 0:
        raise ValueError("-t, --time must be greater than 0.")
    if not 0 <= args.start <= 255:
        raise ValueError("-s, --start must be between 0 and 255.")
    if not 0 <= args.end <= 255:
        raise ValueError("-e, --end must be between 0 and 255.")
    if args.end < args.start:
        raise ValueError("-e, --end must be greater than -s.")
    start = time.time()
    brighten(neopixel.NeoPixel(board.D18, 60), duration, args.start, args.end)  # pyright: ignore
    print(f"duration: {time.time()-start}")


if __name__ == "__main__":
    main()
