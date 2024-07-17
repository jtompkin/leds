#!/usr/bin/env python3
import board
import neopixel
import time

# pyright: basic


def loop(pixels) -> None:
    remmap = {0: 0, 1: 50, 2: 100}
    while True:
        r, g, b = 0, 100, 200
        while r < 255 - 100:
            for i in range(len(pixels)):
                inc = remmap[i % 3]
                pixels[i] = (r + inc, g - inc, b)
            r += 5
            g += 5
            b += 5
            time.sleep(0.01)


def main() -> None:
    pixels = neopixel.NeoPixel(board.D18, 60)
    try:
        loop(pixels)
    except KeyboardInterrupt:
        pixels.fill((0, 0, 0))


if __name__ == "__main__":
    main()
