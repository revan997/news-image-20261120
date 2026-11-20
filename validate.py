#!/usr/bin/env python3
"""validate.py — PNG integrity check for news-image-20261120 round 5.

Checks: magic bytes, IHDR width/height == 1024x1024, CRC of every
chunk, IEND present, no trailing bytes, file non-empty.
Exit 0 = valid, 1 = invalid (reason printed). Stdlib only.
Usage: python3 validate.py <path>
"""

import struct
import sys
import zlib

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def validate(path):
    with open(path, "rb") as f:
        data = f.read()
    if len(data) == 0:
        return "empty file"
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        return "bad magic bytes"
    pos = 8
    seen_ihdr = False
    seen_iend = False
    while True:
        if pos + 8 > len(data):
            return "truncated chunk header"
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        if pos + 12 + length > len(data):
            return "truncated chunk %r" % ctype.decode("latin1")
        chunk_data = data[pos + 8:pos + 8 + length]
        crc_stored = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])[0]
        crc_actual = zlib.crc32(ctype + chunk_data) & 0xFFFFFFFF
        if crc_actual != crc_stored:
            return "bad CRC in chunk %r" % ctype.decode("latin1")
        if ctype == b"IHDR":
            if seen_ihdr:
                return "duplicate IHDR"
            seen_ihdr = True
            if length != 13:
                return "bad IHDR length"
            w, h = struct.unpack(">II", chunk_data[:8])
            if (w, h) != (1024, 1024):
                return "wrong dimensions %dx%d" % (w, h)
        if ctype == b"IEND":
            seen_iend = True
            if length != 0:
                return "bad IEND length"
            pos += 12 + length
            break
        pos += 12 + length
    if not seen_ihdr:
        return "missing IHDR"
    if not seen_iend:
        return "missing IEND"
    if pos != len(data):
        return "trailing bytes after IEND (%d)" % (len(data) - pos)
    return None


if __name__ == "__main__":
    err = validate(sys.argv[1])
    if err is None:
        print("VALID %s" % sys.argv[1])
        sys.exit(0)
    print("INVALID %s: %s" % (sys.argv[1], err))
    sys.exit(1)
