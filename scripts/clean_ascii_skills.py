"""Clean non-ASCII characters in skills/ by replacing common glyphs with ASCII."""
from __future__ import annotations
import os, pathlib

ROOT = pathlib.Path(r"E:\My_Project\My_Github\AxiomEmbedded\skills")
REPL = {
    "—": "--", "–": "-", "→": "->", "←": "<-", "⇒": "=>",
    "≥": ">=", "≤": "<=", "≠": "!=", "×": "x", "•": "*",
    "…": "...", "’": "'", "“": '"', "”": '"', "—": "--",
    "≥": ">=", "≤": "<=", "α": "alpha", "β": "beta",
    "°": "deg", "µ": "u", "§": "S", "¶": "P",
    "©": "(c)", "®": "(R)", "™": "(TM)",
}
# Also handle BOM
count=0
for p in ROOT.rglob("*"):
    if not p.is_file(): continue
    if p.suffix.lower() not in {".md",".yaml",".yml",".py",".json",".csv",".txt",".toml",".cfg",".ini",".rst"}: continue
    if "__pycache__" in p.parts: continue
    try:
        data=p.read_bytes()
        text=data.decode("utf-8")
    except Exception:
        continue
    if all(ord(c)<128 for c in text):
        continue
    orig=text
    # strip BOM
    if text.startswith("\ufeff"):
        text=text.lstrip("\ufeff")
    for k,v in REPL.items():
        text=text.replace(k,v)
    # remove any remaining non-ascii
    text="".join(c if ord(c)<128 else "?" for c in text)
    if text!=orig:
        p.write_text(text, encoding="utf-8")
        count+=1
print("cleaned", count, "files")