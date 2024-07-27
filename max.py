#!/usr/bin/env python3
import board
import neopixel


PIN = board.D10


def main() -> None:
    with neopixel.NeoPixel(PIN, 60) as pixels:  # pyright: ignore
        pixels.fill((255, 255, 255))
        input("press return to exit")


if __name__ == "__main__":
    main()
