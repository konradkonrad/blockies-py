#!/usr/bin/env python
"""
python port of https://github.com/ethereum/blockies for terminal output

author: konrad@brainbot.com
"""
import sys
import math
import random
from itertools import islice
import colorsys
import ctypes

LOWER = chr(9604)
RESET = '\033[39;49m'


def int32(num):
    return ctypes.c_int32(num).value


def triple_shift(num):
    """Emulate js `num >>> 0` behaviour"""
    return int(
        hex(num & 0xFFFFFFFF),
        16
    )


class XORshiftPRNG(object):
    """The random number is a port of the js implementation
    of the Xorshift PRNG"""
    def __init__(self, seed):
        # Xorshift: [x, y, z, w] 32 bit values
        self.randseed = [int32(0)] * 4
        self.seedrand(seed)

    def seedrand(self, seed):
        for i in range(len(seed)):
            self.randseed[i % 4] = int32(
                self.randseed[i % 4] << 5
            ) - self.randseed[i % 4] + ord(seed[i])

    def rand(self):
        # based on Java's String.hashCode(), expanded to 4 32bit values
        t = int32(self.randseed[0] ^ (self.randseed[0] << 11))
        self.randseed[0] = self.randseed[1]
        self.randseed[1] = self.randseed[2]
        self.randseed[2] = self.randseed[3]
        self.randseed[3] = int32(
            self.randseed[3] ^ (int32(self.randseed[3]) >> 19) ^ t ^ (t >> 8)
        )

        result = int32(triple_shift(self.randseed[3])) / triple_shift((1 << 31))
        return result


def sanity_check():
    # Sanity check (test that RNG has same result as js version)
    first_rand = 0.2292061443440616
    seed = '0xfadc801b8b7ff0030f36ba700359d30bb12786e4'
    test = XORshiftPRNG(seed)
    assert test.rand() == first_rand

sanity_check()


class Color(object):
    def __init__(self, hue, light, saturation):
        self.hue = hue
        self.saturation = saturation
        self.light = light

    @staticmethod
    def createColor(prng):
        # saturation is the whole color spectrum
        hue = prng.rand()

        # saturation goes from 40 to 100, it avoids greyish colors
        saturation = ((prng.rand() * .6) + .4)
        # lightness can be anything from 0 to 100, but probabilities are a
        # bell curve around 50%
        light = ((prng.rand() + prng.rand() + prng.rand() + prng.rand()) * .25)
        return Color(hue, light, saturation)

    @property
    def numeric_rgb(self):
        rgb = list(map(lambda c: math.floor(c * 256), colorsys.hls_to_rgb(*self.hls)))
        return rgb

    @property
    def hex_rgb(self):
        rgb_hex = ''.join('{:02x}'.format(math.floor(c * 256)) for c in self.numeric_rgb)
        return rgb_hex

    @property
    def hls(self):
        return (self.hue, self.light, self.saturation)


def createImageData(size, prng):
    width = size  # Only support square icons for now
    height = size

    dataWidth = math.ceil(width / 2)
    mirrorWidth = width - dataWidth

    data = []
    for y in range(height):
        row = []
        for x in range(dataWidth):
            # this makes foreground and background color to have a 43% (1/2.3)
            # probability, spot color has 13% chance
            row.append(math.floor(prng.rand() * 2.3))
        r = row[0:mirrorWidth]
        r.reverse()
        row.extend(r)

        for i in range(len(row)):
            data.append(row[i])
    return data


class Options(object):
    def __init__(self,
        seed=None,
        size=8,
        color=None,
        bgcolor=None,
        spotcolor=None
    ):
        self.seed = seed or hex(
            math.floor((random.random() * math.pow(10, 16)))
        )
        self.prng = XORshiftPRNG(seed)
        self.size = size
        self.color = color or Color.createColor(self.prng)
        self.bgcolor = bgcolor or Color.createColor(self.prng)
        self.spotcolor = spotcolor or Color.createColor(self.prng)


def draw_two(first, second):
    """
    Draws two rows with upper pixel as ANSI background color and
    lower pixel as HALF_LOWER_BLOCK with ANSI foreground color.
    """
    first = '\033[48;2;{};{};{}m'.format(*first)
    second = '\033[38;2;{};{};{}m'.format(*second) + LOWER
    return first + second + RESET


def renderANSI(opts, _print=False):
    imageData = createImageData(opts.size, opts.prng)
    width = opts.size
    rowsData = iter(
        [imageData[i: i + width] for i in range(0, len(imageData), width)]
    )
    rows = []
    odd, even = list(islice(rowsData, 2))
    color_by_field = {
        0: opts.bgcolor.numeric_rgb,
        1: opts.color.numeric_rgb,
        2: opts.spotcolor.numeric_rgb,
    }
    while len(odd):
        upper = None
        lower = None
        row = ''
        for i in range(width):
            upper = color_by_field[odd[i]]
            lower = color_by_field[even[i]]
            row += draw_two(upper, lower)
        rows.append(row)
        odd, even = list(islice(rowsData, 2)) or ([], [])
    if _print:
        for row in rows:
            print(row)
    else:
        return rows


def create_blockie(seed, _print=False):
    """main method: creates a blockie with standard
    options from `seed` and optionally print it to stdout."""
    opts = Options(seed)
    return renderANSI(opts, _print=_print)


def main():
    if len(sys.argv) != 2:
        print('Usage:\n\t{} <seed>'.format(sys.argv[0]))
    elif sys.argv[1] == '--test':
        from blockies.vanity import vanity
        for a in vanity:
            create_blockie(a, True)
            print(a)
    else:
        seed = sys.argv[1].lower()
        create_blockie(seed, True)


if __name__ == '__main__':
    main()
