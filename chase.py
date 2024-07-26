#!/usr/bin/env python3
import board
import time
import neopixel

# pyright: basic

WAIT = 1
NUM_PIXELS = 60
BLACK = (0, 0, 0)


def loop(pixels) -> None:
    r = 255
    b = 0
    g = 0
    while True:
        while r > 20:
            r -= 10
            b += 10
            for i in range(NUM_PIXELS):
                pixels[i] = (r, g, b)
                time.sleep(WAIT / NUM_PIXELS)
            pixels.fill(BLACK)
            r -= 10
            b += 10
            for i in range(NUM_PIXELS):
                pixels[NUM_PIXELS - i - 1] = (r, g, b)
                time.sleep(WAIT / NUM_PIXELS)
            pixels.fill(BLACK)
        while b > 10:
            b -= 10
            g += 10
            for i in range(NUM_PIXELS):
                pixels[i] = (r, g, b)
                time.sleep(WAIT / NUM_PIXELS)
            pixels.fill(BLACK)
            b -= 10
            g += 10
            for i in range(NUM_PIXELS):
                pixels[NUM_PIXELS - i - 1] = (r, g, b)
                time.sleep(WAIT / NUM_PIXELS)
            pixels.fill(BLACK)
        while g > 10:
            g -= 10
            r += 10
            for i in range(NUM_PIXELS):
                pixels[i] = (r, g, b)
                time.sleep(WAIT / NUM_PIXELS)
            pixels.fill(BLACK)
            g -= 10
            r += 10
            for i in range(NUM_PIXELS):
                pixels[NUM_PIXELS - i - 1] = (r, g, b)
                time.sleep(WAIT / NUM_PIXELS)
            pixels.fill(BLACK)


def main() -> None:
    with neopixel.NeoPixel(board.D18, NUM_PIXELS) as pixels:
        loop(pixels)


if __name__ == "__main__":
    main()
