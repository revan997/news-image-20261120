#!/usr/bin/env python3
"""news-image-20261120 entrypoint.

Copies the front-page image bundled beside this file to the output
directory, after proving the file is a whole, well-formed PNG of the
right size. Standard library only; no network; deterministic output.
"""
import hashlib
import os
import struct
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = HERE / "entry.png"
MAX_BYTES = 1_048_576
WANT_W, WANT_H = 1024, 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def abort(message):
    print(f"entry: refusing: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_chunks(data):
    """Walk every PNG chunk, verifying lengths and CRCs, and return the
    (width, height, bit depth, colour type) from IHDR."""
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        abort("not a PNG (bad magic)")
    pos = 8
    seen_iend = False
    header = None
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > len(data):
            abort(f"chunk {kind!r} runs past end of file")
        body = data[pos + 8:pos + 8 + length]
        want_crc = struct.unpack(">I", data[pos + 8 + length:end])[0]
        if zlib.crc32(kind + body) & 0xFFFFFFFF != want_crc:
            abort(f"chunk {kind!r} has a bad CRC")
        if kind == b"IHDR":
            if pos != 8 or length != 13:
                abort("IHDR must be the first 13-byte chunk")
            w, h, depth, colour = struct.unpack(">IIBB", body[:10])
            header = (w, h, depth, colour)
        if kind == b"IEND":
            seen_iend = True
            if end != len(data):
                abort("trailing bytes after IEND")
            break
        pos = end
    if header is None:
        abort("no IHDR chunk")
    if not seen_iend:
        abort("no IEND chunk")
    return header


def main():
    if not IMAGE.is_file():
        abort(f"missing {IMAGE}")
    data = IMAGE.read_bytes()
    if len(data) > MAX_BYTES:
        abort(f"entry.png is {len(data)} bytes, over the 1 MiB cap")
    width, height, depth, colour = check_chunks(data)
    if (width, height) != (WANT_W, WANT_H):
        abort(f"image is {width}x{height}, want {WANT_W}x{WANT_H}")
    if depth != 8 or colour not in (2, 6):
        abort(f"bit depth {depth} / colour type {colour} not supported")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    target.write_bytes(data)
    written = target.read_bytes()
    if written != data:
        abort("output copy differs from the bundled image")
    # Re-validate the copy on disk, not just the bytes in memory.
    check_chunks(written)
    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {target} ({len(data)} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
