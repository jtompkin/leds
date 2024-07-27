#!/usr/bin/env python3
import board
import neopixel


PIN = board.D10

Color = tuple[int, int, int] | int


class Pixels:
    def __init__(self, pixels: neopixel.NeoPixel) -> None:
        self.pixels = pixels

    def __len__(self) -> int:
        return len(self.pixels)

    def set(self, i: int, color: Color) -> None:
        self.pixels[i] = color


def loop(pixels: Pixels) -> None:
    delta = int(2**24 / 60)
    c: int = 0
    while True:
        for i in range(len(pixels)):
            pixels.set(i, 16711680)
            c += delta
        pixels.pixels.show()
        input()


def main() -> None:
    with neopixel.NeoPixel(PIN, 60, auto_write=False) as raw_pixels:  # pyright: ignore
        loop(Pixels(raw_pixels))


if __name__ == "__main__":
    main()
