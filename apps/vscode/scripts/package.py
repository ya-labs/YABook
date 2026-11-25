#!/usr/bin/env python3
"""Empacota a extensão em `.vsix` sem `vsce` nem rede: zip com manifesto VSIX e a pasta `extension/`.

Uso: python3 apps/vscode/scripts/package.py [--saida <arquivo.vsix>]
Instalação: code --install-extension <arquivo.vsix>
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ("package.json", "extension.js", "README.md", "lib", "media")
TYPES = {".json": "application/json", ".js": "application/javascript", ".md": "text/markdown",
         ".svg": "image/svg+xml", ".vsixmanifest": "text/xml", ".css": "text/css", ".html": "text/html"}


def files():
    for name in INCLUDE:
        path = ROOT / name
        if path.is_file():
            yield path
        elif path.is_dir():
            yield from sorted(p for p in path.rglob("*") if p.is_file())


def manifest(meta):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
  <Metadata>
    <Identity Language="en-US" Id="{escape(meta['name'])}" Version="{escape(meta['version'])}" Publisher="{escape(meta['publisher'])}" />
    <DisplayName>{escape(meta['displayName'])}</DisplayName>
    <Description xml:space="preserve">{escape(meta['description'])}</Description>
    <Categories>{escape(','.join(meta.get('categories', [])))}</Categories>
    <GalleryFlags>Public</GalleryFlags>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="{escape(meta['engines']['vscode'])}" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionDependencies" Value="" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionPack" Value="" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionKind" Value="workspace" />
      <Property Id="Microsoft.VisualStudio.Code.LocalizedLanguages" Value="" />
    </Properties>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code" />
  </Installation>
  <Dependencies />
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
  </Assets>
</PackageManifest>
"""


def content_types(paths):
    suffixes = sorted({p.suffix for p in paths} | {".vsixmanifest", ".json"})
    rows = "".join(f'<Default Extension="{s}" ContentType="{TYPES.get(s, "application/octet-stream")}" />' for s in suffixes)
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            f'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">{rows}</Types>\n')


def build(output=None):
    meta = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    target = Path(output) if output else ROOT / "dist" / f"{meta['name']}-{meta['version']}.vsix"
    target.parent.mkdir(parents=True, exist_ok=True)
    paths = list(files())
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types(paths))
        archive.writestr("extension.vsixmanifest", manifest(meta))
        for path in paths:
            archive.write(path, "extension/" + path.relative_to(ROOT).as_posix())
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--saida")
    print(build(parser.parse_args().saida))
