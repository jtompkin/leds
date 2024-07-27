#!/usr/bin/env python3
from colour import Color
from time import sleep
import board
import neopixel


WAIT = 2
NUM_PIXELS = 60
BLACK = (0, 0, 0)
PIN = board.D10


def color_rgb(color: Color) -> tuple[int, int, int]:
    return (
        int(color.rgb[0] * 255),
        int(color.rgb[1] * 255),
        int(color.rgb[2] * 255),
    )


class Pixels:
    def __init__(
        self, pixels: neopixel.NeoPixel, start: Color, duration: float
    ) -> None:
        self.pixels = pixels
        self.base = start
        self.color = start
        self.duration = duration

    def run_off(self, start: int, end: int) -> None:
        if start > end:
            step = -1
        else:
            step = 1
        for i in range(start, end, step):
            self.pixels[i] = 0
            self.pixels.show()
            sleep(self.duration / len(self.pixels))

    def run_down(self) -> None:
        final = self.color
        for i, color in enumerate(
            self.color.range_to(
                Color(self.color.hex, saturation=0.3), len(self.pixels)
            )
        ):
            self.pixels[i] = color_rgb(color)
            self.pixels.show()
            final = color
            sleep(self.duration / len(self.pixels))
        self.color = final
        self.run_off(0, len(self.pixels))

    def run_up(self) -> None:
        final = self.color
        for i, color in enumerate(
            self.color.range_to(
                Color(self.color, saturation=1), len(self.pixels)
            )
        ):
            self.pixels[(len(self.pixels) - 1) - i] = color_rgb(color)
            self.pixels.show()
            final = color
            sleep(self.duration / len(self.pixels))
        self.color = final
        self.run_off(len(self.pixels) - 1, 0)

    def reset(self) -> None:
        self.color = self.base

    def off(self) -> None:
        self.pixels.fill(0)


def loop(pixels: Pixels) -> None:
    while True:
        for color in pixels.base.range_to("blue", 5):
            pixels.run_down()
            pixels.off()
            pixels.run_up()
            pixels.off()
            pixels.reset()
            pixels.color = color


def main() -> None:
    with neopixel.NeoPixel(PIN, NUM_PIXELS, auto_write=False) as raw_pixels:  # pyright: ignore
        pixels = Pixels(raw_pixels, Color("red"), WAIT)
        loop(pixels)


if __name__ == "__main__":
    main()
