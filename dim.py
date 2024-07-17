#!/usr/bin/env python3
import time
import board
import argparse
import neopixel

# pyright: basic

SAMPLE_RATE = 2


def dim(
    pixels: neopixel.NeoPixel, duration: float, start: float, end: float
) -> None:
    for i in range(len(pixels)):
        imap = {0: (255, 0, 0), 1: (0, 255, 0), 2: (0, 0, 255)}
        pixels[i] = imap[i % 3]
    pixels.brightness = start
    brightness = start
    delta = ((end - start) / duration) / SAMPLE_RATE
    t = time.time()
    while time.time() - t < duration:
        brightness += delta
        print(brightness, time.time() - t)
        pixels.brightness = brightness
        pixels.show()
        time.sleep(1 / SAMPLE_RATE)
    pixels.brightness = end
    pixels.show()


def proportion(arg: str) -> float:
    val = float(arg)
    if not 0 <= val <= 1:
        raise argparse.ArgumentTypeError("value must be between 0 and 1")
    return val


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
        type=proportion,
        default=1,
        help="Set the brightness of the pixels to the value given. Must be between 0 and 255.",
    )
    parser.add_argument(
        "-e",
        "--end",
        type=proportion,
        default=0,
        help="End value for brightness. Must be between 0 and 255 and less than -s.",
    )
    args = parser.parse_args(argv)
    duration = int(args.time * 60)
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
