#!/usr/bin/env python3
from collections.abc import Iterable
from time import sleep

import board
import neopixel

PIN = board.D18

Color = Iterable[int] | int


class Pixels:
    def __init__(self, pixels: neopixel.NeoPixel) -> None:
        self.pixels = pixels

    def __len__(self) -> int:
        return len(self.pixels)

    def set(self, i: int, color: Color) -> None:
        self.pixels[i] = color

    def dim(self, time: int) -> None:
        self.pixels.brightness = 1
        delta = 1 / (time * 100)
        for _ in range(time * 100):
            self.pixels.brightness -= delta
            self.pixels.show()
            sleep(0.01)


def loop(pixels: Pixels) -> None:
    delta = 1 / len(pixels)
    while True:
        for i in range(3):
            c = [0, 0, 0]
            for j in range(len(pixels)):
                pixels.set(j, c)
                c[i] = int(255 * ((j + 1) * delta))
            pixels.pixels.show()
            pixels.dim(2)


def main() -> None:
    with neopixel.NeoPixel(PIN, 60, auto_write=False) as raw_pixels:  # pyright: ignore
        try:
            loop(Pixels(raw_pixels))
        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    main()
