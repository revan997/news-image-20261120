#!/usr/bin/env python3
"""Entry point for news-image-20261120, round 2.

Validates entry.png (a whole, well-formed 1024x1024 PNG under 1 MiB),
copies it byte-for-byte to $MAKEFUN_OUTPUT_DIR (default /output), then
re-reads the copy and validates it again. Standard library only.

Usage:  MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import struct
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
MAX_BYTES = 1_048_576
WANT_W, WANT_H = 1024, 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class BadEntry(Exception):
    """Raised when entry.png fails validation."""


def _check_crc(chunk_type, data, stored_crc):
    want = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    if want != stored_crc:
        raise BadEntry(f"bad CRC in {chunk_type.decode('ascii', 'replace')} "
                       f"chunk: stored {stored_crc:#x}, computed {want:#x}")


def validate(data):
    """Validate PNG bytes; return (width, height). Raises BadEntry."""
    if len(data) == 0:
        raise BadEntry("entry.png is empty")
    if len(data) > MAX_BYTES:
        raise BadEntry(f"entry.png is {len(data)} bytes, over the "
                       f"{MAX_BYTES} byte limit")
    if data[:8] != PNG_MAGIC:
        raise BadEntry("bad PNG magic bytes")
    if len(data) < 8 + 25:
        raise BadEntry("file too short to contain IHDR + IEND")

    pos = 8
    seen_ihdr = False
    seen_iend = False
    width = height = None
    while pos < len(data):
        if pos + 8 > len(data):
            raise BadEntry("truncated chunk header")
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        if length > 0x7FFFFFFF:
            raise BadEntry(f"unreasonable chunk length {length}")
        end = pos + 8 + length + 4
        if end > len(data):
            raise BadEntry(f"truncated {ctype.decode('ascii', 'replace')} "
                           "chunk")
        chunk_data = data[pos + 8:pos + 8 + length]
        stored_crc = struct.unpack(">I", data[pos + 8 + length:end])[0]
        _check_crc(ctype, chunk_data, stored_crc)

        if ctype == b"IHDR":
            if pos != 8:
                raise BadEntry("IHDR is not the first chunk")
            if seen_ihdr:
                raise BadEntry("duplicate IHDR chunk")
            if length != 13:
                raise BadEntry("IHDR chunk has wrong length")
            width, height = struct.unpack(">II", chunk_data[:8])
            bit_depth, color_type = chunk_data[8], chunk_data[9]
            if (width, height) != (WANT_W, WANT_H):
                raise BadEntry(f"image is {width}x{height}, "
                               f"expected {WANT_W}x{WANT_H}")
            if bit_depth not in (1, 2, 4, 8, 16):
                raise BadEntry(f"unsupported bit depth {bit_depth}")
            if color_type not in (0, 2, 3, 4, 6):
                raise BadEntry(f"unsupported color type {color_type}")
            seen_ihdr = True
        elif ctype == b"IEND":
            if length != 0:
                raise BadEntry("IEND chunk must be empty")
            seen_iend = True
            pos = end
            break
        pos = end

    if not seen_ihdr:
        raise BadEntry("missing IHDR chunk")
    if not seen_iend:
        raise BadEntry("missing IEND trailer")
    if pos != len(data):
        raise BadEntry(f"{len(data) - pos} trailing bytes after IEND")
    return width, height


def main():
    try:
        raw = SOURCE.read_bytes()
    except OSError as exc:
        print(f"error: cannot read {SOURCE}: {exc}", file=sys.stderr)
        return 1
    try:
        width, height = validate(raw)
    except BadEntry as exc:
        print(f"error: entry.png failed validation: {exc}", file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        dest = out_dir / "entry.png"
        dest.write_bytes(raw)
        copied = dest.read_bytes()
    except OSError as exc:
        print(f"error: cannot write output: {exc}", file=sys.stderr)
        return 1
    if copied != raw:
        print("error: copied file differs from source", file=sys.stderr)
        return 1
    try:
        validate(copied)
    except BadEntry as exc:
        print(f"error: copied file failed validation: {exc}",
              file=sys.stderr)
        return 1

    print(f"ok: entry.png {width}x{height}, {len(raw)} bytes, "
          f"copied to {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
