#!/usr/bin/env python3
import board
import neopixel

# pyright: basic


def main() -> None:
    pixels = neopixel.NeoPixel(board.D18, 60)
    pixels.fill((255, 255, 255))


if __name__ == "__main__":
    main()
