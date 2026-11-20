#!/usr/bin/env python3
"""news-image entrypoint: verify entry.png and stage it into the output dir.

Reads the image sitting next to this script, runs a strict structural
check over the PNG bytes, then copies the untouched bytes into
$MAKEFUN_OUTPUT_DIR (default /output) and re-checks the copy before
declaring success. Pure standard library.
"""

import os
import struct
import sys
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
WANT_WIDTH = 1024
WANT_HEIGHT = 1024
SOURCE_NAME = "entry.png"


class EntryProblem(Exception):
    """Raised whenever the image fails any part of the structural check."""


def fail(msg):
    raise EntryProblem(msg)


def check_signature(blob):
    if not blob:
        fail("input is empty")
    if blob[: len(PNG_SIGNATURE)] != PNG_SIGNATURE:
        fail("missing PNG signature")


def check_size(blob):
    if len(blob) > MAX_BYTES:
        fail("input exceeds 1 MiB limit (%d bytes)" % len(blob))


def walk_chunks(blob):
    """Yield (kind, payload) for every chunk; enforce CRCs and framing."""
    pos = len(PNG_SIGNATURE)
    first = True
    saw_header = False
    saw_end = False
    while True:
        if pos == len(blob):
            if saw_end:
                break
            fail("reached end of file without IEND")
        if saw_end:
            fail("bytes present after IEND")
        if pos + 8 > len(blob):
            fail("truncated chunk header at offset %d" % pos)
        (length,) = struct.unpack(">I", blob[pos : pos + 4])
        kind = blob[pos + 4 : pos + 8]
        body_start = pos + 8
        body_end = body_start + length
        if body_end + 4 > len(blob):
            fail("truncated chunk %r at offset %d" % (kind, pos))
        payload = blob[body_start:body_end]
        stored_crc, = struct.unpack(">I", blob[body_end : body_end + 4])
        actual_crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            fail("CRC mismatch in chunk %r at offset %d" % (kind, pos))
        if first:
            if kind != b"IHDR":
                fail("first chunk is %r, expected IHDR" % kind)
            if length != 13:
                fail("IHDR length is %d, expected 13" % length)
            w, h = struct.unpack(">II", payload[:8])
            if w != WANT_WIDTH or h != WANT_HEIGHT:
                fail("dimensions are %dx%d, expected %dx%d"
                     % (w, h, WANT_WIDTH, WANT_HEIGHT))
            first = False
            saw_header = True
        elif kind == b"IHDR":
            fail("duplicate IHDR chunk at offset %d" % pos)
        if kind == b"IEND":
            if length != 0:
                fail("IEND chunk carries %d bytes, expected none" % length)
            saw_end = True
        yield kind, payload
        pos = body_end + 4


def inspect(blob):
    """Run every structural rule over the raw bytes; return (width, height)."""
    check_size(blob)
    check_signature(blob)
    dims = (None, None)
    found_end = False
    for kind, payload in walk_chunks(blob):
        if kind == b"IHDR":
            dims = struct.unpack(">II", payload[:8])
        if kind == b"IEND":
            found_end = True
    if not found_end:
        fail("no IEND chunk found")
    return dims


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(here, SOURCE_NAME)
    try:
        with open(src_path, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        print("cannot read %s: %s" % (SOURCE_NAME, exc), file=sys.stderr)
        return 1
    try:
        width, height = inspect(raw)
    except EntryProblem as exc:
        print("entry rejected: %s" % exc, file=sys.stderr)
        return 1

    dest_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, SOURCE_NAME)
        with open(dest_path, "wb") as fh:
            fh.write(raw)
        with open(dest_path, "rb") as fh:
            staged = fh.read()
    except OSError as exc:
        print("cannot stage output: %s" % exc, file=sys.stderr)
        return 1
    if staged != raw:
        print("staged copy differs from source", file=sys.stderr)
        return 1
    try:
        inspect(staged)
    except EntryProblem as exc:
        print("staged copy rejected: %s" % exc, file=sys.stderr)
        return 1

    print("ok: %s %dx%d %d bytes -> %s" % (SOURCE_NAME, width, height,
                                           len(raw), dest_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
