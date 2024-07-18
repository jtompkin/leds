# leds

Smoothly dim and brighten LEDs in a circadian cycle on a raspberry pi. Also
other fun and useless LED stuff.

## Install

- Clone repository

```bash
git clone https://github.com/jtompkin/leds.git
```

- OR: download script file directly

```bash
wget https://raw.githubusercontent.com/jtompkin/leds/main/smooth.py
```

## Dependencies

- [`adafruit-blinka`](https://github.com/adafruit/Adafruit_Blinka)
- [`adafruit-circuitpython-neopixel`](https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel)
- Install in a [virtual
environment](https://docs.python.org/3/library/venv.html) (or don't I'm not your boss).
```bash
pip install adafruit-blinka adafruit-circuitpython-neopixel
```

## Usage

- May have to run with `sudo`

```bash
python smooth.py
```

- Run with `-h` to see available options and defaults.

## License

Licensed under the MIT license. See LICENSE file.
