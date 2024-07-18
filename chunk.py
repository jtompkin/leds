#!/usr/bin/env python3
import time
import board
import random
import neopixel

# pyright: basic

PIN = board.D18
NUM_PIXELS = 120
CHUNK_SIZE = 10

Color = tuple[int, int, int]


class Chunk:
    def __init__(self, start: int, length: int, max: int, color: Color) -> None:
        self.start = start
        self.length = length
        self.color = color
        self.max = max

    def move(self, dist: int = 1) -> None:
        self.start = (self.start + dist) % self.max


class Pixels:
    def __init__(
        self,
        pixels: neopixel.NeoPixel,
        color: Color,
        chunk_size: int,
    ) -> None:
        self.pixels = pixels
        self.base_color = color
        self.color = color
        self.chunk_size = chunk_size
        self.delta = 1 / chunk_size
        self.chunks: list[Chunk] = []

    def fill_chunk(self, which: int) -> None:
        chunk = self.chunks[which]
        for i in range(chunk.length):
            self.pixels[(chunk.start + i) % len(self.pixels)] = tuple(
                map(lambda x: x * (self.delta * (i + 1)), chunk.color)
            )
        chunk.move()
        self.pixels.show()

    def add_chunk(self, start: int) -> None:
        self.chunks.append(
            Chunk(start, self.chunk_size, len(self.pixels), self.color)
        )

    def reset_color(self) -> None:
        self.color = self.base_color

    def off(self) -> None:
        self.pixels.fill((0, 0, 0))


def loop(pixels: Pixels) -> None:
    colors = (
        (100, 0, 0),
        (0, 100, 0),
        (0, 0, 100),
        (100, 100, 0),
        (0, 100, 100),
        (100, 0, 100),
    )
    for i, start in enumerate(range(0, NUM_PIXELS, pixels.chunk_size * 2)):
        pixels.color = colors[i % len(colors)]
        pixels.add_chunk(start)
    while True:
        try:
            pixels.off()
            for i in range(len(pixels.chunks)):
                pixels.fill_chunk(i)
            time.sleep(0.05)
        except KeyboardInterrupt:
            if input("\nstop? (y/N) ").lower() == "y":
                return


def main() -> None:
    with neopixel.NeoPixel(PIN, NUM_PIXELS, auto_write=False) as raw_pixels:  # pyright: ignore
        pixels = Pixels(raw_pixels, (0, 100, 100), CHUNK_SIZE)
        loop(pixels)


if __name__ == "__main__":
    main()
