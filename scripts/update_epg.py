"""Update independent XMLTV mirrors; a broken source must not block the others."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zlib


LIVEDNOW_URL = "https://assets.livednow.com/epg.xml"


def validate_xml(path):
    channels = programmes = 0
    root = None
    for event, element in ET.iterparse(path, events=("start", "end")):
        if root is None:
            root = element
            if element.tag != "tv":
                raise ValueError("response is not XMLTV (expected <tv> root)")
        if event == "end":
            if element.tag == "channel":
                channels += 1
            elif element.tag == "programme":
                programmes += 1
            element.clear()
    if not channels or not programmes:
        raise ValueError("XMLTV contains no channels or programmes")
    return channels, programmes


def fetch(url, destination, proxy=""):
    command = [
        "curl", "--fail", "--location", "--compressed", "--silent", "--show-error",
        "--connect-timeout", "15", "--max-time", "90",
        "--retry", "2", "--retry-delay", "2", "--retry-max-time", "180",
        "--output", str(destination),
    ]
    if proxy:
        command.extend(["--proxy", proxy])
    # A configured proxy may contain credentials; never log the command/stderr.
    result = subprocess.run(command + [url], capture_output=True, timeout=300)
    if result.returncode:
        raise ValueError(f"download failed (curl exit {result.returncode})")


def same_bytes(first, second):
    if not second.exists() or first.stat().st_size != second.stat().st_size:
        return False
    with first.open("rb") as left, second.open("rb") as right:
        while block := left.read(1024 * 1024):
            if block != right.read(len(block)):
                return False
    return True


def update_one(filename, url, output, proxy=""):
    target = output / filename
    archive = output / (filename + ".gz")
    try:
        with tempfile.TemporaryDirectory(prefix=".download-", dir=output) as temp:
            temp = Path(temp)
            payload, xml, compressed = temp / "payload", temp / "epg.xml", temp / "epg.gz"
            fetch(url, payload, proxy if url == LIVEDNOW_URL else "")
            with payload.open("rb") as stream:
                is_gzip = stream.read(2) == b"\x1f\x8b"
            if is_gzip:
                with gzip.open(payload, "rb") as source, xml.open("wb") as dest:
                    shutil.copyfileobj(source, dest)
            else:
                payload.replace(xml)
            channels, programmes = validate_xml(xml)
            # Stable header: unchanged content produces identical .gz bytes.
            with xml.open("rb") as source, compressed.open("wb") as dest:
                with gzip.GzipFile(filename="", mode="wb", fileobj=dest, mtime=0) as gz:
                    shutil.copyfileobj(source, gz)
            changed = not same_bytes(xml, target) or not same_bytes(compressed, archive)
            if changed:
                # Both files are fully prepared and validated before publication.
                xml.replace(target)
                compressed.replace(archive)
            return filename, "updated" if changed else "unchanged", f"{channels} channels, {programmes} programmes"
    except (OSError, ValueError, ET.ParseError, EOFError, zlib.error, subprocess.SubprocessError) as error:
        # Older versions could have committed HTML challenge/error pages.
        # Keep valid cached XML, but do not continue serving known corrupt files.
        removed = False
        if target.exists():
            try:
                validate_xml(target)
            except (OSError, ValueError, ET.ParseError):
                target.unlink()
                archive.unlink(missing_ok=True)
                removed = True
        detail = str(error) if isinstance(error, ValueError) else type(error).__name__
        detail += "; removed invalid cached files" if removed else "; kept previous files"
        return filename, "failed", detail


def load_sources(path):
    sources = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(sources, dict) or not sources:
        raise ValueError("files.json must be a nonempty filename-to-URL object")
    for filename, url in sources.items():
        if (not filename.endswith(".xml") or "/" in filename or "\\" in filename
                or not isinstance(url, str) or not url.startswith(("http://", "https://"))):
            raise ValueError("invalid filename or URL in files.json")
    return sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("files.json"))
    parser.add_argument("--output", type=Path, default=Path("epg"))
    args = parser.parse_args()
    sources = load_sources(args.config)
    args.output.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(update_one, name, url, args.output, os.environ.get("PROXY_URL", ""))
                   for name, url in sources.items()]
        results = [future.result() for future in futures]
    lines = ["| File | Result | Detail |", "| --- | --- | --- |"]
    for filename, status, detail in results:
        print(f"{filename}: {status}: {detail}", flush=True)
        if status == "failed" and os.environ.get("GITHUB_ACTIONS"):
            print(f"::warning::{filename}: {detail}", flush=True)
        lines.append(f"| {filename} | {status} | {detail.replace('|', '/')} |")
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write("\n".join(lines) + "\n")
    return 0 if any(status != "failed" for _, status, _ in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
