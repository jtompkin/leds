#!/usr/bin/env python3
import board
import neopixel


PIN = board.D18


def main() -> None:
    pixels = neopixel.NeoPixel(PIN, 60)  # pyright: ignore
    pixels.fill((0, 0, 0))


if __name__ == "__main__":
    main()
