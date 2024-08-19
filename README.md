# leds

Smoothly dim and brighten LEDs in a circadian cycle on a Raspberry Pi. Also
other fun and useless LED stuff.

## Install

- Clone the repository.

```bash
git clone https://github.com/jtompkin/leds.git
```

- OR: Download a script file directly.

```bash
wget https://raw.githubusercontent.com/jtompkin/leds/main/cyle.py
```

- OR OR: Download a script file from github in your browser.

## Dependencies

- [`adafruit-blinka`](https://github.com/adafruit/Adafruit_Blinka)
- [`adafruit-circuitpython-neopixel`](https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel)
- [`colour`](https://github.com/vaab/colour) (only for `chase.py`)

Install in a [virtual
environment](https://docs.python.org/3/library/venv.html) (or don't I'm not your
boss).

```bash
pip install adafruit-blinka adafruit-circuitpython-neopixel colour
```

## Usage

- Run desired script.
- Your will most likely have to use `sudo` to access GPIO.

```bash
sudo python cycle.py
```

- See [example](#Example) if you are having trouble with virtual environments
and `sudo` not getting along.
- Uses pin GPIO 18 by default. This can be changed by editing the value of the
constant `PIN` in the script file.
- Run script with `-h` to see available options and defaults.

### Example

```bash
sudo --preserve-env=PATH,VIRTUAL_ENV cycle.py --dawn 07:00 --duration 60 --color 255 0 0 -n 30
```

- This starts a circadian cycle where dawn starts at 07:00, dusk starts at
19:00, both lasting for 60 minutes, with 30 fully red LEDs.
- `--preserve-env` ensures that dependencies installed in the active virtual
environment are available to the root user while running the script.

## License

Licensed under the MIT license. See LICENSE file.
