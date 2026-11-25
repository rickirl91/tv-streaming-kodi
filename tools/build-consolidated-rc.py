"""Build or verify the three GitHub Pages installers, with byte-level parity."""
import argparse
import hashlib
import io
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive" / "releases"
STREAM_ASSET = "resources/media/see_all_miami_neutral_v024.png"
SOURCES = ("nextepisode", "streamrow", "homepersonalisation")


def packages():
    for directory in SOURCES:
        source = ROOT / "src" / directory
        metadata = ElementTree.parse(source / "addon.xml").getroot()
        addon = metadata.get("id")
        path = ROOT / f"{addon}-{metadata.get('version')}-RC.zip"
        entries = {f"{addon}/{p.relative_to(source).as_posix()}": p.read_bytes()
                   for p in source.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
        if directory == "streamrow":
            asset = f"{addon}/{STREAM_ASSET}"
            with ZipFile(ARCHIVE / f"{addon}-0.3.1-RC.zip") as old:
                entries[asset] = old.read(asset)
        yield path, entries


def zip_bytes(entries):
    output = io.BytesIO()
    with ZipFile(output, "w") as package:
        for name, data in sorted(entries.items()):
            if name.endswith(".py"):
                compile(data, name, "exec")
            if name.endswith(".xml"):
                ElementTree.fromstring(data)
            info = ZipInfo(name)
            info.external_attr = 0o100644 << 16
            package.writestr(info, data, ZIP_DEFLATED, compresslevel=9)
    return output.getvalue()


class ZipLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.url = ""
        self.label = ""
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.url = dict(attrs).get("href", "")
            self.label = ""

    def handle_data(self, data):
        if self.url:
            self.label += data

    def handle_endtag(self, tag):
        if tag == "a":
            if self.url.endswith(".zip"):
                self.links.append((self.url, self.label))
            self.url = ""


def check_links(index):
    parser = ZipLinks()
    parser.feed(index.read_text(encoding="utf-8"))
    for url, label in parser.links:
        if Path(url).name != label or not (index.parent / url).is_file():
            raise SystemExit(f"Invalid ZIP link in {index.name}: {url} ({label})")
    return {url for url, _ in parser.links}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    installers = []
    for path, entries in packages():
        if not args.check:
            path.write_bytes(zip_bytes(entries))
        with ZipFile(path) as actual:
            if (actual.testzip() or sorted(actual.namelist()) != sorted(entries)
                    or any(actual.read(name) != data for name, data in entries.items())):
                raise SystemExit(f"ZIP integrity or source parity failed for {path.name}")
            for name, data in entries.items():
                if name.endswith(".py"):
                    compile(data, name, "exec")
                if name.endswith(".xml"):
                    ElementTree.fromstring(data)
        installers.append(path.name)
        print(f"Verified {path.name}")

    if not set(installers).issubset(check_links(ROOT / "index.html")):
        raise SystemExit("A consolidated installer is missing from index.html")
    check_links(ROOT / "archive" / "index.html")
    manifest = ROOT / "SHA256SUMS.txt"
    paths = sorted([*ROOT.glob("*.zip"), *ARCHIVE.glob("*.zip"), *ROOT.glob("zips/*/*.zip"),
                    ROOT / ".nojekyll", ROOT / "addons.xml", ROOT / "addons.xml.md5",
                    ROOT / "archive/notes/README_SETUP.txt"])
    sums = "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n"
                   for p in paths)
    if args.check:
        if manifest.read_text() != sums:
            raise SystemExit("Checksum manifest differs from published files")
    else:
        manifest.write_text(sums)


if __name__ == "__main__":
    main()
